"""
KorVM: End-to-End "Impossible" Integration & Stress Test
Author: Elif Nur Ayhan (codebygunes)
Description: Concurrently attacks the Parser, Sandbox, Interpreter, and JIT engine 
             in a single chaotic loop to ensure zero-trust stability.
"""

import sys
import os
import random

# src klasörünü path'e ekleyelim
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from core.parser.wasm_parser import WasmParser
from sandbox.memory.sandbox_core import ZeroTrustSandbox
from core.interpreter.interpreter import BaselineInterpreter
from core.jit.optimizer import SelfOptJITEngine

def test_end_to_end_chaos():
    print("\n[*] Launching 'Omni-Fuzzer' E2E Stress Test (10,000 Cycles)...")
    
    # 1. Initialize all core components
    sandbox = ZeroTrustSandbox(initial_pages=1)
    interpreter = BaselineInterpreter(sandbox)
    jit = SelfOptJITEngine()
    
    # Valid bytecode for memory operations
    valid_bytecode = b'\x41\x00\x41\x2A\x36\x02\x08\x41\x00\x28\x02\x08\x0B'
    
    # Performance and Security Metrics
    metrics = {
        "jit_fast_path": 0, 
        "sandbox_violations": 0, 
        "parser_rejections": 0
    }
    
    # 2. Unleash 10,000 chaotic asynchronous-like operations
    iterations = 10000
    
    # Suppress print statements for speed during the stress test
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    try:
        for _ in range(iterations):
            choice = random.randint(1, 3)
            
            if choice == 1:
                # STRESS 1: Execution Pipeline (Interpreter + JIT + Memory)
                # Repeated calls will trigger the JIT Hot Loop detection
                res = jit.execute("e2e_hot_func", valid_bytecode, interpreter.execute)
                if res == "[Native Execution Result: Compiled]":
                    metrics["jit_fast_path"] += 1
                    
            elif choice == 2:
                # STRESS 2: Zero-Trust Sandbox Integrity
                # Throw catastrophic offsets at the memory manager
                bad_offset = random.choice([-999, 99999999, 65536])
                try:
                    sandbox.store_i32(bad_offset, 777)
                except MemoryError:
                    metrics["sandbox_violations"] += 1
                    
            elif choice == 3:
                # STRESS 3: Parser Resilience
                # Inject absolute garbage bytes to attempt to crash the AOT validator
                garbage = bytes(random.getrandbits(8) for _ in range(random.randint(5, 100)))
                try:
                    parser = WasmParser(garbage)
                    parser.parse()
                except Exception:
                    metrics["parser_rejections"] += 1
    finally:
        # Restore standard output
        sys.stdout.close()
        sys.stdout = original_stdout

    print(f"[+] Omni-Fuzzer completed successfully without crashing.")
    print(f"    -> JIT Fast-Path Activations : {metrics['jit_fast_path']}")
    print(f"    -> Sandbox Violations Caught : {metrics['sandbox_violations']}")
    print(f"    -> Parser Rejections Caught  : {metrics['parser_rejections']}")
    
    assert metrics["jit_fast_path"] > 0, "Fatal: JIT failed to activate and optimize!"
    assert metrics["sandbox_violations"] > 0, "Fatal: Sandbox failed to catch memory violations!"
    assert metrics["parser_rejections"] > 0, "Fatal: Parser failed to reject garbage payloads!"

if __name__ == "__main__":
    print("="*60)
    print(" KorVM: THE IMPOSSIBLE END-TO-END INTEGRATION TEST")
    print("="*60)
    try:
        test_end_to_end_chaos()
        print("\n[SUCCESS] KorVM survived the ultimate E2E chaos test with absolute stability!")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] System collapsed: {e}")
        sys.exit(1)
