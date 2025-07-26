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
    #{"owner": "", "repo": "", "prs": []},
    #{"owner": "", "repo": "", "prs": []},
]

BASE_OUTPUT_PATH = "data"  


TEST_EXTENSIONS = [".py", ".cpp", ".c", ".js", ".ts", ".java", ".rb"]
TEST_KEYWORDS = ["test", "spec", "Test"]


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
        file_list = files_response.json()

        
        with open(os.path.join(pr_path, "file_list.txt"), "w") as f:
            for file in file_list:
                f.write(file['filename'] + "\n")

        
        patch_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        patch_response = requests.get(patch_url, headers=PATCH_HEADERS)
        with open(os.path.join(pr_path, "diff.patch"), "w") as f:
            f.write(patch_response.text)

        
        for file in file_list:
            filename = file['filename']
            if any(ext in filename for ext in TEST_EXTENSIONS) and any(keyword.lower() in filename.lower() for keyword in TEST_KEYWORDS):
                raw_url = file.get('raw_url')
                if raw_url:
                    test_content = requests.get(raw_url, headers=HEADERS).text
                    file_name_only = os.path.basename(filename)

                    
                    lang = filename.split('.')[-1]
                    lang_path = os.path.join(test_path, lang)
                    os.makedirs(lang_path, exist_ok=True)

                    with open(os.path.join(lang_path, file_name_only), "w") as f:
                        f.write(test_content)
                    print(f"Saved test: {filename}")

print("\n All done")
