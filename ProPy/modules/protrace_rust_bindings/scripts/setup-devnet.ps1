# ProTrace Devnet Setup Script for Windows
# PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "🔒 ProTrace Devnet Setup" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host ""

# Check if Solana CLI is installed
try {
    $solanaVersion = solana --version 2>$null
    Write-Host "✓ Solana CLI found" -ForegroundColor Green
    Write-Host "  $solanaVersion"
    Write-Host ""
} catch {
    Write-Host "✗ Solana CLI not found" -ForegroundColor Red
    Write-Host "Install from: https://docs.solana.com/cli/install-solana-cli-tools"
    exit 1
}

# Check if Anchor is installed (optional)
try {
    $anchorVersion = anchor --version 2>$null
    Write-Host "✓ Anchor found" -ForegroundColor Green
    Write-Host "  $anchorVersion"
} catch {
    Write-Host "⚠ Anchor not found (optional)" -ForegroundColor Yellow
    Write-Host "Install with: cargo install --git https://github.com/coral-xyz/anchor avm --locked --force"
}
Write-Host ""

# Configure Solana for devnet
Write-Host "📡 Configuring Solana for devnet..." -ForegroundColor Yellow
solana config set --url devnet
Write-Host "✓ Connected to devnet" -ForegroundColor Green
Write-Host ""

# Create wallet if it doesn't exist
$walletPath = "$env:USERPROFILE\.config\solana\protrace-devnet.json"
$walletDir = Split-Path -Parent $walletPath

if (Test-Path $walletPath) {
    Write-Host "⚠ Wallet already exists at: $walletPath" -ForegroundColor Yellow
    $response = Read-Host "Overwrite? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Using existing wallet"
    } else {
        solana-keygen new --outfile $walletPath --force
        Write-Host "✓ New wallet created" -ForegroundColor Green
    }
} else {
    Write-Host "🔑 Creating new wallet..." -ForegroundColor Yellow
    if (-not (Test-Path $walletDir)) {
        New-Item -ItemType Directory -Path $walletDir -Force | Out-Null
    }
    solana-keygen new --outfile $walletPath
    Write-Host "✓ Wallet created at: $walletPath" -ForegroundColor Green
}
Write-Host ""

# Set wallet
solana config set --keypair $walletPath
$pubkey = solana address
Write-Host "✓ Wallet configured" -ForegroundColor Green
Write-Host "  Public Key: $pubkey"
Write-Host ""

# Request airdrop
Write-Host "💰 Requesting airdrop..." -ForegroundColor Yellow
try {
    solana airdrop 2 $pubkey
    Write-Host "✓ Airdrop successful" -ForegroundColor Green
} catch {
    Write-Host "✗ Airdrop failed" -ForegroundColor Red
    Write-Host "You may need to wait or use a faucet: https://solfaucet.com/"
}
Write-Host ""

# Check balance
Write-Host "💵 Checking balance..." -ForegroundColor Yellow
$balance = solana balance
Write-Host "  Balance: $balance"
Write-Host ""

# Summary
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Wallet Path: $walletPath"
Write-Host "Public Key: $pubkey"
Write-Host "Balance: $balance"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Build ProTrace: cargo build --release"
Write-Host "  2. Install CLI: cargo install --path crates/cli"
Write-Host "  3. Run test: protrace test images/*.png --wallet $walletPath"
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor DarkGray
