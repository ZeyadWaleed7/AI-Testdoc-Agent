# AI Pair Programming Agent for Automated Test Writing and Documentation

## You can view the tracking sheet [here](https://docs.google.com/spreadsheets/d/1Y1HOmNrpEKYaUMz9QRFJpv2IKY7jnhiJ8cGuCaS1VGU/edit?usp=sharing).

An intelligent AI agent that observes code diffs and automatically generates unit tests and documentation using CodeLlama.

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

3. Set up .env variables.

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


 
## 📈 Memory and Learning

The agent includes a memory module that:

- Stores test patterns and their effectiveness
- Remembers function contexts and diff patterns
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

The agent is designed to work as a pair programming assistant that can understand code changes and generate appropriate tests and documentation.

 