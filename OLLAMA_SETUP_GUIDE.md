# 🚀 Ollama Integration Setup Guide

## Overview

This guide will help you set up and test the Ollama integration with the DeepSeek Coder model for your AI Test Generation Agent.

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Git** for cloning repositories
3. **Internet connection** for downloading models

## 🔧 Step 1: Install Ollama

### Windows
```bash
# Download from https://ollama.ai/download
# Or use winget
winget install Ollama.Ollama
```

### macOS
```bash
# Download from https://ollama.ai/download
# Or use Homebrew
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 🚀 Step 2: Start Ollama

```bash
# Start the Ollama service
ollama serve

# Keep this terminal open - Ollama needs to keep running
```

## 📥 Step 3: Download DeepSeek Coder Model

Open a new terminal and run:

```bash
# Download the DeepSeek Coder model (776MB)
ollama pull deepseek-coder

# Verify the model is available
ollama list
```

You should see:
```
NAME              ID       SIZE   MODIFIED
deepseek-coder    abc123   776MB  2024-01-01 12:00:00
```

## 🧪 Step 4: Test Ollama Connection

Test if Ollama is working:

```bash
# Test with curl
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder",
  "prompt": "Write a simple JavaScript function that adds two numbers."
}'
```

## 🐍 Step 5: Test Python Integration

Navigate to your AI-Testdoc-Agent directory and run:

```bash
# Test the Ollama integration
python test_ollama_integration.py
```

This will test:
- ✅ Ollama connection
- ✅ Model availability
- ✅ Simple text generation
- ✅ Test generation for JavaScript
- ✅ Facebook React scenario simulation

## 📱 Step 6: Test Facebook React PR

```bash
# Test processing a real Facebook React PR
python test_facebook_react.py
```

## 🎯 Step 7: Run Full Workflow

```bash
# Process Facebook React PRs with DeepSeek Coder
python main.py --provider ollama --model deepseek-coder --process-only --repo-filter facebook_react
```

## 🔍 Troubleshooting

### Ollama Not Starting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not responding, restart Ollama
ollama serve
```

### Model Not Found
```bash
# Check available models
ollama list

# If deepseek-coder not listed, pull it again
ollama pull deepseek-coder
```

### Connection Errors
```bash
# Check Ollama status
ollama ps

# Restart Ollama service
ollama serve
```

### Python Import Errors
```bash
# Install requirements
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📊 Expected Results

### Language Detection
- ✅ JavaScript/JSX files detected correctly
- ✅ React components identified
- ✅ Function patterns extracted

### Test Generation
- ✅ Jest-compatible test files (`.js` extension)
- ✅ React Testing Library patterns
- ✅ Hook testing examples
- ✅ Component testing examples

### File Output
```
test_output/
└── deepseek_coder/
    └── facebook_react/
        └── PR_34264/
            ├── test_useCustomHook.js
            ├── test_validateInput.js
            └── doc_useCustomHook.md
```

## 🎉 Success Indicators

1. **Ollama Connection**: ✅ "Ollama connection established"
2. **Model Loading**: ✅ "Using model: deepseek-coder"
3. **Language Detection**: ✅ "Processing javascript function: useCustomHook"
4. **Test Generation**: ✅ "Successfully generated javascript test for useCustomHook"
5. **File Creation**: ✅ Generated `.js` test files with proper Jest syntax

## 🚀 Advanced Usage

### Custom Models
```bash
# Use other coding models
ollama pull codellama:7b
ollama pull llama2:7b

# Update your command
python main.py --provider ollama --model codellama:7b --process-only
```

### Batch Processing
```bash
# Process multiple PRs
python main.py --provider ollama --model deepseek-coder --process-only --repo-filter facebook_react --limit 5
```

### Strategy Comparison
```bash
# Compare different prompt strategies
python main.py --provider ollama --model deepseek-coder --process-only --repo-filter facebook_react --compare-strategies
```

## 📚 Model Specifications

- **Name**: deepseek-coder
- **Size**: 776MB
- **Context**: 16K tokens
- **Parameters**: 1.3 billion
- **Specialization**: Code generation and understanding
- **Languages**: JavaScript, TypeScript, Python, Java, C++, and more

## 🔮 Next Steps

1. **Test with other repositories** (Microsoft STL, FastAPI)
2. **Experiment with different models** (CodeLlama, Llama2)
3. **Customize prompts** for specific languages
4. **Integrate with CI/CD** pipelines
5. **Add model comparison** tools

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify Ollama is running: `ollama serve`
3. Check model availability: `ollama list`
4. Test basic functionality: `ollama run deepseek-coder`
5. Review error logs in the terminal output

---

**Happy coding with DeepSeek Coder! 🎉**
