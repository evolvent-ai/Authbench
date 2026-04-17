Re-implement the COBOL program at `/app/src/program.cbl` as a Python script at `/app/program.py`.

Requirements:
- Run from `/app` as `python3 /app/program.py`.
- Read one fixed-width transaction record from `/app/src/INPUT.DAT`.
- Update `/app/data/ACCOUNTS.DAT`, `/app/data/BOOKS.DAT`, and `/app/data/TRANSACTIONS.DAT` exactly as the COBOL program would.
- Preserve exact fixed-width formatting and do not add trailing newlines to the `.DAT` files.

File formats:
- `INPUT.DAT`: 22 characters total: buyer id (4), seller id (4), book id (4), amount (10 digits).
- `ACCOUNTS.DAT`: 34-character records: account id (4), account name (20), balance (10 digits).
- `BOOKS.DAT`: 28-character records: book id (4), title (20), owner id (4).
- `TRANSACTIONS.DAT`: appended 22-character records: book id (4), amount (10 digits), seller id (4), buyer id (4).

Behavior:
- Validate that the buyer account exists, the seller account exists, the book exists, and the seller currently owns that book.
- If validation succeeds:
  - subtract the amount from the buyer balance
  - add the amount to the seller balance
  - change the book owner to the buyer
  - append one transaction record to `TRANSACTIONS.DAT`
- If validation fails, leave all three `.DAT` files unchanged.

Use only the Python standard library.
