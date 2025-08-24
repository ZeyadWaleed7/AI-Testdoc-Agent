#!/usr/bin/env python3
"""
Test script to process Facebook React PR with DeepSeek Coder model.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.agent import AIAgent
from ai_agent.language_detector import LanguageDetector

def test_facebook_react_pr():
    """Test processing Facebook React PR with DeepSeek Coder."""
    
    print("📱 Testing Facebook React PR with DeepSeek Coder")
    print("=" * 60)
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama is not responding correctly")
            return False
        print("✅ Ollama is running and accessible")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please start Ollama with: ollama serve")
        return False
    
    # Check if deepseek-coder model is available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        model_names = [model.get("name", "") for model in models]
        
        if "deepseek-coder" not in model_names:
            print("❌ deepseek-coder model not found in Ollama")
            print("Available models:", model_names)
            print("Please install with: ollama pull deepseek-coder")
            return False
        
        print("✅ deepseek-coder model is available")
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False
    
    # Initialize the AI Agent with DeepSeek Coder
    print("\n🤖 Initializing AI Agent with DeepSeek Coder...")
    try:
        agent = AIAgent(
            model_name="deepseek-coder",
            provider="ollama"
        )
        print("✅ AI Agent initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize AI Agent: {e}")
        return False
    
    # Check available PRs
    print("\n📋 Checking available PRs...")
    try:
        from main import list_available_prs
        available_prs = list_available_prs()
        
        facebook_prs = [pr for pr in available_prs if "facebook_react" in pr['repo']]
        
        if not facebook_prs:
            print("❌ No Facebook React PRs found")
            print("Available repos:", list(set(pr['repo'] for pr in available_prs)))
            return False
        
        print(f"✅ Found {len(facebook_prs)} Facebook React PR(s):")
        for pr in facebook_prs:
            print(f"  - {pr['full_name']} at {pr['path']}")
        
        # Select the first Facebook React PR
        selected_pr = facebook_prs[0]
        print(f"\n🎯 Selected PR: {selected_pr['full_name']}")
        
    except Exception as e:
        print(f"❌ Error checking PRs: {e}")
        return False
    
    # Process the PR
    print(f"\n🚀 Processing PR: {selected_pr['full_name']}")
    try:
        results = agent.process_diff_file(
            diff_file_path=str(selected_pr['diff_file']),
            output_dir=f"test_output/deepseek_coder/{selected_pr['full_name']}",
            prompt_strategy="diff-aware",
            generate_docs=True
        )
        
        print("✅ PR processing completed successfully!")
        print(f"  Functions found: {len(results.get('functions', []))}")
        print(f"  Tests generated: {len(results.get('generated_tests', {}))}")
        print(f"  Docs generated: {len(results.get('generated_docs', {}))}")
        
        # Show some details
        for func_info in results.get('functions', []):
            name = func_info.get('name', 'Unknown')
            test_gen = func_info.get('test_generated', False)
            doc_gen = func_info.get('doc_generated', False)
            status = "✅" if test_gen else "❌"
            print(f"  {status} {name}: Test={test_gen}, Doc={doc_gen}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing PR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Facebook React PR Test...")
    
    success = test_facebook_react_pr()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📁 Check the test_output directory for generated files")
    else:
        print("\n❌ Test failed. Check the error messages above.")
        sys.exit(1)
