//! KorVM Core Engine Library Entrypoint
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Exposes the Zero-Trust execution API, ensuring no panics escape the boundary.

// Declare modules correctly so the compiler maps them to error.rs, parser.rs, jit.rs, sandbox.rs
pub mod error;
pub mod parser;
pub mod jit;
pub mod sandbox;

// Import types using proper absolute paths within the crate
use crate::error::KorVmError;
use crate::parser::SafeWasmParser;
use crate::jit::KorVmJitEngine;

/// Main execution pipeline for the KorVM Rust Core.
/// Returns a graceful Result instead of panicking on invalid binaries or unsafe boundaries.
pub fn execute_wasm_safely(wasm_bytes: &[u8]) -> Result<i32, KorVmError> {
    // 1. Safe parsing step (Zero Unwraps)
    SafeWasmParser::validate_and_parse(wasm_bytes)?;

    // 2. Safe JIT Compilation & Execution Step
    let mut engine = KorVmJitEngine::new()?;
    
    let execution_result = engine.compile_and_execute_dummy()?;
    
    Ok(execution_result)
}