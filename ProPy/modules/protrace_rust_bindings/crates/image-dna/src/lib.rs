//! ProTrace Image DNA Engine
//!
//! 256-bit DNA fingerprinting combining dHash (64-bit) + Grid (192-bit)
//! Designed for cross-platform NFT duplicate prevention.

use image::{DynamicImage, GenericImageView, ImageBuffer, Luma, Rgb};
use serde::{Deserialize, Serialize};
use std::path::Path;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DnaError {
    #[error("Failed to load image: {0}")]
    ImageLoadError(#[from] image::ImageError),
    #[error("Invalid hash format: {0}")]
    InvalidHashFormat(String),
    #[error("Hash length mismatch")]
    HashLengthMismatch,
}

/// DNA computation result containing all components
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DnaResult {
    pub dna_hex: String,        // 64 hex chars (256 bits)
    pub dna_binary: String,     // 256 binary chars
    pub dhash: String,          // 16 hex chars (64 bits)
    pub grid_hash: String,      // 48 hex chars (192 bits)
    pub algorithm: String,
    pub bits: u32,
}

/// DNA feature extraction result for compatibility
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DnaFeatures {
    pub dna_signature: String,
    pub dna_hex: String,
    pub dna_binary: String,
    pub dhash: String,
    pub grid_hash: String,
    pub algorithm: String,
    pub perceptual_hash: String,
    pub bits: u32,
}

/// Compute 256-bit DNA fingerprint (dHash + Grid)
pub fn compute_dna<P: AsRef<Path>>(image_path: P) -> Result<DnaResult, DnaError> {
    let img = image::open(image_path)?;
    compute_dna_from_image(&img)
}

/// Compute DNA from DynamicImage
pub fn compute_dna_from_image(img: &DynamicImage) -> Result<DnaResult, DnaError> {
    // Compute dHash (64-bit)
    let dhash = compute_dhash_legacy(img)?;
    
    // Compute Grid hash (192-bit)
    let grid_hash = compute_grid_hash(img)?;
    
    // Combine into 256-bit DNA
    let dna_hex = format!("{}{}", dhash.hash_hex, grid_hash.hash_hex);
    
    // Convert to binary representation
    let dna_int = u128::from_str_radix(&dna_hex[..32], 16).unwrap_or(0) as u128;
    let dna_int2 = u128::from_str_radix(&dna_hex[32..], 16).unwrap_or(0) as u128;
    let dna_binary = format!("{:0128b}{:0128b}", dna_int, dna_int2);
    
    Ok(DnaResult {
        dna_hex,
        dna_binary,
        dhash: dhash.hash_hex,
        grid_hash: grid_hash.hash_hex,
        algorithm: "dHash+Grid".to_string(),
        bits: 256,
    })
}

#[derive(Debug)]
struct HashResult {
    hash_hex: String,
    bits: Vec<u8>,
}

/// Legacy dHash implementation (matches Python version)
fn compute_dhash_legacy(img: &DynamicImage) -> Result<HashResult, DnaError> {
    // Crop to 512×512 center
    let (width, height) = img.dimensions();
    let crop_size = 512;
    let left = width.saturating_sub(crop_size) / 2;
    let top = height.saturating_sub(crop_size) / 2;
    let right = (left + crop_size).min(width);
    let bottom = (top + crop_size).min(height);
    
    let cropped = img.crop_imm(left, top, right - left, bottom - top);
    
    // Convert to grayscale
    let gray = cropped.to_luma8();
    
    // Apply Gaussian blur (simplified - using box blur approximation)
    let blurred = imageproc::filter::gaussian_blur_f32(&gray, 0.8);
    
    // Apply 4×4 block averaging to get 128×128 grid
    let (h, w) = blurred.dimensions();
    let block_size = 4;
    let new_w = w / block_size;
    let new_h = h / block_size;
    
    let mut gray_128 = ImageBuffer::new(new_w, new_h);
    for y in 0..new_h {
        for x in 0..new_w {
            let mut sum = 0u32;
            let mut count = 0u32;
            for by in 0..block_size {
                for bx in 0..block_size {
                    let px = x * block_size + bx;
                    let py = y * block_size + by;
                    if px < w && py < h {
                        sum += blurred.get_pixel(px, py)[0] as u32;
                        count += 1;
                    }
                }
            }
            let avg = if count > 0 { (sum / count) as u8 } else { 0 };
            gray_128.put_pixel(x, y, Luma([avg]));
        }
    }
    
    // Resize to 9×8 for dHash
    let small = image::imageops::resize(&gray_128, 9, 8, image::imageops::FilterType::Lanczos3);
    
    // Compute horizontal gradients
    let mut bits = Vec::with_capacity(64);
    for y in 0..8 {
        for x in 0..8 {
            let left = small.get_pixel(x, y)[0];
            let right = small.get_pixel(x + 1, y)[0];
            bits.push(if right > left { 1 } else { 0 });
        }
    }
    
    // Convert to hex (16 chars for 64 bits)
    let hash_hex = bits_to_hex(&bits);
    
    Ok(HashResult { hash_hex, bits })
}

/// Compute 192-bit Grid hash (matches Python version)
fn compute_grid_hash(img: &DynamicImage) -> Result<HashResult, DnaError> {
    // Pad to 2048×2048
    let padded = pad_to_square(img, 2048);
    
    // Extract center 1024×1024 (1/4)
    let (w, h) = padded.dimensions();
    let quarter_w = w / 2;
    let quarter_h = h / 2;
    let left = (w - quarter_w) / 2;
    let top = (h - quarter_h) / 2;
    
    let center = padded.crop_imm(left, top, quarter_w, quarter_h);
    let gray = center.to_luma8();
    
    let mut all_bits = Vec::new();
    
    // 8×8 grid (64 bits)
    let grid_8 = block_average(&gray, 128); // 1024/8 = 128
    let threshold_8 = compute_median(&grid_8);
    for val in grid_8.iter() {
        all_bits.push(if *val > threshold_8 { 1 } else { 0 });
    }
    
    // 12×12 grid downsampled to 8×8 (64 bits)
    let grid_12 = block_average(&gray, 85); // 1024/12 ≈ 85
    let threshold_12 = compute_median(&grid_12);
    let resized_12 = resize_grid(&grid_12, 12, threshold_12, 8, 8);
    all_bits.extend(resized_12);
    
    // 16×16 grid downsampled to 8×8 (64 bits)
    let grid_16 = block_average(&gray, 64); // 1024/16 = 64
    let threshold_16 = compute_median(&grid_16);
    let resized_16 = resize_grid(&grid_16, 16, threshold_16, 8, 8);
    all_bits.extend(resized_16);
    
    // Convert to hex (48 chars for 192 bits)
    let hash_hex = bits_to_hex(&all_bits);
    
    Ok(HashResult {
        hash_hex,
        bits: all_bits,
    })
}

/// Pad image to target_size × target_size with black padding
fn pad_to_square(img: &DynamicImage, target_size: u32) -> DynamicImage {
    let (w, h) = img.dimensions();
    
    if w >= target_size && h >= target_size {
        return img.clone();
    }
    
    let mut padded = DynamicImage::ImageRgb8(ImageBuffer::from_pixel(
        target_size,
        target_size,
        Rgb([0, 0, 0]),
    ));
    
    let paste_x = (target_size.saturating_sub(w)) / 2;
    let paste_y = (target_size.saturating_sub(h)) / 2;
    
    image::imageops::overlay(&mut padded, img, paste_x.into(), paste_y.into());
    
    padded
}

/// Block averaging for grid hash
fn block_average(img: &ImageBuffer<Luma<u8>, Vec<u8>>, block_size: u32) -> Vec<f32> {
    let (w, h) = img.dimensions();
    let new_w = w / block_size;
    let new_h = h / block_size;
    
    let mut result = Vec::new();
    
    for y in 0..new_h {
        for x in 0..new_w {
            let mut sum = 0u32;
            let mut count = 0u32;
            
            for by in 0..block_size {
                for bx in 0..block_size {
                    let px = x * block_size + bx;
                    let py = y * block_size + by;
                    if px < w && py < h {
                        sum += img.get_pixel(px, py)[0] as u32;
                        count += 1;
                    }
                }
            }
            
            result.push(if count > 0 {
                sum as f32 / count as f32
            } else {
                0.0
            });
        }
    }
    
    result
}

/// Compute median of values
fn compute_median(values: &[f32]) -> f32 {
    if values.is_empty() {
        return 0.0;
    }
    
    let mut sorted = values.to_vec();
    sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    
    let mid = sorted.len() / 2;
    if sorted.len() % 2 == 0 {
        (sorted[mid - 1] + sorted[mid]) / 2.0
    } else {
        sorted[mid]
    }
}

/// Resize grid to target dimensions
fn resize_grid(grid: &[f32], grid_size: usize, threshold: f32, target_h: usize, target_w: usize) -> Vec<u8> {
    // Simple nearest neighbor downsampling
    let mut result = Vec::new();
    let scale_x = grid_size as f32 / target_w as f32;
    let scale_y = grid_size as f32 / target_h as f32;
    
    for y in 0..target_h {
        for x in 0..target_w {
            let src_x = (x as f32 * scale_x) as usize;
            let src_y = (y as f32 * scale_y) as usize;
            let idx = src_y * grid_size + src_x;
            if idx < grid.len() {
                result.push(if grid[idx] > threshold { 1 } else { 0 });
            } else {
                result.push(0);
            }
        }
    }
    
    result
}

/// Convert bits to hex string
fn bits_to_hex(bits: &[u8]) -> String {
    let mut bytes = Vec::new();
    for chunk in bits.chunks(8) {
        let mut byte = 0u8;
        for (i, &bit) in chunk.iter().enumerate() {
            if bit != 0 {
                byte |= 1 << (7 - i);
            }
        }
        bytes.push(byte);
    }
    hex::encode(bytes)
}

/// Calculate Hamming distance between two DNA hashes
pub fn hamming_distance(hash1: &str, hash2: &str) -> Result<u32, DnaError> {
    if hash1.len() != hash2.len() {
        return Err(DnaError::HashLengthMismatch);
    }
    
    let bytes1 = hex::decode(hash1).map_err(|e| DnaError::InvalidHashFormat(e.to_string()))?;
    let bytes2 = hex::decode(hash2).map_err(|e| DnaError::InvalidHashFormat(e.to_string()))?;
    
    let mut distance = 0u32;
    for (b1, b2) in bytes1.iter().zip(bytes2.iter()) {
        distance += (b1 ^ b2).count_ones();
    }
    
    Ok(distance)
}

/// Calculate similarity percentage between two DNA hashes
pub fn dna_similarity(hash1: &str, hash2: &str) -> Result<f64, DnaError> {
    let distance = hamming_distance(hash1, hash2)?;
    Ok(1.0 - (distance as f64 / 256.0))
}

/// Check if two DNA hashes represent duplicate images
pub fn is_duplicate(hash1: &str, hash2: &str, threshold: u32) -> Result<bool, DnaError> {
    let distance = hamming_distance(hash1, hash2)?;
    Ok(distance <= threshold)
}

/// Extract DNA features with BLAKE3 signature
pub fn extract_dna_features<P: AsRef<Path>>(image_path: P) -> Result<DnaFeatures, DnaError> {
    let dna_result = compute_dna(image_path)?;
    
    // Compute BLAKE3 cryptographic hash for final signature
    let dna_signature = blake3::hash(dna_result.dna_hex.as_bytes()).to_hex().to_string();
    
    Ok(DnaFeatures {
        dna_signature: dna_signature.clone(),
        dna_hex: dna_result.dna_hex.clone(),
        dna_binary: dna_result.dna_binary,
        dhash: dna_result.dhash,
        grid_hash: dna_result.grid_hash,
        algorithm: dna_result.algorithm,
        perceptual_hash: dna_result.dna_hex,
        bits: 256,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hamming_distance() {
        let hash1 = "0000000000000000";
        let hash2 = "ffffffffffffffff";
        let distance = hamming_distance(hash1, hash2).unwrap();
        assert_eq!(distance, 64);
    }

    #[test]
    fn test_dna_similarity() {
        let hash1 = "0000000000000000";
        let hash2 = "0000000000000000";
        let similarity = dna_similarity(hash1, hash2).unwrap();
        assert_eq!(similarity, 1.0);
    }

    #[test]
    fn test_is_duplicate() {
        let hash1 = "0000000000000000";
        let hash2 = "0000000000000001";
        assert!(is_duplicate(hash1, hash2, 26).unwrap());
    }
}
