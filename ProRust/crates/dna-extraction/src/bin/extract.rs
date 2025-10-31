//! DNA Extraction CLI
//!
//! Command-line tool for extracting DNA fingerprints from images.

use protrace_dna::DnaExtractor;

#[cfg(feature = "cli")]
use clap::{Parser, Subcommand};

#[cfg(feature = "cli")]
#[derive(Parser)]
#[command(name = "dna-extract")]
#[command(about = "Extract 256-bit DNA fingerprints from images", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[cfg(feature = "cli")]
#[derive(Subcommand)]
enum Commands {
    /// Extract DNA from a single image
    Single {
        /// Path to image file
        #[arg(short, long)]
        input: PathBuf,

        /// Show detailed output
        #[arg(short, long)]
        verbose: bool,
    },
    /// Extract DNA from multiple images
    Batch {
        /// Paths to image files
        #[arg(short, long)]
        inputs: Vec<PathBuf>,

        /// Enable parallel processing
        #[arg(short, long)]
        parallel: bool,

        /// Show detailed output
        #[arg(short, long)]
        verbose: bool,
    },
    /// Compare two images for similarity
    Compare {
        /// Path to first image
        #[arg(short = '1', long)]
        image1: PathBuf,

        /// Path to second image
        #[arg(short = '2', long)]
        image2: PathBuf,

        /// Similarity threshold (0.0-1.0)
        #[arg(short, long, default_value_t = 0.9)]
        threshold: f64,
    },
}

#[cfg(feature = "cli")]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Single { input, verbose } => {
            let extractor = DnaExtractor::new();
            let dna = extractor.extract_from_path(&input)?;

            if verbose {
                println!("File: {}", input.display());
                println!("DNA Hash: {}", dna.hex());
                println!("dHash: {}", dna.dhash);
                println!("Grid Hash: {}", dna.grid_hash);
                println!("BLAKE3: {}", dna.blake3_signature());
            } else {
                println!("{}", dna.hex());
            }
        }
        Commands::Batch {
            inputs,
            parallel,
            verbose,
        } => {
            #[cfg(feature = "parallel")]
            let extractor = if parallel {
                DnaExtractor::new().with_parallel()
            } else {
                DnaExtractor::new()
            };

            #[cfg(not(feature = "parallel"))]
            let extractor = DnaExtractor::new();

            let results = extractor.extract_batch(&inputs);

            for (path, result) in inputs.iter().zip(results.iter()) {
                match result {
                    Ok(dna) => {
                        if verbose {
                            println!("File: {}", path.display());
                            println!("  DNA: {}", dna.hex());
                            println!("  dHash: {}", dna.dhash);
                            println!("  Grid: {}", dna.grid_hash);
                            println!();
                        } else {
                            println!("{}: {}", path.display(), dna.hex());
                        }
                    }
                    Err(e) => {
                        eprintln!("Error processing {}: {}", path.display(), e);
                    }
                }
            }
        }
        Commands::Compare {
            image1,
            image2,
            threshold,
        } => {
            let extractor = DnaExtractor::new();
            let dna1 = extractor.extract_from_path(&image1)?;
            let dna2 = extractor.extract_from_path(&image2)?;

            let similarity = dna1.similarity(&dna2);
            let hamming = dna1.hamming_distance(&dna2);

            println!("Image 1: {}", image1.display());
            println!("  DNA: {}", dna1.hex());
            println!();
            println!("Image 2: {}", image2.display());
            println!("  DNA: {}", dna2.hex());
            println!();
            println!("Similarity: {:.2}%", similarity * 100.0);
            println!("Hamming Distance: {} bits", hamming);
            println!();

            if similarity >= threshold {
                println!("✓ Images are DUPLICATES (≥{:.0}% threshold)", threshold * 100.0);
            } else {
                println!("✗ Images are NOT duplicates (<{:.0}% threshold)", threshold * 100.0);
            }
        }
    }

    Ok(())
}

#[cfg(not(feature = "cli"))]
fn main() {
    eprintln!("This binary requires the 'cli' feature to be enabled.");
    eprintln!("Build with: cargo build --features cli");
    std::process::exit(1);
}
