#!/usr/bin/env python3
"""
ProTRACE CLI - Testnet
Command-line interface for DNA extraction and Merkle trees
"""

import sys
from pathlib import Path
import argparse
import json
import time

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.protrace_legacy.image_dna import compute_dna
from modules.protrace_legacy.merkle import MerkleTree

def print_banner():
    """Print CLI banner"""
    print("=" * 80)
    print("🧬 ProTRACE CLI - Testnet")
    print("=" * 80)
    print()

def cmd_extract_dna(args):
    """Extract DNA from image"""
    print_banner()
    print(f"📸 Extracting DNA from: {args.image}")
    print()
    
    start_time = time.time()
    
    try:
        result = compute_dna(args.image)
        extraction_time = (time.time() - start_time) * 1000
        
        print("✅ DNA Extraction Complete")
        print()
        print(f"DNA Hash:   {result['dna_hex']}")
        print(f"DHash:      {result['dhash']}")
        print(f"Grid Hash:  {result['grid_hash']}")
        print(f"Algorithm:  {result['algorithm']}")
        print(f"Bits:       {result['bits']}")
        print(f"Time:       {extraction_time:.2f}ms")
        print()
        
        if args.output:
            output_data = {
                "image": str(args.image),
                "dna_hash": result['dna_hex'],
                "dhash": result['dhash'],
                "grid_hash": result['grid_hash'],
                "algorithm": result['algorithm'],
                "bits": result['bits'],
                "extraction_time_ms": extraction_time
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Saved to: {args.output}")
            print()
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def cmd_create_merkle(args):
    """Create Merkle tree from DNA hashes"""
    print_banner()
    print(f"🌲 Creating Merkle tree from: {args.input}")
    print()
    
    start_time = time.time()
    
    try:
        # Load DNA hashes from file
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            leaves = data
        elif isinstance(data, dict) and 'leaves' in data:
            leaves = data['leaves']
        else:
            print("❌ Invalid input format. Expected list of DNA hashes or {leaves: [...]}")
            return 1
        
        if not leaves:
            print("❌ No leaves found in input file")
            return 1
        
        print(f"📝 Processing {len(leaves)} leaves...")
        print()
        
        # Create Merkle tree
        tree = MerkleTree()
        
        for i, leaf in enumerate(leaves):
            tree.add_leaf(leaf, f"ptr_{i}", "testnet", int(time.time()))
        
        # Build tree
        root = tree.build_tree()
        
        generation_time = (time.time() - start_time) * 1000
        
        print("✅ Merkle Tree Created")
        print()
        print(f"Root:       {root}")
        print(f"Leaves:     {len(leaves)}")
        print(f"Time:       {generation_time:.2f}ms")
        print()
        
        if args.output:
            output_data = {
                "root": root,
                "leaf_count": len(leaves),
                "network": "testnet",
                "generation_time_ms": generation_time,
                "leaves": leaves
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"💾 Saved to: {args.output}")
            print()
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def cmd_batch_extract(args):
    """Batch extract DNA from multiple images"""
    print_banner()
    print(f"📁 Batch extracting DNA from: {args.directory}")
    print()
    
    directory = Path(args.directory)
    
    if not directory.is_dir():
        print(f"❌ Directory not found: {directory}")
        return 1
    
    # Find all images
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    images = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    
    if not images:
        print(f"❌ No images found in: {directory}")
        return 1
    
    print(f"📸 Found {len(images)} images")
    print()
    
    results = []
    errors = []
    
    for i, image_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] Processing: {image_path.name}...", end=' ')
        
        try:
            result = compute_dna(str(image_path))
            results.append({
                "filename": image_path.name,
                "dna_hash": result['dna_hex'],
                "dhash": result['dhash'],
                "grid_hash": result['grid_hash']
            })
            print("✅")
        
        except Exception as e:
            errors.append({
                "filename": image_path.name,
                "error": str(e)
            })
            print(f"❌ {e}")
    
    print()
    print(f"✅ Successfully processed: {len(results)}/{len(images)}")
    if errors:
        print(f"❌ Failed: {len(errors)}/{len(images)}")
    print()
    
    # Save results
    output_file = args.output or directory / "dna_hashes.json"
    output_data = {
        "directory": str(directory),
        "total_images": len(images),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    
    return 0 if not errors else 1

def cmd_info(args):
    """Show program information"""
    print_banner()
    print("📊 ProTRACE Information")
    print()
    print("Network:     Solana Testnet")
    print("Program ID:  7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG")
    print("RPC URL:     https://api.testnet.solana.com")
    print()
    print("Features:")
    print("  ✅ 256-bit DNA fingerprinting")
    print("  ✅ BLAKE3-based Merkle trees")
    print("  ✅ Solana Testnet integration")
    print()
    print("Commands:")
    print("  extract    - Extract DNA from single image")
    print("  batch      - Batch extract from directory")
    print("  merkle     - Create Merkle tree")
    print("  info       - Show this information")
    print()
    print("API Server:")
    print("  Start: python api_testnet.py")
    print("  Docs:  http://localhost:8000/docs")
    print()
    
    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ProTRACE CLI - DNA extraction and Merkle trees on Solana Testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract DNA from single image
  python cli_testnet.py extract image.png
  
  # Extract and save to file
  python cli_testnet.py extract image.png -o result.json
  
  # Batch extract from directory
  python cli_testnet.py batch ./images/ -o hashes.json
  
  # Create Merkle tree from hashes
  python cli_testnet.py merkle hashes.json -o tree.json
  
  # Show program info
  python cli_testnet.py info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract DNA from image')
    extract_parser.add_argument('image', type=Path, help='Image file path')
    extract_parser.add_argument('-o', '--output', type=Path, help='Output JSON file')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch extract DNA from directory')
    batch_parser.add_argument('directory', type=Path, help='Directory containing images')
    batch_parser.add_argument('-o', '--output', type=Path, help='Output JSON file')
    
    # Merkle command
    merkle_parser = subparsers.add_parser('merkle', help='Create Merkle tree')
    merkle_parser.add_argument('input', type=Path, help='Input JSON file with DNA hashes')
    merkle_parser.add_argument('-o', '--output', type=Path, help='Output JSON file')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show program information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    commands = {
        'extract': cmd_extract_dna,
        'batch': cmd_batch_extract,
        'merkle': cmd_create_merkle,
        'info': cmd_info
    }
    
    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
