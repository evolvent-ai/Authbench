A compiled ELF binary is available at `/app/a.out`.

Write `/app/extract.js`. When run as `node /app/extract.js /app/a.out > /app/out.json`, it must print a JSON object whose keys are virtual memory addresses and whose values are 32-bit unsigned integers.

Match the verifier's extraction semantics:
- load the `.text`, `.data`, and `.rodata` sections when they exist
- use each section's virtual address as the base address
- walk each section in 4-byte chunks
- interpret every complete chunk as a little-endian unsigned 32-bit integer
- emit only complete 4-byte chunks

Example format:
`{"4194304": 1784774249, "4194308": 1718378344}`

Success criteria:
1. Every address you emit must have the exact value expected by the verifier.
2. You must emit at least 75% of the addresses present in the verifier's reference output.
3. Values must be JSON integers, not strings.
