import ast
import re
from typing import Dict, List, Tuple, Optional, Any
import os

def get_changed_functions(before_file: str, after_file: str) -> dict:
    """Get changed functions by comparing two files."""
    with open(before_file, "r") as f:
        before_code_tree = ast.parse(f.read())
    with open(after_file, "r") as f:
        after_code_tree = ast.parse(f.read())

    funcs_before = {f.name: f for f in before_code_tree.body if isinstance(f, ast.FunctionDef)}
    funcs_after = {f.name: f for f in after_code_tree.body if isinstance(f, ast.FunctionDef)}

    changed_funcs = {}
    for name in funcs_after:
        if name not in funcs_before or ast.dump(funcs_before[name]) != ast.dump(funcs_after[name]):
            changed_funcs[name] = funcs_after[name]

    return changed_funcs

def extract_functions_from_diff(diff_content: str) -> List[Tuple[str, str, str]]:
    """
    Extract function definitions from diff content.
    
    Args:
        diff_content: Git diff content
        
    Returns:
        List of tuples (function_name, function_code, file_path)
    """
    functions = []
    
    # Split diff into chunks
    diff_chunks = _split_diff_into_chunks(diff_content)
    
    for chunk in diff_chunks:
        file_path, added_lines, removed_lines = _parse_diff_chunk(chunk)
        
        if not file_path.endswith('.py'):
            continue
            
        # Extract function definitions from added lines
        for line_num, line in added_lines:
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                function_name = _extract_function_name(line)
                if function_name:
                    function_code = _extract_function_code(added_lines, line_num)
                    functions.append((function_name, function_code, file_path))
    
    return functions

def _split_diff_into_chunks(diff_content: str) -> List[str]:
    """Split diff content into individual file chunks."""
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
    """Parse a diff chunk to extract file path and line changes."""
    lines = chunk.split('\n')
    file_path = ""
    added_lines = []
    removed_lines = []
    
    for line in lines:
        if line.startswith('+++ b/'):
            file_path = line[6:]  # Remove '+++ b/' prefix
        elif line.startswith('+') and not line.startswith('+++'):
            # Extract line number from context
            line_num = len(added_lines) + 1  # Approximate line number
            added_lines.append((line_num, line[1:]))  # Remove '+' prefix
        elif line.startswith('-') and not line.startswith('---'):
            line_num = len(removed_lines) + 1
            removed_lines.append((line_num, line[1:]))
    
    return file_path, added_lines, removed_lines

def _extract_function_name(line: str) -> Optional[str]:
    """Extract function name from function definition line."""
    match = re.match(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(', line)
    return match.group(1) if match else None

def _extract_function_code(added_lines: List[Tuple[int, str]], start_line: int) -> str:
    """Extract complete function code from added lines."""
    function_lines = []
    indent_level = None
    
    for line_num, line in added_lines:
        if line_num >= start_line:
            # Determine initial indentation
            if indent_level is None:
                indent_level = len(line) - len(line.lstrip())
            
            # Check if we've reached the end of the function
            if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line_num > start_line:
                break
            
            function_lines.append(line)
    
    return '\n'.join(function_lines)

def load_diff_from_file(diff_file_path: str) -> str:
    """
    Load diff content from a file.
    
    Args:
        diff_file_path: Path to the diff file
        
    Returns:
        Diff content as string
    """
    try:
        with open(diff_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading diff file {diff_file_path}: {e}")
        return ""

def get_functions_from_diff_file(diff_file_path: str) -> List[Tuple[str, str, str]]:
    """
    Extract functions from a diff file.
    
    Args:
        diff_file_path: Path to the diff file
        
    Returns:
        List of tuples (function_name, function_code, file_path)
    """
    diff_content = load_diff_from_file(diff_file_path)
    if not diff_content:
        return []
    
    return extract_functions_from_diff(diff_content)

def analyze_diff_changes(diff_content: str) -> Dict[str, Any]:
    """
    Analyze changes in a diff to understand what was modified.
    
    Args:
        diff_content: Git diff content
        
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        "files_modified": [],
        "functions_added": [],
        "functions_modified": [],
        "functions_removed": [],
        "total_lines_added": 0,
        "total_lines_removed": 0
    }
    
    diff_chunks = _split_diff_into_chunks(diff_content)
    
    for chunk in diff_chunks:
        file_path, added_lines, removed_lines = _parse_diff_chunk(chunk)
        
        if file_path:
            analysis["files_modified"].append(file_path)
            analysis["total_lines_added"] += len(added_lines)
            analysis["total_lines_removed"] += len(removed_lines)
            
            # Extract function names from added lines
            for line_num, line in added_lines:
                if line.strip().startswith('def ') or line.strip().startswith('async def '):
                    function_name = _extract_function_name(line)
                    if function_name:
                        analysis["functions_added"].append((function_name, file_path))
            
            # Extract function names from removed lines
            for line_num, line in removed_lines:
                if line.strip().startswith('def ') or line.strip().startswith('async def '):
                    function_name = _extract_function_name(line)
                    if function_name:
                        analysis["functions_removed"].append((function_name, file_path))
    
    return analysis



