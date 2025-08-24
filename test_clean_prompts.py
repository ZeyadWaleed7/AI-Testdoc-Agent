#!/usr/bin/env python3
"""
Test script to verify clean prompt generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.llm import PhindCodeLlamaLLM

def test_clean_prompts():
    """Test that prompts generate clean code without verbose explanations."""
    
    print("🧪 Testing Clean Prompt Generation")
    print("=" * 50)
    
    # Test with a simple Python function
    test_function = """def is_union_of_base_models(fields):
    \"\"\"Check if all fields in Union are instances or subclasses of BaseModel.\"\"\"
    from typing import Union, get_origin, get_args
    from pydantic import BaseModel
    
    for field in fields.values():
        if get_origin(field.annotation) == Union:
            args = get_args(field.annotation)
            for arg in args:
                if not (isinstance(arg, type) and issubclass(arg, BaseModel)):
                    return False
        elif not (isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel)):
            return False
    return True"""
    
    print("📝 Test Function:")
    print(test_function)
    print("\n" + "=" * 50)
    
    try:
        # Test with Ollama provider
        llm = PhindCodeLlamaLLM(
            model_name="deepseek-coder",
            provider="ollama"
        )
        
        print("✅ LLM initialized successfully")
        
        # Test test generation
        print("\n🧪 Testing Test Generation:")
        test_code = llm.generate_test(
            function_code=test_function,
            diff_context="Added new function to validate Union fields",
            prompt_strategy="diff-aware",
            language="python"
        )
        
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
        
        # Test documentation generation
        print("\n📚 Testing Documentation Generation:")
        doc_code = llm.generate_documentation(
            function_code=test_function,
            function_name="is_union_of_base_models"
        )
        
        print("📄 Generated Documentation:")
        print("-" * 30)
        print(doc_code)
        print("-" * 30)
        
        # Check if response is clean
        if doc_code.startswith(('#', '##', 'function', 'is_union_of_base_models')):
            print("✅ Documentation generation: Clean content generated!")
        else:
            print("❌ Documentation generation: Still contains verbose text")
            print(f"Starts with: {doc_code[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Clean Prompt Generation...")
    
    success = test_clean_prompts()
    
    if success:
        print("\n🎉 Clean prompt test completed!")
        print("The improved prompts should now generate clean code without verbose explanations.")
    else:
        print("\n❌ Clean prompt test failed.")
        print("Check the error messages above.")
