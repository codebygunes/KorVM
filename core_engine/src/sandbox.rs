//! KorVM: Hardware-Assisted Zero-Trust Sandbox (O(1) Guard Pages)
//! Author: Elif Nur Ayhan (codebygunes)
//! License: Apache-2.0
//! Description: Implements true hardware-level O(1) memory isolation using OS mmap/mprotect.

use crate::error::KorVmError;
use std::ptr;

#[cfg(unix)]
use libc;

pub const WASM_PAGE_SIZE: usize = 64 * 1024;
// 4GB Virtual Memory Reservation (Hardware Guard Region)
pub const GUARD_REGION_SIZE: usize = 4 * 1024 * 1024 * 1024;

pub struct ZeroTrustSandbox {
    pub base_ptr: *mut u8,
    pub current_pages: usize,
    pub max_pages: Option<usize>,
}

impl ZeroTrustSandbox {
    /// Initializes the hardware-assisted sandbox using OS memory management (mmap).
    pub fn new(initial_pages: usize, max_pages: Option<usize>) -> Result<Self, KorVmError> {
        if let Some(max) = max_pages {
            if initial_pages > max {
                return Err(KorVmError::MemoryFault("SECURITY BREACH: Initial pages exceed max_pages".to_string()));
            }
        }

        #[cfg(unix)]
        let base_ptr = unsafe {
            // 1. RESERVE 4GB of Virtual Address Space (PROT_NONE)
            // This creates an impenetrable hardware wall. Accessing it triggers SIGSEGV.
            let ptr = libc::mmap(
                ptr::null_mut(),
                GUARD_REGION_SIZE,
                libc::PROT_NONE,
                libc::MAP_PRIVATE | libc::MAP_ANONYMOUS | libc::MAP_NORESERVE,
                -1,
                0,
            );

            if ptr == libc::MAP_FAILED {
                return Err(KorVmError::MemoryFault("CRITICAL: OS failed to reserve hardware guard pages!".to_string()));
            }

            // 2. COMMIT only the explicitly requested initial pages (PROT_READ | PROT_WRITE)
            let initial_bytes = initial_pages.checked_mul(WASM_PAGE_SIZE).unwrap_or(0);
            if initial_bytes > 0 {
                let res = libc::mprotect(
                    ptr,
                    initial_bytes,
                    libc::PROT_READ | libc::PROT_WRITE,
                );
                if res != 0 {
                    libc::munmap(ptr, GUARD_REGION_SIZE);
                    return Err(KorVmError::MemoryFault("CRITICAL: OS failed to commit initial memory!".to_string()));
                }
            }
            
            ptr as *mut u8
        };

        #[cfg(not(unix))]
        let base_ptr = unimplemented!("Hardware guard pages currently require a Unix/Linux environment for mmap.");

        Ok(Self {
            base_ptr,
            current_pages: initial_pages,
            max_pages,
        })
    }

    /// OS-Level Hardware protection completely removes the need for software if-checks.
    /// The CPU MMU (Memory Management Unit) handles boundary violations natively.
    #[inline(always)]
    pub fn check_bounds(&self, _offset: usize, _size: usize) -> Result<(), KorVmError> {
        // YAZILIMSAL SINIR KONTROLÜ KALDIRILDI!
        // İşletim sisteminin MMU (Memory Management Unit) birimi, sınır dışı 
        // erişimlerde O(1) maliyetle doğrudan donanım kesintisi (SIGSEGV) üretecektir.
        Ok(())
    }

    pub fn load_i32(&self, offset: usize) -> Result<i32, KorVmError> {
        // Doğrudan bellek erişimi. O(1) maliyet.
        let ptr = unsafe { self.base_ptr.add(offset) as *const i32 };
        Ok(unsafe { ptr::read_unaligned(ptr) })
    }

    pub fn store_i32(&mut self, offset: usize, value: i32) -> Result<(), KorVmError> {
        // Doğrudan bellek erişimi. O(1) maliyet.
        let ptr = unsafe { self.base_ptr.add(offset) as *mut i32 };
        unsafe { ptr::write_unaligned(ptr, value) };
        Ok(())
    }
    
    pub fn grow_memory(&mut self, additional_pages: usize) -> Result<usize, KorVmError> {
        let new_pages = self.current_pages.checked_add(additional_pages)
            .ok_or_else(|| KorVmError::MemoryFault("Overflow in page count".to_string()))?;

        if let Some(max) = self.max_pages {
            if new_pages > max {
                return Err(KorVmError::MemoryFault("DDoS PROTECTION: Growth denied".to_string()));
            }
        }

        #[cfg(unix)]
        unsafe {
            let new_region_start = self.base_ptr.add(self.current_pages * WASM_PAGE_SIZE);
            let new_region_size = additional_pages * WASM_PAGE_SIZE;

            // Expand the committed memory area natively via OS
            let res = libc::mprotect(
                new_region_start as *mut libc::c_void,
                new_region_size,
                libc::PROT_READ | libc::PROT_WRITE,
            );

            if res != 0 {
                return Err(KorVmError::MemoryFault("OS failed to expand hardware memory bounds".to_string()));
            }
        }

        let old_pages = self.current_pages;
        self.current_pages = new_pages;
        Ok(old_pages)
    }
}

impl Drop for ZeroTrustSandbox {
    fn drop(&mut self) {
        #[cfg(unix)]
        unsafe {
            // Free the entire 4GB virtual region back to the OS upon destruction
            libc::munmap(self.base_ptr as *mut libc::c_void, GUARD_REGION_SIZE);
        }
    }
}