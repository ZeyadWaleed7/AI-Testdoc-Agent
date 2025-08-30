#!/usr/bin/env python3
"""Script to regenerate problematic test files with improved prompts and context"""

import os
import sys
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.agent import AIAgent
from ai_agent.enhanced_context import EnhancedContextLoader

def regenerate_tests():
    """Regenerate test files with improved prompts and context"""
    
    print("🔄 Regenerating test files with improved prompts and context")
    print("=" * 70)
    
    # Path to the problematic PR data
    pr_data_path = "data/fastapi_fastapi/PR_13827"
    
    if not os.path.exists(pr_data_path):
        print(f"❌ PR data path not found: {pr_data_path}")
        return
    
    print(f"📁 Processing PR data from: {pr_data_path}")
    
    # Load enhanced context
    try:
        enhanced_context = EnhancedContextLoader(pr_data_path)
        print(f"✅ Loaded enhanced context with {len(enhanced_context.enhanced_patches)} files")
    except Exception as e:
        print(f"❌ Error loading enhanced context: {e}")
        return
    
    # Create output directory for regenerated tests
    output_dir = "regenerated_tests"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize AI agent
    try:
        agent = AIAgent()
        print("✅ AI Agent initialized")
    except Exception as e:
        print(f"❌ Error initializing AI Agent: {e}")
        return
    
    # Process each file with enhanced context
    processed_files = 0
    successful_files = 0
    
    for filename, patch_data in enhanced_context.enhanced_patches.items():
        if not patch_data.get('patch') or patch_data['status'] == 'removed':
            continue
        
        language = patch_data.get('language', '')
        
        # Fallback language detection
        if not language or language == 'unknown' or len(language) <= 3:
            from ai_agent.language_detector import LanguageDetector
            language = LanguageDetector.get_language_from_extension(filename)
            print(f"🔍 Fallback language detection for {filename}: {language}")
        
        if not language or language == 'unknown':
            print(f"⚠️ Could not determine language for {filename}")
            continue
        
        print(f"\n📄 Processing {language} file: {filename}")
        processed_files += 1
        
        try:
            # Extract functions from the patch
            functions = agent._extract_functions_from_patch(patch_data['patch'], filename, language)
            
            if not functions:
                print(f"⚠️ No functions extracted from {filename}")
                continue
            
            print(f"🔍 Found {len(functions)} functions to test")
            
            for function_name, function_code in functions.items():
                print(f"🧪 Generating test for function: {function_name}")
                
                try:
                    # Generate test using enhanced context
                    test_code = agent.test_generator.generate_tests_with_enhanced_context(
                        function_code=function_code,
                        function_name=function_name,
                        file_path=filename,
                        language=language,
                        enhanced_context=enhanced_context,
                        output_dir=output_dir
                    )
                    
                    if not test_code or not test_code.strip():
                        raise RuntimeError("Empty test generation")
                    
                    # Save test file with proper extension
                    from ai_agent.language_detector import LanguageDetector
                    file_extension = LanguageDetector.get_file_extension_for_language(language, filename)
                    safe_filename = filename.replace('/', '_').replace('\\', '_')
                    test_file_path = os.path.join(output_dir, f"test_{safe_filename}_{function_name}{file_extension}")
                    
                    with open(test_file_path, "w", encoding='utf-8') as f:
                        f.write(test_code)
                    
                    print(f"✅ Generated test: {test_file_path}")
                    successful_files += 1
                    
                except Exception as e:
                    print(f"❌ Error generating test for {function_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error processing file {filename}: {e}")
            continue
    
    print("\n" + "=" * 70)
    print(f"📊 Summary:")
    print(f"   - Files processed: {processed_files}")
    print(f"   - Tests generated successfully: {successful_files}")
    print(f"   - Output directory: {output_dir}")
    
    if successful_files > 0:
        print(f"\n🎉 Successfully regenerated {successful_files} test files!")
        print(f"📁 Check the '{output_dir}' directory for the new test files.")
    else:
        print("\n💥 No tests were generated successfully.")

if __name__ == "__main__":
    regenerate_tests()
