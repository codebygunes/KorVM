/*
 * KorVM: Zero-Trust Linear Memory Sandbox (Rust Core)
 * Author: Elif Nur Ayhan (codebygunes)
 * License: GPL-3.0
 * Description: Implements O(1) linear memory isolation and capability-based boundary checks.
 */

pub const WASM_PAGE_SIZE: usize = 64 * 1024; // 64 KB standart WebAssembly sayfası

pub struct ZeroTrustSandbox {
    pub memory: Vec<u8>,
    pub max_pages: Option<usize>,
}

impl ZeroTrustSandbox {
    /// Sandbox'ı belirtilen sayfa limitleriyle güvenli bir şekilde başlatır.
    pub fn new(initial_pages: usize, max_pages: Option<usize>) -> Result<Self, &'static str> {
        if let Some(max) = max_pages {
            if initial_pages > max {
                return Err("SECURITY BREACH: initial_pages exceeds strict max_pages limit");
            }
        }

        // Güvenli bellek tahsisi: Integer overflow (taşma) riskine karşı 'checked_mul' kullanıyoruz.
        let memory_size = initial_pages.checked_mul(WASM_PAGE_SIZE)
            .ok_or("CRITICAL: Memory allocation integer overflow!")?;
            
        Ok(Self {
            memory: vec![0; memory_size], // Belleği tamamen sıfırlayarak tahsis ediyoruz
            max_pages,
        })
    }

    /// O(1) karmaşıklığında çalışan temel sınır kontrol algoritması. 
    /// Fuzzer'ın saldırdığı kilit nokta burasıdır.
    pub fn check_bounds(&self, offset: usize, size: usize) -> Result<(), &'static str> {
        // Fuzzer devasa sayılar gönderdiğinde çökmemesi için 'checked_add' şarttır.
        let end_offset = offset.checked_add(size)
            .ok_or("ZERO-TRUST VIOLATION: Integer overflow detected during memory access!")?;
        
        if end_offset > self.memory.len() {
            Err("ZERO-TRUST VIOLATION: Illegal out-of-bounds memory access attempt!")
        } else {
            Ok(())
        }
    }

    /// Linear bellekten 32-bit tamsayı okur (WASM Little-Endian standartlarına uygun).
    pub fn load_i32(&self, offset: usize) -> Result<i32, &'static str> {
        // Önce O(1) sınır kontrolü yapılır. Başarısız olursa Rust panic atmaz, kontrollü hata döner.
        self.check_bounds(offset, 4)?;
        
        let bytes = [
            self.memory[offset],
            self.memory[offset + 1],
            self.memory[offset + 2],
            self.memory[offset + 3],
        ];
        
        Ok(i32::from_le_bytes(bytes))
    }

    /// Linear belleğe 32-bit tamsayı yazar.
    pub fn store_i32(&mut self, offset: usize, value: i32) -> Result<(), &'static str> {
        // Yazma işleminden önce mutlak sınır kontrolü
        self.check_bounds(offset, 4)?;
        
        let bytes = value.to_le_bytes();
        self.memory[offset] = bytes[0];
        self.memory[offset + 1] = bytes[1];
        self.memory[offset + 2] = bytes[2];
        self.memory[offset + 3] = bytes[3];
        
        Ok(())
    }
    
    /// Bellek boyutunu WASM 'memory.grow' komutuna benzer şekilde dinamik ve güvenli artırır.
    pub fn grow_memory(&mut self, additional_pages: usize) -> Result<usize, &'static str> {
        let current_pages = self.memory.len() / WASM_PAGE_SIZE;
        let new_pages = current_pages.checked_add(additional_pages)
            .ok_or("CRITICAL: Page count integer overflow!")?;

        // Sınır aşımı kontrolü (DDoS Koruması)
        if let Some(max) = self.max_pages {
            if new_pages > max {
                return Err("DDoS PROTECTION: Growth denied, exceeds max_pages limitation");
            }
        }

        let additional_bytes = additional_pages.checked_mul(WASM_PAGE_SIZE)
            .ok_or("CRITICAL: Additional byte calculation overflow!")?;
            
        // Belleği yeni boyuta genişlet (yeni alanlar güvenli olması için sıfırlarla doldurulur)
        self.memory.resize(self.memory.len() + additional_bytes, 0);
        
        Ok(current_pages)
    }
}