import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class LanguageDetector:
    """Detects programming languages from file extensions and content patterns."""
    
    # Language to file extension mappings
    LANGUAGE_EXTENSIONS = {
        'python': ['.py', '.pyw', '.pyx', '.pyi'],
        'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hxx', '.h', '.cc'],
        'c': ['.c', '.h'],
        'csharp': ['.cs'],
        'go': ['.go'],
        'rust': ['.rs'],
        'php': ['.php'],
        'ruby': ['.rb'],
        'swift': ['.swift'],
        'kotlin': ['.kt', '.kts'],
        'scala': ['.scala'],
        'dart': ['.dart'],
        'r': ['.r', '.R'],
        'matlab': ['.m'],
        'perl': ['.pl', '.pm'],
        'bash': ['.sh', '.bash'],
        'powershell': ['.ps1'],
        'sql': ['.sql'],
        'html': ['.html', '.htm'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'yaml': ['.yml', '.yaml'],
        'json': ['.json'],
        'xml': ['.xml'],
        'markdown': ['.md', '.markdown'],
        'dockerfile': ['Dockerfile', '.dockerfile'],
        'makefile': ['Makefile', 'makefile', '.mk'],
        'cmake': ['CMakeLists.txt', '.cmake'],
        'gradle': ['build.gradle', 'build.gradle.kts'],
        'maven': ['pom.xml'],
        'npm': ['package.json'],
        'cargo': ['Cargo.toml'],
        'go_mod': ['go.mod'],
        'requirements': ['requirements.txt', 'setup.py', 'pyproject.toml'],
    }
    
    # Reverse mapping for quick lookup
    EXTENSION_TO_LANGUAGE = {}
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        for ext in exts:
            EXTENSION_TO_LANGUAGE[ext.lower()] = lang
    
    # Language-specific function patterns
    FUNCTION_PATTERNS = {
        'python': [
            r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
            r'^\s*class\s+(\w+)',
        ],
        'javascript': [
            r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function',
            r'^\s*(?:export\s+)?(\w+)\s*:\s*(?:async\s+)?\(',
            r'^\s*(?:describe|it|test|beforeEach|afterEach|beforeAll|afterAll)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'^\s*(?:describe|it|test|beforeEach|afterEach|beforeAll|afterAll)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*(?:async\s+)?\(',
        ],
        'typescript': [
            r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*:\s*(?:async\s+)?\(',
            r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(',
            r'^\s*(?:export\s+)?(\w+)\s*:\s*(?:async\s+)?\(',
            r'^\s*(?:export\s+)?(?:public|private|protected)?\s*(?:static\s+)?(\w+)\s*\(',
            r'^\s*(?:describe|it|test|beforeEach|afterEach|beforeAll|afterAll)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'^\s*(?:describe|it|test|beforeEach|afterEach|beforeAll|afterAll)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*(?:async\s+)?\(',
        ],
        'java': [
            r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:<[^>]+>\s+)?(\w+)\s*\(',
            r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:abstract\s+)?class\s+(\w+)',
            r'^\s*(?:@Test|@Before|@After|@BeforeClass|@AfterClass)\s*\n\s*(?:public\s+)?(?:static\s+)?(?:void|String|int|boolean|long|double|float)\s+(\w+)\s*\(',
            r'^\s*(?:public\s+)?(?:static\s+)?(?:void|String|int|boolean|long|double|float)\s+(\w+)\s*\(\s*\)\s*\{',
        ],
        'cpp': [
            r'^\s*(?:template\s*<[^>]*>\s*)?(?:inline\s+)?(?:static\s+)?(?:const\s+)?(?:virtual\s+)?(?:explicit\s+)?(?:friend\s+)?(?:constexpr\s+)?(?:noexcept\s*\([^)]*\)\s*)?(?:<[^>]+>\s+)?(\w+)\s*\(',
            r'^\s*(?:template\s*<[^>]*>\s*)?(?:class|struct|union)\s+(\w+)',
            r'^\s*(?:int|void|char|float|double|bool|auto|template\s*<[^>]*>)\s+(\w+)\s*\(',
            r'^\s*(?:TEST|TEST_F|TEST_P)\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)',
            r'^\s*(?:TEST|TEST_F|TEST_P)\s*\(\s*(\w+)\s*\)',
        ],
        'c': [
            r'^\s*(?:static\s+)?(?:inline\s+)?(?:const\s+)?(\w+)\s*\(',
            r'^\s*(?:struct|union|enum)\s+(\w+)',
        ],
        'csharp': [
            r'^\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:virtual\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:override\s+)?(?:readonly\s+)?(?:const\s+)?(?:async\s+)?(?:<[^>]+>\s+)?(\w+)\s*\(',
            r'^\s*(?:public|private|protected|internal)?\s*(?:static\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:partial\s+)?class\s+(\w+)',
        ],
        'go': [
            r'^\s*func\s+(\w+)\s*\(',
            r'^\s*func\s*\(\s*\w+\s+\w+\s*\)\s*(\w+)\s*\(',
            r'^\s*func\s*\(\s*\w+\s+\w+\s*\)\s*(\w+)\s*\([^)]*\)\s*[^{]*{',
            r'^\s*type\s+(\w+)\s+',
            r'^\s*func\s+Test(\w+)\s*\(',
        ],
        'rust': [
            r'^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(',
            r'^\s*(?:pub\s+)?(?:struct|enum|trait|impl)\s+(\w+)',
        ],
        'php': [
            r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:abstract\s+)?function\s+(\w+)\s*\(',
            r'^\s*(?:abstract\s+)?(?:final\s+)?class\s+(\w+)',
        ],
        'ruby': [
            r'^\s*def\s+(\w+)',
            r'^\s*class\s+(\w+)',
        ],
        'swift': [
            r'^\s*(?:public|private|internal|fileprivate)?\s*(?:static\s+)?(?:class|struct|enum)\s+(\w+)',
            r'^\s*(?:public|private|internal|fileprivate)?\s*(?:static\s+)?(?:mutating\s+)?func\s+(\w+)\s*\(',
            r'^\s*(?:public|private|internal|fileprivate)?\s*(?:static\s+)?(?:class|struct|enum)\s+(\w+)\s*:\s*',
        ],
        'kotlin': [
            r'^\s*(?:public|private|protected|internal)?\s*(?:open\s+)?(?:data\s+)?(?:sealed\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)',
            r'^\s*(?:public|private|protected|internal)?\s*(?:open\s+)?(?:suspend\s+)?fun\s+(\w+)\s*\(',
        ],
        'scala': [
            r'^\s*(?:private|protected)?\s*(?:final\s+)?(?:sealed\s+)?(?:abstract\s+)?(?:case\s+)?class\s+(\w+)',
            r'^\s*(?:private|protected)?\s*(?:final\s+)?(?:def\s+)(\w+)\s*\(',
            r'^\s*(?:private|protected)?\s*(?:final\s+)?(?:sealed\s+)?(?:abstract\s+)?(?:case\s+)?class\s+(\w+)\s*[\(:]',
        ],
    }
    
    # Test framework mappings
    TEST_FRAMEWORKS = {
        'python': ['pytest', 'unittest', 'nose'],
        'javascript': ['jest', 'mocha', 'jasmine', 'tape', 'ava'],
        'typescript': ['jest', 'mocha', 'jasmine', 'tape', 'ava'],
        'java': ['junit', 'testng', 'mockito', 'powermock'],
        'cpp': ['gtest', 'catch2', 'boost.test', 'cppunit'],
        'c': ['unity', 'cmocka', 'cunit'],
        'csharp': ['nunit', 'xunit', 'mstest', 'moq'],
        'go': ['testing', 'testify', 'gomock'],
        'rust': ['test', 'mockall', 'mockiato'],
        'php': ['phpunit', 'codeception', 'pest'],
        'ruby': ['rspec', 'minitest', 'test-unit'],
        'swift': ['xctest', 'quick', 'nimble'],
        'kotlin': ['junit', 'kotlin.test', 'mockk'],
        'scala': ['scalatest', 'specs2', 'scalacheck'],
    }
    
    @classmethod
    def detect_language_from_file(cls, file_path: str) -> Optional[str]:
        """Detect programming language from file path."""
        if not file_path:
            return None
            
        # Handle special files first
        filename = os.path.basename(file_path)
        if filename in cls.LANGUAGE_EXTENSIONS.get('dockerfile', []):
            return 'dockerfile'
        if filename in cls.LANGUAGE_EXTENSIONS.get('makefile', []):
            return 'makefile'
        if filename in cls.LANGUAGE_EXTENSIONS.get('cmake', []):
            return 'cmake'
        if filename in cls.LANGUAGE_EXTENSIONS.get('gradle', []):
            return 'gradle'
        if filename in cls.LANGUAGE_EXTENSIONS.get('maven', []):
            return 'maven'
        if filename in cls.LANGUAGE_EXTENSIONS.get('npm', []):
            return 'npm'
        if filename in cls.LANGUAGE_EXTENSIONS.get('cargo', []):
            return 'cargo'
        if filename in cls.LANGUAGE_EXTENSIONS.get('go_mod', []):
            return 'go_mod'
        if filename in cls.LANGUAGE_EXTENSIONS.get('requirements', []):
            return 'requirements'
        
        # Check file extensions
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        
        return cls.EXTENSION_TO_LANGUAGE.get(ext_lower)
    
    @classmethod
    def detect_language_from_content(cls, content: str, file_path: str = None) -> Optional[str]:
        """Detect programming language from file content."""
        if not content:
            return None
            
        # Try file extension first if available
        if file_path:
            lang_from_ext = cls.detect_language_from_file(file_path)
            if lang_from_ext:
                return lang_from_ext
        
        # Content-based detection
        content_lower = content.lower()
        
        # Check for language-specific patterns
        for lang, patterns in cls.FUNCTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return lang
        
        # Check for shebang
        if content.startswith('#!/'):
            shebang = content.split('\n')[0].lower()
            if 'python' in shebang:
                return 'python'
            elif 'node' in shebang or 'js' in shebang:
                return 'javascript'
            elif 'bash' in shebang or 'sh' in shebang:
                return 'bash'
            elif 'perl' in shebang:
                return 'perl'
            elif 'ruby' in shebang:
                return 'ruby'
        
        # Check for HTML/XML
        if re.search(r'<!DOCTYPE\s+html|<html|<head|<body', content, re.IGNORECASE):
            return 'html'
        if re.search(r'<\?xml|<root|<element', content, re.IGNORECASE):
            return 'xml'
        
        # Check for JSON
        if content.strip().startswith('{') or content.strip().startswith('['):
            try:
                import json
                json.loads(content)
                return 'json'
            except:
                pass
        
        # Check for YAML
        if re.search(r'^---\s*$|^[a-zA-Z_][a-zA-Z0-9_]*\s*:', content, re.MULTILINE):
            return 'yaml'
        
        # Check for Markdown
        if re.search(r'^#\s+|^##\s+|^###\s+|^\[.*\]\(.*\)', content, re.MULTILINE):
            return 'markdown'
        
        return None
    
    @classmethod
    def get_function_patterns_for_language(cls, language: str) -> List[str]:
        """Get function detection patterns for a specific language."""
        return cls.FUNCTION_PATTERNS.get(language.lower(), [])
    
    @classmethod
    def get_test_frameworks_for_language(cls, language: str) -> List[str]:
        """Get available test frameworks for a specific language."""
        return cls.TEST_FRAMEWORKS.get(language.lower(), [])
    
    @classmethod
    def get_file_extension_for_language(cls, language: str, file_path: str = None) -> str:
        """Get the primary file extension for a language."""
        # If we have a file path, try to preserve the original extension for special cases
        if file_path and '.' in file_path:
            original_ext = '.' + file_path.lower().split('.')[-1]
            # Check if this is a special extension that should be preserved
            special_extensions = ['.tsx', '.jsx', '.h', '.hpp', '.hxx', '.cc', '.cxx']
            if original_ext in special_extensions:
                return original_ext
        
        # First try to get extension from language name
        extensions = cls.LANGUAGE_EXTENSIONS.get(language.lower(), [])
        if extensions:
            return extensions[0]
        
        # If language is actually a file extension, try to map it to a language
        if language.startswith('.'):
            language = language[1:]  # Remove the dot
        
        # Map common extensions to languages
        extension_to_language = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',  # Add tsx support
            'jsx': 'javascript',  # Add jsx support
            'java': 'java',
            'cpp': 'cpp',
            'cc': 'cpp',  # Add cc support
            'cxx': 'cpp',  # Add cxx support
            'hpp': 'cpp',  # Add hpp support
            'hxx': 'cpp',  # Add hxx support
            'c': 'c',
            'h': 'cpp',  # Add header file support
            'cs': 'csharp',
            'go': 'go',
            'rs': 'rust',
            'php': 'php',
            'rb': 'ruby',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
            'dart': 'dart',
            'r': 'r',
            'm': 'matlab',
            'pl': 'perl',
            'sh': 'bash',
            'ps1': 'powershell',
            'sql': 'sql',
            'html': 'html',
            'css': 'css',
            'yml': 'yaml',
            'yaml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'md': 'markdown',
            'markdown': 'markdown',
        }
        
        # Try to get the language from the extension
        if language in extension_to_language:
            mapped_language = extension_to_language[language]
            extensions = cls.LANGUAGE_EXTENSIONS.get(mapped_language, [])
            if extensions:
                # For special cases like tsx, jsx, h, cc, cxx, hpp, hxx return the original extension
                if language in ['tsx', 'jsx', 'h', 'cc', 'cxx', 'hpp', 'hxx']:
                    return f'.{language}'
                return extensions[0]
        
        # Default fallback - but try to be smarter about it
        if language.lower() in ['cpp', 'c++']:
            return '.cpp'
        elif language.lower() in ['c']:
            return '.c'
        elif language.lower() in ['java']:
            return '.java'
        elif language.lower() in ['go']:
            return '.go'
        elif language.lower() in ['python', 'py']:
            return '.py'
        elif language.lower() in ['javascript', 'js']:
            return '.js'
        elif language.lower() in ['typescript', 'ts']:
            return '.ts'
        
        return '.txt'
    
    @classmethod
    def get_language_from_extension(cls, file_path: str) -> str:
        """Get language name from file extension."""
        if not file_path or '.' not in file_path:
            return 'unknown'
        
        ext = file_path.lower().split('.')[-1]
        
        # Map extensions to language names
        extension_to_language = {
            'py': 'python',
            'pyw': 'python',
            'pyx': 'python',
            'pyi': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'mjs': 'javascript',
            'cjs': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'java': 'java',
            'cpp': 'cpp',
            'cc': 'cpp',
            'cxx': 'cpp',
            'hpp': 'cpp',
            'hxx': 'cpp',
            'h': 'cpp',
            'c': 'c',
            'cs': 'csharp',
            'go': 'go',
            'rs': 'rust',
            'php': 'php',
            'rb': 'ruby',
            'swift': 'swift',
            'kt': 'kotlin',
            'kts': 'kotlin',
            'scala': 'scala',
            'dart': 'dart',
            'r': 'r',
            'R': 'r',
            'm': 'matlab',
            'pl': 'perl',
            'pm': 'perl',
            'sh': 'bash',
            'bash': 'bash',
            'ps1': 'powershell',
            'sql': 'sql',
            'html': 'html',
            'htm': 'html',
            'css': 'css',
            'scss': 'css',
            'sass': 'css',
            'less': 'css',
            'yml': 'yaml',
            'yaml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'md': 'markdown',
            'markdown': 'markdown',
            'dockerfile': 'dockerfile',
            'mk': 'makefile',
            'cmake': 'cmake',
            'gradle': 'gradle',
            'kts': 'gradle',
            'xml': 'maven',
            'toml': 'cargo',
            'mod': 'go_mod',
            'txt': 'requirements',
            'cfg': 'requirements',
            'ini': 'requirements',
        }
        
        return extension_to_language.get(ext, 'unknown')
    
    @classmethod
    def is_supported_language(cls, language: str) -> bool:
        """Check if a language is supported."""
        return language.lower() in cls.LANGUAGE_EXTENSIONS
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """Get list of all supported languages."""
        return list(cls.LANGUAGE_EXTENSIONS.keys())
