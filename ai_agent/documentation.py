import ast
import re
import os
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
            
            # Skip non-source code files
            if not self._is_source_code_file(file_path):
                continue
                
            # Detect language from file extension
            language = self._detect_language_from_file(file_path)
            if not language:
                continue
                
            for line_num, line in added_lines:
                if self._is_function_definition(line, language):
                    function_name = self._extract_function_name(line, language)
                    if function_name:
                        function_code = self._extract_function_code(added_lines, line_num, language)
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
    
    def _is_source_code_file(self, file_path: str) -> bool:
        """Check if file is a source code file that should have documentation generated"""
        if not file_path:
            return False
        
        # Define source code file extensions
        source_extensions = {
            '.py', '.pyw', '.pyx', '.pyi',  # Python
            '.js', '.jsx', '.mjs', '.cjs',  # JavaScript
            '.ts', '.tsx',                   # TypeScript
            '.java',                         # Java
            '.cpp', '.cc', '.cxx', '.hpp', '.hxx', '.h', '.c',  # C/C++
            '.cs',                           # C#
            '.go',                           # Go
            '.rs',                           # Rust
            '.php',                          # PHP
            '.rb',                           # Ruby
            '.swift',                        # Swift
            '.kt', '.kts',                   # Kotlin
            '.scala',                        # Scala
            '.dart',                         # Dart
            '.r', '.R',                      # R
            '.m',                            # MATLAB
            '.pl', '.pm',                    # Perl
            '.sh', '.bash',                  # Bash
            '.ps1',                          # PowerShell
            '.sql',                          # SQL
        }
        
        _, ext = os.path.splitext(file_path)
        return ext.lower() in source_extensions
    
    def _detect_language_from_file(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        if not file_path:
            return None
        
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        
        # Language to extension mapping
        language_map = {
            '.py': 'python', '.pyw': 'python', '.pyx': 'python', '.pyi': 'python',
            '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript', '.cjs': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.hxx': 'cpp', '.h': 'c', '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin', '.kts': 'kotlin',
            '.scala': 'scala',
            '.dart': 'dart',
            '.r': 'r', '.R': 'r',
            '.m': 'matlab',
            '.pl': 'perl', '.pm': 'perl',
            '.sh': 'bash', '.bash': 'bash',
            '.ps1': 'powershell',
            '.sql': 'sql',
        }
        
        return language_map.get(ext_lower)
    
    def _is_function_definition(self, line: str, language: str) -> bool:
        """Check if a line contains a function definition based on language"""
        line = line.strip()
        
        if language == 'python':
            return line.startswith('def ') or line.startswith('async def ')
        elif language == 'go':
            return line.startswith('func ')
        elif language in ['javascript', 'typescript']:
            return (line.startswith('function ') or 
                   line.startswith('export function ') or
                   '= function' in line or
                   '= (' in line or
                   ': (' in line)
        elif language == 'java':
            return (line.startswith('public ') or 
                   line.startswith('private ') or 
                   line.startswith('protected ')) and '(' in line
        elif language in ['cpp', 'c']:
            return '(' in line and not line.startswith('#') and not line.startswith('//')
        elif language == 'csharp':
            return (line.startswith('public ') or 
                   line.startswith('private ') or 
                   line.startswith('protected ') or
                   line.startswith('internal ')) and '(' in line
        elif language == 'rust':
            return line.startswith('fn ') or line.startswith('pub fn ')
        elif language == 'php':
            return line.startswith('function ') or line.startswith('public function ')
        elif language == 'ruby':
            return line.startswith('def ')
        elif language == 'swift':
            return line.startswith('func ') or line.startswith('public func ')
        elif language == 'kotlin':
            return line.startswith('fun ') or line.startswith('public fun ')
        elif language == 'scala':
            return line.startswith('def ') or line.startswith('private def ')
        elif language == 'dart':
            return line.startswith('void ') or line.startswith('String ') or line.startswith('int ') or line.startswith('bool ')
        elif language == 'r':
            return line.startswith('function(') or '<-' in line
        elif language == 'matlab':
            return line.startswith('function ')
        elif language == 'perl':
            return line.startswith('sub ')
        elif language == 'bash':
            return line.startswith('function ') or line.startswith('()')
        elif language == 'powershell':
            return line.startswith('function ') or line.startswith('param(')
        elif language == 'sql':
            return line.startswith('CREATE ') or line.startswith('INSERT ') or line.startswith('SELECT ')
        
        # Default fallback - look for common patterns
        return '(' in line and not line.startswith('#') and not line.startswith('//')
    
    def _extract_function_name(self, line: str, language: str) -> Optional[str]:
        """Extract function name from function definition line based on language"""
        line = line.strip()
        
        if language == 'python':
            match = re.match(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'go':
            match = re.match(r'^\s*func\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language in ['javascript', 'typescript']:
            # Handle various JS/TS function patterns
            patterns = [
                r'^\s*(?:export\s+)?function\s+(\w+)\s*\(',
                r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(',
                r'^\s*(?:export\s+)?(\w+)\s*:\s*(?:async\s+)?\(',
            ]
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    return match.group(1)
            return None
        elif language == 'java':
            match = re.match(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:<[^>]+>\s+)?(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language in ['cpp', 'c']:
            # Handle C/C++ function patterns
            patterns = [
                r'^\s*(?:template\s*<[^>]*>\s*)?(?:inline\s+)?(?:static\s+)?(?:const\s+)?(?:virtual\s+)?(?:explicit\s+)?(?:friend\s+)?(?:constexpr\s+)?(?:noexcept\s*\([^)]*\)\s*)?(?:<[^>]+>\s+)?(\w+)\s*\(',
                r'^\s*(?:int|void|char|float|double|bool|auto|template\s*<[^>]*>)\s+(\w+)\s*\(',
            ]
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    return match.group(1)
            return None
        elif language == 'csharp':
            match = re.match(r'^\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:virtual\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:override\s+)?(?:readonly\s+)?(?:const\s+)?(?:async\s+)?(?:<[^>]+>\s+)?(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'rust':
            match = re.match(r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'php':
            match = re.match(r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:abstract\s+)?function\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'ruby':
            match = re.match(r'^\s*def\s+(\w+)', line)
            return match.group(1) if match else None
        elif language == 'swift':
            match = re.match(r'^\s*(?:public|private|internal|fileprivate)?\s*(?:static\s+)?(?:mutating\s+)?func\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'kotlin':
            match = re.match(r'^\s*(?:public|private|protected|internal)?\s*(?:open\s+)?(?:suspend\s+)?fun\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'scala':
            match = re.match(r'^\s*(?:private|protected)?\s*(?:final\s+)?(?:def\s+)(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'dart':
            match = re.match(r'^\s*(?:void|String|int|bool|double|num|List|Map|Set)\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        elif language == 'r':
            match = re.match(r'^\s*(\w+)\s*<-\s*function', line)
            return match.group(1) if match else None
        elif language == 'matlab':
            match = re.match(r'^\s*function\s+(\w+)', line)
            return match.group(1) if match else None
        elif language == 'perl':
            match = re.match(r'^\s*sub\s+(\w+)', line)
            return match.group(1) if match else None
        elif language == 'bash':
            match = re.match(r'^\s*(\w+)\s*\(\)', line)
            return match.group(1) if match else None
        elif language == 'powershell':
            match = re.match(r'^\s*function\s+(\w+)', line)
            return match.group(1) if match else None
        elif language == 'sql':
            # For SQL, we might not have traditional functions, but could have procedures
            match = re.match(r'^\s*CREATE\s+(?:PROCEDURE|FUNCTION)\s+(\w+)', line, re.IGNORECASE)
            return match.group(1) if match else None
        
        # Default fallback - try to extract any word before parentheses
        match = re.match(r'^\s*(\w+)\s*\(', line)
        return match.group(1) if match else None
    
    def _extract_function_code(self, added_lines: List[Tuple[int, str]], start_line: int, language: str) -> str:
        """Extract function code based on language-specific patterns"""
        function_lines = []
        
        if language == 'python':
            # Python uses indentation
            indent_level = None
            for line_num, line in added_lines:
                if line_num >= start_line:
                    if indent_level is None:
                        indent_level = len(line) - len(line.lstrip())
                    
                    if line.strip() and len(line) - len(line.lstrip()) <= indent_level and line_num > start_line:
                        break
                    
                    function_lines.append(line)
        else:
            # For C-style languages, use brace counting
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
    
    def generate_documentation(self, function_code: str, function_name: str, diff_context: str = "", language: str = "python") -> str:
        """Generate comprehensive documentation for a test file in any programming language"""
        try:
            # Create language-specific prompts
            if language == "python":
                code_block = f"```python\n{function_code}\n```"
                test_framework = "pytest, unittest, nose"
                run_command = "pytest -v"
            elif language == "go":
                code_block = f"```go\n{function_code}\n```"
                test_framework = "testing, testify, gomock"
                run_command = "go test -v"
            elif language in ["javascript", "typescript"]:
                code_block = f"```{language}\n{function_code}\n```"
                test_framework = "jest, mocha, jasmine, tape, ava"
                run_command = "npm test" if language == "javascript" else "npm run test"
            elif language == "java":
                code_block = f"```java\n{function_code}\n```"
                test_framework = "junit, testng, mockito, powermock"
                run_command = "mvn test"
            elif language in ["cpp", "c"]:
                code_block = f"```{language}\n{function_code}\n```"
                test_framework = "gtest, catch2, boost.test, cppunit"
                run_command = "make test" if language == "cpp" else "make test"
            elif language == "csharp":
                code_block = f"```csharp\n{function_code}\n```"
                test_framework = "nunit, xunit, mstest, moq"
                run_command = "dotnet test"
            elif language == "rust":
                code_block = f"```rust\n{function_code}\n```"
                test_framework = "test, mockall, mockiato"
                run_command = "cargo test"
            elif language == "php":
                code_block = f"```php\n{function_code}\n```"
                test_framework = "phpunit, codeception, pest"
                run_command = "vendor/bin/phpunit"
            elif language == "ruby":
                code_block = f"```ruby\n{function_code}\n```"
                test_framework = "rspec, minitest, test-unit"
                run_command = "bundle exec rspec"
            elif language == "swift":
                code_block = f"```swift\n{function_code}\n```"
                test_framework = "xctest, quick, nimble"
                run_command = "swift test"
            elif language == "kotlin":
                code_block = f"```kotlin\n{function_code}\n```"
                test_framework = "junit, kotlin.test, mockk"
                run_command = "gradle test"
            elif language == "scala":
                code_block = f"```scala\n{function_code}\n```"
                test_framework = "scalatest, specs2, scalacheck"
                run_command = "sbt test"
            elif language == "dart":
                code_block = f"```dart\n{function_code}\n```"
                test_framework = "test"
                run_command = "dart test"
            elif language == "r":
                code_block = f"```r\n{function_code}\n```"
                test_framework = "testthat"
                run_command = "Rscript -e 'devtools::test()'"
            elif language == "matlab":
                code_block = f"```matlab\n{function_code}\n```"
                test_framework = "matlab.unittest"
                run_command = "matlab -batch 'runtests'"
            elif language == "perl":
                code_block = f"```perl\n{function_code}\n```"
                test_framework = "Test::More, Test::Simple"
                run_command = "perl -MTest::More -e 'runtests'"
            elif language == "bash":
                code_block = f"```bash\n{function_code}\n```"
                test_framework = "bats, shunit2"
                run_command = "bats test.sh"
            elif language == "powershell":
                code_block = f"```powershell\n{function_code}\n```"
                test_framework = "Pester"
                run_command = "Invoke-Pester"
            elif language == "sql":
                code_block = f"```sql\n{function_code}\n```"
                test_framework = "dbunit, testcontainers"
                run_command = "mvn test"  # Assuming Maven for SQL testing
            else:
                # Generic fallback for unknown languages
                code_block = f"```\n{function_code}\n```"
                test_framework = "standard testing framework"
                run_command = "run tests using appropriate test runner"
            
            # Create a detailed prompt for comprehensive documentation
            prompt = f"""You are a technical documentation expert. Create comprehensive documentation for this {language.capitalize()} test file.

CRITICAL: Analyze the actual test code and provide specific, detailed explanations based on what the code actually does.

Test Code:
{code_block}

Generate a complete markdown documentation file with the following structure:

# Test File Documentation: {function_name}

## Overview
Analyze the test code and explain:
- What specific functionality is being tested
- What the main purpose of these tests is
- What business logic or features are being validated

## Individual Test Functions
For EACH test function in the code, provide:
- Function name and signature
- Specific purpose and what it validates
- Input parameters and test data used
- Expected outcomes and assertions
- Any mocking or setup required

## Test Strategy and Coverage
Based on the actual test code, explain:
- What types of scenarios are covered (happy path, edge cases, errors)
- What specific business rules are being validated
- What parts of the system are being tested

## Technical Details
- Required imports and their purposes
- Test framework being used ({test_framework})
- Any mock objects and why they're needed
- Test data and fixtures used

## Running and Debugging
- Exact command to run these tests: `{run_command}`
- Prerequisites and environment setup
- How to debug failures
- Common issues and solutions

## Code Structure Analysis
- How the tests are organized
- Naming conventions used
- Test patterns and best practices followed

Generate detailed, specific explanations based on the actual code provided. Avoid generic statements - focus on what this specific test file actually does."""
            
            # Use the LLM to generate comprehensive documentation
            messages = [{"role": "user", "content": prompt}]
            return self.llm.generate(messages, max_new_tokens=2048)
            
        except Exception as e:
            logging.error(f"Error generating comprehensive documentation for {function_name}: {e}")
            return f"# Error generating documentation: {str(e)}"
    
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