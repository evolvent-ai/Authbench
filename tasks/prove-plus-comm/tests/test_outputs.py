from pathlib import Path
import subprocess


def test_proof_file_exists():
    assert Path("/app/plus_comm.v").exists(), "The proof file plus_comm.v should exist"


def test_compiled_proof_exists():
    assert Path("/app/plus_comm.vo").exists(), (
        "The compiled proof file plus_comm.vo should exist"
    )


def test_proof_contents():
    content = Path("/app/plus_comm.v").read_text(encoding="utf-8")
    assert "Theorem plus_comm" in content, "The theorem should be present"
    assert "n + m = m + n" in content, "The theorem statement should be preserved"
    assert "Proof." in content, "The file should contain a proof"
    assert "Qed." in content, "The proof should finish with Qed"
    assert "admit" not in content, "The proof should not contain admit"


def test_proof_compiles():
    result = subprocess.run(
        ["coqc", "/app/plus_comm.v"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Proof should compile without errors.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
