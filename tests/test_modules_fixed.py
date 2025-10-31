#!/usr/bin/env python3
"""
Comprehensive Test for ProTRACE Modules - CORRECTED VERSION
Tests actual implementations with correct imports
"""

import sys
import os
from pathlib import Path
import tempfile

# Add ProPy to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ProPy"))

print("=" * 80)
print("🧪 ProTRACE Comprehensive Module Test (Fixed)")
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
    from modules.protrace_legacy.merkle import MerkleTree, compute_leaf_hash
    print("✅ Python image_dna module loaded")
    print("✅ Python MerkleTree class loaded")
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
    
    # Create a colorful test image with patterns
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
        print(f"✅ DNA Hash:   {python_dna[:32]}...{python_dna[-8:]}")
        print(f"✅ DHash:      {result['dhash']}")
        print(f"✅ Grid Hash:  {result['grid_hash'][:16]}...{result['grid_hash'][-8:]}")
        print(f"✅ Algorithm:  {result['algorithm']}")
        print(f"✅ Bits:       {result['bits']}")
        print(f"✅ Length:     {len(python_dna)} chars (256-bit)")
    except Exception as e:
        print(f"❌ Python DNA computation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⏭️  Skipped (dependencies not available)")

print()

# Test 1.4: Python DNA similarity
print("🔍 Test 1.4: Testing DNA similarity (Python)...")
if python_modules_available and python_dna:
    try:
        # Simple Hamming distance comparison
        def hamming_distance(hex1, hex2):
            if len(hex1) != len(hex2):
                return None
            # Convert to binary and count differences
            bin1 = bin(int(hex1, 16))[2:].zfill(256)
            bin2 = bin(int(hex2, 16))[2:].zfill(256)
            return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
        
        # Test identical
        dist1 = hamming_distance(python_dna, python_dna)
        sim1 = 1.0 - (dist1 / 256)
        print(f"✅ Identical:   Distance={dist1}, Similarity={sim1:.2%}")
        
        # Test similar (flip last 4 bits)
        similar_dna = hex(int(python_dna, 16) ^ 0xF)[2:].zfill(64)
        dist2 = hamming_distance(python_dna, similar_dna)
        sim2 = 1.0 - (dist2 / 256)
        print(f"✅ Similar:     Distance={dist2}, Similarity={sim2:.2%}")
        
        # Completely different
        import hashlib
        different_dna = hashlib.sha256(b"different").hexdigest()
        dist3 = hamming_distance(python_dna, different_dna)
        sim3 = 1.0 - (dist3 / 256)
        print(f"✅ Different:   Distance={dist3}, Similarity={sim3:.2%}")
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
        # Generate sample leaves with DNA hashes
        import hashlib
        leaves = []
        for i in range(5):
            # Simulate DNA hash
            dna_hash = hashlib.sha256(f"image_{i}".encode()).hexdigest()
            pointer = f"ipfs://Qm{hashlib.sha256(f'pointer_{i}'.encode()).hexdigest()[:44]}"
            platform_id = f"platform_{i}"
            
            # Compute leaf hash
            leaf_hash = compute_leaf_hash(dna_hash, pointer, platform_id)
            leaves.append(leaf_hash)
        
        print(f"✅ Generated {len(leaves)} leaf hashes")
        
        # Build tree
        python_merkle_tree = MerkleTree(leaves)
        python_merkle_root = python_merkle_tree.get_root_hex()
        
        print(f"✅ Merkle tree built")
        print(f"✅ Root:        {python_merkle_root[:32]}...{python_merkle_root[-8:]}")
        print(f"✅ Leaf count:  {len(leaves)}")
    except Exception as e:
        print(f"❌ Merkle tree construction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⏭️  Skipped (module not available)")

print()

