"""
Cross-Chain Minting Integration
===============================

Handles minting operations across multiple blockchains:
- Ethereum (ERC-721, ERC-1155)
- Solana (SPL tokens, Metaplex editions)
- Tezos (FA2 multi-edition tokens)
- Bitcoin (Ordinals, Runes) - experimental

Supports lazy minting through relayer activation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import json
import hashlib

from .edition_core import EditionMode, UniversalKey, EditionMetadata
from .eip712 import sign_message, format_for_contract

logger = logging.getLogger(__name__)


class Chain(Enum):
    """Supported blockchains"""
    ETHEREUM = "eth"
    SOLANA = "sol"
    TEZOS = "tez"
    BITCOIN = "btc"


@dataclass
class MintingResult:
    """Result of a minting operation"""
    success: bool
    transaction_hash: Optional[str] = None
    token_id: Optional[str] = None
    contract_address: Optional[str] = None
    edition_no: Optional[int] = None
    error_message: Optional[str] = None
    gas_used: Optional[int] = None
    block_number: Optional[int] = None


@dataclass
class LazyMintRequest:
    """Lazy minting request for relayer processing"""
    universal_key: str
    dna_hash: str
    chain: str
    contract: str
    token_id: str
    edition_no: int
    edition_mode: EditionMode
    creator: str
    metadata: Dict[str, Any]
    signed_payload: Optional[str] = None
    expires_at: Optional[int] = None
    status: str = "pending"


class ChainMinter(ABC):
    """Abstract base class for chain-specific minting"""

    def __init__(self, chain: Chain, config: Dict[str, Any]):
        self.chain = chain
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{chain.value}")

    @abstractmethod
    async def mint_edition(self, edition: EditionMetadata, metadata: Dict[str, Any]) -> MintingResult:
        """Mint a specific edition on this chain"""
        pass

    @abstractmethod
    async def check_authorization(self, universal_key: str) -> bool:
        """Check if edition is authorized for minting"""
        pass

    @abstractmethod
    async def get_minting_fee(self, edition_mode: EditionMode) -> int:
        """Get estimated minting fee in native currency (wei, lamports, etc.)"""
        pass

    def validate_edition_mode(self, edition: EditionMetadata) -> bool:
        """Validate edition mode constraints for this chain"""
        if self.chain == Chain.ETHEREUM:
            return edition.edition_mode in [EditionMode.STRICT_1_1, EditionMode.SERIAL, EditionMode.FUNGIBLE]
        elif self.chain == Chain.SOLANA:
            return edition.edition_mode in [EditionMode.STRICT_1_1, EditionMode.SERIAL, EditionMode.FUNGIBLE]
        elif self.chain == Chain.TEZOS:
            return edition.edition_mode in [EditionMode.STRICT_1_1, EditionMode.SERIAL, EditionMode.FUNGIBLE]
        elif self.chain == Chain.BITCOIN:
            return edition.edition_mode in [EditionMode.STRICT_1_1]  # Limited support
        return False


class EthereumMinter(ChainMinter):
    """Ethereum ERC-721/ERC-1155 minting"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(Chain.ETHEREUM, config)
        self.web3_provider = config.get('web3_provider')
        self.private_key = config.get('private_key')
        self.contract_addresses = config.get('contract_addresses', {})

    async def mint_edition(self, edition: EditionMetadata, metadata: Dict[str, Any]) -> MintingResult:
        """Mint ERC-721 or ERC-1155 token"""
        try:
            # This would integrate with web3.py
            # For now, return mock result

            contract_type = "ERC-721" if edition.edition_mode == EditionMode.STRICT_1_1 else "ERC-1155"

            # Generate EIP-712 signature for authorization
            domain = {
                "name": "ProTrace",
                "version": "1.0",
                "chainId": 1,  # Mainnet
                "verifyingContract": edition.contract
            }

            message = {
                "dna_hash": edition.dna_hash,
                "token_id": edition.token_id,
                "edition_no": edition.edition_no,
                "chain": edition.chain,
                "contract": edition.contract
            }

            signature = sign_message(domain, "EditionMint", message, self.private_key)

            result = MintingResult(
                success=True,
                transaction_hash=f"0x{hashlib.sha256(f'{edition.dna_hash}{edition.token_id}{edition.edition_no}'.encode()).hexdigest()}",
                token_id=edition.token_id,
                contract_address=edition.contract,
                edition_no=edition.edition_no,
                gas_used=150000,  # Estimated gas
                block_number=18500000  # Mock block
            )

            self.logger.info(f"✅ Minted {contract_type} token: {result.transaction_hash}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to mint Ethereum edition: {e}")
            return MintingResult(success=False, error_message=str(e))

    async def check_authorization(self, universal_key: str) -> bool:
        """Check edition authorization via on-chain verification"""
        # In production, this would query the ProTrace oracle contract
        return True  # Mock authorization

    async def get_minting_fee(self, edition_mode: EditionMode) -> int:
        """Get minting fee in wei"""
        base_fee = 50000000000000000  # 0.05 ETH in wei
        if edition_mode == EditionMode.FUNGIBLE:
            return base_fee // 2  # Cheaper for fungible tokens
        return base_fee


