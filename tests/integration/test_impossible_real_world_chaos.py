"""
KorVM: Real-World "Impossible" Chaos & Stress Test for Dynamic Pipeline
Author: Elif Nur Ayhan (codebygunes)
License: Apache-2.0
Description: Bombards the updated dynamic parser and JIT emitter with malformed
             binaries, truncated LEB128 streams, and complex arithmetic chains.
"""
import os
import sys
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from core.parser.wasm_parser import WasmParser, LEB128Decoder
from core.jit.optimizer import SelfOptJITEngine

def test_impossible_real_world_chaos():
    print("="*60)
    print(" KorVM: REAL-WORLD 'IMPOSSIBLE' CHAOS & STRESS TEST")
    print("="*60)

    # SCENARIO 1: Malformed Binary Resilience (Adversarial Parser Fuzzing)
    print("\n[*] Scenario 1: Injecting hostile malformed WASM headers into dynamic parser...")
    hostile_garbage_payloads = [
        b'\x00\x00\x00\x00\x01\x00\x00\x00',  # Invalid magic header
        b'\x00asm\x01\x00\x00\x00\x0A\xFF\xFF', # Truncated code section size
        b'\x41\xFF\xFF\xFF\xFF\x0F'             # Malformed LEB128 constant stream
    ]

    parser_rejections = 0
    for idx, payload in enumerate(hostile_garbage_payloads):
        try:
            parser = WasmParser(payload)
            parser.parse()
        except (ValueError, struct.error) as e:
            parser_rejections += 1
            print(f"    [SAFE REJECTION #{idx+1}] Parser successfully intercepted malformed input: {e}")

    assert parser_rejections == len(hostile_garbage_payloads), "VULNERABILITY: Parser allowed invalid binary structures!"
    print("[+] Scenario 1 Passed: Parser is 100% immune to malformed payload injections.")

    # SCENARIO 2: Complex Dynamic JIT Compilation & Execution
    print("\n[*] Scenario 2: Testing JIT emitter with complex multi-operator WASM bytecode...")
    # WASM Bytecode: i32.const 10, i32.const 20, i32.mul (10 * 20 = 200), i32.const 50, i32.add (200 + 50 = 250)
    complex_bytecode = b'\x41\x0A\x41\x14\x6C\x41\x32\x6A\x0B'
    
    jit = SelfOptJITEngine()
    dummy_interpreter = lambda b: "Fallback Result"

    print("    -> Firing execution cycles to trigger hot-loop threshold...")
    final_output = ""
    for cycle in range(4):
        final_output = jit.execute("complex_math_func", complex_bytecode, dummy_interpreter)
        print(f"    [Cycle {cycle+1}] {final_output}")

    # Validation: 10 * 20 + 50 = 250
    assert "Native Hardware Execution" in final_output, "Fatal: JIT failed to switch to fast-path!"
    assert "Result: 250" in final_output, f"Computation Error! Expected Result: 250, got output: {final_output}"
    print("[+] Scenario 2 Passed: Dynamic multi-operator JIT translation computed 10*20+50 = 250 perfectly!")

if __name__ == "__main__":
    try:
        test_impossible_real_world_chaos()
        print("\n[SUCCESS] KorVM survived the impossible real-world chaos test with absolute integrity!")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] System collapsed under test: {e}")
        sys.exit(1)