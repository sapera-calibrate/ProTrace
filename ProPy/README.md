# ProTRACE Python SDK

**DNA Fingerprinting & Merkle Trees - Python Implementation**

---

## 📚 Overview

The ProTRACE Python SDK provides DNA fingerprinting and Merkle tree functionality for digital assets. It includes:

- **DNA Extraction**: 256-bit perceptual hashing for images
- **Merkle Trees**: BLAKE3-based tree construction and proof generation
- **REST API**: FastAPI server for HTTP access
- **CLI Tool**: Command-line interface for batch operations
- **SDK**: Direct Python module integration

---

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from modules.protrace_legacy.image_dna import compute_dna
from modules.protrace_legacy.merkle import MerkleTree

# Extract DNA from image
result = compute_dna("image.png")
print(f"DNA Hash: {result['dna_hex']}")

# Create Merkle tree
tree = MerkleTree()
tree.add_leaf(result['dna_hex'], "ptr_1", "platform", 1234567890)
root = tree.build_tree()
print(f"Root: {root}")
```

---

## 🔧 Components

### 1. DNA Extraction Module

**Location:** `modules/protrace_legacy/image_dna.py`

#### Features

- **256-bit DNA fingerprints** (dHash 64-bit + Grid Hash 192-bit)
- **Perceptual hashing** - Similar images have similar hashes
- **Fast processing** - ~45ms per image
- **Batch support** - Process multiple images

#### API

```python
compute_dna(image_path: str) -> dict
```

**Returns:**
```python
{
    "dna_hex": str,        # 256-bit hash (64 hex chars)
    "dhash": str,          # 64-bit gradient-based (16 hex chars)
    "grid_hash": str,      # 192-bit structure-based (48 hex chars)
    "algorithm": str,      # "dHash+Grid-Optimized"
    "bits": int            # 256
}
```

#### Example

```python
from modules.protrace_legacy.image_dna import compute_dna

# Extract DNA
result = compute_dna("photo.jpg")

# Access components
dna = result['dna_hex']       # Full 256-bit hash
dhash = result['dhash']        # Gradient component
grid = result['grid_hash']     # Structure component

# Calculate similarity
def hamming_distance(h1, h2):
    return sum(c1 != c2 for c1, c2 in zip(
        bin(int(h1, 16))[2:].zfill(256),
        bin(int(h2, 16))[2:].zfill(256)
    ))

# Compare two images
result1 = compute_dna("image1.jpg")
result2 = compute_dna("image2.jpg")
distance = hamming_distance(result1['dna_hex'], result2['dna_hex'])
similarity = 1.0 - (distance / 256)
print(f"Similarity: {similarity:.2%}")
```

---

### 2. Merkle Tree Module

**Location:** `modules/protrace_legacy/merkle.py`

#### Features

- **BLAKE3 hashing** - Fast cryptographic hash function
- **Balanced binary tree** - Optimal proof size O(log n)
- **Proof generation** - Create Merkle proofs
- **Proof verification** - Verify proof validity
- **SHA256 fallback** - If BLAKE3 not available

#### API

```python
class MerkleTree:
    def __init__(self)
    def add_leaf(self, dna_hex: str, pointer: str, platform_id: str, timestamp: int)
    def build_tree(self) -> str
    def get_proof(self, index: int) -> List[Dict]
    def verify_proof(self, index: int, proof: List[Dict], root_hash: str) -> bool
```

#### Example

```python
from modules.protrace_legacy.merkle import MerkleTree

# Create tree
tree = MerkleTree()

# Add leaves
tree.add_leaf("abc123...", "ipfs://Qm...", "ethereum", 1234567890)
tree.add_leaf("def456...", "ipfs://Qm...", "solana", 1234567891)
tree.add_leaf("ghi789...", "ipfs://Qm...", "polygon", 1234567892)

# Build tree
root = tree.build_tree()
print(f"Merkle Root: {root}")

# Generate proof for first leaf
proof = tree.get_proof(0)
print(f"Proof elements: {len(proof)}")

# Verify proof
is_valid = tree.verify_proof(0, proof, root)
print(f"Proof valid: {is_valid}")
```

---

### 3. REST API Server

**Location:** `api_testnet.py`

#### Starting the Server

```bash
python api_testnet.py

# Server runs on http://localhost:8000
# API Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/dna/extract` | Extract DNA from image |
| POST | `/merkle/create` | Create Merkle tree |
| POST | `/merkle/verify` | Verify Merkle proof |
| GET | `/info/program` | Solana program info |
| GET | `/docs` | Interactive API docs |

#### Examples

**Extract DNA:**
```bash
curl -X POST "http://localhost:8000/dna/extract" \
  -F "file=@image.png"
```

**Response:**
```json
{
  "success": true,
  "dna_hash": "1818181818181818...",
  "dhash": "1818181818181818",
  "grid_hash": "0000001818000000...",
  "algorithm": "dHash+Grid-Optimized",
  "bits": 256,
  "extraction_time_ms": 45.32
}
```

