//! ProTrace Merkle Tree (Rust) - BLAKE3-based
//! ==========================================
//!
//! High-performance Merkle tree implementation matching Python functionality.
//!
//! ## Features
//!
//! - **BLAKE3 hashing**: Fast cryptographic hashing
//! - **Balanced binary tree**: Optimal proof size (O(log n))
//! - **Proof generation**: Efficient O(log n) proof generation
//! - **Proof verification**: Fast O(log n) verification
//! - **Append-only**: Add leaves incrementally
//!
//! ## Algorithm (Aligned with Python)
//!
//! - Leaf = BLAKE3(DNA_hex || pointer || platform_id || timestamp)
//! - Parent = BLAKE3(left_hash || right_hash)
//! - Duplicate last node if odd number at level
//!
//! ## Example
//!
//! ```rust
//! use protrace_merkle::MerkleTree;
//!
//! let mut tree = MerkleTree::new();
//! tree.add_leaf("dna_hash", "ipfs://Qm...", "platform_1", 1234567890);
//! let root = tree.build_tree().unwrap();
//! 
//! // Get proof for leaf 0
//! let proof = tree.get_proof(0).unwrap();
//! assert!(tree.verify_proof(0, &proof, &root).unwrap());
//! ```

use blake3;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

/// Merkle tree errors
#[derive(Error, Debug)]
pub enum MerkleError {
    #[error("Tree is empty")]
    EmptyTree,

    #[error("Invalid leaf index: {0}")]
    InvalidIndex(usize),

    #[error("Tree not built")]
    TreeNotBuilt,

    #[error("Invalid proof")]
    InvalidProof,

    #[error("Invalid hex encoding: {0}")]
    InvalidHex(#[from] hex::FromHexError),
}

/// Result type for Merkle operations
pub type MerkleResult<T> = Result<T, MerkleError>;

/// Merkle tree node
#[derive(Debug, Clone)]
struct MerkleNode {
    hash: Vec<u8>,
    left: Option<Box<MerkleNode>>,
    right: Option<Box<MerkleNode>>,
    is_leaf: bool,
}

impl MerkleNode {
    /// Create leaf node
    fn leaf(data: &[u8]) -> Self {
        let hash = blake3::hash(data).as_bytes().to_vec();
        Self {
            hash,
            left: None,
            right: None,
            is_leaf: true,
        }
    }

    /// Create internal node
    fn internal(left: MerkleNode, right: MerkleNode) -> Self {
        let mut combined = left.hash.clone();
        combined.extend_from_slice(&right.hash);
        let hash = blake3::hash(&combined).as_bytes().to_vec();
        
        Self {
            hash,
            left: Some(Box::new(left)),
            right: Some(Box::new(right)),
            is_leaf: false,
        }
    }

    /// Get hash as hex string
    fn hash_hex(&self) -> String {
        hex::encode(&self.hash)
    }
}

/// Proof element with position
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofElement {
    /// Hash of sibling node
    pub hash: String,
    /// Position: "left" or "right"
    pub position: String,
}

/// Balanced binary Merkle tree
#[derive(Debug)]
pub struct MerkleTree {
    leaves: Vec<Vec<u8>>,
    root: Option<MerkleNode>,
    leaf_map: HashMap<Vec<u8>, usize>,
}

impl Default for MerkleTree {
    fn default() -> Self {
        Self::new()
    }
}

impl MerkleTree {
    /// Create new empty Merkle tree
    pub fn new() -> Self {
        Self {
            leaves: Vec::new(),
            root: None,
            leaf_map: HashMap::new(),
        }
    }

    /// Add registration leaf to tree
    ///
    /// Leaf = BLAKE3(DNA_hex || pointer || platform_id || timestamp)
    ///
    /// # Arguments
    ///
    /// * `dna_hex` - DNA hash (64 hex characters)
    /// * `pointer` - Unique identifier (UUID or IPFS CID)
    /// * `platform_id` - Platform identifier
    /// * `timestamp` - Unix timestamp
    pub fn add_leaf(&mut self, dna_hex: &str, pointer: &str, platform_id: &str, timestamp: u64) {
        let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
        let leaf_bytes = leaf_data.as_bytes().to_vec();

        self.leaf_map.insert(leaf_bytes.clone(), self.leaves.len());
        self.leaves.push(leaf_bytes);
    }

