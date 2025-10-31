//! ProTrace Blockchain Integration
//!
//! Solana blockchain integration for Merkle root anchoring and edition management

use anchor_client::solana_sdk::commitment_config::CommitmentConfig;
use anchor_client::solana_sdk::pubkey::Pubkey;
use anchor_client::solana_sdk::signature::{Keypair, Signature, Signer};
use anchor_client::solana_sdk::system_program;
use anchor_client::{Client, Cluster};
use anyhow::Result;
use protrace_merkle_tree::Manifest;
use serde::{Deserialize, Serialize};
use std::rc::Rc;
use std::str::FromStr;
use thiserror::Error;

pub mod types;
pub use types::*;

#[derive(Error, Debug)]
pub enum BlockchainError {
    #[error("Anchor client error: {0}")]
    AnchorClientError(String),
    #[error("Transaction failed: {0}")]
    TransactionFailed(String),
    #[error("Invalid public key: {0}")]
    InvalidPublicKey(String),
    #[error("Wallet error: {0}")]
    WalletError(String),
    #[error("RPC error: {0}")]
    RpcError(String),
}

/// Program ID for ProTrace on devnet
pub const PROTRACE_PROGRAM_ID: &str = "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS";

/// ProTrace blockchain client for Solana
pub struct ProTraceClient {
    client: Client,
    program_id: Pubkey,
    payer: Rc<Keypair>,
}

impl ProTraceClient {
    /// Create new ProTrace client for devnet
    pub fn new_devnet(payer: Keypair) -> Result<Self> {
        let cluster = Cluster::Devnet;
        let payer_rc = Rc::new(payer);
        let client = Client::new_with_options(
            cluster,
            payer_rc.clone(),
            CommitmentConfig::confirmed(),
        );

        let program_id = Pubkey::from_str(PROTRACE_PROGRAM_ID)
            .map_err(|e| BlockchainError::InvalidPublicKey(e.to_string()))?;

        Ok(Self {
            client,
            program_id,
            payer: payer_rc,
        })
    }

    /// Create new ProTrace client with custom cluster
    pub fn new(cluster: Cluster, payer: Keypair, program_id: &str) -> Result<Self> {
        let payer_rc = Rc::new(payer);
        let client = Client::new_with_options(
            cluster,
            payer_rc.clone(),
            CommitmentConfig::confirmed(),
        );

        let program_id = Pubkey::from_str(program_id)
            .map_err(|e| BlockchainError::InvalidPublicKey(e.to_string()))?;

        Ok(Self {
            client,
            program_id,
            payer: payer_rc,
        })
    }

    /// Get payer public key
    pub fn payer_pubkey(&self) -> Pubkey {
        self.payer.pubkey()
    }

    /// Get program ID
    pub fn program_id(&self) -> Pubkey {
        self.program_id
    }

