#ifndef FEAL_H
#define FEAL_H

#include <stdint.h>

void create_random_keys(void);
uint64_t encrypt(uint64_t plaintext);
uint32_t* get_keys(void);

#endif // FEAL_H
