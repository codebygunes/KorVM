use korvm_core::{execute_wasm_safely, sandbox::ZeroTrustSandbox};

#[test]
fn test_real_wasm_binary_execution_pipeline() {
    // Geçerli bir Wasm dosyası simülasyonu için minimal W3C binary (Magic + Version)
    let valid_wasm_payload: &[u8] = &[
        0x00, 0x61, 0x73, 0x6d, // Magic bytes: \0asm
        0x01, 0x00, 0x00, 0x00, // Version: 1
    ];

    // Hatayı detaylı görebilmek için expect kullanıyoruz
    let result = execute_wasm_safely(valid_wasm_payload);
    
    match result {
        Ok(val) => assert_eq!(val, 42),
        Err(e) => panic!("Execution pipeline failed with error: {:?}", e),
    }
}

#[test]
fn test_real_hardware_sandbox_boundaries() {
    let mut sandbox = ZeroTrustSandbox::new(1, Some(2))
        .expect("Failed to initialize hardware sandbox arena");

    let write_res = sandbox.store_i32(0, 12345);
    assert!(write_res.is_ok(), "In-bounds memory write failed");

    let read_val = sandbox.load_i32(0).expect("Failed to read from sandbox memory");
    assert_eq!(read_val, 12345, "Memory read/write consistency check failed");
}

#[test]
fn test_malformed_wasm_rejection() {
    let malicious_payload: &[u8] = &[
        0x45, 0x56, 0x49, 0x4c, // Invalid magic bytes
        0x01, 0x00, 0x00, 0x00,
    ];

    let result = execute_wasm_safely(malicious_payload);
    assert!(result.is_err(), "Security vulnerability: Malformed Wasm binary was accepted!");
}