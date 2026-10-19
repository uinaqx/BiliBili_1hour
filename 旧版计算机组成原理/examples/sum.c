/* High-level companion, not a promise of a particular compiler's assembly. */
#include <stdint.h>
#include <stdio.h>

int main(void) {
    const int32_t values[] = {3, 5, 7, 9};
    int32_t sum = 0;
    for (unsigned i = 0; i < sizeof(values)/sizeof(values[0]); ++i) {
        sum += values[i];
    }
    printf("%d\n", (int)sum);
    return sum == 24 ? 0 : 1;
}
