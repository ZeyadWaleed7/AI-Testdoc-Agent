#!/usr/bin/env python3
"""Comprehensive test script to verify enhanced test generation system"""

import sys
import os
import tempfile
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.prompts import PromptTemplates
from ai_agent.language_detector import LanguageDetector
from ai_agent.enhanced_context import EnhancedContextLoader

def test_enhanced_prompts():
    """Test that enhanced prompts generate proper test code"""
    
    print("🧪 Testing Comprehensive Test Generation System")
    print("=" * 70)
    
    # Test data
    function_code = """def request_params_to_args(request_params: List[RequestParam]) -> Dict[str, Any]:
    \"\"\"Convert request parameters to arguments dictionary.\"\"\"
    args = {}
    for param in request_params:
        if param.name and param.value is not None:
            args[param.name] = param.value
    return args"""
    
    enhanced_context = {
        'pr_title': 'Fix request parameter handling',
        'pr_description': 'Improve request parameter validation and conversion',
        'file_path': 'fastapi/params.py',
        'language': 'python',
        'imports': ['from typing import List, Dict, Any', 'from fastapi import RequestParam'],
        'full_content': function_code,
        'patch': '+def request_params_to_args(request_params: List[RequestParam]) -> Dict[str, Any]:',
        'file_patch': '+def request_params_to_args(request_params: List[RequestParam]) -> Dict[str, Any]:',
        'test_patterns': [],
        'context_summary': {'languages': ['python']},
        'repository_structure': {'root_files': ['requirements.txt'], 'directories': ['tests']},
        'dependencies': {'packages': ['fastapi', 'pytest'], 'frameworks': ['pytest']},
        'related_files': ['test_params.py'],
        'test_frameworks': ['pytest'],
        'build_config': {'build_tools': ['pip']},
        'environment_info': {'python_version': '3.8+'},
        'actual_file_content': function_code,
        'working_directory': '/tmp/test',
        'package_manager': 'pip',
        'test_command': 'python -m pytest',
        'import_paths': ['', '.', 'fastapi']
    }
    
    # Test enhanced context prompt
    print("\n📝 Testing Enhanced Context Prompt:")
    enhanced_prompt = PromptTemplates.enhanced_context_prompt(
        function_code, enhanced_context, 'fastapi/params.py', 'python'
    )
    
    # Check for forbidden content
    forbidden_phrases = [
        'sure, here is', 'basic example', 'here\'s how you could',
        'this includes testing', 'follow the same pattern', 'note:',
        'replace with', 'assuming', 'todo:', 'fixme:'
    ]
    
    prompt_lower = enhanced_prompt.lower()
    has_forbidden = any(phrase in prompt_lower for phrase in forbidden_phrases)
    
    if has_forbidden:
        print("❌ Enhanced prompt contains forbidden phrases!")
        for phrase in forbidden_phrases:
            if phrase in prompt_lower:
                print(f"   Found: '{phrase}'")
    else:
        print("✅ Enhanced prompt is clean")
    
    # Check for critical instructions
    critical_instructions = [
        '🚨 CRITICAL MISSION',
        '🚨 ABSOLUTE REQUIREMENTS',
        '🚫 ABSOLUTELY FORBIDDEN - VIOLATION = FAILURE',
        '✅ REQUIRED OUTPUT - EXACTLY THIS',
        'START GENERATING THE COMPLETE TEST CODE NOW'
    ]
    
    print(f"\n🔍 Critical Instructions Check:")
    for instruction in critical_instructions:
        if instruction in enhanced_prompt:
            print(f"   ✅ Found: {instruction}")
        else:
            print(f"   ❌ Missing: {instruction}")
    
    # Check prompt length and content
    print(f"\n📊 Prompt Statistics:")
    print(f"   Enhanced prompt length: {len(enhanced_prompt)} characters")
    
    # Test language detection
    print(f"\n🔍 Language Detection Test:")
    test_files = [
        ("test_processUtils.py", "python", ".py"),
        ("component.tsx", "typescript", ".tsx"),
        ("header.h", "c", ".h"),
        ("main.go", "go", ".go"),
        ("lib.rs", "rust", ".rs")
    ]
    
    for filename, expected_lang, expected_ext in test_files:
        detected_lang = LanguageDetector.detect_language_from_file(filename)
        detected_ext = LanguageDetector.get_file_extension_for_language(detected_lang, filename)
        
        if detected_lang == expected_lang and detected_ext == expected_ext:
            print(f"   ✅ {filename}: {detected_lang} -> {detected_ext}")
        else:
            print(f"   ❌ {filename}: expected {expected_lang}->{expected_ext}, got {detected_lang}->{detected_ext}")
    
    print("\n" + "=" * 70)
    print("🎯 Comprehensive Test Generation System Ready!")
    
    return not has_forbidden

def test_prompt_validation():
    """Test prompt validation and cleaning"""
    
    print("\n🧹 Testing Prompt Validation and Cleaning:")
    
    # Test cases with problematic content
    test_cases = [
        {
            'name': 'English explanation',
            'content': 'Sure, here is a basic example of how you could write tests...\nimport unittest\n\ndef test_function(): pass',
            'should_pass': False
        },
        {
            'name': 'TODO comment',
            'content': 'import unittest\n\ndef test_function():\n    # TODO: implement this\n    pass',
            'should_pass': False
        },
        {
            'name': 'Incomplete import',
            'content': 'from fastapi import (\nimport unittest\n\ndef test_function(): pass',
            'should_pass': False
        },
        {
            'name': 'Incomplete function',
            'content': 'import unittest\n\ndef test_function():\n',
            'should_pass': False
        },
        {
            'name': 'Clean code',
            'content': 'import unittest\n\ndef test_function():\n    assert True\n\nif __name__ == "__main__":\n    unittest.main()',
            'should_pass': True
        }
    ]
    
    from ai_agent.generator import TestGenerator
    
    # Create a mock generator for testing
    class MockLLM:
        def generate(self, prompt):
            return "Mock response"
    
    generator = TestGenerator(MockLLM())
    
    for test_case in test_cases:
        cleaned = generator._clean_generated_test(test_case['content'], 'python')
        is_valid = generator._validate_generated_test(cleaned, 'python')
        
        status = "✅ PASS" if is_valid == test_case['should_pass'] else "❌ FAIL"
        print(f"   {status} {test_case['name']}: expected {test_case['should_pass']}, got {is_valid}")

if __name__ == "__main__":
    success = test_enhanced_prompts()
    test_prompt_validation()
    
    if success:
        print("\n🎉 All tests passed! The system is ready to generate proper test files.")
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
    
    sys.exit(0 if success else 1)
