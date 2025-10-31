"""
ProTrace Cross-Chain Edition Management System
==============================================

Extended Core Protocol with support for:
- Edition Modes: 1/1 Strict, Serial Numbered, Fungible/Open
- Universal Keys: dna_hash#chain#contract#token_id#edition_no
- Cross-Chain Minting: ETH, Solana, Tezos, Bitcoin
- Rule Enforcement: Prevents unauthorized editions
- Lazy Minting: Relayer-based activation
"""

import logging
import asyncio
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import json
import time
import hashlib
from enum import Enum
from dataclasses import dataclass, asdict
from .image_dna import compute_dna
from .merkle import MerkleTree

logger = logging.getLogger(__name__)


class EditionMode(Enum):
    """Edition modes for digital assets"""
    STRICT_1_1 = "1/1_strict"      # Single unique NFT
    SERIAL = "serial"              # Limited editions with sequential numbering
    FUNGIBLE = "fungible"          # Multiple instances (ERC-1155 style)


@dataclass
class UniversalKey:
    """Universal edition key format: dna_hash#chain#contract#token_id#edition_no"""
    dna_hash: str
    chain: str
    contract: str
    token_id: str
    edition_no: int

    def to_string(self) -> str:
        """Convert to universal key string format"""
        return f"{self.dna_hash}#{self.chain}#{self.contract}#{self.token_id}#{self.edition_no}"

    @classmethod
    def from_string(cls, key_str: str) -> 'UniversalKey':
        """Parse universal key from string format"""
        parts = key_str.split('#')
        if len(parts) != 5:
            raise ValueError(f"Invalid universal key format: {key_str}")
        return cls(
            dna_hash=parts[0],
            chain=parts[1],
            contract=parts[2],
            token_id=parts[3],
            edition_no=int(parts[4])
        )


@dataclass
class EditionMetadata:
    """Metadata for a specific edition"""
    dna_hash: str
    chain: str
    contract: str
    token_id: str
    edition_no: int
    edition_mode: EditionMode
    max_editions: Optional[int]
    creator: str
    original_asset_path: str
    dna_signature: str
    perceptual_hash: str
    asset_hash: str
    image_info: Dict
    registration_time: float
    last_updated: float
    status: str = "active"
    ipfs_cid: Optional[str] = None
    merkle_proof: Optional[List[str]] = None
    metadata: Optional[Dict] = None

    def to_universal_key(self) -> UniversalKey:
        """Convert to universal key"""
        return UniversalKey(
            dna_hash=self.dna_hash,
            chain=self.chain,
            contract=self.contract,
            token_id=self.token_id,
            edition_no=self.edition_no
        )


@dataclass
class CoreAsset:
    """Core asset information (original DNA)"""
    dna_hash: str
    original_creator: str
    first_registration: float
    total_editions: int = 0
    edition_modes: List[str] = None
    chains: List[str] = None
    contracts: List[str] = None
    ipfs_cid: Optional[str] = None
    merkle_root: Optional[str] = None

    def __post_init__(self):
        if self.edition_modes is None:
            self.edition_modes = []
        if self.chains is None:
            self.chains = []
        if self.contracts is None:
            self.contracts = []


