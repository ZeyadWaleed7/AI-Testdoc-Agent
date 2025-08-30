#!/usr/bin/env python3
"""Script to fix existing problematic .txt files by renaming them with correct extensions"""

import os
import glob
from pathlib import Path

def detect_language_from_content(file_path):
    """Detect language from file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for language-specific patterns in content
        if 'import unittest' in content or 'def test_' in content or 'assert ' in content:
            return '.py'  # Python
        elif 'func Test' in content or 'package main' in content:
            return '.go'  # Go
        elif 'func Test' in content and 'testing.T' in content:
            return '.go'  # Go
        elif 'TEST(' in content or '#include <gtest' in content:
            return '.cpp'  # C++
        elif 'describe(' in content or 'test(' in content or 'expect(' in content:
            return '.js'  # JavaScript
        elif 'class Test' in content or '@Test' in content:
            return '.java'  # Java
        elif 'fn test_' in content or '#[test]' in content:
            return '.rs'  # Rust
        else:
            # Default to Python for now
            return '.py'
            
    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")
        return '.py'  # Default fallback

def fix_existing_files():
    """Fix existing .txt files by renaming them with correct extensions"""
    
    print("🔧 Fixing existing problematic .txt files")
    print("=" * 50)
    
    # Find all .txt files in the deepseek_coder directories
    txt_files = []
    for root, dirs, files in os.walk("data"):
        for file in files:
            if file.endswith('.txt') and 'deepseek_coder' in root:
                txt_files.append(os.path.join(root, file))
    
    if not txt_files:
        print("✅ No problematic .txt files found")
        return
    
    print(f"📁 Found {len(txt_files)} .txt files to fix:")
    
    fixed_count = 0
    
    for txt_file in txt_files:
        print(f"\n🔍 Processing: {txt_file}")
        
        # Detect language from file content
        correct_ext = detect_language_from_content(txt_file)
        print(f"   📝 Detected language: {correct_ext}")
        
        # Create the new filename
        new_filename = str(txt_file).replace('.txt', correct_ext)
        
        try:
            # Rename the file
            os.rename(txt_file, new_filename)
            print(f"✅ Renamed: {txt_file} -> {new_filename}")
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Error renaming {txt_file}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Summary:")
    print(f"   - Files found: {len(txt_files)}")
    print(f"   - Files fixed: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} files!")
    else:
        print("\n💥 No files were fixed.")

if __name__ == "__main__":
    fix_existing_files()
