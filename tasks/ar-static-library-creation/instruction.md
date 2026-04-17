Build a working static library from the C sources in `/workspace/mathlib` and verify that the provided test program links against it correctly.

The directory already contains:

- the library source files and headers
- `test_math.c`
- a helper script at `/workspace/mathlib/build.sh`

Requirements:

1. Compile every library source file except `test_math.c` into object files.
2. Combine those object files into a static library named `libmath.a`.
3. Build the test program and link it against that static library.
4. Run the test program successfully.
5. Complete the build without warnings or errors.
6. Do not install packages or fetch external code.

Write the absolute path to the created static library to `/workspace/solution.txt`.

`/workspace/solution.txt` must contain exactly one line, and that line must be an absolute path to `libmath.a`.
