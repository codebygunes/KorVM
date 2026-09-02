//! KorVM: End-to-End (E2E) Wasm Execution Pipeline Example
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Demonstrates loading, parsing, and executing a .wasm binary 
//!              through the hardware-assisted zero-trust execution pipeline.

use korvm_core::parser::SafeWasmParser;
use korvm_core::execute_wasm_safely;
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    println!("==============================================================");
    println!("[*] KORVM END-TO-END (E2E) PIPELINE INITIALIZED");
    println!("==============================================================");

    // 1. Parse command-line arguments for target .wasm file
    let args: Vec<String> = env::args().collect();
    let default_path = "tests/fixtures/sample.wasm".to_string();
    let wasm_path_str = args.get(1).unwrap_or(&default_path);
    
    let path = Path::new(wasm_path_str);
    
    // Fallback or read binary payload
    let wasm_bytes = if path.exists() {
        println!("[*] Loading target Wasm binary from: {}", path.display());
        match fs::read(path) {
            Ok(bytes) => bytes,
            Err(e) => {
                eprintln!("[!] ERROR: Failed to read Wasm file: {}", e);
                std::process::exit(1);
            }
        }
    } else {
        println!("[*] Target file not found locally. Using embedded W3C compliant stub.");
        // Minimal valid empty Wasm module binary payload as fallback
        b"\x00asm\x01\x00\x00\x00".to_vec()
    };

    println!("[*] Payload size: {} bytes", wasm_bytes.len());

    // 2. Run Safe Wasm Parser Validation
    println!("[*] Step 1/2: Validating module structure via SafeWasmParser...");
    match SafeWasmParser::validate_and_parse(&wasm_bytes) {
        Ok(_) => println!("[PASS] Module passed structural validation and magic checks."),
        Err(e) => {
            eprintln!("[FAIL] Module validation rejected payload: {:?}", e);
            std::process::exit(1);
        }
    }

    // 3. Execute via Hardware-Assisted Sandbox & Execution Pipeline
    println!("[*] Step 2/2: Executing payload through ZeroTrustSandbox / JIT pipeline...");
    match execute_wasm_safely(&wasm_bytes) {
        Ok(exit_code) => {
            println!("--------------------------------------------------------------");
            println!("[SUCCESS] E2E Execution Completed! Result / Exit Code: {}", exit_code);
            println!("==============================================================\n");
        }
        Err(e) => {
            eprintln!("--------------------------------------------------------------");
            eprintln!("[CRITICAL] Execution faulted safely: {:?}", e);
            eprintln!("==============================================================\n");
            std::process::exit(1);
        }
    }
}