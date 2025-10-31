//! Blockchain command handlers

use anyhow::{Context, Result};
use colored::Colorize;
use protrace_blockchain::{manifest_to_anchor_params, ProTraceClient};
use protrace_wallet::WalletManager;
use solana_sdk::pubkey::Pubkey;
use solana_sdk::signature::Signer;
use std::fs;
use std::path::PathBuf;
use std::str::FromStr;

pub async fn handle_blockchain_command(
    action: crate::BlockchainCommands,
    wallet_path: &str,
) -> Result<()> {
    match action {
        crate::BlockchainCommands::InitRoot { root } => init_merkle_root(wallet_path, root).await,
        crate::BlockchainCommands::UpdateRoot { root } => {
            update_merkle_root(wallet_path, root).await
        }
        crate::BlockchainCommands::Anchor { manifest } => {
            anchor_merkle_root(wallet_path, manifest).await
        }
        crate::BlockchainCommands::InitRegistry { oracle } => {
            init_edition_registry(wallet_path, oracle).await
        }
    }
}

async fn init_merkle_root(wallet_path: &str, root: String) -> Result<()> {
    println!("{}", "Initializing Merkle root on blockchain...".yellow());

    let wallet = WalletManager::from_file(wallet_path).context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    // Parse root hash
    let root_bytes = hex::decode(&root).context("Invalid root hash format")?;
    if root_bytes.len() != 32 {
        anyhow::bail!("Root hash must be 32 bytes");
    }
    let mut root_array = [0u8; 32];
    root_array.copy_from_slice(&root_bytes);

    let signature = client
        .initialize_merkle_root(root_array)
        .await
        .context("Failed to initialize Merkle root")?;

    println!("{}", "✅ Merkle Root Initialized".bright_green().bold());
    println!("  🔐 Root: {}", root.bright_white());
    println!("  📝 Transaction: {}", signature);
    println!(
        "  🔗 Explorer: {}",
        format!(
            "https://explorer.solana.com/tx/{}?cluster=devnet",
            signature
        )
        .bright_blue()
    );

    Ok(())
}

async fn update_merkle_root(wallet_path: &str, root: String) -> Result<()> {
    println!("{}", "Updating Merkle root on blockchain...".yellow());

    let wallet = WalletManager::from_file(wallet_path).context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    // Parse root hash
    let root_bytes = hex::decode(&root).context("Invalid root hash format")?;
    if root_bytes.len() != 32 {
        anyhow::bail!("Root hash must be 32 bytes");
    }
    let mut root_array = [0u8; 32];
    root_array.copy_from_slice(&root_bytes);

    let signature = client
        .update_merkle_root(root_array)
        .await
        .context("Failed to update Merkle root")?;

    println!("{}", "✅ Merkle Root Updated".bright_green().bold());
    println!("  🔐 New Root: {}", root.bright_white());
    println!("  📝 Transaction: {}", signature);
    println!(
        "  🔗 Explorer: {}",
        format!(
            "https://explorer.solana.com/tx/{}?cluster=devnet",
            signature
        )
        .bright_blue()
    );

    Ok(())
}

async fn anchor_merkle_root(wallet_path: &str, manifest: PathBuf) -> Result<()> {
    println!("{}", "Anchoring Merkle root via oracle...".yellow());

    let wallet = WalletManager::from_file(wallet_path).context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    // Load manifest
    let manifest_data = fs::read_to_string(&manifest).context("Failed to read manifest")?;
    let manifest: protrace_merkle_tree::Manifest =
        serde_json::from_str(&manifest_data).context("Failed to parse manifest")?;

    println!("  📊 Manifest loaded:");
    println!("    Total leaves: {}", manifest.total_leaves);
    println!("    Root: {}", manifest.root.bright_white());

    // Convert manifest to anchor params
    let (root, _cid, asset_count, timestamp) = manifest_to_anchor_params(&manifest);

    let signature = client
        .anchor_merkle_root_oracle(root, manifest.root.clone(), asset_count, timestamp)
        .await
        .context("Failed to anchor Merkle root")?;

    println!();
    println!("{}", "✅ Merkle Root Anchored".bright_green().bold());
    println!("  🔐 Root: {}", hex::encode(root).bright_white());
    println!("  📦 Assets: {}", asset_count);
    println!("  📝 Transaction: {}", signature);
    println!(
        "  🔗 Explorer: {}",
        format!(
            "https://explorer.solana.com/tx/{}?cluster=devnet",
            signature
        )
        .bright_blue()
    );

    Ok(())
}

async fn init_edition_registry(wallet_path: &str, oracle: Option<String>) -> Result<()> {
    println!("{}", "Initializing edition registry...".yellow());

    let wallet = WalletManager::from_file(wallet_path).context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    let oracle_pubkey = if let Some(oracle_str) = oracle {
        Pubkey::from_str(&oracle_str).context("Invalid oracle pubkey")?
    } else {
        wallet.keypair().pubkey()
    };

    let signature = client
        .initialize_edition_registry(oracle_pubkey)
        .await
        .context("Failed to initialize edition registry")?;

    println!("{}", "✅ Edition Registry Initialized".bright_green().bold());
    println!("  👤 Oracle: {}", oracle_pubkey);
    println!("  📝 Transaction: {}", signature);
    println!(
        "  🔗 Explorer: {}",
        format!(
            "https://explorer.solana.com/tx/{}?cluster=devnet",
            signature
        )
        .bright_blue()
    );

    Ok(())
}
