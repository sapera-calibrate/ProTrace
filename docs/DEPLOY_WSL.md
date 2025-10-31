# 🚀 Deploy ProTRACE on WSL

## Single Command Deployment

```bash
# From Windows PowerShell or CMD
wsl -e bash -c "cd '/mnt/d/ProTRACE - Copy - Copy/ProTRACE' && bash deploy_testnet.sh"
```

## Alternative: Step by Step

```bash
# 1. Enter WSL
wsl

# 2. Navigate to project
cd /mnt/d/ProTRACE\ -\ Copy\ -\ Copy/ProTRACE

# 3. Run deployment
bash deploy_testnet.sh
```

## Prerequisites

### Install Anchor CLI in WSL

```bash
# Install Anchor Version Manager
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force

# Install latest Anchor
avm install latest
avm use latest

# Verify installation
anchor --version
```

### Check Solana CLI

```bash
# Already installed ✅
solana --version
# Output: solana-cli 1.18.26
```

### Check Wallet Balance

```bash
# Check testnet balance
solana balance --url testnet

# Request testnet SOL if needed
solana airdrop 2 --url testnet
```

## Quick Start

```bash
# Complete setup in one go
wsl bash -c '
cd "/mnt/d/ProTRACE - Copy - Copy/ProTRACE" && \
echo "Installing Anchor CLI..." && \
cargo install --git https://github.com/coral-xyz/anchor avm --locked --force && \
avm install latest && \
avm use latest && \
echo "Running deployment..." && \
bash deploy_testnet.sh
'
```

## Troubleshooting

### Issue: Anchor not found
**Solution:** Install Anchor CLI (see above)

### Issue: Insufficient balance
**Solution:** Request testnet SOL
```bash
solana airdrop 2 --url testnet
```

### Issue: Permission denied
**Solution:** Make script executable
```bash
chmod +x deploy_testnet.sh
```

---

**Status:** Ready for deployment  
**Network:** Solana Testnet  
**Estimated Time:** 5-10 minutes
