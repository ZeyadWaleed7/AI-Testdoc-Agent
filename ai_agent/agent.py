import os
import json
import logging
import re
import ast
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from .llm import PhindCodeLlamaLLM
from .generator import TestGenerator
from .documentation import DocumentationGenerator
from .memory import MemoryModule
from .watcher import get_functions_from_diff_file, analyze_diff_changes
from .prompts import PromptStrategy
from .enhanced_context import EnhancedContextLoader

class AIAgent:
    def __init__(
        self,
        llm=None,
        model_name: str = "h2oai/h2ogpt-16k-codellama-13b-python",
        api_token: Optional[str] = None,
        provider: str = "hf-inference",
    ):
        # If LLM is provided directly, use it; otherwise create default
        if llm is not None:
            self.llm = llm
        else:
            self.llm = PhindCodeLlamaLLM(model_name, api_token=api_token, provider=provider)
        
        self.model_name = getattr(self.llm, 'model_name', model_name)
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
        prompt_strategy: str = "naive",
        generate_docs: bool = True,
    ) -> Dict[str, Any]:
        self.logger.info(f"Processing diff file: {diff_file_path}")

        os.makedirs(output_dir, exist_ok=True)

        pr_data_path = self._find_pr_data_directory(diff_file_path)
        
        if pr_data_path and os.path.exists(pr_data_path):
            self.logger.info(f"Found PR data directory: {pr_data_path}")
            return self._process_with_enhanced_context(
                pr_data_path, output_dir, prompt_strategy, generate_docs
            )
        else:
            self.logger.info("No enhanced context found, falling back to basic processing")
            return self._process_with_basic_context(
                diff_file_path, output_dir, prompt_strategy, generate_docs
            )

    def _find_pr_data_directory(self, diff_file_path: str) -> Optional[str]:
        current_path = os.path.dirname(os.path.abspath(diff_file_path))
        
        while current_path and os.path.exists(current_path):
            enhanced_patches_path = os.path.join(current_path, "enhanced_patches.json")
            if os.path.exists(enhanced_patches_path):
                return current_path
            
            parent_path = os.path.dirname(current_path)
            if parent_path == current_path:
                break
            current_path = parent_path
        
        return None

    def _process_with_enhanced_context(
        self,
        pr_data_path: str,
        output_dir: str,
        prompt_strategy: str,
        generate_docs: bool
    ) -> Dict[str, Any]:
        enhanced_context = EnhancedContextLoader(pr_data_path)
        source_files = enhanced_context.get_source_files()
        
        results = {
            "enhanced_context_used": True,
            "pr_title": enhanced_context.get_pr_title(),
            "languages": enhanced_context.get_languages_in_pr(),
            "source_files_processed": [],
            "generated_tests": {},
            "generated_docs": {},
            "memory_summary": self.memory.get_memory_summary(),
        }

        for file_path in source_files:
            self.logger.info(f"Processing source file: {file_path}")
            
            file_context = enhanced_context.get_file_context(file_path)
            language = file_context.get('language', 'unknown')
            
            if not language or language == 'unknown':
                from .language_detector import LanguageDetector
                language = LanguageDetector.get_language_from_extension(file_path)
                self.logger.info(f"Fallback language detection for {file_path}: {language}")
            
            if not language or language == 'unknown':
                self.logger.warning(f"Could not determine language for {file_path}")
                continue
            
            functions = self._extract_functions_from_file_content(
                file_path, file_context, language
            )
            
            if not functions:
                self.logger.warning(f"No functions extracted from {file_path}, creating basic test")
                functions = self._create_basic_function_from_file(file_path, file_context, language)
            
            for function_name, function_code in functions:
                self.logger.info(f"Processing {language} function: {function_name}")
                
                try:
                    test_code = self.test_generator.generate_tests_with_enhanced_context(
                        function_code=function_code,
                        function_name=function_name,
                        file_path=file_path,
                        language=language,
                        enhanced_context=enhanced_context,
                        output_dir=output_dir,
                        prompt_strategy=prompt_strategy
                    )
                    
                    if not test_code or not test_code.strip():
                        raise RuntimeError("Empty test generation")
                    
                    self.memory.store_test_pattern(
                        function_name=function_name,
                        function_signature=function_code.split("\n")[0],
                        test_code=test_code,
                    )
                    
                    results["generated_tests"][function_name] = test_code
                    
                    # Save test file using the proper method
                    self._save_test_file(file_path, language, test_code, prompt_strategy, enhanced_context)
                    self.logger.info(f"Generated test: {file_path} using {prompt_strategy} strategy")
                    
                    # ALWAYS generate documentation for the test file
                    self.logger.info(f"Starting documentation generation for {file_path} using {prompt_strategy} strategy")
                    
                    try:
                        doc_content = self.doc_generator.generate_documentation(
                            function_code=test_code,
                            function_name=f"test_{Path(file_path).stem}",
                            language=language
                        )
                        
                        if doc_content and doc_content.strip():
                            logging.info(f"Documentation generated successfully, length: {len(doc_content)} characters")
                            self._save_documentation_file(file_path, language, doc_content, prompt_strategy, enhanced_context)
                            logging.info(f"Generated documentation for {file_path} using {prompt_strategy} strategy")
                        else:
                            logging.warning(f"Empty documentation generated for {file_path}, attempting fallback")
                            # Generate fallback documentation
                            doc_content = self._generate_fallback_documentation(file_path, language, test_code)
                            if doc_content:
                                self._save_documentation_file(file_path, language, doc_content, prompt_strategy, enhanced_context)
                                logging.info(f"Generated fallback documentation for {file_path}")
                    except Exception as e:
                        logging.error(f"Error generating documentation for {file_path}: {e}")
                        # Generate fallback documentation
                        try:
                            doc_content = self._generate_fallback_documentation(file_path, language, test_code)
                            if doc_content:
                                self._save_documentation_file(file_path, language, doc_content, prompt_strategy, enhanced_context)
                                logging.info(f"Generated fallback documentation for {file_path} after error")
                        except Exception as fallback_error:
                            logging.error(f"Failed to generate fallback documentation for {file_path}: {fallback_error}")
                    
                    # Get the test file path for results
                    from .language_detector import LanguageDetector
                    file_extension = LanguageDetector.get_file_extension_for_language(language, file_path)
                    test_file_name = f"test_{Path(file_path).stem}{file_extension}"
                    
                    results["source_files_processed"].append({
                        "file": file_path,
                        "function": function_name,
                        "language": language,
                        "test_file": test_file_name
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing function {function_name} with strategy {prompt_strategy}: {e}")
                    # Log additional context for debugging
                    self.logger.error(f"Function: {function_name}, Language: {language}, Strategy: {prompt_strategy}")
                    self.logger.error(f"File: {file_path}")
                    continue
        
        return results

    def _process_with_basic_context(
        self,
        diff_file_path: str,
        output_dir: str,
        prompt_strategy: str,
        generate_docs: bool
    ) -> Dict[str, Any]:
        with open(diff_file_path, "r", encoding="utf-8") as f:
            diff_content = f.read()

        analysis = analyze_diff_changes(diff_content)
        self.logger.info(f"Analysis: {analysis}")

        functions = get_functions_from_diff_file(diff_file_path)
        self.logger.info(f"Found {len(functions)} functions in diff")

        results = {
            "enhanced_context_used": False,
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

                if not test_code or not test_code.strip() or test_code.strip().startswith("# Error"):
                    raise RuntimeError("Empty/errored test generation")

                self.memory.store_test_pattern(
                    function_name=function_name,
                    function_signature=function_code.split("\n")[0],
                    test_code=test_code,
                )

                results["generated_tests"][function_name] = test_code

                from .language_detector import LanguageDetector
                file_extension = LanguageDetector.get_file_extension_for_language(language, file_path)
                test_file_path = os.path.join(output_dir, f"test_{function_name}{file_extension}")
                with open(test_file_path, "w", encoding='utf-8') as f:
                    f.write(test_code)

                # ALWAYS generate documentation for both source function and test file
                try:
                    # Generate documentation for the source function
                    doc_content = self.doc_generator.generate_documentation(
                        function_code=function_code,
                        function_name=function_name,
                        language=language
                    )
                    results["generated_docs"][function_name] = doc_content
                    
                    # ALWAYS generate documentation for the test file
                    test_doc_content = self.doc_generator.generate_documentation(
                        function_code=test_code,
                        function_name=f"test_{function_name}",
                        language=language
                    )
                    
                    if test_doc_content and test_doc_content.strip():
                        # Save test documentation file with proper naming
                        test_doc_file_path = test_file_path.replace(file_extension, "_docs.md")
                        with open(test_doc_file_path, "w", encoding='utf-8') as f:
                            f.write(test_doc_content)
                        self.logger.info(f"Generated test documentation: {test_doc_file_path}")
                        
                        # Add test documentation to results
                        results["generated_docs"][f"test_{function_name}"] = test_doc_content
                    else:
                        self.logger.warning(f"Empty test documentation generated for {function_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error generating documentation for {function_name}: {e}")

                results["functions"].append({
                    "name": function_name,
                    "file": file_path,
                    "language": language,
                    "test_file": test_file_path
                })

            except Exception as e:
                self.logger.error(f"Error processing function {function_name}: {e}")
                continue

        return results

    def _extract_functions_from_file_content(
        self,
        file_path: str,
        file_context: Dict[str, Any],
        language: str
    ) -> List[Tuple[str, str]]:
        from .language_detector import LanguageDetector
        
        full_content = file_context.get("full_content", "")
        patch_content = file_context.get("patch", "")
        
        self.logger.info(f"Extracting functions from {file_path} (language: {language})")
        self.logger.info(f"Full content length: {len(full_content)}")
        self.logger.info(f"Patch content length: {len(patch_content)}")
        
        if not full_content or len(full_content) < 1000:
            if patch_content:
                self.logger.info(f"Using patch content for function extraction")
                return self._extract_functions_from_patch_content(patch_content, language)
            else:
                self.logger.warning(f"No content available for function extraction")
                return []
        
        function_patterns = LanguageDetector.get_function_patterns_for_language(language)
        if not function_patterns:
            self.logger.warning(f"No function patterns found for language: {language}")
            return []
        
        self.logger.info(f"Found {len(function_patterns)} function patterns for {language}")
        
        functions = []
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, full_content, re.MULTILINE)
            for match in matches:
                function_name = match.group(1)
                function_code = self._extract_function_code_by_pattern(
                    full_content, match.start(), function_patterns
                )
                if function_code:
                    functions.append((function_name, function_code))
                    self.logger.info(f"Found function: {function_name}")
        
        self.logger.info(f"Extracted {len(functions)} functions from full content")
        return functions
    
    def _create_basic_function_from_file(
        self,
        file_path: str,
        file_context: Dict[str, Any],
        language: str
    ) -> List[Tuple[str, str]]:
        functions = []
        
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        
        if language == "python":
            function_name = f"process_{base_name.lower()}"
            function_code = f"""def {function_name}():
    \"\"\"Basic function created for testing {filename}\"\"\"
    pass"""
            functions.append((function_name, function_code))
            self.logger.info(f"Created basic Python function: {function_name}")
        else:
            function_name = f"process{base_name.capitalize()}"
            function_code = f"// Basic function created for testing {filename}\n// Language: {language}"
            functions.append((function_name, function_code))
            self.logger.info(f"Created basic {language} function: {function_name}")
        
        return functions

    def _extract_functions_from_patch_content(
        self,
        patch_content: str,
        language: str
    ) -> List[Tuple[str, str]]:
        from .language_detector import LanguageDetector
        
        function_patterns = LanguageDetector.get_function_patterns_for_language(language)
        if not function_patterns:
            self.logger.warning(f"No function patterns found for language: {language}")
            return []
        
        self.logger.info(f"Extracting functions from patch content using {len(function_patterns)} patterns")
        
        functions = []
        
        lines = patch_content.split('\n')
        current_function = None
        current_function_lines = []
        
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                line_content = line[1:]
                
                for pattern in function_patterns:
                    match = re.match(pattern, line_content.strip())
                    if match:
                        if current_function and current_function_lines:
                            function_code = '\n'.join(current_function_lines)
                            if len(function_code.strip()) > 10:
                                functions.append((current_function, function_code))
                                self.logger.info(f"Completed function: {current_function}")
                        
                        current_function = match.group(1)
                        current_function_lines = [line_content]
                        self.logger.info(f"Started new function: {current_function}")
                        break
                else:
                    if current_function:
                        current_function_lines.append(line_content)
        
        if current_function and current_function_lines:
            function_code = '\n'.join(current_function_lines)
            if len(function_code.strip()) > 10:
                functions.append((current_function, function_code))
                self.logger.info(f"Completed last function: {current_function}")
        
        self.logger.info(f"Extracted {len(functions)} functions from patch content")
        return functions

    def _extract_function_code_by_pattern(
        self,
        content: str,
        start_pos: int,
        patterns: List[str]
    ) -> Optional[str]:
        remaining_content = content[start_pos:]
        end_pos = start_pos
        
        for pattern in patterns:
            next_match = re.search(pattern, remaining_content[1:], re.MULTILINE)
            if next_match:
                potential_end = start_pos + 1 + next_match.start()
                if potential_end < end_pos or end_pos == start_pos:
                    end_pos = potential_end
        
        if end_pos == start_pos:
            end_pos = len(content)
        
        return content[start_pos:end_pos].strip()

    def compare_prompt_strategies(
        self, diff_file_path: str, output_dir: str = "prompt_comparison"
    ) -> Dict[str, Any]:
        strategies = ["naive", "diff-aware", "few-shot", "cot"]
        results: Dict[str, Any] = {}

        for strategy in strategies:
            # Don't create strategy directories here - let the enhanced context processing handle it
            # strategy_dir = os.path.join(output_dir, strategy)
            # os.makedirs(strategy_dir, exist_ok=True)

            try:
                strategy_results = self.process_diff_file(
                    diff_file_path=diff_file_path,
                    output_dir=output_dir,  # Use the original output_dir, not strategy_dir
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

    def clear_memory(self):
        self.memory.clear()
        self.logger.info("Memory cleared")

    def _process_enhanced_context(self, pr_data_path: str, strategy: str) -> None:
        try:
            enhanced_context = EnhancedContextLoader(pr_data_path)
            source_files = enhanced_context.get_source_files()
            
            if not source_files:
                logging.warning("No source files found for testing")
                return
            
            logging.info(f"Found {len(source_files)} source files to process")
            
            for file_path in source_files:
                try:
                    file_context = enhanced_context.get_file_context(file_path)
                    language = file_context.get('language', 'unknown')
                    
                    if not language or language == 'unknown':
                        from .language_detector import LanguageDetector
                        language = LanguageDetector.detect_language_from_file(file_path)
                    
                    if not language:
                        logging.warning(f"Could not determine language for {file_path}")
                        continue

                    logging.info(f"Processing source file: {file_path} (language: {language})")
                    
                    function_code = self._extract_function_code_from_file(file_path, enhanced_context)
                    
                    if not function_code:
                        logging.warning(f"No function code extracted from {file_path}")
                        continue
                    
                    test_code = self._generate_test_with_strategy_and_context(
                        function_code, file_path, language, prompt_strategy, enhanced_context
                    )
                    
                    if test_code and test_code.strip():
                        # Note: File saving is handled by the main enhanced context processing
                        # This method only generates the test code, it doesn't save files
                        logging.info(f"Generated test code for {file_path} using {strategy} strategy")
                    else:
                        logging.error(f"Failed to generate test for {file_path}")
                        
                except Exception as e:
                    logging.error(f"Error processing {file_path}: {e}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error in enhanced context processing: {e}")
    
    def _generate_fallback_documentation(self, file_path: str, language: str, test_code: str) -> str:
        """Generate basic fallback documentation if the main method fails"""
        try:
            lines = test_code.split('\n')
            test_functions = []
            
            # Detect test functions based on language
            if language in ["python", "py"]:
                test_functions = [line.strip() for line in lines if line.strip().startswith('def test_')]
            elif language in ["go"]:
                test_functions = [line.strip() for line in lines if line.strip().startswith('func Test')]
            elif language in ["javascript", "js"]:
                test_functions = [line.strip() for line in lines if line.strip().startswith(('function test_', 'const test_', 'let test_'))]
            else:
                test_functions = [line.strip() for line in lines if any(keyword in line for keyword in ['test_', 'Test', 'test'])]
            
            base_name = Path(file_path).stem
            doc_content = f"""# Test File Documentation: {base_name}

## Overview
This test file contains {len(test_functions)} test functions for the {base_name} module.

## Language
{language.capitalize()}

## Test Functions
"""
            
            for func in test_functions[:10]:  # Limit to first 10 functions
                doc_content += f"- {func}\n"
            
            doc_content += f"""
## Running Tests
Run the tests using the appropriate test runner for {language}.

## Notes
This is automatically generated fallback documentation. Please review and enhance as needed.
"""
            
            return doc_content
            
        except Exception as e:
            logging.error(f"Error generating fallback documentation: {e}")
            return f"# Test File Documentation: {Path(file_path).stem}\n\n## Overview\nThis test file contains tests.\n\n## Language\n{language.capitalize()}\n\n## Running Tests\nRun the tests using the appropriate test runner for {language}."
    
    def _generate_test_with_strategy_and_context(
        self, 
        function_code: str, 
        file_path: str, 
        language: str, 
        strategy: str, 
        enhanced_context: EnhancedContextLoader
    ) -> str:
        try:
            context_data = enhanced_context.get_full_context_for_prompt(file_path)
            
            logging.info(f"Context data keys: {list(context_data.keys())}")
            logging.info(f"Function code length: {len(function_code)}")
            logging.info(f"Patch content length: {len(context_data.get('patch', ''))}")
            logging.info(f"Full content length: {len(context_data.get('full_content', ''))}")
            
            from .prompts import PromptTemplates
            
            enhanced_context_data = {
                'pr_title': context_data.get('pr_title', 'Unknown'),
                'pr_description': context_data.get('pr_description', ''),
                'imports': context_data.get('imports', []),
                'full_content': context_data.get('full_content', ''),
                'patch': context_data.get('patch', ''),
                'file_patch': context_data.get('file_patch', ''),
                'test_patterns': context_data.get('test_patterns', []),
                'context_summary': context_data.get('context_summary', {}),
                'repository_structure': context_data.get('repository_structure', {}),
                'dependencies': context_data.get('dependencies', {}),
                'related_files': context_data.get('related_files', []),
                'test_frameworks': context_data.get('test_frameworks', []),
                'build_config': context_data.get('build_config', {}),
                'environment_info': context_data.get('environment_info', {}),
                'actual_file_content': context_data.get('actual_file_content', ''),
                'working_directory': context_data.get('working_directory', ''),
                'package_manager': context_data.get('package_manager', ''),
                'test_command': context_data.get('test_command', ''),
                'import_paths': context_data.get('import_paths', [])
            }
            
            logging.info(f"Enhanced context data keys: {list(enhanced_context_data.keys())}")
            logging.info(f"PR Title: {enhanced_context_data.get('pr_title')}")
            logging.info(f"Imports count: {len(enhanced_context_data.get('imports', []))}")
            
            prompt = PromptTemplates.enhanced_context_prompt(
                        function_code=function_code,
                enhanced_context=enhanced_context_data,
                file_path=file_path,
                language=language
            )
            
            logging.info(f"Generated prompt length: {len(prompt)}")
            
            if hasattr(self.llm, 'generate'):
                test_code = self.llm.generate([{"role": "user", "content": prompt}], max_new_tokens=3072, max_retries=3)
            else:
                logging.error("LLM does not have generate method")
                return ""
            
            # DISABLED: Raw file saving to prevent nested directory creation
            # try:
            #     self._save_raw_test_file(file_path, language, test_code, strategy, enhanced_context, suffix="-raw")
            # except Exception as e:
            #     logging.warning(f"Could not save raw test output: {e}")
            
            logging.info(f"Generated test code length: {len(test_code)}")
            
            test_code = self._clean_and_validate_test(test_code, language)
            
            if not self._is_test_valid(test_code, language):
                error_msg = self._get_syntax_error(test_code, language)
                # Retry loop for LLM generation if validation fails
                max_retries = 3
                for attempt in range(max_retries):
                    if attempt > 0:
                        logging.info(f"Retry attempt {attempt + 1}/{max_retries} for {file_path}")
                        
                        # Create a stricter prompt for retries
                        strict_prompt = f"""CRITICAL: Your previous response was INVALID. You MUST generate a COMPLETE, RUNNABLE test file.

PREVIOUS ERRORS FOUND:
- The generated code was incomplete or had syntax errors
- You included English text, comments, or explanations
- The code was not ready to run
- The test logic was too basic or incomplete

ABSOLUTE REQUIREMENTS (NO EXCEPTIONS):
- Generate ONLY the complete test file code
- NO explanations, NO comments, NO English text
- NO backticks (```) or markdown
- NO "TODO" or "needs implementation" comments
- The file must be 100% syntactically correct
- Include ALL necessary imports and test functions
- Make it runnable immediately
- Include COMPLETE test logic with proper assertions
- Test both success and error cases
- Test edge cases and boundary conditions
- NOT just basic test functions - include comprehensive test coverage

IMPORT REQUIREMENTS:
- ALL import statements must be COMPLETE and valid
- NO incomplete imports like "from typing import (" or "from fastapi.concurrency import ("
- ALL parentheses must be properly closed
- Use the exact imports provided in the context
- Ensure all imports are syntactically correct

ORIGINAL PROMPT:
{prompt}

GENERATE THE COMPLETE TEST FILE NOW - NO EXCUSES, NO EXPLANATIONS, ONLY COMPLETE TEST CODE:"""
                        
                        try:
                            generated_test = self.llm.generate(
                                [{"role": "user", "content": strict_prompt}],
                                max_new_tokens=3072
                            )
                            
                            # DISABLED: Save raw retry output to prevent nested directories
                            # self._save_raw_test_file(file_path, language, generated_test, strategy, enhanced_context, suffix=f"-repair{attempt}-raw")
                            
                            # Clean and validate the retry
                            cleaned_test = self._clean_and_validate_test(generated_test, language)
                            
                            if cleaned_test and self._is_test_valid(cleaned_test, language):
                                logging.info(f"Retry {attempt + 1} successful - generated valid test code")
                                return cleaned_test
                            else:
                                logging.warning(f"Retry {attempt + 1} failed - code still invalid")
                                if attempt == max_retries - 1:
                                    logging.error(f"All {max_retries} retry attempts failed for {file_path}")
                                    return ""
                                
                        except Exception as e:
                            logging.error(f"Error during retry {attempt + 1}: {e}")
                            if attempt == max_retries - 1:
                                return ""
                            continue
                    else:
                        # First attempt
                        try:
                            generated_test = self.llm.generate(
                                [{"role": "user", "content": prompt}],
                                max_new_tokens=3072
                            )
                            
                            # DISABLED: Save raw output to prevent nested directories
                            # self._save_raw_test_file(file_path, language, generated_test, strategy, enhanced_context, suffix="-raw")
                            
                            # Clean and validate
                            cleaned_test = self._clean_and_validate_test(generated_test, language)
                            
                            if cleaned_test and self._is_test_valid(cleaned_test, language):
                                logging.info(f"First attempt successful - generated valid test code")
                                return cleaned_test
                            else:
                                logging.warning(f"First attempt failed - code invalid, will retry")
                                continue
                                
                        except Exception as e:
                            logging.error(f"Error during first attempt: {e}")
                            if max_retries == 1:
                                return ""
                            continue
             
            if not self._is_test_valid(test_code, language):
                logging.error("Final validation failed; not saving final file. Raw outputs are available.")
                return ""
            
            return test_code

        except Exception as e:
            logging.error(f"Error generating test with {strategy} strategy: {e}")
            return ""
    
    def _save_test_file(self, file_path: str, language: str, test_code: str, strategy: str, enhanced_context: EnhancedContextLoader) -> None:
        try:
            # Validate strategy parameter - only allow valid strategy names
            valid_strategies = ["naive", "few-shot", "cot", "diff-aware"]
            if strategy not in valid_strategies:
                logging.error(f"INVALID STRATEGY '{strategy}' - skipping file save. Valid strategies: {valid_strategies}")
                return
                
            pr_data_path = enhanced_context.pr_data_path
            # Use the actual model name instead of hardcoded "deepseek_coder"
            model_name = self.model_name.replace("/", "_").replace("-", "_")
            test_dir = pr_data_path / model_name / strategy
            
            logging.info(f"MAIN TEST FILE SAVE - Strategy: '{strategy}', File: {file_path}")
            logging.info(f"Creating test directory: {test_dir}")
            logging.info(f"Strategy parameter: '{strategy}'")
            logging.info(f"PR data path: {pr_data_path}")
            
            test_dir.mkdir(parents=True, exist_ok=True)
            
            base_name = Path(file_path).stem
            if not base_name.startswith('test_'):
                base_name = f"test_{base_name}"
            
            from .language_detector import LanguageDetector
            extension = LanguageDetector.get_file_extension_for_language(language, file_path)
            
            test_filename = f"{base_name}{extension}"
            test_file_path = test_dir / test_filename
            
            logging.info(f"Final test file path: {test_file_path}")
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            logging.info(f"Saved test file: {test_file_path}")
            
        except Exception as e:
            logging.error(f"Error saving test file: {e}")

    def _save_raw_test_file(self, file_path: str, language: str, test_code: str, strategy: str, enhanced_context: EnhancedContextLoader, suffix: str = "-raw") -> None:
        try:
            pr_data_path = enhanced_context.pr_data_path
            
            logging.info(f"RAW FILE SAVE - Strategy: '{strategy}', File: {file_path}")
            
            # Only create directories for valid strategies
            if strategy in ["naive", "few-shot", "cot", "diff-aware"]:
                # This is the main processing path - save to the correct strategy directory
                model_name = self.model_name.replace("/", "_").replace("-", "_")
                test_dir = pr_data_path / model_name / strategy
                logging.info(f"Creating main strategy directory: {test_dir}")
                test_dir.mkdir(parents=True, exist_ok=True)
            else:
                # Invalid strategy - don't create any directories
                logging.warning(f"Invalid strategy '{strategy}' - skipping directory creation")
                return

            base_name = Path(file_path).stem
            if not base_name.startswith('test_'):
                base_name = f"test_{base_name}"

            from .language_detector import LanguageDetector
            extension = LanguageDetector.get_file_extension_for_language(language, file_path)

            test_filename = f"{base_name}{suffix}{extension}"
            test_file_path = test_dir / test_filename

            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_code)

            logging.info(f"Saved RAW test file: {test_file_path}")
        except Exception as e:
            logging.error(f"Error saving RAW test file: {e}")

    def _save_documentation_file(self, file_path: str, language: str, doc_content: str, strategy: str, enhanced_context: EnhancedContextLoader) -> None:
        """Save documentation file for a test file"""
        try:
            pr_data_path = enhanced_context.pr_data_path
            # Use the actual model name instead of hardcoded "deepseek_coder"
            model_name = self.model_name.replace("/", "_").replace("-", "_")
            doc_dir = pr_data_path / model_name / strategy

            logging.info(f"DOC FILE SAVE - Strategy: '{strategy}', File: {file_path}")
            logging.info(f"Creating doc directory: {doc_dir}")

            doc_dir.mkdir(parents=True, exist_ok=True)

            # Extract the test file name from the source file path
            source_file_name = Path(file_path).stem
            test_file_name = f"test_{source_file_name}"
            
            # Create documentation filename with .md extension
            doc_filename = f"{test_file_name}_docs.md"
            doc_file_path = doc_dir / doc_filename

            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)

            logging.info(f"Saved documentation file: {doc_file_path}")
        except Exception as e:
            logging.error(f"Error saving documentation file: {e}")

    def _clean_and_validate_test(self, generated_text: str, language: str) -> str:
        """Clean and validate generated test code to ensure it's complete and error-free"""
        if not generated_text or not generated_text.strip():
            return ""
        
        # Step 1: Remove all markdown formatting and backticks
        cleaned = self._strip_fenced_code_blocks(generated_text)
        
        # Step 2: Remove all English text, comments, and explanations
        cleaned = self._strip_comments_and_prose(cleaned)
        
        # Step 3: Remove any remaining unwanted patterns
        cleaned = self._remove_unwanted_patterns(cleaned)
        
        # Step 4: Ensure proper file structure
        cleaned = self._ensure_complete_file_structure(cleaned, language)
        
        # Step 5: Final cleanup - remove any remaining backticks or markdown
        cleaned = cleaned.replace('```', '').replace('`', '')
        
        # Step 6: Validate syntax
        if language == "python":
            if not self._check_python_syntax_with_ast(cleaned):
                logging.warning("Generated code has syntax errors after cleaning")
                return ""
        
        return cleaned.strip()
    
    def _strip_fenced_code_blocks(self, text: str) -> str:
        """Remove all markdown code blocks and backticks while preserving content"""
        # Remove ```python, ```py, ``` blocks but keep the content
        text = re.sub(r'```(?:python|py|js|java|cpp|c|cs|go|rs|php|rb|swift|kt|scala|ts|jsx|tsx)?\s*\n?', '', text)
        text = re.sub(r'```\s*\n?', '', text)
        
        # Remove any remaining backticks (including single backticks)
        text = text.replace('`', '')
        
        # Remove any trailing incomplete import statements
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Skip incomplete import statements
            if stripped.endswith(('import', 'from', 'import ', 'from ')):
                continue
            # Skip incomplete from statements without import
            if stripped.startswith('from ') and ' import ' not in stripped:
                continue
            # Skip incomplete typing imports
            if stripped.startswith('from typing import (') and not stripped.endswith(')'):
                continue
            # Skip incomplete fastapi imports
            if stripped.startswith('from fastapi.') and stripped.endswith('('):
                continue
            # Skip any import line ending with open parenthesis
            if stripped.startswith(('import ', 'from ')) and stripped.endswith('('):
                continue
            # Skip any line that looks like an incomplete import
            if stripped.startswith('from ') and stripped.count('(') > stripped.count(')'):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _strip_comments_and_prose(self, text: str) -> str:
        """Remove all comments, English text, and explanations"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Skip comment lines
            if stripped.startswith('#'):
                continue
            
            # Skip lines that are just English text (no code) - but be more careful
            # Only skip if it's clearly just English prose, not code
            if (re.match(r'^[A-Za-z\s,\.!?]+$', stripped) and 
                not any(char in stripped for char in ['(', ')', '[', ']', '{', '}', ':', '=', '@', '.', '_']) and
                not stripped.startswith(('def ', 'class ', 'import ', 'from ', 'async ', 'await '))):
                continue
            
            # Skip lines with obvious unwanted patterns
            if any(pattern in stripped.lower() for pattern in [
                'sure,', 'here is', 'here\'s', 'this is', 'let me', 'i will',
                'i\'ll', 'you can', 'this function', 'the function', 'based on',
                'looking at', 'for this', 'to test', 'to document', 'example:',
                'note:', 'warning:', 'important:', 'remember:', 'assume',
                'replace', 'write here', 'your code', 'needs implementation',
                'basic test', 'simple example', 'comprehensive', 'detailed',
                'this demonstrates', 'as you can see', 'obviously', 'clearly',
                'evidently', 'therefore', 'thus', 'hence', 'consequently',
                'as a result', 'in conclusion', 'in summary', 'to summarize',
                'let me explain', 'i will explain', 'here\'s what', 'this shows',
                'you can see', 'as you can see', 'obviously', 'clearly',
                'evidently', 'therefore', 'thus', 'hence', 'consequently',
                'as a result', 'in conclusion', 'in summary', 'to summarize',
                'this is a', 'here is a', 'let me show', 'i will show',
                'you can see', 'as you can see', 'obviously', 'clearly',
                'evidently', 'therefore', 'thus', 'hence', 'consequently',
                'as a result', 'in conclusion', 'in summary', 'to summarize'
            ]):
                continue
            
            # Keep all other lines - be conservative
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _remove_unwanted_patterns(self, text: str) -> str:
        """Remove any remaining unwanted patterns"""
        # Remove lines with placeholder text
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip().lower()
            
            # Skip lines with unwanted content
            if any(pattern in stripped for pattern in [
                'todo', 'fixme', 'xxx', 'hack', 'note:', 'warning:', 'important:',
                'example:', 'sample:', 'template:', 'placeholder', 'your code here',
                'needs implementation', 'basic test', 'simple example', 'comprehensive',
                'detailed explanation', 'here is how', 'this shows', 'you can see',
                'as you can see', 'obviously', 'clearly', 'evidently', 'therefore',
                'thus', 'hence', 'consequently', 'as a result', 'in conclusion'
            ]):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _ensure_complete_file_structure(self, text: str, language: str) -> str:
        """Ensure the file has complete structure with proper imports and functions"""
        lines = text.split('\n')
        
        # Check if we have imports
        has_imports = any('import ' in line or 'from ' in line for line in lines)
        
        # Check if we have test functions
        has_test_functions = any('def test_' in line or 'def test' in line for line in lines)
        
        # If missing critical parts, return empty to trigger regeneration
        if not has_imports or not has_test_functions:
            logging.warning("Generated code missing critical parts (imports or test functions)")
            return ""
        
        return text

    def _is_test_valid(self, test_code: str, language: str) -> bool:
        """Validate that the generated test code is complete and runnable"""
        if not test_code or not test_code.strip():
            return False
        
        # Check for forbidden patterns that indicate incomplete or malformed code
        forbidden_patterns = [
            'todo', 'fixme', 'xxx', 'hack', 'needs implementation',
            'basic test', 'simple example', 'your code here', 'replace this',
            'write here', 'assuming', 'example:', 'note:', 'warning:',
            'here is how', 'this shows', 'you can see', 'obviously',
            'clearly', 'evidently', 'therefore', 'thus', 'hence',
            'consequently', 'as a result', 'in conclusion', 'sure,',
            'here is', 'here\'s', 'this is', 'let me', 'i will',
            'i\'ll', 'you can', 'this function', 'the function',
            'based on', 'looking at', 'for this', 'to test', 'to document',
            'this demonstrates', 'as you can see', 'obviously', 'clearly',
            'evidently', 'therefore', 'thus', 'hence', 'consequently',
            'as a result', 'in conclusion', 'in summary', 'to summarize',
            'let me explain', 'i will explain', 'here\'s what', 'this shows',
            'you can see', 'as you can see', 'obviously', 'clearly',
            'evidently', 'therefore', 'thus', 'hence', 'consequently',
            'as a result', 'in conclusion', 'in summary', 'to summarize'
        ]
        
        test_lower = test_code.lower()
        for pattern in forbidden_patterns:
            if pattern in test_lower:
                logging.warning(f"Generated code contains forbidden pattern: {pattern}")
                return False
        
        # Check for incomplete function definitions
        if 'def ' in test_code and ':' in test_code:
            lines = test_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('def ') and line.strip().endswith(':'):
                    # Check if the next line is properly indented and contains code
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if not next_line or next_line.startswith('#'):
                            logging.warning("Found incomplete function definition")
                            return False
        
        # Check for proper imports
        if language == "python":
            if not any('import ' in line or 'from ' in line for line in test_code.split('\n')):
                logging.warning("Generated code missing imports")
                return False
        
        # Check for test functions
        if not any('def test_' in line or 'def test' in line for line in test_code.split('\n')):
            logging.warning("Generated code missing test functions")
            return False
        
        # Check for assertions or test logic
        if not any('assert ' in line or 'assert' in line for line in test_code.split('\n')):
            logging.warning("Generated code missing assertions")
            return False
        
        # Check for syntax errors using AST for Python
        if language == "python":
            if not self._check_python_syntax_with_ast(test_code):
                logging.warning("Generated code has syntax errors")
                return False
        
        # Check for backticks or markdown
        if '`' in test_code or '```' in test_code:
            logging.warning("Generated code contains markdown formatting")
            return False
        
        # Check for repetitive imports (common LLM failure mode)
        import_lines = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
        if len(import_lines) > 20:  # More than 20 import lines is suspicious
            # Check for duplicate imports
            unique_imports = set(import_lines)
            if len(import_lines) > len(unique_imports) * 2:  # If we have more than 2x unique imports, likely repetitive
                logging.warning("Generated code has excessive repetitive imports")
                return False
        
        # Check for incomplete import statements
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                # Check if import statement is complete
                if stripped.endswith(('import', 'from', 'import ', 'from ')):
                    logging.warning("Generated code has incomplete import statements")
                    return False
                # Check if from statement has proper structure
                if stripped.startswith('from ') and ' import ' not in stripped:
                    logging.warning("Generated code has incomplete from import statements")
                    return False
                # Check for incomplete parentheses in imports
                if stripped.endswith('(') and not stripped.endswith(')'):
                    logging.warning("Generated code has incomplete import statements with unclosed parentheses")
                    return False
                # Check for incomplete typing imports
                if stripped.startswith('from typing import (') and not stripped.endswith(')'):
                    logging.warning("Generated code has incomplete typing import statements")
                    return False
                # Check for incomplete fastapi imports
                if stripped.startswith('from fastapi.') and stripped.endswith('('):
                    logging.warning("Generated code has incomplete fastapi import statements")
                    return False
                # Check for any import line ending with open parenthesis
                if stripped.endswith('('):
                    logging.warning("Generated code has incomplete import statements with unclosed parentheses")
                    return False
        
        # Check for excessive English text (more than 15% non-code lines)
        code_lines = 0
        total_lines = len(lines)
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Check if line contains actual code
                if any(char in stripped for char in ['import', 'from', 'def ', 'class ', 'test_', 'assert', '=', '(', ')', '[', ']', '{', '}', ':', 'if ', 'for ', 'while ', 'return', 'raise', 'try:', 'except:', 'finally:', 'with ', 'as ', 'in ', 'is ', 'and ', 'or ', 'not ', 'True', 'False', 'None', 'self', 'super', 'lambda', 'yield', 'async', 'await']):
                    code_lines += 1
                elif re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*[=<>!+\-*/%&|^~]', stripped):
                    # Assignment or comparison operations
                    code_lines += 1
                elif re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\(', stripped):
                    # Function calls
                    code_lines += 1
                elif re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\[', stripped):
                    # Array/list access
                    code_lines += 1
                elif re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\.', stripped):
                    # Method calls or attribute access
                    code_lines += 1
                elif stripped.startswith(('    ', '\t')):
                    code_lines += 1
        
        if total_lines > 0 and (code_lines / total_lines) < 0.85:
            logging.warning(f"Generated code has too much non-code content: {code_lines}/{total_lines} lines are code")
            return False
        
        # Ensure minimum content length for a proper test file
        if len(test_code.strip()) < 200:
            logging.warning("Generated code is too short for a complete test file")
            return False
        
        return True

    def _check_python_syntax_with_ast(self, code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
        except Exception:
            return False

    def _get_syntax_error(self, code: str, language: str) -> str:
        if language == 'py' or language == 'python':
            try:
                ast.parse(code)
                return ''
            except Exception as e:
                return str(e)
        return ''

    def _extract_function_code_from_file(self, file_path: str, enhanced_context: EnhancedContextLoader) -> str:
        try:
            file_context = enhanced_context.get_file_context(file_path)
            
            full_content = file_context.get('full_content', '')
            if not full_content:
                full_content = enhanced_context._get_actual_file_content(file_path)
            
            if not full_content:
                logging.warning(f"No content found for {file_path}")
                return ""
            
            patch_content = file_context.get('patch', '')
            
            if patch_content:
                lines = patch_content.split('\n')
                function_lines = []
                in_function = False
                
                for line in lines:
                    if line.startswith('+') and not line.startswith('+++'):
                        clean_line = line[1:]
                        
                        if any(keyword in clean_line for keyword in ['def ', 'class ', 'async def ']):
                            if in_function:
                                break
                            in_function = True
                            function_lines = [clean_line]
                        elif in_function:
                            function_lines.append(clean_line)
                
                if function_lines:
                    return '\n'.join(function_lines)
            
            if patch_content:
                function_patterns = [
                    r'def\s+(\w+)\s*\(',
                    r'class\s+(\w+)',
                    r'async\s+def\s+(\w+)\s*\('
                ]
                
                for pattern in function_patterns:
                    matches = re.finditer(pattern, patch_content)
                    for match in matches:
                        function_name = match.group(1)
                        function_pattern = rf'def\s+{re.escape(function_name)}\s*\([^)]*\):.*?(?=\n\s*def|\n\s*class|\Z)'
                        function_match = re.search(function_pattern, full_content, re.DOTALL)
                        if function_match:
                            return function_match.group(0)
            
            lines = full_content.split('\n')
            function_lines = []
            
            for line in lines:
                if any(keyword in line for keyword in ['def ', 'class ', 'async def ']):
                    function_lines.append(line)
                elif function_lines and line.strip():
                    function_lines.append(line)
                elif function_lines and not line.strip():
                    if len(function_lines) > 1:
                        break
            
            return '\n'.join(function_lines) if function_lines else full_content[:1000]
            
        except Exception as e:
            logging.error(f"Error extracting function code from {file_path}: {e}")
            return ""
