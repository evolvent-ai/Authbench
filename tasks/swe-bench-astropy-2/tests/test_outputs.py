import ast
import copy
import math
import re
import warnings
from collections.abc import Iterable
from pathlib import Path


REPO_ROOT = Path("/app/astropy")
SOURCE_PATH = REPO_ROOT / "astropy" / "io" / "ascii" / "qdp.py"
EXPECTED_NEW_REGEX_LINE = "    _line_type_re = re.compile(_type_re, re.IGNORECASE)\n"
EXPECTED_NEW_REGEX_LINE_WITH_FLAGS = "    _line_type_re = re.compile(_type_re, flags=re.IGNORECASE)\n"
EXPECTED_OLD_REGEX_LINE = "    _line_type_re = re.compile(_type_re)\n"
EXPECTED_NEW_NO_LINE = "            if v.upper() == \"NO\":\n"
EXPECTED_NEW_NO_LINE_WITH_STRIP = "            if v.strip().upper() == \"NO\":\n"
EXPECTED_OLD_NO_LINE = "            if v == \"NO\":\n"


class _MaskedSentinel:
    def __deepcopy__(self, memo):
        return self


MASKED = _MaskedSentinel()


class _MaskedModule:
    masked = MASKED

    @staticmethod
    def is_masked(value):
        return value is MASKED


class _DummyNP:
    ma = _MaskedModule()

    @staticmethod
    def any(values):
        return any(values)


class _DummyTable:
    def __init__(self, rows, names, masked=False):
        self._rows = [list(row) for row in rows]
        self.colnames = list(names)
        self.masked = masked
        self.meta = {}

    def __getitem__(self, key):
        index = self.colnames.index(key)
        return [row[index] for row in self._rows]

    def __len__(self):
        return len(self._rows)


class _DummyWarning(UserWarning):
    pass


def _load_qdp_helpers():
    source = SOURCE_PATH.read_text(encoding="utf-8")
    module = ast.parse(source)
    snippets = {}

    target_names = {
        "_line_type",
        "_get_lines_from_file",
        "_interpret_err_lines",
        "_parse_value",
        "_get_tables_from_qdp_file",
    }

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            snippets[node.name] = ast.get_source_segment(source, node)

    missing = target_names - snippets.keys()
    assert not missing, f"Missing functions in qdp.py: {sorted(missing)}"

    namespace = {
        "copy": copy,
        "Iterable": Iterable,
        "np": _DummyNP(),
        "re": re,
        "Table": _DummyTable,
        "warnings": warnings,
        "AstropyUserWarning": _DummyWarning,
    }
    exec(
        "\n\n".join(snippets[name] for name in (
            "_line_type",
            "_get_lines_from_file",
            "_interpret_err_lines",
            "_parse_value",
            "_get_tables_from_qdp_file",
        )),
        namespace,
    )
    return namespace


def test_source_file_contains_fix():
    content = SOURCE_PATH.read_text(encoding="utf-8")
    assert (
        EXPECTED_NEW_REGEX_LINE in content
        or EXPECTED_NEW_REGEX_LINE_WITH_FLAGS in content
    ), "Case-insensitive regex compile not found"
    assert EXPECTED_OLD_REGEX_LINE not in content, "Buggy case-sensitive regex is still present"
    assert (
        EXPECTED_NEW_NO_LINE in content
        or EXPECTED_NEW_NO_LINE_WITH_STRIP in content
    ), "Uppercasing NO marker fix not found"
    assert EXPECTED_OLD_NO_LINE not in content, "Buggy NO marker comparison is still present"


def test_lowercase_line_types_are_accepted():
    namespace = _load_qdp_helpers()
    line_type = namespace["_line_type"]

    assert line_type("read serr 1 2") == "command"
    assert line_type("no no no no") == "new"
    assert line_type("1 0.5 2 0.5") == "data"


def test_lowercase_qdp_file_with_serr_and_no_values():
    namespace = _load_qdp_helpers()
    get_tables = namespace["_get_tables_from_qdp_file"]

    example = """\
read serr 1 2
1 0.5 2 0.1
3 no 4 no
no no no no
5 0.2 6 0.3
"""

    tables = get_tables(example, input_colnames=["x", "y"])

    assert len(tables) == 2, "Lowercase NO separator should split two tables"

    first = tables[0]
    assert first.colnames == ["x", "x_err", "y", "y_err"]
    assert len(first) == 2
    assert first["x"][0] == 1
    assert first["x_err"][0] == 0.5
    assert first["y"][0] == 2
    assert first["y_err"][0] == 0.1
    assert first["x"][1] == 3
    assert _DummyNP.ma.is_masked(first["x_err"][1]), "Lowercase no should map to a masked value"
    assert first["y"][1] == 4
    assert _DummyNP.ma.is_masked(first["y_err"][1]), "Lowercase no should map to a masked value"

    second = tables[1]
    assert len(second) == 1
    assert second["x"][0] == 5
    assert math.isclose(second["x_err"][0], 0.2)
    assert second["y"][0] == 6
    assert math.isclose(second["y_err"][0], 0.3)
