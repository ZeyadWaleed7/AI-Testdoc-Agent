# Language-Agnostic AI Test Generation Agent

## Overview

The AI Test Generation Agent has been completely refactored to support multiple programming languages beyond just Python. It now automatically detects the programming language of files in PRs and generates appropriate tests using the correct testing frameworks and language conventions.

## 🚀 New Features

### Multi-Language Support
- **Automatic Language Detection**: Detects programming languages from file extensions and content patterns
- **Language-Specific Test Generation**: Generates tests using appropriate testing frameworks for each language
- **Correct File Extensions**: Creates test files with the proper extension for each language
- **Language-Aware Parsing**: Uses regex patterns instead of Python AST for function extraction

### Supported Languages

| Language | File Extensions | Test Frameworks | Function Patterns |
|----------|----------------|-----------------|-------------------|
| **Python** | `.py`, `.pyw`, `.pyx`, `.pyi` | pytest, unittest, nose | `def`, `async def`, `class` |
| **JavaScript** | `.js`, `.jsx`, `.mjs`, `.cjs` | jest, mocha, jasmine, tape, ava | `function`, `const/let/var =`, `:` |
| **TypeScript** | `.ts`, `.tsx` | jest, mocha, jasmine, tape, ava | `function`, `const/let/var:`, `:` |
| **Java** | `.java` | junit, testng, mockito, powermock | `public/private/protected`, `class` |
| **C++** | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.h` | gtest, catch2, boost.test, cppunit | `template`, `class`, `struct`, `union` |
| **C** | `.c`, `.h` | unity, cmocka, cunit | `static`, `inline`, `struct`, `union` |
| **C#** | `.cs` | nunit, xunit, mstest, moq | `public/private/protected`, `class` |
| **Go** | `.go` | testing, testify, gomock | `func`, `type` |
| **Rust** | `.rs` | test, mockall, mockiato | `fn`, `struct`, `enum`, `trait` |
| **PHP** | `.php` | phpunit, codeception, pest | `function`, `class` |
| **Ruby** | `.rb` | rspec, minitest, test-unit | `def`, `class` |
| **Swift** | `.swift` | xctest, quick, nimble | `func`, `class`, `struct`, `enum` |
| **Kotlin** | `.kt`, `.kts` | junit, kotlin.test, mockk | `fun`, `class` |
| **Scala** | `.scala` | scalatest, specs2, scalacheck | `def`, `class` |
| **Dart** | `.dart` | test | `class`, `function` |
| **R** | `.r`, `.R` | testthat | `function`, `<-` |
| **MATLAB** | `.m` | matlab.unittest | `function`, `classdef` |
| **Perl** | `.pl`, `.pm` | Test::More, Test::Simple | `sub`, `package` |
| **Bash** | `.sh`, `.bash` | bats, shunit2 | `#!/bin/bash` |
| **PowerShell** | `.ps1` | Pester | `function`, `param` |
| **SQL** | `.sql` | dbunit, testcontainers | `CREATE`, `INSERT`, `SELECT` |
| **HTML** | `.html`, `.htm` | jest, cypress | `<!DOCTYPE html>`, `<html>` |
| **CSS** | `.css`, `.scss`, `.sass`, `.less` | jest-css-modules | `@media`, `@keyframes` |
| **YAML** | `.yml`, `.yaml` | yaml-test | `---`, `key:` |
| **JSON** | `.json` | jest-json-schema | `{`, `[` |
| **XML** | `.xml` | xml-test | `<?xml`, `<root>` |
| **Markdown** | `.md`, `.markdown` | markdownlint | `#`, `##`, `[link]` |

### Special Files
- **Dockerfile**: `Dockerfile`, `.dockerfile`
- **Makefile**: `Makefile`, `makefile`, `.mk`
- **CMake**: `CMakeLists.txt`, `.cmake`
- **Gradle**: `build.gradle`, `build.gradle.kts`
- **Maven**: `pom.xml`
- **NPM**: `package.json`
- **Cargo**: `Cargo.toml`
- **Go Modules**: `go.mod`
- **Python Dependencies**: `requirements.txt`, `setup.py`, `pyproject.toml`

