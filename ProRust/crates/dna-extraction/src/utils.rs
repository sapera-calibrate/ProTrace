//! Utility Functions
//!
//! Helper functions for DNA hash comparison and analysis.

// Utility functions - no imports needed

/// Calculate Hamming distance between two DNA hashes
///
/// Returns the number of differing bits (0-256)
///
/// # Example
///
/// ```
/// use protrace_dna::utils::hamming_distance;
///
/// let hash1 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// let hash2 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// assert_eq!(hamming_distance(hash1, hash2), 0);
/// ```
pub fn hamming_distance(hash1: &str, hash2: &str) -> u32 {
    if hash1.len() != hash2.len() {
        return u32::MAX; // Invalid comparison
    }

    let bytes1 = hex::decode(hash1).unwrap_or_default();
    let bytes2 = hex::decode(hash2).unwrap_or_default();

    bytes1
        .iter()
        .zip(bytes2.iter())
        .map(|(b1, b2)| (b1 ^ b2).count_ones())
        .sum()
}

/// Calculate similarity percentage between two DNA hashes
///
/// Returns value from 0.0 (completely different) to 1.0 (identical)
///
/// # Example
///
/// ```
/// use protrace_dna::utils::similarity;
///
/// let hash1 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// let hash2 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// assert_eq!(similarity(hash1, hash2), 1.0);
/// ```
pub fn similarity(hash1: &str, hash2: &str) -> f64 {
    let distance = hamming_distance(hash1, hash2) as f64;
    1.0 - (distance / 256.0)
}

/// Check if two hashes represent duplicate images
///
/// Default threshold: ≤26 bits = ≥90% similarity
///
/// # Example
///
/// ```
/// use protrace_dna::utils::is_duplicate;
///
/// let hash1 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// let hash2 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
/// assert!(is_duplicate(hash1, hash2, 26));
/// ```
pub fn is_duplicate(hash1: &str, hash2: &str, threshold: u32) -> bool {
    hamming_distance(hash1, hash2) <= threshold
}

/// Convert hex string to binary string
pub fn hex_to_binary(hex: &str) -> String {
    let bytes = hex::decode(hex).unwrap_or_default();
    bytes
        .iter()
        .map(|b| format!("{:08b}", b))
        .collect::<String>()
}

/// Convert binary string to hex string
pub fn binary_to_hex(binary: &str) -> String {
    let mut hex = String::new();
    for chunk in binary.as_bytes().chunks(8) {
        let byte_str = std::str::from_utf8(chunk).unwrap_or("00000000");
        let byte = u8::from_str_radix(byte_str, 2).unwrap_or(0);
        hex.push_str(&format!("{:02x}", byte));
    }
    hex
}

/// Find all duplicate pairs in a batch of DNA hashes
///
/// Returns list of (index1, index2, hamming_distance)
pub fn find_duplicate_pairs(
    hashes: &[String],
    threshold: u32,
) -> Vec<(usize, usize, u32)> {
    let mut duplicates = Vec::new();

    for i in 0..hashes.len() {
        for j in (i + 1)..hashes.len() {
            let distance = hamming_distance(&hashes[i], &hashes[j]);
            if distance <= threshold {
                duplicates.push((i, j, distance));
            }
        }
    }

    duplicates
}

/// Compute BLAKE3 hash of a DNA fingerprint
pub fn blake3_signature(dna_hex: &str) -> String {
    hex::encode(blake3::hash(dna_hex.as_bytes()).as_bytes())
}

/// Compute SHA256 hash of a DNA fingerprint
pub fn sha256_signature(dna_hex: &str) -> String {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(dna_hex.as_bytes());
    hex::encode(hasher.finalize())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hamming_distance_identical() {
        let hash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        assert_eq!(hamming_distance(hash, hash), 0);
    }

    #[test]
    fn test_hamming_distance_different() {
        let hash1 = "0000000000000000000000000000000000000000000000000000000000000000";
        let hash2 = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";
        assert_eq!(hamming_distance(hash1, hash2), 256);
    }

    #[test]
    fn test_similarity() {
        let hash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        assert_eq!(similarity(hash, hash), 1.0);
    }

    #[test]
    fn test_is_duplicate() {
        let hash1 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        let hash2 = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        assert!(is_duplicate(hash1, hash2, 26));
    }

    #[test]
    fn test_hex_to_binary() {
        let hex = "ff";
        let binary = hex_to_binary(hex);
        assert_eq!(binary, "11111111");
    }

    #[test]
    fn test_binary_to_hex() {
        let binary = "11111111";
        let hex = binary_to_hex(binary);
        assert_eq!(hex, "ff");
    }

    #[test]
    fn test_blake3_signature() {
        let dna = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        let sig = blake3_signature(dna);
        assert_eq!(sig.len(), 64); // BLAKE3 outputs 256 bits = 64 hex chars
    }

    #[test]
    fn test_find_duplicate_pairs() {
        let hashes = vec![
            "0000000000000000000000000000000000000000000000000000000000000000".to_string(),
            "0000000000000000000000000000000000000000000000000000000000000001".to_string(),
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff".to_string(),
        ];

        let pairs = find_duplicate_pairs(&hashes, 5);
        assert_eq!(pairs.len(), 1); // Only first two are similar enough
        assert_eq!(pairs[0], (0, 1, 1));
    }
}
