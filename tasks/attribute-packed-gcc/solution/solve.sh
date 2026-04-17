#!/bin/bash
set -euo pipefail

cat > /workspace/packet_parser.c <<'EOF'
#include <stdio.h>
#include <stdint.h>

struct __attribute__((packed)) NetworkPacket {
    uint8_t version;
    uint8_t type;
    uint32_t sequence;
    uint16_t length;
    uint8_t flags;
    uint16_t checksum;
    uint32_t reserved;
};

int main(void) {
    FILE *fp = fopen("/workspace/test_packet.bin", "rb");
    struct NetworkPacket packet;

    if (fp == NULL) {
        fprintf(stderr, "Error: Unable to open test_packet.bin\n");
        return 1;
    }

    size_t bytes_read = fread(&packet, 1, sizeof(packet), fp);
    fclose(fp);

    if (bytes_read != sizeof(packet)) {
        fprintf(stderr, "Error: Failed to read complete packet\n");
        return 1;
    }

    printf("SEQUENCE_NUMBER=%u\n", packet.sequence);
    printf("PAYLOAD_LENGTH=%u\n", packet.length);
    printf("CHECKSUM=0x%04X\n", packet.checksum);

    return 0;
}
EOF

gcc -Wall -Wextra -Werror -o /tmp/packet_parser /workspace/packet_parser.c
/tmp/packet_parser > /workspace/solution.txt
