// demo.rs
// İşletim sistemi veya standart kütüphane kullanmayan saf(pure) mantık.

#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}