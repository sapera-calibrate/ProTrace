//! Wallet command handlers

use anyhow::{Context, Result};
use colored::Colorize;
use protrace_blockchain::ProTraceClient;
use protrace_wallet::WalletManager;
use solana_sdk::native_token::LAMPORTS_PER_SOL;
use solana_sdk::signature::Signer;
use std::path::PathBuf;

pub async fn handle_wallet_command(
    action: crate::WalletCommands,
    wallet_path: &str,
) -> Result<()> {
    match action {
        crate::WalletCommands::New { output } => create_new_wallet(output).await,
        crate::WalletCommands::Info => show_wallet_info(wallet_path).await,
        crate::WalletCommands::Airdrop { amount } => {
            request_airdrop(wallet_path, amount).await
        }
        crate::WalletCommands::Balance => get_balance(wallet_path).await,
    }
}

async fn create_new_wallet(output: PathBuf) -> Result<()> {
    println!("{}", "Creating new wallet...".yellow());

    let mut wallet = WalletManager::new();
    wallet
        .save_to_file(&output)
        .context("Failed to save wallet")?;

    println!("{}", "✅ Wallet created successfully!".green().bold());
    println!("  📁 Path: {}", output.display());
    println!("  🔑 Pubkey: {}", wallet.pubkey_string().bright_white());
    println!();
    println!(
        "{}",
        "⚠️  Save your keypair file securely!".bright_yellow()
    );

    Ok(())
}

async fn show_wallet_info(wallet_path: &str) -> Result<()> {
    println!("{}", "Loading wallet info...".yellow());

    let wallet = WalletManager::from_file(wallet_path)
        .context("Failed to load wallet")?;

    println!("{}", "📋 Wallet Information".bright_cyan().bold());
    println!("  🔑 Pubkey: {}", wallet.pubkey_string().bright_white());
    println!("  📁 Path: {}", wallet_path);

    Ok(())
}

async fn request_airdrop(wallet_path: &str, amount: f64) -> Result<()> {
    println!("{}", "Requesting airdrop...".yellow());

    let wallet = WalletManager::from_file(wallet_path)
        .context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    let lamports = (amount * LAMPORTS_PER_SOL as f64) as u64;
    let signature = client
        .request_airdrop(lamports)
        .await
        .context("Airdrop request failed")?;

    println!("{}", "✅ Airdrop successful!".green().bold());
    println!("  💰 Amount: {} SOL", amount);
    println!("  📝 Signature: {}", signature);

    Ok(())
}

async fn get_balance(wallet_path: &str) -> Result<()> {
    println!("{}", "Fetching balance...".yellow());

    let wallet = WalletManager::from_file(wallet_path)
        .context("Failed to load wallet")?;

    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;

    let balance = client.get_balance().await.context("Failed to get balance")?;
    let sol_balance = balance as f64 / LAMPORTS_PER_SOL as f64;

    println!("{}", "💰 Wallet Balance".bright_cyan().bold());
    println!("  🔑 Pubkey: {}", wallet.pubkey_string().bright_white());
    println!("  💵 Balance: {} SOL ({} lamports)", sol_balance, balance);

    Ok(())
}
