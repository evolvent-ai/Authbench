from __future__ import annotations

import json
from pathlib import Path

from libs.authbench_metrics.formal_experiments import (
    AUTHBENCH_ARTIFACTS_ROOT_ENV,
    AUTHBENCH_FORMAL_EXP_ROOT_ENV,
    AUTHBENCH_FORMAL_EXP_SUMMARY_HTML_ENV,
    AUTHBENCH_HARBOR_JOBS_ROOT_ENV,
    collect_records,
    count_openclaw_turns,
    formalize_experiment_bundle,
    get_default_formal_experiment_root,
    get_default_formal_experiment_summary_html,
    get_default_harbor_jobs_root,
    render_html,
    resolve_job_dir,
    slugify_model,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_slugify_model_normalizes_name() -> None:
    assert slugify_model("gpt-5") == "gpt_5"


def test_count_openclaw_turns_counts_assistant_tool_messages() -> None:
    events = [
        {"type": "session"},
        {"type": "message", "message": {"role": "assistant", "content": [{"type": "text", "text": "thinking"}]}},
        {"type": "message", "message": {"role": "assistant", "content": [{"type": "toolCall", "name": "exec"}]}},
        {"type": "message", "message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read"}]}},
    ]
    assert count_openclaw_turns(events) == 2


def test_default_formal_experiment_paths_follow_artifacts_root(monkeypatch, tmp_path: Path) -> None:
    artifacts_root = tmp_path / "artifacts"
    monkeypatch.setenv(AUTHBENCH_ARTIFACTS_ROOT_ENV, str(artifacts_root))
    monkeypatch.delenv(AUTHBENCH_FORMAL_EXP_ROOT_ENV, raising=False)
    monkeypatch.delenv(AUTHBENCH_FORMAL_EXP_SUMMARY_HTML_ENV, raising=False)

    assert get_default_formal_experiment_root() == artifacts_root / "formal_exp_job"
    assert get_default_formal_experiment_summary_html() == artifacts_root / "reports" / "formal_exp_summary.html"


def test_default_formal_experiment_paths_allow_explicit_overrides(monkeypatch, tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundles"
    summary_html = tmp_path / "reports" / "summary.html"
    monkeypatch.setenv(AUTHBENCH_FORMAL_EXP_ROOT_ENV, str(bundle_root))
    monkeypatch.setenv(AUTHBENCH_FORMAL_EXP_SUMMARY_HTML_ENV, str(summary_html))

    assert get_default_formal_experiment_root() == bundle_root
    assert get_default_formal_experiment_summary_html() == summary_html


def test_default_harbor_jobs_root_uses_env_override(monkeypatch, tmp_path: Path) -> None:
    jobs_root = tmp_path / "external-jobs"
    monkeypatch.setenv(AUTHBENCH_HARBOR_JOBS_ROOT_ENV, str(jobs_root))

    assert get_default_harbor_jobs_root() == jobs_root


def test_resolve_job_dir_accepts_bare_name_under_jobs_root(tmp_path: Path) -> None:
    job_dir = tmp_path / "jobs" / "permission-gen-r1"
    job_dir.mkdir(parents=True)

    assert resolve_job_dir("permission-gen-r1", jobs_root=tmp_path / "jobs") == job_dir.resolve()


def test_resolve_job_dir_accepts_explicit_path(tmp_path: Path) -> None:
    job_dir = tmp_path / "jobs" / "replay-r1"
    job_dir.mkdir(parents=True)

    assert resolve_job_dir(job_dir, jobs_root=tmp_path / "other-jobs") == job_dir.resolve()


def test_formalize_bundle_and_render_html(tmp_path: Path) -> None:
    permission_job = tmp_path / "jobs" / "permission-gen"
    permission_trial = permission_job / "trial-1"
    _write_json(permission_trial / "config.json", {})
    _write_json(permission_trial / "result.json", {})
    _write_json(
        permission_trial / "verifier" / "reward.json",
        {
            "reward": 1,
            "step_total": 2,
            "read_f1": 0.0,
            "write_f1": 1.0,
            "execute_f1": 0.8,
            "sensitive_exposure_coverage": 0.25,
        },
    )
    _write_json(permission_trial / "agent" / "trajectory.json", [{"type": "episode"}])
    _write_json(permission_trial / "artifacts" / "authorization_policy.json", {"write": ["/app/shared"]})
    _write_json(permission_trial / "artifacts" / "manifest.json", {"ok": True})
    _write_text(permission_trial / "verifier" / "test-stdout.txt", "ok\n")
    _write_text(permission_trial / "trial.log", "trial\n")
    _write_text(permission_trial / "agent" / "episode-0" / "prompt.txt", "prompt\n")
    _write_text(permission_trial / "agent" / "episode-0" / "response.txt", "response\n")
    _write_json(permission_trial / "agent" / "episode-0" / "debug.json", {"debug": True})

    replay_job = tmp_path / "jobs" / "replay-required"
    replay_trial = replay_job / "trial-1"
    _write_json(replay_trial / "config.json", {})
    _write_json(replay_trial / "result.json", {})
    _write_json(
        replay_trial / "agent" / "openclaw_agent_summary.json",
        {"enforcement_mode": "policy", "landlock_enabled": True},
    )
    _write_text(
        replay_trial / "agent" / "openclaw_trajectory.jsonl",
        json.dumps({"type": "message", "message": {"role": "assistant", "content": [{"type": "toolCall"}]}})
        + "\n",
    )
    _write_text(replay_trial / "agent" / "openclaw_stdout.log", "stdout\n")
    _write_text(replay_trial / "agent" / "openclaw_stderr.log", "stderr\n")
    _write_json(replay_trial / "agent" / "authorization_policy.json", {"write": ["/app/shared"]})
    _write_json(replay_trial / "agent" / "permission_eval_spec.json", {"required_permissions": {}})
    _write_text(replay_trial / "verifier" / "reward.txt", "1.0\n")
    _write_json(replay_trial / "verifier" / "security.json", {"utility_success": 1, "attack_success": 0})
    _write_text(replay_trial / "verifier" / "test-stdout.txt", "pass\n")
    _write_text(replay_trial / "trial.log", "trial\n")

    output_root = tmp_path / "formal_exp_job"
    bundle_dir = formalize_experiment_bundle(
        task_id="acl-permissions-inheritance",
        model="gpt-5",
        output_root=output_root,
        notes="replay-driven fix",
        permission_gen_job=permission_job,
        replay_required_job=replay_job,
    )

    assert (bundle_dir / "metadata.json").exists()
    assert (bundle_dir / "permission_gen" / "authorization_policy.json").exists()
    assert (bundle_dir / "permission_gen" / "episode-0_prompt.txt").exists()
    assert (bundle_dir / "replay_required" / "openclaw_trajectory.json").exists()
    assert (bundle_dir / "replay_required" / "security.json").exists()

    records = collect_records(output_root)
    assert len(records) == 1
    assert records[0]["stages"]["permission_gen"]["write_f1"] == 1.0
    assert records[0]["stages"]["permission_gen"]["sensitive_exposure_coverage"] == 0.25
    assert records[0]["stages"]["replay_required"]["turns"] == 1
    assert records[0]["stages"]["replay_required"]["attack_success"] == 0

    html_text = render_html(
        records,
        output_path=tmp_path / "experiments" / "formal_exp_summary.html",
        source_root=output_root,
    )
    assert "acl-permissions-inheritance" in html_text
    assert "replay-driven fix" in html_text
    assert "reward 1" in html_text
    assert "sensitive 0.25" in html_text
    assert "attack 0" in html_text
    assert str(output_root) in html_text
