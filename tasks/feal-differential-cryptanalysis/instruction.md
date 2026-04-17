The file `/app/feal.py` implements a FEAL-like encryption function. Implement a chosen-plaintext attack that recovers the value of `key[5]`.

Create `/app/attack.py` that defines:

```python
def attack(encrypt_fn) -> int:
    ...
```

Requirements:

- `attack(encrypt_fn)` receives an encryption oracle function `encrypt_fn`
- it must return the recovered `uint32` value of `key[5]`
- each of the six round keys is derived from a 16-bit seed
- the attack should finish in less than 30 seconds

Hint:

- use paired plaintexts `value` and `value ^ 0x8080000080800000`
- a candidate `key[5]` is `(seed * 1234567) & 0xFFFFFFFF` for a 16-bit `seed`
- for a ciphertext `c`, let `left = getleft(c)` and `right = getright(c)`, then partially undo the final key guess with `left ^= f_function((left ^ right) ^ candidate_key)`
- for the correct candidate, the adjusted left halves from the paired ciphertexts differ by `0x02000000`
- repeating this filter across several random `value` inputs quickly narrows the 16-bit seeds to one answer
- you only need helper functions equivalent to `getleft`, `getright`, `g_function`, and `f_function` from `/app/feal.py`

The verifier will build a local C extension and call your Python function against random keys.
