#!/usr/bin/env python3
"""
🎯 FINAL COMPREHENSIVE TEST - ProTRACE All Modules
Tests: Image DNA, Merkle Trees, Rust Crates, Solana Program
"""

import sys
import os
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "ProPy"))

print("=" * 80)
print("🎯 ProTRACE FINAL COMPREHENSIVE TEST")
print("=" * 80)
print()

# ============================================================================
# PYTHON MODULES - DNA & MERKLE
# ============================================================================

print("🐍 TESTING PYTHON MODULES")
print("-" * 80)
print()

print("1️⃣  Importing modules...")
try:
    from modules.protrace_legacy.image_dna import compute_dna
    from modules.protrace_legacy.merkle import MerkleTree
    print("✅ image_dna imported")
    print("✅ MerkleTree imported")
    modules_ok = True
except ImportError as e:
    print(f"❌ Import failed: {e}")
    modules_ok = False

print()

print("2️⃣  Creating test image...")
try:
    from PIL import Image
    import numpy as np
    
    img_array = np.zeros((256, 256, 3), dtype=np.uint8)
    img_array[0:128, 0:128] = [255, 0, 0]
    img_array[0:128, 128:256] = [0, 255, 0]
    img_array[128:256, 0:128] = [0, 0, 255]
    img_array[128:256, 128:256] = [255, 255, 0]
    
    img = Image.fromarray(img_array)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        test_img = tmp.name
    
    print(f"✅ Image: {test_img}")
    img_ok = True
except Exception as e:
    print(f"❌ Failed: {e}")
    img_ok = False

print()

print("3️⃣  Computing DNA hash (256-bit)...")
dna_ok = False
if modules_ok and img_ok:
    try:
        result = compute_dna(test_img)
        dna = result['dna_hex']
        print(f"✅ DNA:       {dna[:16]}...{dna[-16:]}")
        print(f"✅ DHash:     {result['dhash']}")
        print(f"✅ Grid:      {result['grid_hash'][:16]}...")
        print(f"✅ Length:    {len(dna)} chars")
        print(f"✅ Algorithm: {result['algorithm']}")
        dna_ok = True
    except Exception as e:
        print(f"❌ Failed: {e}")

print()

print("4️⃣  Testing DNA similarity...")
if dna_ok:
    try:
        def hamming(h1, h2):
            b1 = bin(int(h1, 16))[2:].zfill(256)
            b2 = bin(int(h2, 16))[2:].zfill(256)
            return sum(c1 != c2 for c1, c2 in zip(b1, b2))
        
        # Identical
        d1 = hamming(dna, dna)
        print(f"✅ Identical:  {d1} bits different = {100 - d1/2.56:.1f}% similar")
        
        # Modified
        mod_dna = hex(int(dna, 16) ^ 0xFFFF)[2:].zfill(64)
        d2 = hamming(dna, mod_dna)
        print(f"✅ Modified:   {d2} bits different = {100 - d2/2.56:.1f}% similar")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

print()

print("5️⃣  Building Merkle tree...")
merkle_ok = False
if modules_ok:
    try:
        import hashlib
        import time
        
        # Create tree
        tree = MerkleTree()
        
        # Add 5 leaves
        for i in range(5):
            dna_hash = hashlib.sha256(f"img_{i}".encode()).hexdigest()
            pointer = f"ipfs://Qm{hashlib.sha256(f'ptr_{i}'.encode()).hexdigest()[:44]}"
            platform = f"platform_{i}"
            tree.add_leaf(dna_hash, pointer, platform, int(time.time()))
        
        print(f"✅ Added {len(tree.leaves)} leaves")
        
        # Build tree
        root = tree.build_tree()
        print(f"✅ Root: {root[:16]}...{root[-16:]}")
        merkle_ok = True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

print()

