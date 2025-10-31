//! ProTrace Merkle Tree Manager
//!
//! BLAKE3-based Merkle tree for tamper-proof DNA registration commitments.
//! Optimized for batch verification with O(log n) proof generation.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MerkleError {
    #[error("Tree not built")]
    TreeNotBuilt,
    #[error("Leaf index out of range: {0}")]
    LeafIndexOutOfRange(usize),
    #[error("Invalid proof")]
    InvalidProof,
    #[error("Root mismatch")]
    RootMismatch,
}

/// Merkle tree node
#[derive(Debug, Clone)]
struct MerkleNode {
    hash: [u8; 32],
    left: Option<Box<MerkleNode>>,
    right: Option<Box<MerkleNode>>,
    is_leaf: bool,
    data: Option<Vec<u8>>,
}

impl MerkleNode {
    fn new_leaf(data: Vec<u8>) -> Self {
        let hash = blake3::hash(&data).into();
        Self {
            hash,
            left: None,
            right: None,
            is_leaf: true,
            data: Some(data),
        }
    }

    fn new_internal(left: MerkleNode, right: MerkleNode) -> Self {
        let mut combined = Vec::with_capacity(64);
        combined.extend_from_slice(&left.hash);
        combined.extend_from_slice(&right.hash);
        let hash = blake3::hash(&combined).into();
        
        Self {
            hash,
            left: Some(Box::new(left)),
            right: Some(Box::new(right)),
            is_leaf: false,
            data: None,
        }
    }
}

/// Proof element for Merkle proof
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProofElement {
    pub hash: String,
    pub position: Position,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum Position {
    Left,
    Right,
}

/// Leaf information for manifest
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LeafInfo {
    pub index: usize,
    pub dna_hex: String,
    pub pointer: String,
    pub platform_id: String,
    pub timestamp: i64,
}

/// Manifest for IPFS storage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    pub root: String,
    pub total_leaves: usize,
    pub leaves: Vec<LeafInfo>,
    pub proofs: HashMap<String, Vec<ProofElement>>,
}

/// Balanced binary Merkle tree with BLAKE3 hashing
pub struct MerkleTree {
    leaves: Vec<Vec<u8>>,
    root: Option<MerkleNode>,
    leaf_map: HashMap<Vec<u8>, usize>,
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
    pub fn add_leaf(
        &mut self,
        dna_hex: &str,
        pointer: &str,
        platform_id: &str,
        timestamp: Option<i64>,
    ) {
        let timestamp = timestamp.unwrap_or_else(|| chrono::Utc::now().timestamp());
        
        // Construct leaf data
        let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
        let leaf_bytes = leaf_data.as_bytes().to_vec();
        
        // Store leaf
        self.leaf_map.insert(leaf_bytes.clone(), self.leaves.len());
        self.leaves.push(leaf_bytes);
    }

    /// Construct balanced binary Merkle tree from leaves
    pub fn build_tree(&mut self) -> Result<String, MerkleError> {
        if self.leaves.is_empty() {
            self.root = None;
            return Ok(String::new());
        }

        // Create leaf nodes
        let mut nodes: Vec<MerkleNode> = self
            .leaves
            .iter()
            .map(|leaf| MerkleNode::new_leaf(leaf.clone()))
            .collect();

        // Build tree bottom-up
        while nodes.len() > 1 {
            let mut next_level = Vec::new();

            for i in (0..nodes.len()).step_by(2) {
                let left = nodes[i].clone();
                let right = if i + 1 < nodes.len() {
                    nodes[i + 1].clone()
                } else {
                    nodes[i].clone() // Duplicate last if odd
                };

                next_level.push(MerkleNode::new_internal(left, right));
            }

            nodes = next_level;
        }

        self.root = Some(nodes[0].clone());
        Ok(hex::encode(nodes[0].hash))
    }

    /// Get Merkle root hash
    pub fn get_root(&self) -> Result<String, MerkleError> {
        self.root
            .as_ref()
            .map(|root| hex::encode(root.hash))
            .ok_or(MerkleError::TreeNotBuilt)
    }

    /// Generate Merkle proof for leaf at given index
    pub fn get_proof(&self, leaf_index: usize) -> Result<Vec<ProofElement>, MerkleError> {
        if leaf_index >= self.leaves.len() {
            return Err(MerkleError::LeafIndexOutOfRange(leaf_index));
        }

        if self.root.is_none() {
            return Err(MerkleError::TreeNotBuilt);
        }

        let mut proof = Vec::new();

        // Rebuild tree structure to track path
        let mut nodes: Vec<MerkleNode> = self
            .leaves
            .iter()
            .map(|leaf| MerkleNode::new_leaf(leaf.clone()))
            .collect();
        
        let mut current_index = leaf_index;

        while nodes.len() > 1 {
            let mut next_level = Vec::new();

            for i in (0..nodes.len()).step_by(2) {
                let left = nodes[i].clone();
                let right = if i + 1 < nodes.len() {
                    nodes[i + 1].clone()
                } else {
                    nodes[i].clone()
                };

                // Check if current node is in this pair
                if i == current_index || i + 1 == current_index {
                    // Add sibling to proof
                    if i == current_index {
                        // Left node, add right sibling
                        proof.push(ProofElement {
                            hash: hex::encode(right.hash),
                            position: Position::Right,
                        });
                    } else {
                        // Right node, add left sibling
                        proof.push(ProofElement {
                            hash: hex::encode(left.hash),
                            position: Position::Left,
                        });
                    }

                    // Update index for next level
                    current_index = i / 2;
                }

                next_level.push(MerkleNode::new_internal(left, right));
            }

            nodes = next_level;
        }

        Ok(proof)
    }

