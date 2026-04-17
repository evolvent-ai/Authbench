#!/bin/bash
set -euo pipefail

cat /scripts/process_sales.awk >/dev/null

cat <<'AWK' > /solution/fixed_process_sales.awk
BEGIN {
    FS = ","
    overall_total = 0
    overall_records = 0
    region_count = 0
}

FNR == 1 {
    if (NR > 1) {
        print ""
        print "Region: " region_title " Summary"
        printf "Total Amount: %.2f\n", file_total
        print "Total Records: " file_records
        print ""
    }

    region_count++
    split(FILENAME, path_parts, "/")
    current_file = path_parts[length(path_parts)]
    region_name = current_file
    sub(/^region_/, "", region_name)
    sub(/\.csv$/, "", region_name)
    region_title = toupper(substr(region_name, 1, 1)) substr(region_name, 2)

    file_total = 0
    file_records = 0

    print "Processing " current_file "..."
    next
}

{
    amount = $3 + 0

    print "Processing line " FNR " from file " current_file
    printf "Date: %s, Product: %s, Amount: %.2f, Quantity: %s\n", $1, $2, amount, $4

    file_total += amount
    file_records++
    overall_total += amount
    overall_records++
}

END {
    if (current_file != "") {
        print ""
        print "Region: " region_title " Summary"
        printf "Total Amount: %.2f\n", file_total
        print "Total Records: " file_records
        print ""
    }

    print "========================================"
    print "OVERALL SUMMARY"
    print "========================================"
    printf "Total Amount Across All Regions: %.2f\n", overall_total
    print "Total Records Processed: " overall_records
    print "Number of Regions: " region_count
}
AWK

awk -f /solution/fixed_process_sales.awk \
    /data/sales/region_north.csv \
    /data/sales/region_south.csv \
    /data/sales/region_west.csv \
    | diff -u /expected/correct_output.txt -
