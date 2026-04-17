from __future__ import annotations

import html
import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTHBENCH_ARTIFACTS_ROOT_ENV = "AUTHBENCH_ARTIFACTS_ROOT"
AUTHBENCH_FORMAL_EXP_ROOT_ENV = "AUTHBENCH_FORMAL_EXP_ROOT"
AUTHBENCH_FORMAL_EXP_SUMMARY_HTML_ENV = "AUTHBENCH_FORMAL_EXP_SUMMARY_HTML"
AUTHBENCH_HARBOR_JOBS_ROOT_ENV = "AUTHBENCH_HARBOR_JOBS_ROOT"
STAGE_ORDER = [
    "permission_gen",
    "replay_allowall",
    "replay_required",
    "replay_restricted",
    "replay_generated_policy",
]


def slugify_model(model: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", model.lower()).strip("_")


def get_default_artifacts_root() -> Path:
    configured = os.environ.get(AUTHBENCH_ARTIFACTS_ROOT_ENV)
    if configured:
        return Path(configured).expanduser()
    return REPO_ROOT.parent / "authbench-artifacts"


def get_default_formal_experiment_root() -> Path:
    configured = os.environ.get(AUTHBENCH_FORMAL_EXP_ROOT_ENV)
    if configured:
        return Path(configured).expanduser()
    return get_default_artifacts_root() / "formal_exp_job"


def get_default_formal_experiment_summary_html() -> Path:
    configured = os.environ.get(AUTHBENCH_FORMAL_EXP_SUMMARY_HTML_ENV)
    if configured:
        return Path(configured).expanduser()
    return get_default_artifacts_root() / "reports" / "formal_exp_summary.html"


def get_default_harbor_jobs_root() -> Path:
    configured = os.environ.get(AUTHBENCH_HARBOR_JOBS_ROOT_ENV)
    if configured:
        return Path(configured).expanduser()
    return REPO_ROOT / "jobs"


def resolve_job_dir(job: str | Path, *, jobs_root: Path | None = None) -> Path:
    raw_path = Path(job).expanduser()
    candidates: list[Path] = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.append(raw_path)
        candidates.append((jobs_root or get_default_harbor_jobs_root()) / raw_path)

    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()

    joined = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"Harbor job directory does not exist. Checked: {joined}")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def detect_single_trial(job_dir: Path) -> Path:
    trial_dirs = sorted(
        path
        for path in job_dir.iterdir()
        if path.is_dir() and (path / "config.json").exists() and (path / "result.json").exists()
    )
    if len(trial_dirs) != 1:
        raise ValueError(f"expected exactly one trial directory under {job_dir}, found {len(trial_dirs)}")
    return trial_dirs[0]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


def count_openclaw_turns(events: list[dict[str, Any]]) -> int:
    turns = 0
    for event in events:
        if event.get("type") != "message":
            continue
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        if any(isinstance(item, dict) and item.get("type") == "toolCall" for item in content):
            turns += 1
    return turns


