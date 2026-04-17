The files `/app/feal.c` and `/app/decrypt.c` implement a FEAL-like 4-round block cipher and its corresponding decryption routine.

You are given:

- `/app/pairs.txt`: 32 known plaintext/ciphertext pairs, one decimal pair per line
- `/app/ciphertexts.txt`: 100 ciphertexts, one decimal value per line

Each round key is derived from a 20-bit seed using:

```c
expand(seed) = seed ^ (seed << 16) ^ (seed * 12345)
```

Recover the four 20-bit seeds, then decrypt every ciphertext in `/app/ciphertexts.txt`.

Write the decrypted decimal plaintexts to `/app/plaintexts.txt`, one per line, in the same order as the ciphertexts.

Notes:

- the compiled helpers `/app/feal` and `/app/decrypt` are already available
- `/app/decrypt` expects: `./decrypt ciphertexts.txt <k0> <k1> <k2> <k3>`
- each `<k*>` argument must be the original 20-bit seed, not the expanded 32-bit round key

Practical route:

- you do not need to derive a fresh attack from scratch
- implement the FEAL helper functions locally: `bit`, `popcnt`, `expand`, `g_function`, `f_function`, plus 64-bit half extraction helpers
- parse `pairs.txt` into `(plaintext, ciphertext)` pairs and use the first 16 pairs for key recovery
- recover the first three expanded round keys with a brute-force search over all `seed in [0, 0xFFFFF]`, using the linear masks below
- for a candidate seed, compute `candidate = expand(seed)` and test whether the parity expression below is constant across the 16 pairs
- for each round, there are 5 masks; keep the first non-zero seed whose candidate passes all 5 masks for that round
- after the first three expanded round keys are known, brute-force the last seed by checking which `expand(seed)` reproduces the known plaintext/ciphertext pairs under the full cipher
- finally invert the expanded keys back to the original 20-bit seeds and run `/app/decrypt`, redirecting stdout to `/app/plaintexts.txt`

Masks to use, in order:

```text
0x006a54727723
0x00ea44ca9fdb
0x004545cd88cd
0x00e050682d7d
0x0023051d4c49
0x00428f890688
0x00beb917ae06
0x0028f8c03890
0x00c679ef96ae
0x00eb9937ae26
0x002520384d6d
0x006520a8ddfd
0x006a3e187749
0x00829620f761
0x00cb8e06cc42
```

For round `r = 0, 1, 2`, use masks `masks[r * 5 : r * 5 + 5]`.

For each 48-bit mask value `maskctr`, derive:

```text
mask_pl = bits  0.. 7 mapped to positions  0, 2, 8,10,16,18,24,26
mask_pr = bits  8..15 mapped to positions  0, 2, 8,10,16,18,24,26
mask_cl = bits 16..23 mapped to positions  0, 2, 8,10,16,18,24,26
mask_cr = bits 24..31 mapped to positions  0, 2, 8,10,16,18,24,26
mask_fm = bits 32..39 mapped to positions  0, 2, 8,10,16,18,24,26
```

For a pair `(plaintext, ciphertext)`:

- let `pl` and `pr` be the 32-bit halves of `plaintext`
- let `cl` and `cr` be the 32-bit halves of `ciphertext`
- run the FEAL round function far enough to obtain the round-`r` intermediate `fm[r] = f_function(right ^ candidate)` exactly as in the cipher
- compute:

```text
almost_const =
  (popcnt(mask_cl & cl) +
   popcnt(mask_cr & cr) +
   popcnt(mask_pl & pl) +
   popcnt(mask_pr & pr)) % 2

cc = popcnt(fm[r] & mask_fm) % 2
```

- for a correct candidate, `almost_const XOR cc` stays constant across the 16 pairs for each of that round's 5 masks

Final step:

- once all four seeds are recovered, run:

```bash
./decrypt ciphertexts.txt 0x<k0> 0x<k1> 0x<k2> 0x<k3> > plaintexts.txt
```
