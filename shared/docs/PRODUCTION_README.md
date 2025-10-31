## ProTRACE - Production-Ready NFT Authenticity Verification

**Version:** 1.0.0  
**Status:** Production Ready  
**Environment:** Devnet Testing Ready  

---

## 🎯 Overview

ProTRACE is a production-grade NFT authenticity verification system using DNA fingerprinting, Merkle trees, and multi-chain support (Ethereum, Solana, Tezos).

### Key Features

- ✅ **DNA Fingerprinting** - Perceptual hashing for image uniqueness
- ✅ **Merkle Tree Proofs** - Cryptographic verification
- ✅ **Multi-Chain Support** - Ethereum, Solana, Tezos
- ✅ **Duplicate Detection** - AI-powered similarity matching
- ✅ **Production API** - Clean, organized, documented
- ✅ **TestSprite Integration** - Automated testing
- ✅ **Devnet Ready** - Configured for testnet deployment

---

## 📁 Project Structure

```
ProTRACE/
├── backend/                    # Production backend
│   ├── api.py                 # Main FastAPI application
│   ├── config.py              # Configuration management
│   ├── testsprite_runner.py   # TestSprite integration
│   ├── routers/               # API route handlers
│   ├── services/              # Business logic
│   └── models/                # Data models
│
├── protrace/                   # Core library
│   ├── image_dna.py           # DNA fingerprinting
│   ├── merkle.py              # Merkle tree implementation
│   ├── eip712.py              # Ethereum signing
│   ├── vector_db.py           # Similarity search
│   ├── ipfs.py                # IPFS integration
│   └── registration/          # Image registration
│
├── solana-program/             # Solana smart contracts
├── V_on_chain/                 # Ethereum contracts
├── protrace-rust/              # Rust implementations
│
├── tests/                      # All tests
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── testsprite/            # TestSprite tests
│
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
├── data/                       # Data storage
├── registry/                   # Image registry
└── logs/                       # Application logs
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd ProTRACE

# Install Python dependencies
pip install -r requirements.txt

# Install Rust (if using Rust components)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Solana CLI (if deploying to Solana)
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

### 2. Configuration

Create `.env` file:

```bash
# Environment
ENVIRONMENT=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Blockchain
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_CLUSTER=devnet

# Features
IPFS_ENABLED=False
VECTOR_DB_ENABLED=False
```

### 3. Start Backend

```bash
# Development mode
python3 -m backend.api

# Production mode
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

---

## 🧪 Testing

### Run All Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# TestSprite tests
python3 backend/testsprite_runner.py
```

### Manual API Testing

```bash
# Compute DNA hash
curl -X POST http://localhost:8000/api/v1/dna/compute \
  -H "Content-Type: application/json" \
  -d '{"image_path": "path/to/image.png"}'

# Register image
curl -X POST http://localhost:8000/api/v1/images/register \
  -H "Content-Type: application/json" \
  -d '{
    "image_identifier": "artwork_001",
    "image_id": "nft_001",
    "platform_id": "opensea"
  }'

# Build Merkle tree
curl -X POST http://localhost:8000/api/v1/merkle/build \
  -H "Content-Type: application/json" \
  -d '{"dna_hashes": ["hash1", "hash2", "hash3"]}'
