I have already compiled the decompressor as `/app/decomp`. The original minified source is still available at `/app/decomp.c`, but you do not need to reverse-engineer it from scratch.

A clean reference encoder is available at `/app/reference_compressor.rs`.

Create `/app/data.comp` so that:

`cat /app/data.comp | /app/decomp`

produces exactly the contents of `/app/data.txt`.

A straightforward solution is:

```bash
TMPDIR=/tmp rustc /app/reference_compressor.rs -O -o /tmp/reference_compressor_bin
/tmp/reference_compressor_bin < /app/data.txt > /app/data.comp
```

Then verify with:

```bash
cat /app/data.comp | /app/decomp
```

`/app/data.comp` must be at most 2500 bytes.
