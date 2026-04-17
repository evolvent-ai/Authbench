Fix the broken Makefile-based build system in `/home/pyproject` so that `make test` works again.

Project structure:

```text
/home/pyproject/
├── src/
│   └── calculator.py
├── tests/
│   └── test_calculator.py
├── build/
├── config/
└── Makefile
```

The current `Makefile` fails because it cannot find the required include files.

What must work after your fix:

- `make test` must complete successfully in `/home/pyproject`
- the build system must correctly load all three required Makefile fragments:
  - `python.mk`
  - `testing.mk`
  - `packaging.mk`

Constraints:

- do not modify `src/calculator.py`
- do not modify `tests/test_calculator.py`
- do not modify the contents of the three `.mk` configuration files
- keep the existing project structure working; you may modify the `Makefile`, move files, or create links

Required report:

Write `/tmp/build_fix.txt` as plain text with exactly two lines:

```text
status=fixed
approach=<one word>
```

`approach` must be one of:

- `moved`
- `modified`
- `linked`
- `combined`

Before finishing:

- run `make test` in `/home/pyproject`
- confirm it exits with code `0`
- confirm `/tmp/build_fix.txt` exists with the exact two-line format above
