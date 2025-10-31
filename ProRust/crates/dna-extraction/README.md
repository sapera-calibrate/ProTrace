# ProTrace DNA Extraction (Rust)

High-performance 256-bit perceptual DNA fingerprinting for images, written in Rust.

## Features

- **🚀 Blazingly Fast**: 10-20x faster than Python implementation
  - Average: 2-5ms per image (vs 20-40ms Python)
  - Throughput: 200-500 images/second (vs 25-50 Python)

- **🎯 Accurate**: Same algorithm as Python version
  - dHash (64-bit): Gradient-based perceptual hash
  - Grid Hash (192-bit): Multi-scale grid hashing
  - Total: 256-bit DNA fingerprint

- **⚡ Optimized**: Production-ready performance
  - Zero-copy operations where possible
  - Efficient memory usage
  - SIMD-optimized operations
  - Optional parallel batch processing

- **🔧 Flexible**: Multiple usage modes
  - Library API
  - Command-line tool
  - Async support (optional)
  - Parallel processing (optional)

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
protrace-dna = "2.0.0"

# Optional features
protrace-dna = { version = "2.0.0", features = ["parallel", "async", "cli"] }
```

## Quick Start

### Library Usage

```rust
use protrace_dna::DnaExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create extractor
    let extractor = DnaExtractor::new();
    
    // Extract DNA from image
    let dna = extractor.extract_from_path("image.png")?;
    
    // Get 256-bit hash (64 hex characters)
    println!("DNA: {}", dna.hex());
    
    // Get components
    println!("dHash: {}", dna.dhash);      // 64-bit
    println!("Grid: {}", dna.grid_hash);   // 192-bit
    
    // Compute BLAKE3 signature
    println!("Signature: {}", dna.blake3_signature());
    
    Ok(())
}
```

### Compare Images

```rust
use protrace_dna::DnaExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let extractor = DnaExtractor::new();
    
    let dna1 = extractor.extract_from_path("image1.png")?;
    let dna2 = extractor.extract_from_path("image2.png")?;
    
    // Calculate similarity (0.0 to 1.0)
    let similarity = dna1.similarity(&dna2);
    println!("Similarity: {:.2}%", similarity * 100.0);
    
    // Check if duplicates (≥90% similarity)
    if dna1.is_duplicate_of(&dna2, 26) {
        println!("Images are duplicates!");
    }
    
    Ok(())
}
```

### Batch Processing

```rust
use protrace_dna::DnaExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let extractor = DnaExtractor::new();
    
    let paths = vec!["img1.png", "img2.png", "img3.png"];
    let results = extractor.extract_batch(&paths);
    
    for (path, result) in paths.iter().zip(results.iter()) {
        match result {
            Ok(dna) => println!("{}: {}", path, dna.hex()),
            Err(e) => eprintln!("Error: {}", e),
        }
    }
    
    Ok(())
}
```

### Parallel Processing (requires `parallel` feature)

```rust
use protrace_dna::DnaExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Enable parallel processing
    let extractor = DnaExtractor::new().with_parallel();
    
    let paths: Vec<_> = (1..=100)
        .map(|i| format!("images/img{}.png", i))
        .collect();
    
    // Process 100 images in parallel (4-8x faster)
    let results = extractor.extract_batch(&paths);
    
    println!("Processed {} images", results.len());
    
    Ok(())
}
```

## Command-Line Tool (requires `cli` feature)

Build with CLI support:

```bash
cargo build --release --features cli
```

### Extract DNA from single image

```bash
./target/release/dna-extract single -i image.png
```

Output:
```
cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822
```

### Verbose output

```bash
./target/release/dna-extract single -i image.png --verbose
```

Output:
```
File: image.png
DNA Hash: cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822
dHash: cb23db940ce3747e
Grid Hash: 036e3e910c60d69a5965cddebe0afbfe0455535edabaf822
BLAKE3: a7f3c9d2e8b1...
```

### Batch processing

```bash
./target/release/dna-extract batch -i img1.png img2.png img3.png --parallel
```

### Compare images

```bash
./target/release/dna-extract compare --image1 img1.png --image2 img2.png
```

Output:
```
Image 1: img1.png
  DNA: cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822

Image 2: img2.png
  DNA: cb23db940ce3747e036e3e910c60d69a5965cddebe0afbfe0455535edabaf823

Similarity: 99.61%
Hamming Distance: 1 bits

