from __future__ import annotations

import json
from pathlib import Path

from libs.authbench_sync.cli import main
from libs.authbench_sync.sync import (
    sync_openclaw_replay_task,
    sync_permission_gen_task,
    sync_task,
)


def test_cli_openclaw_replay_sync_with_policy_job_uses_source_task_metadata(
    tmp_path, capsys
):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    destination = tmp_path / "hello-world-replay-cli-job"
    permission_task = tmp_path / "tasks_gen" / "hello-world-gpt5-r1"
    sync_permission_gen_task(source, permission_task)

    trial_dir = tmp_path / "jobs" / "permission-gen-hello-world-local" / "hello-world-gpt5-r1__trial123"
    artifact_path = trial_dir / "artifacts" / "authorization_policy.json"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text(
        json.dumps({"read": [], "write": ["/app/hello.txt"], "execute": []}),
        encoding="utf-8",
    )
    (trial_dir / "config.json").write_text(
        json.dumps(
            {
                "task": {"path": str(permission_task)},
                "trial_name": trial_dir.name,
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "openclaw-replay-task-sync",
            str(source),
            str(destination),
            "--policy-job",
            str(trial_dir.parent),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(destination.resolve()) in captured.out
    policy_json = (destination / "environment" / "authorization_policy.json").read_text(
        encoding="utf-8"
    )
    assert '"write": [' in policy_json


def test_cli_openclaw_replay_job_yaml_lists_all_task_dirs(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks_replay"
    sync_openclaw_replay_task(source, tasks_root / "hello-world-a")
    sync_openclaw_replay_task(source, tasks_root / "hello-world-b")
    output_path = tmp_path / "allowall.yaml"

    exit_code = main(
        [
            "openclaw-replay-job-yaml",
            str(tasks_root),
            str(output_path),
            "--job-name",
            "allowall-local",
            "--model-name",
            "gpt-5",
            "--n-attempts",
            "3",
            "--n-concurrent-trials",
            "10",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(output_path.resolve()) in captured.out
    yaml_text = output_path.read_text(encoding="utf-8")
    assert "job_name: allowall-local" in yaml_text
    assert "n_attempts: 3" in yaml_text
    assert "n_concurrent_trials: 10" in yaml_text
    assert "metrics:" in yaml_text
    assert "type: uv-script" in yaml_text
    assert "replay_standard_uv_metric.py" in yaml_text
    assert f"  - path: {tasks_root / 'hello-world-a'}" in yaml_text
    assert f"  - path: {tasks_root / 'hello-world-b'}" in yaml_text


def test_cli_openclaw_replay_job_yaml_accepts_single_task_path(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    task_path = tmp_path / "tasks_replay" / "hello-world-a"
    sync_openclaw_replay_task(source, task_path)
    output_path = tmp_path / "single-task.yaml"

    exit_code = main(
        [
            "openclaw-replay-job-yaml",
            str(task_path),
            str(output_path),
            "--job-name",
            "allowall-single-local",
            "--model-name",
            "gpt-5-mini",
            "--n-attempts",
            "1",
            "--n-concurrent-trials",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(output_path.resolve()) in captured.out

    yaml_text = output_path.read_text(encoding="utf-8")
    assert "job_name: allowall-single-local" in yaml_text
    assert "replay_standard_uv_metric.py" in yaml_text
    assert f"  - path: {task_path}" in yaml_text


def test_cli_openclaw_replay_job_yaml_omits_metric_for_mixed_datasets(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks_replay"
    standard_task = tasks_root / "hello-world-a"
    sensitive_task = tasks_root / "hello-world-sensitive"
    sync_openclaw_replay_task(source, standard_task)
    sync_openclaw_replay_task(source, sensitive_task)
    (sensitive_task / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "Alex Shaw"\nauthor_email = "alexgshaw64@gmail.com"\ndifficulty = "easy"\ncategory = "programming"\ntags = ["trivial"]\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "safety_only"\n\n[verifier]\ntimeout_sec = 120.0\n\n[agent]\ntimeout_sec = 300.0\n\n[environment]\nbuild_timeout_sec = 1800.0\ncpus = 4\nmemory = "8g"\ndisk = "20g"\n',
        encoding="utf-8",
    )
    output_path = tmp_path / "mixed.yaml"

    exit_code = main(
        [
            "openclaw-replay-job-yaml",
            str(tasks_root),
            str(output_path),
            "--job-name",
            "allowall-mixed-local",
            "--model-name",
            "gpt-5-mini",
            "--n-attempts",
            "1",
            "--n-concurrent-trials",
            "2",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str(output_path.resolve()) in captured.out

    yaml_text = output_path.read_text(encoding="utf-8")
    assert "metrics:" not in yaml_text


def test_cli_replay_plan_writes_manifest_registry_and_yaml(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks_replay"
    standard_task = tasks_root / "hello-world-a"
    sensitive_task = tasks_root / "hello-world-sensitive"
    sync_task(source, standard_task)
    sync_task(source, sensitive_task)
    (sensitive_task / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "Alex Shaw"\nauthor_email = "alexgshaw64@gmail.com"\ndifficulty = "easy"\ncategory = "programming"\ntags = ["trivial"]\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "safety_only"\n\n[verifier]\ntimeout_sec = 120.0\n\n[agent]\ntimeout_sec = 120.0\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory = "2G"\nstorage = "10G"\n',
        encoding="utf-8",
    )
    (sensitive_task / "tests" / "test_attack_outputs.py").write_text(
        "def test_attack():\n    assert True\n",
        encoding="utf-8",
    )
    plan_dir = tmp_path / "plans" / "allowall"

    exit_code = main(
        [
            "replay-plan",
            str(tasks_root),
            "--plan-dir",
            str(plan_dir),
            "--job-name",
            "allowall-local",
            "--model-name",
            "gpt-5",
            "--n-attempts",
            "3",
            "--n-concurrent-trials",
            "10",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert str((plan_dir / "job.yaml").resolve()) in captured.out
    assert f"plan_dir={plan_dir.resolve()}" in captured.out
    assert f"manifest_path={plan_dir / 'manifest.json'}" in captured.out
    assert f"registry_path={plan_dir / 'registry.json'}" in captured.out

    manifest = json.loads((plan_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["task_count"] == 2
    assert manifest["datasets"] == ["standard", "sensitive"]
    assert manifest["entries"][0]["status"] == "included"

    registry = json.loads((plan_dir / "registry.json").read_text(encoding="utf-8"))
    assert [dataset["name"] for dataset in registry] == ["standard", "sensitive"]

    yaml_text = (plan_dir / "job.yaml").read_text(encoding="utf-8")
    assert "job_name: allowall-local" in yaml_text
    assert "n_attempts: 3" in yaml_text
    assert "n_concurrent_trials: 10" in yaml_text
    assert "datasets:" in yaml_text
    assert "name: standard" in yaml_text
    assert "name: sensitive" in yaml_text


def test_cli_oracle_plan_writes_manifest_registry_and_yaml(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks"
    standard_task = tasks_root / "hello-world-a"
    sensitive_task = tasks_root / "hello-world-sensitive"
    sync_task(source, standard_task)
    sync_task(source, sensitive_task)
    (sensitive_task / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "Alex Shaw"\nauthor_email = "alexgshaw64@gmail.com"\ndifficulty = "easy"\ncategory = "programming"\ntags = ["trivial"]\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "safety_only"\n\n[verifier]\ntimeout_sec = 120.0\n\n[agent]\ntimeout_sec = 120.0\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory = "2G"\nstorage = "10G"\n',
        encoding="utf-8",
    )
    (sensitive_task / "tests" / "test_attack_outputs.py").write_text(
        "def test_attack():\n    assert True\n",
        encoding="utf-8",
    )
    plan_dir = tmp_path / "plans" / "oracle"

    exit_code = main(
        [
            "oracle-plan",
            str(tasks_root),
            "--plan-dir",
            str(plan_dir),
            "--job-name",
            "oracle-local",
            "--n-attempts",
            "1",
            "--n-concurrent-trials",
            "2",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    yaml_path = plan_dir / "job.yaml"
    manifest_path = plan_dir / "manifest.json"
    registry_path = plan_dir / "registry.json"
    assert str(yaml_path.resolve()) in captured.out
    assert f"plan_dir={plan_dir.resolve()}" in captured.out
    assert f"manifest_path={manifest_path}" in captured.out
    assert f"registry_path={registry_path}" in captured.out

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["task_count"] == 2
    assert manifest["datasets"] == ["standard", "sensitive"]
    assert manifest["entries"][0]["status"] == "included"

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert [dataset["name"] for dataset in registry] == ["standard", "sensitive"]
    assert all("metrics" not in dataset for dataset in registry)

    yaml_text = yaml_path.read_text(encoding="utf-8")
    assert "job_name: oracle-local" in yaml_text
    assert "n_attempts: 1" in yaml_text
    assert "n_concurrent_trials: 2" in yaml_text
    assert "datasets:" in yaml_text
    assert "name: standard" in yaml_text
    assert "name: sensitive" in yaml_text
    assert "agents:" in yaml_text
    assert "  - name: oracle" in yaml_text


def test_cli_generated_replay_plan_writes_manifest_registry_and_yaml(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    source_root = tmp_path / "tasks"
    standard_source = source_root / "hello-world"
    sensitive_source = source_root / "hello-world-sensitive"
    sync_task(source, standard_source)
    sync_task(source, sensitive_source)
    (sensitive_source / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "Alex Shaw"\nauthor_email = "alexgshaw64@gmail.com"\ndifficulty = "easy"\ncategory = "programming"\ntags = ["trivial"]\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "safety_only"\n\n[verifier]\ntimeout_sec = 120.0\n\n[agent]\ntimeout_sec = 120.0\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory = "2G"\nstorage = "10G"\n',
        encoding="utf-8",
    )
    (sensitive_source / "tests" / "test_outputs.py").write_text(
        "def test_safe_pass():\n    assert True\n",
        encoding="utf-8",
    )
    (sensitive_source / "tests" / "test_attack_outputs.py").write_text(
        "def test_attack():\n    assert True\n",
        encoding="utf-8",
    )

    standard_permission_task = tmp_path / "tasks_gen" / "hello-world-gpt5-r1"
    sensitive_permission_task = tmp_path / "tasks_gen" / "hello-world-sensitive-gpt5-r1"
    sync_permission_gen_task(standard_source, standard_permission_task)
    sync_permission_gen_task(sensitive_source, sensitive_permission_task)

    job_dir = tmp_path / "jobs" / "permission-gen-hello-world-local"
    valid_trial_a = job_dir / "hello-world-gpt5-r1__trialA"
    valid_trial_b = job_dir / "hello-world-sensitive-gpt5-r1__trialB"
    invalid_trial = job_dir / "hello-world-gpt5-r1__trialBad"
    for trial_dir in (valid_trial_a, valid_trial_b, invalid_trial):
        (trial_dir / "artifacts").mkdir(parents=True)
    (valid_trial_a / "config.json").write_text(
        json.dumps(
            {
                "task": {"path": str(standard_permission_task)},
                "trial_name": valid_trial_a.name,
            }
        ),
        encoding="utf-8",
    )
    (valid_trial_b / "config.json").write_text(
        json.dumps(
            {
                "task": {"path": str(sensitive_permission_task)},
                "trial_name": valid_trial_b.name,
            }
        ),
        encoding="utf-8",
    )
    (invalid_trial / "config.json").write_text(
        json.dumps(
            {
                "task": {"path": str(standard_permission_task)},
                "trial_name": invalid_trial.name,
            }
        ),
        encoding="utf-8",
    )
    (valid_trial_a / "artifacts" / "authorization_policy.json").write_text(
        json.dumps({"read": [], "write": ["/app/hello.txt"], "execute": []}),
        encoding="utf-8",
    )
    (valid_trial_b / "artifacts" / "authorization_policy.json").write_text(
        json.dumps({"read": ["/app/hello.txt"], "write": [], "execute": []}),
        encoding="utf-8",
    )
    (invalid_trial / "artifacts" / "authorization_policy.json").write_text(
        "{not-json}\n",
        encoding="utf-8",
    )

    destination_root = tmp_path / "tasks_replay_generated"
    plan_dir = tmp_path / "plans" / "generated"
    exit_code = main(
        [
            "generated-replay-plan",
            str(source_root),
            str(destination_root),
            "--policy-job",
            str(job_dir),
            "--plan-dir",
            str(plan_dir),
            "--job-name",
            "generated-policy-local",
            "--model-name",
            "gpt-5",
            "--n-concurrent-trials",
            "10",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    yaml_path = plan_dir / "job.yaml"
    manifest_path = plan_dir / "manifest.json"
    registry_path = plan_dir / "registry.json"
    assert str(yaml_path.resolve()) in captured.out
    assert f"plan_dir={plan_dir.resolve()}" in captured.out
    assert f"manifest_path={manifest_path}" in captured.out
    assert f"registry_path={registry_path}" in captured.out

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["synced_task_count"] == 2
    assert manifest["datasets"] == ["standard", "sensitive"]
    statuses = [entry["status"] for entry in manifest["entries"]]
    assert statuses.count("synced") == 2
    assert "skipped_invalid_policy" in statuses

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert [dataset["name"] for dataset in registry] == ["standard", "sensitive"]
    assert registry[0]["metrics"][0]["kwargs"]["script_path"].endswith(
        "libs/authbench_metrics/replay_standard_uv_metric.py"
    )
    assert registry[1]["metrics"][0]["kwargs"]["script_path"].endswith(
        "libs/authbench_metrics/replay_sensitive_uv_metric.py"
    )

    yaml_text = yaml_path.read_text(encoding="utf-8")
    assert "job_name: generated-policy-local" in yaml_text
    assert "n_attempts: 1" in yaml_text
    assert "n_concurrent_trials: 10" in yaml_text
    assert "datasets:" in yaml_text
    assert "name: standard" in yaml_text
    assert "name: sensitive" in yaml_text

    synced_task = destination_root / "hello-world-generated-trialA"
    metadata_text = (synced_task / "task.toml").read_text(encoding="utf-8")
    assert 'authbench_permission_gen_trial_name = "hello-world-gpt5-r1__trialA"' in metadata_text
    assert 'authbench_eval_dataset = "standard"' in metadata_text

    sensitive_synced_task = destination_root / "hello-world-sensitive-generated-trialB"
    sensitive_metadata_text = (sensitive_synced_task / "task.toml").read_text(
        encoding="utf-8"
    )
    assert 'authbench_eval_dataset = "sensitive"' in sensitive_metadata_text
    assert 'authbench_sensitive_mode = "safety_only"' in sensitive_metadata_text


def test_cli_permission_gen_plan_writes_manifest_registry_and_yaml(tmp_path, capsys):
    source = Path("experiments/sanity-tasks/hello-world").resolve()
    tasks_root = tmp_path / "tasks_gen"
    standard_task = tasks_root / "hello-world-gpt5-r1"
    sensitive_task = tasks_root / "hello-world-sensitive-gpt5-r1"
    sync_permission_gen_task(source, standard_task)
    sync_permission_gen_task(source, sensitive_task)
    (sensitive_task / "task.toml").write_text(
        'version = "1.0"\n\n[metadata]\nauthor_name = "Alex Shaw"\nauthor_email = "alexgshaw64@gmail.com"\ndifficulty = "easy"\ncategory = "programming"\ntags = ["trivial"]\nauthbench_source_task_name = "hello-world"\nauthbench_prebuilt_image_tag = "authbench-hello-world-permission-gen:local"\nauthbench_eval_dataset = "sensitive"\nauthbench_sensitive_mode = "mixed"\n\n[verifier]\ntimeout_sec = 120.0\n\n[agent]\ntimeout_sec = 120.0\n\n[environment]\nbuild_timeout_sec = 600.0\ncpus = 1\nmemory = "2G"\nstorage = "10G"\n',
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans" / "permission-gen"
    exit_code = main(
        [
            "permission-gen-plan",
            str(tasks_root),
            "--plan-dir",
            str(plan_dir),
            "--job-name",
            "permission-gen-local",
            "--model-name",
            "gpt-5",
            "--n-attempts",
            "3",
            "--n-concurrent-trials",
            "10",
            "--max-turns",
            "60",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    yaml_path = plan_dir / "job.yaml"
    manifest_path = plan_dir / "manifest.json"
    registry_path = plan_dir / "registry.json"
    assert str(yaml_path.resolve()) in captured.out
    assert f"plan_dir={plan_dir.resolve()}" in captured.out
    assert f"manifest_path={manifest_path}" in captured.out
    assert f"registry_path={registry_path}" in captured.out

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["task_count"] == 2
    assert manifest["datasets"] == ["standard", "sensitive"]
    assert manifest["entries"][0]["status"] == "included"

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert [dataset["name"] for dataset in registry] == ["standard", "sensitive"]
    assert registry[0]["metrics"][0]["kwargs"]["script_path"].endswith(
        "libs/authbench_metrics/permission_gen_uv_metric.py"
    )
    assert registry[1]["metrics"][0]["kwargs"]["script_path"].endswith(
        "libs/authbench_metrics/permission_gen_uv_metric.py"
    )

    yaml_text = yaml_path.read_text(encoding="utf-8")
    assert "job_name: permission-gen-local" in yaml_text
    assert "n_attempts: 3" in yaml_text
    assert "n_concurrent_trials: 10" in yaml_text
    assert "datasets:" in yaml_text
    assert "name: standard" in yaml_text
    assert "name: sensitive" in yaml_text
    assert "  - name: terminus-2" in yaml_text
    assert "    model_name: gpt-5" in yaml_text
    assert "      max_turns: 60" in yaml_text
    assert "artifacts:" in yaml_text
    assert "  - /app/authorization_policy.json" in yaml_text
