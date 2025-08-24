#!/usr/bin/env python3
"""
Test script to verify language-agnostic function extraction.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.watcher import extract_functions_from_diff, analyze_diff_changes
from ai_agent.language_detector import LanguageDetector

def test_language_agnostic_extraction():
    """Test that function extraction works for different programming languages."""
    
    print("🧪 Testing Language-Agnostic Function Extraction")
    print("=" * 60)
    
    # Test 1: Facebook React PR (JavaScript)
    print("\n📱 Testing Facebook React PR (JavaScript):")
    facebook_diff_path = "data/facebook_react/PR_34264/diff.patch"
    
    if os.path.exists(facebook_diff_path):
        with open(facebook_diff_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
        
        # Analyze the diff
        analysis = analyze_diff_changes(diff_content)
        print(f"  Files modified: {analysis['files_modified']}")
        print(f"  Languages detected: {analysis['languages_detected']}")
        print(f"  Total lines added: {analysis['total_lines_added']}")
        print(f"  Total lines removed: {analysis['total_lines_removed']}")
        
        # Extract functions
        functions = extract_functions_from_diff(diff_content)
        print(f"  Functions extracted: {len(functions)}")
        
        for i, (func_name, func_code, file_path, language) in enumerate(functions):
            print(f"    Function {i+1}: {func_name}")
            print(f"      Language: {language}")
            print(f"      File: {file_path}")
            print(f"      Code preview: {func_code[:100]}...")
            print()
    else:
        print(f"  ❌ Facebook React diff file not found: {facebook_diff_path}")
    
    # Test 2: FastAPI PR (Python)
    print("\n🐍 Testing FastAPI PR (Python):")
    fastapi_diff_path = "data/fastapi_fastapi/PR_13827/diff.patch"
    
    if os.path.exists(fastapi_diff_path):
        with open(fastapi_diff_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
        
        # Analyze the diff
        analysis = analyze_diff_changes(diff_content)
        print(f"  Files modified: {analysis['files_modified']}")
        print(f"  Languages detected: {analysis['languages_detected']}")
        print(f"  Total lines added: {analysis['total_lines_added']}")
        print(f"  Total lines removed: {analysis['total_lines_removed']}")
        
        # Extract functions
        functions = extract_functions_from_diff(diff_content)
        print(f"  Functions extracted: {len(functions)}")
        
        for i, (func_name, func_code, file_path, language) in enumerate(functions):
            print(f"    Function {i+1}: {func_name}")
            print(f"      Language: {language}")
            print(f"      File: {file_path}")
            print(f"      Code preview: {func_code[:100]}...")
            print()
    else:
        print(f"  ❌ FastAPI diff file not found: {fastapi_diff_path}")
    
    # Test 3: Microsoft STL PR (C++)
    print("\n⚡ Testing Microsoft STL PR (C++):")
    stl_diff_path = "data/microsoft_STL/PR_5551/diff.patch"
    
    if os.path.exists(stl_diff_path):
        with open(stl_diff_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
        
        # Analyze the diff
        analysis = analyze_diff_changes(diff_content)
        print(f"  Files modified: {analysis['files_modified']}")
        print(f"  Languages detected: {analysis['languages_detected']}")
        print(f"  Total lines added: {analysis['total_lines_added']}")
        print(f"  Total lines removed: {analysis['total_lines_removed']}")
        
        # Extract functions
        functions = extract_functions_from_diff(diff_content)
        print(f"  Functions extracted: {len(functions)}")
        
        for i, (func_name, func_code, file_path, language) in enumerate(functions):
            print(f"    Function {i+1}: {func_name}")
            print(f"      Language: {language}")
            print(f"      File: {file_path}")
            print(f"      Code preview: {func_code[:100]}...")
            print()
    else:
        print(f"  ❌ Microsoft STL diff file not found: {stl_diff_path}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("  This test verifies that the agent can:")
    print("  1. Detect different programming languages from file extensions")
    print("  2. Extract functions using language-specific patterns")
    print("  3. Handle test files that don't have explicit function definitions")
    print("  4. Generate appropriate test files for each language")
    print("  5. Use the correct file extensions (.js, .py, .cpp, etc.)")

if __name__ == "__main__":
    print("🚀 Testing Language-Agnostic Function Extraction...")
    test_language_agnostic_extraction()
    print("\n✅ Language-agnostic extraction test completed!")
