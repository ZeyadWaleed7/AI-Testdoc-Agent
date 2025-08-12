# AI Pair Programming Agent for Automated Test Writing and Documentation

## You can view the tracking sheet [here](https://docs.google.com/spreadsheets/d/1Y1HOmNrpEKYaUMz9QRFJpv2IKY7jnhiJ8cGuCaS1VGU/edit?usp=sharing).

An intelligent AI agent that observes code diffs and automatically generates unit tests and documentation using Phind-CodeLlama-34B-v2.

## 🏗️ Architecture

### Components

| Component | Function |
|-----------|----------|
| **Watcher Module** | Monitors code diffs (git diff, GitHub PRs) to detect changed/added functions |
| **Test Generator** | Uses Phind-CodeLlama-34B-v2 LLM to write or update unit tests based on diffs |
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

**Note**: The requirements now include the latest transformers from git to support the Phind-CodeLlama-34B-v2 model via remote inference.

3. Set up Hugging Face API token (optional but recommended for better performance):

```bash
# Set environment variable
export HF_TOKEN="your_huggingface_token_here"

# Or create a .env file
echo "HF_TOKEN=your_huggingface_token_here" > .env
```

**Note**: The API token is optional but recommended for better performance and rate limits.

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

### Try the New Model

Test the Phind-CodeLlama-34B-v2 model with a simple example:

```bash
python examples/phind_model_example.py
```

This will demonstrate the model's capabilities for test generation and documentation.

### Test Model Loading

Before running the full agent, you can test if the model loads correctly:

```bash
python test_model.py
```

This will verify that the Phind-CodeLlama-34B-v2 model can be loaded and used for generation.

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

### Remote Inference Setup

The agent now uses the Phind-CodeLlama-34B-v2 model via **Hugging Face Inference API**, which provides:

- **True Remote Execution**: Model runs on Hugging Face's AWS infrastructure
- **Zero Local Resources**: No GPU, RAM, or storage requirements
- **Instant Access**: No model downloads or setup time
- **Scalable Performance**: Leverages cloud computing resources

- **Enhanced Code Understanding**: Better comprehension of complex code structures
- **Improved Test Generation**: More accurate and comprehensive unit tests
- **Better Documentation**: Higher quality docstrings and API documentation
- **Context Awareness**: Superior understanding of code diffs and changes

#### Model Parameters

The model uses optimized generation parameters:
- **Temperature**: 0.1 (for consistent, focused output)
- **Top-p**: 0.75 (nucleus sampling for quality)
- **Top-k**: 40 (diverse token selection)
- **Max Tokens**: 384 for completions, 1024 for tests, 512 for docs

### GitHub Token Setup



### Model Configuration

The agent uses Phind-CodeLlama-34B-v2 by default, which runs remotely without requiring local model downloads. You can specify a different model:

```bash
# Use the default Phind-CodeLlama-34B-v2 model (runs remotely)
python main.py

# Use a different model if needed
python main.py --model "Phind/Phind-CodeLlama-34B-v2"
```

### Model Information

The agent now uses **Phind-CodeLlama-34B-v2** as the default model via **remote inference**, which provides:

- **High Quality**: 34B parameter model trained on code-specific data
- **True Remote Execution**: No local model downloads or GPU requirements
- **Optimized Performance**: Specifically tuned for code generation tasks
- **Cloud-Based**: Runs on Hugging Face's AWS infrastructure

#### Model Details

- **Model**: Phind/Phind-CodeLlama-34B-v2
- **Hardware**: Trained on 32x A100-80GB GPUs
- **Training Time**: 480 GPU-hours
- **Provider**: AWS us-east-1
- **Architecture**: Based on CodeLlama with Phind-specific optimizations
- **Inference**: Uses Hugging Face Inference API for remote execution

#### Benefits of Remote Inference

1. **No Local Resources**: Zero GPU, RAM, or storage requirements
2. **Instant Access**: No waiting for model downloads or setup
3. **Always Available**: Leverages Hugging Face's managed infrastructure
4. **Professional Results**: Generates production-ready tests and documentation


 
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
  --model "Phind/Phind-CodeLlama-34B-v2"
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

### Model Performance

The Phind-CodeLlama-34B-v2 model has been specifically optimized for code generation tasks:

- **HumanEval Benchmark**: Achieves competitive results on the HumanEval benchmark
- **Code Quality**: Generates production-ready code with proper error handling
- **Test Coverage**: Creates comprehensive test suites covering edge cases
- **Documentation**: Produces clear, professional documentation

### Model Capabilities

- **Advanced Code Understanding**: 34B parameters provide deep code comprehension
- **Test Generation**: Creates comprehensive unit tests with edge case coverage
- **Documentation**: Generates professional docstrings and API documentation
- **Diff Analysis**: Understands code changes and generates appropriate updates
- **Remote Execution**: No local computational resources required

 