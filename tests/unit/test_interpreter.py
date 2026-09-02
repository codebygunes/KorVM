"""
KorVM: Unit Test for Milestone 3 (Baseline Interpreter Integration)
Author: Elif Nur Ayhan (codebygunes)
"""

import sys
import os

# src klasörünü path'e ekleyelim
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.interpreter.interpreter import BaselineInterpreter
from sandbox.memory.sandbox_core import ZeroTrustSandbox

def test_arithmetic_execution():
    """Tests basic math opcodes inside the VM stack."""
    print("\n[*] Running Interpreter Arithmetic Test: (10 + (20 * 2))...")
    sandbox = ZeroTrustSandbox(initial_pages=1)
    engine = BaselineInterpreter(sandbox)
    
    # WASM Bytecode: 10 + (20 * 2)
    bytecode = b'\x41\x0A\x41\x14\x41\x02\x6C\x6A\x0B'
    
    final_stack = engine.execute(bytecode)
    
    assert len(final_stack) == 1, "Stack should contain exactly one final result."
    assert final_stack[0] == 50, f"Math Engine Failure! Expected 50, got {final_stack[0]}"
    print("[+] Arithmetic execution passed perfectly!")


def test_memory_operations():
    """Tests if the interpreter successfully reads/writes via the Zero-Trust Sandbox."""
    print("\n[*] Running Interpreter Memory Read/Write Test...")
    sandbox = ZeroTrustSandbox(initial_pages=1)
    engine = BaselineInterpreter(sandbox)
    
    # WASM Bytecode: Store 42 at address (0+8), then load it back
    # i32.const 0       (0x41 0x00) -> Base address
    # i32.const 42      (0x41 0x2A) -> Value to store
    # i32.store align=2, offset=8 (0x36 0x02 0x08)
    # i32.const 0       (0x41 0x00) -> Base address
    # i32.load align=2, offset=8  (0x28 0x02 0x08)
    # end               (0x0B)
    bytecode = b'\x41\x00\x41\x2A\x36\x02\x08\x41\x00\x28\x02\x08\x0B'
    
    final_stack = engine.execute(bytecode)
    
    assert len(final_stack) == 1, "Stack should contain the loaded value."
    assert final_stack[0] == 42, f"Memory Engine Failure! Expected 42, got {final_stack[0]}"
    print("[+] Memory operations passed perfectly! Interpreter <-> Sandbox integration verified.")


if __name__ == "__main__":
    print("="*60)
    print(" KorVM: Milestone 3 Test Suite (Execution Engine)")
    print("="*60)
    try:
        test_arithmetic_execution()
        test_memory_operations()
        print("\n[SUCCESS] All Milestone 3 Execution Engine tests completed successfully!")
    except Exception as e:
        print(f"\n[FAILURE] Test failed with error: {e}")
        sys.exit(1)
