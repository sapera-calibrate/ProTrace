# ProTRACE - Push Clean Code to GitHub
# This script will replace everything in your GitHub repo with the new clean code

Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ProTRACE - Push to GitHub" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Initialize Git (if not already)
Write-Host "Step 1: Checking Git initialization..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    git init
} else {
    Write-Host "Git repository already initialized." -ForegroundColor Green
}

# Step 2: Add your GitHub remote (update URL)
Write-Host "`nStep 2: Setting up GitHub remote..." -ForegroundColor Yellow
Write-Host "Current remotes:" -ForegroundColor Gray
git remote -v

Write-Host "`nEnter your GitHub repository URL:" -ForegroundColor Cyan
Write-Host "Example: https://github.com/username/ProTRACE.git" -ForegroundColor Gray
$repoUrl = Read-Host "Repository URL"

# Remove existing origin if it exists
git remote remove origin 2>$null

# Add new origin
Write-Host "Adding remote origin: $repoUrl" -ForegroundColor Green
git remote add origin $repoUrl

# Step 3: Create .gitignore
Write-Host "`nStep 3: Creating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
*.egg-info/
dist/
build/

# Rust
target/
Cargo.lock
**/*.rs.bk

# Anchor
.anchor/
test-ledger/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Backups
backup_old_docs/

# Logs
*.log
npm-debug.log*

# Environment
.env
.env.local
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host ".gitignore created successfully" -ForegroundColor Green

# Step 4: Stage all files
Write-Host "`nStep 4: Staging all files..." -ForegroundColor Yellow
git add .
Write-Host "Files staged:" -ForegroundColor Green
git status --short

# Step 5: Commit
Write-Host "`nStep 5: Creating commit..." -ForegroundColor Yellow
$commitMessage = "feat: complete repository reorganization and enhancement

- Unified README files (main, ProPy, ProRust)
- Organized all test files into tests/ directory
- Moved documentation to docs/ directory
- Enhanced main README with comprehensive information
- Added architecture diagrams and technical specifications
- Cleaned up root directory (only essential files)
- Added security.txt integration
- Complete Python-Rust parity achieved
- Deployed to Solana Devnet
- Production-ready codebase

Program ID: 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG
Status: Production Ready on Devnet
Version: 1.0.0"

git commit -m $commitMessage
Write-Host "Commit created successfully" -ForegroundColor Green

# Step 6: Push to GitHub
Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Red
Write-Host "  WARNING: This will REPLACE all content" -ForegroundColor Red
Write-Host "  in your GitHub repository!" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""
Write-Host "Do you want to continue? (yes/no): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host

if ($confirm -eq "yes") {
    Write-Host "`nStep 6: Pushing to GitHub (force push)..." -ForegroundColor Yellow
    
    # Set main branch
    git branch -M main
    
    # Force push to replace everything
    Write-Host "Force pushing to origin main..." -ForegroundColor Green
    git push -u origin main --force
    
    Write-Host "`n" -NoNewline
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Code pushed to GitHub" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository has been updated with the clean code!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Visit your GitHub repository" -ForegroundColor Gray
    Write-Host "2. Verify the files look correct" -ForegroundColor Gray
    Write-Host "3. Update repository description and topics" -ForegroundColor Gray
    Write-Host "4. Enable GitHub Pages (optional)" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "`nPush cancelled. No changes made to GitHub." -ForegroundColor Yellow
}

Write-Host "Done!" -ForegroundColor Cyan
Write-Host ""
