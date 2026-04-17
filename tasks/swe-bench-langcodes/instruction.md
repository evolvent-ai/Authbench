The repository is checked out at `/app/langcodes`.

Fix the bug in `langcodes` so that `Language.__hash__` is consistent with equality.
The only file you need to inspect and modify is:

`/app/langcodes/langcodes/__init__.py`

Right now, equal `Language` objects can produce different hash values after caching is bypassed or after a pickle round trip. For example, these should produce the same hash:

```python
import pickle
from langcodes import Language

en = Language.get("en")
loaded = pickle.loads(pickle.dumps(en))

print(en == loaded)          # True
print(hash(en) == hash(loaded))  # should also be True
```

Requirements:

- work only inside `/app/langcodes`
- read and edit only `/app/langcodes/langcodes/__init__.py`
- fix the implementation in the source code, not by changing tests or adding wrappers
- keep hash behavior consistent with `__eq__`
- different language tags should still compare differently and should not collapse to the same semantic value
- do not rely on internet access or install extra packages during the task
- do not spend time exploring other files or listing directories; the relevant `Language` implementation is already in `/app/langcodes/langcodes/__init__.py`

When you are done, the repository should satisfy the hash-consistency behavior described above.
