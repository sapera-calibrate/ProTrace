"""
Relayer Service for Lazy Minting
================================

Monitors blockchain events and processes lazy minting requests.
Supports activation of pending mints based on on-chain events.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import time
import json

from .cross_chain_minting import LazyMintRequest, MintingResult, Chain
from .edition_core import EditionRegistry

logger = logging.getLogger(__name__)


@dataclass
class ChainEvent:
    """Represents a blockchain event"""
    chain: str
    contract: str
    event_type: str  # "Transfer", "Mint", "Sale", etc.
    transaction_hash: str
    block_number: int
    log_index: int
    timestamp: int
    args: Dict[str, Any]  # Event arguments
    raw_data: Dict[str, Any]


@dataclass
class RelayerConfig:
    """Configuration for the relayer service"""
    poll_interval_seconds: int = 30
    max_batch_size: int = 10
    max_retries: int = 3
    retry_delay_seconds: int = 5
    event_lookback_blocks: int = 100
    supported_chains: List[str] = None

    def __post_init__(self):
        if self.supported_chains is None:
            self.supported_chains = [c.value for c in Chain]


class EventMonitor(ABC):
    """Abstract base class for chain-specific event monitoring"""

    def __init__(self, chain: str, config: Dict[str, Any]):
        self.chain = chain
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{chain}")

    @abstractmethod
    async def get_recent_events(self, from_block: int, to_block: int) -> List[ChainEvent]:
        """Get recent events from the blockchain"""
        pass

    @abstractmethod
    async def get_current_block(self) -> int:
        """Get current block number"""
        pass

    def filter_protrace_events(self, events: List[ChainEvent]) -> List[ChainEvent]:
        """Filter events relevant to ProTrace lazy minting"""
        protrace_events = []

        for event in events:
            # Check if event contains ProTrace DNA hash
            if self._is_protrace_event(event):
                protrace_events.append(event)

        return protrace_events

    def _is_protrace_event(self, event: ChainEvent) -> bool:
        """Check if event is related to ProTrace"""
        # Look for ProTrace DNA hash in event args
        args_str = json.dumps(event.args, default=str).lower()
        return 'protrace_dna' in args_str or 'dna_hash' in args_str


class EthereumEventMonitor(EventMonitor):
    """Monitor Ethereum events"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("eth", config)
        self.web3_provider = config.get('web3_provider')
        self.contract_addresses = config.get('contract_addresses', [])

    async def get_recent_events(self, from_block: int, to_block: int) -> List[ChainEvent]:
        """Get Ethereum events (mock implementation)"""
        # In production, this would use web3.py to query events
        # For now, return empty list
        return []

    async def get_current_block(self) -> int:
        """Get current Ethereum block"""
        # Mock implementation
        return 18500000


class SolanaEventMonitor(EventMonitor):
    """Monitor Solana events"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("sol", config)
        self.rpc_url = config.get('rpc_url')
        self.program_ids = config.get('program_ids', [])

    async def get_recent_events(self, from_block: int, to_block: int) -> List[ChainEvent]:
        """Get Solana events (mock implementation)"""
        # In production, this would use solana-py to query logs
        return []

    async def get_current_block(self) -> int:
        """Get current Solana slot"""
        return 200000000


class TezosEventMonitor(EventMonitor):
    """Monitor Tezos events"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("tez", config)
        self.rpc_url = config.get('rpc_url')
        self.contract_addresses = config.get('contract_addresses', [])

    async def get_recent_events(self, from_block: int, to_block: int) -> List[ChainEvent]:
        """Get Tezos events (mock implementation)"""
        return []

    async def get_current_block(self) -> int:
        """Get current Tezos level"""
        return 4000000


