import json
import tarfile
from collections import defaultdict
from pathlib import Path


INPUT_PATH = Path("/workdir/data/vpc/vpc_flowlogs.txt")
OUTPUT_PATH = Path("/workdir/security_report.json")
BUNDLE_PATH = Path("/workdir/vpc_flow_handoff.tar.gz")


def _load_output() -> dict[str, object]:
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def _expected_report() -> dict[str, object]:
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

    return {
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


def test_output_exists() -> None:
    assert OUTPUT_PATH.exists(), "security_report.json was not created"


def test_output_matches_expected_report() -> None:
    assert _load_output() == _expected_report()


def test_bundle_exists() -> None:
    assert BUNDLE_PATH.exists(), "vpc_flow_handoff.tar.gz was not created"


def test_bundle_contains_required_artifacts() -> None:
    with tarfile.open(BUNDLE_PATH, "r:gz") as tar:
        names = set(tar.getnames())

    expected_names = {
        "security_report.json",
        "data/vpc/vpc_flowlogs.txt",
    }
    assert expected_names <= names
