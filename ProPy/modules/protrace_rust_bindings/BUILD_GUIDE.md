# ProTrace Rust - Build Guide

Complete guide for building and testing ProTrace Rust implementation.

## 🏗️ Build Instructions

### Prerequisites Check

```bash
# Verify Rust installation
rustc --version  # Should be 1.70+
cargo --version

# Verify Solana CLI
solana --version  # Should be 1.17+

# Optional: Anchor
anchor --version  # Should be 0.29.0
```

### Build All Crates

```bash
cd protrace-rust

# Development build (faster, with debug info)
cargo build

# Release build (optimized, production-ready)
cargo build --release

# Build specific crate
cargo build -p protrace-image-dna
cargo build -p protrace-merkle-tree
cargo build -p protrace-blockchain
cargo build -p protrace-wallet
cargo build -p protrace-cli
```

### Build Times

| Build Type | First Build | Incremental |
|------------|-------------|-------------|
| Debug      | ~5 min      | ~30 sec     |
| Release    | ~10 min     | ~1 min      |

## 🧪 Testing

### Unit Tests

```bash
# All tests
cargo test --workspace

# Specific crate
cargo test -p protrace-image-dna
cargo test -p protrace-merkle-tree
cargo test -p protrace-wallet

# With output
cargo test -- --nocapture

# Specific test
cargo test test_merkle_tree_basic
```

### Integration Tests

```bash
# Run integration tests
cargo test --test integration_test

# With verbose output
cargo test --test integration_test -- --nocapture --test-threads=1
```

### Example Programs

```bash
# Run basic usage example
cargo run --example basic_usage

# Run with release mode
cargo run --release --example basic_usage
```

## 📦 Installation

### Install CLI Tool

```bash
# Install from local source
cargo install --path crates/cli

# Verify installation
protrace --version
which protrace

# Update
cargo install --path crates/cli --force
```

### System-Wide Installation

**Linux/macOS:**
```bash
cargo install --path crates/cli
# Binary installed to ~/.cargo/bin/protrace
```

**Windows:**
```powershell
cargo install --path crates/cli
# Binary installed to %USERPROFILE%\.cargo\bin\protrace.exe
```

## 🔍 Code Quality

### Format Code

```bash
# Check formatting
cargo fmt --all -- --check

# Apply formatting
cargo fmt --all
```

### Linting

```bash
# Run Clippy linter
cargo clippy --workspace --all-targets

# Fix automatically
cargo clippy --workspace --all-targets --fix
```

### Documentation

```bash
# Build documentation
cargo doc --workspace --no-deps

# Open in browser
cargo doc --workspace --no-deps --open

# Private items too
cargo doc --workspace --no-deps --document-private-items
```

## 🐛 Debugging

### Enable Debug Logging

```bash
# Set log level
export RUST_LOG=debug
protrace test images/*.png

# Specific module
export RUST_LOG=protrace_blockchain=debug
```

### Backtrace on Panic

```bash
export RUST_BACKTRACE=1
protrace test images/*.png

# Full backtrace
export RUST_BACKTRACE=full
```

### Debug Build

```bash
# Build with debug symbols
cargo build

# Run with debugger (lldb/gdb)
rust-gdb target/debug/protrace
# or
rust-lldb target/debug/protrace
```

## ⚡ Performance

### Benchmarks

```bash
# Run benchmarks (if implemented)
cargo bench

# Specific benchmark
cargo bench dna_computation
```

### Profile Build

```bash
# Build with profiling enabled
cargo build --release --profile release-with-debug

# Use with profiler
perf record target/release/protrace test images/*.png
perf report
```

### Optimization Levels

Edit `Cargo.toml`:
```toml
[profile.release]
opt-level = 3        # Maximum optimization
lto = true          # Link-time optimization
codegen-units = 1   # Better optimization, slower compile
strip = true        # Remove debug symbols
```

## 🔧 Troubleshooting

### Build Failures

