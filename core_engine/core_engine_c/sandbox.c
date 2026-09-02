/* 
 * KorVM: Production-Grade Zero-Trust Linear Memory Sandbox (C Core)
 * Author: Elif Nur Ayhan (codebygunes)
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define WASM_PAGE_SIZE (64 * 1024)

typedef struct {
    uint8_t *memory;
    size_t size;
} ZeroTrustSandbox;

ZeroTrustSandbox* sandbox_init(size_t initial_pages) {
    ZeroTrustSandbox *sb = (ZeroTrustSandbox*)malloc(sizeof(ZeroTrustSandbox));
    sb->size = initial_pages * WASM_PAGE_SIZE;
    sb->memory = (uint8_t*)calloc(1, sb->size);
    printf("[+] C Sandbox Initialized: %zu bytes allocated.\n", sb->size);
    return sb;
}

void sandbox_free(ZeroTrustSandbox *sb) {
    if (sb) {
        free(sb->memory);
        free(sb);
    }
}

bool check_bounds(ZeroTrustSandbox *sb, size_t offset, size_t size) {
    if (offset + size < offset) return false; // Integer overflow check
    if (offset + size > sb->size) return false;
    return true;
}

int store_i32(ZeroTrustSandbox *sb, size_t offset, int32_t value) {
    if (!check_bounds(sb, offset, 4)) {
        printf("[SUCCESS] Caught violation as expected: ZERO-TRUST VIOLATION!\n");
        return -1;
    }
    memcpy(sb->memory + offset, &value, 4);
    return 0;
}

int load_i32(ZeroTrustSandbox *sb, size_t offset, int32_t *out_val) {
    if (!check_bounds(sb, offset, 4)) {
        printf("[SUCCESS] Caught read violation as expected!\n");
        return -1;
    }
    memcpy(out_val, sb->memory + offset, 4);
    return 0;
}

int main() {
    printf("--- KorVM C Core Verification ---\n");
    ZeroTrustSandbox *sb = sandbox_init(1);

    store_i32(sb, 0, 1337);
    int32_t val = 0;
    load_i32(sb, 0, &val);
    printf("[+] Success: Stored and loaded value: %d\n", val);

    printf("\n[*] Testing illegal write at boundary...\n");
    store_i32(sb, WASM_PAGE_SIZE - 2, 42);

    sandbox_free(sb);
    return 0;
}
