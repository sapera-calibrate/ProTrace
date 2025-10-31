#!/bin/bash
# ProTRACE Solana Devnet Deployment Script
# Run in WSL: bash deploy_devnet.sh

set -e

echo "=================================================="
echo "🚀 ProTRACE Solana Devnet Deployment"
echo "=================================================="
echo ""

# Step 1: Copy files to WSL home
echo "📦 Step 1: Copying files to WSL home directory..."
cp -r /mnt/d/ProTRACE\ -\ Copy\ -\ Copy/ProTRACE/ProRust ~/ProRust-deploy
cd ~/ProRust-deploy
echo "✅ Files copied to ~/ProRust-deploy"
echo ""

# Step 2: Set Rust version
echo "🦀 Step 2: Setting Rust version to 1.82.0..."
rustup install 1.82.0 2>/dev/null || true
rustup default 1.82.0
RUST_VERSION=$(rustc --version)
echo "✅ Rust version: $RUST_VERSION"
echo ""

# Step 3: Clean build
echo "🔨 Step 3: Building Solana program..."
rm -rf target/ .anchor/ Cargo.lock
anchor build
echo "✅ Build successful!"
echo ""

# Step 4: Check wallet balance
echo "💰 Step 4: Checking wallet balance..."
BALANCE=$(solana balance --url devnet)
echo "Current balance: $BALANCE"

if [[ "$BALANCE" == "0 SOL" ]]; then
    echo "⚠️  Low balance, requesting airdrop..."
    solana airdrop 2 --url devnet
    sleep 30
    NEW_BALANCE=$(solana balance --url devnet)
    echo "✅ New balance: $NEW_BALANCE"
fi
echo ""

# Step 5: Deploy to devnet
echo "🚀 Step 5: Deploying to Solana devnet..."
anchor deploy --provider.cluster devnet
echo "✅ Deployment successful!"
echo ""

# Step 6: Get program ID
echo "🔍 Step 6: Verifying deployment..."
PROGRAM_ID=$(solana address -k target/deploy/protrace-keypair.json)
echo "Program ID: $PROGRAM_ID"
echo ""

# Step 7: Verify on-chain
echo "✅ Step 7: Checking program on-chain..."
solana program show $PROGRAM_ID --url devnet
echo ""

echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "📊 Summary:"
echo "  - Program ID: $PROGRAM_ID"
echo "  - Network: Devnet"
echo "  - Explorer: https://explorer.solana.com/address/$PROGRAM_ID?cluster=devnet"
echo ""
echo "🎯 Next Steps:"
echo "  1. Update Anchor.toml with Program ID"
echo "  2. Update TestSprite config"
echo "  3. Run integration tests"
echo ""
