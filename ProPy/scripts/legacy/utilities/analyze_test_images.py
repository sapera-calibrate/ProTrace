#!/usr/bin/env python3
"""
ProTRACE Test Images DNA Hash Analysis
======================================

Generate DNA hashes for test images, compare them, and build Merkle tree
"""

import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from protrace.image_dna import compute_dna, dna_similarity, hamming_distance
from protrace.merkle import MerkleTree, compute_leaf_hash

print("=" * 80)
print("🧬 ProTRACE - DNA Hash Analysis for Test Images")
print("=" * 80)

# Configuration
TEST_IMAGES_DIR = Path("data/test_images")
OUTPUT_DIR = Path("data/analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Step 1: Generate DNA Hashes
print("\n[STEP 1] Generating DNA Hashes for All Images")
print("-" * 80)

image_files = sorted(list(TEST_IMAGES_DIR.glob("*.png")))
print(f"Found {len(image_files)} PNG images\n")

dna_results = {}
processing_times = []

for idx, image_path in enumerate(image_files, 1):
    print(f"[{idx}/{len(image_files)}] Processing: {image_path.name}")
    
    start_time = time.time()
    try:
        dna_result = compute_dna(str(image_path))
        elapsed = time.time() - start_time
        processing_times.append(elapsed)
        
        dna_results[image_path.name] = {
            'file': image_path.name,
            'dna_hex': dna_result['dna_hex'],
            'dna_binary': dna_result.get('dna_binary', ''),
            'processing_time_ms': elapsed * 1000,
            'file_size_bytes': image_path.stat().st_size,
            'timestamp': int(time.time())
        }
        
        print(f"   ✅ DNA Hash: {dna_result['dna_hex'][:32]}...")
        print(f"   ⏱️  Time: {elapsed*1000:.2f}ms")
        print(f"   📦 Size: {image_path.stat().st_size:,} bytes\n")
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        dna_results[image_path.name] = {
            'file': image_path.name,
            'error': str(e)
        }

# Statistics
avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
print(f"📊 Processing Statistics:")
print(f"   Total images: {len(image_files)}")
print(f"   Successful: {len([r for r in dna_results.values() if 'dna_hex' in r])}")
print(f"   Average time: {avg_time*1000:.2f}ms per image")
print(f"   Throughput: {1/avg_time:.1f} images/second\n")

# Step 2: Direct Hash Comparison
print("\n[STEP 2] Direct DNA Hash Comparison")
print("-" * 80)

successful_results = {k: v for k, v in dna_results.items() if 'dna_hex' in v}
image_names = list(successful_results.keys())
comparison_matrix = {}

print(f"Comparing {len(image_names)} images (pairwise comparison)\n")

for i, img1 in enumerate(image_names):
    comparison_matrix[img1] = {}
    for j, img2 in enumerate(image_names):
        if i <= j:
            dna1 = successful_results[img1]['dna_hex']
            dna2 = successful_results[img2]['dna_hex']
            
            similarity = dna_similarity(dna1, dna2)
            hamming_dist = hamming_distance(dna1, dna2)
            
            comparison_matrix[img1][img2] = {
                'similarity_percentage': similarity * 100,
                'hamming_distance': hamming_dist,
                'match_type': 'identical' if similarity == 1.0 else 
                             'very_similar' if similarity >= 0.95 else
                             'similar' if similarity >= 0.85 else
                             'different'
            }

# Display comparison results
print("Similarity Matrix (showing high similarities):")
print("-" * 80)
for img1 in image_names:
    for img2 in image_names:
        if img1 in comparison_matrix and img2 in comparison_matrix[img1]:
            comp = comparison_matrix[img1][img2]
            if comp['similarity_percentage'] >= 85.0 and img1 != img2:
                print(f"   {img1} ↔️ {img2}")
                print(f"      Similarity: {comp['similarity_percentage']:.2f}%")
                print(f"      Hamming Distance: {comp['hamming_distance']} bits")
                print(f"      Type: {comp['match_type']}")
                print()

# Find potential duplicates (>90% similarity)
print("\n🔍 Potential Duplicates Detection (>90% similarity):")
print("-" * 80)
duplicates_found = False
for img1 in image_names:
    for img2 in image_names:
        if img1 < img2:  # Avoid duplicate comparisons
            if img1 in comparison_matrix and img2 in comparison_matrix[img1]:
                comp = comparison_matrix[img1][img2]
                if comp['similarity_percentage'] > 90.0:
                    duplicates_found = True
                    print(f"⚠️  DUPLICATE DETECTED:")
                    print(f"   {img1} ≈ {img2}")
                    print(f"   Similarity: {comp['similarity_percentage']:.2f}%")
                    print(f"   Hamming Distance: {comp['hamming_distance']} bits\n")

if not duplicates_found:
    print("✅ No duplicates found - all images are unique!\n")

# Step 3: Merkle Tree Implementation
print("\n[STEP 3] Building Merkle Tree with DNA Hashes")
print("-" * 80)

merkle_tree = MerkleTree()
current_time = int(time.time())

print("Adding DNA hashes as leaves to Merkle tree...\n")

for idx, (image_name, data) in enumerate(successful_results.items(), 1):
    if 'dna_hex' in data:
        # Create unique token ID for each image
        token_id = f"IMG_{idx:03d}"
        
        # Add to Merkle tree
        merkle_tree.add_leaf(
            dna_hex=data['dna_hex'],
            pointer=token_id,
            platform_id="ProTRACE_Test",
            timestamp=current_time + idx
        )
        
        print(f"   [{idx}] Added: {image_name}")
        print(f"       Token ID: {token_id}")
        print(f"       DNA Hash: {data['dna_hex'][:32]}...")

# Build the tree
print(f"\n🌳 Building Merkle tree with {len(merkle_tree.leaves)} leaves...")
start_time = time.time()
root_hash = merkle_tree.build_tree()
build_time = time.time() - start_time

print(f"   ✅ Tree built in {build_time*1000:.2f}ms")
print(f"   🌲 Root Hash: {root_hash[:64] if isinstance(root_hash, str) else root_hash.hex()[:64]}...")
print(f"   📊 Tree Height: ~{len(merkle_tree.leaves).bit_length()} levels")

# Generate proofs for each image
print("\n[STEP 4] Generating Merkle Proofs")
print("-" * 80)

proofs = {}
for idx in range(len(merkle_tree.leaves)):
    try:
        proof = merkle_tree.get_proof(idx)
        leaf_data = merkle_tree.leaves[idx]
        image_name = image_names[idx] if idx < len(image_names) else f"Image_{idx}"
        
        # Handle different proof formats
        proof_elements = []
        for p in proof:
            if isinstance(p, str):
                proof_elements.append(p)
            elif isinstance(p, bytes):
                proof_elements.append(p.hex())
            elif isinstance(p, dict):
                proof_elements.append(str(p))
            else:
                proof_elements.append(str(p))
        
        proofs[image_name] = {
            'leaf_index': idx,
            'token_id': f"IMG_{idx+1:03d}",
            'proof_length': len(proof),
            'proof_elements': proof_elements
        }
        
        print(f"   ✅ Proof for {image_name}: {len(proof)} elements")
    except Exception as e:
        print(f"   ⚠️  Proof generation for index {idx}: {str(e)[:50]}")

# Export Merkle manifest
print("\n[STEP 5] Exporting Merkle Manifest")
print("-" * 80)

try:
    manifest = merkle_tree.export_manifest()
    manifest_file = OUTPUT_DIR / f"merkle_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   ✅ Manifest exported: {manifest_file}")
    print(f"   📦 Manifest size: {manifest_file.stat().st_size:,} bytes")
