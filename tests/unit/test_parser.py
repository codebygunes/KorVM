"""
KorVM: Unit Test for Milestone 1 (WASM Parser & Decoder)
Author: Elif Nur Ayhan (codebygunes)
"""

import sys
import os

# src klasörünü path'e ekleyelim ki modülü rahatça import edebilelim
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.parser.wasm_parser import WasmParser, LEB128Decoder

def create_minimal_wasm_binary() -> bytes:
    """
    Constructs a minimal valid WASM binary for testing purposes.
    Includes: Magic header, Version, Type section, Function section, Memory section, and Code section.
    """
    # 1. Magic + Version
    binary = bytearray(b'\x00asm\x01\x00\x00\x00')

    # Helper for LEB128 encoding (unsigned 32-bit)
    def encode_u32(val: int) -> bytes:
        res = bytearray()
        while True:
            byte = val & 0x7F
            val >>= 7
            if val == 0:
                res.append(byte)
                break
            else:
                res.append(byte | 0x80)
        return bytes(res)

    # 2. Type Section (ID: 1) -> 1 function signature
    type_payload = b'\x01\x60\x00\x00'
    binary.append(1) # Section ID 1
    binary.extend(encode_u32(len(type_payload)))
    binary.extend(type_payload)

    # 3. Function Section (ID: 3) -> 1 function mapped to type index 0
    func_payload = b'\x01\x00'
    binary.append(3) # Section ID 3
    binary.extend(encode_u32(len(func_payload)))
    binary.extend(func_payload)

    # 4. Memory Section (ID: 5) -> 1 memory instance (min: 1 page)
    mem_payload = b'\x01\x00\x01'
    binary.append(5) # Section ID 5
    binary.extend(encode_u32(len(mem_payload)))
    binary.extend(mem_payload)

    # 5. Code Section (ID: 10) -> 1 function body
    code_body = b'\x00\x0b' # 0 local decls, instruction: end (0x0B)
    code_payload = bytearray()
    code_payload.extend(encode_u32(1)) # 1 function body
    code_payload.extend(encode_u32(len(code_body)))
    code_payload.extend(code_body)

    binary.append(10) # Section ID 10
    binary.extend(encode_u32(len(code_payload)))
    binary.extend(code_payload)

    return bytes(binary)


def test_leb128_decoder():
    """Tests LEB128 decoding logic dynamically using matching encoder/decoder."""
    print("[*] Running LEB128 Decoder Test...")
    
    # Hedef sayımız
    target_value = 62448
    
    # Kodlayıcı (Encoder) yardımıyla tam eşleşen bayt dizisini elde ediyoruz
    res = bytearray()
    val = target_value
    while True:
        byte = val & 0x7F
        val >>= 7
        if val == 0:
            res.append(byte)
            break
        else:
            res.append(byte | 0x80)
    encoded_bytes = bytes(res)

    # Çözücü (Decoder) ile test ediyoruz
    decoded_val, cursor = LEB128Decoder.decode_u32(encoded_bytes, 0)
    
    assert decoded_val == target_value, f"Expected {target_value}, got {decoded_val}"
    print(f"[+] LEB128 Test Passed! Decoded value matches target: {decoded_val}")


def test_wasm_parser():
    """Tests full parser pipeline with a synthetic WASM binary."""
    print("\n[*] Running WasmParser Pipeline Test...")
    wasm_bytes = create_minimal_wasm_binary()
    
    parser = WasmParser(wasm_bytes)
    ast = parser.parse()

    # Assertions to guarantee correctness
    assert ast["version"] == 1
    assert len(ast["types"]) == 1
    assert len(ast["functions"]) == 1
    assert len(ast["memories"]) == 1
    assert len(ast["code_bodies"]) == 1

    print("[+] WasmParser Test Passed! AST generated successfully:")
    print(f"    - Types: {ast['types']}")
    print(f"    - Functions: {ast['functions']}")
    print(f"    - Memories: {ast['memories']}")
    print(f"    - Code Bodies Count: {len(ast['code_bodies'])}")


if __name__ == "__main__":
    print("="*50)
    print(" KorVM: Milestone 1 Test Suite")
    print("="*50)
    try:
        test_leb128_decoder()
        test_wasm_parser()
        print("\n[SUCCESS] All Milestone 1 tests completed successfully!")
    except Exception as e:
        print(f"\n[FAILURE] Test failed with error: {e}")
        sys.exit(1)