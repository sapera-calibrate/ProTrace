#!/usr/bin/env python3
import json
from SSC.FlamelFusion import calculate_fuzzy_match, verify_images
import os

# Load registry
with open('V_on_chain/registry.json', 'r') as f:
    registry = json.load(f)

# Find entries
dna_entry = None
mind_entry = None

for key, entry in registry.items():
    if entry['filename'] == 'DNA-extraction.png':
        dna_entry = entry
    elif entry['filename'] == 'mind-games.png':
        mind_entry = entry

print('🔍 Detailed Comparison:')
print(f'DNA-extraction.png:')
print(f'  Size: {dna_entry["size"]:,} bytes')
print(f'  ISCC: {dna_entry["perceptual_hash"]}')
print(f'  Blake3: {dna_entry["asset_hash"][:32]}...')

print(f'\nmind-games.png:')
print(f'  Size: {mind_entry["size"]:,} bytes')
print(f'  ISCC: {mind_entry["perceptual_hash"]}')
print(f'  Blake3: {mind_entry["asset_hash"][:32]}...')

# Check similarity
similarity = calculate_fuzzy_match(dna_entry['perceptual_hash'], mind_entry['perceptual_hash'])
print(f'\n📊 Perceptual Hash Similarity: {similarity:.2f}%')

# Full verification if images exist
dna_path = f"V_off_chain/{dna_entry['filename']}"
mind_path = f"V_off_chain/{mind_entry['filename']}"

if os.path.exists(dna_path) and os.path.exists(mind_path):
    print('\n🔬 Running full verification...')
    result = verify_images(dna_path, mind_path)
    print(f'Classification: {result["classification"]}')
    print(f'Fuzzy match: {result["fuzzy_match_percent"]:.2f}%')
    print(f'Manipulation: {result["manipulation_percent"]:.2f}%')
else:
    print('❌ Images not found for full verification')
