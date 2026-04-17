from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .openclaw_replay import (
    DEFAULT_REPLAY_AGENT_TIMEOUT_SEC,
    DEFAULT_REPLAY_BUILD_TIMEOUT_SEC,
    DEFAULT_REPLAY_VERIFIER_TIMEOUT_SEC,
)
from .oracle_batch import (
    DEFAULT_ORACLE_JOBS_DIR,
    DEFAULT_ORACLE_PLAN_ROOT,
    materialize_oracle_plan,
)
from .permission_batch import (
    DEFAULT_PERMISSION_GEN_JOBS_DIR,
    DEFAULT_PERMISSION_GEN_MAX_TURNS,
    DEFAULT_PERMISSION_GEN_PLAN_ROOT,
    materialize_permission_gen_plan,
)
from .prebuild import prebuild_task_image

from .replay_batch import (
    DEFAULT_GENERATED_REPLAY_JOBS_DIR,
    DEFAULT_GENERATED_REPLAY_PLAN_ROOT,
    DEFAULT_REPLAY_PLAN_ROOT,
    list_task_dirs,
    materialize_generated_replay_plan,
    materialize_replay_plan,
    write_openclaw_replay_job_yaml,
)

from .sync import (
    DEFAULT_PERMISSION_GEN_PROMPT_PATH,
    sync_openclaw_replay_task,
    sync_permission_gen_task,
    sync_task,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="authbench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    task_sync = subparsers.add_parser("task-sync", help="Copy a Harbor task into a new location.")
    task_sync.add_argument("src", help="Source Harbor task directory.")
    task_sync.add_argument("dst", help="Destination task directory.")

    prefix_group = task_sync.add_mutually_exclusive_group()
    prefix_group.add_argument("--instruction-prefix", help="Inline text to prepend to instruction.md.")
    prefix_group.add_argument("--instruction-prefix-file", help="Read prefix text from a file.")

    permission_sync = subparsers.add_parser(
        "permission-gen-task-sync",
        help="Generate a permission-generation variant of a Harbor task.",
    )
    permission_sync.add_argument("src", help="Source Harbor task directory.")
    permission_sync.add_argument("dst", help="Destination generated task directory.")
    permission_sync.add_argument(
        "--prompt-file",
        default=str(DEFAULT_PERMISSION_GEN_PROMPT_PATH),
        help="Prompt template file that contains {task_instruction}.",
    )

    openclaw_replay_sync = subparsers.add_parser(
        "openclaw-replay-task-sync",
        help="Generate an OpenClaw replay-ready variant of a Harbor task.",
    )
    openclaw_replay_sync.add_argument("src", help="Source Harbor task directory.")
    openclaw_replay_sync.add_argument("dst", help="Destination generated task directory.")
    replay_policy_group = openclaw_replay_sync.add_mutually_exclusive_group()
    replay_policy_group.add_argument(
        "--policy-file",
        help="Optional strict file-rwx policy JSON used for policy replay; when omitted, replay runs in allow-all mode.",
    )
    replay_policy_group.add_argument(
        "--policy-job",
        help="Optional Harbor job name or job directory used to locate artifacts/authorization_policy.json for the source task.",
    )
    openclaw_replay_sync.add_argument(
        "--verifier-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_VERIFIER_TIMEOUT_SEC,
        help="Replay verifier timeout written into task.toml.",
    )
    openclaw_replay_sync.add_argument(
        "--agent-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_AGENT_TIMEOUT_SEC,
        help="Replay Harbor agent timeout written into task.toml. This is task-local, so one dataset job can still use per-task values.",
    )
    openclaw_replay_sync.add_argument(
        "--build-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_BUILD_TIMEOUT_SEC,
        help="Replay environment build timeout written into task.toml.",
    )

    replay_job_yaml = subparsers.add_parser(
        "openclaw-replay-job-yaml",
        help="Write a Harbor replay job YAML for a replay task root or a single replay task.",
    )
    replay_job_yaml.add_argument(
        "tasks_root",
        help="Root directory that contains replay task directories, or a single replay task directory.",
    )
    replay_job_yaml.add_argument("output", help="Destination Harbor YAML path.")
    replay_job_yaml.add_argument("--job-name", required=True, help="Harbor job_name to write.")
    replay_job_yaml.add_argument(
        "--model-name",
        default="gpt-5",
        help="Replay agent model_name to write into the Harbor YAML.",
    )
    replay_job_yaml.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Harbor n_attempts value.",
    )
    replay_job_yaml.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=1,
        help="Harbor n_concurrent_trials value.",
    )
    replay_job_yaml.add_argument(
        "--retry-max-retries",
        type=int,
        default=0,
        help="Harbor retry.max_retries value written into job.yaml.",
    )

    oracle_plan = subparsers.add_parser(
        "oracle-plan",
        help="Materialize a Harbor oracle-validation plan from a source task root or a single source task.",
    )
    oracle_plan.add_argument(
        "tasks_root",
        help="Root directory that contains source task directories, or a single source task directory.",
    )
    oracle_plan.add_argument(
        "--plan-dir",
        help=(
            "Output directory for manifest.json, registry.json, and job.yaml. "
            f"Default: {DEFAULT_ORACLE_PLAN_ROOT}/<job-name>"
        ),
    )
    oracle_plan.add_argument(
        "--job-name",
        required=True,
        help="Harbor job_name to write into the generated plan.",
    )
    oracle_plan.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Harbor n_attempts value written into job.yaml.",
    )
    oracle_plan.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=1,
        help="Harbor n_concurrent_trials value written into job.yaml.",
    )
    oracle_plan.add_argument(
        "--jobs-dir",
        default=str(DEFAULT_ORACLE_JOBS_DIR),
        help="Harbor jobs_dir value written into job.yaml.",
    )

    replay_plan = subparsers.add_parser(
        "replay-plan",
        help="Materialize a Harbor replay plan from a replay task root or a single replay task.",
    )
    replay_plan.add_argument(
        "tasks_root",
        help="Root directory that contains replay task directories, or a single replay task directory.",
    )
    replay_plan.add_argument(
        "--plan-dir",
        help=(
            "Output directory for manifest.json, registry.json, and job.yaml. "
            f"Default: {DEFAULT_REPLAY_PLAN_ROOT}/<job-name>"
        ),
    )
    replay_plan.add_argument(
        "--job-name",
        required=True,
        help="Harbor job_name to write into the generated plan.",
    )
    replay_plan.add_argument(
        "--model-name",
        default="gpt-5",
        help="Replay agent model_name to write into job.yaml.",
    )
    replay_plan.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Harbor n_attempts value written into job.yaml.",
    )
    replay_plan.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=1,
        help="Harbor n_concurrent_trials value written into job.yaml.",
    )
    replay_plan.add_argument(
        "--jobs-dir",
        default=str(DEFAULT_GENERATED_REPLAY_JOBS_DIR),
        help="Harbor jobs_dir value written into job.yaml.",
    )
    replay_plan.add_argument(
        "--retry-max-retries",
        type=int,
        default=0,
        help="Harbor retry.max_retries value written into job.yaml.",
    )

    generated_replay_plan = subparsers.add_parser(
        "generated-replay-plan",
        help="Materialize a generated-policy replay plan from a permission-gen Harbor job.",
    )
    generated_replay_plan.add_argument(
        "src_root",
        help="Root directory containing source tasks, usually tasks.",
    )
    generated_replay_plan.add_argument(
        "dst_root",
        help="Destination root for generated replay tasks.",
    )
    generated_replay_plan.add_argument(
        "--policy-job",
        required=True,
        help="Harbor permission-gen job name or job directory.",
    )
    generated_replay_plan.add_argument(
        "--plan-dir",
        help=(
            "Output directory for manifest.json, registry.json, and job.yaml. "
            f"Default: {DEFAULT_GENERATED_REPLAY_PLAN_ROOT}/<policy-job-name>"
        ),
    )
    generated_replay_plan.add_argument(
        "--job-name",
        required=True,
        help="Harbor job_name to write into the generated plan.",
    )
    generated_replay_plan.add_argument(
        "--model-name",
        default="gpt-5",
        help="Replay agent model_name to write into job.yaml.",
    )
    generated_replay_plan.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Harbor n_attempts value written into job.yaml.",
    )
    generated_replay_plan.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=10,
        help="Harbor n_concurrent_trials value written into job.yaml.",
    )
    generated_replay_plan.add_argument(
        "--jobs-dir",
        default=str(DEFAULT_GENERATED_REPLAY_JOBS_DIR),
        help="Harbor jobs_dir value written into job.yaml.",
    )
    generated_replay_plan.add_argument(
        "--retry-max-retries",
        type=int,
        default=0,
        help="Harbor retry.max_retries value written into job.yaml.",
    )
    generated_replay_plan.add_argument(
        "--verifier-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_VERIFIER_TIMEOUT_SEC,
        help="Replay verifier timeout written into each generated replay task.",
    )
    generated_replay_plan.add_argument(
        "--agent-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_AGENT_TIMEOUT_SEC,
        help="Replay Harbor agent timeout written into each generated replay task.",
    )
    generated_replay_plan.add_argument(
        "--build-timeout-sec",
        type=float,
        default=DEFAULT_REPLAY_BUILD_TIMEOUT_SEC,
        help="Replay environment build timeout written into each generated replay task.",
    )

    permission_gen_plan = subparsers.add_parser(
        "permission-gen-plan",
        help="Materialize a Harbor permission-generation plan from an existing tasks_gen root.",
    )
    permission_gen_plan.add_argument(
        "tasks_root",
        help="Root directory that contains permission-generation task directories.",
    )
    permission_gen_plan.add_argument(
        "--plan-dir",
        help=(
            "Output directory for manifest.json, registry.json, and job.yaml. "
            f"Default: {DEFAULT_PERMISSION_GEN_PLAN_ROOT}/<job-name>"
        ),
    )
    permission_gen_plan.add_argument(
        "--job-name",
        required=True,
        help="Harbor job_name to write into the generated plan.",
    )
    permission_gen_plan.add_argument(
        "--model-name",
        default="gpt-5",
        help="Permission-generation agent model_name to write into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--reasoning-effort",
        help="Optional permission-generation agent reasoning_effort to write into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Harbor n_attempts value written into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=1,
        help="Harbor n_concurrent_trials value written into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--jobs-dir",
        default=str(DEFAULT_PERMISSION_GEN_JOBS_DIR),
        help="Harbor jobs_dir value written into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--max-turns",
        type=int,
        default=DEFAULT_PERMISSION_GEN_MAX_TURNS,
        help="Permission-generation agent max_turns written into job.yaml.",
    )
    permission_gen_plan.add_argument(
        "--retry-max-retries",
        type=int,
        default=0,
        help="Harbor retry.max_retries value written into job.yaml.",
    )

    prebuild_task = subparsers.add_parser(
        "prebuild-task-image",
        help="Build a task image from the shared bases and write environment.docker_image into task.toml.",
    )
    prebuild_task.add_argument("task", help="Task directory to prebuild.")
    prebuild_task.add_argument(
        "--image-tag",
        help="Optional docker image tag. Defaults to authbench-<task-name>:local.",
    )

    return parser


