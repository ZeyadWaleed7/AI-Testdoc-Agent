# AI Pair Programming Agent for Automated Test Writing and Documentation

An intelligent AI agent that observes code diffs and automatically generates unit tests and documentation using CodeLlama.

## 🎯 Research Objectives

- Design and implement an AI pair programming agent that observes code diffs and automatically generates unit tests and documentation
- Incorporate a memory module into the agent to improve test quality and coverage suggestions over time
- Evaluate the quality of generated tests using mutation score, coverage, flakiness, and comparison with human-written tests
- Assess the effect of prompt design on the quality, robustness, and correctness of generated unit tests
- Compare different prompting strategies (naive, diff-aware, CoT, few-shot) to determine which yields better test quality

## 🏗️ Architecture

### Components

| Component | Function |
|-----------|----------|
| **Watcher Module** | Monitors code diffs (git diff, GitHub PRs) to detect changed/added functions |
| **Test Generator** | Uses CodeLlama LLM to write or update unit tests based on diffs |
| **Documentation Generator** | Generates or edits docstrings and README.md/API.md |
| **Memory Module** | Stores context on past test gaps or diff patterns to improve future suggestions |
| **Interface** | CLI commands and GitHub Bot integration |

### Prompting Strategies

| Strategy | Description |
|----------|-------------|
| **Naive** | "Write a test for this function." |
| **Diff-Aware** | "Write a test for this function, which was modified as follows…" + git diff |
| **Few-Shot** | Show 1–2 examples of function + test before target |
| **CoT** | "Analyze the inputs, expected outputs, edge cases, then write test code." |
| **TDD** | "Here's the function spec. Write tests before code is implemented." |

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI-Testdoc-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
# Create .env file
echo "GITHUB_TOKEN=your_github_token_here" > .env
```

### Basic Usage

1. **Extract PR data and process with AI agent:**
```bash
python main.py
```

2. **Extract PR data only:**
```bash
python main.py --extract-only
```

3. **Process existing diff files only:**
```bash
python main.py --process-only
```

4. **Compare all prompt strategies:**
```bash
python main.py --compare-strategies
```

5. **Use specific prompt strategy:**
```bash
python main.py --prompt-strategy diff-aware
```

6. **Show memory insights:**
```bash
python main.py --memory-insights
```

## 📁 Project Structure

```
AI-Testdoc-Agent/
├── ai_agent/                 # Core AI agent modules
│   ├── __init__.py
│   ├── agent.py             # Main orchestrator
│   ├── llm.py              # CodeLlama integration
│   ├── generator.py        # Test generation
│   ├── documentation.py    # Documentation generation
│   ├── memory.py          # Memory module
│   ├── prompts.py         # Prompt strategies
│   └── watcher.py         # Diff monitoring
├── data/                   # Extracted PR data
├── examples/              # Example files
├── experiments/           # Research experiments
├── interface/             # CLI and bot interfaces
├── tests/                 # Test files
├── extract_prs.py         # PR data extraction
├── main.py               # Main orchestrator
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔧 Configuration

### GitHub Token Setup

To extract PR data from private repositories, you need a GitHub token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Add it to your `.env` file:
```
GITHUB_TOKEN=your_token_here
```

### Model Configuration

The agent uses CodeLlama 7B by default (smaller, faster, less disk space). You can specify a different model:

```bash
# Use the default 7B model (recommended for limited disk space)
python main.py

# Use a larger model if you have more disk space
python main.py --model "codellama/CodeLlama-13b-Instruct-hf"
python main.py --model "codellama/CodeLlama-34b-Instruct-hf"
```

### Model Size Comparison & Selection

Due to disk space constraints and deployment limitations, we selected the **CodeLlama 7B** model as the default choice. Here's a detailed comparison:

| Model | Size | Disk Space | Speed | Quality | Use Case |
|-------|------|------------|-------|---------|----------|
| **CodeLlama 7B** (default) | ~13GB | ✅ Small | ✅ Fast | ✅ Good | ✅ Research & Development |
| CodeLlama 13B | ~40GB | ⚠️ Medium | ⚠️ Medium | ✅ Better | ⚠️ Requires more resources |
| CodeLlama 34B | ~80GB | ❌ Large | ❌ Slow | ✅ Best | ❌ Heavy resource requirements |

