"""
KorVM: Baseline Stack-Machine Interpreter - Milestone 3
Author: Elif Nur Ayhan (codebygunes)
License: Apache-2.0
Description: Stack-based execution engine interpreting WebAssembly bytecode.
"""

from core.parser.wasm_parser import LEB128Decoder
from sandbox.memory.sandbox_core import ZeroTrustSandbox

# Essential WASM Opcodes (W3C Specification)
OP_UNREACHABLE = 0x00
OP_NOP         = 0x01
OP_END         = 0x0B
OP_I32_LOAD    = 0x28
OP_I32_STORE   = 0x36
OP_I32_CONST   = 0x41
OP_I32_ADD     = 0x6A
OP_I32_SUB     = 0x6B
OP_I32_MUL     = 0x6C

class BaselineInterpreter:
    """
    A fast, safe, stack-based execution engine for WebAssembly.
    Executes raw bytecode and guarantees all memory operations pass through the ZeroTrustSandbox.
    """
    def __init__(self, memory: ZeroTrustSandbox):
        self.memory = memory
        self.stack = []
        self.cursor = 0
    
    def execute(self, bytecode: bytes) -> list:
        """Executes a stream of WASM bytecode instructions."""
        self.cursor = 0
        self.stack.clear()
        length = len(bytecode)

        print("\n[*] Engine: Execution loop started...")

        while self.cursor < length:
            opcode = bytecode[self.cursor]
            self.cursor += 1

            if opcode == OP_END:
                break
            
            elif opcode == OP_NOP:
                continue

            elif opcode == OP_I32_CONST:
                val, self.cursor = LEB128Decoder.decode_i32(bytecode, self.cursor)
                self.stack.append(val)
                print(f"    [EXEC] i32.const {val}")

            elif opcode == OP_I32_ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                res = (a + b) & 0xFFFFFFFF
                self.stack.append(res)
                print(f"    [EXEC] i32.add ({a} + {b}) -> {res}")

            elif opcode == OP_I32_SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                res = (a - b) & 0xFFFFFFFF
                self.stack.append(res)
                print(f"    [EXEC] i32.sub ({a} - {b}) -> {res}")
            
            elif opcode == OP_I32_MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                res = (a * b) & 0xFFFFFFFF
                self.stack.append(res)
                print(f"    [EXEC] i32.mul ({a} * {b}) -> {res}")

            elif opcode == OP_I32_STORE:
                align, self.cursor = LEB128Decoder.decode_u32(bytecode, self.cursor)
                offset, self.cursor = LEB128Decoder.decode_u32(bytecode, self.cursor)
                
                val = self.stack.pop()
                base_addr = self.stack.pop()
                effective_addr = base_addr + offset
                
                self.memory.store_i32(effective_addr, val)
                print(f"    [EXEC] i32.store at addr {effective_addr} (value: {val})")

            elif opcode == OP_I32_LOAD:
                align, self.cursor = LEB128Decoder.decode_u32(bytecode, self.cursor)
                offset, self.cursor = LEB128Decoder.decode_u32(bytecode, self.cursor)
                
                base_addr = self.stack.pop()
                effective_addr = base_addr + offset
                
                val = self.memory.load_i32(effective_addr)
                self.stack.append(val)
                print(f"    [EXEC] i32.load from addr {effective_addr} -> {val}")

            else:
                raise NotImplementedError(f"Engine Fault: Opcode {hex(opcode)} not implemented.")
        
        print("[+] Engine: Execution completed.")
        return self.stack
