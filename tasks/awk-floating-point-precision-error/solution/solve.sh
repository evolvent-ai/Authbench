#!/bin/bash
set -euo pipefail

cat <<'AWK' > /workspace/fixed_process_transactions.awk
BEGIN {
    FS = ","
}

function round_to_cents(raw,    sign, parts_count, int_part, frac, cents, round_digit) {
    sign = 1
    if (raw ~ /^-/) {
        sign = -1
        raw = substr(raw, 2)
    }

    parts_count = split(raw, parts, ".")
    int_part = parts[1] + 0
    frac = (parts_count > 1 ? parts[2] : "")
    gsub(/[^0-9]/, "", frac)

    while (length(frac) < 3) {
        frac = frac "0"
    }

    cents = int_part * 100 + (substr(frac, 1, 2) + 0)
    round_digit = substr(frac, 3, 1) + 0
    if (round_digit >= 5) {
        cents++
    }

    return sign * cents
}

function format_cents(total_cents,    abs_cents, dollars, pennies, prefix) {
    prefix = ""
    abs_cents = total_cents
    if (total_cents < 0) {
        prefix = "-"
        abs_cents = -total_cents
    }

    dollars = int(abs_cents / 100)
    pennies = abs_cents % 100
    return sprintf("%s%d.%02d", prefix, dollars, pennies)
}

NR == 1 {
    next
}

{
    account = $2
    cents = round_to_cents($3)

    if ($4 == "CREDIT") {
        balances[account] += cents
    } else if ($4 == "DEBIT") {
        balances[account] -= cents
    }
}

END {
    for (account in balances) {
        accounts[++count] = account
    }

    for (i = 1; i <= count; i++) {
        for (j = i + 1; j <= count; j++) {
            if (accounts[i] > accounts[j]) {
                temp = accounts[i]
                accounts[i] = accounts[j]
                accounts[j] = temp
            }
        }
    }

    for (i = 1; i <= count; i++) {
        account = accounts[i]
        print account "," format_cents(balances[account])
    }
}
AWK

awk -f /workspace/fixed_process_transactions.awk /workspace/transactions.csv > /workspace/output.txt