def _copy_if_exists(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_permission_gen(job_dir: Path, stage_dir: Path) -> dict[str, Any]:
    trial_dir = detect_single_trial(job_dir)
    shutil.rmtree(stage_dir, ignore_errors=True)
    stage_dir.mkdir(parents=True, exist_ok=True)

    reward_path = trial_dir / "verifier" / "reward.json"
    reward = read_json(reward_path)

    _copy_if_exists(trial_dir / "artifacts" / "authorization_policy.json", stage_dir / "authorization_policy.json")
    _copy_if_exists(trial_dir / "artifacts" / "manifest.json", stage_dir / "manifest.json")
    _copy_if_exists(trial_dir / "agent" / "trajectory.json", stage_dir / "trajectory.json")
    _copy_if_exists(trial_dir / "verifier" / "reward.json", stage_dir / "reward.json")
    _copy_if_exists(trial_dir / "verifier" / "test-stdout.txt", stage_dir / "test_stdout.txt")
    _copy_if_exists(trial_dir / "trial.log", stage_dir / "trial.log")

    for episode_dir in sorted((trial_dir / "agent").glob("episode-*")):
        episode_name = episode_dir.name
        _copy_if_exists(episode_dir / "prompt.txt", stage_dir / f"{episode_name}_prompt.txt")
        _copy_if_exists(episode_dir / "response.txt", stage_dir / f"{episode_name}_response.txt")
        _copy_if_exists(episode_dir / "debug.json", stage_dir / f"{episode_name}_debug.json")

    summary = {
        "stage": "permission_gen",
        "reward": reward.get("reward"),
        "step_total": reward.get("step_total"),
        "read_f1": reward.get("read_f1"),
        "write_f1": reward.get("write_f1"),
        "execute_f1": reward.get("execute_f1"),
    }
    if "sensitive_exposure_coverage" in reward:
        summary["sensitive_exposure_coverage"] = reward.get("sensitive_exposure_coverage")
    write_json(stage_dir / "summary.json", summary)
    return summary


def _read_reward_text(path: Path) -> float:
    return float(path.read_text(encoding="utf-8").strip())


def _copy_replay(job_dir: Path, stage_dir: Path, stage_name: str) -> dict[str, Any]:
    trial_dir = detect_single_trial(job_dir)
    shutil.rmtree(stage_dir, ignore_errors=True)
    stage_dir.mkdir(parents=True, exist_ok=True)

    trajectory_events = load_jsonl(trial_dir / "agent" / "openclaw_trajectory.jsonl")
    write_json(stage_dir / "openclaw_trajectory.json", trajectory_events)

    _copy_if_exists(trial_dir / "agent" / "openclaw_agent_summary.json", stage_dir / "openclaw_agent_summary.json")
    _copy_if_exists(trial_dir / "agent" / "openclaw_stdout.log", stage_dir / "openclaw_stdout.log")
    _copy_if_exists(trial_dir / "agent" / "openclaw_stderr.log", stage_dir / "openclaw_stderr.log")
    _copy_if_exists(trial_dir / "agent" / "authorization_policy.json", stage_dir / "authorization_policy.json")
    _copy_if_exists(trial_dir / "agent" / "permission_eval_spec.json", stage_dir / "permission_eval_spec.json")
    _copy_if_exists(trial_dir / "verifier" / "reward.txt", stage_dir / "reward.txt")
    _copy_if_exists(trial_dir / "verifier" / "security.json", stage_dir / "security.json")
    _copy_if_exists(trial_dir / "verifier" / "test-stdout.txt", stage_dir / "test_stdout.txt")
    _copy_if_exists(trial_dir / "trial.log", stage_dir / "trial.log")

    reward = _read_reward_text(trial_dir / "verifier" / "reward.txt")
    agent_summary = read_json(trial_dir / "agent" / "openclaw_agent_summary.json")
    summary = {
        "stage": stage_name,
        "pass": reward > 0.0,
        "reward": reward,
        "turns": count_openclaw_turns(trajectory_events),
        "enforcement_mode": agent_summary.get("enforcement_mode"),
        "landlock_enabled": agent_summary.get("landlock_enabled"),
    }
    security_path = trial_dir / "verifier" / "security.json"
    if security_path.exists():
        security = read_json(security_path)
        if isinstance(security, dict) and "attack_success" in security:
            summary["attack_success"] = security.get("attack_success")
    write_json(stage_dir / "summary.json", summary)
    return summary


def formalize_experiment_bundle(
    *,
    task_id: str,
    model: str,
    output_root: Path,
    notes: str = "",
    permission_gen_job: Path | None = None,
    replay_allowall_job: Path | None = None,
    replay_required_job: Path | None = None,
    replay_restricted_job: Path | None = None,
    replay_generated_policy_job: Path | None = None,
) -> Path:
    model_dir = output_root / task_id / slugify_model(model)
    shutil.rmtree(model_dir, ignore_errors=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, Any] = {
        "task_id": task_id,
        "model": model,
        "model_slug": slugify_model(model),
        "notes": notes,
        "generated_at": datetime.now(UTC).isoformat(),
        "stages": {},
    }

    if permission_gen_job is not None:
        metadata["stages"]["permission_gen"] = _copy_permission_gen(permission_gen_job, model_dir / "permission_gen")
    if replay_allowall_job is not None:
        metadata["stages"]["replay_allowall"] = _copy_replay(
            replay_allowall_job, model_dir / "replay_allowall", "replay_allowall"
        )
    if replay_required_job is not None:
        metadata["stages"]["replay_required"] = _copy_replay(
            replay_required_job, model_dir / "replay_required", "replay_required"
        )
    if replay_restricted_job is not None:
        metadata["stages"]["replay_restricted"] = _copy_replay(
            replay_restricted_job, model_dir / "replay_restricted", "replay_restricted"
        )
    if replay_generated_policy_job is not None:
        metadata["stages"]["replay_generated_policy"] = _copy_replay(
            replay_generated_policy_job,
            model_dir / "replay_generated_policy",
            "replay_generated_policy",
        )

    write_json(model_dir / "metadata.json", metadata)
    return model_dir


def collect_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not root.exists():
        return records
    for metadata_path in sorted(root.glob("*/*/metadata.json")):
        metadata = read_json(metadata_path)
        stage_summaries: dict[str, Any] = {}
        for stage in STAGE_ORDER:
            summary_path = metadata_path.parent / stage / "summary.json"
            stage_summaries[stage] = read_json(summary_path) if summary_path.exists() else None
        records.append(
            {
                "task_id": metadata.get("task_id"),
                "model": metadata.get("model"),
                "notes": metadata.get("notes", ""),
                "bundle_path": metadata_path.parent,
                "stages": stage_summaries,
            }
        )
    return records


def _format_permission_gen_cell(record: dict[str, Any], output_path: Path) -> str:
    summary = record["stages"].get("permission_gen")
    if not summary:
        return '<td class="empty">-</td>'
    rel = html.escape(str(Path(os.path.relpath(record["bundle_path"] / "permission_gen", output_path.parent))))
    sensitive = summary.get("sensitive_exposure_coverage")
    sensitive_line = ""
    if sensitive is not None:
        sensitive_line = f'<br>sensitive {html.escape(str(sensitive))}'
    return (
        "<td>"
        f'<a href="{rel}">reward {summary["reward"]}</a><br>'
        f'steps {summary["step_total"]}<br>'
        f'F1 {summary["read_f1"]} / {summary["write_f1"]} / {summary["execute_f1"]}'
        f"{sensitive_line}"
        "</td>"
    )


def _format_replay_cell(record: dict[str, Any], stage: str, output_path: Path) -> str:
    summary = record["stages"].get(stage)
    if not summary:
        return '<td class="empty">-</td>'
    rel = html.escape(str(Path(os.path.relpath(record["bundle_path"] / stage, output_path.parent))))
    passed = bool(summary["pass"])
    if stage == "replay_restricted":
        label = "blocked" if not passed else "passed"
        badge_class = "ok" if not passed else "warn"
    else:
        label = "pass" if passed else "fail"
        badge_class = "ok" if passed else "bad"
    turns = summary.get("turns")
    attack = summary.get("attack_success")
    attack_line = ""
    if attack is not None:
        attack_line = f'<br>attack {html.escape(str(attack))}'
    return (
        "<td>"
        f'<a href="{rel}"><span class="badge {badge_class}">{html.escape(label)}</span></a><br>'
        f'turns {turns}<br>'
        f'{html.escape(str(summary.get("enforcement_mode")))}'
        f"{attack_line}"
        "</td>"
    )


def render_html(records: list[dict[str, Any]], *, output_path: Path, source_root: Path | None = None) -> str:
    total = len(records)
    required_total = sum(1 for record in records if record["stages"].get("replay_required"))
    required_pass = sum(1 for record in records if (record["stages"].get("replay_required") or {}).get("pass"))
    generated_total = sum(1 for record in records if record["stages"].get("replay_generated_policy"))
    generated_pass = sum(
        1 for record in records if (record["stages"].get("replay_generated_policy") or {}).get("pass")
    )

    rows: list[str] = []
    for record in records:
        bundle_rel = html.escape(str(Path(os.path.relpath(record["bundle_path"], output_path.parent))))
        rows.append(
            "<tr>"
            f'<td><a href="{bundle_rel}">{html.escape(str(record["task_id"]))}</a></td>'
            f"<td>{html.escape(str(record['model']))}</td>"
            f"{_format_permission_gen_cell(record, output_path)}"
            f"{_format_replay_cell(record, 'replay_allowall', output_path)}"
            f"{_format_replay_cell(record, 'replay_required', output_path)}"
            f"{_format_replay_cell(record, 'replay_restricted', output_path)}"
            f"{_format_replay_cell(record, 'replay_generated_policy', output_path)}"
            f"<td>{html.escape(str(record.get('notes', '')))}</td>"
            "</tr>"
        )

    generated_at = html.escape(datetime.now(UTC).isoformat())
    rendered_root = source_root if source_root is not None else Path("formal_exp_job")
    rendered_root_text = html.escape(str(rendered_root))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Formal Experiment Summary</title>
  <style>
    :root {{
      --bg: #f7f3ea;
      --fg: #1f1f1f;
      --muted: #6d665d;
      --table: #fffdf8;
      --line: #d8cdbd;
      --ok: #2f7d4a;
      --bad: #b13a2d;
      --warn: #8a6410;
      --accent: #0f4c5c;
    }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      background: linear-gradient(180deg, #efe7d8 0%, var(--bg) 35%, #f9f7f2 100%);
      color: var(--fg);
    }}
    main {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 38px;
      color: var(--accent);
    }}
    p {{
      margin: 0 0 20px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .card {{
      background: rgba(255, 253, 248, 0.85);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
      box-shadow: 0 8px 24px rgba(31, 31, 31, 0.05);
    }}
    .card .label {{
      display: block;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .card .value {{
      font-size: 28px;
      color: var(--accent);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--table);
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 14px 36px rgba(31, 31, 31, 0.08);
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
      font-size: 14px;
      line-height: 1.45;
    }}
    th {{
      background: #f2eadc;
      color: var(--accent);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      position: sticky;
      top: 0;
    }}
    tr:nth-child(even) td {{
      background: rgba(246, 240, 230, 0.45);
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      color: white;
    }}
    .badge.ok {{
      background: var(--ok);
    }}
    .badge.bad {{
      background: var(--bad);
    }}
    .badge.warn {{
      background: var(--warn);
    }}
    .empty {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Formal Experiment Summary</h1>
    <p>Scanned from <code>{rendered_root_text}</code>. Generated at {generated_at}.</p>
    <section class="cards">
      <div class="card"><span class="label">Bundles</span><span class="value">{total}</span></div>
      <div class="card"><span class="label">Required Replay Pass</span><span class="value">{required_pass}/{required_total}</span></div>
      <div class="card"><span class="label">Generated Policy Replay Pass</span><span class="value">{generated_pass}/{generated_total}</span></div>
    </section>
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Model</th>
          <th>Permission Gen</th>
          <th>Allow All</th>
          <th>Required</th>
          <th>Restricted</th>
          <th>Generated Policy</th>
          <th>Notes</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows) if rows else '<tr><td colspan="8" class="empty">No formal experiment bundles found.</td></tr>'}
      </tbody>
    </table>
  </main>
</body>
</html>
"""


def write_html_summary(*, root: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_text = render_html(collect_records(root), output_path=output_path, source_root=root)
    output_path.write_text(html_text, encoding="utf-8")
    return output_path
