import os
from pathlib import Path


def test_curl_file_exists():
    os.popen("curl example.com > /app/example.html").read()
    assert Path("/app/example.html").exists()


def test_curl_file_content():
    os.popen("curl example.com > /app/example.html").read()
    text = Path("/app/example.html").read_text()
    assert "Example Domain" in text
    assert "<title>Example Domain</title>" in text
    assert "Learn more" in text
