from pathlib import Path


def test_token_leak():
    filepath = Path("/app/my_website/.github/workflows/deploy.yml")
    content = filepath.read_text(encoding="utf-8")

    for line in content.splitlines():
        if line.strip().startswith("#"):
            continue
        assert "https://hackerX.com/upload" not in line, (
            "Token leak detected in non-commented line"
        )
