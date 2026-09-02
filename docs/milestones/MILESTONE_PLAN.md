# KorVM: Project Milestones & Budget Plan

**Total Requested Budget:** €50,000
**Estimated Timeline:** 8 Months

## Milestone 1: Core WASM Decoder & Baseline Interpreter
**Budget:** €10,000 | **Duration:** 2 Months
- **Goal:** Implement a fully compliant WASM binary parser and stack-based interpreter.
- **Deliverables:**
  - Complete reading of all standard WASM sections (Type, Function, Code, Export).
  - Implementation of numeric and control-flow instructions.
  - Passing core test suites from the official WebAssembly spec repository.
- **Verification:** Source code published on GitHub; automated CI passing the baseline tests.

## Milestone 2: Zero-Trust Linear Memory Sandbox
**Budget:** €15,000 | **Duration:** 2 Months
- **Goal:** Architect the isolation layer ensuring memory safety and boundary protection.
- **Deliverables:**
  - Implementation of strict linear memory allocation.
  - O(1) runtime bounds-checking mechanisms for memory load/store instructions.
  - Development of the Capability-Based Syscall filtering module.
- **Verification:** Security audit report demonstrating containment; unit tests simulating out-of-bounds exploits failing gracefully.

## Milestone 3: SelfOpt JIT Integration & Performance Pipeline
**Budget:** €15,000 | **Duration:** 2.5 Months
- **Goal:** Integrate a semantic Just-In-Time (JIT) compiler to accelerate hot code paths without compromising sandbox security.
- **Deliverables:**
  - Profiling engine to identify hot loops during interpreter execution.
  - Native code emission module with sandboxed instruction generation.
  - Minimum 3x performance increase over the baseline interpreter.
- **Verification:** Benchmark suite results comparing baseline vs. JIT execution times.

## Milestone 4: WASI Integration, Security Testing & v1.0 Release
**Budget:** €10,000 | **Duration:** 1.5 Months
- **Goal:** Make KorVM ready for production edge workloads and open-source distribution.
- **Deliverables:**
  - Implementation of essential WASI (WebAssembly System Interface) modules (fs, random).
  - Fuzzing campaign for the parser and execution engine.
  - Comprehensive documentation, API references, and architecture guides.
- **Verification:** v1.0 Release published; Fuzzing results published; Community announcement.