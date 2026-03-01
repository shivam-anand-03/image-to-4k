#!/usr/bin/env python3
"""
Batch convert all images from input folder to 4K resolution (3840x2160)
and save them to the outputs folder.

Usage:
    python batch_convert_4k.py [tool_name]
    
    If tool_name is provided, outputs will be named: toolname_001.jpg, toolname_002.jpg, etc.
    Otherwise, outputs will be named: 001.jpg, 002.jpg, etc.
"""

from PIL import Image
import os
import sys
from pathlib import Path

# Supported image formats
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif'}

def resize_to_4k(image_path, output_path):
    """Resize image to exact 4K dimensions (3840x2160)"""
    try:
        img = Image.open(image_path)
        
        print(f"Processing: {image_path.name}")
        print(f"  Original size: {img.size}")
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])
            img = rgb_img
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Resize to exact 4K dimensions
        img_4k = img.resize((3840, 2160), Image.Resampling.LANCZOS)
        
        # Save with optimization
        img_4k.save(output_path, quality=95, optimize=True)
        
        print(f"  ✓ Saved to: {output_path.name} (4K: 3840x2160)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {image_path.name}: {str(e)}")
        return False

def batch_convert(tool_name=None):
    """Convert all images from input folder to 4K
    
    Args:
        tool_name: Optional tool/project name for output files
    """
    # Set up directories
    input_dir = Path('input')
    output_dir = Path('outputs')
    
    # Create directories if they don't exist
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Get all image files from input directory
    image_files = [
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in ALLOWED_EXTENSIONS
    ]
    
    if not image_files:
        print("No images found in the input folder!")
        print(f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
        return
    
    print(f"Found {len(image_files)} image(s) to process")
    if tool_name:
        print(f"Tool name: {tool_name}")
        print(f"Output format: {tool_name}_image_001.jpg, {tool_name}_image_002.jpg, etc.\n")
    else:
        print("Output format: 001.jpg, 002.jpg, etc.\n")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for index, image_file in enumerate(image_files, start=1):
        # Create output filename with sequential numbering (3-digit zero-padded)
        if tool_name:
            # Sanitize tool name
            safe_tool_name = tool_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            output_filename = f'{safe_tool_name}_image_{index:03d}.jpg'
        else:
            output_filename = f'{index:03d}.jpg'
        output_path = output_dir / output_filename
        
        if resize_to_4k(image_file, output_path):
            successful += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 60)
    print(f"\nBatch conversion complete!")
    print(f"  ✓ Successfully converted: {successful}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}")
    print(f"\nOutput location: {output_dir.absolute()}")

if __name__ == '__main__':
    # Get tool name from command line argument if provided
    tool_name = sys.argv[1] if len(sys.argv) > 1 else None
    batch_convert(tool_name)
