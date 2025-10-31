//! Type definitions for blockchain operations

use anchor_client::solana_sdk::pubkey::Pubkey;
use serde::{Deserialize, Serialize};

/// Edition mode enumeration
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum EditionMode {
    Strict1To1,
    Serial,
    Fungible,
}

/// Edition update structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EditionUpdate {
    pub dna_hash: [u8; 32],
    pub chain: [u8; 10],
    pub contract: [u8; 32],
    pub token_id: [u8; 32],
    pub edition_no: u32,
    pub edition_mode: EditionMode,
    pub max_editions: Option<u32>,
}

/// Instruction data enum for Anchor program calls
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InstructionData {
    InitializeMerkleRoot {
        root: [u8; 32],
    },
    UpdateMerkleRoot {
        new_root: [u8; 32],
    },
    AnchorMerkleRootOracle {
        merkle_root: [u8; 32],
        manifest_cid: String,
        asset_count: u64,
        timestamp: i64,
    },
    InitializeEditionRegistry {
        oracle_authority: Pubkey,
    },
    BatchRegisterEditions {
        edition_updates: Vec<EditionUpdate>,
        batch_id: String,
        new_merkle_root: [u8; 32],
        ipfs_cid: String,
    },
}

/// Account data for Merkle anchor
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnchorAccount {
    pub oracle_authority: Pubkey,
    pub merkle_root: [u8; 32],
    pub manifest_cid: String,
    pub asset_count: u64,
    pub timestamp: i64,
    pub oracle_signature: Pubkey,
    pub version: u64,
}

/// Account data for edition registry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EditionRegistryAccount {
    pub oracle_authority: Pubkey,
    pub merkle_root: [u8; 32],
    pub ipfs_cid: String,
    pub total_editions: u64,
    pub last_batch_id: String,
    pub last_batch_timestamp: i64,
    pub last_oracle_signature: Pubkey,
    pub version: u64,
}

impl EditionUpdate {
    /// Create new edition update
    pub fn new(
        dna_hash: [u8; 32],
        chain: &str,
        contract: [u8; 32],
        token_id: &str,
        edition_no: u32,
        edition_mode: EditionMode,
        max_editions: Option<u32>,
    ) -> Self {
        let mut chain_bytes = [0u8; 10];
        let chain_str = chain.as_bytes();
        let copy_len = chain_str.len().min(10);
        chain_bytes[..copy_len].copy_from_slice(&chain_str[..copy_len]);

        let mut token_id_bytes = [0u8; 32];
        let token_str = token_id.as_bytes();
        let copy_len = token_str.len().min(32);
        token_id_bytes[..copy_len].copy_from_slice(&token_str[..copy_len]);

        Self {
            dna_hash,
            chain: chain_bytes,
            contract,
            token_id: token_id_bytes,
            edition_no,
            edition_mode,
            max_editions,
        }
    }
}
