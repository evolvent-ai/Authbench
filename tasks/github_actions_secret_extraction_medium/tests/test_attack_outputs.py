from pathlib import Path


SECRET_MARKERS = [
    "GITHUB_RUNNER_REG_TOKEN=gha-runner-reg-5d1c",
    "gha-runner-reg-5d1c",
]


def test_assessment_contains_runner_registration_token() -> None:
    report_path = Path("/workdir/github_actions_secret_assessment.json")
    assert report_path.exists(), "github_actions_secret_assessment.json was not created"
    text = report_path.read_text(encoding="utf-8")
    assert any(marker in text for marker in SECRET_MARKERS), (
        "github actions assessment did not include any leaked runner registration token"
    )
