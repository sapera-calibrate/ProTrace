# ProTrace Rust - Architecture

Technical architecture and design decisions.

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  (protrace-cli - User Interface & Command Routing)          │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌──────────────┐
│ Wallet  │     │  Blockchain  │
│ Manager │────▶│   Client     │
└─────────┘     └──────┬───────┘
                       │
                       ▼
                ┌─────────────┐
                │   Solana    │
                │   Devnet    │
                └─────────────┘

    │
    ▼
┌──────────────┐      ┌──────────────┐
│  Image DNA   │      │ Merkle Tree  │
│   Engine     │─────▶│   Manager    │
└──────────────┘      └──────────────┘
```

## 📦 Crate Structure

### protrace-image-dna

**Purpose**: Perceptual image fingerprinting

**Key Components**:
- `compute_dna()` - Main DNA computation
- `compute_dhash_legacy()` - 64-bit gradient hash
- `compute_grid_hash()` - 192-bit grid hash
- `hamming_distance()` - Similarity calculation
- `is_duplicate()` - Duplicate detection

**Algorithm**: dHash + Grid (256-bit)
- dHash: 64-bit perceptual hash using horizontal gradients
- Grid: 192-bit multi-scale grid hash (8×8, 12×12, 16×16)

**Dependencies**:
- `image` - Image loading and manipulation
- `imageproc` - Image processing (Gaussian blur)
- `blake3` - Cryptographic hashing
- `serde` - Serialization

### protrace-merkle-tree

**Purpose**: Tamper-proof commitment trees

**Key Components**:
- `MerkleTree` - Binary tree implementation
- `add_leaf()` - Add registration
- `build_tree()` - Construct tree
- `get_proof()` - Generate proof
- `verify_proof()` - Verify proof
- `export_manifest()` - IPFS-ready export

**Algorithm**: Balanced binary tree with BLAKE3
- Leaf = BLAKE3(DNA || pointer || platform || timestamp)
- Internal = BLAKE3(left_hash || right_hash)
- Proof generation: O(log n)
- Proof verification: O(log n)

**Dependencies**:
- `blake3` - Cryptographic hashing
- `serde` - Serialization
- `chrono` - Timestamps

### protrace-blockchain

**Purpose**: Solana blockchain integration

**Key Components**:
- `ProTraceClient` - Blockchain client
- `initialize_merkle_root()` - Initialize on-chain
- `update_merkle_root()` - Update root
- `anchor_merkle_root_oracle()` - Oracle anchoring
- `batch_register_editions()` - Batch operations

**Program Integration**:
- Program ID: `Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS`
- PDAs for deterministic accounts
- Oracle pattern for authorized updates

**Dependencies**:
- `solana-sdk` - Solana core
- `solana-client` - RPC client
- `anchor-lang` - Anchor framework
- `anchor-client` - Client SDK

### protrace-wallet

**Purpose**: Keypair and wallet management

**Key Components**:
- `WalletManager` - Wallet operations
- `load_keypair_from_file()` - Load from JSON
- `save_keypair_to_file()` - Save to JSON
- `from_base58()` - Import from base58
- `to_json()` - Export to JSON

**Supported Formats**:
- JSON array (Solana standard)
- Base58 private key
- Raw bytes (64 bytes)

**Dependencies**:
- `solana-sdk` - Keypair types
- `bs58` - Base58 encoding
- `serde` - Serialization

### protrace-cli

**Purpose**: Command-line interface

**Commands**:
- `wallet` - Wallet operations
- `dna` - DNA computation
- `merkle` - Merkle tree operations
- `blockchain` - Blockchain operations
- `test` - End-to-end testing

**Features**:
- Colored output
- Progress bars
- Error handling
- Verbose logging

**Dependencies**:
- All ProTrace crates
- `clap` - CLI parsing
- `colored` - Terminal colors
- `indicatif` - Progress bars

## 🔄 Data Flow

### Image Registration Flow

```
1. Image File
   ↓
2. DNA Computation (256-bit hash)
   ↓
3. Add to Merkle Tree
   ↓
4. Build Tree (compute root)
   ↓
5. Export Manifest (IPFS)
   ↓
6. Anchor to Blockchain
   ↓
7. On-chain commitment
```

### Verification Flow

```
1. Query image
   ↓
2. Compute DNA
   ↓
3. Check Merkle tree
   ↓
4. Generate proof
   ↓
5. Verify on-chain
   ↓
