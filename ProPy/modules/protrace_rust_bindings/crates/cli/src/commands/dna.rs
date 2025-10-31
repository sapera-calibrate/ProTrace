//! DNA command handlers

use anyhow::{Context, Result};
use colored::Colorize;
use protrace_image_dna::{compute_dna, hamming_distance, is_duplicate};
use std::path::PathBuf;

pub async fn handle_dna_command(action: crate::DnaCommands) -> Result<()> {
    match action {
        crate::DnaCommands::Compute { image } => compute_dna_hash(image).await,
        crate::DnaCommands::Compare { image1, image2 } => compare_images(image1, image2).await,
        crate::DnaCommands::Batch { images } => batch_compute_dna(images).await,
    }
}

async fn compute_dna_hash(image: PathBuf) -> Result<()> {
    println!("{}", "Computing DNA hash...".yellow());

    let dna = compute_dna(&image).context("Failed to compute DNA")?;

    println!("{}", "🧬 DNA Fingerprint".bright_cyan().bold());
    println!("  📁 File: {}", image.display());
    println!("  🔢 Algorithm: {}", dna.algorithm.bright_white());
    println!("  📊 Bits: {}", dna.bits);
    println!();
    println!("  🔐 DNA Hash (256-bit):");
    println!("    {}", dna.dna_hex.bright_green());
    println!();
    println!("  Component Hashes:");
    println!("    dHash (64-bit): {}", dna.dhash.bright_yellow());
    println!("    Grid (192-bit): {}", dna.grid_hash.bright_blue());

    Ok(())
}

async fn compare_images(image1: PathBuf, image2: PathBuf) -> Result<()> {
    println!("{}", "Comparing images...".yellow());

    let dna1 = compute_dna(&image1).context("Failed to compute DNA for image 1")?;
    let dna2 = compute_dna(&image2).context("Failed to compute DNA for image 2")?;

    let distance = hamming_distance(&dna1.dna_hex, &dna2.dna_hex)
        .context("Failed to calculate distance")?;
    let similarity = 1.0 - (distance as f64 / 256.0);
    let duplicate = is_duplicate(&dna1.dna_hex, &dna2.dna_hex, 26)?;

    println!("{}", "🔍 Image Comparison".bright_cyan().bold());
    println!("  📁 Image 1: {}", image1.display());
    println!("  📁 Image 2: {}", image2.display());
    println!();
    println!("  📊 Analysis:");
    println!("    Hamming Distance: {}", distance);
    println!("    Similarity: {:.2}%", similarity * 100.0);
    println!(
        "    Duplicate: {}",
        if duplicate {
            "YES ⚠️".bright_red().bold()
        } else {
            "NO ✓".bright_green()
        }
    );
    println!();
    println!("  🔐 DNA Hashes:");
    println!("    Image 1: {}", dna1.dna_hex.bright_yellow());
    println!("    Image 2: {}", dna2.dna_hex.bright_blue());

    Ok(())
}

async fn batch_compute_dna(images: Vec<PathBuf>) -> Result<()> {
    println!("{}", format!("Computing DNA for {} images...", images.len()).yellow());

    let mut results = Vec::new();

    for (i, image) in images.iter().enumerate() {
        print!("  [{}/{}] {}... ", i + 1, images.len(), image.display());
        match compute_dna(image) {
            Ok(dna) => {
                println!("{}", "✓".bright_green());
                results.push((image.clone(), dna));
            }
            Err(e) => {
                println!("{} {}", "✗".bright_red(), e);
            }
        }
    }

    println!();
    println!("{}", "🧬 Batch DNA Results".bright_cyan().bold());
    println!("  Total processed: {}", results.len());
    println!();

    for (image, dna) in &results {
        println!("  📁 {}", image.file_name().unwrap().to_string_lossy());
        println!("    {}", dna.dna_hex.bright_white());
    }

    // Check for duplicates
    println!();
    println!("{}", "🔍 Duplicate Detection".bright_cyan().bold());
    let mut found_duplicates = false;

    for i in 0..results.len() {
        for j in (i + 1)..results.len() {
            let (img1, dna1) = &results[i];
            let (img2, dna2) = &results[j];

            if is_duplicate(&dna1.dna_hex, &dna2.dna_hex, 26)? {
                found_duplicates = true;
                let distance = hamming_distance(&dna1.dna_hex, &dna2.dna_hex)?;
                println!(
                    "  {} ⚠️",
                    "DUPLICATE FOUND".bright_red().bold()
                );
                println!("    {} ↔ {}", 
                    img1.file_name().unwrap().to_string_lossy(),
                    img2.file_name().unwrap().to_string_lossy()
                );
                println!("    Distance: {}", distance);
            }
        }
    }

    if !found_duplicates {
        println!("  {} No duplicates detected", "✓".bright_green());
    }

    Ok(())
}
