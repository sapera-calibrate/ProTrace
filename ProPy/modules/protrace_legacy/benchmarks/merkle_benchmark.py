#!/usr/bin/env python3
"""
Merkle Tree Performance Benchmark
==================================

Comprehensive benchmarking of ProTrace Merkle tree:
- Search/lookup performance
- Memory usage
- Construction time
- Proof generation/verification
- Storage space
- Scalability analysis
"""

import os
import time
import json
import psutil
import tracemalloc
from protrace.image_dna import compute_dna
from protrace.merkle import MerkleTree
from typing import List, Dict, Any
import gc


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage."""
    process = psutil.Process(os.getpid())
    return {
        'rss_mb': process.memory_info().rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': process.memory_info().vms / 1024 / 1024,  # Virtual Memory Size
    }


def benchmark_construction(images: List[str], registry_file: str = "merkle_tree.json") -> Dict[str, Any]:
    """Benchmark Merkle tree construction."""
    print("🔧 Benchmarking Merkle Tree Construction...")

    # Start memory and time tracking
    tracemalloc.start()
    start_time = time.time()
    start_mem = get_memory_usage()

    # Load existing hashes for duplicate checking
    existing_hashes = set()
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            data = json.load(f)
        for leaf_hex in data['leaves']:
            leaf_bytes = bytes.fromhex(leaf_hex)
            leaf_str = leaf_bytes.decode('utf-8')
            dna_hex = leaf_str.split('|')[0]
            existing_hashes.add(dna_hex)

    # Create new Merkle tree
    merkle = MerkleTree()
    processed = 0
    accepted = 0
    rejected = 0

    construction_start = time.time()

    for img_path in images:
        try:
            # Compute DNA
            dna_result = compute_dna(img_path)
            dna_hex = dna_result['dna_hex']

            # Check for duplicates
            if dna_hex in existing_hashes:
                rejected += 1
            else:
                # Add to tree
                timestamp = int(time.time())
                merkle.add_leaf(dna_hex, pointer=os.path.basename(img_path),
                              platform_id='benchmark', timestamp=timestamp)
                existing_hashes.add(dna_hex)
                accepted += 1

            processed += 1

            # Progress update
            if processed % 100 == 0:
                print(f"  Processed {processed}/{len(images)} images...")

        except Exception as e:
            print(f"  Error processing {img_path}: {e}")

    # Build the tree
    tree_build_start = time.time()
    root_hash = merkle.build_tree()
    tree_build_time = time.time() - tree_build_start

    # Save the tree
    save_start = time.time()
    leaves_serialized = [leaf.hex() for leaf in merkle.leaves]
    root_hex = merkle.root.hash.hex() if merkle.root else None
    data = {
        'leaves': leaves_serialized,
        'root_hash': root_hex,
        'leaf_count': len(merkle.leaves)
    }
    with open(registry_file, 'w') as f:
        json.dump(data, f, indent=2)
    save_time = time.time() - save_start

    # End tracking
    total_time = time.time() - start_time
    end_mem = get_memory_usage()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'total_images': len(images),
        'processed': processed,
        'accepted': accepted,
        'rejected': rejected,
        'tree_size': len(merkle.leaves),
        'total_time': total_time,
        'computation_time': construction_start - start_time,
        'tree_build_time': tree_build_time,
        'save_time': save_time,
        'memory_start_mb': start_mem['rss_mb'],
        'memory_end_mb': end_mem['rss_mb'],
        'memory_peak_mb': peak / 1024 / 1024,
        'root_hash': root_hash
    }


def benchmark_search(registry_file: str = "merkle_tree.json", test_hashes: List[str] = None) -> Dict[str, Any]:
    """Benchmark search/lookup performance."""
    print("🔍 Benchmarking Search Performance...")

    # Load registry
    if not os.path.exists(registry_file):
        return {'error': 'Registry file not found'}

    with open(registry_file, 'r') as f:
        data = json.load(f)

    registry_size = len(data['leaves'])

    # Extract all hashes from registry
    registry_hashes = set()
    for leaf_hex in data['leaves']:
        leaf_bytes = bytes.fromhex(leaf_hex)
        leaf_str = leaf_bytes.decode('utf-8')
        dna_hex = leaf_str.split('|')[0]
        registry_hashes.add(dna_hex)

    # Generate test hashes if not provided
    if test_hashes is None:
        # Use some existing hashes and some random ones
        existing_sample = list(registry_hashes)[:100]  # Sample of existing
        # Generate some fake hashes for misses
        fake_hashes = [f"{i:064x}" for i in range(100)]
        test_hashes = existing_sample + fake_hashes

    # Benchmark searches
    tracemalloc.start()
    start_time = time.time()

    hits = 0
    misses = 0
    search_times = []

    for test_hash in test_hashes:
        search_start = time.perf_counter()
        found = test_hash in registry_hashes
        search_time = time.perf_counter() - search_start
        search_times.append(search_time)

        if found:
            hits += 1
        else:
            misses += 1

    total_search_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    avg_search_time = sum(search_times) / len(search_times) if search_times else 0
    min_search_time = min(search_times) if search_times else 0
    max_search_time = max(search_times) if search_times else 0

    return {
        'registry_size': registry_size,
        'test_queries': len(test_hashes),
        'hits': hits,
        'misses': misses,
        'total_search_time': total_search_time,
        'avg_search_time_us': avg_search_time * 1_000_000,
        'min_search_time_us': min_search_time * 1_000_000,
        'max_search_time_us': max_search_time * 1_000_000,
        'searches_per_second': len(test_hashes) / total_search_time if total_search_time > 0 else 0,
        'memory_peak_mb': peak / 1024 / 1024
    }


def benchmark_proof_operations(registry_file: str = "merkle_tree.json") -> Dict[str, Any]:
    """Benchmark Merkle proof generation and verification."""
    print("📋 Benchmarking Merkle Proof Operations...")

    # Load registry and reconstruct tree
    if not os.path.exists(registry_file):
        return {'error': 'Registry file not found'}

    with open(registry_file, 'r') as f:
        data = json.load(f)

    # Reconstruct Merkle tree
    merkle = MerkleTree()
    for leaf_hex in data['leaves']:
        leaf_bytes = bytes.fromhex(leaf_hex)
        merkle.leaves.append(leaf_bytes)

    if merkle.leaves:
        merkle.build_tree()

    if not merkle.root:
        return {'error': 'Could not build tree'}

    # Test proof generation for random leaves
    import random
    test_indices = random.sample(range(len(merkle.leaves)), min(50, len(merkle.leaves)))

    proof_gen_times = []
    proof_verify_times = []

    tracemalloc.start()
    start_time = time.time()

    for idx in test_indices:
        # Generate proof
        proof_start = time.perf_counter()
        proof = merkle.get_proof(idx)
        proof_gen_time = time.perf_counter() - proof_start
        proof_gen_times.append(proof_gen_time)

        # Verify proof
        leaf_data = merkle.leaves[idx]
        verify_start = time.perf_counter()
        is_valid = merkle.verify_proof(leaf_data, proof, merkle.root.hash.hex())
        verify_time = time.perf_counter() - verify_start
        proof_verify_times.append(verify_time)

        if not is_valid:
            print(f"  WARNING: Proof verification failed for index {idx}")

    total_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'tree_size': len(merkle.leaves),
        'proofs_tested': len(test_indices),
        'avg_proof_gen_time_us': (sum(proof_gen_times) / len(proof_gen_times)) * 1_000_000,
        'avg_proof_verify_time_us': (sum(proof_verify_times) / len(proof_verify_times)) * 1_000_000,
        'total_time': total_time,
        'memory_peak_mb': peak / 1024 / 1024
    }


def benchmark_storage(registry_file: str = "merkle_tree.json") -> Dict[str, Any]:
    """Benchmark storage space and efficiency."""
    print("💾 Benchmarking Storage Space...")

    if not os.path.exists(registry_file):
        return {'error': 'Registry file not found'}

    # File size
    file_size_bytes = os.path.getsize(registry_file)
    file_size_mb = file_size_bytes / 1024 / 1024

    # Load and analyze content
    with open(registry_file, 'r') as f:
        data = json.load(f)

    num_leaves = len(data['leaves'])

    # Calculate space efficiency
    total_hash_bytes = 32 * num_leaves  # 32 bytes per BLAKE3 hash
    total_pointer_overhead = sum(len(leaf.split('|')[1]) + len(leaf.split('|')[2]) + len(leaf.split('|')[3])
                                for leaf in [bytes.fromhex(h).decode('utf-8') for h in data['leaves']])
    total_metadata_bytes = len(json.dumps(data, indent=2).encode('utf-8')) - total_hash_bytes - total_pointer_overhead

    return {
        'file_size_mb': file_size_mb,
        'file_size_kb': file_size_bytes / 1024,
        'num_leaves': num_leaves,
        'bytes_per_leaf': file_size_bytes / num_leaves if num_leaves > 0 else 0,
        'hash_storage_bytes': total_hash_bytes,
        'metadata_overhead_bytes': total_metadata_bytes,
        'pointer_overhead_bytes': total_pointer_overhead,
        'storage_efficiency': total_hash_bytes / file_size_bytes if file_size_bytes > 0 else 0
    }


def run_full_benchmark():
    """Run comprehensive benchmark suite."""
    print("=" * 60)
    print("ProTrace Merkle Tree Performance Benchmark")
    print("=" * 60)

    # Get test images (use existing Folder X)
    folder = "Folder X"
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    images = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(extensions):
                images.append(os.path.join(folder, f))

    print(f"📊 Test Dataset: {len(images)} images from {folder}")
    print()

    # Benchmark 1: Construction
    construct_results = benchmark_construction(images)
    print("✅ Construction Results:")
    print(f"   Images processed: {construct_results['processed']}")
    print(f"   Accepted/Rejected: {construct_results['accepted']}/{construct_results['rejected']}")
    print(f"   Total time: {construct_results['total_time']:.3f}s")
    print(f"   Tree build time: {construct_results['tree_build_time']:.3f}s")
    print(f"   Memory peak: {construct_results['memory_peak_mb']:.1f} MB")
    print()

    # Benchmark 2: Search Performance
    search_results = benchmark_search()
    print("✅ Search Results:")
    print(f"   Registry size: {search_results['registry_size']}")
    print(f"   Test queries: {search_results['test_queries']}")
    print(f"   Hit rate: {search_results['hits']/search_results['test_queries']*100:.1f}%")
    print(f"   Avg search time: {search_results['avg_search_time_us']:.2f} μs")
    print(f"   Searches/sec: {search_results['searches_per_second']:.0f}")
    print()

    # Benchmark 3: Proof Operations
    proof_results = benchmark_proof_operations()
    print("✅ Proof Operations:")
    print(f"   Proofs tested: {proof_results['proofs_tested']}")
    print(f"   Avg proof generation: {proof_results['avg_proof_gen_time_us']:.2f} μs")
    print(f"   Avg proof verification: {proof_results['avg_proof_verify_time_us']:.2f} μs")
    print()

    # Benchmark 4: Storage
    storage_results = benchmark_storage()
    print("✅ Storage Analysis:")
    print(f"   Registry file size: {storage_results['file_size_mb']:.2f} MB")
    print(f"   Bytes per leaf: {storage_results['bytes_per_leaf']:.0f}")
    print(f"   Storage efficiency: {storage_results['storage_efficiency']*100:.1f}%")
    print()

    # Summary
    print("🎯 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Dataset Size: {len(images)} images")
    print(f"Registry Size: {storage_results['num_leaves']} entries")
    print()
    print("Timing (per operation):")
    print(f"  • DNA Computation: ~{(construct_results['computation_time']/len(images))*1000:.1f} ms")
    print(f"  • Hash Lookup: ~{search_results['avg_search_time_us']:.1f} μs")
    print(f"  • Proof Generation: ~{proof_results['avg_proof_gen_time_us']:.1f} μs")
    print()
    print("Scalability:")
    print(f"  • Storage: {storage_results['file_size_mb']:.2f} MB for {storage_results['num_leaves']} entries")
    print(f"  • Memory Peak: {max(construct_results['memory_peak_mb'], search_results['memory_peak_mb'], proof_results['memory_peak_mb']):.1f} MB")
    print(f"  • Search Throughput: {search_results['searches_per_second']:.0f} queries/sec")
    print()
    print("✅ Benchmark completed successfully!")


if __name__ == "__main__":
    run_full_benchmark()
