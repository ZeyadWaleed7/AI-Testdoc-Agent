import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

class EnhancedContextLoader:
    """Loads enhanced context data from the new extraction format"""
    
    def __init__(self, pr_data_path: str):
        self.pr_data_path = Path(pr_data_path)
        self.enhanced_patches = {}
        self.file_patches = {}
        self.context_summary = {}
        self.test_patterns = {}
        self.pr_metadata = {}
        self.file_list = []
        self.diff_patch = ""
        
        self._load_all_context()
    
    def _load_all_context(self):
        """Load all context files from the PR data directory"""
        try:
            # Load enhanced patches (main source of context)
            enhanced_patches_path = self.pr_data_path / "enhanced_patches.json"
            if enhanced_patches_path.exists():
                with open(enhanced_patches_path, 'r', encoding='utf-8') as f:
                    self.enhanced_patches = json.load(f)
            
            # Load file patches
            file_patches_path = self.pr_data_path / "file_patches.json"
            if file_patches_path.exists():
                with open(file_patches_path, 'r', encoding='utf-8') as f:
                    self.file_patches = json.load(f)
            
            # Load context summary
            context_summary_path = self.pr_data_path / "context_summary.json"
            if context_summary_path.exists():
                with open(context_summary_path, 'r', encoding='utf-8') as f:
                    self.context_summary = json.load(f)
            
            # Load test patterns
            test_patterns_path = self.pr_data_path / "test_patterns.json"
            if test_patterns_path.exists():
                with open(test_patterns_path, 'r', encoding='utf-8') as f:
                    self.test_patterns = json.load(f)
            
            # Load PR metadata
            pr_metadata_path = self.pr_data_path / "pr_metadata.json"
            if pr_metadata_path.exists():
                with open(pr_metadata_path, 'r', encoding='utf-8') as f:
                    self.pr_metadata = json.load(f)
            
            # Load file list
            file_list_path = self.pr_data_path / "file_list.txt"
            if file_list_path.exists():
                with open(file_list_path, 'r', encoding='utf-8') as f:
                    self.file_list = [line.strip() for line in f.readlines() if line.strip()]
            
            # Load diff.patch
            diff_patch_path = self.pr_data_path / "diff.patch"
            if diff_patch_path.exists():
                with open(diff_patch_path, 'r', encoding='utf-8') as f:
                    self.diff_patch = f.read()
                    
        except Exception as e:
            print(f"Error loading enhanced context: {e}")
    
    def get_source_files(self) -> List[str]:
        """Get source files (non-test files that were changed)"""
        source_files = []
        for filename, patch_data in self.enhanced_patches.items():
            if not patch_data.get('is_test_file', False):
                source_files.append(filename)
        return source_files
    
    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive context for a specific file"""
        if file_path in self.enhanced_patches:
            return self.enhanced_patches[file_path]
        return {}
    
    def get_file_language(self, file_path: str) -> Optional[str]:
        """Get the programming language of a file"""
        file_context = self.get_file_context(file_path)
        return file_context.get('language')
    
    def get_pr_title(self) -> str:
        """Get the PR title"""
        return self.pr_metadata.get('title', 'Unknown PR')
    
    def get_languages_in_pr(self) -> List[str]:
        """Get all programming languages found in the PR"""
        languages = set()
        for patch_data in self.enhanced_patches.values():
            if 'language' in patch_data:
                languages.add(patch_data['language'])
        return list(languages)
    
    def get_test_patterns_for_language(self, language: str) -> List[Dict[str, Any]]:
        """Get test patterns for a specific language"""
        if language in self.test_patterns:
            return self.test_patterns[language]
        return []
    
    def get_imports_for_file(self, file_path: str) -> List[str]:
        """Get imports for a specific file"""
        file_context = self.get_file_context(file_path)
        return file_context.get('imports', [])
    
    def get_full_context_for_prompt(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive context data for prompt generation"""
        file_context = self.get_file_context(file_path)
        language = file_context.get('language', 'unknown')
        
        # Get repository structure and dependencies
        repo_structure = self._get_repository_structure()
        dependencies = self._get_dependencies_for_language(language)
        related_files = self._get_related_files(file_path, language)
        
        # Get actual file contents and imports
        actual_file_content = self._get_actual_file_content(file_path)
        actual_imports = self._extract_actual_imports(actual_file_content, language)
        
        # PRIORITIZE imports from enhanced_patches.json over extracted imports
        # This ensures we use the exact imports that were detected during the PR analysis
        enhanced_imports = file_context.get('imports', [])
        if enhanced_imports:
            # Use the imports from enhanced_patches.json as they are more accurate
            final_imports = enhanced_imports
        else:
            # Fallback to extracted imports if enhanced_patches.json doesn't have imports
            final_imports = actual_imports
        
        # Get test framework information
        test_frameworks = self._get_test_frameworks_for_language(language)
        
        # Get build and environment info
        build_config = self._get_build_configuration()
        environment_info = self._get_environment_info(language)
        
        # Get existing test patterns from the repository
        test_patterns = self._get_existing_test_patterns(language)
        
        return {
            'pr_title': self.get_pr_title(),
            'pr_description': self.pr_metadata.get('description', ''),
            'file_path': file_path,
            'language': language,
            'imports': final_imports,  # Use prioritized imports
            'full_content': actual_file_content,
            'patch': file_context.get('patch', ''),
            'file_patch': file_context.get('file_patch', ''),
            'diff_patch': self.diff_patch,
            'context_summary': self.context_summary,
            'all_file_patches': self.file_patches,
            'test_patterns': test_patterns,
            'repository_structure': repo_structure,
            'dependencies': dependencies,
            'related_files': related_files,
            'test_frameworks': test_frameworks,
            'build_config': build_config,
            'environment_info': environment_info,
            'actual_file_content': actual_file_content,
            'working_directory': self._get_working_directory(),
            'package_manager': self._get_package_manager(language),
            'test_command': self._get_test_command(language),
            'import_paths': self._get_import_paths(file_path, language)
        }
    
    def _get_repository_structure(self) -> Dict[str, Any]:
        """Get repository structure information"""
        structure = {
            'root_files': [],
            'directories': [],
            'language_files': {}
        }
        
        try:
            # Look for common repository files
            root_files = ['README.md', 'requirements.txt', 'setup.py', 'pyproject.toml', 
                         'package.json', 'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
                         'CMakeLists.txt', 'Makefile', '.gitignore', 'Dockerfile']
            
            for file in root_files:
                if (self.pr_data_path.parent / file).exists():
                    structure['root_files'].append(file)
            
            # Look for language-specific directories
            lang_dirs = ['src', 'lib', 'tests', 'test', 'examples', 'docs', 'scripts']
            for dir_name in lang_dirs:
                if (self.pr_data_path.parent / dir_name).exists():
                    structure['directories'].append(dir_name)
                    
        except Exception as e:
            print(f"Error getting repository structure: {e}")
        
        return structure
    
    def _get_dependencies_for_language(self, language: str) -> Dict[str, Any]:
        """Get dependencies for a specific language"""
        dependencies = {
            'packages': [],
            'frameworks': [],
            'tools': []
        }
        
        try:
            if language == 'python':
                # Look for Python dependency files
                req_files = ['requirements.txt', 'setup.py', 'pyproject.toml']
                for req_file in req_files:
                    req_path = self.pr_data_path.parent / req_file
                    if req_path.exists():
                        with open(req_path, 'r') as f:
                            content = f.read()
                            # Extract package names (simplified)
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#') and '==' in line:
                                    pkg = line.split('==')[0].strip()
                                    dependencies['packages'].append(pkg)
                                elif line and not line.startswith('#') and line.startswith(('pytest', 'unittest', 'nose')):
                                    dependencies['frameworks'].append(line.strip())
            
            elif language == 'javascript':
                # Look for Node.js dependencies
                package_path = self.pr_data_path.parent / 'package.json'
                if package_path.exists():
                    import json
                    with open(package_path, 'r') as f:
                        pkg_data = json.load(f)
                        if 'dependencies' in pkg_data:
                            dependencies['packages'].extend(list(pkg_data['dependencies'].keys()))
                        if 'devDependencies' in pkg_data:
                            dependencies['packages'].extend(list(pkg_data['devDependencies'].keys()))
                            
            elif language == 'go':
                # Look for Go dependencies
                go_mod_path = self.pr_data_path.parent / 'go.mod'
                if go_mod_path.exists():
                    with open(go_mod_path, 'r') as f:
                        content = f.read()
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('require '):
                                pkg = line.strip().split(' ')[1]
                                dependencies['packages'].append(pkg)
                                
        except Exception as e:
            print(f"Error getting dependencies for {language}: {e}")
        
        return dependencies
    
    def _get_related_files(self, file_path: str, language: str) -> List[str]:
        """Get related files that might be needed for testing"""
        related = []
        
        try:
            # Look for files in the same directory
            file_dir = file_path.rsplit('/', 1)[0] if '/' in file_path else '.'
            
            # Look for test files, config files, etc.
            for filename, patch_data in self.enhanced_patches.items():
                if filename.startswith(file_dir) and filename != file_path:
                    related.append(filename)
                    
            # Look for common related files
            base_name = file_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            common_patterns = [
                f"{base_name}_test.{language}",
                f"test_{base_name}.{language}",
                f"{base_name}.config.{language}",
                f"{base_name}.conf",
                f"{base_name}.ini",
                f"{base_name}.yaml",
                f"{base_name}.yml"
            ]
            
            for pattern in common_patterns:
                if (self.pr_data_path.parent / pattern).exists():
                    related.append(pattern)
                    
        except Exception as e:
            print(f"Error getting related files: {e}")
        
        return related
    
    def _get_test_frameworks_for_language(self, language: str) -> List[str]:
        """Get available test frameworks for a language"""
        from .language_detector import LanguageDetector
        return LanguageDetector.get_test_frameworks_for_language(language)
    
    def _get_build_configuration(self) -> Dict[str, Any]:
        """Get build configuration information"""
        config = {
            'build_tools': [],
            'config_files': []
        }
        
        try:
            # Look for common build configuration files
            build_files = ['Makefile', 'CMakeLists.txt', 'build.gradle', 'pom.xml', 
                          'Cargo.toml', 'setup.py', 'pyproject.toml', 'package.json']
            
            for build_file in build_files:
                if (self.pr_data_path.parent / build_file).exists():
                    config['build_tools'].append(build_file)
                    config['config_files'].append(build_file)
                    
        except Exception as e:
            print(f"Error getting build configuration: {e}")
        
        return config
    
    def _get_environment_info(self, language: str) -> Dict[str, Any]:
        """Get environment information"""
        return {
            'python_version': '3.8+',  # Default assumption
            'node_version': '16+',     # Default assumption
            'go_version': '1.19+',     # Default assumption
            'rust_version': '1.70+',   # Default assumption
            'java_version': '11+',     # Default assumption
        }

    def _get_actual_file_content(self, file_path: str) -> str:
        """Get the actual content of the file being tested"""
        try:
            # Try to get from the original repository
            original_path = self._get_original_file_path(file_path)
            if original_path and os.path.exists(original_path):
                with open(original_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # Fallback to enhanced context
            file_context = self.get_file_context(file_path)
            return file_context.get('full_content', '')
        except Exception as e:
            logging.warning(f"Could not read actual file content for {file_path}: {e}")
            return ""
    
    def _extract_actual_imports(self, file_content: str, language: str) -> List[str]:
        """Extract actual imports from file content"""
        imports = []
        if not file_content:
            return imports
        
        lines = file_content.split('\n')
        for line in lines:
            line = line.strip()
            if language == 'python':
                if line.startswith(('import ', 'from ')) and not line.startswith('#'):
                    imports.append(line)
            elif language in ['javascript', 'typescript']:
                if line.startswith(('import ', 'const ', 'let ', 'var ')) and not line.startswith('//'):
                    imports.append(line)
            elif language in ['java']:
                if line.startswith('import ') and not line.startswith('//'):
                    imports.append(line)
            elif language in ['cpp', 'c']:
                if line.startswith('#include') and not line.startswith('//'):
                    imports.append(line)
            elif language in ['go']:
                if line.startswith(('import ', 'package ')) and not line.startswith('//'):
                    imports.append(line)
        
        return imports
    
    def _get_original_file_path(self, file_path: str) -> str:
        """Get the original file path in the repository"""
        # This would need to be implemented based on your repository structure
        # For now, return the file_path as is
        return file_path
    
    def _get_working_directory(self) -> str:
        """Get the working directory for the repository"""
        try:
            return os.getcwd()
        except:
            return "."
    
    def _get_package_manager(self, language: str) -> str:
        """Get the package manager for the language"""
        package_managers = {
            'python': 'pip',
            'javascript': 'npm',
            'typescript': 'npm',
            'go': 'go mod',
            'rust': 'cargo',
            'java': 'maven',
            'cpp': 'cmake',
            'c': 'make'
        }
        return package_managers.get(language, 'unknown')
    
    def _get_test_command(self, language: str) -> str:
        """Get the test command for the language"""
        test_commands = {
            'python': 'python -m pytest',
            'javascript': 'npm test',
            'typescript': 'npm test',
            'go': 'go test',
            'rust': 'cargo test',
            'java': 'mvn test',
            'cpp': 'make test',
            'c': 'make test'
        }
        return test_commands.get(language, 'unknown')
    
    def _get_import_paths(self, file_path: str, language: str) -> List[str]:
        """Get possible import paths for the file"""
        if not file_path:
            return []
        
        # Extract directory structure
        dir_parts = file_path.split('/')
        import_paths = []
        
        # Build relative import paths
        for i in range(len(dir_parts) - 1):
            relative_path = '/'.join(dir_parts[i:-1])
            if relative_path:
                import_paths.append(relative_path)
        
        # Add absolute paths
        import_paths.append('')
        import_paths.append('.')
        
        return import_paths

    def _get_existing_test_patterns(self, language: str) -> List[Dict[str, Any]]:
        """Get existing test patterns for a specific language from the repository"""
        try:
            # Look for existing test files in the repository
            test_patterns = []
            
            # Common test file patterns
            test_patterns_files = [
                f"test_*.{language}",
                f"*_test.{language}",
                f"tests/*.{language}",
                f"test/*.{language}"
            ]
            
            # Look for test files in the repository
            for pattern in test_patterns_files:
                try:
                    import glob
                    matches = glob.glob(str(self.pr_data_path.parent / pattern))
                    for match in matches[:5]:  # Limit to 5 examples
                        if os.path.exists(match):
                            with open(match, 'r', encoding='utf-8') as f:
                                content = f.read()
                                test_patterns.append({
                                    'file': match,
                                    'content': content[:1000],  # First 1000 chars
                                    'language': language
                                })
                except Exception as e:
                    logging.warning(f"Error reading test pattern {pattern}: {e}")
                    continue
            
            # If no patterns found, return empty list
            return test_patterns
            
        except Exception as e:
            logging.warning(f"Error getting test patterns for {language}: {e}")
            return []