class EditionRegistry:
    """Enhanced registry supporting cross-chain editions"""

    def __init__(self, registry_path: str = "V_on_chain/edition_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(exist_ok=True)

        # Registry data structures
        self.edition_registry: Dict[str, EditionMetadata] = {}  # universal_key -> metadata
        self.core_assets: Dict[str, CoreAsset] = {}  # dna_hash -> core asset info
        self.chain_registries: Dict[str, Dict] = {}  # chain -> contract data
        self.batch_updates: List[Dict] = []  # batch update history

        # Statistics
        self.total_editions = 0
        self.total_core_assets = 0
        self.last_updated = time.time()

        self._load_registry()

    def _load_registry(self):
        """Load registry from disk"""
        if not self.registry_path.exists():
            logger.info("No existing edition registry found, starting fresh")
            return

        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)

            # Load edition registry
            for key_str, metadata_dict in data.get('edition_registry', {}).items():
                # Convert edition_mode string back to enum
                metadata_dict['edition_mode'] = EditionMode(metadata_dict['edition_mode'])
                metadata = EditionMetadata(**metadata_dict)
                self.edition_registry[key_str] = metadata

            # Load core assets
            for dna_hash, asset_dict in data.get('core_assets', {}).items():
                asset = CoreAsset(**asset_dict)
                self.core_assets[dna_hash] = asset

            # Load chain registries and batch updates
            self.chain_registries = data.get('chain_registries', {})
            self.batch_updates = data.get('batch_updates', [])

            # Load statistics
            self.total_editions = data.get('total_editions', 0)
            self.total_core_assets = data.get('total_core_assets', 0)
            self.last_updated = data.get('last_updated', time.time())

            logger.info(f"Loaded edition registry: {self.total_editions} editions, {self.total_core_assets} core assets")

        except Exception as e:
            logger.error(f"Failed to load edition registry: {e}")
            # Initialize empty registry
            self.edition_registry = {}
            self.core_assets = {}
            self.chain_registries = {}
            self.batch_updates = []

    def _save_registry(self):
        """Save registry to disk"""
        try:
            data = {
                'version': '2.0',
                'edition_registry': {
                    key: asdict(metadata) for key, metadata in self.edition_registry.items()
                },
                'core_assets': {
                    dna_hash: asdict(asset) for dna_hash, asset in self.core_assets.items()
                },
                'chain_registries': self.chain_registries,
                'batch_updates': self.batch_updates,
                'total_editions': self.total_editions,
                'total_core_assets': self.total_core_assets,
                'last_updated': time.time()
            }

            with open(self.registry_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            self.last_updated = time.time()
            logger.info("Edition registry saved successfully")

        except Exception as e:
            logger.error(f"Failed to save edition registry: {e}")
            raise

    def register_edition(self, asset_path: str, creator: str, chain: str, contract: str,
                        token_id: str, edition_no: int, edition_mode: EditionMode,
                        max_editions: Optional[int] = None) -> Tuple[bool, str, Optional[EditionMetadata]]:
        """
        Register a new edition with rule enforcement

        Returns: (success, message, edition_metadata)
        """
        try:
            # Compute DNA hash
            dna_result = compute_dna(asset_path)
            dna_hash = dna_result['dna_hex']

            # Create universal key
            universal_key = UniversalKey(dna_hash, chain, contract, token_id, edition_no)
            key_str = universal_key.to_string()

            # Check if edition already exists
            if key_str in self.edition_registry:
                return False, f"Edition already exists: {key_str}", None

            # Validate edition rules
            validation_result = self._validate_edition_rules(dna_hash, chain, contract,
                                                          token_id, edition_no, edition_mode)
            if not validation_result[0]:
                return False, validation_result[1], None

            # Create edition metadata
            edition_metadata = EditionMetadata(
                dna_hash=dna_hash,
                chain=chain,
                contract=contract,
                token_id=token_id,
                edition_no=edition_no,
                edition_mode=edition_mode,
                max_editions=max_editions,
                creator=creator,
                original_asset_path=asset_path,
                dna_signature=dna_result['dna_hex'],
                perceptual_hash=dna_result.get('perceptual_hash', ''),
                asset_hash=hashlib.sha256(open(asset_path, 'rb').read()).hexdigest(),
                image_info=dna_result.get('image_info', {}),
                registration_time=time.time(),
                last_updated=time.time(),
                status="active",
                metadata={"name": f"Edition {edition_no}", "description": f"Edition {edition_no} of token {token_id}"}
            )

            # Store in registry
            self.edition_registry[key_str] = edition_metadata

            # Update or create core asset
            if dna_hash not in self.core_assets:
                self.core_assets[dna_hash] = CoreAsset(
                    dna_hash=dna_hash,
                    original_creator=creator,
                    first_registration=time.time()
                )
                self.total_core_assets += 1

            core_asset = self.core_assets[dna_hash]
            core_asset.total_editions += 1

            # Update chain registry
            self._update_chain_registry(chain, contract, edition_mode, dna_hash, max_editions)

            self.total_editions += 1
            self._save_registry()

            logger.info(f"✅ Edition registered: {key_str}")
            return True, f"Edition registered successfully: {key_str}", edition_metadata

        except Exception as e:
            logger.error(f"Failed to register edition: {e}")
            return False, f"Registration failed: {e}", None

    def _validate_edition_rules(self, dna_hash: str, chain: str, contract: str,
                              token_id: str, edition_no: int, edition_mode: EditionMode) -> Tuple[bool, str]:
        """Validate edition registration rules"""

        # Check edition mode rules
        if edition_mode == EditionMode.STRICT_1_1:
            if edition_no != 0:
                return False, "1/1 strict mode only allows edition_no = 0"

            # Check if any other editions exist for this DNA
            for key_str in self.edition_registry.keys():
                key = UniversalKey.from_string(key_str)
                if key.dna_hash == dna_hash:
                    return False, f"1/1 strict mode violation: DNA {dna_hash} already has editions"

        elif edition_mode == EditionMode.SERIAL:
            if edition_no < 1:
                return False, "Serial mode requires edition_no >= 1"

            # Check for duplicate edition numbers for same contract/token
            for key_str, metadata in self.edition_registry.items():
                if (metadata.contract == contract and
                    metadata.token_id == token_id and
                    metadata.edition_no == edition_no):
                    return False, f"Edition {edition_no} already exists for contract {contract} token {token_id}"

        elif edition_mode == EditionMode.FUNGIBLE:
            if edition_no != 0:
                return False, "Fungible mode only allows edition_no = 0"

        return True, "Validation passed"

    def _update_chain_registry(self, chain: str, contract: str, edition_mode: EditionMode,
                             dna_hash: str, max_editions: Optional[int]):
        """Update chain-specific registry data"""
        if chain not in self.chain_registries:
            self.chain_registries[chain] = {'contracts': {}}

        if contract not in self.chain_registries[chain]['contracts']:
            self.chain_registries[chain]['contracts'][contract] = {
                'total_minted': 0,
                'max_supply': max_editions or 0,
                'edition_mode': edition_mode.value,
                'dna_hash': dna_hash
            }

        # Update mint count
        self.chain_registries[chain]['contracts'][contract]['total_minted'] += 1

    def get_editions_for_asset(self, dna_hash: str) -> List[EditionMetadata]:
        """Get all editions for a core asset"""
        editions = []
        for key_str, metadata in self.edition_registry.items():
            if metadata.dna_hash == dna_hash:
                editions.append(metadata)
        return sorted(editions, key=lambda x: x.edition_no)

    def get_editions_for_contract(self, chain: str, contract: str) -> List[EditionMetadata]:
        """Get all editions for a contract"""
        editions = []
        for metadata in self.edition_registry.values():
            if metadata.chain == chain and metadata.contract == contract:
                editions.append(metadata)
        return sorted(editions, key=lambda x: x.edition_no)

    def check_edition_exists(self, universal_key: Union[str, UniversalKey]) -> bool:
        """Check if an edition exists"""
        if isinstance(universal_key, UniversalKey):
            key_str = universal_key.to_string()
        else:
            key_str = universal_key
        return key_str in self.edition_registry

    def batch_register_editions(self, editions: List[Dict]) -> Tuple[bool, str, List[str]]:
        """
        Batch register multiple editions

        Returns: (success, message, successful_keys)
        """
        successful_keys = []
        failed_editions = []

        for edition_data in editions:
            success, message, metadata = self.register_edition(**edition_data)
            if success and metadata:
                successful_keys.append(metadata.to_universal_key().to_string())
            else:
                failed_editions.append((edition_data, message))

        if failed_editions:
            return False, f"Batch registration partial failure: {len(failed_editions)} failed", successful_keys

        # Record batch update
        batch_update = {
            'batch_id': f"batch_{int(time.time())}",
            'timestamp': time.time(),
            'editions_added': len(successful_keys),
            'merkle_root': self._compute_merkle_root(),
            'ipfs_cid': None  # Would be set by IPFS manager
        }
        self.batch_updates.append(batch_update)

        self._save_registry()
        return True, f"Successfully registered {len(successful_keys)} editions", successful_keys

    def _compute_merkle_root(self) -> str:
        """Compute Merkle root for current registry state"""
        if not self.edition_registry:
            return "empty_tree"

        # Simple hash of all edition keys
        sorted_keys = sorted(self.edition_registry.keys())
        combined = "".join(sorted_keys)
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_registry_stats(self) -> Dict:
        """Get comprehensive registry statistics"""
        return {
            'total_editions': self.total_editions,
            'total_core_assets': self.total_core_assets,
            'chains': list(self.chain_registries.keys()),
            'edition_modes': list(set(
                metadata.edition_mode.value for metadata in self.edition_registry.values()
            )),
            'last_updated': self.last_updated,
            'registry_version': '2.0'
        }


class EditionCoreProtocol:
    """Cross-Chain Edition Management Protocol"""

    def __init__(self, registry_path: str = "V_on_chain/edition_registry.json"):
        self.registry = EditionRegistry(registry_path)
        self.merkle_tree = MerkleTree()
        self.logger = logging.getLogger(__name__)

    async def register_asset_edition(self, asset_path: str, creator: str, chain: str,
                                   contract: str, token_id: str, edition_no: int,
                                   edition_mode: EditionMode, max_editions: Optional[int] = None) -> Tuple[bool, str]:
        """
        Register a new asset edition with cross-chain support
        """
        return self.registry.register_edition(
            asset_path, creator, chain, contract, token_id, edition_no, edition_mode, max_editions
        )[:2]  # Return success and message only

    async def batch_register_editions(self, editions: List[Dict]) -> Tuple[bool, str]:
        """
        Batch register multiple editions
        """
        success, message, _ = self.registry.batch_register_editions(editions)
        return success, message

    def get_editions_for_asset(self, dna_hash: str) -> List[EditionMetadata]:
        """Get all editions for a DNA hash"""
        return self.registry.get_editions_for_asset(dna_hash)

    def get_editions_for_contract(self, chain: str, contract: str) -> List[EditionMetadata]:
        """Get all editions for a contract"""
        return self.registry.get_editions_for_contract(chain, contract)

    def check_edition_authorization(self, dna_hash: str, chain: str, contract: str,
                                  token_id: str, edition_no: int) -> Tuple[bool, str]:
        """
        Check if an edition is authorized to be minted
        """
        universal_key = UniversalKey(dna_hash, chain, contract, token_id, edition_no)
        key_str = universal_key.to_string()

        if not self.registry.check_edition_exists(key_str):
            return False, f"Edition not found: {key_str}"

        metadata = self.registry.edition_registry[key_str]

        # Additional validation logic can be added here
        # e.g., check creator permissions, contract authorization, etc.

        return True, "Edition authorized"

    def get_merkle_proof(self, universal_key: str) -> Optional[List[str]]:
        """Generate Merkle proof for an edition"""
        if universal_key not in self.registry.edition_registry:
            return None

        # Simple mock proof - in production, use actual Merkle tree
        return [f"proof_element_{i}" for i in range(4)]

    def verify_edition_proof(self, universal_key: str, proof: List[str], expected_root: str) -> bool:
        """Verify Merkle proof for an edition"""
        if universal_key not in self.registry.edition_registry:
            return False

        # Simple mock verification
        current_root = self.registry._compute_merkle_root()
        return current_root == expected_root

    def get_registry_stats(self) -> Dict:
        """Get registry statistics"""
        return self.registry.get_registry_stats()