class SolanaMinter(ChainMinter):
    """Solana SPL token minting with Metaplex"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(Chain.SOLANA, config)
        self.rpc_url = config.get('rpc_url', 'https://api.mainnet-beta.solana.com')
        self.private_key = config.get('private_key')
        self.program_ids = config.get('program_ids', {})

    async def mint_edition(self, edition: EditionMetadata, metadata: Dict[str, Any]) -> MintingResult:
        """Mint Solana SPL token with Metaplex metadata"""
        try:
            # This would integrate with solana-py and metaplex
            # For now, return mock result

            mint_address = f"{edition.contract}_{edition.token_id}_{edition.edition_no}"

            result = MintingResult(
                success=True,
                transaction_hash=hashlib.sha256(f"sol_{edition.dna_hash}_{edition.token_id}_{edition.edition_no}".encode()).hexdigest(),
                token_id=mint_address,
                contract_address=edition.contract,
                edition_no=edition.edition_no,
                gas_used=5000,  # Solana compute units
            )

            self.logger.info(f"✅ Minted Solana SPL token: {result.transaction_hash}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to mint Solana edition: {e}")
            return MintingResult(success=False, error_message=str(e))

    async def check_authorization(self, universal_key: str) -> bool:
        """Check via Solana ProTrace program"""
        # In production, this would call the Anchor program's verify_edition_authorization
        return True  # Mock authorization

    async def get_minting_fee(self, edition_mode: EditionMode) -> int:
        """Get minting fee in lamports"""
        base_fee = 5000000  # ~0.005 SOL in lamports
        if edition_mode == EditionMode.FUNGIBLE:
            return base_fee // 2
        return base_fee


class TezosMinter(ChainMinter):
    """Tezos FA2 multi-edition minting"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(Chain.TEZOS, config)
        self.rpc_url = config.get('rpc_url', 'https://mainnet.api.tez.ie')
        self.private_key = config.get('private_key')
        self.contract_addresses = config.get('contract_addresses', {})

    async def mint_edition(self, edition: EditionMetadata, metadata: Dict[str, Any]) -> MintingResult:
        """Mint Tezos FA2 token"""
        try:
            # This would integrate with pytezos
            # For now, return mock result

            operation_hash = f"o{hashlib.sha256(f'tez_{edition.dna_hash}_{edition.token_id}_{edition.edition_no}'.encode()).hexdigest()[:50]}"

            result = MintingResult(
                success=True,
                transaction_hash=operation_hash,
                token_id=edition.token_id,
                contract_address=edition.contract,
                edition_no=edition.edition_no,
                gas_used=1420,  # Tezos gas
            )

            self.logger.info(f"✅ Minted Tezos FA2 token: {result.transaction_hash}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to mint Tezos edition: {e}")
            return MintingResult(success=False, error_message=str(e))

    async def check_authorization(self, universal_key: str) -> bool:
        """Check via Tezos contract view"""
        return True  # Mock authorization

    async def get_minting_fee(self, edition_mode: EditionMode) -> int:
        """Get minting fee in mutez"""
        base_fee = 1000000  # 1 XTZ in mutez
        if edition_mode == EditionMode.FUNGIBLE:
            return base_fee // 2
        return base_fee


class RelayerService:
    """Lazy minting relayer service"""

    def __init__(self, edition_registry, chain_miners: Dict[str, ChainMinter]):
        self.edition_registry = edition_registry
        self.chain_miners = chain_miners
        self.pending_mints: List[LazyMintRequest] = []
        self.logger = logging.getLogger(__name__)

    async def submit_lazy_mint(self, request: LazyMintRequest) -> bool:
        """Submit a lazy minting request"""
        try:
            # Validate the request
            if not self._validate_lazy_request(request):
                return False

            # Store for later processing
            self.pending_mints.append(request)
            self.logger.info(f"✅ Lazy mint request submitted: {request.universal_key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to submit lazy mint: {e}")
            return False

    async def process_pending_mints(self) -> List[MintingResult]:
        """Process pending lazy mint requests"""
        results = []

        for request in self.pending_mints[:]:
            try:
                # Check if edition is authorized
                miner = self.chain_miners.get(request.chain)
                if not miner:
                    self.logger.error(f"No miner for chain: {request.chain}")
                    continue

                authorized = await miner.check_authorization(request.universal_key)
                if not authorized:
                    self.logger.warning(f"Edition not authorized: {request.universal_key}")
                    continue

                # Create edition metadata from request
                edition = EditionMetadata(
                    dna_hash=request.dna_hash,
                    chain=request.chain,
                    contract=request.contract,
                    token_id=request.token_id,
                    edition_no=request.edition_no,
                    edition_mode=request.edition_mode,
                    creator=request.creator,
                    original_asset_path="",  # Would be provided in real implementation
                    dna_signature=request.dna_hash,
                    perceptual_hash="",
                    asset_hash="",
                    image_info={},
                    registration_time=time.time(),
                    last_updated=time.time()
                )

                # Mint the edition
                result = await miner.mint_edition(edition, request.metadata)

                if result.success:
                    request.status = "completed"
                    self.pending_mints.remove(request)
                    self.logger.info(f"✅ Processed lazy mint: {request.universal_key}")
                else:
                    request.status = "failed"
                    self.logger.error(f"Failed to mint: {request.universal_key} - {result.error_message}")

                results.append(result)

            except Exception as e:
                self.logger.error(f"Error processing lazy mint {request.universal_key}: {e}")
                request.status = "error"
                results.append(MintingResult(success=False, error_message=str(e)))

        return results

    def _validate_lazy_request(self, request: LazyMintRequest) -> bool:
        """Validate lazy minting request"""
        # Check expiration
        if request.expires_at and time.time() > request.expires_at:
            return False

        # Check if chain is supported
        if request.chain not in [c.value for c in Chain]:
            return False

        # Check edition mode
        if not isinstance(request.edition_mode, EditionMode):
            return False

        return True

    async def monitor_chain_events(self):
        """Monitor blockchain events for lazy mint activation"""
        # This would integrate with chain-specific event monitoring
        # For now, just a placeholder
        pass


