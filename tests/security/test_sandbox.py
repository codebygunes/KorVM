"""
KorVM: FFI & Zero-Trust Sandbox Security Test
Author: Elif Nur Ayhan (codebygunes)
License: GPL-3.0
Description: Validates memory isolation, page limits, and FFI bridge security constraints.
"""
import sys
import os
import unittest

# src klasörünü path'e ekliyoruz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from sandbox.memory.sandbox_core import ZeroTrustSandbox

class TestZeroTrustSandboxFFI(unittest.TestCase):
    
    def setUp(self):
        # 1 sayfalık (64KB) güvenli sandbox başlatıyoruz, max limit 5 sayfa
        self.sandbox = ZeroTrustSandbox(initial_pages=1, max_pages=5)

    def test_valid_memory_access(self):
        """Test legitimate read/write operations within boundary limits."""
        try:
            self.sandbox.store_i32(0, 42)
            val = self.sandbox.load_i32(0)
            self.assertEqual(val, 42)
        except Exception as e:
            self.fail(f"Valid memory operation failed unexpectedly: {e}")

    def test_out_of_bounds_memory_access(self):
        """Test that out-of-bounds adversarial writes throw strict MemoryError exceptions."""
        illegal_offset = 64 * 1024 + 10  # 1. sayfanın dışı (64KB sınır ihlali)
        with self.assertRaises(MemoryError):
            self.sandbox.store_i32(illegal_offset, 1337)

    def test_negative_offset_handling(self):
        """Test that negative memory addresses are safely intercepted."""
        with self.assertRaises(MemoryError):
            self.sandbox.load_i32(-4)

if __name__ == "__main__":
    unittest.main()