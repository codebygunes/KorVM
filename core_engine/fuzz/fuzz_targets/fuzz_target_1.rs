#![no_main]
use libfuzzer_sys::fuzz_target;
use kor_engine::ZeroTrustSandbox;

/*
 * KorVM: Coverage-Guided Memory Sandbox Fuzzing
 * Author: Elif Nur Ayhan (codebygunes)
 * License: GPL-3.0
 */

fuzz_target!(|data: &[u8]| {
    // Fuzzer'ın ürettiği veriyi offset ve işlem türü olarak kullanalım
    if data.len() < 5 {
        return;
    }

    // 1. bayt: O(1) bellekte Okuma mı Yazma mı yapılacağını belirler
    let operation = data[0] % 2; 
    
    // Sonraki 4 bayt: Tamamen fuzzer'ın mutasyonla ürettiği bir bellek adresi (offset)
    let offset = u32::from_le_bytes([data[1], data[2], data[3], data[4]]) as usize;

    // 1 sayfalık (64KB) bir sandbox başlatıyoruz
    let mut sandbox = ZeroTrustSandbox::new(1, Some(10)).unwrap();

    // Akıllı fuzzer'ın ürettiği korkunç offset'lerle sandbox'a saldırıyoruz!
    if operation == 0 {
        // Okuma Saldırısı
        let _ = sandbox.load_i32(offset); 
    } else {
        // Yazma Saldırısı
        let _ = sandbox.store_i32(offset, 1337); 
    }
    
    // EĞER SANDBOX BU OFFSET'E İZİN VERİRSE RUST 'PANIC' ATACAK VE FUZZER BUNU ZAFİYET OLARAK YAKALAYACAK.
    // Ancak Zero-Trust algoritmamız sayesinde sadece Result::Err dönecek ve sistem dimdik ayakta kalacak.
});