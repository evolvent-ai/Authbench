Fix `/workspace/packet_parser.c` so it correctly parses the legacy packet stored in `/workspace/test_packet.bin`.

The protocol layout is exactly 15 bytes with no padding between fields:

- `version`: 1 byte, `0x02`
- `type`: 1 byte, `0x45`
- `sequence`: 4 bytes, little-endian, `0x12345678`
- `length`: 2 bytes, little-endian, `0x0100`
- `flags`: 1 byte, `0x0F`
- `checksum`: 2 bytes, little-endian, `0xABCD`
- `reserved`: 4 bytes, little-endian, `0x00000000`

Requirements:

1. Fix the structure layout in `/workspace/packet_parser.c` so the packet fields are read from the correct byte offsets with no compiler-inserted padding.
2. The corrected source file must compile cleanly with `gcc -Wall -Wextra -Werror`.
3. Running the compiled program must print exactly these three lines:

```text
SEQUENCE_NUMBER=305419896
PAYLOAD_LENGTH=256
CHECKSUM=0xABCD
```

4. Save those same three lines to `/workspace/solution.txt`.
5. Do not install packages or fetch external code.

`/workspace/solution.txt` must contain exactly 3 lines in this order:

```text
SEQUENCE_NUMBER=<decimal>
PAYLOAD_LENGTH=<decimal>
CHECKSUM=0x<uppercase hex>
```