except Exception as e:
    print(f"   ⚠️  Manifest export: {e}")

# Step 6: Save Complete Analysis Report
print("\n[STEP 6] Saving Analysis Report")
print("-" * 80)

report = {
    'analysis_timestamp': datetime.now().isoformat(),
    'total_images': len(image_files),
    'successful_hashes': len(successful_results),
    'processing_stats': {
        'average_time_ms': avg_time * 1000,
        'throughput_per_second': 1 / avg_time if avg_time > 0 else 0,
        'total_time_ms': sum(processing_times) * 1000
    },
    'dna_hashes': dna_results,
    'comparison_matrix': comparison_matrix,
    'merkle_tree': {
        'root_hash': root_hash if isinstance(root_hash, str) else root_hash.hex(),
        'total_leaves': len(merkle_tree.leaves),
        'build_time_ms': build_time * 1000,
        'tree_height': len(merkle_tree.leaves).bit_length()
    },
    'merkle_proofs': proofs
}

report_file = OUTPUT_DIR / f"dna_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"   ✅ Full report saved: {report_file}")
print(f"   📦 Report size: {report_file.stat().st_size:,} bytes")

# Step 7: Generate Human-Readable Summary
print("\n[STEP 7] Generating Human-Readable Summary")
print("-" * 80)

