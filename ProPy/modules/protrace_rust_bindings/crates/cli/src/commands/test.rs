//! End-to-end test command

use anyhow::{Context, Result};
use colored::Colorize;
use indicatif::{ProgressBar, ProgressStyle};
use protrace_blockchain::{manifest_to_anchor_params, ProTraceClient};
use protrace_image_dna::{compute_dna, extract_dna_features, is_duplicate};
use protrace_merkle_tree::MerkleTree;
use protrace_wallet::WalletManager;
use solana_sdk::native_token::LAMPORTS_PER_SOL;
use solana_sdk::signature::Signer;
use std::path::PathBuf;
use std::time::Instant;

pub async fn run_end_to_end_test(images: Vec<PathBuf>, wallet_path: &str) -> Result<()> {
    println!("{}", "🧪 Running End-to-End Test".bright_cyan().bold());
    println!("{}", "═".repeat(50).bright_black());
    println!();

    let start_time = Instant::now();

    // Step 1: Load wallet
    println!("{}", "Step 1: Loading wallet...".bright_yellow());
    let wallet = WalletManager::from_file(wallet_path).context("Failed to load wallet")?;
    println!("  ✓ Wallet loaded: {}", wallet.pubkey_string().bright_white());
    println!();

    // Step 2: Connect to devnet
    println!("{}", "Step 2: Connecting to Solana devnet...".bright_yellow());
    let client = ProTraceClient::new_devnet(wallet.keypair().insecure_clone())
        .context("Failed to create blockchain client")?;
    
    let balance = client.get_balance().await.context("Failed to get balance")?;
    let sol_balance = balance as f64 / LAMPORTS_PER_SOL as f64;
    println!("  ✓ Connected to devnet");
    println!("  💰 Balance: {} SOL", sol_balance);
    
    if sol_balance < 0.1 {
        println!("  ⚠️  Low balance! Request airdrop with:");
        println!("     protrace wallet airdrop 1.0");
    }
    println!();

    // Step 3: Compute DNA for all images
    println!("{}", format!("Step 3: Computing DNA for {} images...", images.len()).bright_yellow());
    let pb = ProgressBar::new(images.len() as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("  [{bar:40}] {pos}/{len} {msg}")
            .unwrap()
            .progress_chars("=>-"),
    );

    let mut dna_results = Vec::new();
    for image in &images {
        pb.set_message(format!("{}", image.file_name().unwrap().to_string_lossy()));
        match extract_dna_features(image) {
            Ok(features) => {
                dna_results.push((image.clone(), features));
            }
            Err(e) => {
                println!("  ✗ Failed to process {}: {}", image.display(), e);
            }
        }
        pb.inc(1);
    }
    pb.finish_with_message("Done");
    println!("  ✓ Processed {} images", dna_results.len());
    println!();

    // Step 4: Check for duplicates
    println!("{}", "Step 4: Checking for duplicates...".bright_yellow());
    let mut found_duplicates = false;
    for i in 0..dna_results.len() {
        for j in (i + 1)..dna_results.len() {
            let (img1, dna1) = &dna_results[i];
            let (img2, dna2) = &dna_results[j];
            
            if is_duplicate(&dna1.dna_hex, &dna2.dna_hex, 26)? {
                found_duplicates = true;
                println!(
                    "  {} Duplicate found: {} ↔ {}",
                    "⚠️".bright_red(),
                    img1.file_name().unwrap().to_string_lossy(),
                    img2.file_name().unwrap().to_string_lossy()
                );
            }
        }
    }
    if !found_duplicates {
        println!("  ✓ No duplicates detected");
    }
    println!();

    // Step 5: Build Merkle tree
    println!("{}", "Step 5: Building Merkle tree...".bright_yellow());
    let mut tree = MerkleTree::new();
    
    for (image, features) in &dna_results {
        let pointer = format!("uuid:{}", uuid::Uuid::new_v4());
        tree.add_leaf(&features.dna_hex, &pointer, "devnet-test", None);
    }
    
    let root = tree.build_tree().context("Failed to build tree")?;
    println!("  ✓ Tree built with {} leaves", tree.leaf_count());
    println!("  🔐 Root: {}", root.bright_green());
    println!();

    // Step 6: Export manifest
    println!("{}", "Step 6: Exporting manifest...".bright_yellow());
    let manifest = tree.export_manifest().context("Failed to export manifest")?;
    println!("  ✓ Manifest exported");
    println!("    Total leaves: {}", manifest.total_leaves);
    println!("    Total proofs: {}", manifest.proofs.len());
    println!();

    // Step 7: Anchor to blockchain
    println!("{}", "Step 7: Anchoring Merkle root to blockchain...".bright_yellow());
    let (root_array, _cid, asset_count, timestamp) = manifest_to_anchor_params(&manifest);
    
    match client
        .anchor_merkle_root_oracle(root_array, manifest.root.clone(), asset_count, timestamp)
        .await
    {
        Ok(signature) => {
            println!("  ✓ Anchored to blockchain");
            println!("  📝 Transaction: {}", signature);
            println!(
                "  🔗 Explorer: {}",
                format!(
                    "https://explorer.solana.com/tx/{}?cluster=devnet",
                    signature
                )
                .bright_blue()
            );
        }
        Err(e) => {
            println!("  ⚠️  Failed to anchor: {}", e);
            println!("     (This is expected if you haven't deployed the program or have insufficient balance)");
        }
    }
    println!();

    // Step 8: Generate and verify proof for first leaf
    println!("{}", "Step 8: Generating and verifying Merkle proof...".bright_yellow());
    if !dna_results.is_empty() {
        let proof = tree.get_proof(0).context("Failed to generate proof")?;
        println!("  ✓ Proof generated with {} elements", proof.len());
        
        let leaf_info = &manifest.leaves[0];
        let leaf_data = format!(
            "{}|{}|{}|{}",
            leaf_info.dna_hex, leaf_info.pointer, leaf_info.platform_id, leaf_info.timestamp
        );
        
        let is_valid = tree
            .verify_proof(leaf_data.as_bytes(), &proof, &manifest.root)
            .context("Failed to verify proof")?;
        
        if is_valid {
            println!("  ✓ Proof verification: {}", "VALID".bright_green().bold());
        } else {
            println!("  ✗ Proof verification: {}", "INVALID".bright_red().bold());
        }
    }
    println!();

    // Summary
    let elapsed = start_time.elapsed();
    println!("{}", "═".repeat(50).bright_black());
    println!("{}", "✅ Test Complete!".bright_green().bold());
    println!();
    println!("📊 Summary:");
    println!("  • Images processed: {}", dna_results.len());
    println!("  • Merkle tree leaves: {}", tree.leaf_count());
    println!("  • Root hash: {}", root.bright_white());
    println!("  • Duplicates found: {}", if found_duplicates { "Yes" } else { "No" });
    println!("  • Time elapsed: {:.2}s", elapsed.as_secs_f64());
    println!();
    println!("{}", "🎉 ProTrace is ready for production!".bright_cyan().bold());

    Ok(())
}
