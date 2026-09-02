"""
KorVM: Native x86-64 Dynamic Translation Unit Test
Author: Elif Nur Ayhan (codebygunes)
License: GPL-3.0
Description: Validates dynamic translation of WASM bytecodes to x86-64 CPU instructions.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from core.jit.optimizer import SelfOptJITEngine

class TestSelfOptJITEngine(unittest.TestCase):
    
    def setUp(self):
        self.jit = SelfOptJITEngine()
        # DİNAMİK TEST PAYLOAD'U: 5 + 7 işlemi. 
        # 0x41 (const), 0x05 (5), 0x41 (const), 0x07 (7), 0x6A (add), 0x0B (end)
        self.dynamic_bytecode = b'\x41\x05\x41\x07\x6A\x0B'
        self.dummy_func_id = "dynamic_math_loop"

    def dummy_interpreter(self, bytecode):
        return "Interpreter Execution Result"

    def test_dynamic_jit_compilation(self):
        """Test that the JIT reads bytecode dynamically and returns accurate CPU computations."""
        # Yorumlayıcı Aşaması (Slow Path)
        self.jit.execute(self.dummy_func_id, self.dynamic_bytecode, self.dummy_interpreter)
        self.jit.execute(self.dummy_func_id, self.dynamic_bytecode, self.dummy_interpreter)

        # 3. Çağrı: JIT Derlemesi (WASM'dan x86-64'e anlık çeviri)
        res3 = self.jit.execute(self.dummy_func_id, self.dynamic_bytecode, self.dummy_interpreter)
        
        # Test 1: Donanım devrede mi?
        self.assertIn("Native Hardware Execution", res3)
        # Test 2: İşlemci 5+7=12 işlemini x86-64 seviyesinde doğru hesapladı mı?
        self.assertIn("Result: 12", res3, "JIT failed to dynamically translate and execute 5+7!")
        
        # 4. Çağrı: Tamamen bellekten hızlı okuma
        res4 = self.jit.execute(self.dummy_func_id, self.dynamic_bytecode, self.dummy_interpreter)
        self.assertIn("Result: 12", res4)

if __name__ == "__main__":
    unittest.main()