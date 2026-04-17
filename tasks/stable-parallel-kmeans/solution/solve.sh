#!/bin/bash
set -euo pipefail

cd /app

python3 - <<'PY'
from pathlib import Path

stable_kmeans_code = """import copy
import multiprocessing as mp
import os
import time
import warnings

import numpy as np
from joblib import Parallel, delayed
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")


class StableKMeans:
    def __init__(self, data, k_max, percent_subsampling=0.7, number_of_subsamples=20):
        self.data = np.asarray(data)
        self.k_max = int(k_max)
        self.percent_subsampling = float(percent_subsampling)
        self.number_of_subsamples = int(number_of_subsamples)
        self.scores = {k: copy.deepcopy([]) for k in range(2, self.k_max)}

    def fit_serial(self, verbose=True):
        self._reset_scores()
        for k in range(2, self.k_max):
            start = time.time()
            for _ in range(self.number_of_subsamples):
                self.scores[k].append(self._compute_stability_score(k))
            if verbose:
                print(f"K={k} done in {time.time() - start:.4f} seconds")
        return self

    def fit_parallel(self, n_jobs=None, verbose=True):
        self._reset_scores()
        if n_jobs is None:
            n_jobs = mp.cpu_count()

        os.environ["JOBLIB_START_METHOD"] = "spawn"
        start = time.time()
        results = Parallel(n_jobs=n_jobs, backend="loky", verbose=0)(
            delayed(self._compute_parallel_scores_for_k)(k) for k in range(2, self.k_max)
        )

        for k, scores, elapsed in results:
            self.scores[k] = scores
            if verbose:
                print(f"K={k} done in {elapsed:.4f} seconds")

        if verbose:
            print(f"Total parallel execution time: {time.time() - start:.4f} seconds")
        return self

    def get_optimal_k(self):
        averaged = {
            k: float(np.mean(values))
            for k, values in self.scores.items()
            if values
        }
        if not averaged:
            return 2
        return int(max(averaged, key=averaged.get))

    def get_stability_summary(self):
        summary = {}
        for k, values in self.scores.items():
            if not values:
                continue
            summary[k] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }
        return summary

    def _reset_scores(self):
        self.scores = {k: [] for k in range(2, self.k_max)}

    def _compute_parallel_scores_for_k(self, k):
        start = time.time()
        scores = [self._compute_stability_score_optimized(k) for _ in range(self.number_of_subsamples)]
        return k, scores, time.time() - start

    def _compute_stability_score(self, k):
        subsample_1 = self._subsample()
        subsample_2 = self._subsample()
        intersection_matrix = self._intersect(subsample_1, subsample_2)
        labels_1 = self._cluster(subsample_1, k)
        labels_2 = self._cluster(subsample_2, k)
        labels_1_common, labels_2_common = self._find_common_elements(
            intersection_matrix, labels_1, labels_2
        )
        if len(labels_1_common) == 0:
            return 0.0
        matrix_1 = self._create_label_matrix(labels_1_common)
        matrix_2 = self._create_label_matrix(labels_2_common)
        return self._compute_correlation(matrix_1, matrix_2)

    def _compute_stability_score_optimized(self, k):
        sample_size = max(1, int(self.percent_subsampling * len(self.data)))
        rng = np.random.default_rng()
        indices_1 = rng.choice(len(self.data), sample_size, replace=True)
        indices_2 = rng.choice(len(self.data), sample_size, replace=True)
        subsample_1 = self.data[indices_1]
        subsample_2 = self.data[indices_2]

        distances = np.linalg.norm(
            subsample_1[:, np.newaxis, :] - subsample_2[np.newaxis, :, :],
            axis=2,
        )
        common_indices = np.where(distances < 1e-10)
        if len(common_indices[0]) == 0:
            return 0.0

        labels_1 = self._cluster(subsample_1, k)
        labels_2 = self._cluster(subsample_2, k)
        labels_1_common = labels_1[common_indices[0]]
        labels_2_common = labels_2[common_indices[1]]
        if len(labels_1_common) < 2:
            return 0.0

        matrix_1 = self._create_label_matrix(labels_1_common)
        matrix_2 = self._create_label_matrix(labels_2_common)
        return self._compute_correlation(matrix_1, matrix_2)

    def _subsample(self):
        sample_size = max(1, int(self.percent_subsampling * len(self.data)))
        indices = np.random.randint(0, len(self.data), sample_size)
        return self.data[indices]

    def _cluster(self, sample, k):
        model = KMeans(n_clusters=k, random_state=None, n_init=10)
        return model.fit_predict(sample)

    def _intersect(self, subsample_1, subsample_2):
        if np.shape(subsample_1) != np.shape(subsample_2):
            raise AssertionError("Subsamples have different shapes")
        matrix = np.zeros((len(subsample_1), len(subsample_1)))
        for i, left in enumerate(subsample_1):
            for j, right in enumerate(subsample_2):
                if np.allclose(left, right, rtol=1e-10, atol=1e-10):
                    matrix[i, j] = 1
        return matrix

    def _find_common_elements(self, intersection_matrix, labels_1, labels_2):
        common_indices = np.where(intersection_matrix == 1)
        return labels_1[common_indices[0]], labels_2[common_indices[1]]

    def _create_label_matrix(self, labels):
        labels = np.asarray(labels)
        matrix = (labels[:, np.newaxis] == labels[np.newaxis, :]).astype(float)
        np.fill_diagonal(matrix, 0.0)
        return matrix

    def _compute_correlation(self, matrix_1, matrix_2):
        numerator = float(np.sum(matrix_1 * matrix_2))
        denominator = float(
            np.sqrt(np.sum(matrix_1 * matrix_1) * np.sum(matrix_2 * matrix_2))
        )
        if denominator == 0.0:
            return 0.0
        return numerator / denominator
"""

test_implementation_code = """import multiprocessing as mp
import time

from sklearn.datasets import make_blobs

from stable_kmeans import StableKMeans


def generate_test_data(n_samples=500, n_features=2, n_centers=4, random_state=42):
    data, labels = make_blobs(
        n_samples=n_samples,
        centers=n_centers,
        n_features=n_features,
        random_state=random_state,
        cluster_std=1.5,
    )
    return data, labels


def main():
    data, labels = generate_test_data()
    print(f"Dataset shape: {data.shape}")
    print(f"Reference clusters: {len(set(labels))}")

    serial_model = StableKMeans(data, k_max=8, number_of_subsamples=10)
    serial_start = time.time()
    serial_model.fit_serial(verbose=False)
    serial_time = time.time() - serial_start

    parallel_model = StableKMeans(data, k_max=8, number_of_subsamples=10)
    parallel_start = time.time()
    parallel_model.fit_parallel(n_jobs=min(2, mp.cpu_count()), verbose=False)
    parallel_time = time.time() - parallel_start

    print(f"Serial time: {serial_time:.4f} seconds")
    print(f"Parallel time: {parallel_time:.4f} seconds")
    print(f"Serial optimal k: {serial_model.get_optimal_k()}")
    print(f"Parallel optimal k: {parallel_model.get_optimal_k()}")
    print(f"Parallel summary keys: {sorted(parallel_model.get_stability_summary())}")


if __name__ == "__main__":
    main()
"""

Path("/app/stable_kmeans.py").write_text(stable_kmeans_code)
Path("/app/test_implementation.py").write_text(test_implementation_code)
PY
