#!/bin/bash
# ProTrace Devnet Setup Script

set -e

echo "🔒 ProTrace Devnet Setup"
echo "════════════════════════════════════════════════════════"
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Solana CLI is installed
if ! command -v solana &> /dev/null; then
    echo -e "${RED}✗ Solana CLI not found${NC}"
    echo "Install with: sh -c \"\$(curl -sSfL https://release.solana.com/stable/install)\""
    exit 1
fi

echo -e "${GREEN}✓ Solana CLI found${NC}"
solana --version
echo

# Check if Anchor is installed
if ! command -v anchor &> /dev/null; then
    echo -e "${YELLOW}⚠ Anchor not found (optional)${NC}"
    echo "Install with: cargo install --git https://github.com/coral-xyz/anchor avm --locked --force"
else
    echo -e "${GREEN}✓ Anchor found${NC}"
    anchor --version
fi
echo

# Configure Solana for devnet
echo "📡 Configuring Solana for devnet..."
solana config set --url devnet
echo -e "${GREEN}✓ Connected to devnet${NC}"
echo

# Create wallet if it doesn't exist
WALLET_PATH="${HOME}/.config/solana/protrace-devnet.json"

if [ -f "$WALLET_PATH" ]; then
    echo -e "${YELLOW}⚠ Wallet already exists at: $WALLET_PATH${NC}"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing wallet"
    else
        solana-keygen new --outfile "$WALLET_PATH" --force
        echo -e "${GREEN}✓ New wallet created${NC}"
    fi
else
    echo "🔑 Creating new wallet..."
    mkdir -p "$(dirname "$WALLET_PATH")"
    solana-keygen new --outfile "$WALLET_PATH"
    echo -e "${GREEN}✓ Wallet created at: $WALLET_PATH${NC}"
fi
echo

# Set wallet
solana config set --keypair "$WALLET_PATH"
PUBKEY=$(solana address)
echo -e "${GREEN}✓ Wallet configured${NC}"
echo "  Public Key: $PUBKEY"
echo

# Request airdrop
echo "💰 Requesting airdrop..."
if solana airdrop 2 "$PUBKEY"; then
    echo -e "${GREEN}✓ Airdrop successful${NC}"
else
    echo -e "${RED}✗ Airdrop failed${NC}"
    echo "You may need to wait or use a faucet: https://solfaucet.com/"
fi
echo

# Check balance
echo "💵 Checking balance..."
BALANCE=$(solana balance)
echo "  Balance: $BALANCE"
echo

# Summary
echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo
echo "Wallet Path: $WALLET_PATH"
echo "Public Key: $PUBKEY"
echo "Balance: $BALANCE"
echo
echo "Next steps:"
echo "  1. Build ProTrace: cargo build --release"
echo "  2. Install CLI: cargo install --path crates/cli"
echo "  3. Run test: protrace test images/*.png --wallet $WALLET_PATH"
echo
echo "════════════════════════════════════════════════════════"
