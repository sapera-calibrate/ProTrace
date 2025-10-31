"""
ProTrace Core Protocol
=====================

Core protocol functionality for digital asset verification.
"""

import logging
from typing import Dict, List, Optional
from .image_dna import extract_dna_features
import hashlib
import time
import json
from pathlib import Path
import numpy as np
from PIL import Image
import os
import sys

logger = logging.getLogger(__name__)

# Store processed images and their hashes for similarity-based deduplication
_processed_images = {}

def dna_hash_perceptual(image_path: str, hash_size: int = 8) -> str:
    """
    Improved UTGMH DNA Extraction with Perceptual Hashing.

    Uses gradient-based hashing for fuzzy similarity matching.

    Args:
        image_path: Path to image file
        hash_size: Size of hash grid (default 8x8 = 64-bit hash)

    Returns:
        Hex string representation of perceptual hash
    """
    try:
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)

        # Convert to grayscale
        gray = np.mean(img_array, axis=2).astype(np.float32)

        # Resize to hash_size + 1 for gradient computation
        resized = np.array(Image.fromarray(gray).resize((hash_size + 1, hash_size), Image.LANCZOS))

        # Compute horizontal gradients (difference hash)
        diff = resized[:, 1:] > resized[:, :-1]  # Compare adjacent pixels

        # Flatten to bit array
        hash_bits = diff.flatten()

        # Convert to bytes and then hex
        hash_bytes = np.packbits(hash_bits.astype(np.uint8))
        hash_hex = ''.join(f'{b:02x}' for b in hash_bytes)

        return hash_hex

    except Exception as e:
        return f"Error processing {image_path}: {str(e)}"

def dna_similarity(hash1: str, hash2: str) -> float:
    """
    Calculate similarity between two DNA hashes using Hamming distance.

    Args:
        hash1: First DNA hash (hex string)
        hash2: Second DNA hash (hex string)

    Returns:
        Similarity score between 0.0 and 1.0 (1.0 = identical)
    """
    if len(hash1) != len(hash2):
        return 0.0

    try:
        # Convert hex to bytes
        bytes1 = bytes.fromhex(hash1)
        bytes2 = bytes.fromhex(hash2)

        # Calculate Hamming distance
        hamming_distance = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(bytes1, bytes2))

        # Maximum possible distance = 8 * len(bytes)
        max_distance = 8 * len(bytes1)

        # Similarity = 1 - (distance / max_distance)
        similarity = 1.0 - (hamming_distance / max_distance)

        return similarity

    except Exception:
        return 0.0

def dna_hash(image_path: str, bin_size: int = 1) -> str:
    """
    Enhanced UTGMH DNA hash with similarity-based deduplication.

    Images with >80% similarity get the same DNA hash.
    Returns 64-character BLAKE3-style hash for compatibility.

    Args:
        image_path: Path to image file

    Returns:
        64-character hex string (32 bytes)
    """
    global _processed_images

    try:
        # Generate perceptual hash
        perceptual_hash = dna_hash_perceptual(image_path)

        # Check similarity against previously processed images
        best_match_hash = None
        best_similarity = 0.0

        for existing_path, existing_hash in _processed_images.items():
            similarity = dna_similarity(perceptual_hash, dna_hash_perceptual(existing_path))
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_hash = existing_hash

        # If similarity > 80%, use the existing hash
        if best_similarity > 0.80 and best_match_hash:
            final_hash = best_match_hash
        else:
            # Generate new 32-byte hash from perceptual hash
            # Extend perceptual hash to 32 bytes by repeating and hashing
            extended_data = (perceptual_hash * 4)[:64]  # Repeat to get more data
            final_hash = hashlib.sha256(extended_data.encode()).hexdigest()
            _processed_images[image_path] = final_hash

        return final_hash

    except Exception as e:
        # Fallback: generate hash from error message
        error_str = f"Error:{image_path}:{str(e)}"
        return hashlib.sha256(error_str.encode()).hexdigest()

