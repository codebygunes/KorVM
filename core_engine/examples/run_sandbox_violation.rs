//! KorVM: Sandbox Boundary Violation & Security Fault Example
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Demonstrates hardware-level interception of out-of-bounds 
//!              memory access attacks through OS guard pages.

use korvm_core::sandbox::ZeroTrustSandbox;

fn main() {
    println!("==============================================================");
    println!("[*] KORVM SECURITY BREACH SIMULATION INITIALIZED");
    println!("==============================================================\n");

    // Initialize sandbox with 1 Wasm page (64KB)
    println!("[*] Allocating secure sandbox with 1 initial page (64KB)...");
    let mut sandbox = ZeroTrustSandbox::new(1, Some(4)).expect("Failed to create sandbox");

    println!("[*] Sandbox base pointer mapped at: {:p}", sandbox.base_ptr);

    // 1. Safe access within allocated boundary
    println!("[*] Test 1: Writing data to valid memory offset (0x100)...");
    match sandbox.store_i32(0x100, 1337) {
        Ok(_) => println!("[PASS] Valid write succeeded."),
        Err(e) => eprintln!("[FAIL] Unexpected error on valid write: {:?}", e),
    }

    // 2. Malicious / Out-of-bounds access attempt breaching guard region
    println!("[*] Test 2: Attempting malicious write to uncommitted guard region (3GB offset)...");
    let malicious_offset = 3 * 1024 * 1024 * 1024; // 3 GB deep into guard zone
    
    match sandbox.store_i32(malicious_offset, 9999) {
        Ok(_) => {
            eprintln!("[CRITICAL SECURITY VULNERABILITY] Guard page failed to intercept out-of-bounds write!");
            std::process::exit(1);
        }
        Err(e) => {
            println!("--------------------------------------------------------------");
            println!("[SECURE DEFENSE] Hardware Guillotine triggered successfully!");
            println!("[BLOCKED] Caught memory fault vector: {:?}", e);
            println!("==============================================================\n");
        }
    }
}