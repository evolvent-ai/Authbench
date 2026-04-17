#!/bin/bash
set -euo pipefail

cat > /workspace/solution.sh <<'EOF'
#!/bin/bash
set -euo pipefail

cd /workspace

for object in add.o subtract.o multiply.o divide.o; do
    if [ ! -f "/workspace/obj/${object}" ]; then
        echo "missing object file: ${object}" >&2
        exit 1
    fi
done

rm -f /workspace/lib/libcalc.a /tmp/test_calc_validation

ar rcs /workspace/lib/libcalc.a \
    /workspace/obj/add.o \
    /workspace/obj/subtract.o \
    /workspace/obj/multiply.o \
    /workspace/obj/divide.o

ranlib /workspace/lib/libcalc.a

gcc /workspace/test_calc.c -L/workspace/lib -lcalc -o /tmp/test_calc_validation

output="$("/tmp/test_calc_validation")"
if [ "${output}" != "add=5 subtract=3 multiply=15 divide=5" ]; then
    echo "unexpected program output: ${output}" >&2
    exit 1
fi
EOF

chmod +x /workspace/solution.sh
/workspace/solution.sh