summary_file = OUTPUT_DIR / f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ProTRACE - DNA Hash Analysis Summary\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total Images Analyzed: {len(image_files)}\n")
    f.write(f"Successful DNA Hashes: {len(successful_results)}\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("DNA HASHES\n")
    f.write("=" * 80 + "\n\n")
    
    for image_name, data in successful_results.items():
        f.write(f"Image: {image_name}\n")
        f.write(f"  DNA Hash: {data['dna_hex']}\n")
        f.write(f"  Processing Time: {data['processing_time_ms']:.2f}ms\n")
        f.write(f"  File Size: {data['file_size_bytes']:,} bytes\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("MERKLE TREE INFORMATION\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Root Hash: {root_hash if isinstance(root_hash, str) else root_hash.hex()}\n")
    f.write(f"Total Leaves: {len(merkle_tree.leaves)}\n")
    f.write(f"Build Time: {build_time*1000:.2f}ms\n")
    f.write(f"Tree Height: {len(merkle_tree.leaves).bit_length()} levels\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("COMPARISON RESULTS\n")
    f.write("=" * 80 + "\n\n")
    
    duplicate_count = 0
    for img1 in image_names:
        for img2 in image_names:
            if img1 < img2 and img1 in comparison_matrix and img2 in comparison_matrix[img1]:
                comp = comparison_matrix[img1][img2]
                if comp['similarity_percentage'] > 90.0:
                    duplicate_count += 1
                    f.write(f"Potential Duplicate Pair {duplicate_count}:\n")
                    f.write(f"  {img1} <-> {img2}\n")
                    f.write(f"  Similarity: {comp['similarity_percentage']:.2f}%\n")
                    f.write(f"  Hamming Distance: {comp['hamming_distance']} bits\n\n")
    
    if duplicate_count == 0:
        f.write("No duplicates found - all images are unique!\n\n")

print(f"   ✅ Summary saved: {summary_file}")

# Final Summary
print("\n" + "=" * 80)
print("📊 ANALYSIS COMPLETE")
print("=" * 80)
print(f"\n✅ Successfully analyzed {len(successful_results)}/{len(image_files)} images")
print(f"✅ Generated {len(successful_results)} DNA hashes")
print(f"✅ Built Merkle tree with {len(merkle_tree.leaves)} leaves")
print(f"✅ Generated {len(proofs)} Merkle proofs")
print(f"\n📁 Output Files:")
print(f"   - Analysis Report (JSON): {report_file.name}")
print(f"   - Summary (TXT): {summary_file.name}")
print(f"   - Merkle Manifest (JSON): merkle_manifest_*.json")
print(f"\n📂 All files saved to: {OUTPUT_DIR}")
print("\n" + "=" * 80)
print("🎉 DNA Hash Analysis Complete!")
print("=" * 80)
