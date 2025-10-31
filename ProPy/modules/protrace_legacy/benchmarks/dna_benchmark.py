#!/usr/bin/env python3
"""
DNA Merkle Tree Benchmark Script
================================

Computes 256-bit DNA hashes for images in Folder X and builds a virtual Merkle tree.
Benchmarks speed and accuracy, stores the tree locally.
"""

import os
import time
import json
from typing import List, Dict
from protrace.image_dna import compute_dna
from protrace.merkle import MerkleTree


def find_images(folder_path: str) -> List[str]:
    """Find all image files in the folder."""
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    images = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.lower().endswith(extensions):
                images.append(os.path.join(folder_path, file))
    return images


def compute_hashes(images: List[str]) -> List[str]:
    """Compute DNA hashes for all images."""
    hashes = []
    for img_path in images:
        try:
            dna = compute_dna(img_path)
            hashes.append(dna['dna_hex'])
            print(f"Computed DNA for {os.path.basename(img_path)}: {dna['dna_hex'][:16]}...")
        except Exception as e:
            print(f"Error computing DNA for {img_path}: {e}")
    return hashes


def build_merkle_tree(hashes: List[str]) -> MerkleTree:
    """Build Merkle tree from hashes."""
    merkle = MerkleTree()
    for i, h in enumerate(hashes):
        merkle.add_leaf(h, pointer=f'image_{i}', platform_id='benchmark', timestamp=0)
    return merkle


def save_merkle_tree(merkle: MerkleTree, filename: str):
    """Save Merkle tree to JSON file."""
    # Serialize leaves
    leaves_serialized = [leaf.hex() for leaf in merkle.leaves]

    # Serialize root if exists
    root_hex = merkle.root.hash.hex() if merkle.root else None

    # Note: Full tree serialization is complex, saving leaves and root hash
    data = {
        'leaves': leaves_serialized,
        'root_hash': root_hex,
        'leaf_count': len(merkle.leaves)
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def benchmark_accuracy(merkle: MerkleTree, hashes: List[str]) -> bool:
    """Basic accuracy check: verify root hash computation."""
    if not merkle.root:
        return True  # Empty tree is accurate

    from protrace.merkle import blake3_hash

    # Recompute root manually
    nodes = [blake3_hash(leaf) for leaf in merkle.leaves]
    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
            combined = blake3_hash(left + right)
            next_level.append(combined)
        nodes = next_level

    manual_root_hash = nodes[0].hex()
    tree_root_hash = merkle.root.hash.hex()
    return manual_root_hash == tree_root_hash


def main():
    folder = "Folder X"
    output_file = "merkle_tree.json"

    print("DNA Merkle Tree Benchmark")
    print("=" * 40)

    # Find images
    images = find_images(folder)
    print(f"Found {len(images)} images in {folder}")

    if not images:
        print("No images found. Exiting.")
        return

    # Compute hashes
    hash_start = time.time()
    hashes = compute_hashes(images)
    hash_time = time.time() - hash_start
    print(f"Hashing time: {hash_time:.4f} seconds")

    # Build Merkle tree
    build_start = time.time()
    merkle = build_merkle_tree(hashes)
    root_hash = merkle.build_tree()
    build_time = time.time() - build_start
    print(f"Merkle tree build time: {build_time:.4f} seconds")
    print(f"Root hash: {root_hash}")

    # Accuracy check
    accurate = benchmark_accuracy(merkle, hashes)
    print(f"Accuracy check: {'PASSED' if accurate else 'FAILED'}")

    # Save tree
    save_merkle_tree(merkle, output_file)
    print(f"Merkle tree saved to {output_file}")

    # Summary
    print("\nBenchmark Summary:")
    print(f"- Images processed: {len(images)}")
    print(f"- Total hashing time: {hash_time:.4f} s")
    print(f"- Merkle build time: {build_time:.4f} s")
    print(f"- Average hash time per image: {hash_time / len(images):.4f} s")
    print(f"- Accuracy: {'OK' if accurate else 'ERROR'}")


if __name__ == "__main__":
    main()