    /// Add raw leaf data
    pub fn add_raw_leaf(&mut self, data: &[u8]) {
        let leaf_bytes = data.to_vec();
        self.leaf_map.insert(leaf_bytes.clone(), self.leaves.len());
        self.leaves.push(leaf_bytes);
    }

    /// Get number of leaves
    pub fn leaf_count(&self) -> usize {
        self.leaves.len()
    }

    /// Build balanced binary Merkle tree from leaves
    ///
    /// Returns root hash as hex string
    pub fn build_tree(&mut self) -> MerkleResult<String> {
        if self.leaves.is_empty() {
            return Err(MerkleError::EmptyTree);
        }

        // Create leaf nodes
        let mut nodes: Vec<MerkleNode> = self
            .leaves
            .iter()
            .map(|leaf| MerkleNode::leaf(leaf))
            .collect();

        // Build tree bottom-up
        while nodes.len() > 1 {
            let mut next_level = Vec::new();

            for i in (0..nodes.len()).step_by(2) {
                let left = nodes[i].clone();
                let right = if i + 1 < nodes.len() {
                    nodes[i + 1].clone()
                } else {
                    // Duplicate last node if odd number
                    nodes[i].clone()
                };

                next_level.push(MerkleNode::internal(left, right));
            }

            nodes = next_level;
        }

        self.root = Some(nodes[0].clone());
        Ok(self.root.as_ref().unwrap().hash_hex())
    }

    /// Get Merkle root hash
    pub fn get_root(&self) -> MerkleResult<String> {
        match &self.root {
            Some(node) => Ok(node.hash_hex()),
            None => Err(MerkleError::TreeNotBuilt),
        }
    }

    /// Get Merkle root as bytes
    pub fn get_root_bytes(&self) -> MerkleResult<Vec<u8>> {
        match &self.root {
            Some(node) => Ok(node.hash.clone()),
            None => Err(MerkleError::TreeNotBuilt),
        }
    }

    /// Generate Merkle proof for leaf at index
    ///
    /// Returns vector of sibling hashes along path to root
    pub fn get_proof(&self, index: usize) -> MerkleResult<Vec<ProofElement>> {
        if index >= self.leaves.len() {
            return Err(MerkleError::InvalidIndex(index));
        }

        if self.root.is_none() {
            return Err(MerkleError::TreeNotBuilt);
        }

        let mut proof = Vec::new();
        let mut leaf_index = index;

        // Create leaf nodes for proof generation
        let mut nodes: Vec<MerkleNode> = self
            .leaves
            .iter()
            .map(|leaf| MerkleNode::leaf(leaf))
            .collect();

        // Build proof by traversing tree levels
        while nodes.len() > 1 {
            let mut next_level = Vec::new();
            let sibling_index = if leaf_index % 2 == 0 {
                leaf_index + 1
            } else {
                leaf_index - 1
            };

            // Get sibling hash
            if sibling_index < nodes.len() {
                let sibling = &nodes[sibling_index];
                let position = if leaf_index % 2 == 0 {
                    "right"
                } else {
                    "left"
                };
                
                proof.push(ProofElement {
                    hash: sibling.hash_hex(),
                    position: position.to_string(),
                });
            }

            // Build next level
            for i in (0..nodes.len()).step_by(2) {
                let left = nodes[i].clone();
                let right = if i + 1 < nodes.len() {
                    nodes[i + 1].clone()
                } else {
                    nodes[i].clone()
                };

                next_level.push(MerkleNode::internal(left, right));
            }

            nodes = next_level;
            leaf_index /= 2;
        }

        Ok(proof)
    }

