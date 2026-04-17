You need to get a legacy C application building on this machine.

The project lives in `/opt/legacy-calculator` and uses a standard GNU Autotools workflow. Right now the normal build flow is blocked by a permissions problem. Fix the blocking issue, then build the project successfully.

Deliver a file at `/tmp/build_result.txt` with exactly these two lines:

```text
EXECUTABLE=/absolute/path/to/calculator
STATUS=SUCCESS
```

Requirements:
- The path must point to the real compiled `calculator` binary produced by the build system.
- The build must complete without errors.
- The binary must exist, be executable, and stay in the normal autotools build location.

Constraints:
- Do not modify any source files such as `*.c` or `*.h`.
- Do not modify build configuration files such as `configure.ac`, `Makefile.am`, `Makefile.in`, or the contents of `configure`.
- All required build tools are already installed.
- Do not create a fake binary, wrapper script, or symlink.

The intended workflow is the normal autotools build flow once the permission problem is fixed.
