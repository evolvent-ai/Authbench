The `filesystem_spec` repository is already checked out at `/app/filesystem_spec`.

`DirFileSystem` is missing an async `open_async()` implementation, so async callers currently hit `NotImplementedError`.

Fix the bug in `/app/filesystem_spec/fsspec/implementations/dirfs.py`.

The new method must delegate directly to the wrapped filesystem and preserve the same flexible calling convention as `open()`. In practice, `DirFileSystem.open_async()` should:

- accept `path, *args, **kwargs`
- call `self.fs.open_async(self._join(path), *args, **kwargs)`
- return the awaited result

Do not add a workaround elsewhere and do not hard-code a `mode`-only signature. The verifier will run the upstream `test_dirfs.py` suite.
