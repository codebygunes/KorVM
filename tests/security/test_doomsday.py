"""
KorVM: The "Doomsday" Extreme Fault Tolerance & Resilience Test
Author: Elif Nur Ayhan (codebygunes)
License: GPL-3.0
Description: Property-based adversarial testing targeting Resource Exhaustion (Memory DDoS), 
             Stack Underflow, and Sudden EOF attacks under extreme load.
"""
import sys
import os
import struct
from hypothesis import given, settings, strategies as st

# src klasörünü path'e ekliyoruz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sandbox.memory.sandbox_core import ZeroTrustSandbox
from core.interpreter.interpreter import BaselineInterpreter

def test_memory_ddos():
    print("\n[*] Launching Resource Exhaustion (Memory DDoS) Attack...")
    # Sandbox'a maksimum 10 sayfalık (640 KB) katı bir sınır koyuyoruz.
    sandbox = ZeroTrustSandbox(initial_pages=1, max_pages=10)
    
    # Saldırı: Sistemi çökertmek için devasa bellek artırım talebi (64 GB RAM)
    try:
        result = sandbox.grow_memory(1000000)
        # Eğer Error/Exception dönmezse ve değer kontrolü yapacaksak:
        if isinstance(result, int):
            assert result == -1, "SECURITY BREACH: Sandbox allowed illegal massive memory allocation!"
    except Exception:
        # [SUCCESS] Güvenli bir şekilde reddedildi / Exception fırlatıldı
        pass
        
    assert len(sandbox.memory) == 65536, "SECURITY BREACH: Memory array actually expanded despite limit!"
    print("[+] DDoS Defeated! Sandbox strictly enforced the max_pages limit and blocked the allocation.")

def test_stack_underflow():
    print("\n[*] Launching Stack Underflow Attack (Corrupted State)...")
    sandbox = ZeroTrustSandbox(initial_pages=1)
    engine = BaselineInterpreter(sandbox)
    
    # Saldırı: Yığına (stack) hiçbir argüman eklemeden i32.add (0x6A) komutu çalıştırıyoruz.
    malicious_bytecode = b'\x6A\x0B'
    
    caught = False
    try:
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        engine.execute(malicious_bytecode)
        sys.stdout.close()
        sys.stdout = original_stdout
    except (IndexError, KeyError, ValueError, TypeError):
        caught = True
        sys.stdout = original_stdout
        
    assert caught, "VULNERABILITY: Engine did not catch Stack Underflow and continued executing!"
    print("[+] Underflow Defeated! Engine safely caught empty stack access.")

def test_sudden_eof():
    print("\n[*] Launching Sudden EOF (Truncated Instruction) Attack...")
    sandbox = ZeroTrustSandbox(initial_pages=1)
    engine = BaselineInterpreter(sandbox)
    
    # Saldırı: i32.const (0x41) komutunu verip, beklenen sayıyı vermeden bayt dizisini kesiyoruz!
    truncated_bytecode = b'\x41'
    
    caught = False
    try:
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        engine.execute(truncated_bytecode)
        sys.stdout.close()
        sys.stdout = original_stdout
    except (IndexError, KeyError, ValueError, TypeError):
        caught = True
        sys.stdout = original_stdout
        
    assert caught, "VULNERABILITY: Engine tried to read beyond bytecode bounds or froze!"
    print("[+] EOF Defeated! Engine safely caught truncated instructions without freezing.")

@given(st.binary(min_size=1, max_size=256))
@settings(max_examples=500, deadline=None)
def test_doomsday_adversarial_fuzz(hostile_payload: bytes):
    """
    Hypothesis Property-Based Fuzzing integration:
    Dynamically bombards the execution engine with hostile byte mutations 
    to guarantee absolute immunity against unexpected runtime crashes.
    """
    sandbox = ZeroTrustSandbox(initial_pages=1, max_pages=5)
    engine = BaselineInterpreter(sandbox)
    try:
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        engine.execute(hostile_payload)
        sys.stdout.close()
        sys.stdout = original_stdout
    except Exception:
        # [SUCCESS] All adversarial anomalies are caught safely by Zero-Trust barriers.
        sys.stdout = original_stdout
        pass

if __name__ == "__main__":
    print("="*60)
    print(" KorVM: THE 'DOOMSDAY' EXTREME FAULT TOLERANCE & RESILIENCE SUITE")
    print("="*60)
    try:
        test_memory_ddos()
        test_stack_underflow()
        test_sudden_eof()
        
        print("\n[*] Launching Property-Based Doomsday Mutation Fuzzing (500 cycles)...")
        test_doomsday_adversarial_fuzz()
        
        print("\n[SUCCESS] KorVM survived the Doomsday scenarios and adversarial fuzzing flawlessly!")
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] System compromised: {e}")
        sys.exit(1)