```

---

## 🌐 Devnet Deployment

### Automated Deployment

```bash
# Deploy to devnet (Solana, Ethereum testnets)
bash deploy_devnet.sh
```

### Manual Deployment

#### 1. Configure for Devnet

```bash
# Update .env
ENVIRONMENT=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
```

#### 2. Deploy Solana Program

```bash
cd solana-program
anchor build
anchor deploy --provider.cluster devnet
```

#### 3. Start API Server

```bash
python3 -m backend.api
```

#### 4. Run Tests

```bash
python3 backend/testsprite_runner.py
```

---

## 📚 API Documentation

### Core Endpoints

#### DNA Fingerprinting

```
POST /api/v1/dna/compute
```

**Request:**
```json
{
  "image_data": "base64_encoded_image",
  "image_path": "/path/to/image.png",
  "image_url": "https://example.com/image.png"
}
```

**Response:**
```json
{
  "dna_hex": "64_character_hex_string",
  "dhash": "16_character_dhash",
  "grid_hash": "48_character_grid_hash",
  "timestamp": 1234567890,
  "success": true
}
```

#### Image Registration

```
POST /api/v1/images/register
```

**Request:**
```json
{
  "image_identifier": "unique_id",
  "image_id": "nft_001",
  "platform_id": "opensea",
  "similarity_threshold": 0.90
}
```

**Response:**
```json
{
  "success": true,
  "plagiarized": false,
  "root_hash": "merkle_root",
  "match": null,
  "dna_hex": "computed_dna",
  "registration_id": "nft_001",
  "timestamp": 1234567890
}
```

#### Merkle Tree

```
POST /api/v1/merkle/build
```

**Request:**
```json
{
  "dna_hashes": ["hash1", "hash2", "hash3"],
  "session_name": "batch_001"
}
```

**Response:**
```json
{
  "root_hash": "merkle_root",
  "leaf_count": 3,
  "session_id": "session_identifier",
  "tree_height": 2,
  "timestamp": 1234567890
}
```

```
GET /api/v1/merkle/proof/{session_id}/{leaf_index}
```

**Response:**
```json
{
  "leaf_index": 0,
  "proof": ["hash1", "hash2"],
  "root_hash": "merkle_root",
  "verified": true
}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | development | No |
| `DEBUG` | Enable debug mode | False | No |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `API_PREFIX` | API route prefix | /api/v1 | No |
| `SOLANA_RPC_URL` | Solana RPC endpoint | devnet | Yes* |
| `SOLANA_PROGRAM_ID` | Deployed program ID | - | Yes* |
| `ETH_RPC_URL` | Ethereum RPC endpoint | - | Yes* |
| `ETH_CONTRACT_ADDRESS` | Contract address | - | Yes* |
| `DATABASE_URL` | PostgreSQL URL | - | No |
| `REDIS_URL` | Redis URL | - | No |
| `IPFS_ENABLED` | Enable IPFS | False | No |
| `VECTOR_DB_ENABLED` | Enable vector DB | False | No |

\* Required for blockchain features

---

## 📊 Monitoring & Logging

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-10-30T12:00:00Z",
  "uptime": 12345.67,
  "services": {
    "api": true,
    "vector_db": false,
    "ipfs": false,
    "merkle": true
  }
}
```

### Statistics

```bash
curl http://localhost:8000/api/v1/stats
```

### Logs

```bash
# View logs
tail -f logs/api.log

# Set log level in .env
LOG_LEVEL=DEBUG
```

---

## 🔐 Security

### API Key Authentication (Production)

```bash
# Enable in .env
API_KEY_ENABLED=True
JWT_SECRET=your_secret_key

# Include in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/v1/...
```

### Rate Limiting

```bash
# Configure in .env
RATE_LIMIT=100  # requests per minute
```

---

## 🛠️ Development

### Repository Cleanup

```bash
# Remove test artifacts and organize
python3 cleanup_and_organize.py
```

### Code Quality

```bash
# Format code
black backend/ protrace/

# Lint
flake8 backend/ protrace/

# Type check
mypy backend/ protrace/
```

### Build

```bash
# Python package
python3 setup.py sdist bdist_wheel

# Rust components
cd protrace-rust
cargo build --release

# Solana program
cd solana-program
anchor build
```

---

## 📦 Deployment

### Docker

```bash
# Build image
docker build -t protrace-api:latest .

# Run container
docker run -p 8000:8000 protrace-api:latest

# Docker Compose
docker-compose up -d
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure database (PostgreSQL)
- [ ] Configure Redis for caching
- [ ] Enable API key authentication
- [ ] Set up monitoring (Sentry)
- [ ] Configure SSL/TLS
- [ ] Set up load balancer
- [ ] Configure backups
- [ ] Set up CI/CD pipeline

---

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 python3 -m backend.api
```

**Module not found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Solana deployment fails:**
```bash
# Check balance
solana balance

# Request airdrop
solana airdrop 2

# Check network
solana config get
```

---

## 📖 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **GitHub Repository:** [Link]
- **Discord Community:** [Link]
- **Technical Blog:** [Link]

---

## 📄 License

[Your License]

---

## 👥 Contributors

[List of contributors]

---

## 🙏 Acknowledgments

- Solana Foundation
- Ethereum Foundation
- TestSprite

---

**Last Updated:** 2025-10-30  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
