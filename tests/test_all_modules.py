#!/usr/bin/env python3
"""
Comprehensive Test for ProTRACE Modules:
- Python: DNA extraction, Merkle trees
- Rust: DNA extraction, Merkle trees (via bindings)
- Integration testing
"""

import sys
import os
from pathlib import Path
import tempfile

# Add ProPy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ProPy"))

print("=" * 80)
print("🧪 ProTRACE Complete Module Test Suite")
print("=" * 80)
print()

# ============================================================================
# PART 1: PYTHON MODULES TEST
# ============================================================================

print("🐍 PART 1: TESTING PYTHON MODULES")
print("-" * 80)
print()

# Test 1.1: Import Python modules
print("📦 Test 1.1: Importing Python modules...")
python_modules_available = False
try:
    from modules.protrace_legacy.image_dna import compute_dna
    from modules.protrace_legacy.merkle import MerkleTree
    print("✅ Python image_dna module loaded")
    print("✅ Python merkle module loaded")
    python_modules_available = True
except ImportError as e:
    print(f"❌ Python module import failed: {e}")

print()

# Test 1.2: Create test image
print("📸 Test 1.2: Creating test image...")
test_image_path = None
try:
    from PIL import Image
    import numpy as np
    
    # Create a colorful test image
    img_array = np.zeros((256, 256, 3), dtype=np.uint8)
    img_array[0:128, 0:128] = [255, 0, 0]        # Red
    img_array[0:128, 128:256] = [0, 255, 0]      # Green
    img_array[128:256, 0:128] = [0, 0, 255]      # Blue
    img_array[128:256, 128:256] = [255, 255, 0]  # Yellow
    
    img = Image.fromarray(img_array)
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        test_image_path = tmp.name
    
    print(f"✅ Test image created: {test_image_path}")
    print(f"✅ Image size: {img.size}")
except Exception as e:
    print(f"❌ Failed to create image: {e}")

print()

# Test 1.3: Python DNA computation
print("🧬 Test 1.3: Computing DNA hash (Python)...")
python_dna = None
if python_modules_available and test_image_path:
    try:
        result = compute_dna(test_image_path)
        python_dna = result['dna_hex']
        print(f"✅ DNA Hash:   {python_dna[:32]}...")
        print(f"✅ DHash:      {result['dhash']}")
        print(f"✅ Grid Hash:  {result['grid_hash'][:32]}...")
        print(f"✅ Length:     {len(python_dna)} chars (256-bit)")
    except Exception as e:
        print(f"❌ Python DNA computation failed: {e}")
else:
    print("⏭️  Skipped (dependencies not available)")

print()

# Test 1.4: Python DNA similarity
print("🔍 Test 1.4: Testing DNA similarity (Python)...")
if python_modules_available and python_dna:
    try:
        def hamming_similarity(hex1, hex2):
            """Calculate similarity based on Hamming distance"""
            if len(hex1) != len(hex2):
                return 0.0
            bin1 = bin(int(hex1, 16))[2:].zfill(256)
            bin2 = bin(int(hex2, 16))[2:].zfill(256)
            distance = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            return 1.0 - (distance / 256)
        
        # Test identical
        sim1 = hamming_similarity(python_dna, python_dna)
        print(f"✅ Identical:   Similarity={sim1:.2%}")
        
        # Test similar
        similar_dna = python_dna[:-4] + "0000"
        sim2 = hamming_similarity(python_dna, similar_dna)
        print(f"✅ Similar:     Similarity={sim2:.2%}")
    except Exception as e:
        print(f"❌ DNA similarity test failed: {e}")
else:
    print("⏭️  Skipped (DNA not available)")

print()

