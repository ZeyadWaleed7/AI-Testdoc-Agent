import ast
import re
from typing import Dict, List, Tuple, Optional
from .llm import PhindCodeLlamaLLM
import logging

class TestGenerator:
    def __init__(self, llm: PhindCodeLlamaLLM):
        self.llm = llm
        self.prompt_strategies = ["naive", "diff-aware", "few-shot", "cot"]
    
    def extract_functions_from_diff(self, diff_content: str) -> List[Tuple[str, str, str]]:
        functions = []
        
        diff_chunks = self._split_diff_into_chunks(diff_content)
        
        for chunk in diff_chunks:
            file_path, added_lines, removed_lines = self._parse_diff_chunk(chunk)
            
            if not file_path.endswith('.py'):
                continue
                
            for line_num, line in added_lines:
                if line.strip().startswith('def ') or line.strip().startswith('async def '):
                    function_name = self._extract_function_name(line)
                    if function_name:
                        function_code = self._extract_function_code(added_lines, line_num)
                        diff_context = self._create_diff_context(added_lines, removed_lines)
                        functions.append((function_name, function_code, diff_context))
        
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
    
    def _extract_function_name(self, line: str) -> Optional[str]:
        match = re.match(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(', line)
        return match.group(1) if match else None
    
    def _extract_function_code(self, added_lines: List[Tuple[int, str]], start_line: int) -> str:
        function_lines = []
        indent_level = None
        
        for line_num, line in added_lines:
            if line_num >= start_line:
                if indent_level is None:
                    indent_level = len(line) - len(line.lstrip())
                
                if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line_num > start_line:
                    break
                
                function_lines.append(line)
        
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
    
    def generate_tests_for_diff(self, diff_content: str, prompt_strategy: str = "diff-aware") -> Dict[str, str]:
        functions = self.extract_functions_from_diff(diff_content)
        generated_tests = {}
        
        for function_name, function_code, diff_context in functions:
            try:
                logging.info(f"Generating test for function: {function_name}")
                test_code = self.llm.generate_test(
                    function_code=function_code,
                    diff_context=diff_context,
                    prompt_strategy=prompt_strategy
                )
                generated_tests[function_name] = test_code
                logging.info(f"Successfully generated test for {function_name}")
            except Exception as e:
                logging.error(f"Error generating test for {function_name}: {e}")
                generated_tests[function_name] = f"# Error generating test: {str(e)}"
        
        return generated_tests
    
    def generate_tests_for_function(self, function_code: str, function_name: str, 
                                  diff_context: str = "", prompt_strategy: str = "diff-aware") -> str:
        try:
            return self.llm.generate_test(
                function_code=function_code,
                diff_context=diff_context,
                prompt_strategy=prompt_strategy
            )
        except Exception as e:
            logging.error(f"Error generating test for {function_name}: {e}")
            return f"# Error generating test: {str(e)}"
    
    def compare_prompt_strategies(self, function_code: str, diff_context: str = "") -> Dict[str, str]:
        results = {}
        
        for strategy in self.prompt_strategies:
            try:
                test_code = self.llm.generate_test(
                    function_code=function_code,
                    diff_context=diff_context,
                    prompt_strategy=strategy
                )
                results[strategy] = test_code
            except Exception as e:
                logging.error(f"Error with strategy {strategy}: {e}")
                results[strategy] = f"# Error: {str(e)}"
        
        return results
