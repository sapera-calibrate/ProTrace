#!/usr/bin/env python3
"""
Simple Virtual IPFS Manager for testing
"""

import hashlib
import os

class MockNode:
    def __init__(self, node_id, ipfs_cid, perceptual_hash, dna_hash, file_size):
        self.node_id = node_id
        self.ipfs_cid = ipfs_cid
        self.perceptual_hash = perceptual_hash
        self.dna_hash = dna_hash
        self.file_size = file_size
        self.parent_hash = None

class VirtualIPFSManager:
    def __init__(self, enable_caching=True):
        self.enable_caching = enable_caching
        self.merkle_root = "0x" + "00" * 32
        self.nodes = []
        self.image_count = 0

    def add_image(self, image_path):
        # Simple placeholder - just return success with mock node
        filename = os.path.basename(image_path)
        
        # Create mock hashes
        node_id = hashlib.sha256(filename.encode()).hexdigest()
        ipfs_cid = f"Qm{hashlib.sha256(image_path.encode()).hexdigest()[:44]}"
        perceptual_hash = hashlib.md5(filename.encode()).hexdigest()
        dna_hash = hashlib.sha256(filename.encode()).hexdigest()  # Mock DNA hash
        
        # Get file size
        try:
            file_size = os.path.getsize(image_path)
        except:
            file_size = 0
        
        node = MockNode(node_id, ipfs_cid, perceptual_hash, dna_hash, file_size)
        self.nodes.append(node)
        self.image_count += 1
        
        return True, node, "Image added successfully"

    def list_nodes(self):
        return self.nodes

    def get_statistics(self):
        return {
            'total_images': self.image_count,
            'original_images': self.image_count,
            'duplicate_variants': 0,
            'total_size_mb': 0.0,
            'total_size_bytes': 0,
            'merkle_root': self.merkle_root,
            'ipfs_directory': 'V_ipfs',
            'merkle_directory': 'merkle_nodes',
            'performance': {
                'cache_hits': 0,
                'cache_misses': self.image_count,
                'cache_hit_rate': 0.0
            }
        }

    def verify_image(self, image_path):
        return True, "Image verified successfully"
