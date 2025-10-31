#!/usr/bin/env python3
"""
ProTRACE Workflow Demonstration
================================

Demonstrates the exact workflow:
1. Extract 256-bit Digital DNA from Image
2. Add DNA to Merkle tree leaves
3. Check if DNA is unique (< 90% similar)
4. If >90% similar → Reject as "DNA Already Exists"
"""

from protrace.image_dna import compute_dna, hamming_distance, dna_similarity
from protrace.merkle import MerkleTree
import time


def demonstrate_workflow():
    """Demonstrate the complete ProTRACE workflow."""
    
    print("\n" + "=" * 70)
    print("ProTRACE WORKFLOW DEMONSTRATION")
    print("=" * 70)
    
    # Simulate 3 images with their DNA hashes
    print("\n📋 SCENARIO: Registering 3 images")
    print("-" * 70)
    
    # Create test DNA hashes (simulating extracted DNAs)
    images = {
        'artwork1.png': 'd7b523525080445e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822',
        'artwork2.png': 'a4c8f92371de89bc1f2e5d9a837b4fc6d2e8a1b7f9c3e045876d2a1b9f4e6c8a',
        'artwork1_copy.png': 'd7b523525080545e036e3e910c60d69a5965cddebe0afbfe0455535edabaf822',  # Very similar to artwork1
    }
    
    # Initialize Merkle tree
    merkle = MerkleTree()
    registered_dnas = []
    
    # Process each image
    for idx, (image_name, dna_hex) in enumerate(images.items(), 1):
        print(f"\n{'='*70}")
        print(f"IMAGE {idx}: {image_name}")
        print('='*70)
        
        # STEP 1: Extract 256-bit DNA (simulated - already extracted)
        print(f"\n🧬 STEP 1: Extract 256-bit Digital DNA")
        print(f"   DNA: {dna_hex[:32]}...{dna_hex[-8:]}")
        print(f"   Bits: 256 (64 hex characters)")
        print(f"   Algorithm: dHash (64-bit) + Grid Hash (192-bit)")
        
        # STEP 2: Check against existing DNAs in Merkle tree
        print(f"\n🔍 STEP 2: Check Against Merkle Tree Leaves")
        print(f"   Existing DNAs in tree: {len(registered_dnas)}")
        
        if len(registered_dnas) == 0:
            print(f"   → First entry - No comparison needed")
            is_duplicate = False
        else:
            print(f"   → Comparing with each existing DNA using Hamming distance...")
            
            is_duplicate = False
            max_similarity = 0.0
            best_match_idx = -1
            best_distance = 0
            
            # Check each existing DNA
            for i, existing_dna in enumerate(registered_dnas):
                # Calculate Hamming distance (bits flipped)
                distance = hamming_distance(dna_hex, existing_dna)
                similarity = dna_similarity(dna_hex, existing_dna)
                
                print(f"\n   Comparison #{i+1}:")
                print(f"     Existing DNA: {existing_dna[:32]}...{existing_dna[-8:]}")
                print(f"     Hamming Distance: {distance} bits different")
                print(f"     Similarity: {similarity*100:.2f}%")
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match_idx = i
                    best_distance = distance
                
                # Check 90% threshold
                if similarity >= 0.90:
                    print(f"     ⚠️  ALERT: Similarity ≥ 90% threshold!")
                    is_duplicate = True
                else:
                    print(f"     ✓ Below 90% threshold")
        
        # STEP 3: Decision
        print(f"\n⚖️  STEP 3: Decision")
        
        if is_duplicate:
            # REJECT: >90% similar
            print(f"   ❌ DUPLICATE DETECTED!")
            print(f"   ┌─────────────────────────────────────────────────")
            print(f"   │ Similarity: {max_similarity*100:.2f}%")
            print(f"   │ Hamming Distance: {best_distance} bits")
            print(f"   │ Threshold: 90.00% (≤26 bits different)")
            print(f"   │ Matched Entry: #{best_match_idx + 1}")
            print(f"   └─────────────────────────────────────────────────")
            print(f"\n   🚫 Result: DNA ALREADY EXISTS")
            print(f"   📛 Action: Image REJECTED - NOT added to Merkle tree")
            
        else:
            # ACCEPT: <90% similar or unique
            print(f"   ✅ UNIQUE DNA!")
            
            if len(registered_dnas) > 0:
                print(f"   ┌─────────────────────────────────────────────────")
                print(f"   │ Best Match: {max_similarity*100:.2f}%")
                print(f"   │ Hamming Distance: {best_distance} bits")
                print(f"   │ Threshold: 90.00% (≤26 bits different)")
                print(f"   │ Status: Below threshold ✓")
                print(f"   └─────────────────────────────────────────────────")
            
            print(f"\n   ✅ Result: DNA is Unique")
            print(f"   ➕ Action: ADD to Merkle tree as new leaf")
            
            # Add to Merkle tree
            timestamp = int(time.time())
            merkle.add_leaf(dna_hex, pointer=image_name, platform_id="demo", timestamp=timestamp)
            registered_dnas.append(dna_hex)
            
            # Rebuild tree
            root_hash = merkle.build_tree()
            
            print(f"\n   📊 Merkle Tree Updated:")
            print(f"      Total Leaves: {len(merkle.leaves)}")
            print(f"      New Root Hash: {root_hash[:32]}...{root_hash[-8:]}")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"WORKFLOW SUMMARY")
    print('='*70)
    print(f"\n📊 Registration Results:")
    print(f"   Total Images Processed: {len(images)}")
    print(f"   Images Registered: {len(registered_dnas)}")
    print(f"   Images Rejected: {len(images) - len(registered_dnas)}")
    
    print(f"\n🌳 Final Merkle Tree:")
    print(f"   Total Leaves: {len(merkle.leaves)}")
    print(f"   Root Hash: {merkle.root.hash.hex() if merkle.root else 'None'}")
    
    print(f"\n✅ Workflow Demonstration Complete!")
    print('='*70)


