#!/usr/bin/env python3
"""
Debug script to check perceptual hash issues
"""

import json
from SSC.FlamelFusion import calculate_fuzzy_match, compute_perceptual_hash

# Load registry
with open('V_on_chain/registry.json', 'r') as f:
    registry = json.load(f)

# Get the perceptual hashes
dna_hash = None
mind_hash = None

for entry in registry.values():
    if entry['filename'] == 'DNA-extraction.png':
        dna_hash = entry['perceptual_hash']
    elif entry['filename'] == 'mind-games.png':
        mind_hash = entry['perceptual_hash']

print(f"DNA perceptual hash: {dna_hash}")
print(f"Mind perceptual hash: {mind_hash}")

# Check if they start with ISCC:
print(f"DNA starts with ISCC: {dna_hash.startswith('ISCC:')}")
print(f"Mind starts with ISCC: {mind_hash.startswith('ISCC:')}")

# Try fuzzy matching
try:
    similarity = calculate_fuzzy_match(dna_hash, mind_hash)
    print(f"Fuzzy match result: {similarity}%")
except Exception as e:
    print(f"Fuzzy match error: {e}")

# Check what happens if we strip the ISCC prefix
if dna_hash.startswith('ISCC:') and mind_hash.startswith('ISCC:'):
    dna_clean = dna_hash[5:]  # Remove "ISCC:"
    mind_clean = mind_hash[5:]

    print(f"DNA clean hash: {dna_clean}")
    print(f"Mind clean hash: {mind_clean}")

    try:
        similarity_clean = calculate_fuzzy_match(dna_clean, mind_clean)
        print(f"Fuzzy match on clean hashes: {similarity_clean}%")
    except Exception as e:
        print(f"Clean fuzzy match error: {e}")

# Also test direct perceptual hash computation
print("\nDirect perceptual hash computation:")
dna_img = "V_off_chain/DNA-extraction.png"
mind_img = "V_off_chain/mind-games.png"

try:
    dna_phash = compute_perceptual_hash(dna_img)
    mind_phash = compute_perceptual_hash(mind_img)

    print(f"DNA computed phash: {dna_phash}")
    print(f"Mind computed phash: {mind_phash}")
    print(f"Match: {dna_phash == mind_phash}")

    similarity_computed = calculate_fuzzy_match(dna_phash, mind_phash)
    print(f"Similarity of computed hashes: {similarity_computed}%")

except Exception as e:
    print(f"Direct computation error: {e}")