**Create Merkle Tree:**
```bash
curl -X POST "http://localhost:8000/merkle/create" \
  -H "Content-Type: application/json" \
  -d '{"leaves": ["abc123...", "def456..."]}'
```

**Response:**
```json
{
  "success": true,
  "root": "4e3bca13b50cf2d9...",
  "leaf_count": 2,
  "network": "testnet",
  "generation_time_ms": 12.45
}
```

---

### 4. CLI Tool

**Location:** `cli_testnet.py`

#### Commands

```bash
# Extract DNA from single image
python cli_testnet.py extract image.png

# Batch extract from directory
python cli_testnet.py batch ./images/ -o results.json

# Create Merkle tree from hashes
python cli_testnet.py merkle results.json -o tree.json

# Show program info
python cli_testnet.py info
```

#### Examples

**Single Image:**
```bash
python cli_testnet.py extract photo.jpg -o output.json

# Output:
# ✅ DNA Extraction Complete
# DNA Hash:   1818181818181818...
# DHash:      1818181818181818
# Grid Hash:  0000001818000000...
# Algorithm:  dHash+Grid-Optimized
# Bits:       256
# Time:       45.32ms
# 💾 Saved to: output.json
```

**Batch Processing:**
```bash
python cli_testnet.py batch ./nft_collection/ -o hashes.json

# Output:
# 📁 Batch extracting DNA from: ./nft_collection/
# 📸 Found 100 images
# [1/100] Processing: image_001.png... ✅
# [2/100] Processing: image_002.png... ✅
# ...
# ✅ Successfully processed: 100/100
# 💾 Results saved to: hashes.json
```

**Merkle Tree:**
```bash
python cli_testnet.py merkle hashes.json -o tree.json

# Output:
# 🌲 Creating Merkle tree from: hashes.json
# 📝 Processing 100 leaves...
# ✅ Merkle Tree Created
# Root:       4e3bca13b50cf2d9...
# Leaves:     100
# Time:       50.23ms
# 💾 Saved to: tree.json
```

---

## 📦 Dependencies

### Required

```txt
Pillow>=10.0.0          # Image processing
numpy>=1.24.0           # Array operations
blake3>=0.3.0           # BLAKE3 hashing (optional, falls back to SHA256)
```

### Optional (for API/CLI)

```txt
fastapi>=0.104.0        # REST API framework
uvicorn>=0.24.0         # ASGI server
pydantic>=2.0.0         # Data validation
```

### Development

```txt
pytest>=7.4.0           # Testing
black>=23.0.0           # Code formatting
mypy>=1.5.0             # Type checking
```

---

## 🧪 Testing

```bash
# Run all tests
cd ../tests
python TEST_FINAL.py

# Test parity with Rust
python test_python_rust_parity.py

# Expected output:
# ✅ DNA Extraction: WORKING
# ✅ Merkle Tree: WORKING
# ✅ Python-Rust Parity: 100% MATCH
```

---

## 📊 Performance

| Operation | Time | Throughput |
|-----------|------|------------|
| **DNA Extraction** | ~45ms | 22 images/sec |
| **Merkle Build (10)** | ~5ms | - |
| **Merkle Build (100)** | ~50ms | - |
| **Merkle Build (1000)** | ~500ms | - |
| **Proof Generation** | ~100μs | - |
| **Proof Verification** | ~100μs | - |

---

## 🔧 Advanced Usage

### Custom DNA Extraction

```python
from PIL import Image
from modules.protrace_legacy.image_dna import compute_dhash_legacy

# Load image
img = Image.open("photo.jpg")

# Compute dHash only
dhash = compute_dhash_legacy(img, hash_size=8)
print(f"dHash: {dhash}")
```

### Standalone Merkle Functions

```python
from modules.protrace_legacy.merkle import compute_leaf_hash, verify_proof_standalone

# Compute leaf hash without tree
leaf_hash = compute_leaf_hash(
    dna_hex="abc123...",
    pointer="ipfs://Qm...",
    platform_id="solana",
    timestamp=1234567890
)

# Verify proof without tree object
is_valid = verify_proof_standalone(
    dna_hex="abc123...",
    pointer="ipfs://Qm...",
    platform_id="solana",
    timestamp=1234567890,
    proof=proof_elements,
    root_hash="expected_root..."
)
```

---

## 🐛 Troubleshooting

### Import Errors

```python
# If you get import errors, add to sys.path:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### BLAKE3 Not Available

```bash
# Install BLAKE3 (optional but recommended)
pip install blake3

# Falls back to SHA256 if not available
```

### PIL/Pillow Issues

```bash
# Reinstall Pillow
pip uninstall Pillow
pip install Pillow --no-cache-dir
```

---

## 📖 API Reference

Complete API documentation available at:
- **Interactive Docs**: http://localhost:8000/docs (after starting API)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🤝 Contributing

See main [README](../README.md) for contribution guidelines.

---

## 📜 License

MIT License - see [LICENSE](../LICENSE) for details.

---

**For full documentation, see the [main README](../README.md)**