class LazyMintingRelayer:
    """Relayer service for processing lazy minting requests"""

    def __init__(self, edition_registry: EditionRegistry,
                 cross_chain_coordinator: Any, config: RelayerConfig):
        self.edition_registry = edition_registry
        self.coordinator = cross_chain_coordinator
        self.config = config

        # Event monitors for each chain
        self.event_monitors: Dict[str, EventMonitor] = {}
        self.last_processed_blocks: Dict[str, int] = {}

        # Pending lazy mints
        self.pending_requests: List[LazyMintRequest] = []
        self.processing_queue: asyncio.Queue = asyncio.Queue()

        # Callbacks
        self.event_callbacks: List[Callable] = []

        self.logger = logging.getLogger(__name__)
        self.running = False

    def register_event_monitor(self, monitor: EventMonitor):
        """Register an event monitor for a chain"""
        self.event_monitors[monitor.chain] = monitor
        self.last_processed_blocks[monitor.chain] = 0
        self.logger.info(f"Registered event monitor for chain: {monitor.chain}")

    def add_event_callback(self, callback: Callable):
        """Add callback for processing events"""
        self.event_callbacks.append(callback)

    async def submit_lazy_request(self, request: LazyMintRequest) -> bool:
        """Submit a lazy minting request"""
        try:
            # Validate request
            if not self._validate_request(request):
                return False

            # Add to pending requests
            self.pending_requests.append(request)

            # Add to processing queue
            await self.processing_queue.put(request)

            self.logger.info(f"✅ Lazy mint request submitted: {request.universal_key}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to submit lazy request: {e}")
            return False

    def _validate_request(self, request: LazyMintRequest) -> bool:
        """Validate lazy minting request"""
        # Check chain support
        if request.chain not in self.config.supported_chains:
            return False

        # Check expiration
        if request.expires_at and time.time() > request.expires_at:
            return False

        # Check for duplicate pending requests
        for pending in self.pending_requests:
            if pending.universal_key == request.universal_key:
                return False

        return True

    async def start_monitoring(self):
        """Start the relayer monitoring loop"""
        self.running = True
        self.logger.info("Starting lazy minting relayer...")

        # Start background tasks
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        processing_task = asyncio.create_task(self._processing_loop())

        try:
            await asyncio.gather(monitoring_task, processing_task)
        except Exception as e:
            self.logger.error(f"Relayer error: {e}")
        finally:
            self.running = False

    async def stop_monitoring(self):
        """Stop the relayer"""
        self.running = False
        self.logger.info("Stopping lazy minting relayer...")

    async def _monitoring_loop(self):
        """Main monitoring loop for blockchain events"""
        while self.running:
            try:
                # Monitor each supported chain
                for chain, monitor in self.event_monitors.items():
                    await self._process_chain_events(chain, monitor)

                # Wait before next poll
                await asyncio.sleep(self.config.poll_interval_seconds)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.retry_delay_seconds)

    async def _process_chain_events(self, chain: str, monitor: EventMonitor):
        """Process events for a specific chain"""
        try:
            # Get current block
            current_block = await monitor.get_current_block()
            last_processed = self.last_processed_blocks.get(chain, current_block - self.config.event_lookback_blocks)

            if current_block <= last_processed:
                return

            # Get recent events
            events = await monitor.get_recent_events(last_processed + 1, current_block)

            # Filter ProTrace events
            protrace_events = monitor.filter_protrace_events(events)

            if protrace_events:
                self.logger.info(f"Found {len(protrace_events)} ProTrace events on {chain}")

                # Process events
                for event in protrace_events:
                    await self._handle_event(event)

            # Update last processed block
            self.last_processed_blocks[chain] = current_block

        except Exception as e:
            self.logger.error(f"Error processing {chain} events: {e}")

    async def _handle_event(self, event: ChainEvent):
        """Handle a blockchain event"""
        try:
            # Check if event triggers lazy mint activation
            activation_data = self._extract_activation_data(event)

            if activation_data:
                # Find matching lazy request
                matching_request = self._find_matching_request(activation_data)

                if matching_request:
                    # Activate the lazy mint
                    await self._activate_lazy_mint(matching_request, event)

            # Call registered callbacks
            for callback in self.event_callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")

        except Exception as e:
            self.logger.error(f"Error handling event {event.transaction_hash}: {e}")

    def _extract_activation_data(self, event: ChainEvent) -> Optional[Dict[str, Any]]:
        """Extract activation data from event"""
        # Look for ProTrace-specific fields
        args = event.args

        dna_hash = args.get('protrace_dna') or args.get('dna_hash')
        if not dna_hash:
            return None

        return {
            'dna_hash': dna_hash,
            'chain': event.chain,
            'contract': event.contract,
            'token_id': args.get('token_id') or args.get('tokenId'),
            'edition_no': args.get('edition_no') or args.get('editionNo', 0),
            'event_type': event.event_type,
            'transaction_hash': event.transaction_hash
        }

    def _find_matching_request(self, activation_data: Dict[str, Any]) -> Optional[LazyMintRequest]:
        """Find matching lazy mint request"""
        for request in self.pending_requests:
            if (request.dna_hash == activation_data['dna_hash'] and
                request.chain == activation_data['chain'] and
                request.contract == activation_data['contract'] and
                request.token_id == activation_data['token_id'] and
                request.edition_no == activation_data['edition_no']):
                return request
        return None

    async def _activate_lazy_mint(self, request: LazyMintRequest, event: ChainEvent):
        """Activate a lazy minting request"""
        try:
            self.logger.info(f"🎯 Activating lazy mint: {request.universal_key}")

            # Submit to cross-chain coordinator for immediate minting
            result = await self.coordinator.mint_cross_chain_edition(
                request.universal_key,
                request.metadata
            )

            if result.success:
                # Remove from pending requests
                self.pending_requests.remove(request)
                self.logger.info(f"✅ Lazy mint activated successfully: {request.universal_key}")
            else:
                self.logger.error(f"Failed to activate lazy mint: {result.error_message}")

        except Exception as e:
            self.logger.error(f"Error activating lazy mint: {e}")

    async def _processing_loop(self):
        """Process queued lazy minting requests"""
        while self.running:
            try:
                # Get next request from queue
                request = await self.processing_queue.get()

                # Process the request
                await self._process_lazy_request(request)

                # Mark task as done
                self.processing_queue.task_done()

            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)

    async def _process_lazy_request(self, request: LazyMintRequest):
        """Process a lazy minting request"""
        try:
            # For immediate processing (not event-triggered)
            # This could be used for direct minting or batch processing

            if request.status == "ready_for_mint":
                result = await self.coordinator.mint_cross_chain_edition(
                    request.universal_key,
                    request.metadata
                )

                if result.success:
                    request.status = "completed"
                    self.logger.info(f"✅ Processed lazy request: {request.universal_key}")
                else:
                    request.status = "failed"
                    self.logger.error(f"Failed to process lazy request: {result.error_message}")

        except Exception as e:
            self.logger.error(f"Error processing lazy request: {e}")
            request.status = "error"

    async def get_pending_requests(self, chain: Optional[str] = None) -> List[LazyMintRequest]:
        """Get pending lazy minting requests"""
        if chain:
            return [r for r in self.pending_requests if r.chain == chain]
        return self.pending_requests.copy()

    async def cancel_request(self, universal_key: str) -> bool:
        """Cancel a lazy minting request"""
        for request in self.pending_requests:
            if request.universal_key == universal_key:
                self.pending_requests.remove(request)
                self.logger.info(f"✅ Cancelled lazy request: {universal_key}")
                return True
        return False

    async def get_relayer_stats(self) -> Dict[str, Any]:
        """Get relayer statistics"""
        return {
            'pending_requests': len(self.pending_requests),
            'supported_chains': list(self.event_monitors.keys()),
            'last_processed_blocks': self.last_processed_blocks.copy(),
            'queue_size': self.processing_queue.qsize(),
            'uptime': time.time() - time.time(),  # Would track actual start time
            'total_processed': 0  # Would track historical data
        }


# Factory functions for creating event monitors
def create_ethereum_monitor(config: Dict[str, Any]) -> EthereumEventMonitor:
    """Create Ethereum event monitor"""
    return EthereumEventMonitor(config)

def create_solana_monitor(config: Dict[str, Any]) -> SolanaEventMonitor:
    """Create Solana event monitor"""
    return SolanaEventMonitor(config)

def create_tezos_monitor(config: Dict[str, Any]) -> TezosEventMonitor:
    """Create Tezos event monitor"""
    return TezosEventMonitor(config)
