// KorVM: Production-Grade Zero-Trust Linear Memory Sandbox (Zig Core)
// Author: Elif Nur Ayhan (codebygunes)

const std = @import("std");

const WASM_PAGE_SIZE: usize = 64 * 1024;

const ZeroTrustSandbox = struct {
    memory: []u8,
    allocator: std.mem.Allocator,

    pub fn init(allocator: std.mem.Allocator, initial_pages: usize) !ZeroTrustSandbox {
        const mem_size = initial_pages * WASM_PAGE_SIZE;
        const mem = try allocator.alloc(u8, mem_size);
        @memset(mem, 0);
        std.debug.print("[+] Zig Sandbox Initialized: {} bytes allocated.\n", .{mem_size});
        return .{
            .memory = mem,
            .allocator = allocator,
        };
    }

    pub fn deinit(self: *ZeroTrustSandbox) void {
        self.allocator.free(self.memory);
    }

    pub fn checkBounds(self: *const ZeroTrustSandbox, offset: usize, size: usize) !void {
        const end = std.math.add(usize, offset, size) catch {
            return error.ZeroTrustViolation;
        };
        if (end > self.memory.len) {
            return error.ZeroTrustViolation;
        }
    }

    pub fn storeI32(self: *ZeroTrustSandbox, offset: usize, value: i32) !void {
        try self.checkBounds(offset, 4);
        var bytes: [4]u8 = undefined;
        std.mem.writeInt(i32, &bytes, value, .little);
        @memcpy(self.memory[offset..][0..4], &bytes);
    }

    pub fn loadI32(self: *const ZeroTrustSandbox, offset: usize) !i32 {
        try self.checkBounds(offset, 4);
        const bytes = self.memory[offset..][0..4];
        return std.mem.readInt(i32, bytes[0..4], .little);
    }
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    std.debug.print("--- KorVM Zig Core Verification ---\n", .{});

    var sandbox = try ZeroTrustSandbox.init(allocator, 1);
    defer sandbox.deinit();

    try sandbox.storeI32(0, 1337);
    const val = try sandbox.loadI32(0);
    std.debug.print("[+] Success: Stored and loaded value: {}\n", .{val});

    std.debug.print("\n[*] Testing illegal write at boundary...\n", .{});
    sandbox.storeI32(WASM_PAGE_SIZE - 2, 42) catch |err| {
        std.debug.print("[SUCCESS] Caught violation as expected: {}\n", .{err});
        return;
    };
    std.debug.print("[-] VULNERABILITY: Illegal write allowed!\n", .{});
}
