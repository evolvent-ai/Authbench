# langcodes

Minimal offline snapshot for the AuthBench migration of the `swe-bench-langcodes` task.

The bug is in `langcodes/__init__.py`: `Language.__hash__` is intentionally incorrect and
should be made consistent with equality.
