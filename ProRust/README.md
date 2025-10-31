# ProTRACE Rust Implementation

**High-Performance DNA Fingerprinting & Solana Program**

---

## 📚 Overview

The ProTRACE Rust implementation provides:

- **Solana Program**: On-chain DNA storage and verification
- **DNA Extraction Crate**: 20-50x faster than Python
- **Merkle Tree Crate**: Efficient proof generation and verification
- **Client SDK**: Interact with Solana program

---

## 🚀 Quick Start

### Solana Program

```bash
# Install Rust and Anchor
rustup install 1.82.0
rustup default 1.82.0
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest

# Build program
anchor build

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

### DNA Extraction Crate

```bash
cd crates/dna-extraction
cargo build --release

# Run example
cargo run --example basic image.png
```

### Merkle Tree Crate

```bash
cd crates/merkle-tree
cargo build --release

# Run example
cargo run --example basic
```

---

## 📦 Crates

### 1. Solana Program

**Location:** `programs/protrace/`

#### Features

- **8 On-Chain Instructions**
- **BLAKE3 hashing** for Merkle verification
- **security.txt** embedded for researcher contact
- **Edition management** for NFT collections
- **Oracle pattern** for off-chain computation

#### Instructions

```rust
// 1. Store DNA hash on-chain
pub fn anchor_dna_hash(
    ctx: Context<AnchorDnaHash>,
    dna_hash: String,
    edition_mode: u8,
) -> Result<()>

// 2. Oracle-signed Merkle root anchoring
pub fn anchor_merkle_root_oracle(
    ctx: Context<AnchorMerkleRootOracle>,
    merkle_root: [u8; 32],
    manifest_cid: String,
    asset_count: u64,
    timestamp: i64,
) -> Result<()>

// 3. Batch register NFT editions
pub fn batch_register_editions(
    ctx: Context<BatchRegisterEditions>,
    edition_numbers: Vec<u64>,
    dna_hashes: Vec<String>,
) -> Result<()>

// 4-8. Additional instructions (see IDL)
```

#### Building

```bash
# Clean build
rm -rf target/ .anchor/

# Build
anchor build

# Test
anchor test

# Deploy
anchor deploy --provider.cluster devnet
```

#### Program ID

```
Devnet: 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG
```

---

### 2. DNA Extraction Crate

**Location:** `crates/dna-extraction/`

#### Features

- **256-bit DNA fingerprinting** (dHash + Grid Hash)
- **20-50x faster** than Python implementation
- **Parallel processing** (with `parallel` feature)
- **Compatible output** with Python version

#### Usage

```rust
use protrace_dna::DnaExtractor;

// Create extractor
let extractor = DnaExtractor::new();

// Extract DNA from path
let dna = extractor.extract_from_path("image.png")?;

// Access components
println!("DNA: {}", dna.hex());           // Full 256-bit
println!("dHash: {}", dna.dhash);          // 64-bit gradient
println!("Grid: {}", dna.grid_hash);       // 192-bit structure

// Calculate similarity
let dna2 = extractor.extract_from_path("image2.png")?;
let similarity = dna.similarity(&dna2);
println!("Similarity: {:.2%}", similarity);

// Check if duplicate
let is_dup = dna.is_duplicate_of(&dna2, 26);  // 90% threshold
println!("Duplicate: {}", is_dup);
```

#### Features

```toml
[dependencies]
protrace-dna = { version = "1.0", features = ["parallel"] }
```

- `parallel`: Enable parallel grid processing (40-50% faster)

#### Performance

```
Average:    2-5ms per image
Throughput: 200-500 images/second
Speedup:    20-50x vs Python baseline
```

#### Building

```bash
# Build release
cargo build --release

# Run tests
cargo test

# Run benchmarks
cargo bench

# Run example
cargo run --example basic image.png
```

---

### 3. Merkle Tree Crate

**Location:** `crates/merkle-tree/`

#### Features

- **BLAKE3 hashing** - Fast cryptographic hash
- **Balanced binary tree** - Optimal O(log n) proofs
- **Proof generation** - 10x faster than Python
- **Proof verification** - O(log n) complexity
- **Compatible format** with Python version

#### Usage

```rust
use protrace_merkle::MerkleTree;

// Create tree
let mut tree = MerkleTree::new();

// Add leaves
tree.add_leaf("abc123...", "ipfs://Qm...", "platform", 1234567890);
tree.add_leaf("def456...", "ipfs://Qm...", "platform", 1234567891);
tree.add_leaf("ghi789...", "ipfs://Qm...", "platform", 1234567892);

