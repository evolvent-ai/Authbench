A damaged static library archive lives at `/workspace/lib/libcalc.a`. The original object files are still available at `/workspace/obj/`, and the test program is `/workspace/test_calc.c`.

Repair the library so that this command succeeds:

```bash
gcc test_calc.c -L./lib -lcalc -o test_calc && ./test_calc
```

The program must print exactly:

```text
add=5 subtract=3 multiply=15 divide=5
```

Requirements:

- Work only with the files that are already present in `/workspace`.
- Do not install packages or fetch external code.
- Save a non-interactive executable shell script at `/workspace/solution.sh`.
- When run, the script must rebuild or repair `/workspace/lib/libcalc.a`, refresh the archive index, and verify that the test program links and runs successfully.

The only deliverable is the executable script `/workspace/solution.sh`.
