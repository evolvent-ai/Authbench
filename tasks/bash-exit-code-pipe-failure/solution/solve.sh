#!/bin/bash
set -euo pipefail

cat > /opt/monitor/process_logs_fixed.sh <<'EOF'
#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <log-file>" >&2
    exit 1
fi

LOG_FILE="$1"

if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Log file not found: ${LOG_FILE}"
    exit 1
fi

validate_error_lines() {
    awk '
        /ERROR/ {
            if ($1 !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/ ||
                $2 !~ /^[0-9]{2}:[0-9]{2}:[0-9]{2}$/ ||
                $3 != "ERROR" ||
                $4 !~ /^[0-9]+$/ ||
                NF < 5) {
                exit 2
            }
            print
        }
    ' "$LOG_FILE"
}

echo "=== Server Log Monitor ==="
echo "Processing logs from: ${LOG_FILE}"
echo ""
echo "Stage 1: Extracting error entries..."
echo "Stage 2: Filtering by severity level (>= 3)..."
echo "Stage 3: Aggregating statistics..."
echo "Stage 4: Formatting report..."
echo ""

if ! report_output=$(validate_error_lines | awk '$4 >= 3 {print $5}' | sort | uniq -c | awk '{print $2": "$1" occurrences"}'); then
    echo ""
    echo "ERROR: Report generation failed"
    exit 1
fi

if [ -n "$report_output" ]; then
    printf '%s\n' "$report_output"
fi

echo ""
echo "=== Report Complete ==="
echo "Log processing finished successfully"
echo ""
echo "=== Summary Statistics ==="

if ! total_errors=$(validate_error_lines | wc -l | awk '{print $1}'); then
    echo "Failed to generate summary"
    exit 1
fi
echo "Total errors found: ${total_errors}"
echo ""
echo "Critical errors (severity >= 3):"

if ! critical_errors=$(validate_error_lines | awk '$4 >= 3' | wc -l | awk '{print $1}'); then
    echo "Failed to generate summary"
    exit 1
fi
echo "Count: ${critical_errors}"
echo ""
echo "Monitoring complete"
EOF

chmod +x /opt/monitor/process_logs_fixed.sh
