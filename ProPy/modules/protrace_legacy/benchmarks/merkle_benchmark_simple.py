#!/usr/bin/env python3
"""
Merkle Tree Performance Benchmark
==================================

Comprehensive benchmarking of ProTrace Merkle tree performance.
"""

import os
import time
import json
import psutil
from protrace.image_dna import compute_dna
from protrace.merkle import MerkleTree


def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def benchmark_dna_computation(images):
    """Benchmark DNA hash computation."""
    print("🧬 Benchmarking DNA Computation...")

    start_time = time.time()
    start_mem = get_memory_usage()

    hashes = []
    for i, img_path in enumerate(images):
        dna_result = compute_dna(img_path)
        hashes.append(dna_result['dna_hex'])

        if (i + 1) % 100 == 0:
            print(f"  Computed {i+1}/{len(images)} hashes...")

    end_time = time.time()
    end_mem = get_memory_usage()

    return {
        'images_processed': len(images),
        'total_time': end_time - start_time,
        'time_per_image': (end_time - start_time) / len(images),
        'hashes_per_second': len(images) / (end_time - start_time),
        'memory_used_mb': end_mem - start_mem,
        'hashes': hashes
    }


def benchmark_tree_construction(hashes):
    """Benchmark Merkle tree construction."""
    print("🌳 Benchmarking Merkle Tree Construction...")

    start_time = time.time()
    start_mem = get_memory_usage()

    merkle = MerkleTree()
    for i, dna_hex in enumerate(hashes):
        merkle.add_leaf(dna_hex, pointer=f'image_{i}', platform_id='benchmark', timestamp=0)

    build_start = time.time()
    root_hash = merkle.build_tree()
    build_time = time.time() - build_start

    end_time = time.time()
    end_mem = get_memory_usage()

    return {
        'leaves_added': len(hashes),
        'total_time': end_time - start_time,
        'build_time': build_time,
        'time_per_leaf': build_time / len(hashes),
        'memory_used_mb': end_mem - start_mem,
        'root_hash': root_hash,
        'tree': merkle
    }


def benchmark_search_performance(hashes, registry_set):
    """Benchmark hash lookup performance."""
    print("🔍 Benchmarking Search Performance...")

    # Test with existing hashes (should find) and fake hashes (should miss)
    test_hashes = hashes[:100] + [f"{i:064x}" for i in range(100)]

    start_time = time.time()
    hits = 0
    misses = 0

    for test_hash in test_hashes:
        if test_hash in registry_set:
            hits += 1
        else:
            misses += 1

    total_time = time.time() - start_time

    return {
        'test_queries': len(test_hashes),
        'hits': hits,
        'misses': misses,
        'total_time': total_time,
        'time_per_query_us': (total_time / len(test_hashes)) * 1_000_000,
        'queries_per_second': len(test_hashes) / total_time
    }


def benchmark_proof_operations(merkle_tree):
    """Benchmark Merkle proof generation and verification."""
    print("📋 Benchmarking Merkle Proof Operations...")

    if not merkle_tree.root:
        return {'error': 'No tree built'}

    import random
    test_indices = random.sample(range(len(merkle_tree.leaves)),
                               min(50, len(merkle_tree.leaves)))

    start_time = time.time()
    proof_times = []
    verify_times = []

    for idx in test_indices:
        # Generate proof
        proof_start = time.perf_counter()
        proof = merkle_tree.get_proof(idx)
        proof_times.append(time.perf_counter() - proof_start)

        # Verify proof
        leaf_data = merkle_tree.leaves[idx]
        verify_start = time.perf_counter()
        is_valid = merkle_tree.verify_proof(leaf_data, proof, merkle_tree.root.hash.hex())
        verify_times.append(time.perf_counter() - verify_start)

        if not is_valid:
            print(f"  WARNING: Invalid proof for index {idx}")

    total_time = time.time() - start_time

    return {
        'proofs_tested': len(test_indices),
        'avg_proof_gen_us': (sum(proof_times) / len(proof_times)) * 1_000_000,
        'avg_proof_verify_us': (sum(verify_times) / len(verify_times)) * 1_000_000,
        'total_time': total_time
    }


