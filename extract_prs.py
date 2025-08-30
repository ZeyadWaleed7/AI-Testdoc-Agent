import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
DIFF_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}
PATCH_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.patch"
}

REPOS = [
    {"owner": "TheAlgorithms", "repo": "Java", "prs": [6504]},
]

BASE_OUTPUT_PATH = "data"
TEST_EXTENSIONS = [".py", ".cpp", ".c", ".js", ".ts", ".java", ".rb",".go"]
TEST_KEYWORDS = ["test", "spec", "Test", "_test"]

def get_language_from_extension(filename):
    """Map file extensions to proper language names"""
    if not filename or '.' not in filename:
        return 'unknown'
    
    ext = filename.lower().split('.')[-1]
    
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
        'h': 'c',
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

def get_file_content(owner, repo, path, ref="main"):
    """Get full file content for context"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        import base64
        content = response.json().get('content', '')
        return base64.b64decode(content).decode('utf-8')
    return None

def extract_imports_and_deps(file_content, language):
    """Extract imports/includes for context"""
    lines = file_content.split('\n')
    imports = []
    
    if language in ['python']:
        imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
    elif language in ['cpp', 'c']:
        imports = [line.strip() for line in lines if line.strip().startswith('#include')]
    elif language in ['java']:
        imports = [line.strip() for line in lines if line.strip().startswith('import ')]
    elif language in ['javascript', 'typescript']:
        imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'export '))]
    elif language in ['go']:
        imports = [line.strip() for line in lines if line.strip().startswith('import ')]
    elif language in ['rust']:
        imports = [line.strip() for line in lines if line.strip().startswith('use ')]
    elif language in ['php']:
        imports = [line.strip() for line in lines if line.strip().startswith(('use ', 'require ', 'include '))]
    elif language in ['ruby']:
        imports = [line.strip() for line in lines if line.strip().startswith(('require ', 'load '))]
    
    return imports[:10]  # Limit to first 10 imports

def is_test_file(filename):
    """Check if a file is a test file based on extension and keywords"""
    has_test_extension = any(ext in filename for ext in TEST_EXTENSIONS)
    has_test_keyword = any(keyword.lower() in filename.lower() for keyword in TEST_KEYWORDS)
    return has_test_extension and has_test_keyword

def save_test_file(filename, raw_url, test_path):
    """Download and save a test file"""
    try:
        test_content = requests.get(raw_url, headers=HEADERS).text
        file_name_only = os.path.basename(filename)
        
        # Get language for language-based organization
        lang = get_language_from_extension(filename)
        lang_path = os.path.join(test_path, lang)
        os.makedirs(lang_path, exist_ok=True)
        
        # Save the test file
        with open(os.path.join(lang_path, file_name_only), "w") as f:
            f.write(test_content)
        
        print(f"   💾 Saved test file: {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Error downloading test file {filename}: {e}")
        return False

def extract_data():
    for repo_info in REPOS:
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        prs = repo_info["prs"]

        for pr_number in prs:
            print(f"\n🔄 Extracting PR #{pr_number} from {owner}/{repo}")

            repo_dir = f"{owner}_{repo}"
            pr_path = os.path.join(BASE_OUTPUT_PATH, repo_dir, f"PR_{pr_number}")
            test_path = os.path.join(pr_path, "tests")
            context_path = os.path.join(pr_path, "context")
            os.makedirs(test_path, exist_ok=True)
            os.makedirs(context_path, exist_ok=True)

            # Get PR metadata
            pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            pr_response = requests.get(pr_url, headers=HEADERS)
            pr_data = pr_response.json() if pr_response.status_code == 200 else {}
            
            # Save PR metadata
            with open(os.path.join(pr_path, "pr_metadata.json"), "w") as f:
                json.dump({
                    "title": pr_data.get("title", ""),
                    "description": pr_data.get("body", ""),
                    "base_branch": pr_data.get("base", {}).get("ref", "main"),
                    "head_branch": pr_data.get("head", {}).get("ref", ""),
                }, f, indent=2)

            # Get changed files
            files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
            files_response = requests.get(files_url, headers=HEADERS)
            
            if files_response.status_code != 200:
                print(f"❌ Error getting files for PR #{pr_number}: {files_response.status_code}")
                continue

            try:
                file_list = files_response.json()
            except Exception as e:
                print(f"❌ Error parsing files response for PR #{pr_number}: {e}")
                continue

            # Enhanced file patches with context
            enhanced_patches = {}
            test_files_saved = 0
            
            for file in file_list:
                if not isinstance(file, dict) or 'filename' not in file:
                    continue

                filename = file['filename']
                language = get_language_from_extension(filename)
                
                # Get full file content for context
                full_content = get_file_content(owner, repo, filename, pr_data.get("head", {}).get("sha"))
                imports = extract_imports_and_deps(full_content or "", language) if full_content else []
                
                enhanced_patches[filename] = {
                    "status": file.get("status"),
                    "patch": file.get("patch", ""),
                    "additions": file.get("additions", 0),
                    "deletions": file.get("deletions", 0),
                    "changes": file.get("changes", 0),
                    "language": language,
                    "imports": imports,
                    "full_content": full_content[:2000] if full_content else None,  # First 2000 chars
                    "raw_url": file.get("raw_url"),
                    "is_test_file": is_test_file(filename)
                }
                
                # Save test files
                if is_test_file(filename) and file.get('raw_url'):
                    if save_test_file(filename, file.get('raw_url'), test_path):
                        test_files_saved += 1
                
                print(f"📄 Processed {filename} ({language})" + (" [TEST]" if is_test_file(filename) else ""))

            # Save enhanced patches
            with open(os.path.join(pr_path, "enhanced_patches.json"), "w") as f:
                json.dump(enhanced_patches, f, indent=2)

            # Save individual file patches (like the original script)
            file_patches = {}
            for filename, data in enhanced_patches.items():
                if data.get("patch"):
                    file_patches[filename] = data["patch"]
            
            with open(os.path.join(pr_path, "file_patches.json"), "w") as f:
                json.dump(file_patches, f, indent=2)

            # Save file list
            with open(os.path.join(pr_path, "file_list.txt"), "w") as f:
                for filename in enhanced_patches.keys():
                    f.write(filename + "\n")

            # Save full PR diff (.diff format)
            diff_response = requests.get(pr_url, headers=DIFF_HEADERS)
            if diff_response.status_code == 200:
                with open(os.path.join(pr_path, "diff.diff"), "w") as f:
                    f.write(diff_response.text)
            else:
                print(f"   ⚠️ Could not fetch diff format: {diff_response.status_code}")

            # Save full PR patch (.patch format like second script)
            patch_response = requests.get(pr_url, headers=PATCH_HEADERS)
            if patch_response.status_code == 200:
                with open(os.path.join(pr_path, "diff.patch"), "w") as f:
                    f.write(patch_response.text)
                print(f"   📄 Saved diff.patch")
            else:
                print(f"   ⚠️ Could not fetch patch format: {patch_response.status_code}")

            # Look for existing test patterns in the repo
            test_patterns = {}
            for filename, data in enhanced_patches.items():
                if data["is_test_file"]:
                    content = data["full_content"]
                    if content:
                        test_patterns[filename] = {
                            "content": content,
                            "language": data["language"]
                        }
            
            # Save test patterns for few-shot prompting
            with open(os.path.join(context_path, "test_patterns.json"), "w") as f:
                json.dump(test_patterns, f, indent=2)

            # Create context summary for LLM
            context_summary = {
                "pr_title": pr_data.get("title", ""),
                "total_files_changed": len(enhanced_patches),
                "languages": list(set(p["language"] for p in enhanced_patches.values() if p["language"])),
                "main_changes": [
                    {
                        "file": fname,
                        "status": data["status"],
                        "changes": data["changes"],
                        "language": data["language"],
                        "is_test_file": data["is_test_file"]
                    }
                    for fname, data in enhanced_patches.items()
                    if data["changes"] > 0
                ][:5],  # Top 5 changed files
                "existing_test_files": len(test_patterns),
                "test_files_saved": test_files_saved,
            }
            
            with open(os.path.join(context_path, "context_summary.json"), "w") as f:
                json.dump(context_summary, f, indent=2)

            print(f"✅ Enhanced extraction complete for PR #{pr_number}")
            print(f"   📊 {len(enhanced_patches)} files processed")
            print(f"   🧪 {len(test_patterns)} test patterns found")
            print(f"   💾 {test_files_saved} test files saved")

    print("\n🎉 All done!")

if __name__ == "__main__":
    extract_data()