"""
ProTrace Merkle Tree Manager
============================

BLAKE3-based Merkle tree for tamper-proof DNA registration commitments.
Optimized for batch verification with O(log n) proof generation.
"""

import hashlib
from typing import List, Dict, Tuple, Optional
import json


def blake3_hash(data: bytes) -> bytes:
    """
    Compute BLAKE3 hash of data.
    Falls back to SHA256 if blake3 not available.
    
    Args:
        data: Bytes to hash
    
    Returns:
        32-byte hash
    """
    try:
        import blake3
        return blake3.blake3(data).digest()
    except ImportError:
        # Fallback to SHA256
        return hashlib.sha256(data).digest()


class MerkleNode:
    """Merkle tree node"""
    
    def __init__(self, left=None, right=None, data=None, is_leaf=False):
        self.left = left
        self.right = right
        self.is_leaf = is_leaf
        
        if data is not None:
            # Leaf node
            self.hash = blake3_hash(data)
            self.data = data
        else:
            # Internal node
            left_hash = left.hash if left else b'\x00' * 32
            right_hash = right.hash if right else b'\x00' * 32
            self.hash = blake3_hash(left_hash + right_hash)
            self.data = None


class MerkleTree:
    """
    Balanced binary Merkle tree with BLAKE3 hashing.
    
    Features:
    - Append-only for new registrations
    - Efficient proof generation (O(log n))
    - Proof verification (O(log n))
    - Supports up to 1M leaves before rotation
    """
    
    def __init__(self):
        self.leaves = []
        self.root = None
        self.leaf_map = {}  # Maps leaf data -> index
        
    def add_leaf(self, dna_hex: str, pointer: str, platform_id: str, timestamp: int = None):
        """
        Add registration leaf to tree.
        
        Leaf = BLAKE3(DNA_hex || pointer || platform_id || timestamp)
        
        Args:
            dna_hex: 128-bit DNA hash (32 hex chars)
            pointer: Unique identifier (UUID or IPFS CID)
            platform_id: Platform identifier
            timestamp: Unix timestamp (optional)
        """
        if timestamp is None:
            import time
            timestamp = int(time.time())
        
        # Construct leaf data
        leaf_data = f"{dna_hex}|{pointer}|{platform_id}|{timestamp}".encode('utf-8')
        
        # Store leaf
        self.leaves.append(leaf_data)
        self.leaf_map[leaf_data] = len(self.leaves) - 1
        
    def build_tree(self):
        """
        Construct balanced binary Merkle tree from leaves.
        
        Returns:
            Root hash as hex string
        """
        if not self.leaves:
            self.root = None
            return None
        
        # Create leaf nodes
        nodes = [MerkleNode(data=leaf, is_leaf=True) for leaf in self.leaves]
        
        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]  # Duplicate last if odd
                
                parent = MerkleNode(left=left, right=right)
                next_level.append(parent)
            
            nodes = next_level
        
        self.root = nodes[0]
        return self.root.hash.hex()
    
    def get_root(self) -> Optional[str]:
        """
        Get Merkle root hash.
        
        Returns:
            Root hash as hex string (64 chars for BLAKE3/SHA256)
        """
        if self.root is None:
            return None
        return self.root.hash.hex()
    
    def get_proof(self, leaf_index: int) -> List[Dict[str, str]]:
        """
        Generate Merkle proof for leaf at given index.
        
        Args:
            leaf_index: Index of leaf in leaves list
        
        Returns:
            List of proof elements: [{'hash': hex_string, 'position': 'left'|'right'}]
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError(f"Leaf index {leaf_index} out of range")
        
        if self.root is None:
            raise ValueError("Tree not built. Call build_tree() first")
        
        proof = []
        
        # Rebuild tree structure to track path
        nodes = [MerkleNode(data=leaf, is_leaf=True) for leaf in self.leaves]
        current_index = leaf_index
        
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
                
                # Check if current node is in this pair
                if i == current_index or i + 1 == current_index:
                    # Add sibling to proof
                    if i == current_index:
                        # Left node, add right sibling
                        proof.append({
                            'hash': right.hash.hex(),
                            'position': 'right'
                        })
                    else:
                        # Right node, add left sibling
                        proof.append({
                            'hash': left.hash.hex(),
                            'position': 'left'
                        })
                    
                    # Update index for next level
                    current_index = i // 2
                
                parent = MerkleNode(left=left, right=right)
                next_level.append(parent)
            
            nodes = next_level
        
        return proof
    
    def verify_proof(self, leaf_data: bytes, proof: List[Dict[str, str]], root_hash: str) -> bool:
        """
        Verify Merkle proof for a leaf.
        
        Args:
            leaf_data: Original leaf data
            proof: Proof path from get_proof()
            root_hash: Expected root hash (hex string)
        
        Returns:
            True if proof is valid
        """
        # Compute leaf hash
        current_hash = blake3_hash(leaf_data)
        
        # Traverse proof path
        for proof_element in proof:
            sibling_hash = bytes.fromhex(proof_element['hash'])
            position = proof_element['position']
            
            if position == 'left':
                current_hash = blake3_hash(sibling_hash + current_hash)
            else:
                current_hash = blake3_hash(current_hash + sibling_hash)
        
        # Compare with expected root
        return current_hash.hex() == root_hash
    
    def export_manifest(self) -> Dict:
        """
        Export tree manifest for IPFS storage.
        
        Returns:
            Dictionary with root, leaves, and proofs
        """
        if self.root is None:
            raise ValueError("Tree not built")
        
        manifest = {
            'root': self.get_root(),
            'total_leaves': len(self.leaves),
            'leaves': [],
            'proofs': {}
        }
        
        # Export leaves
        for i, leaf_data in enumerate(self.leaves):
            parts = leaf_data.decode('utf-8').split('|')
            manifest['leaves'].append({
                'index': i,
                'dna_hex': parts[0],
                'pointer': parts[1],
                'platform_id': parts[2],
                'timestamp': int(parts[3])
            })
            
            # Generate proof for each leaf
            proof = self.get_proof(i)
            manifest['proofs'][str(i)] = proof
        
        return manifest
    
    def import_manifest(self, manifest: Dict):
        """
        Import tree from manifest.
        
        Args:
            manifest: Manifest dictionary from export_manifest()
        """
        self.leaves = []
        self.leaf_map = {}
        
        # Import leaves
        for leaf in manifest['leaves']:
            self.add_leaf(
                leaf['dna_hex'],
                leaf['pointer'],
                leaf['platform_id'],
                leaf['timestamp']
            )
        
        # Rebuild tree
        self.build_tree()
        
        # Verify root matches
        if self.get_root() != manifest['root']:
            raise ValueError("Imported manifest root mismatch")


def compute_leaf_hash(dna_hex: str, pointer: str, platform_id: str, timestamp: int = None) -> str:
    """
    Compute leaf hash for DNA registration.
    
    Args:
        dna_hex: 128-bit DNA hash
        pointer: Unique identifier
        platform_id: Platform identifier
        timestamp: Unix timestamp
    
    Returns:
        Leaf hash as hex string
    """
    if timestamp is None:
        import time
        timestamp = int(time.time())
    
    leaf_data = f"{dna_hex}|{pointer}|{platform_id}|{timestamp}".encode('utf-8')
    return blake3_hash(leaf_data).hex()


def verify_proof_standalone(dna_hex: str, pointer: str, platform_id: str, 
                            timestamp: int, proof: List[Dict[str, str]], 
                            root_hash: str) -> bool:
    """
    Standalone proof verification without tree instance.
    
    Args:
        dna_hex: DNA hash
        pointer: Pointer
        platform_id: Platform ID
        timestamp: Timestamp
        proof: Merkle proof
        root_hash: Expected root hash
    
    Returns:
        True if valid
    """
    leaf_data = f"{dna_hex}|{pointer}|{platform_id}|{timestamp}".encode('utf-8')
    current_hash = blake3_hash(leaf_data)
    
    for proof_element in proof:
        sibling_hash = bytes.fromhex(proof_element['hash'])
        position = proof_element['position']
        
        if position == 'left':
            current_hash = blake3_hash(sibling_hash + current_hash)
        else:
            current_hash = blake3_hash(current_hash + sibling_hash)
    
    return current_hash.hex() == root_hash


# Example usage
if __name__ == "__main__":
    # Create tree
    tree = MerkleTree()
    
    # Add registrations
    tree.add_leaf("abc123def456" + "0" * 20, "uuid:550e8400-opensea-ethereum", "opensea", 1698765432)
    tree.add_leaf("def789abc123" + "0" * 20, "uuid:660e9500-foundation-ethereum", "foundation", 1698765433)
    tree.add_leaf("123456789abc" + "0" * 20, "uuid:770ea600-magiceden-solana", "magiceden", 1698765434)
    
    # Build tree
    root = tree.build_tree()
    print(f"Merkle root: {root}")
    
    # Generate proof for first leaf
    proof = tree.get_proof(0)
    print(f"Proof for leaf 0: {json.dumps(proof, indent=2)}")
    
    # Verify proof
    leaf_data = tree.leaves[0]
    is_valid = tree.verify_proof(leaf_data, proof, root)
    print(f"Proof valid: {is_valid}")
    
    # Export manifest
    manifest = tree.export_manifest()
    print(f"Manifest exported with {manifest['total_leaves']} leaves")
