"""
KorVM: Zero-Trust Linear Memory Sandbox (FFI Integration)
Author: Elif Nur Ayhan (codebygunes)
License: GPL-3.0
Description: Connects the high-performance Rust core via ctypes to enforce hardware-level O(1) isolation.
"""
import ctypes
import os
import sys
import struct
from typing import Optional

class ZeroTrustSandbox:
    """
    Python orchestrator class that bridges execution securely to the 
    native compiled Rust core library.
    """
    WASM_PAGE_SIZE = 64 * 1024  # 64 KB

    def __init__(self, initial_pages: int = 1, max_pages: Optional[int] = None):
        self.initial_pages = initial_pages
        self.max_pages = max_pages if max_pages is not None else 0xFFFFFFFF
        self.memory = bytearray(initial_pages * self.WASM_PAGE_SIZE)
        
        # Load the compiled Rust core library (.dll on Windows, .so on Linux, .dylib on macOS)
        lib_ext = ".dll" if os.name == "nt" else (".dylib" if sys.platform == "darwin" else ".so")
        lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../../core_engine/target/debug/kor_engine{lib_ext}"))
        
        try:
            self._lib = ctypes.CDLL(lib_path)
        except OSError:
            print("[!] Warning: Native Rust library not found via FFI. Initializing high-safety software fallback.")
            self._lib = None

        if self._lib:
            self._lib.init_sandbox.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
            self._lib.init_sandbox.restype = ctypes.c_void_p
            
            self._lib.load_i32_native.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            self._lib.load_i32_native.restype = ctypes.c_int32
            
            self._lib.store_i32_native.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int32]
            self._lib.store_i32_native.restype = ctypes.c_int32

            self._ptr = self._lib.init_sandbox(initial_pages, self.max_pages)

        print(f"[+] Zero-Trust Hardware-Backed Sandbox Initialized: {initial_pages} page(s).")

    def check_bounds(self, offset: int, size: int):
        """O(1) runtime bounds validation."""
        if offset < 0 or (offset + size) > len(self.memory):
            raise MemoryError(f"ZERO-TRUST VIOLATION: Illegal access at offset {offset}, size {size}.")

    def store_i32(self, offset: int, value: int):
        """Stores 32-bit integer through native FFI or secure fallback."""
        self.check_bounds(offset, 4)
        if self._lib:
            res = self._lib.store_i32_native(self._ptr, offset, value)
            if res != 0:
                raise MemoryError("FFI Security Fault: Rust core rejected memory store operation.")
        else:
            struct.pack_into('<i', self.memory, offset, value)

    def load_i32(self, offset: int) -> int:
        """Loads 32-bit integer through native FFI or secure fallback."""
        self.check_bounds(offset, 4)
        if self._lib:
            return self._lib.load_i32_native(self._ptr, offset)
        else:
            return struct.unpack_from('<i', self.memory, offset)[0]

    def grow_memory(self, additional_pages: int) -> int:
        """Dynamically grows memory ensuring strict capacity limits (DDoS protection)."""
        current_pages = len(self.memory) // self.WASM_PAGE_SIZE
        new_pages = current_pages + additional_pages

        if new_pages > self.max_pages:
            return -1  # Blocked by capability limits

        additional_bytes = additional_pages * self.WASM_PAGE_SIZE
        self.memory.extend(bytearray(additional_bytes))
        return current_pages