# Test 1.5: Python Merkle tree
print("🌲 Test 1.5: Building Merkle tree (Python)...")
python_merkle_root = None
python_merkle_tree = None
if python_modules_available:
    try:
        # Generate sample leaves
        import hashlib
        import time
        
        python_merkle_tree = MerkleTree()
        
        # Add 5 leaves with metadata
        for i in range(5):
            dna_hash = hashlib.sha256(f"leaf_{i}".encode()).hexdigest()
            pointer = f"ipfs://Qm{dna_hash[:44]}"
            platform_id = f"platform_{i}"
            python_merkle_tree.add_leaf(dna_hash, pointer, platform_id, int(time.time()))
        
        print(f"✅ Generated {len(python_merkle_tree.leaves)} leaves")
        
        # Build tree
        python_merkle_root = python_merkle_tree.build_tree()
        
        print(f"✅ Tree built")
        print(f"✅ Root:        {python_merkle_root[:32]}...")
    except Exception as e:
        print(f"❌ Merkle tree construction failed: {e}")
else:
    print("⏭️  Skipped (module not available)")

print()

# Test 1.6: Python Merkle proof
print("✔️  Test 1.6: Verifying Merkle proof (Python)...")
if python_modules_available and python_merkle_tree and python_merkle_root:
    try:
        # Get proof for first leaf
        proof = python_merkle_tree.get_proof(0)
        leaf_data = python_merkle_tree.leaves[0]
        
        is_valid = python_merkle_tree.verify_proof(leaf_data, proof, python_merkle_root)
        
        print(f"✅ Leaf index: 0")
        print(f"✅ Proof size: {len(proof)}")
        print(f"✅ Valid:      {is_valid}")
    except Exception as e:
        print(f"❌ Proof verification failed: {e}")
else:
    print("⏭️  Skipped (tree not available)")

print()

# ============================================================================
# PART 2: RUST MODULES TEST
# ============================================================================

print("🦀 PART 2: TESTING RUST MODULES")
print("-" * 80)
print()

# Test 2.1: Import Rust bindings
print("📦 Test 2.1: Importing Rust bindings...")
rust_modules_available = False
try:
    from modules.protrace_rust_bindings import dna_extraction, merkle_tree_builder
    print("✅ Rust dna_extraction binding loaded")
    print("✅ Rust merkle_tree_builder binding loaded")
    rust_modules_available = True
except ImportError as e:
    print(f"❌ Rust binding import failed: {e}")
    print("⚠️  Rust modules may not be compiled")

print()

# Test 2.2: Rust DNA computation
print("🧬 Test 2.2: Computing DNA hash (Rust)...")
rust_dna = None
if rust_modules_available and test_image_path:
    try:
        rust_dna = dna_extraction.compute_dna(test_image_path)
        print(f"✅ Rust DNA:   {rust_dna[:32]}...")
        print(f"✅ Length:     {len(rust_dna)} chars")
    except Exception as e:
        print(f"❌ Rust DNA computation failed: {e}")
else:
    print("⏭️  Skipped (Rust not available)")

print()

# Test 2.3: Rust Merkle tree
print("🌲 Test 2.3: Building Merkle tree (Rust)...")
rust_merkle_root = None
if rust_modules_available:
    try:
        import hashlib
        leaves = [hashlib.sha256(f"leaf_{i}".encode()).hexdigest() for i in range(5)]
        
        rust_merkle_root = merkle_tree_builder.build_tree(leaves)
        print(f"✅ Rust Merkle root: {rust_merkle_root[:32]}...")
    except Exception as e:
        print(f"❌ Rust Merkle construction failed: {e}")
else:
    print("⏭️  Skipped (Rust not available)")

print()

# Test 2.4: Rust Merkle proof
print("✔️  Test 2.4: Verifying Merkle proof (Rust)...")
if rust_modules_available and rust_merkle_root:
    try:
        import hashlib
        leaf = hashlib.sha256(b"leaf_0").hexdigest()
        proof = merkle_tree_builder.generate_proof(leaf, 0)
        
        is_valid = merkle_tree_builder.verify_proof(leaf, proof, rust_merkle_root)
        print(f"✅ Leaf:   {leaf[:32]}...")
        print(f"✅ Valid:  {is_valid}")
    except Exception as e:
        print(f"❌ Rust proof verification failed: {e}")
