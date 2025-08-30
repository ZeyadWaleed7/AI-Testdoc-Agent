#!/usr/bin/env python3
"""Script to clean up problematic test files and regenerate them"""

import os
import shutil
import logging
from pathlib import Path

def cleanup_problematic_tests():
    """Remove existing problematic test files"""
    print("🧹 Cleaning up problematic test files...")
    
    # Path to the PR data
    pr_data_path = "data/fastapi_fastapi/PR_13827"
    
    if not os.path.exists(pr_data_path):
        print(f"❌ PR data path not found: {pr_data_path}")
        return
    
    # Remove existing test files
    test_dir = f"{pr_data_path}/deepseek_coder/enhanced_context"
    if os.path.exists(test_dir):
        print(f"🗑️  Removing existing test directory: {test_dir}")
        shutil.rmtree(test_dir)
        print("✅ Existing test files removed")
    
    # Remove the enhanced-context directory if it exists
    enhanced_context_dir = f"{pr_data_path}/deepseek_coder/enhanced_context/enhanced-context"
    if os.path.exists(enhanced_context_dir):
        print(f"🗑️  Removing enhanced-context directory: {enhanced_context_dir}")
        shutil.rmtree(enhanced_context_dir)
        print("✅ Enhanced-context directory removed")

def main():
    """Main cleanup function"""
    print("🚀 Test File Cleanup and Regeneration")
    print("=" * 50)
    
    # Clean up existing files
    cleanup_problematic_tests()
    
    print("\n✅ Cleanup completed!")
    print("\n📝 Now run: python regenerate_fixed_tests.py")
    print("This will regenerate all test files with the improved agent.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
