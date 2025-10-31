#!/usr/bin/env python3
"""
ProTrace 2.0 - Cross-Platform NFT Duplicate Prevention Service
==============================================================

Main CLI application for ProTrace digital asset verification with advanced
edition management and duplicate prevention across multiple blockchains.

New Features (v2.0):
- 128-bit DNA (dHash + pHash) perceptual fingerprinting
- Vector database integration for O(log n) similarity search
- BLAKE3 Merkle tree commitments
- EIP-712 signed registrations
- Hamming distance-based duplicate detection (≤13 bits = ≥90% match)

Usage:
    # DNA Operations
    python protrace.py dna compute <image_path>
    python protrace.py dna check <image_path> [--threshold BITS]
    python protrace.py dna compare <image1> <image2>
    
    # Registration & Verification
    python protrace.py register <image_path> [--edition-mode MODE] [--series-size SIZE]
    python protrace.py verify <dna_hash> <chain> <contract> <token_id> <edition_no>
    
    # Edition Management
    python protrace.py edition add <dna_hash> <edition_no> [--chain CHAIN] [--contract CONTRACT]
    
    # Registry Operations
    python protrace.py registry info
    python protrace.py registry export
    
    # Legacy Commands (still supported)
    python protrace.py similarity <image1> <image2>
"""

import sys
import os
import json
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from protrace.image_dna import extract_dna_features, dna_similarity_unified, dna_feasibility_matrix

# Registry file path
REGISTRY_FILE = Path("V_on_chain/minted_registry.json")

