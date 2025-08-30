#!/usr/bin/env python3
"""Test script to verify language detection fixes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.language_detector import LanguageDetector

def test_language_detection():
    """Test the improved language detection"""
    
    print("🧪 Testing Language Detection Fixes")
    print("=" * 50)
    
    # Test cases: (filename, expected_language, expected_extension)
    test_cases = [
        ("test_processUtils.py", "python", ".py"),
        ("utils.py", "python", ".py"),
        ("main.js", "javascript", ".js"),
        ("component.tsx", "typescript", ".tsx"),
        ("test.cpp", "cpp", ".cpp"),
        ("header.h", "c", ".h"),
        ("main.go", "go", ".go"),
        ("lib.rs", "rust", ".rs"),
        ("test.java", "java", ".java"),
        ("app.rb", "ruby", ".rb"),
        ("unknown.xyz", "unknown", ".txt"),
    ]
    
    all_passed = True
    
    for filename, expected_lang, expected_ext in test_cases:
        print(f"\n📁 Testing: {filename}")
        
        # Test language detection from extension
        detected_lang = LanguageDetector.get_language_from_extension(filename)
        print(f"   Language: {detected_lang} (expected: {expected_lang})")
        
        # Test file extension from language
        detected_ext = LanguageDetector.get_file_extension_for_language(detected_lang, filename)
        print(f"   Extension: {detected_ext} (expected: {expected_ext})")
        
        # Test file extension from extension (should work now)
        detected_ext_from_ext = LanguageDetector.get_file_extension_for_language(filename.split('.')[-1], filename)
        print(f"   Extension from ext: {detected_ext_from_ext} (expected: {expected_ext})")
        
        # Check results
        lang_correct = detected_lang == expected_lang
        ext_correct = detected_ext == expected_ext
        ext_from_ext_correct = detected_ext_from_ext == expected_ext
        
        if lang_correct and ext_correct and ext_from_ext_correct:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Language detection is working correctly.")
    else:
        print("💥 Some tests failed. Check the output above.")
    
    return all_passed

if __name__ == "__main__":
    success = test_language_detection()
    sys.exit(0 if success else 1)
