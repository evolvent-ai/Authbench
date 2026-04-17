#!/bin/bash
set -euo pipefail

cd /app

python3 - <<'PY'
from pathlib import Path

app = Path("/app")

_ = (app / "src" / "program.cbl").read_text(encoding="utf-8")

(app / "data" / "ACCOUNTS.DAT").write_text(
    "U001John Doe            0000001000"
    "U002Jane Smith          0000002000"
    "U003Bob Wilson          0000001500",
    encoding="utf-8",
)
(app / "data" / "BOOKS.DAT").write_text(
    "B001Python Basics       U001"
    "B002COBOL Guide         U002"
    "B003Java Tutorial       U003",
    encoding="utf-8",
)
(app / "data" / "TRANSACTIONS.DAT").write_text("", encoding="utf-8")
(app / "src" / "INPUT.DAT").write_text("U001U003B0030000000020", encoding="utf-8")
PY

cat > /app/program.py <<'PY'
from pathlib import Path

ACCOUNTS_PATH = Path("/app/data/ACCOUNTS.DAT")
BOOKS_PATH = Path("/app/data/BOOKS.DAT")
TRANSACTIONS_PATH = Path("/app/data/TRANSACTIONS.DAT")
INPUT_PATH = Path("/app/src/INPUT.DAT")

ACCOUNT_RECORD_LEN = 34
BOOK_RECORD_LEN = 28
TRANSACTION_RECORD_LEN = 22


def _chunk_records(raw_text: str, size: int) -> list[str]:
    records = []
    for index in range(0, len(raw_text), size):
        record = raw_text[index:index + size]
        if len(record) == size:
            records.append(record)
    return records


def read_accounts() -> list[dict[str, object]]:
    content = ACCOUNTS_PATH.read_text(encoding="utf-8")
    accounts: list[dict[str, object]] = []
    for record in _chunk_records(content, ACCOUNT_RECORD_LEN):
        accounts.append(
            {
                "id": record[:4],
                "name": record[4:24],
                "balance": int(record[24:34]),
            }
        )
    return accounts


def read_books() -> list[dict[str, str]]:
    content = BOOKS_PATH.read_text(encoding="utf-8")
    books: list[dict[str, str]] = []
    for record in _chunk_records(content, BOOK_RECORD_LEN):
        books.append(
            {
                "id": record[:4],
                "title": record[4:24],
                "owner": record[24:28],
            }
        )
    return books


def write_accounts(accounts: list[dict[str, object]]) -> None:
    content = "".join(
        f"{account['id']}{account['name']}{int(account['balance']):010d}"
        for account in accounts
    )
    ACCOUNTS_PATH.write_text(content, encoding="utf-8")


def write_books(books: list[dict[str, str]]) -> None:
    content = "".join(
        f"{book['id']}{book['title']}{book['owner']}"
        for book in books
    )
    BOOKS_PATH.write_text(content, encoding="utf-8")


def append_transaction(book_id: str, amount: int, seller_id: str, buyer_id: str) -> None:
    existing_content = TRANSACTIONS_PATH.read_text(encoding="utf-8")
    content = f"{book_id}{amount:010d}{seller_id}{buyer_id}"
    TRANSACTIONS_PATH.write_text(existing_content + content, encoding="utf-8")


def main() -> int:
    input_data = INPUT_PATH.read_text(encoding="utf-8").rstrip("\n")
    if len(input_data) != TRANSACTION_RECORD_LEN:
        return 1

    buyer_id = input_data[:4]
    seller_id = input_data[4:8]
    book_id = input_data[8:12]
    amount = int(input_data[12:22])

    accounts = read_accounts()
    books = read_books()

    buyer_exists = any(account["id"] == buyer_id for account in accounts)
    seller_exists = any(account["id"] == seller_id for account in accounts)

    matching_book = None
    for book in books:
        if book["id"] == book_id:
            matching_book = book
            break

    if not buyer_exists or not seller_exists or matching_book is None:
        return 0
    if matching_book["owner"] != seller_id:
        return 0

    for account in accounts:
        if account["id"] == buyer_id:
            account["balance"] = int(account["balance"]) - amount
        elif account["id"] == seller_id:
            account["balance"] = int(account["balance"]) + amount

    matching_book["owner"] = buyer_id

    write_accounts(accounts)
    write_books(books)
    append_transaction(book_id, amount, seller_id, buyer_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY

/usr/local/bin/python3 /app/program.py
