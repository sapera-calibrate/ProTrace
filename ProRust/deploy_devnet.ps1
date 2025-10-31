# ProTRACE Solana Devnet Deployment Script (Windows PowerShell)
# Run this from Windows to deploy to Solana devnet via WSL

Write-Host "=================================================="
Write-Host "🚀 ProTRACE Solana Devnet Deployment"
Write-Host "=================================================="
Write-Host ""

# Step 1: Copy files to WSL
Write-Host "📦 Step 1: Copying files to WSL home directory..."
wsl bash -c "cp -r /mnt/d/ProTRACE\ -\ Copy\ -\ Copy/ProTRACE/ProRust ~/ProRust-deploy"
Write-Host "✅ Files copied to ~/ProRust-deploy"
Write-Host ""

# Step 2: Set Rust version
Write-Host "🦀 Step 2: Setting Rust version to 1.82.0..."
wsl bash -c "cd ~/ProRust-deploy && rustup install 1.82.0 && rustup default 1.82.0"
$rustVersion = wsl bash -c "rustc --version"
Write-Host "✅ Rust version: $rustVersion"
Write-Host ""

# Step 3: Clean build
Write-Host "🔨 Step 3: Building Solana program..."
wsl bash -c "cd ~/ProRust-deploy && rm -rf target/ .anchor/ Cargo.lock && anchor build"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!"
} else {
    Write-Host "❌ Build failed! Check errors above."
    exit 1
}
Write-Host ""

# Step 4: Check wallet balance
Write-Host "💰 Step 4: Checking wallet balance..."
$balance = wsl bash -c "solana balance --url devnet"
Write-Host "Current balance: $balance"

if ($balance -match "^0") {
    Write-Host "⚠️  Low balance, requesting airdrop..."
    wsl bash -c "solana airdrop 2 --url devnet"
    Start-Sleep -Seconds 30
    $newBalance = wsl bash -c "solana balance --url devnet"
    Write-Host "✅ New balance: $newBalance"
}
Write-Host ""

# Step 5: Deploy to devnet
Write-Host "🚀 Step 5: Deploying to Solana devnet..."
wsl bash -c "cd ~/ProRust-deploy && anchor deploy --provider.cluster devnet"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!"
} else {
    Write-Host "❌ Deployment failed! Check errors above."
    exit 1
}
Write-Host ""

# Step 6: Get program ID
Write-Host "🔍 Step 6: Verifying deployment..."
$programId = wsl bash -c "cd ~/ProRust-deploy && solana address -k target/deploy/protrace-keypair.json"
Write-Host "Program ID: $programId"
Write-Host ""

# Step 7: Verify on-chain
Write-Host "✅ Step 7: Checking program on-chain..."
wsl bash -c "solana program show $programId --url devnet"
Write-Host ""

Write-Host "=================================================="
Write-Host "✅ Deployment Complete!"
Write-Host "=================================================="
Write-Host ""
Write-Host "📊 Summary:"
Write-Host "  - Program ID: $programId"
Write-Host "  - Network: Devnet"
Write-Host "  - Explorer: https://explorer.solana.com/address/$programId?cluster=devnet"
Write-Host ""
Write-Host "🎯 Next Steps:"
Write-Host "  1. Update Anchor.toml with Program ID"
Write-Host "  2. Update TestSprite config"
Write-Host "  3. Run integration tests"
Write-Host ""