def _read_prefix(args: argparse.Namespace) -> str | None:
    if args.instruction_prefix_file:
        return Path(args.instruction_prefix_file).read_text()
    return args.instruction_prefix


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "task-sync":
            task_path = sync_task(args.src, args.dst, instruction_prefix=_read_prefix(args))
        elif args.command == "permission-gen-task-sync":
            task_path = sync_permission_gen_task(
                args.src,
                args.dst,
                prompt_template_path=args.prompt_file,
            )
        elif args.command == "openclaw-replay-task-sync":
            task_path = sync_openclaw_replay_task(
                args.src,
                args.dst,
                policy_path=args.policy_file,
                policy_job=args.policy_job,
                verifier_timeout_sec=args.verifier_timeout_sec,
                agent_timeout_sec=args.agent_timeout_sec,
                build_timeout_sec=args.build_timeout_sec,
            )
        elif args.command == "openclaw-replay-job-yaml":
            task_dirs = list_task_dirs(args.tasks_root)
            task_path = write_openclaw_replay_job_yaml(
                task_dirs,
                args.output,
                job_name=args.job_name,
                model_name=args.model_name,
                n_attempts=args.n_attempts,
                n_concurrent_trials=args.n_concurrent_trials,
                retry_max_retries=args.retry_max_retries,
            )
        elif args.command == "oracle-plan":
            resolved_plan_dir = (
                Path(args.plan_dir).expanduser().resolve()
                if args.plan_dir
                else (DEFAULT_ORACLE_PLAN_ROOT / args.job_name).resolve()
            )
            plan = materialize_oracle_plan(
                args.tasks_root,
                plan_dir=resolved_plan_dir,
                job_name=args.job_name,
                n_attempts=args.n_attempts,
                n_concurrent_trials=args.n_concurrent_trials,
                jobs_dir=args.jobs_dir,
            )
            print(f"plan_dir={plan.plan_dir}")
            print(f"manifest_path={plan.manifest_path}")
            print(f"registry_path={plan.registry_path}")
            task_path = plan.job_yaml_path
        elif args.command == "replay-plan":
            resolved_plan_dir = (
                Path(args.plan_dir).expanduser().resolve()
                if args.plan_dir
                else (DEFAULT_REPLAY_PLAN_ROOT / args.job_name).resolve()
            )
            plan = materialize_replay_plan(
                args.tasks_root,
                plan_dir=resolved_plan_dir,
                job_name=args.job_name,
                model_name=args.model_name,
                n_attempts=args.n_attempts,
                n_concurrent_trials=args.n_concurrent_trials,
                jobs_dir=args.jobs_dir,
                retry_max_retries=args.retry_max_retries,
            )
            print(f"plan_dir={plan.plan_dir}")
            print(f"manifest_path={plan.manifest_path}")
            print(f"registry_path={plan.registry_path}")
            task_path = plan.job_yaml_path
        elif args.command == "generated-replay-plan":
            resolved_plan_dir = (
                Path(args.plan_dir).expanduser().resolve()
                if args.plan_dir
                else (DEFAULT_GENERATED_REPLAY_PLAN_ROOT / Path(args.policy_job).name).resolve()
            )
            plan = materialize_generated_replay_plan(
                args.src_root,
                args.dst_root,
                policy_job=args.policy_job,
                plan_dir=resolved_plan_dir,
                job_name=args.job_name,
                model_name=args.model_name,
                n_attempts=args.n_attempts,
                n_concurrent_trials=args.n_concurrent_trials,
                jobs_dir=args.jobs_dir,
                verifier_timeout_sec=args.verifier_timeout_sec,
                agent_timeout_sec=args.agent_timeout_sec,
                build_timeout_sec=args.build_timeout_sec,
                retry_max_retries=args.retry_max_retries,
            )
            print(f"plan_dir={plan.plan_dir}")
            print(f"manifest_path={plan.manifest_path}")
            print(f"registry_path={plan.registry_path}")
            task_path = plan.job_yaml_path
        elif args.command == "permission-gen-plan":
            resolved_plan_dir = (
                Path(args.plan_dir).expanduser().resolve()
                if args.plan_dir
                else (DEFAULT_PERMISSION_GEN_PLAN_ROOT / args.job_name).resolve()
            )
            plan = materialize_permission_gen_plan(
                args.tasks_root,
                plan_dir=resolved_plan_dir,
                job_name=args.job_name,
                model_name=args.model_name,
                reasoning_effort=args.reasoning_effort,
                n_attempts=args.n_attempts,
                n_concurrent_trials=args.n_concurrent_trials,
                jobs_dir=args.jobs_dir,
                max_turns=args.max_turns,
                retry_max_retries=args.retry_max_retries,
            )
            print(f"plan_dir={plan.plan_dir}")
            print(f"manifest_path={plan.manifest_path}")
            print(f"registry_path={plan.registry_path}")
            task_path = plan.job_yaml_path
        elif args.command == "prebuild-task-image":
            image_tag, task_toml_path = prebuild_task_image(args.task, image_tag=args.image_tag)
            print(f"image_tag={image_tag}")
            task_path = task_toml_path
        else:
            parser.error(f"Unsupported command: {args.command}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(task_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
