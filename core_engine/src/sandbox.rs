/// KorVM: Production-Grade Zero-Trust Linear Memory Sandbox (Rust Core)
/// Author: Elif Nur Ayhan (codebygunes)

pub struct ZeroTrustSandbox {
    memory: Vec<u8>,
    max_pages: Option<usize>,
}

const WASM_PAGE_SIZE: usize = 64 * 1024; // 64 KB

impl ZeroTrustSandbox {
    pub fn new(initial_pages: usize, max_pages: Option<usize>) -> Self {
        let memory_size = initial_pages * WASM_PAGE_SIZE;
        println!("[+] Rust Sandbox Initialized: {} bytes allocated.", memory_size);
        Self {
            memory: vec![0; memory_size],
            max_pages,
        }
    }

    #[inline(always)]
    pub fn check_bounds(&self, offset: usize, size: usize) -> Result<(), &'static str> {
        if offset.checked_add(size).map_or(true, |end| end > self.memory.len()) {
            return Err("ZERO-TRUST VIOLATION: Illegal memory access attempt!");
        }
        Ok(())
    }

    pub fn store_i32(&mut self, offset: usize, value: i32) -> Result<(), &'static str> {
        self.check_bounds(offset, 4)?;
        let bytes = value.to_le_bytes();
        self.memory[offset..offset + 4].copy_from_slice(&bytes);
        Ok(())
    }

    pub fn load_i32(&self, offset: usize) -> Result<i32, &'static str> {
        self.check_bounds(offset, 4)?;
        let bytes: [u8; 4] = self.memory[offset..offset + 4]
            .try_into()
            .map_err(|_| "Memory conversion error")?;
        Ok(i32::from_le_bytes(bytes))
    }
}