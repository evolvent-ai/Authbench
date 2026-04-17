# Stable Parallel K-Means

Create a parallel implementation of the stable k-means algorithm in `/app`.

You must create these files:

- `/app/stable_kmeans.py`
- `/app/test_implementation.py`

Requirements for `stable_kmeans.py`:

- Define a `StableKMeans` class.
- Include these methods:
  - `__init__(self, data, k_max, percent_subsampling=0.7, number_of_subsamples=20)`
  - `fit_serial(self, verbose=True)`
  - `fit_parallel(self, n_jobs=None, verbose=True)`
  - `get_optimal_k(self)`
  - `get_stability_summary(self)`
- Use `scikit-learn` k-means for clustering.
- Include a real parallel implementation using `multiprocessing`, `joblib`, or an equivalent process-based approach.
- Determine the best cluster count by comparing clustering stability across repeated subsamples.
- `get_optimal_k()` must return an integer cluster count.
- `get_stability_summary()` must return a dictionary keyed by each tested `k`, where each value summarizes the stability scores for that `k`.

Requirements for `test_implementation.py`:

- Generate synthetic data.
- Run both the serial and parallel implementations.
- Print a short comparison summary, including the chosen cluster count and the returned stability summary.

The verifier reads the files directly from `/app`, so keep the file names exactly as specified.
