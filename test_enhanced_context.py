#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced context functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.enhanced_context import EnhancedContextLoader

def test_enhanced_context_loading():
    """Test loading enhanced context from a PR directory"""
    
    # Find a PR directory with enhanced context
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Data directory not found. Run extract_prs.py first.")
        return False
    
    # Look for a PR with enhanced context
    pr_dirs = []
    for repo_dir in data_dir.iterdir():
        if repo_dir.is_dir():
            for pr_dir in repo_dir.iterdir():
                if pr_dir.is_dir() and pr_dir.name.startswith("PR_"):
                    enhanced_patches = pr_dir / "enhanced_patches.json"
                    if enhanced_patches.exists():
                        pr_dirs.append(pr_dir)
    
    if not pr_dirs:
        print("❌ No PR directories with enhanced context found.")
        print("💡 Run extract_prs.py first to extract PR data.")
        return False
    
    # Test with the first available PR
    test_pr_dir = pr_dirs[0]
    print(f"🧪 Testing enhanced context with: {test_pr_dir}")
    
    try:
        # Load enhanced context
        enhanced_context = EnhancedContextLoader(str(test_pr_dir))
        
        # Test various methods
        print(f"✅ Enhanced context loaded successfully!")
        print(f"   📝 PR Title: {enhanced_context.get_pr_title()}")
        print(f"   🌐 Languages: {', '.join(enhanced_context.get_languages_in_pr())}")
        print(f"   📁 Changed files: {len(enhanced_context.get_changed_files())}")
        print(f"   🧪 Test files: {len(enhanced_context.get_test_files())}")
        print(f"   📚 Source files: {len(enhanced_context.get_source_files())}")
        
        # Test file context
        if enhanced_context.get_source_files():
            source_file = enhanced_context.get_source_files()[0]
            print(f"\n📄 Testing file context for: {source_file}")
            
            file_context = enhanced_context.get_file_context(source_file)
            if file_context:
                print(f"   ✅ File context loaded")
                print(f"   📊 Status: {file_context.get('status', 'N/A')}")
                print(f"   🔢 Changes: {file_context.get('changes', 0)}")
                print(f"   🌐 Language: {file_context.get('language', 'N/A')}")
                print(f"   📦 Imports: {len(file_context.get('imports', []))}")
                print(f"   📝 Has full content: {bool(file_context.get('full_content'))}")
            else:
                print(f"   ❌ No file context found")
        
        # Test test patterns
        languages = enhanced_context.get_languages_in_pr()
        if languages:
            language = languages[0]
            print(f"\n🧪 Testing test patterns for language: {language}")
            
            test_patterns = enhanced_context.get_test_patterns_for_language(language)
            print(f"   📊 Found {len(test_patterns)} test patterns")
            
            for i, pattern in enumerate(test_patterns[:2], 1):
                print(f"   Pattern {i}: {pattern['filename']}")
                print(f"      Content preview: {pattern['content'][:100]}...")
        
        print(f"\n🎉 Enhanced context test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced context: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_summary():
    """Test loading context summary"""
    data_dir = Path("data")
    
    # Find a context summary file
    context_files = list(data_dir.rglob("context/context_summary.json"))
    
    if not context_files:
        print("❌ No context summary files found.")
        return False
    
    context_file = context_files[0]
    print(f"🧪 Testing context summary: {context_file}")
    
    try:
        with open(context_file, 'r') as f:
            summary = json.load(f)
        
        print(f"✅ Context summary loaded successfully!")
        print(f"   📝 PR Title: {summary.get('title', 'N/A')}")
        print(f"   🌐 Languages: {', '.join(summary.get('languages', []))}")
        print(f"   📁 Total files changed: {summary.get('total_files_changed', 0)}")
        print(f"   🧪 Test files saved: {summary.get('test_files_saved', 0)}")
        
        # Show main changes
        main_changes = summary.get('main_changes', [])
        if main_changes:
            print(f"   📊 Main changes:")
            for change in main_changes[:3]:  # Show first 3
                print(f"      - {change['file']} ({change['status']}, {change['changes']} changes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing context summary: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Enhanced Context Functionality")
    print("=" * 50)
    
    # Test 1: Enhanced context loading
    print("\n1️⃣ Testing Enhanced Context Loading...")
    success1 = test_enhanced_context_loading()
    
    # Test 2: Context summary
    print("\n2️⃣ Testing Context Summary...")
    success2 = test_context_summary()
    
    # Summary
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Enhanced context is working correctly.")
        print("💡 You can now use the agent with enhanced context for better test generation.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print("💡 Make sure you have run extract_prs.py to generate the required data files.")

if __name__ == "__main__":
    main()
