import os
import json
import logging
from typing import Dict, List, Any, Optional
from .llm import PhindCodeLlamaLLM
from .generator import TestGenerator
from .documentation import DocumentationGenerator
from .memory import MemoryModule
from .watcher import get_functions_from_diff_file, analyze_diff_changes, load_enhanced_context
from .prompts import PromptStrategy

class AIAgent:
    def __init__(
        self,
        model_name: str = "h2oai/h2ogpt-16k-codellama-13b-python",
        api_token: Optional[str] = None,
        provider: str = "hf-inference",
    ):
        self.model_name = model_name
        self.llm = PhindCodeLlamaLLM(model_name, api_token=api_token, provider=provider)
        self.test_generator = TestGenerator(self.llm)
        self.doc_generator = DocumentationGenerator(self.llm)
        self.memory = MemoryModule()
        self.prompt_strategy = PromptStrategy()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def process_diff_file(
        self,
        diff_file_path: str,
        output_dir: str = "generated",
        prompt_strategy: str = "diff-aware",
        generate_docs: bool = True,
    ) -> Dict[str, Any]:
        self.logger.info(f"Processing diff file: {diff_file_path}")

        os.makedirs(output_dir, exist_ok=True)

        with open(diff_file_path, "r", encoding="utf-8") as f:
            diff_content = f.read()

        analysis = analyze_diff_changes(diff_content)
        self.logger.info(f"Analysis: {analysis}")

        functions = get_functions_from_diff_file(diff_file_path)
        self.logger.info(f"Found {len(functions)} functions in diff")

        results = {
            "analysis": analysis,
            "functions": [],
            "generated_tests": {},
            "generated_docs": {},
            "memory_summary": self.memory.get_memory_summary(),
        }

        for function_name, function_code, file_path, language in functions:
            self.logger.info(f"Processing {language} function: {function_name}")

            self.memory.store_function_context(
                function_name=function_name,
                file_path=file_path,
                diff_context=diff_content[:1000],
            )

            try:
                test_code = self.test_generator.generate_tests_for_function(
                    function_code=function_code,
                    function_name=function_name,
                    diff_context=diff_content,
                    prompt_strategy=prompt_strategy,
                    language=language,
                )

                # treat empty/error placeholders as failures (don't mark success)
                if not test_code or not test_code.strip() or test_code.strip().startswith("# Error"):
                    raise RuntimeError("Empty/errored test generation")

                self.memory.store_test_pattern(
                    function_name=function_name,
                    function_signature=function_code.split("\n")[0],
                    test_code=test_code,
                )

                results["generated_tests"][function_name] = test_code

                # Get the correct file extension for the language
                from .language_detector import LanguageDetector
                file_extension = LanguageDetector.get_file_extension_for_language(language)
                test_file_path = os.path.join(output_dir, f"test_{function_name}{file_extension}")
                with open(test_file_path, "w", encoding='utf-8') as f:
                    f.write(test_code)

                if generate_docs:
                    try:
                        doc_content = self.doc_generator.generate_documentation(
                            function_code=function_code,
                            function_name=function_name,
                            diff_context=diff_content,
                        )
                        results["generated_docs"][function_name] = doc_content

                        doc_file_path = os.path.join(output_dir, f"doc_{function_name}.md")
                        with open(doc_file_path, "w") as f:
                            f.write(doc_content)

                    except Exception as doc_error:
                        self.logger.error(
                            f"Error generating documentation for {function_name}: {doc_error}"
                        )
                        doc_content = f"# Error generating documentation: {str(doc_error)}"
                        results["generated_docs"][function_name] = doc_content

                results["functions"].append(
                    {
                        "name": function_name,
                        "file_path": file_path,
                        "test_generated": True,
                        "doc_generated": generate_docs,
                    }
                )

                self.logger.info(f"Successfully processed function: {function_name}")

            except Exception as e:
                self.logger.error(f"Error processing function {function_name}: {e}")
                results["functions"].append(
                    {
                        "name": function_name,
                        "file_path": file_path,
                        "test_generated": False,
                        "doc_generated": False,
                        "error": str(e),
                    }
                )

                # fallback: write a minimal placeholder test so the pipeline still produces a file
                try:
                    from .language_detector import LanguageDetector
                    file_extension = LanguageDetector.get_file_extension_for_language(language)
                    test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
                    primary_framework = test_frameworks[0] if test_frameworks else "standard"
                    
                    basic_test = self._generate_fallback_test(function_name, language, primary_framework)
                    results["generated_tests"][function_name] = basic_test
                    test_file_path = os.path.join(output_dir, f"test_{function_name}{file_extension}")
                    with open(test_file_path, "w", encoding='utf-8') as f:
                        f.write(basic_test)
                    self.logger.info(f"Generated basic {language} test for {function_name}")
                except Exception as basic_test_error:
                    self.logger.error(
                        f"Failed to generate basic {language} test for {function_name}: {basic_test_error}"
                    )

        return results

    def process_enhanced_pr_data(
        self,
        pr_data_dir: str,
        output_dir: str = "generated",
        prompt_strategy: str = "diff-aware",
        generate_docs: bool = True,
    ) -> Dict[str, Any]:
        """Process PR data from enhanced extraction with rich context."""
        self.logger.info(f"Processing enhanced PR data from: {pr_data_dir}")

        os.makedirs(output_dir, exist_ok=True)

        # Load enhanced context
        enhanced_context = load_enhanced_context(pr_data_dir)
        if not enhanced_context:
            self.logger.error(f"Could not load enhanced context from {pr_data_dir}")
            return {"error": "Failed to load enhanced context"}

        self.logger.info(f"Loaded enhanced context with {len(enhanced_context['enhanced_patches'])} files")

        results = {
            "enhanced_context": enhanced_context,
            "functions": [],
            "generated_tests": {},
            "generated_docs": {},
            "memory_summary": self.memory.get_memory_summary(),
        }

        # Process each file with enhanced context
        for filename, patch_data in enhanced_context['enhanced_patches'].items():
            if not patch_data.get('patch') or patch_data['status'] == 'removed':
                continue

            language = patch_data.get('language', '')
            if not language:
                continue

            self.logger.info(f"Processing {language} file: {filename}")

            # Extract functions from the patch
            functions = self._extract_functions_from_patch(patch_data['patch'], filename, language)
            
            for function_name, function_code in functions.items():
                self.logger.info(f"Processing function: {function_name}")

                # Store enhanced context in memory
                self.memory.store_function_context(
                    function_name=function_name,
                    file_path=filename,
                    diff_context=patch_data['patch'],
                    enhanced_context={
                        'imports': patch_data.get('imports', []),
                        'full_content': patch_data.get('full_content', ''),
                        'pr_title': enhanced_context.get('pr_metadata', {}).get('title', ''),
                        'test_patterns': enhanced_context.get('test_patterns', {}),
                    }
                )

                try:
                    # Generate tests with enhanced context
                    test_code = self.test_generator.generate_tests_for_function_enhanced(
                        function_code=function_code,
                        function_name=function_name,
                        enhanced_context=patch_data,
                        pr_context=enhanced_context,
                        prompt_strategy=prompt_strategy,
                        language=language,
                    )

                    if not test_code or not test_code.strip() or test_code.strip().startswith("# Error"):
                        raise RuntimeError("Empty/errored test generation")

                    self.memory.store_test_pattern(
                        function_name=function_name,
                        function_signature=function_code.split("\n")[0] if function_code else "",
                        test_code=test_code,
                    )

                    results["generated_tests"][f"{filename}:{function_name}"] = test_code

                    # Save test file
                    from .language_detector import LanguageDetector
                    file_extension = LanguageDetector.get_file_extension_for_language(language)
                    safe_filename = filename.replace('/', '_').replace('\\', '_')
                    test_file_path = os.path.join(output_dir, f"test_{safe_filename}_{function_name}{file_extension}")
                    with open(test_file_path, "w", encoding='utf-8') as f:
                        f.write(test_code)

                    if generate_docs:
                        try:
                            doc_content = self.doc_generator.generate_documentation_enhanced(
                                function_code=function_code,
                                function_name=function_name,
                                enhanced_context=patch_data,
                                pr_context=enhanced_context,
                            )
                            results["generated_docs"][f"{filename}:{function_name}"] = doc_content

                            doc_file_path = os.path.join(output_dir, f"doc_{safe_filename}_{function_name}.md")
                            with open(doc_file_path, "w") as f:
                                f.write(doc_content)

                        except Exception as doc_error:
                            self.logger.error(f"Error generating documentation for {function_name}: {doc_error}")
                            results["generated_docs"][f"{filename}:{function_name}"] = f"# Error: {str(doc_error)}"

                    results["functions"].append({
                        "name": function_name,
                        "file_path": filename,
                        "test_generated": True,
                        "doc_generated": generate_docs,
                        "language": language,
                    })

                    self.logger.info(f"Successfully processed function: {function_name}")

                except Exception as e:
                    self.logger.error(f"Error processing function {function_name}: {e}")
                    results["functions"].append({
                        "name": function_name,
                        "file_path": filename,
                        "test_generated": False,
                        "doc_generated": False,
                        "error": str(e),
                        "language": language,
                    })

                    # Generate fallback test
                    try:
                        from .language_detector import LanguageDetector
                        file_extension = LanguageDetector.get_file_extension_for_language(language)
                        test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
                        primary_framework = test_frameworks[0] if test_frameworks else "standard"
                        
                        basic_test = self._generate_fallback_test(function_name, language, primary_framework)
                        results["generated_tests"][f"{filename}:{function_name}"] = basic_test
                        
                        safe_filename = filename.replace('/', '_').replace('\\', '_')
                        test_file_path = os.path.join(output_dir, f"test_{safe_filename}_{function_name}{file_extension}")
                        with open(test_file_path, "w", encoding='utf-8') as f:
                            f.write(basic_test)
                        
                        self.logger.info(f"Generated fallback test for {function_name}")
                    except Exception as fallback_error:
                        self.logger.error(f"Failed to generate fallback test for {function_name}: {fallback_error}")

        return results

    def _extract_functions_from_patch(self, patch_content: str, filename: str, language: str) -> Dict[str, str]:
        """Extract function definitions from patch content."""
        from .language_detector import LanguageDetector
        
        functions = {}
        function_patterns = LanguageDetector.get_function_patterns_for_language(language)
        
        lines = patch_content.split('\n')
        current_function = None
        current_function_lines = []
        
        for line in lines:
            if line.startswith('+'):  # Only process added lines
                line_content = line[1:]  # Remove the '+' prefix
                
                # Check if this line starts a new function
                for pattern in function_patterns:
                    import re
                    match = re.match(pattern, line_content.strip())
                    if match:
                        # Save previous function if exists
                        if current_function and current_function_lines:
                            functions[current_function] = '\n'.join(current_function_lines)
                        
                        # Start new function
                        current_function = match.group(1)
                        current_function_lines = [line_content]
                        break
                else:
                    # This line is part of the current function
                    if current_function:
                        current_function_lines.append(line_content)
        
        # Save the last function
        if current_function and current_function_lines:
            functions[current_function] = '\n'.join(current_function_lines)
        
        return functions

    def compare_prompt_strategies(
        self, diff_file_path: str, output_dir: str = "prompt_comparison"
    ) -> Dict[str, Any]:
        strategies = ["naive", "diff-aware", "few-shot", "cot", "tdd"]
        results: Dict[str, Any] = {}

        for strategy in strategies:
            strategy_dir = os.path.join(output_dir, strategy)
            os.makedirs(strategy_dir, exist_ok=True)

            try:
                strategy_results = self.process_diff_file(
                    diff_file_path=diff_file_path,
                    output_dir=strategy_dir,
                    prompt_strategy=strategy,
                    generate_docs=True,
                )
                results[strategy] = strategy_results

            except Exception as e:
                self.logger.error(f"Error with strategy {strategy}: {e}")
                results[strategy] = {"error": str(e)}

        return results

    def compare_prompt_strategies_enhanced(
        self, pr_data_dir: str, output_dir: str = "prompt_comparison_enhanced"
    ) -> Dict[str, Any]:
        """Compare prompt strategies using enhanced PR data."""
        strategies = ["naive", "diff-aware", "few-shot", "cot", "tdd"]
        results: Dict[str, Any] = {}

        for strategy in strategies:
            strategy_dir = os.path.join(output_dir, strategy)
            os.makedirs(strategy_dir, exist_ok=True)

            try:
                strategy_results = self.process_enhanced_pr_data(
                    pr_data_dir=pr_data_dir,
                    output_dir=strategy_dir,
                    prompt_strategy=strategy,
                    generate_docs=True,
                )
                results[strategy] = strategy_results

            except Exception as e:
                self.logger.error(f"Error with strategy {strategy}: {e}")
                results[strategy] = {"error": str(e)}

        return results

    def suggest_improvements(self, function_name: str, current_test_code: str) -> List[str]:
        suggestions: List[str] = []

        try:
            messages = [
                {"role": "system", "content": "You are a senior test engineer."},
                {
                    "role": "user",
                    "content": f"""Analyze this test code and suggest improvements:

Function: {function_name}
Test Code:
{current_test_code}

Provide specific, actionable suggestions for improving test coverage, readability, and robustness.""",
                },
            ]

            response = self.llm.generate(messages)
            suggestions = [s.strip() for s in response.split("\n") if s.strip()]

        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            suggestions = ["Unable to generate suggestions due to an error"]

        return suggestions

    def get_memory_insights(self) -> Dict[str, Any]:
        return self.memory.get_insights()

    def _generate_fallback_test(self, function_name: str, language: str, framework: str) -> str:
        """Generate a basic fallback test based on the language and framework."""
        if language == "python":
            return f"""# Basic test for {function_name}
import pytest

def test_{function_name}_basic():
    pass
"""
        elif language in ["javascript", "typescript"]:
            if framework == "jest":
                return f"""// Basic test for {function_name}
describe('{function_name}', () => {{
    test('should work', () => {{
        expect(true).toBe(true);
    }});
}});
"""
            else:
                return f"""// Basic test for {function_name}
// TODO: Implement proper tests using {framework}
"""
        elif language == "java":
            return f"""// Basic test for {function_name}
import org.junit.Test;
import static org.junit.Assert.*;

public class {function_name}Test {{
    @Test
    public void testBasic() {{
        assertTrue(true);
    }}
}}
"""
        elif language == "cpp":
            return f"""// Basic test for {function_name}
#include <gtest/gtest.h>

TEST({function_name}Test, Basic) {{
    EXPECT_TRUE(true);
}}
"""
        elif language == "c":
            return f"""// Basic test for {function_name}
#include <unity.h>

void test_{function_name}_basic(void) {{
    TEST_ASSERT_TRUE(1);
}}
"""
        elif language == "go":
            return f"""// Basic test for {function_name}
package main

import "testing"

func Test{function_name}Basic(t *testing.T) {{
    if true != true {{
        t.Error("Basic test failed")
    }}
}}
"""
        elif language == "rust":
            return f"""// Basic test for {function_name}
#[cfg(test)]
mod tests {{
    #[test]
    fn test_{function_name}_basic() {{
        assert!(true);
    }}
}}
"""
        else:
            return f"""# Basic test for {function_name} ({language})
# TODO: Implement proper tests using {framework}
"""

    def clear_memory(self):
        self.memory.clear()
        self.logger.info("Memory cleared")