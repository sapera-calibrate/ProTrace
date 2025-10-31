//! ProTrace CLI - Command Line Interface for blockchain testing

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use colored::Colorize;
use protrace_blockchain::{manifest_to_anchor_params, ProTraceClient};
use protrace_image_dna::{compute_dna, extract_dna_features, hamming_distance, is_duplicate};
use protrace_merkle_tree::MerkleTree;
use protrace_wallet::WalletManager;
use solana_sdk::signature::Signer;
use std::path::PathBuf;

mod commands;

#[derive(Parser)]
#[command(name = "protrace")]
#[command(about = "ProTrace - NFT Duplicate Prevention on Solana Devnet", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,

    /// Wallet keypair file path
    #[arg(short, long, global = true, default_value = "~/.config/solana/id.json")]
    wallet: String,

    /// Enable verbose logging
    #[arg(short, long, global = true)]
    verbose: bool,
}

#[derive(Subcommand)]
enum Commands {
    /// Wallet operations
    Wallet {
        #[command(subcommand)]
        action: WalletCommands,
    },

    /// Image DNA operations
    Dna {
        #[command(subcommand)]
        action: DnaCommands,
    },

    /// Merkle tree operations
    Merkle {
        #[command(subcommand)]
        action: MerkleCommands,
    },

    /// Blockchain operations
    Blockchain {
        #[command(subcommand)]
        action: BlockchainCommands,
    },

    /// Run complete end-to-end test
    Test {
        /// Image files to test
        #[arg(required = true)]
        images: Vec<PathBuf>,
    },
}

#[derive(Subcommand)]
enum WalletCommands {
    /// Create new wallet
    New {
        /// Output file path
        #[arg(short, long)]
        output: PathBuf,
    },

    /// Show wallet info
    Info,

    /// Request devnet airdrop
    Airdrop {
        /// Amount in SOL
        #[arg(default_value = "1.0")]
        amount: f64,
    },

    /// Get wallet balance
    Balance,
}

#[derive(Subcommand)]
enum DnaCommands {
    /// Compute DNA hash for an image
    Compute {
        /// Image file path
        image: PathBuf,
    },

    /// Compare two images
    Compare {
        /// First image
        image1: PathBuf,
        /// Second image
        image2: PathBuf,
    },

    /// Batch compute DNA for multiple images
    Batch {
        /// Image files
        images: Vec<PathBuf>,
    },
}

#[derive(Subcommand)]
enum MerkleCommands {
    /// Build Merkle tree from images
    Build {
        /// Image files
        images: Vec<PathBuf>,
        /// Platform ID
        #[arg(short, long, default_value = "devnet-test")]
        platform: String,
        /// Output file
        #[arg(short, long)]
        output: Option<PathBuf>,
    },

    /// Generate proof for specific image
    Proof {
        /// Manifest file
        manifest: PathBuf,
        /// Image index
        index: usize,
    },

    /// Verify proof
    Verify {
        /// Manifest file
        manifest: PathBuf,
        /// Proof file
        proof: PathBuf,
        /// Leaf index
        index: usize,
    },
}

#[derive(Subcommand)]
enum BlockchainCommands {
    /// Initialize Merkle root on blockchain
    InitRoot {
        /// Root hash (hex)
        root: String,
    },

    /// Update Merkle root
    UpdateRoot {
        /// New root hash (hex)
        root: String,
    },

    /// Anchor Merkle root via oracle
    Anchor {
        /// Manifest file
        manifest: PathBuf,
    },

    /// Initialize edition registry
    InitRegistry {
        /// Oracle authority pubkey (defaults to wallet)
        #[arg(short, long)]
        oracle: Option<String>,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize logger
    let log_level = if cli.verbose { "debug" } else { "info" };
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or(log_level))
        .init();

    println!("{}", "🔒 ProTrace - NFT Duplicate Prevention".bright_cyan().bold());
    println!("{}", "─".repeat(50).bright_black());

    match cli.command {
        Commands::Wallet { action } => {
            commands::wallet::handle_wallet_command(action, &cli.wallet).await
        }
        Commands::Dna { action } => commands::dna::handle_dna_command(action).await,
        Commands::Merkle { action } => commands::merkle::handle_merkle_command(action).await,
        Commands::Blockchain { action } => {
            commands::blockchain::handle_blockchain_command(action, &cli.wallet).await
        }
        Commands::Test { images } => commands::test::run_end_to_end_test(images, &cli.wallet).await,
    }
}
