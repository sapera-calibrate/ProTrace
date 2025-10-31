# ProTRACE

A digital asset verification system that detects duplicate images using perceptual hashing and cryptographic proofs.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org/)
[![Tests](https://img.shields.io/badge/tests-19%2F19%20passing-success.svg)]()

**Version** 2.0 | **Last Updated** October 30, 2025

---

## Table of Contents

- [What is ProTRACE?](#what-is-protrace)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Details](#technical-details)
- [Architecture](#architecture)
- [Performance](#performance)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Repository Structure](#repository-structure)

---

## What is ProTRACE?

ProTRACE solves a fundamental problem in digital asset management: **detecting when the same image appears multiple times**, even if it has been slightly modified. This is particularly important for NFT platforms, art galleries, and content verification systems.

### The Problem

Imagine you run an NFT marketplace. An artist uploads an image. Later, someone else tries to upload the same image with minor changes—perhaps slightly brighter, cropped differently, or saved in a different format. Traditional file hashing (like MD5 or SHA-256) would see these as completely different files because even a single pixel change produces a completely different hash.

### The Solution

ProTRACE uses **perceptual hashing** (we call it "DNA fingerprinting") to create a fingerprint that captures what the image "looks like" rather than its exact pixel values. Two images that look similar to a human will have similar DNA fingerprints, even if their raw pixel data is different.

The system then uses these fingerprints to:
1. Detect if an image is a duplicate of something already registered
2. Store the fingerprints in a tamper-proof Merkle tree
3. Generate cryptographic proofs that an image was registered at a specific time

---

## Key Concepts

### Perceptual Hashing vs Traditional Hashing

Traditional cryptographic hashes (MD5, SHA-256) are designed to produce completely different outputs for even tiny input changes. ProTRACE uses **perceptual hashing**, which produces similar outputs for visually similar images.

```
Traditional Hash (SHA-256):
  image.png        → a1b2c3d4e5f6...
  image_bright.png → 9z8y7x6w5v4u...  (completely different)

Perceptual Hash (ProTRACE DNA):
  image.png        → d7b523525080...
  image_bright.png → d7b523525081...  (1 bit different, 99.6% similar)
```

### DNA Fingerprint Structure

The 256-bit DNA is composed of two complementary algorithms:

**dHash (64 bits)**: Gradient-based hash that captures overall image structure and lighting patterns. Robust to brightness/contrast adjustments, rotation-sensitive.

**Grid Hash (192 bits)**: Multi-scale structural hash analyzing image content at three resolutions (8×8, 12×12, 16×16 grids). Robust to minor crops and noise, scale-sensitive.

### Similarity Threshold Configuration

The default 90% threshold can be adjusted based on use case:

| Threshold | Use Case | False Positive Risk | False Negative Risk |
|-----------|----------|---------------------|---------------------|
| 95-100% | Exact duplicate detection | Low | High |
| 90-95% | Standard NFT verification (default) | Medium | Low |
| 85-90% | Lenient duplicate detection | High | Very low |
| <85% | Similar image clustering | Very high | Minimal |

### Registry Limitations and Considerations

**Performance**: Duplicate detection is O(n) where n = number of registered DNAs. For large registries (>100K entries), consider:
- Index optimization using locality-sensitive hashing (LSH)
- Database-backed storage instead of JSON
- Distributed comparison using parallel processing

**Storage**: Each DNA entry consumes ~239 bytes. Plan storage accordingly:
- 10K images = ~2.4 MB
- 100K images = ~24 MB
- 1M images = ~240 MB

**False Positives**: Images with repetitive patterns (tiles, textures) may generate similar DNAs. Manual review recommended for edge cases.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/sapera-calibrate/ProTRACE.git
cd ProTRACE
pip install -e .
```

Verify installation:
```bash
python -c "import protrace; print('Installation successful')"
```

---

## Usage

### Quick Start Examples

**Extract DNA and compare two images:**
```python
from protrace.image_dna import compute_dna, dna_similarity

dna1 = compute_dna("original.png")['dna_hex']
dna2 = compute_dna("modified.png")['dna_hex']
similarity = dna_similarity(dna1, dna2)

print(f"Similarity: {similarity*100:.2f}%")
print("DUPLICATE" if similarity >= 0.90 else "UNIQUE")
```

**Register image with automatic duplicate detection:**
```python
from protrace.registration.register_image import register_image

result = register_image("artwork.png", "artwork_001", "opensea")
if result['success']:
    print(f"Registered. Root: {result['root_hash'][:16]}...")
else:
    print(f"Duplicate: {result['match']['similarity']:.1f}% similar")
```

**Generate and verify cryptographic proof:**
```python
from protrace.merkle import MerkleTree

tree = MerkleTree()
tree.add_leaf("dna_hash", "img_001", "platform", 1698765432)
root_hash = tree.build_tree()
proof = tree.get_proof(0)
valid = tree.verify_proof(tree.leaves[0], proof, bytes.fromhex(root_hash))
```

### Advanced Usage Patterns

**Batch registration with progress tracking:**
```python
from protrace.registration.batch_register import batch_register
from pathlib import Path

images = list(Path("artwork_folder").glob("*.png"))
results = batch_register(images, platform_id="gallery")

print(f"Registered: {sum(r['success'] for r in results)}/{len(results)}")
print(f"Duplicates found: {sum(r['plagiarized'] for r in results)}")
```

**Custom similarity threshold for specific use case:**
```python
# Stricter threshold for legal evidence
result = register_image("evidence.png", "case_001", "legal", 
                       similarity_threshold=0.95)

# Lenient threshold for similar image clustering
result = register_image("variant.png", "cluster_001", "research",
                       similarity_threshold=0.85)
```

**Cross-chain edition tracking:**
```python
from protrace.edition_core import EditionRegistry, EditionMode

registry = EditionRegistry()
registry.register_edition(
    asset_path="art.png",
    creator="0xArtist...",
    chain="ethereum",
    contract="0x1234...",
    token_id="42",
    edition_no=1,
    edition_mode=EditionMode.SERIAL,
    max_editions=100
)
```

### Command Line Tools

```bash
# Basic DNA extraction
python -c "from protrace.image_dna import compute_dna; \
           print(compute_dna('image.png')['dna_hex'])"

# Register with duplicate detection
python -m protrace.registration.register_image image.png

# Run interactive demonstration
python demo_workflow.py

# Execute test suite
python protrace_test_suite.py
```

---

## Technical Details

### DNA Extraction Algorithm

The DNA extraction process generates a 256-bit perceptual hash from any input image. This hash is designed to be robust to minor image modifications while remaining sensitive to significant content changes.

#### Algorithm Components

**dHash (Difference Hash) - 64 bits**

The dHash component captures gradient information:

1. Center crop image to 512×512 pixels
2. Convert to grayscale using weighted RGB channels
3. Apply separable box blur (kernel size 3×3)
4. Resize to 9×8 using block averaging
5. Compute horizontal gradients by comparing adjacent columns
6. Pack 64 binary values into 8 bytes

Processing time: 18-24ms

**Grid Hash (Multi-scale) - 192 bits**

The Grid Hash analyzes local structure at three scales:

1. Pad image to ensure divisibility
2. Apply uniform filter for noise reduction
3. Divide into three grids:
   - 8×8 grid (64 cells) - coarse structure
   - 12×12 grid (144 cells) - medium structure
   - 16×16 grid (256 cells) - fine structure
4. For each cell, compute mean intensity
5. Compare cell mean against grid median
6. Pack 64 bits from each scale (192 bits total)

Processing time: 22-30ms

**Combined Output**: 256-bit fingerprint (64 hexadecimal characters)

Example:
```
Input:  artwork.png (1920×1080, PNG format)
Output: d7b523525080445e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822
        |------- dHash -------|-------------- Grid Hash --------------|
        64 bits (16 hex)      192 bits (48 hex)
```

#### Optimization Techniques

Seven optimizations were applied to achieve 2.4x speedup over baseline:

1. Separable box blur - Decomposes 2D convolution (50% faster)
2. Fast numpy padding - Native operations vs PIL (80% faster)
3. Direct grayscale - Single-pass weighted sum (50% faster)
4. Strided block averaging - Zero-copy downsampling
5. Scipy zoom resize - Hardware-accelerated interpolation (50% faster)
6. Parallel grid processing - Concurrent scale processing (40-50% faster)
7. Direct bit packing - Vectorized numpy.packbits (80% faster)

### Hamming Distance Calculation

Hamming distance measures bit-level differences between DNA hashes using XOR operations.

**Implementation**:
```python
def hamming_distance(hash1: str, hash2: str) -> int:
    bytes1 = bytes.fromhex(hash1)
    bytes2 = bytes.fromhex(hash2)
    return sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(bytes1, bytes2))

# Optimized version using lookup table (10x faster)
POPCOUNT_TABLE = [bin(i).count('1') for i in range(256)]
def hamming_distance_fast(hash1: str, hash2: str) -> int:
    bytes1 = bytes.fromhex(hash1)
    bytes2 = bytes.fromhex(hash2)
    return sum(POPCOUNT_TABLE[b1 ^ b2] for b1, b2 in zip(bytes1, bytes2))
```

**Computational Complexity**: O(1) - constant time for 256-bit hashes (32 bytes)

### Robustness Analysis

ProTRACE DNA is robust to common image transformations:

| Transformation | Typical Bit Changes | Detected as Duplicate? |
|----------------|---------------------|------------------------|
| Brightness ±10% | 2-5 bits | Yes (98-99% similar) |
| Contrast adjustment | 3-8 bits | Yes (97-99% similar) |
| JPEG compression (Q=90) | 4-10 bits | Yes (96-98% similar) |
| Small crop (<5%) | 5-12 bits | Yes (95-98% similar) |
| Gaussian blur (σ=1) | 8-15 bits | Yes (94-97% similar) |
| Rotation ±5° | 15-30 bits | Maybe (88-94% similar) |
| Significant crop (>20%) | 30-60 bits | No (77-88% similar) |
| Color shift | 10-20 bits | Yes (92-96% similar) |

These values are approximate and depend on image content. Images with high entropy (detailed photos) are more stable than low entropy images (simple graphics).

### Merkle Tree Implementation

ProTRACE uses a binary Merkle tree with BLAKE3 cryptographic hash function.

**Tree Structure**:
```
                    Root (32 bytes)
                    BLAKE3(H_A || H_B)
                    /                \
                   /                  \
              H_A                      H_B
          BLAKE3(H1 || H2)        BLAKE3(H3 || H4)
           /          \             /          \
          /            \           /            \
        H1              H2        H3              H4
     BLAKE3(L1)      BLAKE3(L2) BLAKE3(L3)    BLAKE3(L4)
         |               |          |              |
        L1              L2         L3             L4
     (DNA 1)         (DNA 2)    (DNA 3)        (DNA 4)
```

**Leaf Format**:
```
<dna_hex>|<pointer>|<platform_id>|<timestamp>

Example:
d7b523525080445e036e3e910c60d69a...|IMG_00042|opensea|1698765432
```

**Proof Generation**:

To prove a leaf exists in the tree, provide sibling hashes along the path from leaf to root.

Example proof for L1:
```
Siblings: [H2, H_B]

Verification:
  Step 1: Compute H_A = BLAKE3(BLAKE3(L1) || H2)
  Step 2: Compute Root = BLAKE3(H_A || H_B)
  Step 3: Compare with known root
```

Proof size scales logarithmically: log₂(n) sibling hashes for n leaves.

**Performance Characteristics**:

| Operation | Complexity | Time (1K leaves) | Time (1M leaves) |
|-----------|------------|------------------|------------------|
| Add Leaf | O(1) | 0.007 ms | 0.007 ms |
| Build Tree | O(n) | 7 ms | 7000 ms |
| Generate Proof | O(log n) | 0.7 ms | 1.0 ms |
| Verify Proof | O(log n) | 0.016 ms | 0.016 ms |

**Storage Requirements**:
- Leaf data: ~91 bytes (DNA + metadata)
- BLAKE3 hash: 32 bytes
- Internal nodes: ~116 bytes (amortized)
- Total per DNA: ~239 bytes

Recommended capacity: 100K-1M DNAs per tree. For larger registries, use tree sharding.

### Security Considerations

**Collision Resistance**: With 256 bits of entropy, the probability of accidental collision is approximately 2^-256. For practical purposes, collisions are computationally infeasible.

**Pre-image Resistance**: Given a DNA hash, it is not feasible to reconstruct the original image. The hash is a one-way function capturing visual patterns, not image data.

**Adversarial Robustness**: 
- The system is not designed to resist targeted attacks where an adversary specifically crafts images to produce similar DNA hashes
- For high-security applications, combine DNA fingerprinting with cryptographic hashing (SHA-256) of the original file
- Consider watermarking or additional authentication mechanisms for legal evidence

**Registry Integrity**:
- Merkle tree provides tamper-evidence but not tamper-proof storage
- Root hash should be anchored on blockchain or distributed ledger for immutability
- Periodic audits recommended for large registries

### Integration Patterns

**NFT Minting Pipeline**:
```python
# 1. Pre-mint verification
dna = compute_dna(artwork_file)['dna_hex']
result = register_image(artwork_file, artwork_id, platform)

if not result['success']:
    return {"error": "Duplicate detected", "similarity": result['match']['similarity']}

# 2. Mint NFT on blockchain
nft_tx = mint_nft(metadata, artwork_file)

# 3. Update edition registry
edition_registry.register_edition(
    dna_hash=dna,
    chain=chain_id,
    contract=nft_contract,
    token_id=nft_tx.token_id
)

# 4. Anchor Merkle root on-chain (optional)
anchor_merkle_root(result['root_hash'])
```

**Content Moderation System**:
```python
# Automated flagging system
def check_content(submitted_image):
    dna = compute_dna(submitted_image)['dna_hex']
    
    # Check against known infringing content
    for banned_dna in banned_database:
        if dna_similarity(dna, banned_dna) >= 0.90:
            return {"action": "block", "reason": "copyright_infringement"}
    
    # Check against user-reported content
    for reported_dna in reported_database:
        if dna_similarity(dna, reported_dna) >= 0.95:
            return {"action": "review", "reason": "similar_to_reported"}
    
    return {"action": "allow"}
```

---

## Architecture

The system architecture is designed for modularity and performance. Three primary components work together to provide duplicate detection and cryptographic verification.

```
┌──────────────────────────────────────────────────────────────┐
│                     INPUT: Image File                         │
└──────────────────────────────────┬───────────────────────────┘
                                   │
                                   ▼
          ┌────────────────────────────────────────┐
          │   DNA EXTRACTION MODULE                │
          │   • Load & preprocess image            │
          │   • Compute dHash (64 bits)            │
          │   • Compute Grid Hash (192 bits)       │
          │   • Output: 256-bit fingerprint        │
          └─────────────────┬──────────────────────┘
                            │
                            ▼
                 DNA: [64 hex characters]
                            │
                            ▼
          ┌────────────────────────────────────────┐
          │   DUPLICATE DETECTION MODULE           │
          │   • Load existing DNAs from registry   │
          │   • For each: compute Hamming distance │
          │   • Check similarity >= 90% threshold  │
          │   • Return: UNIQUE or DUPLICATE        │
          └─────────────────┬──────────────────────┘
                            │
              ┌─────────────┴──────────────┐
              │                            │
              ▼                            ▼
        UNIQUE (<90%)              DUPLICATE (>=90%)
              │                            │
              ▼                            ▼
    ┌─────────────────────┐    ┌──────────────────────┐
    │ MERKLE TREE MODULE  │    │ REJECT & REPORT      │
    │ • Create leaf data  │    │ • Return error       │
    │ • Hash with BLAKE3  │    │ • Report similarity  │
    │ • Append to tree    │    │ • Identify match     │
    │ • Rebuild tree      │    └──────────────────────┘
    │ • Save registry     │
    └─────────────────────┘
              │
              ▼
      New Root Hash
      (Registry updated)
```

### Component Details

**DNA Extraction Module** (`protrace/image_dna.py`)
- Implements dHash and Grid Hash algorithms
- Handles image preprocessing and normalization
- Exports `compute_dna()`, `hamming_distance()`, `dna_similarity()`

**Duplicate Detection Module** (`protrace/registration/register_image.py`)
- Manages comparison logic against existing registry
- Implements threshold-based decision making
- Exports `register_image()`, `check_for_duplicates()`

**Merkle Tree Module** (`protrace/merkle.py`)
- Implements binary Merkle tree with BLAKE3
- Manages leaf creation, tree construction, proof generation
- Exports `MerkleTree`, `add_leaf()`, `build_tree()`, `get_proof()`, `verify_proof()`

**Edition Registry Module** (`protrace/edition_core.py`)
- Tracks cross-chain NFT editions
- Manages universal key generation
- Exports `EditionRegistry`, `EditionMode`

---

## Performance

### DNA Extraction

Performance measurements based on 1,300 diverse test images (artwork, photographs, graphics):

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Time per image | 107ms | 45-50ms | 2.4x faster |
| Throughput | 9.3 images/sec | 20-22 images/sec | 2.4x faster |
| Memory usage | ~3 MB | 2.7 MB | 10% reduction |
| Batch (100 images) | 10.7 sec | 4.7 sec | 2.3x faster |

### Merkle Tree Operations

| Operation | 14 entries | 100 entries | 1K entries | 10K entries | 1M entries |
|-----------|------------|-------------|------------|-------------|------------|
| Build tree | <1ms | 0.7ms | 7ms | 70ms | 7 sec |
| Add leaf | 0.01ms | 0.01ms | 0.007ms | 0.007ms | 0.007ms |
| Generate proof | 0.27ms | 0.5ms | 0.7ms | 0.93ms | 1.0ms |
| Verify proof | 0.016ms | 0.016ms | 0.016ms | 0.016ms | 0.016ms |
| Proof size | 4 hashes | 7 hashes | 10 hashes | 14 hashes | 20 hashes |
| Tree depth | 4 | 7 | 10 | 14 | 20 |

Note: O(log n) complexity means doubling entries adds only one tree level.

### Duplicate Detection

| Metric | Performance |
|--------|-------------|
| Single comparison (Hamming distance) | 0.09 microseconds |
| Throughput | 11.5 million comparisons/sec |
| Check against 100 DNAs | <10ms |
| Check against 1,000 DNAs | <100ms |
| Algorithmic complexity | O(n), where n = existing DNAs |

### Storage Requirements

| Registry size | Disk space | RAM (in-memory) | JSON file | Compressed (gzip) |
|---------------|------------|-----------------|-----------|-------------------|
| 1,000 DNAs | 239 KB | 1.2 MB | 250 KB | ~60 KB |
| 10,000 DNAs | 2.4 MB | 12 MB | 2.5 MB | ~600 KB |
| 100,000 DNAs | 24 MB | 120 MB | 25 MB | ~6 MB |
| 1,000,000 DNAs | 240 MB | 330 MB | 250 MB | ~60 MB |

---

## Testing

### Test Results

The test suite validates all core functionality with 100% pass rate (19/19 tests).

| Test Suite | Tests | Passed | Duration |
|------------|-------|--------|----------|
| Comprehensive Suite | 9 | 9 | 5.60s |
| Full Functionality | 6 | 6 | ~3s |
| Merkle DNA Integration | 4 | 4 | ~2s |
| Total | 19 | 19 | ~11s |

### Component Validation

| Component | Status | Performance | Details |
|-----------|--------|-------------|---------|
| DNA fingerprinting | PASS | 756ms (2 images) | 100% success rate |
| Similarity detection | PASS | 235ms | Hamming distance verified |
| Duplicate detection | PASS | 1,378ms | 90% threshold working |
| Merkle construction | PASS | 4.46ms | Tree building correct |
| Merkle proofs | PASS | 0.27ms | All proofs verified |
| Edition management | PASS | <10ms | All modes functional |
| Cross-chain support | PASS | N/A | 4 blockchains supported |
| Performance benchmark | PASS | 1,172ms | 26.8 images/sec |

### Test Scenarios

**Scenario 1: Identical images**
- Input: Same image twice
- Hamming distance: 0 bits
- Similarity: 100.00%
- Result: DUPLICATE (rejected)

**Scenario 2: Minor modification**
- Input: Image with 1 bit changed
- Hamming distance: 1 bit
- Similarity: 99.61%
- Result: DUPLICATE (rejected)

**Scenario 3: Different images**
- Input: Two unrelated images
- Hamming distance: 126 bits
- Similarity: 50.78%
- Result: UNIQUE (both registered)

---

## Repository Structure

```
ProTRACE/
├── protrace/                       # Core Python package
│   ├── image_dna.py                # DNA extraction (optimized)
│   ├── merkle.py                   # BLAKE3 Merkle trees
│   ├── edition_core.py             # Cross-chain edition management
│   ├── cross_chain_minting.py      # Multi-chain minting logic
│   ├── vector_db.py                # Vector similarity search
│   ├── registration/               # Image registration system
│   │   ├── register_image.py       # Main registration workflow
│   │   └── batch_register.py       # Batch processing
│   ├── cli/                        # Command-line interface
│   └── tools/                      # Utility scripts
│
├── tests/                          # Test suite
│   ├── protrace_test_suite.py      # Main test suite
│   ├── test_all_functionality.py   # Integration tests
│   ├── integration/                # Integration tests
│   └── benchmarks/                 # Performance tests
│
├── demos/                          # Demonstration applications
│   ├── demo_workflow.py            # Complete workflow demo
│   └── mvp_demo.py                 # Minimal viable product demo
│
├── crates/                         # Rust implementation (optional)
│   └── dna-extraction/             # Rust DNA engine (20-50x faster)
│       ├── src/lib.rs              # Main library
│       ├── src/dhash.rs            # dHash implementation
│       └── src/grid.rs             # Grid hash (parallel)
│
├── data/                           # Data and registries
│   └── registry/                   # Test data
│
├── README.md                       # This file
├── setup.py                        # Python package configuration
├── requirements.txt                # Python dependencies
├── perceptual_hash_final.py        # Algorithm reference implementation
└── demo_workflow.py                # Interactive demonstration
```

---

##API Reference

### Core Functions

**compute_dna(image_path_or_bytes)**

Extracts 256-bit DNA fingerprint from an image.

Parameters:
- `image_path_or_bytes`: str, bytes, or PIL.Image - Input image

Returns:
- dict with keys:
  - `dna_hex`: 64-character hex string (256 bits)
  - `dna_binary`: 256-character binary string
  - `dhash`: 16-character hex (64 bits)
  - `grid_hash`: 48-character hex (192 bits)
  - `algorithm`: str - Algorithm identifier
  - `bits`: int - Total bits (256)

**hamming_distance(hash1, hash2)**

Calculates number of differing bits between two DNA hashes.

Parameters:
- `hash1`: str - First DNA hash (64 hex characters)
- `hash2`: str - Second DNA hash (64 hex characters)

Returns:
- int - Number of bits that differ (0-256)

**dna_similarity(hash1, hash2)**

Calculates similarity score between two DNA hashes.

Parameters:
- `hash1`: str - First DNA hash
- `hash2`: str - Second DNA hash

Returns:
- float - Similarity score (0.0-1.0, where 1.0 = identical)

**register_image(image_path, pointer, platform_id, similarity_threshold=0.90)**

Registers an image in the system with duplicate detection.

Parameters:
- `image_path`: str - Path to image file
- `pointer`: str - Unique identifier for the image
- `platform_id`: str - Platform identifier
- `similarity_threshold`: float - Duplicate detection threshold (default 0.90)

Returns:
- dict with keys:
  - `success`: bool - Whether registration succeeded
  - `plagiarized`: bool - Whether image is a duplicate
  - `root_hash`: str - New Merkle tree root hash (if successful)
  - `registry_size`: int - Total registered images (if successful)
  - `reason`: str - Failure reason (if unsuccessful)
  - `match`: dict - Match details (if duplicate)

### Merkle Tree API

**MerkleTree()**

Creates a new Merkle tree instance.

Methods:
- `add_leaf(dna_hex, pointer, platform_id, timestamp=None)` - Add entry to tree
- `build_tree()` - Construct tree and return root hash
- `get_proof(index)` - Generate inclusion proof for entry at index
- `verify_proof(leaf_data, proof, root_hash)` - Verify an inclusion proof

---

## Development

### Setup

```bash
git clone https://github.com/sapera-calibrate/ProTRACE.git
cd ProTRACE
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

### Running Tests

```bash
# Main test suite
python protrace_test_suite.py

# Integration tests
python tests/test_all_functionality.py

# Specific test
python tests/integration/test_merkle_dna_final.py
```

### Building Rust Implementation (Optional)

The Rust implementation provides 20-50x performance improvement (2-5ms per image).

```bash
cd crates/dna-extraction
cargo build --release --features parallel
cargo bench
```

---

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'protrace'"**
- Solution: Install in editable mode: `pip install -e .`
- Verify: `python -c "import protrace"`

**Issue: DNA extraction fails with "Image file not found"**
- Solution: Use absolute paths or verify working directory
- Check file permissions and format support

**Issue: High memory usage with large registries**
- Solution: Use database-backed storage instead of JSON
- Implement pagination for registry queries
- Consider registry sharding for >100K entries

**Issue: Slow duplicate detection on large registries**
- Solution: Pre-filter candidates using locality-sensitive hashing (LSH)
- Implement caching for frequently compared DNAs
- Use parallel processing: `multiprocessing.Pool`

### Performance Tuning

**For high-throughput scenarios (>1000 images/hour)**:
```python
# Use Rust implementation (20-50x faster)
from protrace_rust import compute_dna_fast
dna = compute_dna_fast(image_bytes)

# Batch processing
from protrace.registration.batch_register import batch_register_parallel
results = batch_register_parallel(image_paths, num_workers=8)
```

**For low-latency scenarios (<10ms response time)**:
- Pre-compute DNAs and store in database
- Use Redis cache for recent comparisons
- Implement bloom filters for quick negative lookups

### Extending ProTRACE

**Adding custom hash algorithms**:
```python
from protrace.image_dna import register_hash_algorithm

@register_hash_algorithm("custom_hash")
def my_custom_hash(image_array):
    # Your algorithm here
    return 256_bit_hash
```

**Custom similarity metrics**:
```python
from protrace.core import register_similarity_metric

@register_similarity_metric("weighted_hamming")
def weighted_similarity(hash1, hash2):
    # Weight different bit positions differently
    # Example: dHash bits weighted higher than Grid bits
    pass
```

---

## Contributing

This is proprietary software. For bug reports or feature requests, contact the development team.

---

## License

© 2025 Sapera Calibrate. Proprietary software.

---

## Documentation Notes

This README consolidates technical information from multiple sources including test reports, optimization studies, and workflow verification documents. For implementation-specific details, refer to inline code comments and docstrings in the source code.
