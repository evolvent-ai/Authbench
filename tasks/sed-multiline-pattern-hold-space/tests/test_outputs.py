from collections import Counter, defaultdict
from pathlib import Path
import re


LOG_PATH = Path("/var/log/app/production.log")
OUTPUT_PATH = Path("/tmp/stack_trace_analysis.txt")

EXCEPTION_RE = re.compile(
    r"\bERROR\s+([A-Za-z0-9_.$]+(?:Exception|Error|Throwable)):\s"
)
FRAME_RE = re.compile(r"^\s+at\s+([A-Za-z0-9_.$<>]+)\([^)]*\)$")


def iter_stack_traces(lines: list[str]):
    current_exception: str | None = None
    current_frames: list[str] = []

    for line in lines:
        exception_match = EXCEPTION_RE.search(line)
        if exception_match is not None:
            if current_exception is not None and current_frames:
                yield current_exception, current_frames[-1]
            current_exception = exception_match.group(1)
            current_frames = []
            continue

        if current_exception is None:
            continue

        frame_match = FRAME_RE.match(line)
        if frame_match is not None:
            current_frames.append(frame_match.group(1))
            continue

        if current_frames:
            yield current_exception, current_frames[-1]
        current_exception = None
        current_frames = []

    if current_exception is not None and current_frames:
        yield current_exception, current_frames[-1]


def compute_expected_lines() -> list[str]:
    counts: Counter[str] = Counter()
    root_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for exception_type, deepest_frame in iter_stack_traces(
        LOG_PATH.read_text(encoding="utf-8").splitlines()
    ):
        counts[exception_type] += 1
        root_counts[exception_type][deepest_frame] += 1

    expected_lines: list[str] = []
    for exception_type, count in sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        root_cause_method = sorted(
            root_counts[exception_type].items(),
            key=lambda item: (-item[1], item[0]),
        )[0][0]
        expected_lines.append(f"{exception_type}|{count}|{root_cause_method}")

    return expected_lines


def test_output_file_exists() -> None:
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"


def test_output_matches_expected_analysis() -> None:
    assert OUTPUT_PATH.read_text(encoding="utf-8").splitlines() == compute_expected_lines()


def test_output_is_pipe_delimited_and_sorted() -> None:
    lines = OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
    counts = []

    for line in lines:
        parts = line.split("|")
        assert len(parts) == 3, f"Expected 3 fields, got: {line}"
        exception_type, count, root_cause_method = parts
        assert "." in exception_type
        assert count.isdigit()
        assert "." in root_cause_method
        counts.append(int(count))

    assert counts == sorted(counts, reverse=True)
