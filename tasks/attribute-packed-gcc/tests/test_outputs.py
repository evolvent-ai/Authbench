from pathlib import Path
import subprocess
import textwrap


SOURCE_PATH = Path("/workspace/packet_parser.c")
PACKET_PATH = Path("/workspace/test_packet.bin")
SOLUTION_PATH = Path("/workspace/solution.txt")
EXPECTED_LINES = [
    "SEQUENCE_NUMBER=305419896",
    "PAYLOAD_LENGTH=256",
    "CHECKSUM=0xABCD",
]


def read_solution_lines() -> list[str]:
    assert SOLUTION_PATH.exists(), f"Missing {SOLUTION_PATH}"
    lines = SOLUTION_PATH.read_text(encoding="utf-8").splitlines()
    assert lines == EXPECTED_LINES, f"Unexpected solution.txt contents: {lines!r}"
    return lines


def compile_packet_parser(output_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gcc", "-Wall", "-Wextra", "-Werror", "-o", str(output_path), str(SOURCE_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_solution_file_matches_expected_lines() -> None:
    read_solution_lines()


def test_source_compiles_cleanly_and_outputs_expected_values() -> None:
    binary_path = Path("/tmp/packet_parser_check")
    compile_result = compile_packet_parser(binary_path)
    assert compile_result.returncode == 0, (
        f"Compilation failed:\nstdout: {compile_result.stdout}\nstderr: {compile_result.stderr}"
    )
    assert compile_result.stderr.strip() == "", (
        f"Compilation emitted warnings or errors:\n{compile_result.stderr}"
    )

    run_result = subprocess.run(
        [str(binary_path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )
    assert run_result.returncode == 0, (
        f"Compiled parser failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )
    assert run_result.stdout.splitlines() == EXPECTED_LINES, (
        f"Unexpected parser output: {run_result.stdout!r}"
    )


def test_struct_layout_matches_the_protocol() -> None:
    assert SOURCE_PATH.exists(), f"Missing {SOURCE_PATH}"
    assert PACKET_PATH.exists(), f"Missing {PACKET_PATH}"

    layout_check_path = Path("/tmp/layout_check.c")
    layout_check_path.write_text(
        textwrap.dedent(
            """
            #include <stddef.h>
            #define main packet_parser_original_main
            #include "/workspace/packet_parser.c"
            #undef main

            _Static_assert(sizeof(struct NetworkPacket) == 15, "NetworkPacket size must be 15");
            _Static_assert(offsetof(struct NetworkPacket, version) == 0, "version offset");
            _Static_assert(offsetof(struct NetworkPacket, type) == 1, "type offset");
            _Static_assert(offsetof(struct NetworkPacket, sequence) == 2, "sequence offset");
            _Static_assert(offsetof(struct NetworkPacket, length) == 6, "length offset");
            _Static_assert(offsetof(struct NetworkPacket, flags) == 8, "flags offset");
            _Static_assert(offsetof(struct NetworkPacket, checksum) == 9, "checksum offset");
            _Static_assert(offsetof(struct NetworkPacket, reserved) == 11, "reserved offset");

            int main(void) {
                return 0;
            }
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    compile_result = subprocess.run(
        ["gcc", "-Wall", "-Wextra", "-Werror", "-o", "/tmp/layout_check", str(layout_check_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert compile_result.returncode == 0, (
        f"Layout check failed:\nstdout: {compile_result.stdout}\nstderr: {compile_result.stderr}"
    )
