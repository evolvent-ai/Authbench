Compile the SQLite source tree already present in `/app/sqlite` with gcov instrumentation enabled, and make the resulting `sqlite3` binary available in `PATH`.

Use the source tree that is already in `/app/sqlite`. Do not install a prebuilt SQLite package and do not download a different source tree.

The compiled binary must work from anywhere in the container. The verifier will run `sqlite3 ":memory:" "SELECT 1;"` and will also check that gcov coverage artifacts are generated under `/app/sqlite`.
