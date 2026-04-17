Repair the AWK script bug in `/scripts/process_sales.awk`.

The task uses these inputs:

- `/data/sales/region_north.csv`
- `/data/sales/region_south.csv`
- `/data/sales/region_west.csv`
- `/scripts/process_sales.awk`
- `/expected/correct_output.txt`

Write the corrected AWK script to `/solution/fixed_process_sales.awk`.

Requirements:

- Running
  `awk -f /solution/fixed_process_sales.awk /data/sales/region_north.csv /data/sales/region_south.csv /data/sales/region_west.csv`
  must produce output exactly equal to `/expected/correct_output.txt`.
- Use the per-file line number for `Processing line ... from file ...`, so the first data row in each CSV is line `2`.
- Derive the region summary name from the input filename, producing `North`, `South`, and `West`.
- Process every data row from all three CSV files.
- Reset per-file totals and record counts when the input file changes.
- Print amounts with exactly two decimal places.

The existing bug is that the original script mixes up global line numbers and per-file line numbers and also mishandles per-file summary state across multiple input files.
