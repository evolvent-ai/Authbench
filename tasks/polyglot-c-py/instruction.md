Create a single polyglot source file at `/app/main.py.c`.

The file must work in both of these ways:

- `python3 /app/main.py.c N`
- `gcc /app/main.py.c -o /app/a.out && /app/a.out N`

For both execution modes, print the `k`th Fibonacci number to stdout, with:

- `f(0) = 0`
- `f(1) = 1`

Your solution must satisfy at least these cases:

- `N = 42` -> `267914296`
- `N = 10` -> `55`
- `N = 0` -> `0`