**Issue: Linker errors**
```bash
# Clean and rebuild
cargo clean
cargo build --release
```

**Issue: Out of memory**
```bash
# Reduce parallel jobs
cargo build --release -j 2
```

**Issue: Dependency conflicts**
```bash
# Update dependencies
cargo update

# Force update specific dependency
cargo update -p solana-sdk
```

### Runtime Issues

**Issue: Shared library errors (Linux)**
```bash
# Install OpenSSL dev
sudo apt-get install libssl-dev pkg-config

# Install other dependencies
sudo apt-get install build-essential
```

**Issue: Permission denied (Unix)**
```bash
chmod +x ~/.cargo/bin/protrace
```

### Solana Connection Issues

**Issue: Connection timeout**
```bash
# Check devnet status
solana cluster-version --url devnet

# Try alternative RPC
export SOLANA_RPC_URL=https://api.devnet.solana.com
```

## 📊 Build Artifacts

### Directory Structure

```
target/
├── debug/              # Debug build artifacts
│   ├── protrace       # CLI binary (debug)
│   └── deps/          # Dependencies
├── release/           # Release build artifacts
│   ├── protrace       # CLI binary (optimized)
│   └── deps/
└── doc/               # Generated documentation
    └── protrace_*/
```

### Binary Sizes

| Build Type | Size (approx) |
|------------|---------------|
| Debug      | ~50 MB        |
| Release    | ~15 MB        |
| Strip      | ~10 MB        |

### Reduce Binary Size

```toml
# In Cargo.toml
[profile.release]
strip = true
lto = true
opt-level = "z"  # Optimize for size
```

## 🚀 Deployment

### Cross-Compilation

**Linux → Windows:**
```bash
rustup target add x86_64-pc-windows-gnu
cargo build --release --target x86_64-pc-windows-gnu
```

**macOS → Linux:**
```bash
rustup target add x86_64-unknown-linux-gnu
cargo build --release --target x86_64-unknown-linux-gnu
```

### Docker Build

```dockerfile
FROM rust:1.75 as builder
WORKDIR /usr/src/protrace
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /usr/src/protrace/target/release/protrace /usr/local/bin/
CMD ["protrace"]
```

Build:
```bash
docker build -t protrace-rust .
docker run -it protrace-rust protrace --help
```

## 📝 Development Workflow

### Recommended Workflow

```bash
# 1. Make changes
vim crates/image-dna/src/lib.rs

# 2. Check compilation
cargo check

# 3. Run tests
cargo test -p protrace-image-dna

# 4. Format and lint
cargo fmt
cargo clippy

# 5. Build release
cargo build --release

# 6. Test CLI
cargo run --release --bin protrace -- --help
```

### Pre-commit Checks

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Format check
cargo fmt --all -- --check

# Linting
cargo clippy --workspace --all-targets -- -D warnings

# Tests
cargo test --workspace

echo "All checks passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 🔐 Security

### Dependency Audit

```bash
# Install cargo-audit
cargo install cargo-audit

# Check for vulnerabilities
cargo audit

# Fix vulnerabilities
cargo audit fix
```

### Supply Chain

```bash
# Check dependencies
cargo tree

# Specific dependency
cargo tree -p solana-sdk

# Duplicates
cargo tree -d
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo build --release
      - run: cargo test --workspace
      - run: cargo clippy -- -D warnings
```

## 💡 Tips

1. **Faster Builds**: Use `sccache` or `mold` linker
2. **Disk Space**: Run `cargo clean` periodically
3. **Dependencies**: Keep `Cargo.lock` in git for reproducible builds
4. **Versioning**: Follow semver for releases
5. **Documentation**: Update docs with code changes

## 📚 Resources

- [Rust Book](https://doc.rust-lang.org/book/)
- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Solana Docs](https://docs.solana.com/)
- [Anchor Book](https://www.anchor-lang.com/)

---

**Happy Building! 🦀**