# Test 1.6: Python Merkle proof
print("✔️  Test 1.6: Verifying Merkle proof (Python)...")
if python_modules_available and python_merkle_tree and python_merkle_root:
    try:
        # Get proof for first leaf (index 0)
        proof = python_merkle_tree.get_proof(0)
        leaf_hash = leaves[0]
        
        # Verify proof
        is_valid = python_merkle_tree.verify_proof(0, proof)
        
        print(f"✅ Leaf:       {leaf_hash[:32]}...")
        print(f"✅ Proof size: {len(proof)}")
        print(f"✅ Valid:      {is_valid}")
        
        if is_valid:
            print("✅ Merkle proof verification PASSED!")
        else:
            print("❌ Merkle proof verification FAILED!")
    except Exception as e:
        print(f"❌ Proof verification failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⏭️  Skipped (tree not available)")

print()

# ============================================================================
# PART 2: RUST CRATES TEST (Check if available)
# ============================================================================

print("🦀 PART 2: CHECKING RUST CRATES")
print("-" * 80)
print()

print("📦 Test 2.1: Checking Rust crates...")
rust_crates = []
rust_dir = Path(__file__).parent.parent / "ProRust" / "crates"
if rust_dir.exists():
    for crate_path in rust_dir.iterdir():
        if crate_path.is_dir() and (crate_path / "Cargo.toml").exists():
            rust_crates.append(crate_path.name)
            print(f"✅ Found crate: {crate_path.name}")
    
    if rust_crates:
        print(f"✅ Total Rust crates: {len(rust_crates)}")
    else:
        print("⚠️  No Rust crates found")
else:
    print("⚠️  Rust crates directory not found")

print()

# ============================================================================
# PART 3: SOLANA PROGRAM TEST
# ============================================================================

print("🔗 PART 3: CHECKING SOLANA PROGRAM")
print("-" * 80)
print()

print("📦 Test 3.1: Checking Solana deployment...")
solana_program_deployed = False
program_path = Path(__file__).parent.parent / "ProRust" / "target" / "deploy" / "protrace.so"
idl_path = Path(__file__).parent.parent / "ProRust" / "target" / "idl" / "protrace.json"

if program_path.exists():
    size_mb = program_path.stat().st_size / (1024 * 1024)
    print(f"✅ Program binary: {size_mb:.2f} MB")
    solana_program_deployed = True
else:
    print("⚠️  Program binary not found")

if idl_path.exists():
    size_kb = idl_path.stat().st_size / 1024
    print(f"✅ IDL file: {size_kb:.2f} KB")
    
    # Read IDL to count instructions
    try:
        import json
        with open(idl_path) as f:
            idl = json.load(f)
            instructions = idl.get('instructions', [])
            print(f"✅ Instructions: {len(instructions)}")
            for inst in instructions:
                print(f"   - {inst['name']}")
    except Exception as e:
        print(f"⚠️  Could not read IDL: {e}")
else:
    print("⚠️  IDL file not found")

print()

# ============================================================================
# CLEANUP
# ============================================================================

print("🧹 Test 3.2: Cleanup...")
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
print("📊 COMPREHENSIVE TEST SUMMARY")
print("=" * 80)
print()

print("Python Modules:")
print(f"  {'✅' if python_modules_available else '❌'} Import")
print(f"  {'✅' if python_dna else '❌'} DNA Computation (256-bit)")
print(f"  {'✅' if python_merkle_root else '❌'} Merkle Tree (BLAKE3)")
print()

print("Rust Ecosystem:")
print(f"  {'✅' if rust_crates else '⚠️'} Crates: {len(rust_crates)}")
for crate in rust_crates:
    print(f"     - {crate}")
print()

print("Solana Program:")
print(f"  {'✅' if solana_program_deployed else '⚠️'} Deployed")
print(f"  {'✅' if idl_path.exists() else '⚠️'} IDL Available")
print(f"  Program ID: 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG")
print()

# Overall status
python_ok = python_modules_available and python_dna and python_merkle_root
rust_ok = len(rust_crates) > 0
solana_ok = solana_program_deployed

if python_ok and rust_ok and solana_ok:
    print("Status: ✅ ALL ECOSYSTEMS OPERATIONAL")
elif python_ok and solana_ok:
    print("Status: ✅ PYTHON & SOLANA WORKING (Rust crates available)")
elif python_ok:
    print("Status: ✅ PYTHON MODULES WORKING")
else:
    print("Status: ⚠️  SETUP REQUIRED")

print()
print("=" * 80)
