import re
from typing import Dict, List, Tuple, Optional, Any
import os
from .language_detector import LanguageDetector

def get_changed_functions(before_file: str, after_file: str) -> dict:
    """Get changed functions from before and after files using language-agnostic parsing."""
    try:
        with open(before_file, "r", encoding='utf-8') as f:
            before_content = f.read()
        with open(after_file, "r", encoding='utf-8') as f:
            after_content = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        return {}

    # Detect language from file extension
    language = LanguageDetector.detect_language_from_file(before_file)
    if not language:
        print(f"Could not detect language for file: {before_file}")
        return {}

    # Get function patterns for the detected language
    function_patterns = LanguageDetector.get_function_patterns_for_language(language)
    
    # Extract functions using regex patterns
    funcs_before = _extract_functions_with_patterns(before_content, function_patterns)
    funcs_after = _extract_functions_with_patterns(after_content, function_patterns)

    changed_funcs = {}
    for name, func_code in funcs_after.items():
        if name not in funcs_before or funcs_before[name] != func_code:
            changed_funcs[name] = func_code

    return changed_funcs

def _extract_functions_with_patterns(content: str, patterns: List[str]) -> Dict[str, str]:
    """Extract functions using language-specific patterns."""
    functions = {}
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            func_name = match.group(1)
            func_code = _extract_function_code_by_pattern(content, match.start(), patterns)
            if func_code:
                functions[func_name] = func_code
    
    return functions

def _extract_function_code_by_pattern(content: str, start_pos: int, patterns: List[str]) -> Optional[str]:
    """Extract function code starting from a pattern match position."""
    lines = content[:start_pos].split('\n')
    start_line = len(lines)
    
    # Find the end of the function by looking for the next function or class definition
    remaining_content = content[start_pos:]
    end_pos = start_pos
    
    # Look for the next function/class definition
    for pattern in patterns:
        next_match = re.search(pattern, remaining_content[1:], re.MULTILINE)
        if next_match:
            potential_end = start_pos + 1 + next_match.start()
            if potential_end < end_pos or end_pos == start_pos:
                end_pos = potential_end
    
    # If no next function found, take to end of file
    if end_pos == start_pos:
        end_pos = len(content)
    
    return content[start_pos:end_pos].strip()

def extract_functions_from_diff(diff_content: str) -> List[Tuple[str, str, str, str]]:
    functions = []
    
    diff_chunks = _split_diff_into_chunks(diff_content)
    
    for chunk in diff_chunks:
        file_path, added_lines, removed_lines = _parse_diff_chunk(chunk)
        
        # Skip if no file path or if it's a binary/config file
        if not file_path or _is_binary_or_config_file(file_path):
            continue
        
        # Detect language from file path
        language = LanguageDetector.detect_language_from_file(file_path)
        if not language or not LanguageDetector.is_supported_language(language):
            continue
            
        # Get function patterns for the detected language
        function_patterns = LanguageDetector.get_function_patterns_for_language(language)
        
        # Check if this is a test file
        is_test_file = _is_test_file(file_path, language)
            
        for line_num, line in added_lines:
            # Check if line matches any function pattern for the language
            for pattern in function_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    function_name = match.group(1)
                    function_code = _extract_function_code_language_aware(added_lines, line_num, language, function_patterns)
                    if function_code:
                        functions.append((function_name, function_code, file_path, language))
                    break
        
        # If no functions found but this is a test file, create a synthetic test function
        if not functions and is_test_file and added_lines:
            synthetic_function = _create_synthetic_test_function(added_lines, language, file_path)
            if synthetic_function:
                functions.append(synthetic_function)
    
    return functions

def _split_diff_into_chunks(diff_content: str) -> List[str]:
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

def _parse_diff_chunk(chunk: str) -> Tuple[str, List[Tuple[int, str]], List[Tuple[int, str]]]:
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

