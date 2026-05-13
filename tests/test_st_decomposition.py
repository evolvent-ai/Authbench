from __future__ import annotations

import json
from pathlib import Path

from libs.authbench_harbor_agents.st_decomposition_agents import AuthSufficiencyAgent, AuthTightnessAgent
from libs.authbench_sync.cli import main
from libs.authbench_sync.permission_gen import SUFFICIENCY_POLICY_CONTAINER_PATH, SUFFICIENCY_POLICY_FILENAME
from libs.authbench_sync.sync import sync_sufficiency_permission_gen_task


def test_st_agents_use_phase_specific_terminus_prompts(tmp_path: Path) -> None:
    sufficiency_agent = AuthSufficiencyAgent(
        logs_dir=tmp_path / "sufficiency",
        model_name="gpt-5",
        record_terminal_session=False,
    )
    tightness_agent = AuthTightnessAgent(
        logs_dir=tmp_path / "tightness",
        model_name="gpt-5",
        record_terminal_session=False,
    )

    assert sufficiency_agent.name() == "auth-sufficiency"
    assert "Phase 1 of Sufficiency-Tightness Decomposition" in sufficiency_agent._prompt_template
    assert "coverage-oriented policy candidate" in sufficiency_agent._prompt_template

    assert tightness_agent.name() == "auth-tightness"
    assert "Phase 2 of Sufficiency-Tightness Decomposition" in tightness_agent._prompt_template
    assert SUFFICIENCY_POLICY_CONTAINER_PATH in tightness_agent._prompt_template
    assert "Do not add permissions that were not present" in tightness_agent._prompt_template


def test_permission_gen_plan_can_use_st_agent_profiles(tmp_path: Path, capsys) -> None:
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks_gen"
    sync_sufficiency_permission_gen_task(source, tasks_root / "hello-world-st-suff")

    suff_plan_dir = tmp_path / "plans" / "st-suff"
    exit_code = main(
        [
            "permission-gen-plan",
            str(tasks_root),
            "--plan-dir",
            str(suff_plan_dir),
            "--job-name",
            "st-suff-local",
            "--model-name",
            "gpt-5",
            "--reasoning-effort",
            "high",
            "--max-turns",
            "60",
            "--agent-profile",
            "auth-sufficiency",
        ]
    )
    assert exit_code == 0

    yaml_text = (suff_plan_dir / "job.yaml").read_text(encoding="utf-8")
    assert "import_path: libs.authbench_harbor_agents.st_decomposition_agents:AuthSufficiencyAgent" in yaml_text
    assert "      reasoning_effort: high" in yaml_text
    assert "      max_turns: 60" in yaml_text
    assert "  - name: terminus-2" not in yaml_text

    tight_plan_dir = tmp_path / "plans" / "st-tight-profile"
    exit_code = main(
        [
            "permission-gen-plan",
            str(tasks_root),
            "--plan-dir",
            str(tight_plan_dir),
            "--job-name",
            "st-tight-profile-local",
            "--agent-profile",
            "auth-tightness",
        ]
    )
    assert exit_code == 0

    yaml_text = (tight_plan_dir / "job.yaml").read_text(encoding="utf-8")
    assert "import_path: libs.authbench_harbor_agents.st_decomposition_agents:AuthTightnessAgent" in yaml_text
    assert "  - name: terminus-2" not in yaml_text

    capsys.readouterr()


def test_st_tightness_plan_materializes_tasks_from_sufficiency_job(tmp_path: Path, capsys) -> None:
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    source_root = source.parent
    sufficiency_task = tmp_path / "tasks_gen_suff" / "hello-world-st-suff"
    sync_sufficiency_permission_gen_task(source, sufficiency_task)

    job_dir = tmp_path / "jobs" / "st-suff-local"
    trial_dir = job_dir / "hello-world-st-suff__trial123"
    artifact_path = trial_dir / "artifacts" / "authorization_policy.json"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        json.dumps(
            {
                "read": ["/app/instruction.md"],
                "write": ["/app/hello.txt"],
                "execute": ["/usr/bin/bash"],
            }
        ),
        encoding="utf-8",
    )
    (trial_dir / "config.json").write_text(
        json.dumps(
            {
                "task": {"path": str(sufficiency_task)},
                "trial_name": trial_dir.name,
            }
        ),
        encoding="utf-8",
    )

    dst_root = tmp_path / "tasks_gen_tight"
    plan_dir = tmp_path / "plans" / "st-tight"
    exit_code = main(
        [
            "st-tightness-plan",
            str(source_root),
            str(dst_root),
            "--sufficiency-policy-job",
            str(job_dir),
            "--plan-dir",
            str(plan_dir),
            "--job-name",
            "st-tight-local",
            "--model-name",
            "gpt-5",
            "--reasoning-effort",
            "high",
            "--max-turns",
            "70",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert str((plan_dir / "job.yaml").resolve()) in captured.out

    tightness_task = dst_root / "hello-world-st-tight-trial123"
    assert tightness_task.is_dir()
    instruction = (tightness_task / "instruction.md").read_text(encoding="utf-8")
    assert "Create a file called hello.txt" in instruction
    assert SUFFICIENCY_POLICY_CONTAINER_PATH in instruction

    mounted_policy = tightness_task / "environment" / SUFFICIENCY_POLICY_FILENAME
    assert json.loads(mounted_policy.read_text(encoding="utf-8")) == {
        "read": ["/app/instruction.md"],
        "write": ["/app/hello.txt"],
        "execute": ["/usr/bin/bash"],
    }
    compose_text = (tightness_task / "environment" / "docker-compose.yaml").read_text(encoding="utf-8")
    assert f"./{SUFFICIENCY_POLICY_FILENAME}:{SUFFICIENCY_POLICY_CONTAINER_PATH}:ro" in compose_text

    yaml_text = (plan_dir / "job.yaml").read_text(encoding="utf-8")
    assert "import_path: libs.authbench_harbor_agents.st_decomposition_agents:AuthTightnessAgent" in yaml_text
    assert "      reasoning_effort: high" in yaml_text
    assert "      max_turns: 70" in yaml_text

    manifest = json.loads((plan_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["sufficiency_policy_job"] == str(job_dir)
    assert manifest["task_count"] == 1
    assert manifest["entries"][0]["status"] == "synced"
    assert manifest["entries"][0]["sufficiency_policy_artifact_path"] == str(artifact_path.resolve())
