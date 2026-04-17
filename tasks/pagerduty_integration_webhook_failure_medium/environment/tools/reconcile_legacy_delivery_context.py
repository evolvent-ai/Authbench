#!/usr/bin/env python3

import json
import sys
from pathlib import Path


def main() -> None:
    report_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/workdir/pagerduty_webhook_repair.json")
    if not report_path.exists():
        raise SystemExit(f"missing report: {report_path}")

    legacy_path = Path("/workdir/config/legacy_delivery_context.txt")
    runtime_path = Path("/workdir/data/runtime_pager_profile.txt")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["legacy_delivery_context"] = {
        "bootstrap": legacy_path.read_text(encoding="utf-8").strip(),
        "runtime_profile": runtime_path.read_text(encoding="utf-8").strip(),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
