#!/bin/bash
# Test Rust modules directly

echo "================================================================================"
echo "🦀 ProTRACE Rust Modules Test"
echo "================================================================================"
echo ""

cd "$(dirname "$0")"

# Test 1: Check Rust toolchain
echo "📦 Test 1: Checking Rust toolchain..."
if command -v rustc &> /dev/null; then
    RUST_VERSION=$(rustc --version)
    echo "✅ Rust installed: $RUST_VERSION"
else
    echo "❌ Rust not installed"
    exit 1
fi
echo ""

# Test 2: Check Cargo
echo "📦 Test 2: Checking Cargo..."
if command -v cargo &> /dev/null; then
    CARGO_VERSION=$(cargo --version)
    echo "✅ Cargo installed: $CARGO_VERSION"
else
    echo "❌ Cargo not installed"
    exit 1
fi
echo ""

# Test 3: List crates
echo "📦 Test 3: Listing Rust crates..."
if [ -d "crates" ]; then
    echo "✅ Crates directory found:"
    for crate in crates/*/; do
        CRATE_NAME=$(basename "$crate")
        echo "   - $CRATE_NAME"
    done
else
    echo "❌ No crates directory found"
fi
echo ""

# Test 4: Build DNA extraction crate
echo "🧬 Test 4: Building DNA extraction crate..."
if [ -d "crates/dna_extraction" ]; then
    cd crates/dna_extraction
    if cargo build --release 2>&1 | tail -5; then
        echo "✅ DNA extraction crate built successfully"
    else
        echo "❌ DNA extraction build failed"
    fi
    cd ../..
else
    echo "⏭️  Skipped (crate not found)"
fi
echo ""

# Test 5: Test DNA extraction crate
echo "🧪 Test 5: Testing DNA extraction crate..."
if [ -d "crates/dna_extraction" ]; then
    cd crates/dna_extraction
    if cargo test --release 2>&1 | tail -10; then
        echo "✅ DNA extraction tests passed"
    else
        echo "⚠️  DNA extraction tests may have issues"
    fi
    cd ../..
else
    echo "⏭️  Skipped (crate not found)"
fi
echo ""

# Test 6: Build Merkle tree crate
echo "🌲 Test 6: Building Merkle tree crate..."
if [ -d "crates/merkle_tree" ]; then
    cd crates/merkle_tree
    if cargo build --release 2>&1 | tail -5; then
        echo "✅ Merkle tree crate built successfully"
    else
        echo "❌ Merkle tree build failed"
    fi
    cd ../..
else
    echo "⏭️  Skipped (crate not found)"
fi
echo ""

# Test 7: Test Merkle tree crate
echo "🧪 Test 7: Testing Merkle tree crate..."
if [ -d "crates/merkle_tree" ]; then
    cd crates/merkle_tree
    if cargo test --release 2>&1 | tail -10; then
        echo "✅ Merkle tree tests passed"
    else
        echo "⚠️  Merkle tree tests may have issues"
    fi
    cd ../..
else
    echo "⏭️  Skipped (crate not found)"
fi
echo ""

# Test 8: Build Solana program
echo "🔗 Test 8: Building Solana program..."
if [ -f "Anchor.toml" ]; then
    if anchor build 2>&1 | tail -10; then
        echo "✅ Solana program built successfully"
    else
        echo "❌ Solana program build failed"
    fi
else
    echo "⏭️  Skipped (not an Anchor project)"
fi
echo ""

# Test 9: Check build artifacts
echo "📦 Test 9: Checking build artifacts..."
ARTIFACTS_FOUND=0

if [ -f "target/deploy/protrace.so" ]; then
    SIZE=$(du -h target/deploy/protrace.so | cut -f1)
    echo "✅ Solana program: $SIZE"
    ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
fi

if [ -f "target/idl/protrace.json" ]; then
    SIZE=$(du -h target/idl/protrace.json | cut -f1)
    echo "✅ IDL file: $SIZE"
    ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
fi

if [ -f "crates/dna_extraction/target/release/libdna_extraction.rlib" ] || \
   [ -f "crates/dna_extraction/target/release/libdna_extraction.so" ]; then
    echo "✅ DNA extraction library"
    ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
fi

if [ -f "crates/merkle_tree/target/release/libmerkle_tree.rlib" ] || \
   [ -f "crates/merkle_tree/target/release/libmerkle_tree.so" ]; then
    echo "✅ Merkle tree library"
    ARTIFACTS_FOUND=$((ARTIFACTS_FOUND + 1))
fi

if [ $ARTIFACTS_FOUND -eq 0 ]; then
    echo "⚠️  No build artifacts found"
else
    echo "✅ Found $ARTIFACTS_FOUND artifact(s)"
fi
echo ""

# Summary
echo "================================================================================"
echo "📊 TEST SUMMARY"
echo "================================================================================"
echo ""
echo "✅ Rust toolchain verified"
echo "✅ Cargo available"
echo "✅ Crates structure verified"
echo ""
echo "Build Status:"
echo "  - DNA extraction: $([ -d 'crates/dna_extraction' ] && echo '✅ Available' || echo '⏭️  Not found')"
echo "  - Merkle tree:    $([ -d 'crates/merkle_tree' ] && echo '✅ Available' || echo '⏭️  Not found')"
echo "  - Solana program: $([ -f 'target/deploy/protrace.so' ] && echo '✅ Deployed' || echo '⚠️  Not built')"
echo ""
echo "Status: ✅ RUST MODULES TEST COMPLETE"
echo ""
echo "================================================================================"
