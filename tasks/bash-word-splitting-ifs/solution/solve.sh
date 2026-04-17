#!/bin/bash
set -euo pipefail

cat <<'EOF' > /opt/data_processor/process_records.sh
#!/bin/bash

# Data Processing Pipeline for Customer Records
# Generates summary reports from CSV data

INPUT_FILE="/opt/data_processor/sample_data.csv"
OUTPUT_FILE="/opt/data_processor/report.txt"
TEMP_FILE="/tmp/processing_temp.txt"

# Initialize counters
total_balance=0
record_count=0

# Clear previous output
> "$OUTPUT_FILE"

echo "Processing customer records..." > "$TEMP_FILE"

# Process CSV file
while IFS=',' read -r name address balance
do
    # Skip header line
    if [ "$name" = "Name" ]; then
        continue
    fi

    # Increment counter
    record_count=$((record_count + 1))

    echo "Record $record_count:" >> "$OUTPUT_FILE"
    echo "  Customer: $name" >> "$OUTPUT_FILE"
    echo "  Address: $address" >> "$OUTPUT_FILE"
    echo "  Balance: $balance" >> "$OUTPUT_FILE"

    clean_balance=$(printf '%s\n' "$balance" | tr -d '$,')
    total_balance=$(echo "$total_balance + $clean_balance" | bc)

    echo "Processing: $name from $address" >> "$TEMP_FILE"

    echo "---" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

# Generate summary
echo "" >> "$OUTPUT_FILE"
echo "SUMMARY REPORT" >> "$OUTPUT_FILE"
echo "Total Records Processed: $record_count" >> "$OUTPUT_FILE"
echo "Total Balance: \$$total_balance" >> "$OUTPUT_FILE"

# Clean temp file
cat "$TEMP_FILE" >> "$OUTPUT_FILE"
rm -f "$TEMP_FILE"

echo "Report generated at $OUTPUT_FILE"
EOF

chmod +x /opt/data_processor/process_records.sh
/opt/data_processor/process_records.sh

cat <<'EOF' > /solution/fix_summary.txt
ISSUE=Unquoted expansions made field handling whitespace-sensitive
LINES_MODIFIED=13,15,27,32,37,48
EOF
