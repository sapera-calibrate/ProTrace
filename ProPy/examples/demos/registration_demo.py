#!/usr/bin/env python3
"""
Demo: Register New Image with Duplicate Detection
=================================================

This demonstrates the registration system that:
1. Computes 256-bit DNA hash for a new image
2. Checks similarity against all existing entries
3. Flags as plagiarized if >90% similar to any existing image
4. Adds to Merkle tree registry only if unique
"""

from register_image import register_image
import os

def demo_with_new_image():
    """
    Demo registration with a new image.
    
    To use with the uploaded character art image:
    1. Save the image to this directory as 'new_character_art.png'
    2. Run: python demo_registration.py
    """
    
    # Check if user has placed a new image
    new_image_path = "new_character_art.png"
    
    if not os.path.exists(new_image_path):
        print("=" * 60)
        print("DEMO: Image Registration System")
        print("=" * 60)
        print("\nTo test with your uploaded character art image:")
        print("1. Save the image as 'new_character_art.png' in this directory")
        print("2. Run: python demo_registration.py")
        print("\nOr use the command line:")
        print("  python register_image.py <path_to_image> [pointer] [platform]")
        print("\nExample:")
        print("  python register_image.py new_character_art.png my_nft opensea")
        print("\n" + "=" * 60)
        
        # Demo with existing image to show plagiarism detection
        print("\nDEMO: Testing with an existing image (should be flagged)...")
        print("=" * 60)
        test_image = "Folder X/# (100).png"
        if os.path.exists(test_image):
            result = register_image(test_image, pointer="demo_test", platform_id="demo")
            return result
        else:
            print("Demo image not found.")
            return None
    
    # Register the new image
    print("\n🎨 Registering your character art image...")
    result = register_image(
        new_image_path, 
        pointer="character_art_nft", 
        platform_id="opensea"
    )
    
    return result


if __name__ == "__main__":
    result = demo_with_new_image()
    
    if result:
        print("\n" + "=" * 60)
        print("REGISTRATION SUMMARY")
        print("=" * 60)
        
        if result['success']:
            print("✅ STATUS: ACCEPTED")
            print(f"   DNA Hash: {result['dna'][:32]}...")
            print(f"   Pointer: {result['pointer']}")
            print(f"   Platform: {result['platform_id']}")
            print(f"   Registry Size: {result['registry_size']} images")
            print(f"   Root Hash: {result['root_hash'][:32]}...")
            
            if result.get('best_match'):
                print(f"\n   Closest Match: {result['best_match']['similarity']:.2f}%")
        else:
            print("❌ STATUS: REJECTED")
            if result.get('plagiarized'):
                print(f"   Reason: Plagiarism detected")
                print(f"   Similarity: {result['match']['similarity']:.2f}%")
                print(f"   Matched Entry: #{result['match']['index']}")
            else:
                print(f"   Reason: {result.get('error', 'Unknown error')}")
        
        print("=" * 60)
