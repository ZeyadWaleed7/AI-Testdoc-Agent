# Enhanced Context for AI Test Generation

This document explains how to use the enhanced context functionality to generate complete, runnable test units without any TODO comments or assumptions.

## Overview

The enhanced context system provides comprehensive information about PR changes, including:
- **Full file content** (first 2000 characters)
- **Required imports and dependencies**
- **Existing test patterns** from the codebase
- **PR metadata** (title, description, languages)
- **File change details** (additions, deletions, status)

This allows the AI agent to generate 100% executable tests without making assumptions about missing dependencies or imports.

## How It Works

### 1. Data Extraction (`extract_prs.py`)

The extraction script creates several files for each PR:

```
data/
├── repo_name/
│   └── PR_number/
│       ├── enhanced_patches.json      # Full metadata for each changed file
│       ├── file_patches.json          # Clean patch content per file
│       ├── diff.diff                  # Full PR diff
│       ├── diff.patch                 # GitHub patch format
│       ├── file_list.txt              # List of changed files
│       ├── pr_metadata.json           # PR title, description, branches
│       ├── tests/                     # Test files organized by language
│       │   ├── py/                    # Python tests
│       │   ├── js/                    # JavaScript tests
│       │   └── cpp/                   # C++ tests
│       └── context/
│           ├── context_summary.json   # PR summary and statistics
│           └── test_patterns.json     # Existing test patterns for few-shot learning
```

### 2. Enhanced Context Loading

The `EnhancedContextLoader` class loads all this data:

```python
from ai_agent.enhanced_context import EnhancedContextLoader

# Load context for a PR
enhanced_context = EnhancedContextLoader("data/repo_name/PR_number")

# Get file-specific information
file_context = enhanced_context.get_file_context("src/example.py")
imports = enhanced_context.get_imports_for_file("src/example.py")
test_patterns = enhanced_context.get_test_patterns_for_language("python")
```

### 3. Comprehensive Test Generation

The agent uses all available context to generate tests:

```python
# Generate test with enhanced context
test_code = test_generator.generate_tests_with_enhanced_context(
    function_code=function_code,
    function_name=function_name,
    file_path=file_path,
    language=language,
    enhanced_context=enhanced_context
)
```

## Usage

### Step 1: Extract PR Data

```bash
# Extract data for configured PRs
python extract_prs.py

# This will create enhanced context files for each PR
```

### Step 2: Generate Tests with Enhanced Context

```bash
# Use the enhanced-context strategy (default)
python main.py --interactive

# Or process specific PRs
python main.py --pr-filter 123,456

# The agent will automatically detect and use enhanced context
```

### Step 3: Verify Generated Tests

The generated tests will be:
- ✅ **Complete and runnable** - No TODO comments or placeholders
- ✅ **Properly imported** - All necessary dependencies included
- ✅ **Well-tested** - Cover normal cases, edge cases, and error conditions
- ✅ **Framework-aware** - Use correct test framework for the language

## Example Output

### Before (Basic Context)
```python
# Basic prompt with limited context
def test_function():
    # TODO: Add proper imports
    # TODO: Replace with actual path
    result = function(1, 2)
    assert result == 3
```

### After (Enhanced Context)
```python
import pytest
from src.example import function
from unittest.mock import Mock, patch

def test_function_normal_case():
    """Test normal operation"""
    result = function(1, 2)
    assert result == 3

def test_function_edge_cases():
    """Test edge cases"""
    result = function(0, 0)
    assert result == 0
    
    result = function(-1, 1)
    assert result == 0

def test_function_error_conditions():
    """Test error handling"""
    with pytest.raises(ValueError):
        function(None, 1)
    
    with pytest.raises(TypeError):
        function("invalid", 2)
```

## Benefits

### 1. **No More TODO Comments**
- All imports are automatically included
- Dependencies are resolved from actual file content
- Test patterns follow existing codebase conventions

### 2. **Higher Quality Tests**
- Tests cover edge cases and error conditions
- Use proper assertions for the test framework
- Follow existing testing patterns in the codebase

### 3. **Language-Aware Generation**
- Automatically detects language and test framework
- Uses appropriate syntax and conventions
- Handles language-specific import patterns

### 4. **Context-Aware Prompts**
- Includes PR title and description
- Shows related file changes
- References existing test patterns

## Configuration

### Customizing Extraction

Edit `extract_prs.py` to configure:
- Repository list and PR numbers
- File content length limits
- Test file detection patterns
- Output directory structure

### Customizing Prompts

The enhanced context prompts can be customized in `ai_agent/prompts.py`:
- `enhanced_context_prompt()` - Main comprehensive prompt
- `comprehensive_test_prompt()` - Alternative detailed prompt

### Adding New Languages

Support for new languages can be added in `ai_agent/language_detector.py`:
- Function detection patterns
- Test framework mappings
- Import extraction rules

## Troubleshooting

### Common Issues

1. **"No enhanced context found"**
   - Run `extract_prs.py` first
   - Check that PR directories contain `enhanced_patches.json`

2. **"Empty test generation"**
   - Verify LLM provider is working
   - Check model compatibility
   - Review prompt content

3. **"Generated test still contains TODO comments"**
   - The agent will automatically retry with stronger prompts
   - Check that all required context files are present

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Enhanced Context

Use the test script to verify functionality:
```bash
python test_enhanced_context.py
```

## Migration from Basic Context

If you're currently using basic diff processing:

1. **Run extraction** to create enhanced context files
2. **Update agent calls** to use `enhanced-context` strategy
3. **Verify results** - tests should be more complete and runnable

The agent automatically falls back to basic processing if enhanced context is unavailable.

## Best Practices

1. **Always run extraction first** - Enhanced context requires pre-processing
2. **Use the default strategy** - `enhanced-context` provides best results
3. **Review generated tests** - Verify they meet your quality standards
4. **Customize prompts** - Adapt to your specific testing conventions
5. **Monitor memory usage** - Large PRs may require significant context

## Future Enhancements

Planned improvements:
- **Incremental context updates** - Only re-extract changed files
- **Cross-PR learning** - Use patterns from multiple PRs
- **Custom context providers** - Support for other data sources
- **Context validation** - Verify context quality and completeness
- **Performance optimization** - Faster context loading and processing
