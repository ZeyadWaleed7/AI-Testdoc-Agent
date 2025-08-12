#!/usr/bin/env python3
"""
Example script demonstrating the Phind-CodeLlama-34B-v2 model usage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.llm import PhindCodeLlamaLLM

def main():
    """Demonstrate the new Phind model capabilities."""
    
    print("🚀 Phind-CodeLlama-34B-v2 Model Example")
    print("=" * 50)
    
    try:
        # Initialize the model
        print("Initializing Phind-CodeLlama-34B-v2 model...")
        llm = PhindCodeLlamaLLM()
        print("✅ Model initialized successfully!")
        
        # Example function to test
        function_code = """
def calculate_fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
        
        print("\n📝 Generating unit tests...")
        tests = llm.generate_test(function_code)
        print("Generated tests:")
        print(tests)
        
        print("\n📚 Generating documentation...")
        docs = llm.generate_documentation(function_code, "calculate_fibonacci")
        print("Generated documentation:")
        print(docs)
        
        print("\n🎯 Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 