#!/usr/bin/env python3
"""
Cross-Chain Edition Management Demo
==================================

Demonstrates the complete ProTrace Cross-Chain Edition Management System:
1. Edition registration with universal keys
2. Cross-chain minting coordination
3. Lazy minting with relayer activation
4. Rule enforcement and validation
"""

import asyncio
import logging
from pathlib import Path
from protrace.edition_core import EditionRegistry, EditionMode, UniversalKey
from protrace.cross_chain_minting import (
    CrossChainMintingCoordinator,
    LazyMintRequest,
    create_ethereum_miner,
    create_solana_miner,
    create_tezos_miner
)
from protrace.relayer_service import LazyMintingRelayer, RelayerConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_edition_management():
    """Demonstrate the complete edition management system"""

    print("🚀 ProTrace Cross-Chain Edition Management Demo")
    print("=" * 60)

    # 1. Initialize Edition Registry
    print("\n1. 📋 Initializing Edition Registry...")
    registry = EditionRegistry()

    # 2. Initialize Cross-Chain Coordinator
    print("2. 🌐 Initializing Cross-Chain Coordinator...")
    coordinator = CrossChainMintingCoordinator(registry)

    # Register chain miners (mock configurations)
    eth_config = {
        'web3_provider': 'https://mainnet.infura.io/v3/...',
        'private_key': '0x...',
        'contract_addresses': {'0x1234...': 'ERC721'}
    }
    sol_config = {
        'rpc_url': 'https://api.mainnet-beta.solana.com',
        'private_key': 'solana_keypair...',
        'program_ids': {'prog1...': 'SPL'}
    }
    tez_config = {
        'rpc_url': 'https://mainnet.api.tez.ie',
        'private_key': 'edsk...',
        'contract_addresses': {'KT1...': 'FA2'}
    }

    coordinator.register_chain_miner(create_ethereum_miner(eth_config))
    coordinator.register_chain_miner(create_solana_miner(sol_config))
    coordinator.register_chain_miner(create_tezos_miner(tez_config))

    # 3. Initialize Relayer Service
    print("3. 📡 Initializing Relayer Service...")
    relayer_config = RelayerConfig(
        poll_interval_seconds=10,
        max_batch_size=5,
        supported_chains=['eth', 'sol', 'tez']
    )
    coordinator.initialize_relayer(relayer_config)

    # 4. Register Core Asset Editions
    print("4. 🎨 Registering Core Asset Editions...")

    # Mock asset path
    asset_path = "Folder X/# (433).png"  # Using existing file

    # Register multiple editions for different chains
    editions_to_register = [
        {
            'asset_path': asset_path,
            'creator': 'artist123',
            'chain': 'eth',
            'contract': '0x1234567890123456789012345678901234567890',
            'token_id': '1',
            'edition_no': 0,
            'edition_mode': EditionMode.STRICT_1_1,
            'max_editions': None
        },
        {
            'asset_path': asset_path,
            'creator': 'artist123',
            'chain': 'sol',
            'contract': '11111111111111111111111111111112',  # Mock Solana program
            'token_id': 'token123',
            'edition_no': 1,
            'edition_mode': EditionMode.SERIAL,
            'max_editions': 100
        },
        {
            'asset_path': asset_path,
            'creator': 'artist123',
            'chain': 'tez',
            'contract': 'KT1BRwoJcnqkKUjQ2vjN2n6mQFQGYmF8tKvV',
            'token_id': '100',
            'edition_no': 0,
            'edition_mode': EditionMode.FUNGIBLE,
            'max_editions': None
        }
    ]

    registered_editions = []
    for edition_data in editions_to_register:
        success, message, edition = registry.register_edition(**edition_data)
        if success:
            registered_editions.append(edition)
            print(f"   ✅ Registered: {edition.to_universal_key().to_string()}")
        else:
            print(f"   ❌ Failed: {message}")

    # 5. Demonstrate Rule Enforcement
    print("\n5. 🛡️  Testing Rule Enforcement...")

    # Try to register invalid edition (duplicate 1/1)
    invalid_edition = {
        'asset_path': asset_path,
        'creator': 'artist123',
        'chain': 'eth',
        'contract': '0x1234567890123456789012345678901234567890',
        'token_id': '1',
        'edition_no': 0,  # Same as existing 1/1
        'edition_mode': EditionMode.STRICT_1_1,
        'max_editions': None
    }

    success, message, _ = registry.register_edition(**invalid_edition)
    if not success:
        print(f"   ✅ Rule enforced: {message}")
    else:
        print("   ❌ Rule violation allowed!")

    # 6. Demonstrate Cross-Chain Minting Quotes
    print("\n6. 💰 Getting Minting Quotes...")

    for edition in registered_editions:
        universal_key = edition.to_universal_key().to_string()
        quote = await coordinator.get_minting_quote(universal_key)

        if 'error' not in quote:
            print(f"   {universal_key}: {quote['estimated_fee']} {quote['fee_unit']} ({quote['edition_mode']})")
        else:
            print(f"   {universal_key}: Error - {quote['error']}")

    # 7. Demonstrate Lazy Minting
    print("\n7. 🕐 Setting up Lazy Minting...")

    lazy_request = LazyMintRequest(
        universal_key=registered_editions[0].to_universal_key().to_string(),
        dna_hash=registered_editions[0].dna_hash,
        chain='eth',
        contract='0x1234567890123456789012345678901234567890',
        token_id='1',
        edition_no=0,
        edition_mode=EditionMode.STRICT_1_1,
        creator='artist123',
        metadata={'name': 'Lazy Minted NFT', 'description': 'Activated by sale'},
        expires_at=None
    )

    success = await coordinator.submit_lazy_mint(lazy_request)
    if success:
        print(f"   ✅ Lazy mint request submitted: {lazy_request.universal_key}")
    else:
        print("   ❌ Lazy mint request failed")

    # 8. Demonstrate Registry Queries
    print("\n8. 📊 Registry Statistics...")

    stats = registry.get_registry_stats()
    print(f"   Total Editions: {stats['total_editions']}")
    print(f"   Total Core Assets: {stats['total_core_assets']}")
    print(f"   Supported Chains: {', '.join(stats['chains'])}")
    print(f"   Edition Modes: {', '.join(stats['edition_modes'])}")

    # Show editions for the core asset
    dna_hash = registered_editions[0].dna_hash
    asset_editions = registry.get_editions_for_asset(dna_hash)
    print(f"   Editions for DNA {dna_hash[:16]}...: {len(asset_editions)}")

    for edition in asset_editions:
        key = edition.to_universal_key()
        print(f"     • {key.to_string()} ({edition.edition_mode.value})")

    # 9. Demonstrate Cross-Chain Minting (Mock)
    print("\n9. 🪙 Cross-Chain Minting Simulation...")

    # Note: Actual minting would require real blockchain connections
    # This demonstrates the interface
    for edition in registered_editions[:1]:  # Just demo one
        universal_key = edition.to_universal_key().to_string()
        print(f"   Simulating mint for: {universal_key}")

        # In production, this would actually mint on the blockchain
        # result = await coordinator.mint_cross_chain_edition(universal_key)
        # if result.success:
        #     print(f"   ✅ Minted: {result.transaction_hash}")
        # else:
        #     print(f"   ❌ Mint failed: {result.error_message}")

        print("   (Minting skipped - requires real blockchain connection)")

    print("\n" + "=" * 60)
    print("✅ Cross-Chain Edition Management Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("• ✅ Universal Key Format (dna_hash#chain#contract#token_id#edition_no)")
    print("• ✅ Edition Modes (1/1 Strict, Serial, Fungible)")
    print("• ✅ Rule Enforcement (prevents unauthorized editions)")
    print("• ✅ Cross-Chain Support (ETH, SOL, TEZ)")
    print("• ✅ Lazy Minting Infrastructure")
    print("• ✅ Registry with Comprehensive Metadata")
    print("• ✅ Minting Cost Estimation")
    print("\n🎯 Ready for production deployment!")


async def demo_batch_edition_registration():
    """Demonstrate batch edition registration for efficiency"""

    print("\n🔄 Batch Edition Registration Demo")
    print("-" * 40)

    registry = EditionRegistry()

    # Create batch of editions
    batch_editions = []
    asset_path = "Folder X/# (433).png"

    for i in range(1, 11):  # Editions 1-10
        batch_editions.append({
            'asset_path': asset_path,
            'creator': 'batch_artist',
            'chain': 'eth',
            'contract': '0x9876543210987654321098765432109876543210',
            'token_id': str(i),
            'edition_no': 1,  # All serial editions
            'edition_mode': EditionMode.SERIAL,
            'max_editions': 10
        })

    # Register batch
    success, message, successful_keys = registry.batch_register_editions(batch_editions)

    if success:
        print(f"✅ Batch registration successful: {len(successful_keys)} editions")
        for key in successful_keys[:3]:  # Show first 3
            print(f"   • {key}")
        if len(successful_keys) > 3:
            print(f"   • ... and {len(successful_keys) - 3} more")
    else:
        print(f"❌ Batch registration failed: {message}")


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(demo_edition_management())

    # Run batch demo
    asyncio.run(demo_batch_edition_registration())
