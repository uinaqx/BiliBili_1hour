#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

extern uint64_t add_two(uint64_t a, uint64_t b);

int main(void) {
    uint64_t result = add_two(UINT64_C(7), UINT64_C(5));
    printf("%" PRIu64 "\n", result);
    return result == UINT64_C(12) ? 0 : 1;
}
