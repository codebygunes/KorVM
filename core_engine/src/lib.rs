//! KorVM: Zero-Trust Linear Memory Sandbox (Rust Core)
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Implements O(1) linear memory isolation and capability-based boundary checks.

use crate::error::KorVmError;

pub const WASM_PAGE_SIZE: usize = 64 * 1024; // 64 KB standard WebAssembly page

pub struct ZeroTrustSandbox {
    pub memory: Vec<u8>,
    pub max_pages: Option<usize>,
}

impl ZeroTrustSandbox {
    /// Initializes the sandbox safely with specified page limits.
    pub fn new(initial_pages: usize, max_pages: Option<usize>) -> Result<Self, KorVmError> {
        if let Some(max) = max_pages {
            if initial_pages > max {
                return Err(KorVmError::MemoryFault(
                    "SECURITY BREACH: initial_pages exceeds strict max_pages limit".to_string()
                ));
            }
        }

        // Safe memory allocation: Using 'checked_mul' to prevent integer overflow attacks.
        let memory_size = initial_pages
            .checked_mul(WASM_PAGE_SIZE)
            .ok_or_else(|| KorVmError::MemoryFault("CRITICAL: Memory allocation integer overflow!".to_string()))?;
            
        Ok(Self {
            memory: vec![0; memory_size], // Allocate and zero-initialize memory
            max_pages,
        })
    }

    /// O(1) complexity foundational boundary check algorithm.
    /// This is the primary defense mechanism tested against fuzzers.
    pub fn check_bounds(&self, offset: usize, size: usize) -> Result<(), KorVmError> {
        // 'checked_add' is mandatory to prevent overflows when malicious huge offsets are provided.
        let end_offset = offset
            .checked_add(size)
            .ok_or_else(|| KorVmError::MemoryFault("ZERO-TRUST VIOLATION: Integer overflow detected during memory access!".to_string()))?;
        
        if end_offset > self.memory.len() {
            Err(KorVmError::MemoryFault("ZERO-TRUST VIOLATION: Illegal out-of-bounds memory access attempt!".to_string()))
        } else {
            Ok(())
        }
    }

    /// Reads a 32-bit integer from linear memory (WASM Little-Endian compliant).
    pub fn load_i32(&self, offset: usize) -> Result<i32, KorVmError> {
        // Perform O(1) boundary check first. Returns a controlled error instead of panicking on failure.
        self.check_bounds(offset, 4)?;
        
        let bytes = [
            self.memory[offset],
            self.memory[offset + 1],
            self.memory[offset + 2],
            self.memory[offset + 3],
        ];
        
        Ok(i32::from_le_bytes(bytes))
    }

    /// Writes a 32-bit integer to linear memory.
    pub fn store_i32(&mut self, offset: usize, value: i32) -> Result<(), KorVmError> {
        // Absolute boundary check before any write operation
        self.check_bounds(offset, 4)?;
        
        let bytes = value.to_le_bytes();
        self.memory[offset] = bytes[0];
        self.memory[offset + 1] = bytes[1];
        self.memory[offset + 2] = bytes[2];
        self.memory[offset + 3] = bytes[3];
        
        Ok(())
    }
    
    /// Dynamically and safely increases memory size, simulating WASM 'memory.grow' instruction.
    pub fn grow_memory(&mut self, additional_pages: usize) -> Result<usize, KorVmError> {
        let current_pages = self.memory.len() / WASM_PAGE_SIZE;
        let new_pages = current_pages
            .checked_add(additional_pages)
            .ok_or_else(|| KorVmError::MemoryFault("CRITICAL: Page count integer overflow!".to_string()))?;

        // Boundary limit check (DDoS Protection against resource exhaustion)
        if let Some(max) = self.max_pages {
            if new_pages > max {
                return Err(KorVmError::MemoryFault("DDoS PROTECTION: Growth denied, exceeds max_pages limitation".to_string()));
            }
        }

        let additional_bytes = additional_pages
            .checked_mul(WASM_PAGE_SIZE)
            .ok_or_else(|| KorVmError::MemoryFault("CRITICAL: Additional byte calculation overflow!".to_string()))?;
            
        // Expand memory to the new size (new areas are zero-filled for security)
        self.memory.resize(self.memory.len() + additional_bytes, 0);
        
        Ok(current_pages)
    }
}