//! ProTrace Wallet Integration
//!
//! Wallet management and keypair handling for Solana blockchain

use anyhow::{Context, Result};
use solana_sdk::signature::{Keypair, Signer};
use std::fs;
use std::path::{Path, PathBuf};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum WalletError {
    #[error("Failed to load keypair: {0}")]
    KeypairLoadError(String),
    #[error("Failed to save keypair: {0}")]
    KeypairSaveError(String),
    #[error("Invalid keypair format")]
    InvalidKeypairFormat,
    #[error("File not found: {0}")]
    FileNotFound(String),
}

/// Wallet manager for handling Solana keypairs
pub struct WalletManager {
    keypair: Keypair,
    path: Option<PathBuf>,
}

impl WalletManager {
    /// Create new wallet with random keypair
    pub fn new() -> Self {
        Self {
            keypair: Keypair::new(),
            path: None,
        }
    }

    /// Load wallet from file
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        let path_ref = path.as_ref();
        log::info!("Loading wallet from: {}", path_ref.display());

        let keypair = load_keypair_from_file(path_ref)?;

        Ok(Self {
            keypair,
            path: Some(path_ref.to_path_buf()),
        })
    }

    /// Load wallet from JSON string
    pub fn from_json(json: &str) -> Result<Self> {
        let bytes: Vec<u8> = serde_json::from_str(json)
            .context("Failed to parse keypair JSON")?;

        if bytes.len() != 64 {
            return Err(WalletError::InvalidKeypairFormat.into());
        }

        let keypair = Keypair::from_bytes(&bytes)
            .map_err(|e| WalletError::KeypairLoadError(e.to_string()))?;

        Ok(Self {
            keypair,
            path: None,
        })
    }

    /// Load wallet from byte array
    pub fn from_bytes(bytes: &[u8]) -> Result<Self> {
        if bytes.len() != 64 {
            return Err(WalletError::InvalidKeypairFormat.into());
        }

        let keypair = Keypair::from_bytes(bytes)
            .map_err(|e| WalletError::KeypairLoadError(e.to_string()))?;

        Ok(Self {
            keypair,
            path: None,
        })
    }

    /// Load wallet from base58 private key
    pub fn from_base58(base58_key: &str) -> Result<Self> {
        let bytes = bs58::decode(base58_key)
            .into_vec()
            .context("Failed to decode base58 private key")?;

        Self::from_bytes(&bytes)
    }

    /// Save wallet to file
    pub fn save_to_file<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        let path_ref = path.as_ref();
        log::info!("Saving wallet to: {}", path_ref.display());

        save_keypair_to_file(&self.keypair, path_ref)?;
        self.path = Some(path_ref.to_path_buf());

        Ok(())
    }

    /// Get keypair reference
    pub fn keypair(&self) -> &Keypair {
        &self.keypair
    }

    /// Get public key as string
    pub fn pubkey_string(&self) -> String {
        self.keypair.pubkey().to_string()
    }

    /// Get private key as base58
    pub fn private_key_base58(&self) -> String {
        bs58::encode(self.keypair.to_bytes()).into_string()
    }

    /// Export keypair as JSON
    pub fn to_json(&self) -> Result<String> {
        let bytes = self.keypair.to_bytes();
        serde_json::to_string(&bytes.to_vec())
            .context("Failed to serialize keypair")
    }

    /// Get file path if loaded from file
    pub fn path(&self) -> Option<&Path> {
        self.path.as_deref()
    }
}

impl Default for WalletManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Load keypair from file (supports JSON array format)
pub fn load_keypair_from_file<P: AsRef<Path>>(path: P) -> Result<Keypair> {
    let path_ref = path.as_ref();

    if !path_ref.exists() {
        return Err(WalletError::FileNotFound(path_ref.display().to_string()).into());
    }

    let contents = fs::read_to_string(path_ref)
        .context("Failed to read keypair file")?;

    // Try parsing as JSON array
    if let Ok(bytes) = serde_json::from_str::<Vec<u8>>(&contents) {
        if bytes.len() == 64 {
            return Keypair::from_bytes(&bytes)
                .map_err(|e| WalletError::KeypairLoadError(e.to_string()).into());
        }
    }

    // Try parsing as base58
    if let Ok(bytes) = bs58::decode(contents.trim()).into_vec() {
        if bytes.len() == 64 {
            return Keypair::from_bytes(&bytes)
                .map_err(|e| WalletError::KeypairLoadError(e.to_string()).into());
        }
    }

    Err(WalletError::InvalidKeypairFormat.into())
}

/// Save keypair to file (JSON array format)
pub fn save_keypair_to_file<P: AsRef<Path>>(keypair: &Keypair, path: P) -> Result<()> {
    let path_ref = path.as_ref();

    // Create parent directories if they don't exist
    if let Some(parent) = path_ref.parent() {
        fs::create_dir_all(parent)
            .context("Failed to create parent directories")?;
    }

    let bytes = keypair.to_bytes();
    let json = serde_json::to_string_pretty(&bytes.to_vec())
        .context("Failed to serialize keypair")?;

    fs::write(path_ref, json)
        .context("Failed to write keypair file")?;

    log::info!("Keypair saved to: {}", path_ref.display());
    Ok(())
}

/// Get default Solana config directory
pub fn get_default_keypair_path() -> PathBuf {
    let home = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .unwrap_or_else(|_| ".".to_string());

    PathBuf::from(home)
        .join(".config")
        .join("solana")
        .join("id.json")
}

/// Try to load keypair from default Solana location
pub fn load_default_keypair() -> Result<Keypair> {
    let path = get_default_keypair_path();
    load_keypair_from_file(path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_new_wallet() {
        let wallet = WalletManager::new();
        assert!(!wallet.pubkey_string().is_empty());
    }

    #[test]
    fn test_wallet_json_roundtrip() {
        let wallet1 = WalletManager::new();
        let json = wallet1.to_json().unwrap();
        let wallet2 = WalletManager::from_json(&json).unwrap();

        assert_eq!(wallet1.pubkey_string(), wallet2.pubkey_string());
    }

    #[test]
    fn test_wallet_save_load() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test_keypair.json");

        let mut wallet1 = WalletManager::new();
        wallet1.save_to_file(&file_path).unwrap();

        let wallet2 = WalletManager::from_file(&file_path).unwrap();

        assert_eq!(wallet1.pubkey_string(), wallet2.pubkey_string());
    }
}
