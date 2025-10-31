# ProTrace Rust - Quick Start Guide

Get up and running with ProTrace in 5 minutes!

## 🚀 Installation

### Step 1: Install Dependencies

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Verify installations
rustc --version
solana --version
```

### Step 2: Build ProTrace

```bash
cd protrace-rust
cargo build --release
```

This will take 5-10 minutes on first build.

### Step 3: Install CLI

```bash
cargo install --path crates/cli
```

Verify:
```bash
protrace --help
```

## 💼 Wallet Setup

### Create Your Wallet

```bash
protrace wallet new --output ~/.config/solana/protrace-wallet.json
```

**Important**: Save this file securely! It contains your private key.

### Fund Your Wallet (Devnet)

```bash
# Set wallet path
export WALLET=~/.config/solana/protrace-wallet.json

# Request airdrop (devnet SOL)
protrace wallet airdrop 2.0 --wallet $WALLET

# Check balance
protrace wallet balance --wallet $WALLET
```

## 🧬 Your First DNA Computation

### Download Test Image

```bash
# Create test directory
mkdir -p test_images
cd test_images

# Download sample image (or use your own)
# For testing, use any PNG/JPG image
```

### Compute DNA Hash

```bash
protrace dna compute test_images/image.png
```

Output:
```
🧬 DNA Fingerprint
  🔐 DNA Hash (256-bit):
    a1b2c3d4e5f6789012345678901234567890abcdef123456789abcdef0123456

  Component Hashes:
    dHash (64-bit): a1b2c3d4e5f67890
    Grid (192-bit): 1234567890abcdef123456789abcdef012345678
```

## 🔍 Compare Images

```bash
# Compare two images for similarity
protrace dna compare image1.png image2.png
```

Output shows:
- Hamming distance
- Similarity percentage
- Duplicate detection (>90% = duplicate)

## 🌳 Build Merkle Tree

### Process Multiple Images

```bash
protrace merkle build \
  image1.png image2.png image3.png \
  --platform devnet-test \
  --output merkle_manifest.json
```

This creates a manifest file with:
- Merkle root hash
- All leaf data
- Proofs for each leaf

## ⛓️ Anchor to Blockchain

### Connect to Devnet

```bash
# Ensure you have balance
protrace wallet balance --wallet $WALLET

# Anchor the Merkle root
protrace blockchain anchor merkle_manifest.json --wallet $WALLET
```

You'll get a transaction signature and Explorer link!

## 🧪 Run Complete Test

### End-to-End Workflow

```bash
protrace test \
  test_images/*.png \
  --wallet $WALLET \
  --verbose
```

This runs the complete workflow:
1. ✅ Wallet connection
2. ✅ DNA computation
3. ✅ Duplicate detection
4. ✅ Merkle tree building
5. ✅ Blockchain anchoring
6. ✅ Proof generation & verification

## 📊 Real-World Usage

### Batch Process Collection

```bash
# Process entire NFT collection
protrace dna batch collection/*.png > dna_results.json

# Build Merkle tree
protrace merkle build collection/*.png \
  --platform my-nft-platform \
  --output collection_manifest.json

# Anchor to blockchain
protrace blockchain anchor collection_manifest.json \
  --wallet $WALLET
```

### Duplicate Detection

```bash
# Find duplicates in batch
protrace dna batch suspicious/*.png

# Output will highlight any duplicates found
```

## 🔧 Common Commands

### Wallet Operations

```bash
# Create wallet
protrace wallet new --output wallet.json

# View wallet info
protrace wallet info --wallet wallet.json

# Get balance
protrace wallet balance --wallet wallet.json

# Request airdrop (devnet only)
protrace wallet airdrop 1.0 --wallet wallet.json
```

### DNA Operations

```bash
# Single image
protrace dna compute image.png

# Compare two images
protrace dna compare image1.png image2.png

# Batch process
protrace dna batch *.png
```

### Merkle Operations

```bash
# Build tree
protrace merkle build *.png --output manifest.json

# Generate proof
protrace merkle proof manifest.json 0

# Verify proof
protrace merkle verify manifest.json proof.json 0
```

### Blockchain Operations

```bash
# Initialize Merkle root
protrace blockchain init-root <root_hash> --wallet wallet.json

# Update root
protrace blockchain update-root <new_root> --wallet wallet.json

# Anchor via oracle
protrace blockchain anchor manifest.json --wallet wallet.json

# Initialize edition registry
protrace blockchain init-registry --wallet wallet.json
```

## 🐛 Troubleshooting

### Build Errors

```bash
# Clean and rebuild
cargo clean
cargo build --release
```

### Wallet Issues

```bash
# Verify wallet file format
cat wallet.json | jq '.'

# Should be JSON array of 64 numbers
```

### Insufficient Balance

```bash
# Check balance
protrace wallet balance --wallet $WALLET

# Request more SOL (devnet)
protrace wallet airdrop 2.0 --wallet $WALLET
```

### Program Not Deployed

The Anchor program must be deployed to devnet. See the main README for deployment instructions.

## 📖 Next Steps

- [Full README](README.md) - Complete documentation
- [API Documentation](https://docs.rs/protrace-*) - Rust API docs
- [Examples](examples/) - Code examples

## 💡 Tips

1. **Always backup your wallet file**
2. **Use environment variables for wallet path**:
   ```bash
   export WALLET=~/.config/solana/protrace-wallet.json
   ```
3. **Enable verbose logging for debugging**:
   ```bash
   protrace --verbose test images/*.png
   ```
4. **Check devnet status** if transactions fail:
   https://status.solana.com/

## 🎯 Production Checklist

Before going to mainnet:

- [ ] Secure wallet management (HSM/hardware wallet)
- [ ] Audit smart contracts
- [ ] Test with large datasets
- [ ] Set up monitoring
- [ ] Configure rate limiting
- [ ] Implement backup strategies
- [ ] Review security best practices

---

**Happy Building! 🚀**

For help: `protrace --help`