#### Why CodeLlama 7B?

1. **Disk Space Constraints**: The original 13B model requires ~40GB of disk space, which exceeds the available storage capacity in our development environment.

2. **Deployment Limitations**: We don't have access to deploy the model on Hugging Face Inference API or similar cloud services, so we must download and run the model locally.

3. **Research Efficiency**: For research purposes, the 7B model provides a good balance between:
   - **Performance**: Sufficient quality for test generation and documentation
   - **Resource Usage**: Reasonable disk space and memory requirements (~13GB)
   - **Speed**: Fast inference for iterative development and testing

4. **Accessibility**: The smaller model makes the research accessible to developers with limited computational resources.

#### Remote Model Access Strategy

Since we cannot deploy the model on Hugging Face's infrastructure, we use the following approach:

- **Remote Download**: Use Hugging Face access tokens to download the model from their model hub
- **Local Caching**: Cache the downloaded model locally for subsequent runs
- **Authentication**: Use read-only access tokens to authenticate with Hugging Face
- **Fallback Options**: Provide multiple model size options for different resource constraints

This approach allows us to leverage Hugging Face's model distribution while working within our deployment and resource constraints.

### Remote Model Access

To use the remote Hugging Face model with authentication:

1. **Set up your Hugging Face access token:**
   ```bash
   # Option 1: Set environment variable
   export HF_TOKEN="your_hugging_face_token_here"
   
   # Option 2: Use command line argument
   python main.py --hf-token "your_hugging_face_token_here"
   ```

2. **Test remote model access:**
   ```bash
   python test_remote_model.py
   ```

3. **The agent will automatically use the token for remote model loading:**
   ```python
   from ai_agent.agent import AIAgent
   
   # Initialize with your token
   agent = AIAgent(auth_token="your_hugging_face_token_here")
   ```

**Note:** The default token provided in the code is for demonstration. For production use, please use your own Hugging Face access token with appropriate permissions.

## 📊 Research Questions

1. **RQ1**: How effective are LLM-generated tests—based on code diffs—compared to human-written ones in terms of code coverage, mutation score, and test quality?

2. **RQ2**: Can a memory-augmented AI agent suggest more complete and useful test cases over time?

3. **RQ3**: What is the impact of different prompt engineering strategies on the quality, correctness, and robustness of generated unit tests?

4. **RQ4**: How usable and helpful is the documentation (docstrings and markdowns) generated by the AI agent during the development process?

5. **RQ5**: What is the developer experience of integrating the AI agent via CLI or GitHub bot into real workflows?

## 🧪 Experiments

The `experiments/` directory contains research experiments:

- `baseline_generation.py`: Baseline test generation experiments
- `prompt_comparison.py`: Prompt strategy comparison experiments
- `report.csv`: Experimental results

## 📈 Memory and Learning

The agent includes a memory module that:

- Stores test patterns and their effectiveness
- Remembers function contexts and diff patterns
- Tracks coverage gaps and suggests improvements
- Learns which prompt strategies work best for different function types

## 🔍 CLI Interface

The agent provides a comprehensive CLI interface:

```bash
# Basic usage
python main.py

# Advanced options
python main.py \
  --prompt-strategy diff-aware \
  --compare-strategies \
  --memory-insights \
  --model "codellama/CodeLlama-7b-Instruct-hf"
```

## 📝 Output

The agent generates:

- **Test files**: `test_<function_name>.py`
- **Documentation**: `doc_<function_name>.md`
- **Summary reports**: `generation_summary.json`
- **Strategy comparisons**: `prompt_comparison_results.json`
- **Memory insights**: `agent_memory.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔬 Research Context

This project is part of research on AI-assisted software development, specifically focusing on automated test generation and documentation. The agent is designed to work as a pair programming assistant that can understand code changes and generate appropriate tests and documentation.

## 📚 References

- CodeLlama: [https://github.com/facebookresearch/codellama](https://github.com/facebookresearch/codellama)
- FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- Transformers: [https://huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)
