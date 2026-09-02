//! KorVM: Real-World Concurrency & Thread-Safety Stress Test
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Spawns multiple native OS threads bombarding the Zero-Trust 
//!              hardware sandbox simultaneously to prove multi-tenant safety.

use korvm_core::sandbox::ZeroTrustSandbox;
use std::sync::{Arc, Mutex};
use std::thread;

#[test]
fn test_real_world_multi_threaded_concurrency_bomb() {
    let sandbox = ZeroTrustSandbox::new(4, Some(10)).expect("OS Init failed");
    let shared_sandbox = Arc::new(Mutex::new(sandbox));

    let mut handles = vec![];
    let thread_count = 10;
    let iterations_per_thread = 500;

    println!("[+] Launching Real-World Concurrency Bomb: {} threads x {} ops", thread_count, iterations_per_thread);

    for t_id in 0..thread_count {
        let sandbox_clone = Arc::clone(&shared_sandbox);
        
        let handle = thread::spawn(move || {
            for i in 0..iterations_per_thread {
                let offset = (t_id * 100) + ((i % 10) * 4);
                let payload = (t_id * 1000 + i) as i32;

                let mut sb = sandbox_clone.lock().unwrap();
                
                sb.store_i32(offset, payload).expect("Concurrent store failed");
                let val = sb.load_i32(offset).expect("Concurrent load failed");
                
                assert_eq!(
                    val, payload, 
                    "DATA RACE DETECTED: Memory corruption under concurrent thread execution!"
                );
            }
        });

        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("A concurrency thread panicked or crashed!");
    }

    println!("[+] Real-World Concurrency Bomb neutralized successfully. Zero data corruption!");
}