    /// Initialize Merkle root account
    pub async fn initialize_merkle_root(&self, root: [u8; 32]) -> Result<Signature> {
        log::info!("Initializing Merkle root: {}", hex::encode(root));

        let program = self.client.program(self.program_id)?;

        // Derive PDA for merkle_account
        let (merkle_account, _bump) = Pubkey::find_program_address(
            &[b"merkle_root"],
            &self.program_id,
        );

        log::info!("Merkle account PDA: {}", merkle_account);

        let signature = program
            .request()
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: merkle_account,
                is_signer: false,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: self.payer.pubkey(),
                is_signer: true,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: system_program::ID,
                is_signer: false,
                is_writable: false,
            })
            .args(InstructionData::InitializeMerkleRoot { root })
            .send()?;

        log::info!("Transaction signature: {}", signature);
        Ok(signature)
    }

    /// Update Merkle root
    pub async fn update_merkle_root(&self, new_root: [u8; 32]) -> Result<Signature> {
        log::info!("Updating Merkle root: {}", hex::encode(new_root));

        let program = self.client.program(self.program_id)?;

        let (merkle_account, _bump) = Pubkey::find_program_address(
            &[b"merkle_root"],
            &self.program_id,
        );

        let signature = program
            .request()
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: merkle_account,
                is_signer: false,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: self.payer.pubkey(),
                is_signer: true,
                is_writable: false,
            })
            .args(InstructionData::UpdateMerkleRoot { new_root })
            .send()?;

        log::info!("Transaction signature: {}", signature);
        Ok(signature)
    }

    /// Anchor Merkle root with oracle authority
    pub async fn anchor_merkle_root_oracle(
        &self,
        merkle_root: [u8; 32],
        manifest_cid: String,
        asset_count: u64,
        timestamp: i64,
    ) -> Result<Signature> {
        log::info!("Anchoring Merkle root via oracle");
        log::info!("  Root: {}", hex::encode(merkle_root));
        log::info!("  CID: {}", manifest_cid);
        log::info!("  Assets: {}", asset_count);

        let program = self.client.program(self.program_id)?;

        let (anchor_account, _bump) = Pubkey::find_program_address(
            &[b"protrace_anchor"],
            &self.program_id,
        );

        let signature = program
            .request()
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: anchor_account,
                is_signer: false,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: self.payer.pubkey(),
                is_signer: true,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: system_program::ID,
                is_signer: false,
                is_writable: false,
            })
            .args(InstructionData::AnchorMerkleRootOracle {
                merkle_root,
                manifest_cid,
                asset_count,
                timestamp,
            })
            .send()?;

        log::info!("Transaction signature: {}", signature);
        Ok(signature)
    }

    /// Initialize edition registry
    pub async fn initialize_edition_registry(&self, oracle_authority: Pubkey) -> Result<Signature> {
        log::info!("Initializing edition registry");
        log::info!("  Oracle authority: {}", oracle_authority);

        let program = self.client.program(self.program_id)?;

        let (edition_registry, _bump) = Pubkey::find_program_address(
            &[b"edition_registry"],
            &self.program_id,
        );

        let signature = program
            .request()
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: edition_registry,
                is_signer: false,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: self.payer.pubkey(),
                is_signer: true,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: system_program::ID,
                is_signer: false,
                is_writable: false,
            })
            .args(InstructionData::InitializeEditionRegistry { oracle_authority })
            .send()?;

        log::info!("Transaction signature: {}", signature);
        Ok(signature)
    }

    /// Batch register editions
    pub async fn batch_register_editions(
        &self,
        edition_updates: Vec<EditionUpdate>,
        batch_id: String,
        new_merkle_root: [u8; 32],
        ipfs_cid: String,
    ) -> Result<Signature> {
        log::info!("Batch registering {} editions", edition_updates.len());
        log::info!("  Batch ID: {}", batch_id);
        log::info!("  New root: {}", hex::encode(new_merkle_root));

        let program = self.client.program(self.program_id)?;

        let (edition_registry, _bump) = Pubkey::find_program_address(
            &[b"edition_registry"],
            &self.program_id,
        );

        let signature = program
            .request()
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: edition_registry,
                is_signer: false,
                is_writable: true,
            })
            .accounts(anchor_client::solana_sdk::instruction::AccountMeta {
                pubkey: self.payer.pubkey(),
                is_signer: true,
                is_writable: false,
            })
            .args(InstructionData::BatchRegisterEditions {
                edition_updates,
                batch_id,
                new_merkle_root,
                ipfs_cid,
            })
            .send()?;

        log::info!("Transaction signature: {}", signature);
        Ok(signature)
    }

    /// Get balance of payer account
    pub async fn get_balance(&self) -> Result<u64> {
        let rpc_client = self.client.program(self.program_id)?.rpc();
        let balance = rpc_client.get_balance(&self.payer.pubkey())?;
        Ok(balance)
    }

    /// Request airdrop (devnet only)
    pub async fn request_airdrop(&self, lamports: u64) -> Result<Signature> {
        log::info!("Requesting airdrop of {} lamports", lamports);
        let rpc_client = self.client.program(self.program_id)?.rpc();
        let signature = rpc_client.request_airdrop(&self.payer.pubkey(), lamports)?;
        log::info!("Airdrop signature: {}", signature);
        Ok(signature)
    }
}

/// Helper to convert Manifest to blockchain format
pub fn manifest_to_anchor_params(manifest: &Manifest) -> ([u8; 32], String, u64, i64) {
    let root_bytes = hex::decode(&manifest.root)
        .unwrap_or_else(|_| vec![0u8; 32]);
    let mut root = [0u8; 32];
    root.copy_from_slice(&root_bytes[..32.min(root_bytes.len())]);

    let timestamp = chrono::Utc::now().timestamp();

    (root, manifest.root.clone(), manifest.total_leaves as u64, timestamp)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_program_id_parsing() {
        let program_id = Pubkey::from_str(PROTRACE_PROGRAM_ID);
        assert!(program_id.is_ok());
    }
}
