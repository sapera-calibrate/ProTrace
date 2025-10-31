//! Basic usage examples for ProTrace

use protrace_image_dna::{compute_dna, extract_dna_features, hamming_distance, is_duplicate};
use protrace_merkle_tree::MerkleTree;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔒 ProTrace - Basic Usage Examples\n");

    // Example 1: Compute DNA for an image
    example_compute_dna()?;

    // Example 2: Compare two images
    example_compare_images()?;

    // Example 3: Build Merkle tree
    example_merkle_tree()?;

    Ok(())
}

fn example_compute_dna() -> Result<(), Box<dyn std::error::Error>> {
    println!("📌 Example 1: Compute DNA Hash");
    println!("{}", "─".repeat(50));

    // Note: Replace with actual image path
    let image_path = "test_image.png";
    
    // This will fail if file doesn't exist, which is expected in example
    match compute_dna(image_path) {
        Ok(dna) => {
            println!("✅ DNA Hash: {}", dna.dna_hex);
            println!("   Algorithm: {}", dna.algorithm);
            println!("   Bits: {}", dna.bits);
            println!("   dHash: {}", dna.dhash);
            println!("   Grid Hash: {}", dna.grid_hash);
        }
        Err(_) => {
            println!("⚠️  Image file not found (expected in example)");
            println!("   Use your own image: protrace dna compute <image.png>");
        }
    }

    println!();
    Ok(())
}

fn example_compare_images() -> Result<(), Box<dyn std::error::Error>> {
    println!("📌 Example 2: Compare Images");
    println!("{}", "─".repeat(50));

    // Mock DNA hashes for demonstration
    let hash1 = "a1b2c3d4e5f6789012345678901234567890abcdef123456789abcdef0123456";
    let hash2 = "a1b2c3d4e5f6789012345678901234567890abcdef123456789abcdef0123456";

    let distance = hamming_distance(hash1, hash2)?;
    let similarity = 1.0 - (distance as f64 / 256.0);
    let is_dup = is_duplicate(hash1, hash2, 26)?;

    println!("Hash 1: {}", hash1);
    println!("Hash 2: {}", hash2);
    println!();
    println!("Hamming Distance: {}", distance);
    println!("Similarity: {:.2}%", similarity * 100.0);
    println!("Is Duplicate: {}", if is_dup { "YES" } else { "NO" });

    println!();
    Ok(())
}

fn example_merkle_tree() -> Result<(), Box<dyn std::error::Error>> {
    println!("📌 Example 3: Build Merkle Tree");
    println!("{}", "─".repeat(50));

    let mut tree = MerkleTree::new();

    // Add sample leaves
    println!("Adding leaves to tree...");
    tree.add_leaf(
        "abc123def456",
        "uuid:550e8400-opensea-eth",
        "opensea",
        Some(1698765432),
    );
    tree.add_leaf(
        "def456ghi789",
        "uuid:660e9500-foundation-eth",
        "foundation",
        Some(1698765433),
    );
    tree.add_leaf(
        "ghi789jkl012",
        "uuid:770ea600-magiceden-sol",
        "magiceden",
        Some(1698765434),
    );

    println!("  ✓ Added 3 leaves");
    println!();

    // Build tree
    println!("Building Merkle tree...");
    let root = tree.build_tree()?;
    println!("  ✓ Tree built successfully");
    println!("  Root: {}", root);
    println!("  Leaves: {}", tree.leaf_count());
    println!();

    // Generate proof
    println!("Generating proof for leaf 0...");
    let proof = tree.get_proof(0)?;
    println!("  ✓ Proof generated");
    println!("  Proof elements: {}", proof.len());
    for (i, element) in proof.iter().enumerate() {
        println!("    [{}] {} ({:?})", i, &element.hash[..16], element.position);
    }
    println!();

    // Verify proof
    println!("Verifying proof...");
    let leaf_data = b"abc123def456|uuid:550e8400-opensea-eth|opensea|1698765432";
    let is_valid = tree.verify_proof(leaf_data, &proof, &root)?;
    println!("  ✓ Proof verification: {}", if is_valid { "VALID ✅" } else { "INVALID ❌" });

    println!();
    Ok(())
}