def load_registry() -> Dict[str, Dict]:
    """Load the registry from file."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return {}

def save_registry(registry: Dict[str, Dict]):
    """Save the registry to file."""
    REGISTRY_FILE.parent.mkdir(exist_ok=True)
    try:
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"✅ Registry saved to {REGISTRY_FILE}")
    except Exception as e:
        print(f"❌ Error saving registry: {e}")

def generate_edition_key(dna_hash: str, chain: str, contract: str, token_id: str, edition_no: int) -> str:
    """Generate universal edition key for cross-chain compatibility."""
    return f"{dna_hash}#{chain}#{contract}#{token_id}#{edition_no}"

def validate_edition_rules(registry: Dict[str, Dict], dna_hash: str, edition_no: int, blockchain: str) -> Tuple[bool, str]:
    """Validate edition minting against edition rules."""
    # Find the core asset by DNA hash
    core_asset = None
    for asset_data in registry.values():
        if asset_data.get('dna_hash') == dna_hash:
            core_asset = asset_data
            break

    if not core_asset:
        return False, "Core asset not found"

    edition_mode = core_asset.get('edition_mode', '1/1 strict')
    series_size = core_asset.get('series_size', 1)
    editions_minted = core_asset.get('editions_minted', 0)

    # Check edition rules
    if edition_mode == '1/1 strict':
        if editions_minted >= 1:
            return False, "1/1 strict: Only one edition allowed"
        if edition_no != 1:
            return False, "1/1 strict: Edition number must be 1"

    elif edition_mode == 'serial':
        if edition_no < 1 or edition_no > series_size:
            return False, f"Serial: Edition number {edition_no} out of range (1-{series_size})"
        # Check if this edition number already exists
        for edition in core_asset.get('editions', []):
            if edition.get('edition_no') == edition_no:
                return False, f"Serial: Edition {edition_no} already exists"

    elif edition_mode == 'fungible/open':
        # Allow unlimited editions, no specific validation needed
        pass

    else:
        return False, f"Unknown edition mode: {edition_mode}"

    return True, "Edition valid"

def verify_nft_edition(dna_hash: str, chain: str, contract: str, token_id: str, edition_no: int, registry: Dict[str, Dict]) -> Dict:
    """Verify an NFT edition and return detailed information."""
    # Generate edition key
    edition_key = generate_edition_key(dna_hash, chain, contract, token_id, edition_no)

    # Find the core asset
    core_asset = None
    for asset_data in registry.values():
        if asset_data.get('dna_hash') == dna_hash:
            core_asset = asset_data
            break

    if not core_asset:
        return {
            "valid": False,
            "error": "Core asset not found",
            "dna_hash": dna_hash
        }

    # Check if edition exists
    edition_found = None
    for edition in core_asset.get('editions', []):
        if edition.get('edition_key') == edition_key:
            edition_found = edition
            break

    if not edition_found:
        return {
            "valid": False,
            "error": "Edition not found",
            "dna_hash": dna_hash,
            "edition_key": edition_key,
            "core_asset": core_asset.get('filename', 'unknown')
        }

    # Return edition verification info
    return {
        "valid": True,
        "dna_hash": dna_hash,
        "edition_key": edition_key,
        "edition_no": edition_no,
        "series_size": core_asset.get('series_size', 1),
        "edition_mode": core_asset.get('edition_mode', '1/1 strict'),
        "editions_minted": core_asset.get('editions_minted', 0),
        "core_asset": {
            "filename": core_asset.get('filename', 'unknown'),
            "creator": core_asset.get('creator', 'unknown'),
            "blockchain": core_asset.get('blockchain', 'unknown'),
            "status": core_asset.get('status', 'unknown')
        },
        "edition": {
            "chain": edition_found.get('chain', 'unknown'),
            "contract": edition_found.get('contract', 'unknown'),
            "token_id": edition_found.get('token_id', 'unknown'),
            "filename": edition_found.get('filename', 'unknown'),
            "minted_at": edition_found.get('minted_at', 'unknown')
        }
    }

def register_asset(image_path: str, edition_mode: str = '1/1 strict', series_size: int = 1) -> Dict:
    """Register a new core asset with edition management."""
    if not os.path.exists(image_path):
        return {"success": False, "error": f"Image file not found: {image_path}"}

    # Extract DNA hash
    try:
        dna_data = extract_dna_features(image_path)
        dna_hash = dna_data['dna_signature']
    except Exception as e:
        return {"success": False, "error": f"Failed to extract DNA: {e}"}

    # Load existing registry
    registry = load_registry()

    # Check if DNA hash already exists
    for asset_data in registry.values():
        if asset_data.get('dna_hash') == dna_hash:
            return {"success": False, "error": "Asset with this DNA hash already exists"}

    # Create new core asset
    asset_id = hashlib.sha256(dna_hash.encode()).hexdigest()

    registry[asset_id] = {
        "asset_id": asset_id,
        "filename": Path(image_path).name,
        "dna_hash": dna_hash,
        "creator": "cli_user",
        "status": "registered",
        "blockchain": "universal",
        "edition_mode": edition_mode,
        "series_size": series_size,
        "editions_minted": 0,
        "metadata": {
            "filename": Path(image_path).name,
            "dna_hash": dna_hash,
            "edition_mode": edition_mode,
            "series_size": series_size
        },
        "editions": [],
        "registered_at": str(Path(image_path).stat().st_mtime)
    }

    # Save registry
    save_registry(registry)

    return {
        "success": True,
        "asset_id": asset_id,
        "dna_hash": dna_hash,
        "edition_mode": edition_mode,
        "series_size": series_size
    }

def add_edition(dna_hash: str, edition_no: int, chain: str = "simulated", contract: str = "test_contract") -> Dict:
    """Add a new edition to an existing core asset."""
    registry = load_registry()

    # Validate edition rules
    is_valid, error_msg = validate_edition_rules(registry, dna_hash, edition_no, chain)
    if not is_valid:
        return {"success": False, "error": error_msg}

    # Find the core asset
    core_asset = None
    asset_id = None
    for aid, asset_data in registry.items():
        if asset_data.get('dna_hash') == dna_hash:
            core_asset = asset_data
            asset_id = aid
            break

    if not core_asset:
        return {"success": False, "error": "Core asset not found"}

    # Generate edition key
    token_id = f"edition_{edition_no}_{len(core_asset['editions']) + 1}"
    edition_key = generate_edition_key(dna_hash, chain, contract, token_id, edition_no)

    # Add edition
    edition_entry = {
        "edition_key": edition_key,
        "edition_no": edition_no,
        "chain": chain,
        "contract": contract,
        "token_id": token_id,
        "filename": core_asset.get('filename', f'edition_{edition_no}'),
        "minted_at": "cli_generated"
    }

    registry[asset_id]['editions'].append(edition_entry)
    registry[asset_id]['editions_minted'] += 1

    # Save registry
    save_registry(registry)

    return {
        "success": True,
        "edition_key": edition_key,
        "edition_no": edition_no,
        "core_asset": core_asset.get('filename', 'unknown')
    }

def cmd_verify(args):
    """Verify an NFT edition."""
    registry = load_registry()
    result = verify_nft_edition(args.dna_hash, args.chain, args.contract, args.token_id, args.edition_no, registry)

    if result['valid']:
        print("✅ EDITION VERIFIED")
        print(f"DNA Hash: {result['dna_hash']}")
        print(f"Edition Key: {result['edition_key']}")
        print(f"Edition: {result['edition_no']}/{result['series_size']}")
        print(f"Mode: {result['edition_mode']}")
        print(f"Core Asset: {result['core_asset']['filename']}")
        print(f"Chain: {result['edition']['chain']}")
        print(f"Minted: {result['edition']['minted_at']}")
    else:
        print("❌ VERIFICATION FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'edition_key' in result:
            print(f"Edition Key: {result['edition_key']}")

def cmd_register(args):
    """Register a new core asset."""
    result = register_asset(args.image_path, args.edition_mode, args.series_size)

    if result['success']:
        print("✅ ASSET REGISTERED")
        print(f"Asset ID: {result['asset_id']}")
        print(f"DNA Hash: {result['dna_hash']}")
        print(f"Edition Mode: {result['edition_mode']}")
        print(f"Series Size: {result['series_size']}")
    else:
        print("❌ REGISTRATION FAILED")
        print(f"Error: {result['error']}")

def cmd_edition_add(args):
    """Add a new edition to a core asset."""
    result = add_edition(args.dna_hash, args.edition_no, args.chain, args.contract)

    if result['success']:
        print("✅ EDITION ADDED")
        print(f"Edition Key: {result['edition_key']}")
        print(f"Edition: {result['edition_no']}")
        print(f"Core Asset: {result['core_asset']}")
    else:
        print("❌ EDITION ADD FAILED")
        print(f"Error: {result['error']}")

def cmd_registry_info(args):
    """Show registry information."""
    registry = load_registry()
    print("📊 REGISTRY INFO")
    print(f"Total Assets: {len(registry)}")

    total_editions = 0
    edition_modes = {}

    for asset_data in registry.values():
        editions = asset_data.get('editions', [])
        total_editions += len(editions)
        mode = asset_data.get('edition_mode', 'unknown')
        edition_modes[mode] = edition_modes.get(mode, 0) + 1

    print(f"Total Editions: {total_editions}")
    print("Edition Modes:")
    for mode, count in edition_modes.items():
        print(f"  {mode}: {count} assets")

def cmd_registry_export(args):
    """Export registry to console."""
    registry = load_registry()
    print(json.dumps(registry, indent=2))

def cmd_similarity_check(args):
    """Check similarity between two images using advanced algorithms."""
    if not os.path.exists(args.image1) or not os.path.exists(args.image2):
        print("❌ One or both image files not found")
        return

    print("🔍 ANALYZING IMAGE SIMILARITY")
    print(f"Image 1: {args.image1}")
    print(f"Image 2: {args.image2}")
    print("-" * 40)

    # Unified similarity analysis
    unified_result = dna_similarity_unified(args.image1, args.image2)
    print("📊 UNIFIED SIMILARITY SCORE:")
    print(f"Similarity: {unified_result['unified_similarity']:.3f}")
    print(f"Hamming Distance: {unified_result['hamming_distance']} bits")
    print(f"Is Duplicate (≤13 bits): {unified_result['is_duplicate']}")
    print(f"Individual Scores: {unified_result['individual_scores']}")
    print(f"Method: {unified_result['method']}")

    # Feasibility matrix analysis
    feasibility = dna_feasibility_matrix(args.image1, args.image2)
    print("\n🎯 FEASIBILITY MATRIX ANALYSIS:")
    print(f"Overall Feasibility: {feasibility['overall_feasibility']:.3f}")
    print(f"Feasibility Level: {feasibility['feasibility_level']}")
    print(f"Confidence Level: {feasibility['confidence_level']}")
    print(f"Recommendation: {feasibility['recommendation']}")

    # Interpretation
    similarity = unified_result['unified_similarity']
    if similarity >= 0.95:
        print("\n✅ IMAGES ARE IDENTICAL OR NEAR-IDENTICAL")
    elif similarity >= 0.90:
        print("\n⚠️  IMAGES ARE VERY SIMILAR (duplicate detected)")
    elif similarity >= 0.80:
        print("\n🤔 IMAGES ARE SIMILAR")
    else:
        print("\n❌ IMAGES ARE DIFFERENT")

def cmd_dna_compute(args):
    """Compute DNA fingerprint for an image."""
    from protrace import compute_dna
    
    if not os.path.exists(args.image_path):
        print(f"❌ Image not found: {args.image_path}")
        return
    
    print(f"🧬 Computing DNA for: {args.image_path}")
    
    try:
        dna_result = compute_dna(args.image_path)
        
        print("\n✅ DNA COMPUTED SUCCESSFULLY")
        print(f"DNA (256-bit): {dna_result['dna_hex']}")
        print(f"dHash (64-bit): {dna_result['dhash']}")
        print(f"Grid Hash (192-bit): {dna_result['grid_hash']}")
        print(f"Algorithm: {dna_result['algorithm']}")
        print(f"Total bits: {dna_result['bits']}")
        
        if args.verbose:
            print(f"\nBinary representation:")
            print(f"{dna_result['dna_binary']}")
            
    except Exception as e:
        print(f"❌ DNA computation failed: {e}")
        import traceback
        traceback.print_exc()

def cmd_dna_check(args):
    """Check if image is a duplicate in registry."""
    from protrace import compute_dna, create_vector_db
    
    if not os.path.exists(args.image_path):
        print(f"❌ Image not found: {args.image_path}")
        return
    
    print(f"🔍 Checking uniqueness for: {args.image_path}")
    
    try:
        # Compute DNA
        dna_result = compute_dna(args.image_path)
        dna_hex = dna_result['dna_hex']
        
        print(f"DNA: {dna_hex}")
        
        # Check in vector DB (using in-memory for now)
        db = create_vector_db(use_postgres=False)
        db.connect()
        
        is_unique, candidates = db.check_uniqueness(dna_hex, threshold=args.threshold)
        
        if is_unique:
            print(f"\n✅ UNIQUE - No duplicates found")
            print(f"This image can be minted")
        else:
            print(f"\n⚠️  DUPLICATE DETECTED")
            print(f"Found {len(candidates)} similar image(s):")
            for i, candidate in enumerate(candidates, 1):
                print(f"\n  {i}. Platform: {candidate['platform_id']}")
                print(f"     Token ID: {candidate['token_id']}")
                print(f"     Hamming Distance: {candidate['hamming_distance']} bits")
                print(f"     Similarity: {candidate['similarity_percent']}%")
                
        db.close()
        
    except Exception as e:
        print(f"❌ Check failed: {e}")

def cmd_dna_compare(args):
    """Compare DNA of two images."""
    from protrace import compute_dna, hamming_distance, dna_similarity
    
    if not os.path.exists(args.image1):
        print(f"❌ Image 1 not found: {args.image1}")
        return
    if not os.path.exists(args.image2):
        print(f"❌ Image 2 not found: {args.image2}")
        return
    
    print("🔬 COMPARING DNA FINGERPRINTS\n")
    
    try:
        # Compute DNAs
        dna1 = compute_dna(args.image1)
        dna2 = compute_dna(args.image2)
        
        print(f"Image 1: {args.image1}")
        print(f"DNA: {dna1['dna_hex']}\n")
        
        print(f"Image 2: {args.image2}")
        print(f"DNA: {dna2['dna_hex']}\n")
        
        # Calculate metrics
        distance = hamming_distance(dna1['dna_hex'], dna2['dna_hex'])
        similarity = dna_similarity(dna1['dna_hex'], dna2['dna_hex'])
        
        print("=" * 60)
        print(f"Hamming Distance: {distance} bits (out of 128)")
        print(f"Similarity: {similarity:.1%}")
        print(f"Duplicate (≤13 bits): {'YES ⚠️' if distance <= 13 else 'NO ✅'}")
        print("=" * 60)
        
        if distance == 0:
            print("\n🎯 EXACT MATCH - Identical images")
        elif distance <= 13:
            print("\n⚠️  DUPLICATE - Images are perceptually identical (≥90% match)")
        elif distance <= 26:
            print("\n🤔 SIMILAR - Images are very similar (≥80% match)")
        else:
            print("\n✅ DIFFERENT - Images are distinct")
            
    except Exception as e:
        print(f"❌ Comparison failed: {e}")

def cli():
    """CLI entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="ProTrace 2.0 - Cross-Platform NFT Duplicate Prevention Service")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # DNA command group (NEW in v2.0)
    dna_parser = subparsers.add_parser('dna', help='DNA fingerprint operations')
    dna_subparsers = dna_parser.add_subparsers(dest='dna_command')
    
    # DNA compute
    compute_parser = dna_subparsers.add_parser('compute', help='Compute DNA fingerprint for image')
    compute_parser.add_argument('image_path', help='Path to image file')
    compute_parser.add_argument('-v', '--verbose', action='store_true', help='Show binary representation')
    compute_parser.set_defaults(func=cmd_dna_compute)
    
    # DNA check
    check_parser = dna_subparsers.add_parser('check', help='Check if image is duplicate')
    check_parser.add_argument('image_path', help='Path to image file')
    check_parser.add_argument('--threshold', type=int, default=13, help='Hamming distance threshold (default: 13)')
    check_parser.set_defaults(func=cmd_dna_check)
    
    # DNA compare
    compare_parser = dna_subparsers.add_parser('compare', help='Compare DNA of two images')
    compare_parser.add_argument('image1', help='Path to first image')
    compare_parser.add_argument('image2', help='Path to second image')
    compare_parser.set_defaults(func=cmd_dna_compare)

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify an NFT edition')
    verify_parser.add_argument('dna_hash', help='DNA hash of the asset')
    verify_parser.add_argument('chain', help='Blockchain (ethereum, solana, bitcoin, etc.)')
    verify_parser.add_argument('contract', help='Contract address')
    verify_parser.add_argument('token_id', help='Token ID')
    verify_parser.add_argument('edition_no', type=int, help='Edition number')
    verify_parser.set_defaults(func=cmd_verify)

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new core asset')
    register_parser.add_argument('image_path', help='Path to image file')
    register_parser.add_argument('--edition-mode', default='1/1 strict',
                                choices=['1/1 strict', 'serial', 'fungible/open'],
                                help='Edition mode (default: 1/1 strict)')
    register_parser.add_argument('--series-size', type=int, default=1,
                                help='Series size for serial editions (default: 1)')
    register_parser.set_defaults(func=cmd_register)

    # Edition command
    edition_parser = subparsers.add_parser('edition', help='Edition management')
    edition_subparsers = edition_parser.add_subparsers(dest='edition_command')

    # Edition add
    add_parser = edition_subparsers.add_parser('add', help='Add a new edition')
    add_parser.add_argument('dna_hash', help='DNA hash of the core asset')
    add_parser.add_argument('edition_no', type=int, help='Edition number')
    add_parser.add_argument('--chain', default='simulated', help='Blockchain')
    add_parser.add_argument('--contract', default='test_contract', help='Contract address')
    add_parser.set_defaults(func=cmd_edition_add)

    # Registry command
    registry_parser = subparsers.add_parser('registry', help='Registry management')
    registry_subparsers = registry_parser.add_subparsers(dest='registry_command')

    # Registry info
    info_parser = registry_subparsers.add_parser('info', help='Show registry info')
    info_parser.set_defaults(func=cmd_registry_info)

    # Registry export
    export_parser = registry_subparsers.add_parser('export', help='Export registry to console')
    export_parser.set_defaults(func=cmd_registry_export)

    # Similarity command
    similarity_parser = subparsers.add_parser('similarity', help='Check image similarity using advanced algorithms')
    similarity_parser.add_argument('image1', help='Path to first image')
    similarity_parser.add_argument('image2', help='Path to second image')
    similarity_parser.set_defaults(func=cmd_similarity_check)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    args.func(args)

def main():
    """Main entry point for CLI."""
    return cli()

if __name__ == "__main__":
    sys.exit(main() or 0)