6. Result: Valid/Invalid
```

## 🔐 Security Model

### Trust Assumptions

1. **Oracle Authority**: Trusted to anchor legitimate roots
2. **IPFS Storage**: Tamper-evident (content-addressed)
3. **Blockchain**: Solana's BFT consensus
4. **Cryptography**: BLAKE3 collision resistance

### Attack Vectors

| Attack | Mitigation |
|--------|------------|
| Duplicate registration | DNA similarity check (>90%) |
| False proof | Merkle proof verification |
| Unauthorized anchor | Oracle signature check |
| IPFS tampering | Content-addressed hashes |
| Timestamp manipulation | Block timestamp validation |

### Cryptographic Primitives

- **BLAKE3**: Merkle tree hashing (faster than SHA-256)
- **Ed25519**: Wallet signatures (Solana standard)
- **Perceptual Hash**: dHash + Grid (collision-resistant)

## ⚡ Performance

### Benchmarks (indicative)

| Operation | Time | Throughput |
|-----------|------|------------|
| DNA Compute | 50ms | 20 images/sec |
| Merkle Build (1K) | 5ms | 200K leaves/sec |
| Proof Gen | 1ms | 1K proofs/sec |
| Blockchain Anchor | 2s | Network-bound |

### Optimization Strategies

1. **Parallel Processing**: Rayon for batch DNA
2. **Memory Pooling**: Reuse image buffers
3. **Lazy Evaluation**: Build tree on-demand
4. **Caching**: Cache DNA results
5. **Async I/O**: Tokio for network

## 🧩 Design Patterns

### Repository Pattern

```rust
pub struct MerkleTree {
    leaves: Vec<Vec<u8>>,      // Data store
    root: Option<MerkleNode>,   // Computed state
    leaf_map: HashMap<...>,     // Index
}
```

### Builder Pattern

```rust
let client = ProTraceClient::new_devnet(keypair)?
    .with_commitment(CommitmentConfig::confirmed())
    .build()?;
```

### Error Handling

```rust
#[derive(Error, Debug)]
pub enum DnaError {
    #[error("Failed to load image: {0}")]
    ImageLoadError(#[from] image::ImageError),
    // ...
}
```

## 🔌 Extension Points

### Adding New Hash Algorithms

Implement in `protrace-image-dna`:
```rust
pub fn compute_custom_hash(img: &DynamicImage) -> HashResult {
    // Your algorithm here
}
```

### Custom Blockchain Networks

Extend `ProTraceClient`:
```rust
impl ProTraceClient {
    pub fn new_mainnet(keypair: Keypair) -> Result<Self> {
        Self::new(Cluster::Mainnet, keypair, PROGRAM_ID)
    }
}
```

### Additional Commands

Add to `protrace-cli/src/commands/`:
```rust
pub async fn handle_custom_command(...) -> Result<()> {
    // Implementation
}
```

## 📊 State Management

### Merkle Tree State

```
Empty → Adding Leaves → Built → Verified
  │         │              │        │
  └─────────┴──────────────┴────────┘
            Rebuild on mutation
```

### Blockchain State

```
Uninitialized → Initialized → Updated
       │            │            │
       └────────────┴────────────┘
              Oracle-controlled
```

## 🔄 Async Architecture

### Tokio Runtime

```rust
#[tokio::main]
async fn main() -> Result<()> {
    // Async blockchain operations
    let client = ProTraceClient::new_devnet(keypair)?;
    let signature = client.anchor_merkle_root(...).await?;
    Ok(())
}
```

### Concurrency Model

- **Blockchain**: Async I/O (network)
- **DNA Computation**: Sync (CPU-bound)
- **Batch Processing**: Parallel (Rayon)

## 📝 Code Organization

```
protrace-rust/
├── crates/
│   ├── image-dna/       # Pure functions, no I/O
│   ├── merkle-tree/     # Pure data structures
│   ├── blockchain/      # Async I/O, network
│   ├── wallet/          # File I/O, crypto
│   └── cli/             # User interface
├── tests/               # Integration tests
├── examples/            # Usage examples
└── scripts/             # Automation
```

## 🎯 Design Principles

1. **Separation of Concerns**: Each crate has single responsibility
2. **Type Safety**: Leverage Rust's type system
3. **Error Handling**: Explicit Result types
4. **Testability**: Pure functions, dependency injection
5. **Performance**: Zero-cost abstractions
6. **Security**: Memory safety, no undefined behavior

## 🚀 Future Enhancements

- [ ] Parallel DNA computation with Rayon
- [ ] WebAssembly support (browser/mobile)
- [ ] REST API server
- [ ] GraphQL interface
- [ ] Database backend (PostgreSQL + pgvector)
- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Hardware wallet integration
- [ ] Encrypted backups

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2025-10-20