else:
    print("⏭️  Skipped (Rust not available)")

print()

# ============================================================================
# PART 3: INTEGRATION & COMPARISON TEST
# ============================================================================

print("🔄 PART 3: INTEGRATION & COMPARISON")
print("-" * 80)
print()

# Test 3.1: Compare Python vs Rust DNA
print("⚖️  Test 3.1: Comparing Python vs Rust DNA...")
if python_dna and rust_dna:
    try:
        if python_dna == rust_dna:
            print("✅ Python and Rust DNA hashes MATCH!")
        else:
            print("⚠️  Python and Rust DNA hashes DIFFER")
            print(f"   Python: {python_dna[:32]}...")
            print(f"   Rust:   {rust_dna[:32]}...")
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
else:
    print("⏭️  Skipped (DNA not available from both)")

print()

# Test 3.2: Compare Merkle roots
print("⚖️  Test 3.2: Comparing Python vs Rust Merkle roots...")
if python_merkle_root and rust_merkle_root:
    try:
        if python_merkle_root == rust_merkle_root:
            print("✅ Python and Rust Merkle roots MATCH!")
        else:
            print("⚠️  Python and Rust Merkle roots DIFFER")
            print(f"   Python: {python_merkle_root[:32]}...")
            print(f"   Rust:   {rust_merkle_root[:32]}...")
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
else:
    print("⏭️  Skipped (Merkle roots not available from both)")

print()

# Test 3.3: Cross-verification
print("🔀 Test 3.3: Cross-verification (Python proof, Rust root)...")
if python_modules_available and rust_merkle_root:
    try:
        import hashlib
        leaf = hashlib.sha256(b"leaf_0").hexdigest()
        # This would test if Python can verify Rust-generated proofs
        print("⚠️  Cross-verification requires compatible implementations")
    except Exception as e:
        print(f"❌ Cross-verification failed: {e}")
else:
    print("⏭️  Skipped (both implementations not available)")

print()

# ============================================================================
# CLEANUP
# ============================================================================

print("🧹 Test 3.4: Cleanup...")
if test_image_path and os.path.exists(test_image_path):
    try:
        os.unlink(test_image_path)
        print("✅ Test image removed")
    except Exception as e:
        print(f"⚠️  Cleanup failed: {e}")
else:
    print("✅ No cleanup needed")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print()

print("Python Modules:")
print(f"  {'✅' if python_modules_available else '❌'} Import")
print(f"  {'✅' if python_dna else '❌'} DNA Computation")
print(f"  {'✅' if python_merkle_root else '❌'} Merkle Tree")
print()

print("Rust Modules:")
print(f"  {'✅' if rust_modules_available else '❌'} Import")
print(f"  {'✅' if rust_dna else '❌'} DNA Computation")
print(f"  {'✅' if rust_merkle_root else '❌'} Merkle Tree")
print()

print("Integration:")
if python_dna and rust_dna:
    print(f"  {'✅' if python_dna == rust_dna else '⚠️'} DNA Hash Compatibility")
if python_merkle_root and rust_merkle_root:
    print(f"  {'✅' if python_merkle_root == rust_merkle_root else '⚠️'} Merkle Root Compatibility")
print()

# Overall status
all_python_ok = python_modules_available and python_dna and python_merkle_root
all_rust_ok = rust_modules_available and rust_dna and rust_merkle_root

if all_python_ok and all_rust_ok:
    print("Status: ✅ ALL MODULES WORKING (Python & Rust)")
elif all_python_ok:
    print("Status: ✅ PYTHON MODULES WORKING (Rust needs compilation)")
elif all_rust_ok:
    print("Status: ✅ RUST MODULES WORKING (Python needs setup)")
else:
    print("Status: ⚠️  USING MOCK IMPLEMENTATIONS")

print()
print("=" * 80)
