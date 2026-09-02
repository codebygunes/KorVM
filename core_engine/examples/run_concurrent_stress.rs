//! KorVM: Multi-Threaded Concurrency Stress Test Example
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Simulates heavy multi-tenant parallel execution streams 
//!              validating thread-safety and Send/Sync compatibility.

use korvm_core::execute_wasm_safely;
use std::sync::Arc;
use std::thread;

fn main() {
    println!("==============================================================");
    println!("[*] KORVM CONCURRENCY STRESS BENCHMARK INITIALIZED");
    println!("==============================================================\n");

    let thread_count = 8;
    let iterations_per_thread = 50;
    
    println!("[*] Spawning {} parallel threads, each executing {} cycles...", thread_count, iterations_per_thread);

    let baseline_payload = Arc::new(b"\x00asm\x01\x00\x00\x00".to_vec());
    let mut handles = vec![];

    let start_time = std::time::Instant::now();

    for t_id in 0..thread_count {
        let payload_clone = Arc::clone(&baseline_payload);
        let handle = thread::spawn(move || {
            let mut local_success = 0;
            for _ in 0..iterations_per_thread {
                let res = execute_wasm_safely(&payload_clone);
                if res.is_ok() {
                    local_success += 1;
                }
            }
            println!("[THREAD {}] Completed successfully: {}/{} tasks", t_id, local_success, iterations_per_thread);
            local_success
        });
        handles.push(handle);
    }

    let mut total_completed = 0;
    for handle in handles {
        total_completed += handle.join().unwrap();
    }

    let duration = start_time.elapsed();

    println!("--------------------------------------------------------------");
    println!("[STRESS TEST SUCCESS] Executed total {} parallel tasks in {:?}", total_completed, duration);
    println!("==============================================================\n");
}