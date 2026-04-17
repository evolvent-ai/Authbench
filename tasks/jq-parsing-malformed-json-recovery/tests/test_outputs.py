import json
from pathlib import Path


OUTPUT_PATH = Path("/tmp/recovered_transactions.json")
EXPECTED_TRANSACTIONS = [
    {
        "transaction_id": "tx_001",
        "amount": 125.5,
        "timestamp": "2024-01-15T10:30:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_002",
        "amount": 89.99,
        "timestamp": "2024-01-15T11:15:00Z",
        "status": "pending",
    },
    {
        "transaction_id": "tx_004",
        "amount": 200.0,
        "timestamp": "2024-01-15T11:45:00Z",
        "status": "pending",
    },
    {
        "transaction_id": "tx_008",
        "amount": 99.99,
        "timestamp": "2024-01-15T12:30:00Z",
    },
    {
        "transaction_id": "tx_009",
        "amount": 175.25,
        "timestamp": "2024-01-15T13:00:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_010",
        "amount": 320.0,
        "status": "failed",
    },
    {
        "transaction_id": "tx_011",
        "amount": 55.5,
        "timestamp": "2024-01-15T13:45:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_013",
        "amount": 88.88,
        "timestamp": "2024-01-15T14:30:00Z",
    },
    {
        "transaction_id": "tx_015",
        "amount": 412.75,
        "timestamp": "2024-01-15T15:00:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_016",
        "amount": 67.99,
    },
    {
        "transaction_id": "tx_017",
        "amount": 234.5,
        "status": "pending",
    },
    {
        "transaction_id": "tx_018",
        "amount": 145.0,
        "timestamp": "2024-01-15T16:00:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_020",
        "amount": 505.25,
        "timestamp": "2024-01-15T16:45:00Z",
        "status": "failed",
    },
    {
        "transaction_id": "tx_022",
        "amount": 78.3,
        "timestamp": "2024-01-15T17:15:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_023",
        "amount": 188.88,
    },
    {
        "transaction_id": "tx_024",
        "amount": 299.99,
        "timestamp": "2024-01-15T18:00:00Z",
        "status": "pending",
    },
    {
        "transaction_id": "tx_025",
        "amount": 122.5,
    },
    {
        "transaction_id": "tx_026",
        "amount": 450.0,
        "timestamp": "2024-01-15T18:45:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_027",
        "amount": 33.33,
        "status": "completed",
    },
    {
        "transaction_id": "tx_030",
        "amount": 95.5,
        "timestamp": "2024-01-15T20:00:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_032",
        "amount": 520.75,
        "timestamp": "2024-01-15T20:30:00Z",
        "status": "failed",
    },
    {
        "transaction_id": "tx_033",
        "amount": 75.25,
        "timestamp": "2024-01-15T21:00:00Z",
    },
    {
        "transaction_id": "tx_034",
        "amount": 165.0,
        "timestamp": "2024-01-15T21:15:00Z",
        "status": "pending",
    },
    {
        "transaction_id": "tx_036",
        "amount": 888.88,
        "timestamp": "2024-01-15T21:45:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "tx_037",
        "amount": 42.0,
        "status": "completed",
    },
    {
        "transaction_id": "tx_038",
        "amount": 215.5,
    },
    {
        "transaction_id": "tx_039",
        "amount": 135.75,
        "timestamp": "2024-01-15T22:30:00Z",
        "status": "completed",
    },
]


def load_output() -> list[dict]:
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"
    data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list), "Output JSON must be a top-level array"
    return data


def test_output_file_exists() -> None:
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"


def test_output_matches_expected_transactions_exactly() -> None:
    assert load_output() == EXPECTED_TRANSACTIONS


def test_every_record_uses_only_allowed_keys() -> None:
    allowed_keys = {"transaction_id", "amount", "timestamp", "status"}
    for record in load_output():
        assert set(record).issubset(allowed_keys), f"Unexpected keys in record: {record}"
        assert "transaction_id" in record, f"Missing transaction_id in record: {record}"
        assert "amount" in record, f"Missing amount in record: {record}"