def show_threshold_examples():
    """Show examples of different similarity levels."""
    
    print("\n" + "=" * 70)
    print("90% SIMILARITY THRESHOLD EXAMPLES")
    print("=" * 70)
    
    print("\n📊 What does 90% similarity mean?")
    print("-" * 70)
    
    examples = [
        (0, "Identical images"),
        (10, "Almost identical (minor edit)"),
        (26, "At the threshold (90%)"),
        (50, "Somewhat different"),
        (128, "Very different"),
        (256, "Completely different")
    ]
    
    print(f"\n{'Hamming Distance':<20} {'Similarity':<15} {'Result':<15} {'Description'}")
    print("-" * 70)
    
    for distance, description in examples:
        similarity = 1.0 - (distance / 256.0)
        result = "❌ DUPLICATE" if similarity >= 0.90 else "✅ UNIQUE"
        print(f"{distance} bits{'':<13} {similarity*100:>5.2f}%{'':<8} {result:<15} {description}")
    
    print("\n💡 Key Insight:")
    print("   • Hamming Distance ≤ 26 bits → Similarity ≥ 90% → DUPLICATE")
    print("   • Hamming Distance > 26 bits → Similarity < 90% → UNIQUE")
    print('='*70)


if __name__ == "__main__":
    # Run workflow demonstration
    demonstrate_workflow()
    
    # Show threshold examples
    show_threshold_examples()
    
    print("\n✅ All demonstrations complete!")
    print("\n📝 Key Takeaways:")
    print("   1. ✅ 256-bit DNA extracted from each image")
    print("   2. ✅ DNA compared against all existing DNAs in Merkle tree")
    print("   3. ✅ Hamming distance used to calculate similarity (bits flipped)")
    print("   4. ✅ If ≥90% similar (≤26 bits different) → REJECT as duplicate")
    print("   5. ✅ If <90% similar → ADD as unique to Merkle tree")
    print()
