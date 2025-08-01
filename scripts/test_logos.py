#!/usr/bin/env python3
"""
Test script to verify that logos are properly generated and accessible
"""

import os
from PIL import Image

def test_logos():
    """Test that logo files exist and are valid"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(os.path.dirname(script_dir), 'frontend', 'public')
    
    logos_to_test = [
        ('logo192.png', 192, 192),
        ('logo512.png', 512, 512),
        ('favicon.ico', None, None)  # ICO files can have multiple sizes
    ]
    
    print("🔍 Testing logo files...")
    
    all_passed = True
    
    for filename, expected_width, expected_height in logos_to_test:
        logo_path = os.path.join(public_dir, filename)
        
        # Check if file exists
        if not os.path.exists(logo_path):
            print(f"❌ {filename}: File does not exist")
            all_passed = False
            continue
        
        # Check file size
        file_size = os.path.getsize(logo_path)
        if file_size == 0:
            print(f"❌ {filename}: File is empty (0 bytes)")
            all_passed = False
            continue
        
        # Try to open and validate image
        try:
            with Image.open(logo_path) as img:
                if filename.endswith('.png') and expected_width and expected_height:
                    if img.size != (expected_width, expected_height):
                        print(f"❌ {filename}: Wrong size {img.size}, expected ({expected_width}, {expected_height})")
                        all_passed = False
                        continue
                
                print(f"✅ {filename}: Valid image, size {img.size}, format {img.format}, {file_size} bytes")
                
        except Exception as e:
            print(f"❌ {filename}: Cannot open as image - {e}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All logo files are valid and properly sized!")
    else:
        print("\n⚠️  Some logo files have issues. Run generate_logo512.py to fix them.")
    
    return all_passed

if __name__ == "__main__":
    test_logos()
