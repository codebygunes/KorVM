# KorVM Architecture Specification

## 1. System Overview
Kor (KorVM) is a lightweight, zero-trust WebAssembly (WASM) runtime and sandbox designed for secure edge computing and strict memory isolation. It executes WASM binaries while ensuring that untrusted code cannot escape its predefined linear memory boundaries or execute unauthorized system calls.

## 2. Core Components

The architecture is strictly modular, consisting of four primary pipelines:

### A. Parser & Decoder (`src/core/parser`)
- **Binary Reader:** Reads the `.wasm` binary format according to the IEEE 754 and W3C WebAssembly Core Specification.
- **Validation Engine:** Performs ahead-of-time (AOT) type checking and opcode validation before any execution begins, rejecting malformed binaries to prevent runtime exploits.

### B. Zero-Trust Sandbox (`src/sandbox`)
- **Linear Memory Boundary:** All WASM instances operate within a strict contiguous byte array (linear memory). Memory accesses are bounds-checked at runtime using bit-masking or hardware-assisted guard pages to guarantee $O(1)$ verification overhead.
- **Capability-Based Syscalls:** System calls are disabled by default. Kor provides a restricted pseudo-WASI (WebAssembly System Interface) layer where permissions (e.g., file read, network) must be explicitly injected by the host.

### C. Execution Engine (`src/core/interpreter`)
- **Baseline Interpreter:** A fast-startup, stack-based virtual machine loop for immediate execution of instructions without compilation latency. Ideal for small, short-lived edge functions.

### D. SelfOpt JIT Compiler (`src/core/jit`)
- **Semantic Optimizer:** For hot code paths, the interpreter dynamically hands over execution to the JIT pipeline. 
- **Native Emission:** Compiles WASM bytecodes to native machine instructions, applying inline caching and dead-code elimination while preserving the sandbox boundaries via instrumentation.

## 3. Data Flow
1. Host loads `module.wasm` -> `Parser`
2. `Parser` validates and extracts sections (Code, Memory, Data) -> `Environment`
3. `Sandbox` allocates isolated linear memory for the `Environment`.
4. `Execution Engine` begins executing the `_start` function.
5. If thresholds are met, `SelfOpt JIT` compiles hot loops to native code.