class CrossChainMintingCoordinator:
    """Main coordinator for cross-chain edition minting"""

    def __init__(self, edition_registry):
        self.edition_registry = edition_registry
        self.chain_miners: Dict[str, ChainMinter] = {}
        self.relayer = None
        self.logger = logging.getLogger(__name__)

    def register_chain_miner(self, miner: ChainMinter):
        """Register a chain-specific miner"""
        self.chain_miners[miner.chain.value] = miner
        self.logger.info(f"Registered miner for chain: {miner.chain.value}")

    def initialize_relayer(self, relayer_config: Dict[str, Any]):
        """Initialize the lazy minting relayer"""
        self.relayer = RelayerService(self.edition_registry, self.chain_miners)

    async def mint_cross_chain_edition(self, universal_key: str,
                                     metadata: Optional[Dict[str, Any]] = None) -> MintingResult:
        """Mint an edition across chains"""
        try:
            # Parse universal key
            key = UniversalKey.from_string(universal_key)
            miner = self.chain_miners.get(key.chain)

            if not miner:
                return MintingResult(success=False, error_message=f"No miner for chain: {key.chain}")

            # Check authorization
            authorized = await miner.check_authorization(universal_key)
            if not authorized:
                return MintingResult(success=False, error_message="Edition not authorized")

            # Get edition metadata from registry
            editions = self.edition_registry.get_editions_for_asset(key.dna_hash)
            edition = next((e for e in editions if e.edition_no == key.edition_no and
                           e.contract == key.contract and e.token_id == key.token_id), None)

            if not edition:
                return MintingResult(success=False, error_message="Edition not found in registry")

            # Mint the edition
            if metadata is None:
                metadata = {"name": f"Edition {key.edition_no}", "description": f"Edition {key.edition_no}"}

            result = await miner.mint_edition(edition, metadata)
            return result

        except Exception as e:
            self.logger.error(f"Cross-chain minting failed: {e}")
            return MintingResult(success=False, error_message=str(e))

    async def submit_lazy_mint(self, request: LazyMintRequest) -> bool:
        """Submit lazy minting request"""
        if not self.relayer:
            self.logger.error("Relayer not initialized")
            return False

        return await self.relayer.submit_lazy_mint(request)

    async def process_lazy_mints(self) -> List[MintingResult]:
        """Process pending lazy mints"""
        if not self.relayer:
            return []

        return await self.relayer.process_pending_mints()

    async def get_minting_quote(self, universal_key: str) -> Dict[str, Any]:
        """Get minting cost quote for an edition"""
        try:
            key = UniversalKey.from_string(universal_key)
            miner = self.chain_miners.get(key.chain)

            if not miner:
                return {"error": f"No miner for chain: {key.chain}"}

            # Get edition to determine mode
            editions = self.edition_registry.get_editions_for_asset(key.dna_hash)
            edition = next((e for e in editions if e.edition_no == key.edition_no), None)

            if not edition:
                return {"error": "Edition not found"}

            fee = await miner.get_minting_fee(edition.edition_mode)

            return {
                "chain": key.chain,
                "edition_mode": edition.edition_mode.value,
                "estimated_fee": fee,
                "fee_unit": "wei" if key.chain == "eth" else "lamports" if key.chain == "sol" else "mutez",
                "authorized": await miner.check_authorization(universal_key)
            }

        except Exception as e:
            return {"error": str(e)}


# Factory functions for creating miners
def create_ethereum_miner(config: Dict[str, Any]) -> EthereumMinter:
    """Create Ethereum miner instance"""
    return EthereumMinter(config)

def create_solana_miner(config: Dict[str, Any]) -> SolanaMinter:
    """Create Solana miner instance"""
    return SolanaMinter(config)

def create_tezos_miner(config: Dict[str, Any]) -> TezosMinter:
    """Create Tezos miner instance"""
    return TezosMinter(config)
