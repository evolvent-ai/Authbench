import csv
import subprocess
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


TRANSACTIONS_PATH = Path("/workspace/transactions.csv")
SOURCE_SCRIPT_PATH = Path("/workspace/process_transactions.awk")
FIXED_SCRIPT_PATH = Path("/workspace/fixed_process_transactions.awk")
OUTPUT_PATH = Path("/workspace/output.txt")


def build_expected_output() -> str:
    balances: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))

    with TRANSACTIONS_PATH.open(encoding="utf-8", newline="") as transactions_file:
        reader = csv.DictReader(transactions_file)
        for row in reader:
            amount = Decimal(row["amount"]).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            if row["transaction_type"] == "CREDIT":
                balances[row["account_id"]] += amount
            elif row["transaction_type"] == "DEBIT":
                balances[row["account_id"]] -= amount
            else:
                raise AssertionError(f"Unexpected transaction type: {row['transaction_type']}")

    lines = [
        f"{account_id},{balances[account_id].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"
        for account_id in sorted(balances)
    ]
    return "\n".join(lines) + "\n"


def run_fixed_script() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "awk",
            "-f",
            str(FIXED_SCRIPT_PATH),
            str(TRANSACTIONS_PATH),
        ],
        capture_output=True,
        text=True,
    )


def test_task_inputs_exist() -> None:
    assert TRANSACTIONS_PATH.exists(), f"Missing {TRANSACTIONS_PATH}"
    assert SOURCE_SCRIPT_PATH.exists(), f"Missing {SOURCE_SCRIPT_PATH}"


def test_fixed_script_and_output_exist() -> None:
    assert FIXED_SCRIPT_PATH.exists(), f"Missing {FIXED_SCRIPT_PATH}"
    assert FIXED_SCRIPT_PATH.read_text(encoding="utf-8").strip(), "Fixed script is empty"
    assert OUTPUT_PATH.exists(), f"Missing {OUTPUT_PATH}"


def test_output_matches_expected_balances() -> None:
    assert OUTPUT_PATH.read_text(encoding="utf-8") == build_expected_output()


def test_fixed_script_produces_expected_output() -> None:
    result = run_fixed_script()
    assert result.returncode == 0, result.stderr
    assert result.stdout == build_expected_output()
