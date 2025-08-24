#!/usr/bin/env python3
"""
Test script to verify Ollama integration with DeepSeek Coder model.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.llm import PhindCodeLlamaLLM
from ai_agent.language_detector import LanguageDetector

def test_ollama_integration():
    """Test the Ollama integration with DeepSeek Coder."""
    
    print("🧪 Testing Ollama Integration with DeepSeek Coder")
    print("=" * 60)
    
    # Test 1: Language Detection
    print("\n📁 Testing Language Detection:")
    test_file = "test_component.jsx"
    detected_lang = LanguageDetector.detect_language_from_file(test_file)
    print(f"  File: {test_file} -> Language: {detected_lang}")
    
    # Test 2: Test Framework Detection
    if detected_lang:
        frameworks = LanguageDetector.get_test_frameworks_for_language(detected_lang)
        print(f"  Test frameworks: {', '.join(frameworks)}")
    
    # Test 3: Ollama Connection
    print("\n🔌 Testing Ollama Connection:")
    try:
        llm = PhindCodeLlamaLLM(
            model_name="deepseek-coder",
            provider="ollama"
        )
        print("  ✅ Ollama connection successful!")
        print(f"  Model: {llm.model_name}")
        print(f"  Provider: {llm.provider}")
        
    except Exception as e:
        print(f"  ❌ Ollama connection failed: {e}")
        print("  Make sure Ollama is running: ollama serve")
        print("  Make sure deepseek-coder is available: ollama list")
        return False
    
    # Test 4: Simple Generation
    print("\n💬 Testing Simple Generation:")
    try:
        response = llm.generate("Write a simple JavaScript function that adds two numbers.")
        print("  ✅ Generation successful!")
        print(f"  Response length: {len(response)} characters")
        print(f"  Response preview: {response[:100]}...")
        
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        return False
    
    # Test 5: Test Generation
    print("\n🧪 Testing Test Generation:")
    try:
        test_code = llm.generate_test(
            function_code="""export function add(a, b) {
    return a + b;
}""",
            diff_context="Added new add function",
            prompt_strategy="diff-aware",
            language="javascript"
        )
        print("  ✅ Test generation successful!")
        print(f"  Test code length: {len(test_code)} characters")
        print(f"  Test code preview: {test_code[:100]}...")
        
    except Exception as e:
        print(f"  ❌ Test generation failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Ollama integration is working correctly.")
    return True

def test_facebook_react_scenario():
    """Test a realistic Facebook React PR scenario."""
    
    print("\n" + "=" * 60)
    print("📱 Testing Facebook React PR Scenario")
    print("=" * 60)
    
    try:
        llm = PhindCodeLlamaLLM(
            model_name="deepseek-coder",
            provider="ollama"
        )
        
        # Simulate a React component from Facebook React
        react_component = """import React from 'react';

export function useCustomHook() {
    const [state, setState] = React.useState(null);
    
    React.useEffect(() => {
        // Effect logic
    }, []);
    
    return [state, setState];
}"""
        
        print("  📝 React Component:")
        print(f"  {react_component}")
        
        print("\n  🧪 Generating Tests...")
        test_code = llm.generate_test(
            function_code=react_component,
            diff_context="Added new custom hook for state management",
            prompt_strategy="diff-aware",
            language="javascript"
        )
        
        print("  ✅ Test Generation Successful!")
        print(f"  Generated test file extension: {LanguageDetector.get_file_extension_for_language('javascript')}")
        print("\n  📄 Generated Test Code:")
        print("  " + "=" * 50)
        print(test_code)
        print("  " + "=" * 50)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Facebook React scenario failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ollama Integration Tests...")
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
        else:
            print("❌ Ollama is not responding correctly")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please start Ollama with: ollama serve")
        sys.exit(1)
    
    # Run tests
    success = test_ollama_integration()
    
    if success:
        test_facebook_react_scenario()
    
    print("\n🎯 Test Summary:")
    if success:
        print("✅ Ollama integration is ready for use!")
        print("🚀 You can now run: python main.py --provider ollama --model deepseek-coder --process-only --repo-filter facebook_react")
    else:
        print("❌ Ollama integration needs attention")
        print("🔧 Check the error messages above and ensure Ollama is running")