## 🔧 How It Works

### 1. Language Detection
The agent automatically detects the programming language using:
- **File Extension**: Primary method for most files
- **Content Analysis**: Fallback using regex patterns and heuristics
- **Shebang Detection**: For script files

### 2. Function Extraction
Instead of Python-specific AST parsing, the agent now uses:
- **Language-Specific Regex Patterns**: Custom patterns for each language
- **Brace Counting**: For C-style languages
- **Indentation Analysis**: For Python-style languages

### 3. Test Generation
Tests are generated with:
- **Appropriate Testing Framework**: Uses the primary framework for each language
- **Language Conventions**: Follows language-specific best practices
- **Correct File Extensions**: Creates test files with proper extensions

### 4. File Output
Generated files use:
- **Language-Appropriate Extensions**: `.js` for JavaScript, `.java` for Java, etc.
- **Proper Encoding**: UTF-8 encoding for all files
- **Framework-Specific Structure**: Follows testing framework conventions

## 📁 Example Output Structure

```
generated/
├── h2oai_h2ogpt_16k_codellama_13b_python/
│   └── diff_aware/
│       ├── test_calculate.js          # JavaScript test
│       ├── test_validate.java         # Java test
│       ├── test_process.cpp           # C++ test
│       └── test_handler.go            # Go test
```

## 🧪 Testing the Language Detection

Run the test script to verify language detection:

```bash
cd AI-Testdoc-Agent
python test_language_detection.py
```

This will test:
- File extension detection
- Content-based detection
- Function pattern matching
- Test framework mapping

## 🚀 Usage Examples

### Process a JavaScript PR
```bash
python main.py --process-only --repo-filter "facebook_react"
```

### Process a Java PR
```bash
python main.py --process-only --repo-filter "microsoft_STL"
```

### Process a C++ PR
```bash
python main.py --process-only --repo-filter "microsoft_STL" --pr-filter "5551"
```

## 🔍 Language Detection Examples

### JavaScript/TypeScript
```javascript
export function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
}

export const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
```

### Java
```java
public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }
    
    private boolean isValid(int value) {
        return value >= 0;
    }
}
```

### C++
```cpp
template<typename T>
class Vector {
public:
    void push_back(const T& value) {
        // implementation
    }
    
private:
    std::vector<T> data;
};
```

### Go
```go
package calculator

func Add(a, b int) int {
    return a + b
}

type Calculator struct {
    result int
}
```

## 🎯 Benefits

1. **Universal Coverage**: Works with any programming language, not just Python
2. **Correct Test Frameworks**: Uses appropriate testing tools for each language
3. **Language Conventions**: Follows language-specific best practices
4. **Automatic Detection**: No manual configuration needed
5. **Extensible**: Easy to add support for new languages

## 🔮 Future Enhancements

- **Language-Specific Prompts**: Customized prompts for each language
- **Framework Detection**: Auto-detect testing frameworks in use
- **Code Style**: Language-specific code formatting
- **Dependency Analysis**: Parse package files for context
- **IDE Integration**: Language server protocol support

## 🐛 Troubleshooting

### Language Not Detected
- Check file extension is supported
- Verify file content contains language-specific patterns
- Ensure file is not binary or config file

### Test Generation Fails
- Check LLM model supports the language
- Verify function extraction worked correctly
- Review error logs for specific issues

### Wrong File Extension
- Verify language detection is correct
- Check `LanguageDetector.get_file_extension_for_language()`
- Ensure language is in supported languages list

## 📚 Technical Details

### Architecture Changes
- **Removed Python AST dependency**: Now uses regex-based parsing
- **Added LanguageDetector class**: Centralized language detection logic
- **Updated all generators**: Language-aware test and documentation generation
- **Enhanced file handling**: Proper extensions and encoding

### Performance Improvements
- **Faster parsing**: Regex patterns vs AST parsing
- **Language caching**: Detected languages are cached per file
- **Efficient patterns**: Optimized regex patterns for each language

### Error Handling
- **Graceful fallbacks**: Basic test generation when LLM fails
- **Language validation**: Ensures detected languages are supported
- **File validation**: Skips binary and unsupported file types
