import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
PATCH_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.patch"
}

REPOS = [
    {"owner": "fastapi", "repo": "fastapi", "prs": [13827]},
]

BASE_OUTPUT_PATH = "data"  

TEST_EXTENSIONS = [".py", ".cpp", ".c", ".js", ".ts", ".java", ".rb"]
TEST_KEYWORDS = ["test", "spec", "Test"]

def extract_data():
    for repo_info in REPOS:
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        prs = repo_info["prs"]

        for pr_number in prs:
            print(f"\n Extracting PR #{pr_number} from {owner}/{repo}")

            repo_dir = f"{owner}_{repo}"
            pr_path = os.path.join(BASE_OUTPUT_PATH, repo_dir, f"PR_{pr_number}")
            test_path = os.path.join(pr_path, "tests")
            os.makedirs(test_path, exist_ok=True)

            files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
            files_response = requests.get(files_url, headers=HEADERS)
            
            if files_response.status_code != 200:
                print(f"❌ Error getting files for PR #{pr_number}: {files_response.status_code}")
                print(f"Response: {files_response.text}")
                continue
                
            try:
                file_list = files_response.json()
            except Exception as e:
                print(f"❌ Error parsing files response for PR #{pr_number}: {e}")
                print(f"Response: {files_response.text}")
                continue
            
            if not isinstance(file_list, list):
                print(f"❌ Unexpected response format for PR #{pr_number}: {type(file_list)}")
                print(f"Response: {file_list}")
                continue

            with open(os.path.join(pr_path, "file_list.txt"), "w") as f:
                for file in file_list:
                    if isinstance(file, dict) and 'filename' in file:
                        f.write(file['filename'] + "\n")
                    else:
                        print(f"⚠️ Skipping invalid file entry: {file}")

            patch_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            patch_response = requests.get(patch_url, headers=PATCH_HEADERS)
            
            if patch_response.status_code != 200:
                print(f"❌ Error getting patch for PR #{pr_number}: {patch_response.status_code}")
                print(f"Response: {patch_response.text}")
                continue
                
            with open(os.path.join(pr_path, "diff.patch"), "w") as f:
                f.write(patch_response.text)

            for file in file_list:
                if not isinstance(file, dict) or 'filename' not in file:
                    continue
                    
                filename = file['filename']
                if any(ext in filename for ext in TEST_EXTENSIONS) and any(keyword.lower() in filename.lower() for keyword in TEST_KEYWORDS):
                    raw_url = file.get('raw_url')
                    if raw_url:
                        try:
                            test_content = requests.get(raw_url, headers=HEADERS).text
                            file_name_only = os.path.basename(filename)

                            lang = filename.split('.')[-1]
                            lang_path = os.path.join(test_path, lang)
                            os.makedirs(lang_path, exist_ok=True)

                            with open(os.path.join(lang_path, file_name_only), "w") as f:
                                f.write(test_content)
                            print(f"Saved test: {filename}")
                        except Exception as e:
                            print(f"❌ Error downloading test file {filename}: {e}")

    print("\n All done")

if __name__ == "__main__":
    extract_data()
