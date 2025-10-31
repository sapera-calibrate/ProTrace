# 🚀 ProTRACE Testnet Deployment Guide

**Complete guide for deploying ProTRACE to Solana Testnet**

---

## 📋 Pre-Deployment Checklist

### ✅ Prerequisites

- [ ] Solana CLI installed (`solana --version`)
- [ ] Anchor CLI installed (`anchor --version`)
- [ ] Rust toolchain 1.82.0 (`rustup default 1.82.0`)
- [ ] Node.js and Yarn (`node --version`, `yarn --version`)
- [ ] Testnet SOL in wallet (use faucet)
- [ ] Python 3.10+ with venv
- [ ] Git repository access

### ✅ Environment Check

```bash
# Check Solana CLI
solana --version  # Should be 1.18+

# Check Anchor
anchor --version  # Should be 0.32.1

# Check Rust
rustc --version  # Should be 1.82.0

# Check wallet
solana address
solana balance --url testnet

# Request testnet SOL if needed
solana airdrop 2 --url testnet
```

---

## 🔧 Step 1: Build Solana Program

### Navigate to ProRust

```bash
cd ProRust
```

### Update Anchor.toml for Testnet

```toml
[provider]
cluster = "testnet"  # Change from devnet
wallet = "~/.config/solana/id.json"

[programs.testnet]
protrace = "7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG"  # Will update after deploy
```

### Build Program

```bash
# Clean build
rm -rf target/ .anchor/

# Build with security.txt
anchor build

# Verify binary size (should be ~340KB)
ls -lh target/deploy/protrace.so

# Verify IDL
cat target/idl/protrace.json | jq '.instructions[] | .name'
```

**Expected Output:**
```
✓ Built program: protrace.so (340KB)
✓ Generated IDL: protrace.json (1.5KB)
✓ 8 instructions available
```

---

## 🌐 Step 2: Deploy to Testnet

### Deploy Program

```bash
# Deploy to testnet
anchor deploy --provider.cluster testnet

# Save the Program ID!
# Example output:
# Program Id: AbcDefGhiJkLmNoPqRsTuVwXyZ123456789
```

### Verify Deployment

```bash
# Check program on-chain
solana program show <PROGRAM_ID> --url testnet

# Query security.txt
cargo install query-security-txt
query-security-txt <PROGRAM_ID> --url testnet
```

### Update Configuration

Update `Anchor.toml` with your new Program ID:

```toml
[programs.testnet]
protrace = "YOUR_NEW_PROGRAM_ID_HERE"
```

---

## 🐍 Step 3: Setup Python SDK

### Install Python Environment

```bash
cd ../ProPy
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install solders solana anchorpy
```

### Test DNA Extraction

```python
# test_dna_extraction.py
from modules.protrace_legacy.image_dna import compute_dna

# Extract DNA from image
result = compute_dna("path/to/image.png")
print(f"DNA Hash: {result['dna_hex']}")
print(f"Algorithm: {result['algorithm']}")
print(f"Bits: {result['bits']}")
```

```bash
python test_dna_extraction.py
```

---

## 🦀 Step 4: Build Rust Crates (Optional)

### DNA Extraction Crate

```bash
cd ../ProRust/crates/dna-extraction
cargo build --release
cargo test

# Run example
cargo run --example basic path/to/image.png
```

### Merkle Tree Crate

```bash
cd ../merkle-tree
cargo build --release
cargo test

# Run example
cargo run --example basic
```

---

## 📦 Step 5: Create User-Facing API

### FastAPI Server

Create `ProPy/api_testnet.py`:

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from modules.protrace_legacy.image_dna import compute_dna
from modules.protrace_legacy.merkle import MerkleTree
import tempfile
import os

