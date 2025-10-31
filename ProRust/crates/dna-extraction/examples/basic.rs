//! Basic DNA Extraction Example
//!
//! Run with: cargo run --example basic

use protrace_dna::DnaExtractor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("ProTrace DNA Extraction - Basic Example");
    println!("========================================\n");

    // Create extractor
    let extractor = DnaExtractor::new();

    // Example: Extract from test image (if available)
    let test_image = "../../data/test_images/# (1).png";

    match extractor.extract_from_path(test_image) {
        Ok(dna) => {
            println!("✓ Successfully extracted DNA fingerprint!\n");

            println!("Complete DNA Hash (256-bit):");
            println!("  {}\n", dna.hex());

            println!("Components:");
            println!("  dHash (64-bit):  {}", dna.dhash);
            println!("  Grid (192-bit):  {}\n", dna.grid_hash);

            println!("Binary representation ({} bits):", dna.binary().len());
            println!("  {}...\n", &dna.binary()[..64]);

            println!("Cryptographic signatures:");
            println!("  BLAKE3: {}", dna.blake3_signature());

            println!("\n✓ All done!");
        }
        Err(e) => {
            eprintln!("✗ Error: {}", e);
            eprintln!("\nNote: Make sure test images are available at:");
            eprintln!("  {}", test_image);
        }
    }

    Ok(())
}
