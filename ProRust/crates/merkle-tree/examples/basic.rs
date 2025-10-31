//! Basic Merkle tree example

use protrace_merkle::MerkleTree;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("=== ProTrace Merkle Tree Example ===\n");

    // Create tree
    let mut tree = MerkleTree::new();
    println!("✅ Created empty Merkle tree");

    // Add 5 leaves
    println!("\n📝 Adding leaves...");
    for i in 0..5 {
        let dna_hash = format!("{:064x}", i);  // Simulate 256-bit DNA hash
        let pointer = format!("ipfs://Qm{:044x}", i);
        let platform = format!("platform_{}", i);
        let timestamp = 1234567890 + i as u64;

        tree.add_leaf(&dna_hash, &pointer, &platform, timestamp);
        println!("   Added leaf {}: DNA={}", i, &dna_hash[..16]);
    }

    println!("\n🌲 Building Merkle tree...");
    let root = tree.build_tree()?;
    println!("✅ Tree built successfully");
    println!("   Root: {}...{}", &root[..16], &root[root.len()-8..]);
    println!("   Leaves: {}", tree.leaf_count());

    // Generate proof for first leaf
    println!("\n🔍 Generating proof for leaf 0...");
    let proof = tree.get_proof(0)?;
    println!("✅ Proof generated");
    println!("   Proof elements: {}", proof.len());
    
    for (i, element) in proof.iter().enumerate() {
        println!("   Element {}: {} ({})", i, &element.hash[..16], element.position);
    }

    // Verify proof
    println!("\n✔️  Verifying proof...");
    let is_valid = tree.verify_proof(0, &proof, &root)?;
    
    if is_valid {
        println!("✅ Proof VALID!");
    } else {
        println!("❌ Proof INVALID!");
    }

    // Verify all leaves
    println!("\n✔️  Verifying all leaves...");
    for i in 0..tree.leaf_count() {
        let proof = tree.get_proof(i)?;
        let is_valid = tree.verify_proof(i, &proof, &root)?;
        
        if is_valid {
            println!("   Leaf {}: ✅ Valid", i);
        } else {
            println!("   Leaf {}: ❌ Invalid", i);
        }
    }

    println!("\n🎉 All operations completed successfully!");

    Ok(())
}