    /// Verify Merkle proof for a leaf
    pub fn verify_proof(
        &self,
        leaf_data: &[u8],
        proof: &[ProofElement],
        root_hash: &str,
    ) -> Result<bool, MerkleError> {
        // Compute leaf hash
        let mut current_hash = blake3::hash(leaf_data).as_bytes().to_vec();

        // Traverse proof path
        for proof_element in proof {
            let sibling_hash = hex::decode(&proof_element.hash)
                .map_err(|_| MerkleError::InvalidProof)?;

            let mut combined = Vec::with_capacity(64);
            match proof_element.position {
                Position::Left => {
                    combined.extend_from_slice(&sibling_hash);
                    combined.extend_from_slice(&current_hash);
                }
                Position::Right => {
                    combined.extend_from_slice(&current_hash);
                    combined.extend_from_slice(&sibling_hash);
                }
            }

            current_hash = blake3::hash(&combined).as_bytes().to_vec();
        }

        // Compare with expected root
        Ok(hex::encode(current_hash) == root_hash)
    }

    /// Export tree manifest for IPFS storage
    pub fn export_manifest(&self) -> Result<Manifest, MerkleError> {
        if self.root.is_none() {
            return Err(MerkleError::TreeNotBuilt);
        }

        let root = self.get_root()?;
        let mut leaves = Vec::new();
        let mut proofs = HashMap::new();

        // Export leaves
        for (i, leaf_data) in self.leaves.iter().enumerate() {
            let leaf_str = String::from_utf8_lossy(leaf_data);
            let parts: Vec<&str> = leaf_str.split('|').collect();

            if parts.len() >= 4 {
                leaves.push(LeafInfo {
                    index: i,
                    dna_hex: parts[0].to_string(),
                    pointer: parts[1].to_string(),
                    platform_id: parts[2].to_string(),
                    timestamp: parts[3].parse().unwrap_or(0),
                });

                // Generate proof for each leaf
                let proof = self.get_proof(i)?;
                proofs.insert(i.to_string(), proof);
            }
        }

        Ok(Manifest {
            root,
            total_leaves: self.leaves.len(),
            leaves,
            proofs,
        })
    }

    /// Import tree from manifest
    pub fn import_manifest(&mut self, manifest: &Manifest) -> Result<(), MerkleError> {
        self.leaves.clear();
        self.leaf_map.clear();

        // Import leaves
        for leaf in &manifest.leaves {
            self.add_leaf(
                &leaf.dna_hex,
                &leaf.pointer,
                &leaf.platform_id,
                Some(leaf.timestamp),
            );
        }

        // Rebuild tree
        let root = self.build_tree()?;

        // Verify root matches
        if root != manifest.root {
            return Err(MerkleError::RootMismatch);
        }

        Ok(())
    }

    /// Get number of leaves
    pub fn leaf_count(&self) -> usize {
        self.leaves.len()
    }
}

impl Default for MerkleTree {
    fn default() -> Self {
        Self::new()
    }
}

/// Compute leaf hash for DNA registration
pub fn compute_leaf_hash(
    dna_hex: &str,
    pointer: &str,
    platform_id: &str,
    timestamp: Option<i64>,
) -> String {
    let timestamp = timestamp.unwrap_or_else(|| chrono::Utc::now().timestamp());
    let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
    hex::encode(blake3::hash(leaf_data.as_bytes()).as_bytes())
}

/// Standalone proof verification without tree instance
pub fn verify_proof_standalone(
    dna_hex: &str,
    pointer: &str,
    platform_id: &str,
    timestamp: i64,
    proof: &[ProofElement],
    root_hash: &str,
) -> Result<bool, MerkleError> {
    let leaf_data = format!("{}|{}|{}|{}", dna_hex, pointer, platform_id, timestamp);
    let mut current_hash = blake3::hash(leaf_data.as_bytes()).as_bytes().to_vec();

    for proof_element in proof {
        let sibling_hash = hex::decode(&proof_element.hash)
            .map_err(|_| MerkleError::InvalidProof)?;

        let mut combined = Vec::with_capacity(64);
        match proof_element.position {
            Position::Left => {
                combined.extend_from_slice(&sibling_hash);
                combined.extend_from_slice(&current_hash);
            }
            Position::Right => {
                combined.extend_from_slice(&current_hash);
                combined.extend_from_slice(&sibling_hash);
            }
        }

        current_hash = blake3::hash(&combined).as_bytes().to_vec();
    }

    Ok(hex::encode(current_hash) == root_hash)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_merkle_tree_basic() {
        let mut tree = MerkleTree::new();

        tree.add_leaf(
            "abc123def456",
            "uuid:550e8400-opensea-ethereum",
            "opensea",
            Some(1698765432),
        );
        tree.add_leaf(
            "def789abc123",
            "uuid:660e9500-foundation-ethereum",
            "foundation",
            Some(1698765433),
        );

        let root = tree.build_tree().unwrap();
        assert!(!root.is_empty());
        assert_eq!(tree.leaf_count(), 2);
    }

    #[test]
    fn test_merkle_proof() {
        let mut tree = MerkleTree::new();

        tree.add_leaf("abc123", "ptr1", "platform1", Some(1000));
        tree.add_leaf("def456", "ptr2", "platform2", Some(2000));
        tree.add_leaf("ghi789", "ptr3", "platform3", Some(3000));

        let root = tree.build_tree().unwrap();
        let proof = tree.get_proof(0).unwrap();

        let leaf_data = b"abc123|ptr1|platform1|1000";
        let is_valid = tree.verify_proof(leaf_data, &proof, &root).unwrap();
        assert!(is_valid);
    }
}
