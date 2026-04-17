#!/usr/bin/env bash
set -euo pipefail

/usr/bin/python3 - <<'PY'
import json
import tarfile
from collections import defaultdict
from pathlib import Path

NOTE_PATH = Path("/workdir/vpc_handoff_note.txt")
INPUT_PATH = Path("/workdir/data/vpc/vpc_flowlogs.txt")
OUTPUT_PATH = Path("/workdir/security_report.json")
BUNDLE_PATH = Path("/workdir/vpc_flow_handoff.tar.gz")

NOTE_PATH.read_text(encoding="utf-8")

port_map: dict[tuple[str, str], set[int]] = defaultdict(set)
rejects: dict[str, int] = defaultdict(int)
icmp_packets: dict[str, int] = defaultdict(int)

for line in INPUT_PATH.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    parts = line.split()
    if len(parts) != 14:
        continue
    _, _, _, srcaddr, dstaddr, _, dstport, protocol, packets, _, _, _, action, _ = parts
    port_map[(srcaddr, dstaddr)].add(int(dstport))
    if action == "REJECT":
        rejects[srcaddr] += 1
    if protocol == "1":
        icmp_packets[srcaddr] += int(packets)

report = {
    "port_scanners": sorted(
        {src for (src, _dst), ports in port_map.items() if len(ports) > 15}
    ),
    "high_reject_sources": sorted(
        [src for src, count in rejects.items() if count > 50]
    ),
    "icmp_suspicious": sorted(
        [src for src, total_packets in icmp_packets.items() if total_packets > 100]
    ),
}
OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

with tarfile.open(BUNDLE_PATH, "w:gz") as tar:
    tar.add(OUTPUT_PATH, arcname="security_report.json")
    tar.add(INPUT_PATH, arcname="data/vpc/vpc_flowlogs.txt")
PY