class CoreProtocol:
    """Placeholder for CoreProtocol class"""

    def __init__(self, registry_dir: str = "registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        self.assets = {}  # asset_id -> fingerprint data
        self.merkle_leaves = []  # list of asset_ids in registration order
        self._load_registry()

    def register_asset(self, asset_path: str, creator_id: str):
        """Register an asset with ProTrace fingerprinting"""
        logger.info(f"Registering asset: {asset_path} for creator: {creator_id}")

        try:
            # Extract DNA features from the image
            dna_data = extract_dna_features(asset_path)

            # Generate asset ID from DNA signature
            asset_id = dna_data['dna_signature'][:32]  # Use first 32 chars as asset ID

            # Check for duplicates: if asset with same DNA already exists, don't register
            existing_dna_hashes = set()
            for asset in self.assets.values():
                fingerprint = asset['fingerprint']
                # Handle both object and dict formats (when loaded from JSON)
                if hasattr(fingerprint, 'dna_hash'):
                    existing_dna_hashes.add(fingerprint.dna_hash)
                elif isinstance(fingerprint, dict) and 'dna_hash' in fingerprint:
                    existing_dna_hashes.add(fingerprint['dna_hash'])

            if dna_data['dna_signature'] in existing_dna_hashes:
                logger.warning(f"🚫 Duplicate DNA detected! Asset {asset_path} has same DNA as existing asset. Registration blocked.")
                # Find the existing asset
                for existing_id, existing_data in self.assets.items():
                    fingerprint = existing_data['fingerprint']
                    existing_dna = fingerprint.dna_hash if hasattr(fingerprint, 'dna_hash') else fingerprint.get('dna_hash', '')
                    if existing_dna == dna_data['dna_signature']:
                        logger.info(f"   Matches existing asset: {existing_id}")
                        break
                return None  # Return None to indicate registration was blocked

            # Create fingerprint object
            class Fingerprint:
                def __init__(self, asset_id, creator, dna_signature, features, image_info):
                    self.asset_id = asset_id
                    self.creator = creator
                    self.dna_hash = dna_signature  # UTGMH DNA hash
                    self.timestamp = int(time.time())
                    self.features = features
                    self.image_info = image_info

            fingerprint = Fingerprint(
                asset_id=asset_id,
                creator=creator_id,
                dna_signature=dna_data['dna_signature'],
                features=dna_data['features'],
                image_info=dna_data['image_info']
            )

            # Store in registry
            self.assets[asset_id] = {
                'fingerprint': fingerprint,
                'dna_data': dna_data,
                'registration_time': time.time()
            }
            self.merkle_leaves.append(asset_id)
            self._save_registry()

            logger.info(f"✅ Asset registered successfully: {asset_id}")
            return fingerprint

        except Exception as e:
            logger.error(f"Failed to register asset {asset_path}: {e}")
            raise

    def _load_registry(self):
        """Load asset registry from disk"""
        registry_file = self.registry_dir / "assets.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.assets = data.get('assets', {})
                    self.merkle_leaves = data.get('merkle_leaves', [])
                logger.info(f"Loaded {len(self.assets)} assets from registry")
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")
                self.assets = {}
                self.merkle_leaves = []

    def _save_registry(self):
        """Save asset registry to disk"""
        registry_file = self.registry_dir / "assets.json"
        try:
            data = {
                'assets': self.assets,
                'merkle_leaves': self.merkle_leaves,
                'last_updated': time.time()
            }
            with open(registry_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def get_merkle_proof(self, asset_id: str):
        """Generate Merkle proof for an asset"""
        if asset_id not in self.assets:
            return []
        # Simple implementation - return the asset's position
        index = self.merkle_leaves.index(asset_id) if asset_id in self.merkle_leaves else -1
        return [f"proof_element_{i}" for i in range(min(4, len(self.merkle_leaves)))]  # Mock proof

    def get_merkle_root(self):
        """Generate Merkle root from all registered assets"""
        if not self.merkle_leaves:
            return "empty_tree_root"
        # Simple hash of all asset IDs
        combined = "".join(self.merkle_leaves)
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_merkle_tree_info(self):
        """Get information about the current Merkle tree"""
        leaves = []
        for asset_id in self.merkle_leaves:
            if asset_id in self.assets:
                asset_data = self.assets[asset_id]
                leaves.append({
                    'asset_id': asset_id,
                    'creator': asset_data['fingerprint'].creator,
                    'dna_signature': asset_data['fingerprint'].dna_hash,
                    'timestamp': asset_data['fingerprint'].timestamp
                })

        return {
            "leaves": leaves,
            "root_hash": self.get_merkle_root(),
            "tree_depth": max(1, len(self.merkle_leaves).bit_length()),
            "leaf_count": len(self.merkle_leaves)
        }

    def verify_merkle_proof(self, asset_id: str, proof: List[str], expected_root: str) -> bool:
        """Verify a Merkle proof (mock implementation)"""
        if asset_id not in self.assets:
            return False
        # Simple mock verification - just check if asset exists and root matches
        current_root = self.get_merkle_root()
        return current_root == expected_root
