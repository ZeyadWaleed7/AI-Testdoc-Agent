import os
import re
from typing import Dict, List, Tuple, Optional
from .llm import PhindCodeLlamaLLM
from .language_detector import LanguageDetector
import logging

class TestGenerator:
    def __init__(self, llm: PhindCodeLlamaLLM):
        self.llm = llm
        self.prompt_strategies = ["naive", "diff-aware", "few-shot", "cot"]
    
    def extract_functions_from_diff(self, diff_content: str) -> List[Tuple[str, str, str, str]]:
        functions = []
        
        diff_chunks = self._split_diff_into_chunks(diff_content)
        
        for chunk in diff_chunks:
            file_path, added_lines, removed_lines = self._parse_diff_chunk(chunk)
            
            # Skip if no file path or if it's a binary/config file
            if not file_path or self._is_binary_or_config_file(file_path):
                continue
            
            # Detect language from file path
            language = LanguageDetector.detect_language_from_file(file_path)
            if not language or not LanguageDetector.is_supported_language(language):
                continue
                
                        # Get function patterns for the detected language
            function_patterns = LanguageDetector.get_function_patterns_for_language(language)
            
            # Check if this is a test file
            is_test_file = self._is_test_file(file_path, language)
            
            for line_num, line in added_lines:
                # Check if line matches any function pattern for the language
                for pattern in function_patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        function_name = match.group(1)
                        function_code = self._extract_function_code_language_aware(added_lines, line_num, language, function_patterns)
                        diff_context = self._create_diff_context(added_lines, removed_lines)
                        if function_code:
                            functions.append((function_name, function_code, diff_context, language))
                        break
            
            # If no functions found but this is a test file, create a synthetic test function
            if not functions and is_test_file and added_lines:
                synthetic_function = self._create_synthetic_test_function(added_lines, language, file_path)
                if synthetic_function:
                    functions.append(synthetic_function)
            
        return functions
    
    def _split_diff_into_chunks(self, diff_content: str) -> List[str]:
        chunks = []
        current_chunk = []
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
            else:
                current_chunk.append(line)
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _parse_diff_chunk(self, chunk: str) -> Tuple[str, List[Tuple[int, str]], List[Tuple[int, str]]]:
        lines = chunk.split('\n')
        file_path = ""
        added_lines = []
        removed_lines = []
        
        for line in lines:
            if line.startswith('+++ b/'):
                file_path = line[6:]
            elif line.startswith('+') and not line.startswith('+++'):
                line_num = len(added_lines) + 1
                added_lines.append((line_num, line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                line_num = len(removed_lines) + 1
                removed_lines.append((line_num, line[1:]))
        
        return file_path, added_lines, removed_lines
    
    def _is_binary_or_config_file(self, file_path: str) -> bool:
        """Check if file is binary or config file that shouldn't be processed."""
        config_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', 
                             '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
                             '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
                             '.bin', '.dat', '.db', '.sqlite', '.sqlite3'}
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in config_extensions

    def _is_test_file(self, file_path: str, language: str) -> bool:
        """Check if file is a test file based on naming conventions."""
        filename = os.path.basename(file_path).lower()
        
        # Common test file patterns
        test_patterns = [
            'test_', '_test', 'test.', '.test',
            'spec_', '_spec', 'spec.', '.spec',
            'test.js', 'test.ts', 'test.jsx', 'test.tsx',
            'test.py', 'test.java', 'test.cpp', 'test.c',
            'tests.js', 'tests.ts', 'tests.py', 'tests.java'
        ]
        
        return any(pattern in filename for pattern in test_patterns)

    def _create_synthetic_test_function(self, added_lines: List[Tuple[int, str]], language: str, file_path: str) -> Optional[Tuple[str, str, str, str]]:
        """Create a synthetic test function when no explicit functions are found in test files."""
        if not added_lines:
            return None
        
        # Extract meaningful content from added lines
        content_lines = []
        for line_num, line in added_lines:
            if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('#'):
                content_lines.append(line)
        
        if not content_lines:
            return None
        
        # Create a synthetic function name based on the content
        if language in ['javascript', 'typescript']:
            # Look for describe/it blocks
            for line in content_lines:
                if 'describe(' in line or 'it(' in line:
                    # Extract the test description
                    match = re.search(r'[\'"`]([^\'"`]+)[\'"`]', line)
                    if match:
                        test_desc = match.group(1)
                        # Create a clean function name
                        func_name = re.sub(r'[^a-zA-Z0-9]', '_', test_desc.lower())
                        func_name = re.sub(r'_+', '_', func_name).strip('_')
                        if func_name:
                            return (f"test_{func_name}", '\n'.join(content_lines), self._create_diff_context(added_lines, []), language)
        
        elif language == 'python':
            # Look for test functions or assertions
            for line in content_lines:
                if line.strip().startswith('def test_') or 'assert' in line:
                    # Extract test function name
                    match = re.search(r'def\s+(\w+)', line)
                    if match:
                        return (match.group(1), '\n'.join(content_lines), self._create_diff_context(added_lines, []), language)
        
        elif language == 'java':
            # Look for @Test annotations
            for line in content_lines:
                if '@Test' in line:
                    # Look for the next line with a method definition
                    for next_line in content_lines[content_lines.index(line):]:
                        if 'public' in next_line and '(' in next_line:
                            match = re.search(r'public\s+\w+\s+(\w+)\s*\(', next_line)
                            if match:
                                return (match.group(1), '\n'.join(content_lines), self._create_diff_context(added_lines, []), language)
        
        elif language in ['cpp', 'c']:
            # Look for TEST macros
            for line in content_lines:
                if line.strip().startswith('TEST(') or line.strip().startswith('TEST_F('):
                    # Extract test name
                    match = re.search(r'TEST(?:_F)?\s*\(\s*\w+\s*,\s*(\w+)\s*\)', line)
                    if match:
                        return (f"test_{match.group(1)}", '\n'.join(content_lines), self._create_diff_context(added_lines, []), language)
        
        # Fallback: create a generic test function name
        return (f"test_added_functionality", '\n'.join(content_lines), self._create_diff_context(added_lines, []), language)

    def _extract_function_code_language_aware(self, added_lines: List[Tuple[int, str]], start_line: int, 
                                            language: str, function_patterns: List[str]) -> str:
        """Extract function code using language-aware parsing."""
        function_lines = []
        
        # Get language-specific indentation rules
        if language in ['python', 'yaml']:
            # Python-style indentation
            indent_level = None
            for line_num, line in added_lines:
                if line_num >= start_line:
                    if indent_level is None:
                        indent_level = len(line) - len(line.lstrip())
                    
                    if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line_num > start_line:
                        break
                    
                    function_lines.append(line)
        else:
            # Brace-based languages (C, Java, JavaScript, etc.)
            brace_count = 0
            started = False
            
            for line_num, line in added_lines:
                if line_num >= start_line:
                    if not started:
                        started = True
                    
                    # Count braces
                    brace_count += line.count('{') - line.count('}')
                    function_lines.append(line)
                    
                    # If we've closed all braces, we're done
                    if brace_count <= 0 and started:
                        break
        
        return '\n'.join(function_lines)
    
    def _create_diff_context(self, added_lines: List[Tuple[int, str]], removed_lines: List[Tuple[int, str]]) -> str:
        context_lines = []
        
        if removed_lines:
            context_lines.append("Removed lines:")
            for line_num, line in removed_lines:
                context_lines.append(f"  - {line}")
        
        if added_lines:
            context_lines.append("Added lines:")
            for line_num, line in added_lines:
                context_lines.append(f"  + {line}")
        
        return '\n'.join(context_lines)
    
    def generate_tests_for_diff(self, diff_content: str, prompt_strategy: str = "diff-aware") -> Dict[str, Dict[str, str]]:
        functions = self.extract_functions_from_diff(diff_content)
        generated_tests = {}
        
        for function_name, function_code, diff_context, language in functions:
            try:
                logging.info(f"Generating {language} test for function: {function_name}")
                test_code = self.llm.generate_test(
                    function_code=function_code,
                    diff_context=diff_context,
                    prompt_strategy=prompt_strategy,
                    language=language
                )
                generated_tests[function_name] = {
                    'test_code': test_code,
                    'language': language,
                    'file_extension': LanguageDetector.get_file_extension_for_language(language)
                }
                logging.info(f"Successfully generated {language} test for {function_name}")
            except Exception as e:
                logging.error(f"Error generating {language} test for {function_name}: {e}")
                generated_tests[function_name] = {
                    'test_code': f"# Error generating test: {str(e)}",
                    'language': language,
                    'file_extension': LanguageDetector.get_file_extension_for_language(language)
                }
        
        return generated_tests
    
    def generate_tests_for_function(self, function_code: str, function_name: str, 
                                  diff_context: str = "", prompt_strategy: str = "diff-aware",
                                  language: str = "python") -> str:
        try:
            return self.llm.generate_test(
                function_code=function_code,
                diff_context=diff_context,
                prompt_strategy=prompt_strategy,
                language=language
            )
        except Exception as e:
            logging.error(f"Error generating {language} test for {function_name}: {e}")
            return f"# Error generating test: {str(e)}"
    
    def compare_prompt_strategies(self, function_code: str, diff_context: str = "", 
                                language: str = "python") -> Dict[str, str]:
        results = {}
        
        for strategy in self.prompt_strategies:
            try:
                test_code = self.llm.generate_test(
                    function_code=function_code,
                    diff_context=diff_context,
                    prompt_strategy=strategy,
                    language=language
                )
                results[strategy] = test_code
            except Exception as e:
                logging.error(f"Error with strategy {strategy}: {e}")
                results[strategy] = f"# Error: {str(e)}"
        
        return results
