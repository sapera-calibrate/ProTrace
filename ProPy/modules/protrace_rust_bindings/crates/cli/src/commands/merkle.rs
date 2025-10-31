//! Merkle tree command handlers

use anyhow::{Context, Result};
use colored::Colorize;
use protrace_image_dna::extract_dna_features;
use protrace_merkle_tree::MerkleTree;
use std::fs;
use std::path::PathBuf;

pub async fn handle_merkle_command(action: crate::MerkleCommands) -> Result<()> {
    match action {
        crate::MerkleCommands::Build {
            images,
            platform,
            output,
        } => build_merkle_tree(images, platform, output).await,
        crate::MerkleCommands::Proof { manifest, index } => {
            generate_proof(manifest, index).await
        }
        crate::MerkleCommands::Verify {
            manifest,
            proof,
            index,
        } => verify_proof(manifest, proof, index).await,
    }
}

async fn build_merkle_tree(
    images: Vec<PathBuf>,
    platform: String,
    output: Option<PathBuf>,
) -> Result<()> {
    println!(
        "{}",
        format!("Building Merkle tree from {} images...", images.len()).yellow()
    );

    let mut tree = MerkleTree::new();

    for (i, image) in images.iter().enumerate() {
        print!("  [{}/{}] Processing {}... ", i + 1, images.len(), image.display());

        match extract_dna_features(image) {
            Ok(features) => {
                let pointer = format!("uuid:{}", uuid::Uuid::new_v4());
                tree.add_leaf(&features.dna_hex, &pointer, &platform, None);
                println!("{}", "✓".bright_green());
            }
            Err(e) => {
                println!("{} {}", "✗".bright_red(), e);
            }
        }
    }

    println!();
    println!("{}", "Building tree structure...".yellow());
    let root = tree.build_tree().context("Failed to build tree")?;

    println!("{}", "🌳 Merkle Tree Built".bright_cyan().bold());
    println!("  📊 Total leaves: {}", tree.leaf_count());
    println!("  🔐 Root hash:");
    println!("    {}", root.bright_green());

    // Export manifest
    let manifest = tree.export_manifest().context("Failed to export manifest")?;
    let output_path = output.unwrap_or_else(|| PathBuf::from("merkle_manifest.json"));

    let json = serde_json::to_string_pretty(&manifest).context("Failed to serialize manifest")?;
    fs::write(&output_path, json).context("Failed to write manifest file")?;

    println!();
    println!("  📁 Manifest saved: {}", output_path.display());

    Ok(())
}

async fn generate_proof(manifest: PathBuf, index: usize) -> Result<()> {
    println!("{}", "Generating Merkle proof...".yellow());

    let manifest_data = fs::read_to_string(&manifest).context("Failed to read manifest")?;
    let manifest: protrace_merkle_tree::Manifest =
        serde_json::from_str(&manifest_data).context("Failed to parse manifest")?;

    let mut tree = MerkleTree::new();
    tree.import_manifest(&manifest)
        .context("Failed to import manifest")?;

    let proof = tree.get_proof(index).context("Failed to generate proof")?;

    println!("{}", "✅ Proof Generated".bright_cyan().bold());
    println!("  📊 Leaf index: {}", index);
    println!("  📝 Proof elements: {}", proof.len());
    println!();
    println!("  Proof path:");
    for (i, element) in proof.iter().enumerate() {
        println!(
            "    [{}] {} ({})",
            i,
            element.hash.bright_white(),
            format!("{:?}", element.position).bright_yellow()
        );
    }

    Ok(())
}

async fn verify_proof(manifest: PathBuf, proof_file: PathBuf, index: usize) -> Result<()> {
    println!("{}", "Verifying Merkle proof...".yellow());

    let manifest_data = fs::read_to_string(&manifest).context("Failed to read manifest")?;
    let manifest: protrace_merkle_tree::Manifest =
        serde_json::from_str(&manifest_data).context("Failed to parse manifest")?;

    let proof_data = fs::read_to_string(&proof_file).context("Failed to read proof")?;
    let proof: Vec<protrace_merkle_tree::ProofElement> =
        serde_json::from_str(&proof_data).context("Failed to parse proof")?;

    let mut tree = MerkleTree::new();
    tree.import_manifest(&manifest)
        .context("Failed to import manifest")?;

    let leaf_info = manifest
        .leaves
        .get(index)
        .context("Leaf index out of range")?;
    let leaf_data = format!(
        "{}|{}|{}|{}",
        leaf_info.dna_hex, leaf_info.pointer, leaf_info.platform_id, leaf_info.timestamp
    );

    let is_valid = tree
        .verify_proof(leaf_data.as_bytes(), &proof, &manifest.root)
        .context("Proof verification failed")?;

    if is_valid {
        println!("{}", "✅ PROOF VALID".bright_green().bold());
    } else {
        println!("{}", "❌ PROOF INVALID".bright_red().bold());
    }

    Ok(())
}
