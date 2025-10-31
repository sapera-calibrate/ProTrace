# ProTrace Merkle Tree (Rust)

**BLAKE3-based Merkle tree matching Python functionality**

## Features

- ✅ **BLAKE3 hashing** - Fast cryptographic hashing (same as Python)
- ✅ **Balanced binary tree** - Optimal proof size O(log n)
- ✅ **Proof generation** - Efficient O(log n) proof generation
- ✅ **Proof verification** - Fast O(log n) verification
- ✅ **Append-only** - Add leaves incrementally

## Algorithm (Matches Python Implementation)

```
Leaf = BLAKE3(DNA_hex || pointer || platform_id || timestamp)
Parent = BLAKE3(left_hash || right_hash)
Root = Final hash at tree top
```

## Installation

```toml
[dependencies]
protrace-merkle = "1.0"
```

## Usage

### Basic Example

```rust
use protrace_merkle::MerkleTree;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create tree
    let mut tree = MerkleTree::new();
    
    // Add leaves (DNA registrations)
    tree.add_leaf(
        "abc123...",           // DNA hash (64 hex chars)
        "ipfs://Qm...",        // IPFS pointer
        "platform_1",          // Platform ID
        1234567890             // Timestamp
    );
    
    tree.add_leaf(
        "def456...",
        "ipfs://Qm...",
        "platform_2",
        1234567891
    );
    
    // Build tree
    let root = tree.build_tree()?;
    println!("Merkle root: {}", root);
    
    // Generate proof for leaf 0
    let proof = tree.get_proof(0)?;
    println!("Proof size: {} elements", proof.len());
    
    // Verify proof
    let is_valid = tree.verify_proof(0, &proof, &root)?;
    println!("Proof valid: {}", is_valid);
    
    Ok(())
}
```

### Standalone Functions

```rust
use protrace_merkle::{compute_leaf_hash, verify_proof_standalone};

// Compute leaf hash without tree
let leaf_hash = compute_leaf_hash(
    "abc123...",
    "ipfs://Qm...",
    "platform_1",
    1234567890
);

// Verify proof without tree object
let is_valid = verify_proof_standalone(
    "abc123...",
    "ipfs://Qm...",
    "platform_1",
    1234567890,
    &proof,
    &root_hash
)?;
```

## API Reference

### MerkleTree

```rust
impl MerkleTree {
    // Create new tree
    pub fn new() -> Self
    
    // Add leaf to tree
    pub fn add_leaf(&mut self, dna_hex: &str, pointer: &str, platform_id: &str, timestamp: u64)
    
    // Build tree and get root
    pub fn build_tree(&mut self) -> MerkleResult<String>
    
    // Get root hash
    pub fn get_root(&self) -> MerkleResult<String>
    
    // Generate proof
    pub fn get_proof(&self, index: usize) -> MerkleResult<Vec<ProofElement>>
    
    // Verify proof
    pub fn verify_proof(&self, index: usize, proof: &[ProofElement], root_hash: &str) -> MerkleResult<bool>
    
    // Get leaf count
    pub fn leaf_count(&self) -> usize
}
```

### ProofElement

```rust
pub struct ProofElement {
    pub hash: String,      // Sibling hash (hex)
    pub position: String,  // "left" or "right"
}
```

## Performance

- **Build time**: ~1-5ms for 1000 leaves
- **Proof generation**: ~10μs (O(log n))
- **Verification**: ~10μs (O(log n))
- **Memory**: ~64 bytes per leaf

## Comparison with Python

| Feature | Python | Rust | Speedup |
|---------|--------|------|---------|
| Build (1000 leaves) | ~50ms | ~2ms | 25x |
| Proof generation | ~100μs | ~10μs | 10x |
| Verification | ~100μs | ~10μs | 10x |
| Hash function | BLAKE3/SHA256 | BLAKE3 | Same |

## Examples

See `examples/` directory for more examples:

- `basic.rs` - Basic tree construction
- `batch.rs` - Batch processing
- `verify.rs` - Proof verification

## Testing

```bash
cargo test
cargo test --release
```

## Benchmarks

```bash
cargo bench
```

## License

MIT
