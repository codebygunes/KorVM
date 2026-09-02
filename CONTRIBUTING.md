# Contributing to KorVM

Thank you for your interest in contributing to KorVM! As a high-performance, zero-trust WebAssembly runtime engineered in Rust, we welcome contributions from systems engineers, security researchers, and the wider open-source community.

To ensure a smooth collaboration and maintain the highest standards of code safety, memory security, and spec-compliance, please follow the guidelines below.

---

## 🛠️ Getting Started
1. **Fork the Repository** and clone it locally.
2. **Set up your environment:** Ensure you have the latest stable Rust toolchain installed.
3. **Create a Branch:** Name your branch descriptively (e.g., `feature/jit-optimization` or `fix/mmap-guard-page`).
4. **Run Tests:** Before opening a Pull Request, ensure all tests pass locally via the unified Makefile:
   `make test`

---

## 📝 Pull Request Guidelines
* **Zero-Panic Policy:** KorVM core engine runs under strict safety margins. Avoid unhandled `unwrap()` or `panic!()` in production pathways; propagate `KorVmError` cleanly.
* **Test Coverage:** Any bug fix or new feature **must** include corresponding unit or integration tests inside the `core_engine/tests/` directory.
* **CI/CD Compliance:** Your PR will automatically trigger the GitHub Actions workflow checking hardware isolation, concurrency safety, and W3C compliance reports. All checks must pass with a green "Success" status.
* **Commit Messages:** Use clear and descriptive commit messages adhering to conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).

---

## 🔒 Security Vulnerabilities
If you discover a security vulnerability or a memory isolation bypass within KorVM, please **do not open a public issue**. Instead, review our `SECURITY.md` guidelines for private disclosure instructions.

---
*Maintained by Elif Nur Ayhan (codebygunes).*