    /// Verify Merkle proof for leaf at index
    ///
    /// # Arguments
    ///
    /// * `index` - Leaf index
    /// * `proof` - Proof elements (sibling hashes with positions)
    /// * `root_hash` - Expected root hash
    pub fn verify_proof(
        &self,
        index: usize,
        proof: &[ProofElement],
        root_hash: &str,
    ) -> MerkleResult<bool> {
        if index >= self.leaves.len() {
            return Err(MerkleError::InvalidIndex(index));
        }

        // Start with leaf hash
        let mut current = blake3::hash(&self.leaves[index]).as_bytes().to_vec();
        let mut current_index = index;

        // Apply proof elements
        for element in proof {
            let sibling_bytes = hex::decode(&element.hash)?;
            
            let combined = if element.position == "right" || current_index % 2 == 0 {
                // Sibling is on right
                let mut combined = current.clone();
                combined.extend_from_slice(&sibling_bytes);
                combined
            } else {
                // Sibling is on left
                let mut combined = sibling_bytes.clone();
                combined.extend_from_slice(&current);
                combined
            };

            current = blake3::hash(&combined).as_bytes().to_vec();
            current_index /= 2;
        }

        // Compare with expected root
        let computed_root = hex::encode(&current);
        Ok(computed_root == root_hash)
    }

    /// Get leaf data at index
    pub fn get_leaf(&self, index: usize) -> MerkleResult<&[u8]> {
        self.leaves
            .get(index)
            .map(|v| v.as_slice())
            .ok_or(MerkleError::InvalidIndex(index))
    }

    /// Get leaf hash at index
    pub fn get_leaf_hash(&self, index: usize) -> MerkleResult<String> {
        let leaf = self.get_leaf(index)?;
        Ok(hex::encode(blake3::hash(leaf).as_bytes()))
    }
}

/// Standalone function to compute leaf hash
pub fn compute_leaf_hash(dna_hex: &str, pointer: &str, platform_id: &str, timestamp: u64) -> String {
    let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
    hex::encode(blake3::hash(leaf_data.as_bytes()).as_bytes())
}

/// Standalone function to verify proof
pub fn verify_proof_standalone(
    dna_hex: &str,
    pointer: &str,
    platform_id: &str,
    timestamp: u64,
    proof: &[ProofElement],
    root_hash: &str,
) -> MerkleResult<bool> {
    // Compute leaf hash
    let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
    let mut current = blake3::hash(leaf_data.as_bytes()).as_bytes().to_vec();

    // Apply proof elements
    for (i, element) in proof.iter().enumerate() {
        let sibling_bytes = hex::decode(&element.hash)?;
        
        let combined = if element.position == "right" || i % 2 == 0 {
            let mut combined = current.clone();
            combined.extend_from_slice(&sibling_bytes);
            combined
        } else {
            let mut combined = sibling_bytes.clone();
            combined.extend_from_slice(&current);
            combined
        };

        current = blake3::hash(&combined).as_bytes().to_vec();
    }

    // Compare with expected root
    let computed_root = hex::encode(&current);
    Ok(computed_root == root_hash)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_merkle_tree_creation() {
        let mut tree = MerkleTree::new();
        assert_eq!(tree.leaf_count(), 0);

        tree.add_leaf("abc123", "ptr1", "platform1", 1234567890);
        assert_eq!(tree.leaf_count(), 1);
    }

    #[test]
    fn test_merkle_tree_build() {
        let mut tree = MerkleTree::new();
        
        for i in 0..5 {
            tree.add_leaf(&format!("dna_{}", i), &format!("ptr_{}", i), "platform", 1234567890);
        }

        let root = tree.build_tree().unwrap();
        assert_eq!(root.len(), 64); // BLAKE3 = 32 bytes = 64 hex chars
    }

    #[test]
    fn test_merkle_proof_verification() {
        let mut tree = MerkleTree::new();
        
        for i in 0..5 {
            tree.add_leaf(&format!("dna_{}", i), &format!("ptr_{}", i), "platform", 1234567890);
        }

        let root = tree.build_tree().unwrap();
        let proof = tree.get_proof(0).unwrap();
        
        assert!(tree.verify_proof(0, &proof, &root).unwrap());
    }

    #[test]
    fn test_leaf_hash_computation() {
        let hash = compute_leaf_hash("abc123", "ptr1", "platform1", 1234567890);
        assert_eq!(hash.len(), 64); // 32 bytes = 64 hex chars
    }

    #[test]
    fn test_single_leaf_tree() {
        let mut tree = MerkleTree::new();
        tree.add_leaf("dna_0", "ptr_0", "platform", 1234567890);
        
        let root = tree.build_tree().unwrap();
        let proof = tree.get_proof(0).unwrap();
        
        // Single leaf should have empty proof
        assert_eq!(proof.len(), 0);
        assert!(tree.verify_proof(0, &proof, &root).unwrap());
    }
}