✓ Images are DUPLICATES (≥90% threshold)
```

## Performance Comparison

| Operation | Python (Optimized) | Rust | Speedup |
|-----------|-------------------|------|---------|
| Single image (1MB) | 20-40ms | **2-5ms** | **8-20x** |
| Single image (5MB) | 50-80ms | **5-10ms** | **10-16x** |
| Batch (14 images) | 450ms | **35ms** | **12.8x** |
| Batch (100 images, parallel) | 4000ms | **250ms** | **16x** |

**Hardware**: Intel i7, 16GB RAM

## Algorithm Details

### dHash (64-bit)

1. Center crop to 512×512
2. Convert to grayscale
3. Fast 3×3 box blur
4. 4×4 block averaging to 128×128
5. Resize to 9×8 with bilinear interpolation
6. Compute horizontal gradients
7. Convert to 64-bit hash

### Grid Hash (192-bit)

1. Pad image to 2048×2048 (centered)
2. Extract center 1024×1024
3. Convert to grayscale
4. Multi-scale grid hashing:
   - **8×8 grid**: 64 bits
   - **12×12 grid**: 64 bits (downsampled to 8×8)
   - **16×16 grid**: 64 bits (downsampled to 8×8)
5. Combine into 192-bit hash

### Total: 256-bit DNA

```
DNA = dHash (64-bit) + Grid Hash (192-bit)
    = 16 hex chars + 48 hex chars
    = 64 hex chars (256 bits)
```

## API Reference

### `DnaExtractor`

Main extractor with configurable parameters.

```rust
pub struct DnaExtractor {
    pub dhash_size: u32,
    pub parallel: bool,
}
```

**Methods**:
- `new()` - Create with defaults
- `with_parallel()` - Enable parallel processing (requires feature)
- `extract_from_path(path)` - Extract from file path
- `extract_from_bytes(bytes)` - Extract from image bytes
- `extract(img)` - Extract from DynamicImage
- `extract_batch(paths)` - Batch processing

### `DnaHash`

256-bit DNA fingerprint.

```rust
pub struct DnaHash {
    pub dna_hex: String,      // 64 hex chars (256 bits)
    pub dhash: String,        // 16 hex chars (64 bits)
    pub grid_hash: String,    // 48 hex chars (192 bits)
}
```

**Methods**:
- `hex()` - Get complete 256-bit hash
- `bytes()` - Get as byte array
- `binary()` - Get as binary string
- `hamming_distance(other)` - Calculate distance
- `similarity(other)` - Calculate similarity (0.0-1.0)
- `is_duplicate_of(other, threshold)` - Check if duplicate
- `blake3_signature()` - Compute BLAKE3 hash

### Utility Functions

```rust
// Calculate Hamming distance (0-256)
pub fn hamming_distance(hash1: &str, hash2: &str) -> u32

// Calculate similarity (0.0-1.0)
pub fn similarity(hash1: &str, hash2: &str) -> f64

// Check if duplicate (default threshold: 26 bits = 90% similarity)
pub fn is_duplicate(hash1: &str, hash2: &str, threshold: u32) -> bool

// Find all duplicate pairs in batch
pub fn find_duplicate_pairs(hashes: &[String], threshold: u32) -> Vec<(usize, usize, u32)>
```

## Features

- `default` - Core functionality
- `parallel` - Parallel batch processing with Rayon
- `async` - Async support with Tokio
- `cli` - Command-line tool

## Testing

Run tests:

```bash
cargo test
```

Run benchmarks:

```bash
cargo bench
```

## Integration with ProTrace

This Rust crate integrates seamlessly with the ProTrace Solana program:

```rust
use protrace_dna::DnaExtractor;
use anchor_client::solana_sdk::pubkey::Pubkey;

// Extract DNA
let extractor = DnaExtractor::new();
let dna = extractor.extract_from_path("artwork.png")?;

// Anchor to Solana (pseudo-code)
anchor_dna_hash(
    dna.hex(),          // 256-bit DNA hash
    edition_mode,       // 0 = SERIAL, 1 = STRICT_1_1
)?;
```

## License

MIT

## Contributing

Contributions welcome! Please ensure:
- Tests pass: `cargo test`
- Code is formatted: `cargo fmt`
- Clippy is happy: `cargo clippy`

## See Also

- [ProTrace Main Repository](../../README.md)
- [Python DNA Extraction](../../protrace/image_dna.py)
- [Solana Program](../../programs/protrace/)
