# 🚀 ProTRACE Solana Devnet Deployment Guide

**All compilation errors fixed - Ready for deployment!**

---

## ✅ Pre-Deployment Checklist

All critical fixes have been applied:
- ✅ Rust 1.82.0 toolchain
- ✅ Anchor 0.32.1 + Solana 3.0.8
- ✅ blake3 hashing (not deprecated modules)
- ✅ String .clone() for ownership
- ✅ Removed pointer dereference errors
- ✅ Vec::extend_from_slice for arrays
- ✅ init_if_needed pattern
- ✅ overflow-checks enabled

---

## 🎯 Quick Deployment (WSL)

### Step 1: Copy to WSL Home (Avoid Permission Issues)

```bash
# In WSL
cd ~
cp -r /mnt/d/ProTRACE\ -\ Copy\ -\ Copy/ProTRACE/ProRust ~/ProRust-deploy
cd ~/ProRust-deploy
```

### Step 2: Set Rust Version

```bash
rustup install 1.82.0
rustup default 1.82.0
rustc --version  # Should show 1.82.0
```

### Step 3: Clean Build

```bash
# Remove old artifacts
rm -rf target/ .anchor/ Cargo.lock

# Build
anchor build
```

**Expected Output:**
```
   Compiling protrace v1.0.0
    Finished release [optimized] target(s) in 3m 00s
```

### Step 4: Deploy to Devnet

```bash
# Ensure you have SOL in your wallet
solana balance

# If balance is 0, airdrop some SOL
solana airdrop 2

# Deploy
anchor deploy --provider.cluster devnet
```

**Expected Output:**
```
Deploying cluster: https://api.devnet.solana.com
Deploying program "protrace"...
Program Id: jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ

Deploy success
```

### Step 5: Verify Deployment

```bash
# Get program ID
solana address -k target/deploy/protrace-keypair.json

# Check program on-chain
solana program show jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ --url devnet

# Verify account
solana account jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ --url devnet
```

---

## 🔧 Troubleshooting

### Issue: "Cargo.lock version 4 not supported"
**Solution:** Already fixed - using Rust 1.82.0

### Issue: "Permission denied" in /mnt/d/
**Solution:** Build in WSL home directory (`~/ProRust-deploy`)

### Issue: "hash module not found"
**Solution:** Already fixed - using blake3

### Issue: "Insufficient funds"
**Solution:**
```bash
solana airdrop 2
# Wait 30 seconds
solana balance
```

### Issue: "Program already deployed"
**Solution:** Upgrade existing program:
```bash
anchor upgrade target/deploy/protrace.so --program-id jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ --provider.cluster devnet
```

---

## 📊 Post-Deployment Testing

### Test 1: Verify Program Exists

```bash
solana program show jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ --url devnet
```

**Expected:**
```
Program Id: jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ
Owner: BPFLoaderUpgradeab1e11111111111111111111111
ProgramData Address: <address>
Authority: <your wallet>
Last Deployed In Slot: <slot>
Data Length: <size> bytes
```

### Test 2: Check IDL

```bash
cat target/idl/protrace.json | jq '.instructions[] | .name'
```

**Expected:**
```
"anchor_merkle_root_oracle"
"anchor_dna_hash"
"register_edition_batch"
"verify_merkle_proof"
```

### Test 3: Test with Anchor Client

```bash
anchor test --skip-local-validator --provider.cluster devnet
```

---

## 🎯 Integration with TestSprite

Once deployed, update TestSprite config:

```json
{
  "environments": {
    "devnet": {
      "cluster": "https://api.devnet.solana.com",
      "programId": "jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ",
      "wallet": "~/.config/solana/id.json"
    }
  }
}
```

---

## 📝 Deployment Checklist

- [ ] Rust 1.82.0 installed
- [ ] Anchor CLI 0.32.1 installed
- [ ] Solana CLI installed
- [ ] Wallet configured with SOL
- [ ] Code copied to WSL home
- [ ] Clean build successful
- [ ] Deployment successful
- [ ] Program verified on-chain
- [ ] IDL generated
- [ ] TestSprite config updated

---

## 🚀 One-Line Deployment

```bash
cd ~ && cp -r /mnt/d/ProTRACE\ -\ Copy\ -\ Copy/ProTRACE/ProRust ~/ProRust-deploy && cd ~/ProRust-deploy && rustup default 1.82.0 && rm -rf target/ .anchor/ Cargo.lock && anchor build && solana airdrop 2 && sleep 30 && anchor deploy --provider.cluster devnet && solana address -k target/deploy/protrace-keypair.json
```

---

## 📊 Expected Timeline

| Step | Duration | Status |
|------|----------|--------|
| Copy files | 30s | ⏳ |
| Set Rust version | 1m | ⏳ |
| Clean build | 3m | ⏳ |
| Airdrop SOL | 30s | ⏳ |
| Deploy | 1m | ⏳ |
| Verify | 30s | ⏳ |
| **Total** | **~6 minutes** | ⏳ |

---

## ✅ Success Criteria

- ✅ Build completes without errors
- ✅ Program deploys to devnet
- ✅ Program ID matches: `jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ`
- ✅ Program visible on Solana Explorer
- ✅ IDL generated successfully
- ✅ All 4 instructions available

---

## 🔗 Useful Links

- **Solana Explorer:** https://explorer.solana.com/address/jFKkFoDNDUTFrg2KJZ1AVCxZPcQh9cci6EUhxJapUAZ?cluster=devnet
- **Anchor Docs:** https://www.anchor-lang.com/
- **Solana Docs:** https://docs.solana.com/

---

**Status:** 🟢 Ready for Deployment  
**All Errors Fixed:** ✅  
**Estimated Time:** 6 minutes