// Build tree
let root = tree.build_tree()?;
println!("Root: {}", root);

// Generate proof
let proof = tree.get_proof(0)?;
println!("Proof elements: {}", proof.len());

// Verify proof
let is_valid = tree.verify_proof(0, &proof, &root)?;
println!("Valid: {}", is_valid);
```

#### Standalone Functions

```rust
use protrace_merkle::{compute_leaf_hash, verify_proof_standalone};

// Compute leaf hash without tree
let leaf_hash = compute_leaf_hash(
    "abc123...",
    "ipfs://Qm...",
    "platform",
    1234567890
);

// Verify proof without tree object
let is_valid = verify_proof_standalone(
    "abc123...",
    "ipfs://Qm...",
    "platform",
    1234567890,
    &proof,
    &root_hash
)?;
```

#### Performance

```
Build (1000):  ~2ms
Proof Gen:     ~10μs
Verification:  ~10μs
Speedup:       10-25x vs Python
```

#### Building

```bash
# Build release
cargo build --release

# Run tests
cargo test

# Run benchmarks
cargo bench

# Run example
cargo run --example basic
```

---

### 4. Client SDK

**Location:** `crates/client/`

#### Features

- **Solana program interaction**
- **Transaction building**
- **Account management**

#### Usage

```rust
use protrace_client::ProTraceClient;
use solana_sdk::signature::Keypair;

// Create client
let keypair = Keypair::new();
let client = ProTraceClient::new(
    "https://api.devnet.solana.com",
    keypair
);

// Anchor DNA hash
let signature = client.anchor_dna_hash(
    "abc123...",
    0  // edition_mode
).await?;

println!("Transaction: {}", signature);
```

---

## 🔧 Development

### Prerequisites

```bash
# Rust toolchain
rustup install 1.82.0
rustup default 1.82.0

# Anchor CLI
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
avm install latest
avm use latest

# Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

### Project Structure

```
ProRust/
├── programs/
│   └── protrace/              # Solana program
│       ├── src/
│       │   └── lib.rs         # Program logic
│       └── Cargo.toml
│
├── crates/
│   ├── dna-extraction/        # DNA crate
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── dhash.rs
│   │   │   ├── grid.rs
│   │   │   └── utils.rs
│   │   ├── examples/
│   │   └── benches/
│   │
│   ├── merkle-tree/           # Merkle crate
│   │   ├── src/
│   │   │   └── lib.rs
│   │   ├── examples/
│   │   └── benches/
│   │
│   └── client/                # Client SDK
│       └── src/
│           └── main.rs
│
├── Anchor.toml                # Anchor configuration
└── Cargo.toml                 # Workspace configuration
```

### Building Workspace

```bash
# Build all crates
cargo build --workspace --release

# Test all crates
cargo test --workspace

# Run all benchmarks
cargo bench --workspace
```

---

## 📊 Benchmarks

### DNA Extraction

```
Test name              Time
---------------------------------
extract_10_images      ~20ms    (2ms each)
extract_100_images     ~200ms   (2ms each)
extract_parallel       ~100ms   (0.5ms each with 4 cores)
```

### Merkle Trees

```
Test name              Time
---------------------------------
build_10_leaves        ~500μs
build_100_leaves       ~2ms
build_1000_leaves      ~20ms
proof_generation       ~10μs
proof_verification     ~10μs
```

---

## 🧪 Testing

### Unit Tests

```bash
# Test specific crate
cd crates/dna-extraction
cargo test

# Test with output
cargo test -- --nocapture

# Test specific function
cargo test test_dna_extraction
```

### Integration Tests

```bash
# Solana program tests
cd programs/protrace
anchor test
```

### Benchmarks

```bash
# Run benchmarks
cargo bench

# Benchmark specific crate
cd crates/dna-extraction
cargo bench
```

---

## 🔒 Security

### security.txt

Query embedded security information:

```bash
cargo install query-security-txt
query-security-txt 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG --url devnet
```

### Security Policy

See [SECURITY.md](../SECURITY.md) for vulnerability reporting.

---

## 📖 API Documentation

Generate and view documentation:

```bash
# Generate docs
cargo doc --no-deps --open

# Specific crate docs
cd crates/dna-extraction
cargo doc --open
```

---

## 🤝 Contributing

See main [README](../README.md) for contribution guidelines.

---

## 📜 License

MIT License - see [LICENSE](../LICENSE) for details.

---

**For full documentation, see the [main README](../README.md)**