app = FastAPI(
    title="ProTRACE Testnet API",
    description="DNA Extraction and Merkle Tree API on Solana Testnet",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "ProTRACE Testnet API",
        "version": "1.0.0",
        "network": "Solana Testnet",
        "program_id": "7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG",
        "endpoints": {
            "extract_dna": "/dna/extract",
            "create_merkle": "/merkle/create",
            "health": "/health"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "network": "testnet",
        "modules": {
            "dna_extraction": True,
            "merkle_tree": True
        }
    }

@app.post("/dna/extract")
async def extract_dna(file: UploadFile = File(...)):
    """Extract DNA hash from uploaded image"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract DNA
        result = compute_dna(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "dna_hash": result['dna_hex'],
            "dhash": result['dhash'],
            "grid_hash": result['grid_hash'],
            "algorithm": result['algorithm'],
            "bits": result['bits']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/merkle/create")
def create_merkle_tree(leaves: list[str]):
    """Create Merkle tree from DNA hashes"""
    try:
        tree = MerkleTree()
        
        for i, leaf in enumerate(leaves):
            tree.add_leaf(leaf, f"ptr_{i}", "testnet", int(time.time()))
        
        root = tree.build_tree()
        
        return {
            "success": True,
            "root": root,
            "leaf_count": len(leaves),
            "network": "testnet"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Start API Server

```bash
cd ProPy
source venv/bin/activate
python api_testnet.py
```

**API will be available at:** http://localhost:8000

**API Docs:** http://localhost:8000/docs

---

## 🧪 Step 6: Test End-to-End

### Test DNA Extraction

```bash
curl -X POST "http://localhost:8000/dna/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/image.png"
```

### Test Merkle Tree

```bash
curl -X POST "http://localhost:8000/merkle/create" \
  -H "Content-Type: application/json" \
  -d '{"leaves": ["abc123...", "def456..."]}'
```

### Test Solana Integration

```python
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from anchorpy import Program, Provider, Wallet

# Connect to testnet
client = Client("https://api.testnet.solana.com")

# Your program ID
PROGRAM_ID = Pubkey.from_string("7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG")

# Load program
provider = Provider(client, wallet)
program = await Program.at(PROGRAM_ID, provider)

# Call anchor_dna_hash instruction
tx = await program.rpc["anchor_dna_hash"](
    dna_hash,
    edition_mode,
    ctx=Context(
        accounts={
            "hash_data": hash_data_pubkey,
            "user": wallet.public_key,
            "system_program": SYS_PROGRAM_ID,
        }
    )
)

print(f"Transaction: {tx}")
```

---

## 📚 Step 7: Documentation for Users

### Create User Guide

File: `USER_GUIDE.md`

```markdown
# ProTRACE User Guide - Testnet

## DNA Extraction

### Via API

curl -X POST "http://api.protrace.io/dna/extract" \
  -F "file=@image.png"

### Via Python

from protrace import extract_dna
dna = extract_dna("image.png")

### Via CLI

protrace extract image.png
```

### Create API Documentation

Generate OpenAPI docs:

```bash
cd ProPy
python -c "from api_testnet import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

---

## 🔐 Step 8: Security Configuration

### Update Security.txt

Ensure security information is current:

```bash
# Query security info
query-security-txt <PROGRAM_ID> --url testnet

# Should show:
# - Contact: security@protrace.io
# - Policy: SECURITY.md
# - Testnet deployment info
```

### Configure Rate Limiting

Add to API:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/dna/extract")
@limiter.limit("10/minute")
async def extract_dna(request: Request, file: UploadFile = File(...)):
    ...
```

---

## 📊 Step 9: Monitoring & Analytics

### Setup Monitoring

```python
# monitoring.py
from prometheus_client import Counter, Histogram
import time

dna_extractions = Counter('dna_extractions_total', 'Total DNA extractions')
extraction_duration = Histogram('extraction_duration_seconds', 'DNA extraction duration')

@app.post("/dna/extract")
async def extract_dna(file: UploadFile = File(...)):
    start_time = time.time()
    
    # ... extraction logic ...
    
    dna_extractions.inc()
    extraction_duration.observe(time.time() - start_time)
    
    return result
```

### Create Health Checks

```python
@app.get("/health/live")
def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
def readiness():
    # Check Solana connection
    try:
        client = Client("https://api.testnet.solana.com")
        client.is_connected()
        return {"status": "ready", "solana": "connected"}
    except:
        return {"status": "not_ready", "solana": "disconnected"}
```

---

## 🚢 Step 10: Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`python TEST_FINAL.py`)
- [ ] Solana program built (`anchor build`)
- [ ] Security.txt verified
- [ ] API server tested locally
- [ ] Documentation complete
- [ ] Security audit completed (recommended)

### Deployment

- [ ] Deploy Solana program to testnet
- [ ] Verify program on-chain
- [ ] Update all configuration files
- [ ] Deploy API server
- [ ] Test all endpoints
- [ ] Monitor for issues

### Post-Deployment

- [ ] Verify all functionality
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Update user documentation
- [ ] Announce testnet availability
- [ ] Gather user feedback

---

## 📞 Support & Resources

### Getting Help

- **Email**: hello@protrace.io
- **Security**: security@protrace.io  
- **Documentation**: README.md, USER_GUIDE.md
- **API Docs**: http://api.protrace.io/docs

### Useful Commands

```bash
# Check testnet balance
solana balance --url testnet

# Request SOL
solana airdrop 2 --url testnet

# View program logs
solana logs <PROGRAM_ID> --url testnet

# Check program info
solana program show <PROGRAM_ID> --url testnet

# Rebuild and redeploy
anchor build && anchor deploy --provider.cluster testnet
```

---

## ✅ Success Criteria

- ✅ Solana program deployed and verified
- ✅ DNA extraction API accessible
- ✅ Merkle tree generation working
- ✅ Security.txt queryable on-chain
- ✅ API documentation published
- ✅ User guide available
- ✅ Monitoring active
- ✅ All tests passing

---

**Status**: 🟢 **READY FOR TESTNET DEPLOYMENT**  
**Network**: Solana Testnet  
**Estimated Deploy Time**: 30 minutes  
**User-Facing**: API + SDK + CLI
