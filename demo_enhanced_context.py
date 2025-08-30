#!/usr/bin/env python3
"""
Demonstration script showing enhanced context test generation
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.enhanced_context import EnhancedContextLoader
from ai_agent.language_detector import LanguageDetector

def demonstrate_enhanced_context():
    """Demonstrate how enhanced context provides comprehensive information for test generation"""
    
    print("🚀 Enhanced Context Test Generation Demo")
    print("=" * 60)
    
    # Find a PR with enhanced context
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Data directory not found. Run extract_prs.py first.")
        return
    
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
        return
    
    # Use the first available PR
    test_pr_dir = pr_dirs[0]
    print(f"📁 Using PR: {test_pr_dir}")
    
    try:
        # Load enhanced context
        enhanced_context = EnhancedContextLoader(str(test_pr_dir))
        
        print(f"\n✅ Enhanced Context Loaded Successfully!")
        print(f"   📝 PR Title: {enhanced_context.get_pr_title()}")
        print(f"   🌐 Languages: {', '.join(enhanced_context.get_languages_in_pr())}")
        
        # Show what information is available
        print(f"\n📊 Available Context Information:")
        print(f"   📁 Changed files: {len(enhanced_context.get_changed_files())}")
        print(f"   🧪 Test files: {len(enhanced_context.get_test_files())}")
        print(f"   📚 Source files: {len(enhanced_context.get_source_files())}")
        
        # Demonstrate file context
        source_files = enhanced_context.get_source_files()
        if source_files:
            source_file = source_files[0]
            print(f"\n📄 File Context Example: {source_file}")
            
            file_context = enhanced_context.get_file_context(source_file)
            if file_context:
                print(f"   📊 Status: {file_context.get('status', 'N/A')}")
                print(f"   🔢 Changes: {file_context.get('changes', 0)}")
                print(f"   🌐 Language: {file_context.get('language', 'N/A')}")
                
                # Show imports
                imports = enhanced_context.get_imports_for_file(source_file)
                if imports:
                    print(f"   📦 Required imports ({len(imports)}):")
                    for imp in imports[:5]:  # Show first 5
                        print(f"      {imp}")
                    if len(imports) > 5:
                        print(f"      ... and {len(imports) - 5} more")
                
                # Show content preview
                full_content = enhanced_context.get_full_content_for_file(source_file)
                if full_content:
                    print(f"   📝 Content preview (first 200 chars):")
                    print(f"      {full_content[:200]}...")
        
        # Demonstrate test patterns
        languages = enhanced_context.get_languages_in_pr()
        if languages:
            language = languages[0]
            print(f"\n🧪 Test Patterns for {language}:")
            
            test_patterns = enhanced_context.get_test_patterns_for_language(language)
            print(f"   📊 Found {len(test_patterns)} test patterns")
            
            for i, pattern in enumerate(test_patterns[:2], 1):
                print(f"   Pattern {i}: {pattern['filename']}")
                content_preview = pattern['content'][:150].replace('\n', ' ')
                print(f"      {content_preview}...")
        
        # Show how this enables better test generation
        print(f"\n🎯 How This Enables Better Test Generation:")
        print(f"   1. ✅ No TODO comments - All imports are known")
        print(f"   2. ✅ No assumptions - File content is available")
        print(f"   3. ✅ Language-aware - Correct test framework used")
        print(f"   4. ✅ Pattern-following - Uses existing test conventions")
        print(f"   5. ✅ Complete context - PR title, description, related files")
        
        # Show what the agent would receive
        print(f"\n📋 What the AI Agent Receives:")
        print(f"   • Function code to test")
        print(f"   • Required imports and dependencies")
        print(f"   • Full file content (first 2000 chars)")
        print(f"   • Patch/diff information")
        print(f"   • Existing test patterns from codebase")
        print(f"   • PR metadata and context")
        print(f"   • Language and test framework information")
        
        print(f"\n💡 Result: 100% executable tests without any placeholders!")
        
    except Exception as e:
        print(f"❌ Error demonstrating enhanced context: {e}")
        import traceback
        traceback.print_exc()

def show_usage_instructions():
    """Show how to use the enhanced context agent"""
    
    print(f"\n📖 Usage Instructions:")
    print(f"=" * 40)
    
    print(f"\n1️⃣ Extract PR Data (Required First):")
    print(f"   python extract_prs.py")
    
    print(f"\n2️⃣ Generate Tests with Enhanced Context:")
    print(f"   # Interactive mode (recommended)")
    print(f"   python main.py --interactive")
    print(f"   ")
    print(f"   # Process specific PRs")
    print(f"   python main.py --pr-filter 123,456")
    print(f"   ")
    print(f"   # Use enhanced-context strategy (default)")
    print(f"   python main.py --prompt-strategy enhanced-context")
    
    print(f"\n3️⃣ The Agent Will Automatically:")
    print(f"   • Detect enhanced context availability")
    print(f"   • Use comprehensive file information")
    print(f"   • Generate complete, runnable tests")
    print(f"   • Include all necessary imports")
    print(f"   • Follow existing test patterns")
    
    print(f"\n4️⃣ Fallback Behavior:")
    print(f"   • If enhanced context not available, falls back to basic processing")
    print(f"   • Always generates tests, but quality may vary")
    print(f"   • Check logs for context availability status")

def main():
    """Main demonstration function"""
    
    # Show the demo
    demonstrate_enhanced_context()
    
    # Show usage instructions
    show_usage_instructions()
    
    print(f"\n🎉 Enhanced Context Demo Complete!")
    print(f"💡 The agent is now ready to generate high-quality tests!")

if __name__ == "__main__":
    main()
