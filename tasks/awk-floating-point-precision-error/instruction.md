Repair the AWK script bug in `/workspace/process_transactions.awk`.

The task uses these inputs:

- `/workspace/transactions.csv`
- `/workspace/process_transactions.awk`

Write the corrected AWK script to `/workspace/fixed_process_transactions.awk`, then run it and save the script output to `/workspace/output.txt`.

Requirements:

- Running `awk -f /workspace/fixed_process_transactions.awk /workspace/transactions.csv` must print one line per account in this exact format:
  `ACCOUNT_ID,FINAL_BALANCE`
- Sort output lines by `ACCOUNT_ID` ascending.
- Format every `FINAL_BALANCE` with exactly 2 decimal places.
- For each transaction amount, round to the nearest cent using half-up rounding before applying it to the account balance.
  Examples: `250.333 -> 250.33`, `99.999 -> 100.00`, `0.001 -> 0.00`.
- Apply credits as additions and debits as subtractions after that per-transaction cent rounding.
- Keep balances exact to the cent throughout the calculation so floating-point accumulation does not affect the result.
- `/workspace/output.txt` must exactly match the output of the corrected AWK script.
- Use this exact command to generate the output file:
  `awk -f /workspace/fixed_process_transactions.awk /workspace/transactions.csv > /workspace/output.txt`
- Writing a fresh corrected AWK script is acceptable; it does not need to preserve the structure of the original script.

Do not install packages or use the network.
