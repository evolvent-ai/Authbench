Fix the bug in `/app/astropy` where the reduced `ascii.qdp` reader treats QDP commands as case-sensitive.

A minimized reproduction of the relevant Astropy code is provided under `/app/astropy`. The bug is in `/app/astropy/astropy/io/ascii/qdp.py`.

QDP itself is case-insensitive, so files such as:

```text
read serr 1 2
1 0.5 1 0.5
```

should be accepted the same way as their uppercase equivalents.

The fix should make the parser accept lowercase command lines and lowercase `no` markers in data rows, instead of crashing or treating them as ordinary strings.

Keep the fix in the library code rather than adding a workaround in tests.
