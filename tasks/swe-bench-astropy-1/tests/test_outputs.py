import ast
from pathlib import Path

import numpy as np


REPO_ROOT = Path("/app/astropy")
SOURCE_PATH = REPO_ROOT / "astropy" / "modeling" / "separable.py"
EXPECTED_NEW_LINE = "        cright[-right.shape[0]:, -right.shape[1]:] = right\n"
EXPECTED_OLD_LINE = "        cright[-right.shape[0]:, -right.shape[1]:] = 1\n"


def _load_cstack():
    source = SOURCE_PATH.read_text(encoding="utf-8")
    module = ast.parse(source)
    snippets = {}

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in {"_compute_n_outputs", "_cstack"}:
            snippets[node.name] = ast.get_source_segment(source, node)

    missing = {"_compute_n_outputs", "_cstack"} - snippets.keys()
    assert not missing, f"Missing functions in separable.py: {sorted(missing)}"

    namespace = {"np": np}

    class DummyModel:
        pass

    namespace["Model"] = DummyModel
    exec(
        snippets["_compute_n_outputs"] + "\n\n" + snippets["_cstack"],
        namespace,
    )
    return namespace["_cstack"]


def test_source_file_contains_fix():
    content = SOURCE_PATH.read_text(encoding="utf-8")
    assert EXPECTED_NEW_LINE in content, "Fixed assignment not found in separable.py"
    assert EXPECTED_OLD_LINE not in content, "Buggy assignment is still present"


def test_nested_compound_regression():
    cstack = _load_cstack()

    left = np.array([[1, 1], [1, 1]], dtype=int)
    right = np.array([[1, 0], [0, 1]], dtype=int)

    result = cstack(left, right)
    expected = np.array(
        [
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ],
        dtype=int,
    )
    buggy = np.array(
        [
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1],
        ],
        dtype=int,
    )

    np.testing.assert_array_equal(result, expected)
    assert not np.array_equal(result, buggy), "Nested right-hand matrix is still collapsed"
