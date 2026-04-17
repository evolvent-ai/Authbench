from pathlib import Path


def test_stable_kmeans_file_exists():
    stable_kmeans_path = Path("/app/stable_kmeans.py")
    assert stable_kmeans_path.exists(), f"File {stable_kmeans_path} does not exist"


def test_test_implementation_file_exists():
    test_impl_path = Path("/app/test_implementation.py")
    assert test_impl_path.exists(), f"File {test_impl_path} does not exist"


def test_stable_kmeans_has_required_class_and_methods():
    stable_kmeans_path = Path("/app/stable_kmeans.py")
    content = stable_kmeans_path.read_text()

    assert "class StableKMeans" in content
    assert "fit_serial" in content
    assert "fit_parallel" in content
    assert "get_optimal_k" in content
    assert "get_stability_summary" in content


def test_stable_kmeans_has_parallel_support():
    stable_kmeans_path = Path("/app/stable_kmeans.py")
    content = stable_kmeans_path.read_text()

    has_parallel_import = (
        "import multiprocessing" in content
        or "from multiprocessing" in content
        or "from joblib import Parallel" in content
        or "Parallel(" in content
    )

    assert has_parallel_import, "Parallel execution support not found in stable_kmeans.py"


def test_stable_kmeans_uses_sklearn_kmeans():
    stable_kmeans_path = Path("/app/stable_kmeans.py")
    content = stable_kmeans_path.read_text()

    assert "from sklearn" in content or "import sklearn" in content
    assert "KMeans" in content


def test_serial_fit_produces_summary_and_optimal_k():
    import sys

    from sklearn.datasets import make_blobs

    sys.path.append("/app")
    from stable_kmeans import StableKMeans

    data, _ = make_blobs(
        n_samples=100,
        centers=3,
        n_features=2,
        random_state=42,
        cluster_std=1.0,
    )

    model = StableKMeans(data, k_max=5, number_of_subsamples=5)
    model.fit_serial(verbose=False)

    summary = model.get_stability_summary()
    optimal_k = model.get_optimal_k()

    assert summary
    assert isinstance(summary, dict)
    assert isinstance(optimal_k, int)
    assert optimal_k >= 2


def test_parallel_fit_runs_on_small_dataset():
    import sys

    from sklearn.datasets import make_blobs

    sys.path.append("/app")
    from stable_kmeans import StableKMeans

    data, _ = make_blobs(
        n_samples=60,
        centers=3,
        n_features=2,
        random_state=7,
        cluster_std=1.0,
    )

    model = StableKMeans(data, k_max=5, number_of_subsamples=3)
    model.fit_parallel(n_jobs=2, verbose=False)

    summary = model.get_stability_summary()
    assert summary
    assert isinstance(model.get_optimal_k(), int)


def test_test_implementation_generates_synthetic_data():
    test_impl_path = Path("/app/test_implementation.py")
    content = test_impl_path.read_text()

    has_synthetic_data = (
        "make_blobs" in content
        or "generate_test_data" in content
        or "synthetic" in content.lower()
    )

    assert has_synthetic_data
