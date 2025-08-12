import ast
import re
from typing import Dict, List, Tuple, Optional
from .llm import PhindCodeLlamaLLM
import logging

class DocumentationGenerator:
    def __init__(self, llm: PhindCodeLlamaLLM):
        self.llm = llm
    
    def extract_functions_for_documentation(self, diff_content: str) -> List[Tuple[str, str, str]]:
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
                        functions.append((function_name, function_code, file_path))
        
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
    
    def generate_documentation_for_diff(self, diff_content: str) -> Dict[str, str]:
        functions = self.extract_functions_for_documentation(diff_content)
        generated_docs = {}
        
        for function_name, function_code, file_path in functions:
            try:
                logging.info(f"Generating documentation for function: {function_name}")
                doc = self.llm.generate_documentation(
                    function_code=function_code,
                    function_name=function_name
                )
                generated_docs[function_name] = doc
                logging.info(f"Successfully generated documentation for {function_name}")
            except Exception as e:
                logging.error(f"Error generating documentation for {function_name}: {e}")
                generated_docs[function_name] = f"# Error generating documentation: {str(e)}"
        
        return generated_docs
    
    def generate_documentation_for_function(self, function_code: str, function_name: str) -> str:
        try:
            return self.llm.generate_documentation(
                function_code=function_code,
                function_name=function_name
            )
        except Exception as e:
            logging.error(f"Error generating documentation for {function_name}: {e}")
            return f"# Error generating documentation: {str(e)}"
    
    def generate_documentation(self, function_code: str, function_name: str, diff_context: str = "") -> str:
        return self.generate_documentation_for_function(function_code, function_name)
    
    def generate_readme_section(self, functions: List[Tuple[str, str]], module_name: str) -> str:
        try:
            function_summaries = []
            for func_name, func_code in functions:
                lines = func_code.split('\n')
                signature = lines[0] if lines else ""
                function_summaries.append(f"- `{func_name}`: {signature}")
            
            functions_text = '\n'.join(function_summaries)
            
            messages = [
                {"role": "user", "content": f"""Generate a README section for the {module_name} module.

Functions in this module:
{functions_text}

Please provide:
1. A brief overview of what this module does
2. Installation/usage instructions if relevant
3. API documentation for each function
4. Examples of how to use the functions
5. Any important notes or dependencies"""}
            ]
            
            return self.llm.generate(messages, max_new_tokens=1024)
        except Exception as e:
            logging.error(f"Error generating README section: {e}")
            return f"# Error generating README section: {str(e)}"
    
    def format_docstring(self, doc_content: str, style: str = "google") -> str:
        if style == "google":
            return self._format_google_docstring(doc_content)
        elif style == "numpy":
            return self._format_numpy_docstring(doc_content)
        else:
            return self._format_sphinx_docstring(doc_content)
    
    def _format_google_docstring(self, doc_content: str) -> str:
        lines = doc_content.split('\n')
        formatted_lines = ['"""']
        
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                section_name = line.split(':', 1)[1].strip() if ':' in line else line[2:].strip()
                formatted_lines.append(f"\n{section_name}:")
            elif line.startswith('- '):
                formatted_lines.append(f"    {line[2:]}")
            elif line:
                formatted_lines.append(line)
        
        formatted_lines.append('"""')
        return '\n'.join(formatted_lines)
    
    def _format_numpy_docstring(self, doc_content: str) -> str:
        lines = doc_content.split('\n')
        formatted_lines = ['"""']
        
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                section_name = line.split(':', 1)[1].strip() if ':' in line else line[2:].strip()
                formatted_lines.append(f"\n{section_name}\n{'-' * len(section_name)}")
            elif line.startswith('- '):
                formatted_lines.append(f"    {line[2:]}")
            elif line:
                formatted_lines.append(line)
        
        formatted_lines.append('"""')
        return '\n'.join(formatted_lines)
    
    def _format_sphinx_docstring(self, doc_content: str) -> str:
        lines = doc_content.split('\n')
        formatted_lines = ['"""']
        
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                section_name = line.split(':', 1)[1].strip() if ':' in line else line[2:].strip()
                formatted_lines.append(f"\n:{section_name}:")
            elif line.startswith('- '):
                formatted_lines.append(f"    {line[2:]}")
            elif line:
                formatted_lines.append(line)
        
        formatted_lines.append('"""')
        return '\n'.join(formatted_lines) 