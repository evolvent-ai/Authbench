from __future__ import annotations

import copy
import re
import warnings
from collections.abc import Iterable


def _line_type(line, delimiter=None):
    if line is None:
        return "comment"

    line = line.strip()
    if not line or line.startswith("!"):
        return "comment"

    sep = delimiter if delimiter else r"\s+"
    _decimal_re = r"[-+]?(?:(?:\d+\.\d*)|(?:\d*\.\d+)|(?:\d+))(?:[Ee][-+]?\d+)?"
    _command_re = rf"READ({sep}(SERR|TERR))({sep}\d+)+"
    _new_re = rf"NO({sep}NO)+"
    _data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*"
    _type_re = (
        rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re}))"
        rf"\s*(\!(?P<comment>.*))?\s*$"
    )
    _line_type_re = re.compile(_type_re)
    match = _line_type_re.match(line)
    if match is None:
        raise ValueError(f"Unrecognized QDP line: {line}")

    for name in ("command", "new", "data"):
        if match.group(name) is not None:
            return name

    return "comment"


def _get_lines_from_file(qdp_file):
    if isinstance(qdp_file, str):
        if "\n" in qdp_file:
            lines = qdp_file.splitlines()
        else:
            with open(qdp_file, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
    elif isinstance(qdp_file, Iterable):
        lines = list(qdp_file)
    else:
        raise TypeError("qdp_file should be a string path, a string payload, or an iterable of lines")

    return [str(line).rstrip("\n") for line in lines]


def _interpret_err_lines(command_lines, input_colnames):
    serr_cols = []
    terr_cols = []

    for line in command_lines:
        tokens = line.split()
        upper_tokens = [token.upper() for token in tokens]
        if upper_tokens[:2] == ["READ", "SERR"]:
            serr_cols.extend(int(token) for token in tokens[2:])
        elif upper_tokens[:2] == ["READ", "TERR"]:
            terr_cols.extend(int(token) for token in tokens[2:])

    names = []
    for index, name in enumerate(input_colnames, start=1):
        names.append(name)
        if index in terr_cols:
            names.extend([f"{name}_perr", f"{name}_nerr"])
        if index in serr_cols:
            names.append(f"{name}_err")

    return names


def _parse_value(token):
    if token.lower() == "nan":
        return float("nan")
    if any(char in token.lower() for char in (".", "e")):
        return float(token)
    return int(token)


def _get_tables_from_qdp_file(qdp_file, input_colnames=None, delimiter=None):
    lines = _get_lines_from_file(qdp_file)
    if not input_colnames:
        raise ValueError("input_colnames must be provided in this reduced reproduction")

    command_lines = []
    current_rows = []
    tables = []

    for line in lines:
        kind = _line_type(line, delimiter=delimiter)

        if kind == "comment":
            continue
        if kind == "command":
            command_lines.append(line)
            continue
        if kind == "new":
            if current_rows:
                names = _interpret_err_lines(command_lines, input_colnames)
                tables.append(Table(rows=copy.deepcopy(current_rows), names=names, masked=True))
                current_rows = []
            continue

        values = []
        for v in line.split(delimiter) if delimiter else line.split():
            if v == "NO":
                values.append(np.ma.masked)
            else:
                values.append(_parse_value(v))
        current_rows.append(values)

    if current_rows:
        names = _interpret_err_lines(command_lines, input_colnames)
        tables.append(Table(rows=copy.deepcopy(current_rows), names=names, masked=True))

    if len(tables) > 1:
        warnings.warn(
            "This file contains multiple command blocks",
            AstropyUserWarning,
        )

    return tables
