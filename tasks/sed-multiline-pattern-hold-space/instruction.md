Analyze `/var/log/app/production.log` and write `/tmp/stack_trace_analysis.txt`.

The output must contain one line per exception type in this exact format:

```text
EXCEPTION_TYPE|COUNT|ROOT_CAUSE_METHOD
```

Use these exact rules:

- A stack trace starts on a log line containing `ERROR <exception class>:` and continues through the following indented `at ...` lines.
- Treat the deepest frame as the last `at ...` line in that stack trace.
- `EXCEPTION_TYPE` is the fully qualified exception class from the `ERROR` line.
- `COUNT` is the number of stack traces for that exception type.
- `ROOT_CAUSE_METHOD` is the most common deepest frame for that exception type.
- If multiple root-cause methods are tied for most common, choose the lexicographically smallest fully qualified method name.
- Sort output lines by `COUNT` descending. Break ties by `EXCEPTION_TYPE` ascending.

Requirements:

- read only from `/var/log/app/production.log`
- write only `/tmp/stack_trace_analysis.txt`
- preserve the exact pipe-delimited format with no extra text
- `python3` is available and is enough for this task; prefer a short local script
- do not install packages
- do not use the network
