"""
ProTrace Protocol Package
========================

Cross-Platform NFT Duplicate Prevention Service
Zero-Knowledge Digital Asset Verification & NFT Attestation
"""

__version__ = "2.0.0"
__author__ = "Sapera Calibrate"

# Core DNA Engine (256-bit: dHash + Grid)
from .image_dna import (
    compute_dna,
    hamming_distance,
    dna_similarity,
    is_duplicate,
    extract_dna_features,
    dna_similarity_unified,
    dna_feasibility_matrix,
    compute_dna_batch,
    find_duplicates_in_batch
)

# Merkle Tree
from .merkle import (
    MerkleTree,
    compute_leaf_hash,
    verify_proof_standalone
)

# Vector Database
from .vector_db import (
    VectorDBClient,
    InMemoryVectorDB,
    create_vector_db
)

# EIP-712 Signing
from .eip712 import (
    build_registration_message,
    verify_signature_offline,
    sign_message,
    format_for_contract,
    update_domain,
    nonce_manager
)

# Relayer Service
from .relayer_service import (
    LazyMintingRelayer,
    RelayerConfig,
    ChainEvent,
    create_ethereum_monitor,
    create_solana_monitor,
    create_tezos_monitor
)

__all__ = [
    # DNA Engine (256-bit)
    'compute_dna',
    'hamming_distance',
    'dna_similarity',
    'is_duplicate',
    'extract_dna_features',
    'dna_similarity_unified',
    'dna_feasibility_matrix',
    'compute_dna_batch',
    'find_duplicates_in_batch',
    
    # Merkle Tree
    'MerkleTree',
    'compute_leaf_hash',
    'verify_proof_standalone',
    
    # Vector Database
    'VectorDBClient',
    'InMemoryVectorDB',
    'create_vector_db',
    
    # EIP-712
    'build_registration_message',
    'verify_signature_offline',
    'sign_message',
    'format_for_contract',
    'update_domain',
    'nonce_manager',
    
    # Edition Management System
    'EditionRegistry',
    'EditionCoreProtocol',
    'EditionMode',
    'UniversalKey',
    'EditionMetadata',
    'CoreAsset',
    
    # Relayer Service
    'LazyMintingRelayer',
    'RelayerConfig',
    'ChainEvent',
    'create_ethereum_monitor',
    'create_solana_monitor',
    'create_tezos_monitor',
    
    # Cross-Chain Minting
    'CrossChainMintingCoordinator',
    'Chain',
    'MintingResult',
    'LazyMintRequest',
    'create_ethereum_miner',
    'create_solana_miner',
    'create_tezos_miner',
    
    # IPFS Manager (Extended)
    'IPFSManager',
    'EditionIPFSManager',
    
    # Legacy
    'CoreProtocol',
    'setup_logging',
    
    # Version
    '__version__',
    '__author__'
]
