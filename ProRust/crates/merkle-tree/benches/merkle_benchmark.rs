use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use protrace_merkle::MerkleTree;

fn bench_tree_build(c: &mut Criterion) {
    let mut group = c.benchmark_group("merkle_tree_build");
    
    for size in [10, 100, 1000, 10000].iter() {
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, &size| {
            b.iter(|| {
                let mut tree = MerkleTree::new();
                
                for i in 0..size {
                    tree.add_leaf(
                        &format!("{:064x}", i),
                        &format!("ipfs://Qm{:044x}", i),
                        "platform",
                        1234567890
                    );
                }
                
                black_box(tree.build_tree().unwrap());
            });
        });
    }
    
    group.finish();
}

fn bench_proof_generation(c: &mut Criterion) {
    let mut tree = MerkleTree::new();
    
    for i in 0..1000 {
        tree.add_leaf(
            &format!("{:064x}", i),
            &format!("ipfs://Qm{:044x}", i),
            "platform",
            1234567890
        );
    }
    
    tree.build_tree().unwrap();
    
    c.bench_function("proof_generation", |b| {
        b.iter(|| {
            black_box(tree.get_proof(500).unwrap());
        });
    });
}

fn bench_proof_verification(c: &mut Criterion) {
    let mut tree = MerkleTree::new();
    
    for i in 0..1000 {
        tree.add_leaf(
            &format!("{:064x}", i),
            &format!("ipfs://Qm{:044x}", i),
            "platform",
            1234567890
        );
    }
    
    let root = tree.build_tree().unwrap();
    let proof = tree.get_proof(500).unwrap();
    
    c.bench_function("proof_verification", |b| {
        b.iter(|| {
            black_box(tree.verify_proof(500, &proof, &root).unwrap());
        });
    });
}

criterion_group!(benches, bench_tree_build, bench_proof_generation, bench_proof_verification);
criterion_main!(benches);
