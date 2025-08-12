#!/usr/bin/env python3
"""
Test script to verify the Phind-CodeLlama-34B-v2 model can be accessed remotely
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.llm import PhindCodeLlamaLLM

def test_model_loading():
    """Test if the remote model can be accessed successfully."""
    
    print("🧪 Testing Phind-CodeLlama-34B-v2 remote inference...")
    print("=" * 60)
    
    try:
        # Initialize the model (this will test the API connection)
        print("1. Testing remote model connection...")
        llm = PhindCodeLlamaLLM()
        print("✅ Remote model connection successful!")
        
        # Test basic generation
        print("\n2. Testing basic generation...")
        test_prompt = "Write a simple Python function to add two numbers:"
        
        messages = [
            {"role": "system", "content": "You are a helpful Python programming assistant."},
            {"role": "user", "content": test_prompt}
        ]
        
        response = llm.generate(messages, max_new_tokens=100)
        print(f"✅ Generation successful! Response: {response[:200]}...")
        
        print("\n🎯 All tests passed! The remote model is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1) 