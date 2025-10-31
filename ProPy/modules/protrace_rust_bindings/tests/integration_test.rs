//! Integration tests for ProTrace Rust implementation

use protrace_image_dna::{compute_dna, hamming_distance, is_duplicate};
use protrace_merkle_tree::MerkleTree;
use protrace_wallet::WalletManager;

#[test]
fn test_dna_computation() {
    // This test requires actual image files
    // Skip if no test images available
    println!("DNA computation test - requires test images");
}

#[test]
fn test_merkle_tree_operations() {
    let mut tree = MerkleTree::new();
    
    // Add test leaves
    tree.add_leaf("abc123def456", "ptr1", "platform1", Some(1000));
    tree.add_leaf("def456ghi789", "ptr2", "platform2", Some(2000));
    tree.add_leaf("ghi789jkl012", "ptr3", "platform3", Some(3000));
    
    // Build tree
    let root = tree.build_tree().unwrap();
    assert!(!root.is_empty());
    assert_eq!(tree.leaf_count(), 3);
    
    // Generate proof
    let proof = tree.get_proof(0).unwrap();
    assert!(!proof.is_empty());
    
    // Verify proof
    let leaf_data = b"abc123def456|ptr1|platform1|1000";
    let is_valid = tree.verify_proof(leaf_data, &proof, &root).unwrap();
    assert!(is_valid);
}

#[test]
fn test_wallet_operations() {
    // Create new wallet
    let wallet1 = WalletManager::new();
    assert!(!wallet1.pubkey_string().is_empty());
    
    // Export and import
    let json = wallet1.to_json().unwrap();
    let wallet2 = WalletManager::from_json(&json).unwrap();
    assert_eq!(wallet1.pubkey_string(), wallet2.pubkey_string());
}

#[test]
fn test_manifest_export_import() {
    let mut tree = MerkleTree::new();
    
    tree.add_leaf("hash1", "ptr1", "platform1", Some(1000));
    tree.add_leaf("hash2", "ptr2", "platform2", Some(2000));
    
    tree.build_tree().unwrap();
    
    // Export manifest
    let manifest = tree.export_manifest().unwrap();
    assert_eq!(manifest.total_leaves, 2);
    assert_eq!(manifest.leaves.len(), 2);
    
    // Import manifest
    let mut tree2 = MerkleTree::new();
    tree2.import_manifest(&manifest).unwrap();
    
    assert_eq!(tree.get_root().unwrap(), tree2.get_root().unwrap());
}