def benchmark_storage(merkle_tree, filename="benchmark_registry.json"):
    """Benchmark storage requirements."""
    print("💾 Benchmarking Storage...")

    # Serialize tree
    leaves_serialized = [leaf.hex() for leaf in merkle_tree.leaves]
    root_hex = merkle_tree.root.hash.hex() if merkle_tree.root else None

    data = {
        'leaves': leaves_serialized,
        'root_hash': root_hex,
        'leaf_count': len(merkle_tree.leaves)
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    # Get file size
    file_size_bytes = os.path.getsize(filename)
    file_size_mb = file_size_bytes / 1024 / 1024

    return {
        'file_size_mb': file_size_mb,
        'file_size_kb': file_size_bytes / 1024,
        'leaves_stored': len(merkle_tree.leaves),
        'bytes_per_leaf': file_size_bytes / len(merkle_tree.leaves),
        'json_size_mb': len(json.dumps(data, indent=2)) / 1024 / 1024
    }


def run_benchmark():
    """Run complete benchmark suite."""
    print("=" * 60)
    print("ProTrace Merkle Tree Performance Benchmark")
    print("=" * 60)

    # Get test dataset
    folder = "Folder X"
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    images = []

    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.lower().endswith(extensions):
                images.append(os.path.join(folder, f))

    print(f"📊 Test Dataset: {len(images)} images")
    print()

    # 1. DNA Computation Benchmark
    dna_results = benchmark_dna_computation(images)
    print("✅ DNA Computation:")
    print(f"   Images: {dna_results['images_processed']}")
    print(f"   Total time: {dna_results['total_time']:.2f}s")
    print(f"   Time per image: {dna_results['time_per_image']*1000:.1f}ms")
    print(f"   Hashes/sec: {dna_results['hashes_per_second']:.1f}")
    print(f"   Memory used: {dna_results['memory_used_mb']:.1f} MB")
    print()

    # 2. Tree Construction Benchmark
    construct_results = benchmark_tree_construction(dna_results['hashes'])
    print("✅ Tree Construction:")
    print(f"   Leaves: {construct_results['leaves_added']}")
    print(f"   Build time: {construct_results['build_time']:.4f}s")
    print(f"   Time per leaf: {construct_results['time_per_leaf']*1000:.2f}ms")
    print(f"   Memory used: {construct_results['memory_used_mb']:.1f} MB")
    print(f"   Root: {construct_results['root_hash'][:32]}...")
    print()

    # 3. Search Benchmark
    registry_set = set(dna_results['hashes'])  # All hashes are in registry
    search_results = benchmark_search_performance(dna_results['hashes'], registry_set)
    print("✅ Search Performance:")
    print(f"   Test queries: {search_results['test_queries']}")
    print(f"   Hit rate: {search_results['hits']/search_results['test_queries']*100:.1f}%")
    print(f"   Total time: {search_results['total_time']:.4f}s")
    print(f"   Time per query: {search_results['time_per_query_us']:.2f}μs")
    print(f"   Queries/sec: {search_results['queries_per_second']:.0f}")
    print()

    # 4. Proof Operations Benchmark
    proof_results = benchmark_proof_operations(construct_results['tree'])
    if 'error' not in proof_results:
        print("✅ Proof Operations:")
        print(f"   Proofs tested: {proof_results['proofs_tested']}")
        print(f"   Avg generation: {proof_results['avg_proof_gen_us']:.2f}μs")
        print(f"   Avg verification: {proof_results['avg_proof_verify_us']:.2f}μs")
        print()

    # 5. Storage Benchmark
    storage_results = benchmark_storage(construct_results['tree'])
    print("✅ Storage Analysis:")
    print(f"   File size: {storage_results['file_size_mb']:.2f} MB")
    print(f"   Bytes per leaf: {storage_results['bytes_per_leaf']:.0f}")
    print(f"   JSON overhead: {storage_results['json_size_mb']:.2f} MB")
    print()

    # Performance Summary
    print("🎯 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Dataset: {len(images)} images → {len(dna_results['hashes'])} unique hashes")
    print()
    print("Timing (average per operation):")
    print(f"  • DNA Hash: {dna_results['time_per_image']*1000:.1f} ms")
    print(f"  • Tree insertion: {construct_results['time_per_leaf']*1000:.2f} ms")
    print(f"  • Hash lookup: {search_results['time_per_query_us']:.2f} μs")
    if 'avg_proof_gen_us' in proof_results:
        print(f"  • Proof generation: {proof_results['avg_proof_gen_us']:.1f} μs")
    print()
    print("Throughput:")
    print(f"  • Hash computation: {dna_results['hashes_per_second']:.1f} images/sec")
    print(f"  • Search queries: {search_results['queries_per_second']:.0f} queries/sec")
    print()
    print("Resource Usage:")
    print(f"  • Peak memory: {max(dna_results['memory_used_mb'], construct_results['memory_used_mb']):.1f} MB")
    print(f"  • Storage: {storage_results['file_size_mb']:.2f} MB ({storage_results['bytes_per_leaf']:.0f} bytes/leaf)")
    print()
    print("Scalability: Excellent - O(1) search, O(log n) proofs, O(n) storage")
    print("=" * 60)


if __name__ == "__main__":
    run_benchmark()