def _is_binary_or_config_file(file_path: str) -> bool:
    """Check if file is binary or config file that shouldn't be processed."""
    config_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', 
                         '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
                         '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
                         '.bin', '.dat', '.db', '.sqlite', '.sqlite3'}
    
    _, ext = os.path.splitext(file_path.lower())
    return ext in config_extensions

def _is_test_file(file_path: str, language: str) -> bool:
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

def _create_synthetic_test_function(added_lines: List[Tuple[int, str]], language: str, file_path: str) -> Optional[Tuple[str, str, str, str]]:
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
                        return (f"test_{func_name}", '\n'.join(content_lines), file_path, language)
    
    elif language == 'python':
        # Look for test functions or assertions
        for line in content_lines:
            if line.strip().startswith('def test_') or 'assert' in line:
                # Extract test function name
                match = re.search(r'def\s+(\w+)', line)
                if match:
                    return (match.group(1), '\n'.join(content_lines), file_path, language)
    
    elif language == 'java':
        # Look for @Test annotations
        for line in content_lines:
            if '@Test' in line:
                # Look for the next line with a method definition
                for next_line in content_lines[content_lines.index(line):]:
                    if 'public' in next_line and '(' in next_line:
                        match = re.search(r'public\s+\w+\s+(\w+)\s*\(', next_line)
                        if match:
                            return (match.group(1), '\n'.join(content_lines), file_path, language)
    
    elif language in ['cpp', 'c']:
        # Look for TEST macros
        for line in content_lines:
            if line.strip().startswith('TEST(') or line.strip().startswith('TEST_F('):
                # Extract test name
                match = re.search(r'TEST(?:_F)?\s*\(\s*\w+\s*,\s*(\w+)\s*\)', line)
                if match:
                    return (f"test_{match.group(1)}", '\n'.join(content_lines), file_path, language)
    
    # Fallback: create a generic test function name
    return (f"test_added_functionality", '\n'.join(content_lines), file_path, language)

def _extract_function_code_language_aware(added_lines: List[Tuple[int, str]], start_line: int, 
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

def load_diff_from_file(diff_file_path: str) -> str:
    try:
        with open(diff_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading diff file {diff_file_path}: {e}")
        return ""

def get_functions_from_diff_file(diff_file_path: str) -> List[Tuple[str, str, str, str]]:
    diff_content = load_diff_from_file(diff_file_path)
    if not diff_content:
        return []
    
    return extract_functions_from_diff(diff_content)

def analyze_diff_changes(diff_content: str) -> Dict[str, Any]:
    analysis = {
        "files_modified": [],
        "functions_added": [],
        "functions_modified": [],
        "functions_removed": [],
        "total_lines_added": 0,
        "total_lines_removed": 0,
        "languages_detected": set()
    }
    
    diff_chunks = _split_diff_into_chunks(diff_content)
    
    for chunk in diff_chunks:
        file_path, added_lines, removed_lines = _parse_diff_chunk(chunk)
        
        if file_path and not _is_binary_or_config_file(file_path):
            analysis["files_modified"].append(file_path)
            analysis["total_lines_added"] += len(added_lines)
            analysis["total_lines_removed"] += len(removed_lines)
            
            # Detect language for this file
            language = LanguageDetector.detect_language_from_file(file_path)
            if language:
                analysis["languages_detected"].add(language)
                
                # Get function patterns for the detected language
                function_patterns = LanguageDetector.get_function_patterns_for_language(language)
                
                # Check added lines for function definitions
                for line_num, line in added_lines:
                    for pattern in function_patterns:
                        match = re.match(pattern, line.strip())
                        if match:
                            function_name = match.group(1)
                            analysis["functions_added"].append((function_name, file_path, language))
                            break
                
                # Check removed lines for function definitions
                for line_num, line in removed_lines:
                    for pattern in function_patterns:
                        match = re.match(pattern, line.strip())
                        if match:
                            function_name = match.group(1)
                            analysis["functions_removed"].append((function_name, file_path, language))
                            break
    
    # Convert set to list for JSON serialization
    analysis["languages_detected"] = list(analysis["languages_detected"])
    
    return analysis



