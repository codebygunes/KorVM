//! KorVM Core Error Handling Architecture
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0

use thiserror::Error;

/// Defines all strictly categorized, recoverable errors across the KorVM lifecycle.
/// Eliminates the need for .unwrap() and prevents untracked system panics.
#[derive(Error, Debug)]
pub enum KorVmError {
    #[error("WASM Parsing Fault: {0}")]
    ParseError(String),

    #[error("JIT Compilation Fault: {0}")]
    CompilationError(String),

    #[error("Runtime Execution Fault: {0}")]
    ExecutionError(String),

    #[error("Zero-Trust Memory Boundary Violation: {0}")]
    MemoryFault(String),

    #[error("Unimplemented WASM Feature Requested: {0}")]
    UnimplementedFeature(String),
}