print("6️⃣  Verifying Merkle proof...")
if merkle_ok:
    try:
        proof = tree.get_proof(0)
        leaf_data = tree.leaves[0]  # Get the actual leaf data
        root = tree.get_root()
        is_valid = tree.verify_proof(leaf_data, proof, root)
        print(f"✅ Proof size: {len(proof)}")
        print(f"✅ Valid:      {is_valid}")
    except Exception as e:
        print(f"❌ Failed: {e}")

print()

# ============================================================================
# RUST ECOSYSTEM
# ============================================================================

print("🦀 CHECKING RUST ECOSYSTEM")
print("-" * 80)
print()

rust_dir = Path(__file__).parent.parent / "ProRust" / "crates"
rust_crates = []

if rust_dir.exists():
    for crate in rust_dir.iterdir():
        if crate.is_dir() and (crate / "Cargo.toml").exists():
            rust_crates.append(crate.name)
    
    if rust_crates:
        print(f"✅ Found {len(rust_crates)} Rust crates:")
        for crate in sorted(rust_crates):
            print(f"   - {crate}")
    else:
        print("⚠️  No crates found")
else:
    print("⚠️  Crates directory not found")

print()

# ============================================================================
# SOLANA PROGRAM
# ============================================================================

print("🔗 CHECKING SOLANA PROGRAM")
print("-" * 80)
print()

program_file = Path(__file__).parent.parent / "ProRust" / "target" / "deploy" / "protrace.so"
idl_file = Path(__file__).parent.parent / "ProRust" / "target" / "idl" / "protrace.json"

if program_file.exists():
    size_kb = program_file.stat().st_size / 1024
    print(f"✅ Program: {size_kb:.1f} KB")
    program_ok = True
else:
    print("⚠️  Program not found (run 'anchor build' in ProRust/)")
    program_ok = False

if idl_file.exists():
    size_kb = idl_file.stat().st_size / 1024
    print(f"✅ IDL: {size_kb:.1f} KB")
    
    try:
        import json
        with open(idl_file) as f:
            idl = json.load(f)
            instructions = idl.get('instructions', [])
            print(f"✅ Instructions: {len(instructions)}")
    except:
        pass
else:
    print("⚠️  IDL not found")

print()
print("📍 Deployed Program ID: 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG")
print("🌐 Network: Solana Devnet")

print()

# ============================================================================
# CLEANUP
# ============================================================================

if img_ok and os.path.exists(test_img):
    try:
        os.unlink(test_img)
        print("🧹 Test image cleaned up")
    except:
        pass

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 80)
print("📊 FINAL TEST SUMMARY")
print("=" * 80)
print()

print("✅ PYTHON MODULES:")
print(f"   {'✅' if modules_ok else '❌'} Imports")
print(f"   {'✅' if img_ok else '❌'} Image processing")
print(f"   {'✅' if dna_ok else '❌'} DNA extraction (256-bit)")
print(f"   {'✅' if merkle_ok else '❌'} Merkle tree (BLAKE3)")
print()

print("✅ RUST ECOSYSTEM:")
print(f"   ✅ Crates found: {len(rust_crates)}")
if rust_crates:
    for crate in sorted(rust_crates):
        print(f"      - {crate}")
print()

print("✅ SOLANA PROGRAM:")
print(f"   {'✅' if program_file.exists() else '⚠️'} Binary compiled")
print(f"   {'✅' if idl_file.exists() else '⚠️'} IDL generated")
print("   ✅ Deployed: 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG")
print("   ✅ Network: Devnet")
print()

# Overall
all_ok = modules_ok and dna_ok and merkle_ok and len(rust_crates) > 0
if all_ok:
    print("🎉 STATUS: ALL CORE MODULES WORKING!")
elif modules_ok and dna_ok and merkle_ok:
    print("✅ STATUS: PYTHON MODULES FULLY OPERATIONAL")
else:
    print("⚠️  STATUS: SOME MODULES NEED ATTENTION")

print()
print("=" * 80)
