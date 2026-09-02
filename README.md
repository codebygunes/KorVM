# KorVM: Zero-Trust WebAssembly Runtime & Execution Engine

**Author:** Elif Nur Ayhan (`codebygunes`)  
**License:** Apache-2.0  
**Current Phase:** Milestone 1 (Parser & Core Architecture Foundation)  

---

## 🚀 Vision & Overview

**KorVM** is an experimental, highly secure, and fault-tolerant WebAssembly (WASM) virtual machine and runtime environment engineered with a strict **Zero-Trust** architecture. KorVM aims to eliminate linear memory vulnerabilities, out-of-bounds pointer exploits, and resource exhaustion attacks at the engine level.

As part of our open-source roadmap, KorVM is developed systematically through structured milestones—beginning with robust binary parsing and advancing toward an optimized JIT execution engine.

---

## 🏛️ Planned Modular Architecture

* **WASM Parser (`core/parser/`):** W3C binary format compliance and LEB128 decoding *(Active - Milestone 1)*.
* **Zero-Trust Memory Sandbox (`sandbox/memory/`):** $O(1)$ constant-time boundary checking and linear memory isolation *(Milestone 2)*.
* **Baseline Stack Interpreter (`core/interpreter/`):** Secure opcode evaluation and stack management *(Milestone 3)*.
* **SelfOpt JIT Compiler (`core/jit/`):** Hot-loop detection and fast-path execution profiler *(Milestone 4)*.

---

## 📅 Roadmap & Milestones

| Milestone | Description | Status |
| :--- | :--- | :--- |
| **Milestone 1** | W3C Binary Parser & LEB128 Decoder Implementation | **In Progress / Current** |
| **Milestone 2** | Zero-Trust Linear Memory Sandbox & DDoS Defenses | *Planned* |
| **Milestone 3** | Baseline Stack-Machine Interpreter | *Planned* |
| **Milestone 4** | SelfOpt JIT Compiler & Omni-Fuzzer Chaos Suites | *Planned* |

---

## 📄 License

Distributed under the **Apache-2.0 License**. See `LICENSE` for more information.

### Proof of Concept: End-to-End Native JIT Execution

Aşağıdaki çalıştırma kaydı (Execution Log), KorVM'in LLVM/Rust ile derlenmiş **1.4 MB'lık standart bir WebAssembly dosyasını** uçtan uca nasıl başarıyla ayrıştırdığını (W3C parsing), Code Section'dan hedef baytları nasıl izole ettiğini ve `SelfOpt` motoru üzerinden **OS seviyesinde (PROT_EXEC)** nasıl anında x86-64 makine koduna çevirdiğini kanıtlamaktadır:

```console
$ python run_demo.py
============================================================
[*] Loading real WebAssembly binary: demo.wasm
============================================================
[+] Loaded 1475016 bytes successfully.

[*] Passing to W3C-Compliant Parser...
[+] Header validated successfully. WASM Binary Version: 1
[+] Parsing Section: Type (ID: 1, Size: 7 bytes)
    -> Decoded 1 function signature types.
[+] Parsing Section: Function (ID: 3, Size: 2 bytes)
    -> Decoded 1 function declarations.
[+] Parsing Section: Table (ID: 4, Size: 5 bytes)
[+] Parsing Section: Memory (ID: 5, Size: 3 bytes)
    -> Decoded 1 linear memory definitions.
[+] Parsing Section: Global (ID: 6, Size: 25 bytes)
    -> Decoded 3 globals.
[+] Parsing Section: Export (ID: 7, Size: 43 bytes)
    -> Decoded 4 exports.
[+] Parsing Section: Code (ID: 10, Size: 9 bytes)
    -> Decoded 1 function code bodies.
[+] Parsing Section: Custom (ID: 0, Size: 4149 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 385737 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 94990 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 750576 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 239152 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 45 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 77 bytes)
[+] Parsing Section: Custom (ID: 0, Size: 148 bytes)
[+] Parser verification passed. Binary structure is strictly W3C valid.

[*] Extracting Target Function Bytecode from .wasm Sections...
[+] SUCCESS: Isolated authentic LLVM/Rust bytecode sequence from Code Section!
    -> Extracted Opcodes: 200020016A0B

[*] Routing AUTHENTIC Bytecode to SelfOpt JIT Engine...
    [*] SLOW PATH: Interpreting 'demo_add_function' (1/3)
    [*] SLOW PATH: Interpreting 'demo_add_function' (2/3)

    [JIT] HOT LOOP DETECTED: Translating 'demo_add_function' dynamically.
    [JIT TRANSLATOR] Parsing 6 bytes of authentic WASM to x86-64...
    [JIT EMITTER] Success! Compiled 17 bytes to RAM address 0x1b00f000000

[SUCCESS] True End-to-End pipeline executed flawlessly!
    -> Final State: [Native Hardware Execution | Result: 12]
```