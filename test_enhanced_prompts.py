#!/usr/bin/env python3
"""Test script to verify enhanced prompts generate proper test code"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.prompts import PromptTemplates
from ai_agent.language_detector import LanguageDetector

def test_enhanced_prompts():
    """Test that enhanced prompts generate proper test code"""
    
    print("🧪 Testing Enhanced Prompts")
    print("=" * 50)
    
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
        'environment_info': {'python_version': '3.8+'}
    }
    
    # Test enhanced context prompt
    print("\n📝 Testing Enhanced Context Prompt:")
    enhanced_prompt = PromptTemplates.enhanced_context_prompt(
        function_code, enhanced_context, 'fastapi/params.py', 'python'
    )
    
    # Check for forbidden content
    forbidden_phrases = [
        'sure, here is', 'basic example', 'here\'s how you could',
        'this includes testing', 'follow the same pattern'
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
    
    # Test naive prompt
    print("\n📝 Testing Naive Prompt:")
    naive_prompt = PromptTemplates.naive_prompt(function_code, 'python')
    
    naive_lower = naive_prompt.lower()
    has_forbidden_naive = any(phrase in naive_lower for phrase in forbidden_phrases)
    
    if has_forbidden_naive:
        print("❌ Naive prompt contains forbidden phrases!")
        for phrase in forbidden_phrases:
            if phrase in naive_lower:
                print(f"   Found: '{phrase}'")
    else:
        print("✅ Naive prompt is clean")
    
    # Check prompt length and content
    print(f"\n📊 Prompt Statistics:")
    print(f"   Enhanced prompt length: {len(enhanced_prompt)} characters")
    print(f"   Naive prompt length: {len(naive_prompt)} characters")
    
    # Check for critical instructions
    critical_instructions = [
        '🚨 CRITICAL REQUIREMENTS',
        '🚫 ABSOLUTELY FORBIDDEN',
        '✅ REQUIRED OUTPUT',
        'START GENERATING THE TEST CODE NOW'
    ]
    
    print(f"\n🔍 Critical Instructions Check:")
    for instruction in critical_instructions:
        if instruction in enhanced_prompt:
            print(f"   ✅ Found: {instruction}")
        else:
            print(f"   ❌ Missing: {instruction}")
    
    print("\n" + "=" * 50)
    print("🎯 Prompt Enhancement Complete!")
    
    return not (has_forbidden or has_forbidden_naive)

if __name__ == "__main__":
    success = test_enhanced_prompts()
    sys.exit(0 if success else 1)
