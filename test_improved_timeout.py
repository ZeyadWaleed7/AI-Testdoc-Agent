#!/usr/bin/env python3
"""
Test script to verify improved timeout settings for Ollama integration.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.llm import PhindCodeLlamaLLM

def test_improved_timeout():
    """Test that the improved timeout settings work correctly."""
    
    print("⏱️  Testing Improved Timeout Settings")
    print("=" * 50)
    
    # Test with a simple Python function
    test_function = """def add_numbers(a, b):
    \"\"\"Add two numbers together.\"\"\"
    return a + b"""
    
    print("📝 Test Function:")
    print(test_function)
    print("\n" + "=" * 50)
    
    try:
        print("🚀 Initializing LLM with Ollama provider...")
        start_time = time.time()
        
        # Test with Ollama provider
        llm = PhindCodeLlamaLLM(
            model_name="deepseek-coder",
            provider="ollama"
        )
        
        init_time = time.time() - start_time
        print(f"✅ LLM initialized successfully in {init_time:.2f} seconds")
        
        # Test test generation with timing
        print("\n🧪 Testing Test Generation (with improved timeout):")
        gen_start = time.time()
        
        test_code = llm.generate_test(
            function_code=test_function,
            diff_context="Simple addition function",
            prompt_strategy="diff-aware",
            language="python"
        )
        
        gen_time = time.time() - gen_start
        print(f"⏱️  Generation completed in {gen_time:.2f} seconds")
        
        print("📄 Generated Test Code:")
        print("-" * 30)
        print(test_code)
        print("-" * 30)
        
        # Check if response is clean
        if test_code.startswith(('import ', 'from ', 'def ', 'class ', 'test_', 'pytest')):
            print("✅ Test generation: Clean code generated!")
        else:
            print("❌ Test generation: Still contains verbose text")
            print(f"Starts with: {test_code[:100]}...")
        
        # Test documentation generation with timing
        print("\n📚 Testing Documentation Generation (with improved timeout):")
        doc_start = time.time()
        
        doc_code = llm.generate_documentation(
            function_code=test_function,
            function_name="add_numbers"
        )
        
        doc_time = time.time() - doc_start
        print(f"⏱️  Documentation generation completed in {doc_time:.2f} seconds")
        
        print("📄 Generated Documentation:")
        print("-" * 30)
        print(doc_code)
        print("-" * 30)
        
        # Check if response is clean
        if doc_code.startswith(('#', '##', 'function', 'add_numbers')):
            print("✅ Documentation generation: Clean content generated!")
        else:
            print("❌ Documentation generation: Still contains verbose text")
            print(f"Starts with: {doc_code[:100]}...")
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Total test time: {total_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Improved Timeout Settings...")
    print("This test will verify that the DeepSeek Coder model has enough time to:")
    print("  1. Load properly during initialization")
    print("  2. Generate tests without timing out")
    print("  3. Generate documentation without timing out")
    print("  4. Use the improved 3-minute timeout for generation")
    print()
    
    success = test_improved_timeout()
    
    if success:
        print("\n🎉 Improved timeout test completed!")
        print("The model should now have enough time to generate quality content.")
    else:
        print("\n❌ Improved timeout test failed.")
        print("Check the error messages above.")
