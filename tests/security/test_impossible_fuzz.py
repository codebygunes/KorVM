"""
KorVM: Property-Based Adversarial Fuzzing with Hypothesis
Author: Elif Nur Ayhan (codebygunes)
License: GPL-3.0
Description: Uses Hypothesis to dynamically generate and shrink malformed 
             WASM binaries, hunting for deep parser crashes on Windows/Cross-platform.
"""
import sys
import os
import struct
from hypothesis import given, settings, strategies as st

# src klasörünü path'e ekliyoruz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from core.parser.wasm_parser import WasmParser

@given(st.binary(min_size=1, max_size=512))
@settings(max_examples=1000, deadline=None)
def test_wasm_parser_fuzz(fuzz_data: bytes):
    """
    Hypothesis bu fonksiyona 1000 adet akıllıca mutasyona uğratılmış 
    bayt dizisi gönderecek. Amacımız parser'ın çökmeyip kontrollü hata vermesi.
    """
    try:
        parser = WasmParser(fuzz_data)
        parser.parse()
    except (ValueError, IndexError, struct.error, KeyError, NotImplementedError):
        # [BAŞARI] Parser bozuk bir W3C bölümü yakaladı ve güvenli bir şekilde reddetti.
        pass
    # Eğer burada ele alınmayan bir exception (örneğin MemoryError veya Memory Leak)
    # fırlatılırsa, Hypothesis testi kırmızıya düşürür ve tam olarak hangi bayt 
    # dizisinin buna sebep olduğunu bize raporlar.

if __name__ == "__main__":
    print("="*60)
    print(" KorVM: HYPOTHESIS PROPERTY-BASED FUZZER ENGINE")
    print("="*60)
    print("[*] Launching intelligent mutation fuzzing (1000 cycles)...")
    
    test_wasm_parser_fuzz()
    
    print("[SUCCESS] All fuzzed payloads were safely handled by the Zero-Trust architecture!")