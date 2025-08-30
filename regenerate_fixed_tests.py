#!/usr/bin/env python3
"""Script to regenerate tests using the fixed agent with comprehensive context"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.agent import AIAgent
from ai_agent.llm import PhindCodeLlamaLLM

def regenerate_tests():
    """Regenerate test files with the fixed agent"""
    
    print("🔄 Regenerating tests with fixed agent (comprehensive context)")
    print("=" * 70)
    
    # Path to the problematic PR data
    pr_data_path = "data/fastapi_fastapi/PR_13827"
    
    if not os.path.exists(pr_data_path):
        print(f"❌ PR data path not found: {pr_data_path}")
        return
    
    # Initialize the LLM and agent with Ollama deepseek-coder
    try:
        llm = PhindCodeLlamaLLM(model_name="deepseek-coder", provider="ollama")
        agent = AIAgent(llm=llm)
        
        print("✅ Agent initialized successfully with Ollama deepseek-coder")
        
        # Define the strategies to use (NO enhanced-context)
        strategies = ["naive", "diff-aware", "few-shot", "cot"]
        
        for strategy in strategies:
            print(f"\n📝 Processing with {strategy} strategy...")
            print("-" * 50)
            
            try:
                # Process using the enhanced context method
                agent._process_enhanced_context(pr_data_path, strategy)
                print(f"✅ {strategy} strategy completed successfully")
                
            except Exception as e:
                print(f"❌ Error with {strategy} strategy: {e}")
                continue
        
        print("\n🎯 Test regeneration completed!")
        print("\n📁 Generated test files:")
        
        # List the generated test files
        for strategy in strategies:
            test_dir = f"{pr_data_path}/deepseek_coder/{strategy}"
            if os.path.exists(test_dir):
                test_files = [f for f in os.listdir(test_dir) if f.endswith('.py')]
                print(f"   {strategy}: {len(test_files)} test files")
                
                # Show content of first test file to verify quality
                if test_files:
                    first_test = os.path.join(test_dir, test_files[0])
                    with open(first_test, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'basic py test' in content.lower() or 'needs implementation' in content.lower():
                            print(f"      ⚠️  {test_files[0]} still has placeholder content")
                        else:
                            print(f"      ✅ {test_files[0]} looks good")
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    regenerate_tests()
