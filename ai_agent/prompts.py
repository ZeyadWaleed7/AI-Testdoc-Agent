from typing import Dict, List, Any

class PromptTemplates:
    
    @staticmethod
    def enhanced_context_prompt(
        function_code: str, 
        enhanced_context: Dict[str, Any],
        file_path: str,
        language: str
    ) -> str:
        """Generate optimized prompt for enhanced context test generation (5-7k chars)"""
        
        # Extract essential context information only
        pr_title = enhanced_context.get('pr_title', 'Unknown PR')
        file_patch = enhanced_context.get('file_patch', '')
        diff_patch = enhanced_context.get('diff_patch', '')
        imports = enhanced_context.get('imports', [])
        full_content = enhanced_context.get('full_content', '')
        
        # Get primary test framework
        test_frameworks = enhanced_context.get('test_frameworks', [])
        primary_framework = test_frameworks[0] if test_frameworks else "pytest"
        
        # Get essential context summary
        context_summary = enhanced_context.get('context_summary', {})
        pr_metadata = enhanced_context.get('pr_metadata', {})
        
        # Language-specific instructions
        language_instructions = ""
        if language.lower() == 'cpp':
            language_instructions = """
C++ SPECIFIC REQUIREMENTS - CRITICAL:
- Use Google Test (gtest) framework: #include <gtest/gtest.h>
- Test class should inherit from ::testing::Test
- Use TEST() macro for simple tests: TEST(TestSuiteName, TestName)
- Use TEST_F() macro for fixture-based tests: TEST_F(TestFixtureName, TestName)
- Include proper headers: #include <gtest/gtest.h>, #include <gmock/gmock.h>
- Use EXPECT_* and ASSERT_* macros for assertions
- Include the source file being tested: #include "filename.cpp" or #include "filename.h"
- Use proper C++ syntax and modern C++ features
- Include necessary standard library headers: #include <vector>, #include <string>, etc.

🚨 ABSOLUTELY FORBIDDEN FOR C++:
- NO placeholder comments like "// Set up your test here" or "// Test logic here"
- NO generic test templates without actual logic
- NO "// TODO" or "// FIXME" comments
- NO empty test functions with just EXPECT_TRUE(true)
- NO comments like "// Clean up after test here"

✅ REQUIRED FOR C++:
- Write ACTUAL test logic based on the function being tested
- Test the specific functionality with real assertions
- Include meaningful test data and edge cases
- Test both success and failure scenarios
- Use proper C++ test patterns and assertions
- Make tests that actually validate the function behavior
- Write complete SetUp() and TearDown() methods with actual initialization code
"""
        elif language.lower() == 'java':
            language_instructions = """
JAVA SPECIFIC REQUIREMENTS:
- Use JUnit 5: import org.junit.jupiter.api.Test, import org.junit.jupiter.api.BeforeEach
- Use proper JUnit annotations: @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll
- Use Assertions class: import static org.junit.jupiter.api.Assertions.*
- Use proper Java syntax and modern Java features
- Include necessary imports for the class being tested
"""
        elif language.lower() == 'go':
            language_instructions = """
GO SPECIFIC REQUIREMENTS:
- Use Go testing package: import "testing"
- Test functions should be named TestFunctionName
- Use testing.T for test functions: func TestFunctionName(t *testing.T)
- Use proper Go assertions: if got != want { t.Errorf("got %v, want %v", got, want) }
- Use testify if available: import "github.com/stretchr/testify/assert"
- Include necessary imports for the package being tested
"""
        
        prompt = f"""CRITICAL MISSION: Generate a COMPLETE, RUNNABLE test file for this {language} function.

ABSOLUTE REQUIREMENTS (NO EXCEPTIONS):
- Generate ONLY the complete test file code
- NO explanations, NO comments, NO English text
- NO backticks (```) or markdown formatting
- NO "TODO" or "needs implementation" comments
- The file must be 100% syntactically correct
- Include ALL necessary imports and test functions
- Make it runnable immediately with {primary_framework}
- Test both success and error cases
- Include proper assertions and test logic
- Use proper import statements for all dependencies
{language_instructions}

FUNCTION TO TEST:
{function_code}

CHANGES MADE (from diff):
{file_patch[:1000] if file_patch else 'No specific changes'}

EXACT IMPORTS FROM SOURCE FILE (USE THESE AS BASE):
{chr(10).join(imports) if imports else 'Standard library imports'}

IMPORT REQUIREMENTS:
- Start with ALL necessary imports from the source file above
- Add testing framework imports ({primary_framework})
- Ensure ALL imports are complete and correct
- NO incomplete import statements

TEST FRAMEWORK: {primary_framework}

PR CONTEXT: {pr_title}
{context_summary.get('description', '')[:200] if context_summary else ''}

CRITICAL: You must generate a COMPLETE test file with:
1. All necessary imports (including testing framework)
2. At least 3-5 test functions that test the actual functionality
3. Proper test logic with assertions
4. Test both normal cases and edge cases
5. NO repetitive imports, NO incomplete code

🚫 ABSOLUTELY FORBIDDEN:
- NO repetitive import statements
- NO incomplete import statements
- NO endless loops of the same imports
- NO English explanations or comments
- NO placeholder text

✅ REQUIRED OUTPUT:
- ONLY the complete test file code
- Clean, non-repetitive imports
- Complete test functions with proper logic
- Ready to run immediately

GENERATE THE COMPLETE TEST FILE NOW - START WITH ALL NECESSARY IMPORTS, THEN TEST FUNCTIONS WITH PROPER SYNTAX:"""

        return prompt

    @staticmethod
    def naive_prompt(function_code: str, language: str = "python") -> str:
        """Generate a comprehensive prompt for basic test generation."""
        from .language_detector import LanguageDetector
        
        test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
        primary_framework = test_frameworks[0] if test_frameworks else "standard"
        
        # Language-specific instructions
        language_instructions = ""
        if language.lower() == 'cpp':
            language_instructions = """
C++ SPECIFIC REQUIREMENTS - CRITICAL:
- Use Google Test (gtest) framework: #include <gtest/gtest.h>
- Test class should inherit from ::testing::Test
- Use TEST() macro for simple tests: TEST(TestSuiteName, TestName)
- Use TEST_F() macro for fixture-based tests: TEST_F(TestFixtureName, TestName)
- Include proper headers: #include <gtest/gtest.h>, #include <gmock/gmock.h>
- Use EXPECT_* and ASSERT_* macros for assertions
- Include the source file being tested: #include "filename.cpp" or #include "filename.h"
- Use proper C++ syntax and modern C++ features
- Include necessary standard library headers: #include <vector>, #include <string>, etc.

🚨 ABSOLUTELY FORBIDDEN FOR C++:
- NO placeholder comments like "// Set up your test here" or "// Test logic here"
- NO generic test templates without actual logic
- NO "// TODO" or "// FIXME" comments
- NO empty test functions with just EXPECT_TRUE(true)
- NO comments like "// Clean up after test here"

✅ REQUIRED FOR C++:
- Write ACTUAL test logic based on the function being tested
- Test the specific functionality with real assertions
- Include meaningful test data and edge cases
- Test both success and failure scenarios
- Use proper C++ test patterns and assertions
- Make tests that actually validate the function behavior
- Write complete SetUp() and TearDown() methods with actual initialization code
"""
        elif language.lower() == 'java':
            language_instructions = """
JAVA SPECIFIC REQUIREMENTS:
- Use JUnit 5: import org.junit.jupiter.api.Test, import org.junit.jupiter.api.BeforeEach
- Use proper JUnit annotations: @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll
- Use Assertions class: import static org.junit.jupiter.api.Assertions.*
- Use proper Java syntax and modern Java features
- Include necessary imports for the class being tested
"""
        elif language.lower() == 'go':
            language_instructions = """
GO SPECIFIC REQUIREMENTS:
- Use Go testing package: import "testing"
- Test functions should be named TestFunctionName
- Use testing.T for test functions: func TestFunctionName(t *testing.T)
- Use proper Go assertions: if got != want { t.Errorf("got %v, want %v", got, want) }
- Use testify if available: import "github.com/stretchr/testify/assert"
- Include necessary imports for the package being tested
"""
        
        return f"""You are a senior test engineer. Generate a COMPLETE, RUNNABLE test file for this {language} function using {primary_framework}.

🚨 CRITICAL REQUIREMENTS - READ CAREFULLY AND FOLLOW EXACTLY:

- Generate ONLY the test code - NO intro text, NO explanations, NO TODO comments, NO placeholders
- The test must be 100% complete and executable without any manual modifications
- Include ALL necessary imports and dependencies
- Test the actual functionality, not generic cases
- Include proper setup, teardown, and cleanup
- Test normal cases, edge cases, and error conditions
- Make sure the test runs successfully on the first try
{language_instructions}

🚫 ABSOLUTELY FORBIDDEN:
- NO English explanations like "Sure, here is a basic example..."
- NO "Here's how you could write tests..."
- NO "This includes testing normal cases..."
- NO TODO comments
- NO FIXME comments
- NO incomplete imports
- NO placeholder text
- NO numbered explanations like "1. This test does..."
- NO "This test validates..." or "This function tests..." explanations
- NO markdown formatting or code blocks
- NO bullet points or lists explaining the code
- NO text after the actual code - ONLY code until the end

✅ REQUIRED OUTPUT:
- ONLY the complete test file code
- All imports must be complete and correct
- All test functions must be fully implemented
- All assertions must be real and test actual functionality

Function to test:
```{language}
{function_code}
```

Generate a complete test that:
1. Has all necessary imports and dependencies
2. Sets up proper test fixtures with cleanup
3. Tests the function thoroughly with real assertions
4. Is immediately runnable
5. Tests normal cases, edge cases, and error conditions
6. Includes proper error handling
7. Has no TODO comments or assumptions

🚨 FINAL INSTRUCTION:
Output ONLY the complete test code, nothing else. The test should work immediately when executed.

START GENERATING THE TEST CODE NOW:"""

    @staticmethod
    def diff_aware_prompt(function_code: str, diff_context: str, language: str = "python") -> str:
        from .language_detector import LanguageDetector
        test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
        primary_framework = test_frameworks[0] if test_frameworks else "standard"
        
        # Language-specific instructions
        language_instructions = ""
        if language.lower() == 'cpp':
            language_instructions = """
C++ SPECIFIC REQUIREMENTS - CRITICAL:
- Use Google Test (gtest) framework: #include <gtest/gtest.h>
- Test class should inherit from ::testing::Test
- Use TEST() macro for simple tests: TEST(TestSuiteName, TestName)
- Use TEST_F() macro for fixture-based tests: TEST_F(TestFixtureName, TestName)
- Include proper headers: #include <gtest/gtest.h>, #include <gmock/gmock.h>
- Use EXPECT_* and ASSERT_* macros for assertions
- Include the source file being tested: #include "filename.cpp" or #include "filename.h"
- Use proper C++ syntax and modern C++ features
- Include necessary standard library headers: #include <vector>, #include <string>, etc.

🚨 ABSOLUTELY FORBIDDEN FOR C++:
- NO placeholder comments like "// Set up your test here" or "// Test logic here"
- NO generic test templates without actual logic
- NO "// TODO" or "// FIXME" comments
- NO empty test functions with just EXPECT_TRUE(true)
- NO comments like "// Clean up after test here"

✅ REQUIRED FOR C++:
- Write ACTUAL test logic based on the function being tested
- Test the specific functionality with real assertions
- Include meaningful test data and edge cases
- Test both success and failure scenarios
- Use proper C++ test patterns and assertions
- Make tests that actually validate the function behavior
- Write complete SetUp() and TearDown() methods with actual initialization code
"""
        elif language.lower() == 'java':
            language_instructions = """
JAVA SPECIFIC REQUIREMENTS:
- Use JUnit 5: import org.junit.jupiter.api.Test, import org.junit.jupiter.api.BeforeEach
- Use proper JUnit annotations: @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll
- Use Assertions class: import static org.junit.jupiter.api.Assertions.*
- Use proper Java syntax and modern Java features
- Include necessary imports for the class being tested
"""
        elif language.lower() == 'go':
            language_instructions = """
GO SPECIFIC REQUIREMENTS:
- Use Go testing package: import "testing"
- Test functions should be named TestFunctionName
- Use testing.T for test functions: func TestFunctionName(t *testing.T)
- Use proper Go assertions: if got != want { t.Errorf("got %v, want %v", got, want) }
- Use testify if available: import "github.com/stretchr/testify/assert"
- Include necessary imports for the package being tested
"""
        
        return f"""You are a senior test engineer. Generate a COMPLETE, RUNNABLE test file for this {language} function using {primary_framework}.

CRITICAL REQUIREMENTS:
- Generate ONLY the test code - NO intro text, NO explanations, NO TODO comments, NO placeholders
- The test must be 100% complete and executable without any manual modifications
- Focus on testing the ACTUAL changes described in the diff
- Include ALL necessary imports and dependencies
- Test the specific functionality that was modified
- Make sure the test runs successfully on the first try
- NO numbered explanations like "1. This test does..."
- NO "This test validates..." or "This function tests..." explanations
- NO text after the actual code - ONLY code until the end
{language_instructions}

Function code:
```{language}
{function_code}
```

Diff context (what was changed):
```diff
{diff_context}
```

Generate a complete test that:
1. Tests the ACTUAL functionality described in the diff
2. Has all necessary imports and dependencies
3. Sets up proper test fixtures with cleanup
4. Tests normal cases, edge cases, and error conditions
5. Is immediately runnable
6. Focuses on the specific changes made
7. Includes proper error handling
8. Has no TODO comments or assumptions

Output ONLY the complete test code, nothing else. The test should work immediately when executed."""

    @staticmethod
    def few_shot_prompt(function_code: str, examples: List[Dict[str, str]] = None, language: str = "python") -> str:
        if not examples:
            # Provide comprehensive examples for the specific language
            if language == "python":
                examples = [
                    {
                        "function": """def add(a: int, b: int) -> int:
    \"\"\"Add two integers together.\"\"\"
    return a + b""",
                        "test": """import pytest

def test_add():
    \"\"\"Test the add function with various inputs.\"\"\"
    # Test normal cases
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    
    # Test edge cases
    assert add(1000000, 2000000) == 3000000
    assert add(-100, -200) == -300
    
    # Test with zero
    assert add(5, 0) == 5
    assert add(0, 5) == 5"""
                    }
                ]
            elif language == "go":
                examples = [
                {
                        "function": """func Add(a int, b int) int {
    return a + b
}""",
                    "test": """package main

import "testing"

func TestAdd(t *testing.T) {
    // Test normal cases
    if result := Add(2, 3); result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
    
    if result := Add(-1, 1); result != 0 {
        t.Errorf("Expected 0, got %d", result)
    }
    
    if result := Add(0, 0); result != 0 {
        t.Errorf("Expected 0, got %d", result)
    }
    
    // Test edge cases
    if result := Add(1000000, 2000000); result != 3000000 {
        t.Errorf("Expected 3000000, got %d", result)
    }
    
    if result := Add(-100, -200); result != -300 {
        t.Errorf("Expected -300, got %d", result)
    }
}"""
                    }
                ]
            elif language == "cpp":
                examples = [
                    {
                        "function": """class StringUtils {
public:
    static std::string reverse(const std::string& str) {
        std::string result = str;
        std::reverse(result.begin(), result.end());
        return result;
    }
    
    static bool isEmpty(const std::string& str) {
        return str.empty();
    }
};""",
                        "test": """#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <string>
#include <vector>
#include "StringUtils.h"

class StringUtilsTest : public ::testing::Test {
protected:
    void SetUp() override {
        test_strings = {"hello", "world", "abc", "12345", ""};
        empty_string = "";
        single_char = "a";
        long_string = "this is a very long string for testing purposes";
    }
    
    void TearDown() override {
        test_strings.clear();
    }
    
    std::vector<std::string> test_strings;
    std::string empty_string;
    std::string single_char;
    std::string long_string;
};

TEST_F(StringUtilsTest, ReverseBasicStrings) {
    EXPECT_EQ(StringUtils::reverse("hello"), "olleh");
    EXPECT_EQ(StringUtils::reverse("world"), "dlrow");
    EXPECT_EQ(StringUtils::reverse("abc"), "cba");
}

TEST_F(StringUtilsTest, ReverseEdgeCases) {
    EXPECT_EQ(StringUtils::reverse(""), "");
    EXPECT_EQ(StringUtils::reverse("a"), "a");
    EXPECT_EQ(StringUtils::reverse("12345"), "54321");
}

TEST_F(StringUtilsTest, ReverseLongString) {
    std::string reversed = StringUtils::reverse(long_string);
    EXPECT_EQ(reversed, "sesoprup gnitset rof gnirts gnol yrev a si siht");
    EXPECT_EQ(reversed.length(), long_string.length());
}

TEST_F(StringUtilsTest, IsEmptyFunction) {
    EXPECT_TRUE(StringUtils::isEmpty(""));
    EXPECT_FALSE(StringUtils::isEmpty("hello"));
    EXPECT_FALSE(StringUtils::isEmpty(" "));
    EXPECT_FALSE(StringUtils::isEmpty("a"));
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}"""
                    }
                ]
            elif language == "java":
                examples = [
                    {
                        "function": """public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }
}""",
                        "test": """import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    
    @Test
    void testBasicAddition() {
        assertEquals(5, Calculator.add(2, 3));
        assertEquals(0, Calculator.add(-1, 1));
        assertEquals(0, Calculator.add(0, 0));
    }
    
    @Test
    void testEdgeCases() {
        assertEquals(3000000, Calculator.add(1000000, 2000000));
        assertEquals(-300, Calculator.add(-100, -200));
    }
    
    @Test
    void testZeroHandling() {
        assertEquals(5, Calculator.add(5, 0));
        assertEquals(5, Calculator.add(0, 5));
    }
}"""
                    }
                ]
            else:
                examples = [
                    {
                        "function": """function add(a, b) {
    return a + b;
}""",
                        "test": """describe('add function', () => {
    test('should add two positive numbers', () => {
        expect(add(2, 3)).toBe(5);
    });
    
    test('should handle negative numbers', () => {
        expect(add(-1, 1)).toBe(0);
        expect(add(-100, -200)).toBe(-300);
    });
    
    test('should handle zero', () => {
        expect(add(5, 0)).toBe(5);
        expect(add(0, 5)).toBe(5);
        expect(add(0, 0)).toBe(0);
    });
    
    test('should handle large numbers', () => {
        expect(add(1000000, 2000000)).toBe(3000000);
    });
});"""
                }
            ]
        
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
Example {i}:
Function:
{example['function']}

Complete Test:
{example['test']}
"""
        
        return f"""You are a senior test engineer. Here are examples of complete, runnable tests:

{examples_text}

Now generate a COMPLETE, RUNNABLE test for this function:
```{language}
{function_code}
```

CRITICAL REQUIREMENTS:
- Follow the same pattern as the examples above
- Generate ONLY the test code - NO intro text, NO explanations, NO TODO comments
- The test must be 100% complete and executable without any manual modifications
- Include ALL necessary imports and dependencies
- Test normal cases, edge cases, and error conditions
- Make sure the test runs successfully on the first try

Generate ONLY the complete test code, nothing else. The test should work immediately when executed."""

    @staticmethod
    def chain_of_thought_prompt(function_code: str, language: str = "python") -> str:
        from .language_detector import LanguageDetector
        
        test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
        primary_framework = test_frameworks[0] if test_frameworks else "standard"
        
        # Language-specific instructions
        language_instructions = ""
        if language.lower() == 'cpp':
            language_instructions = """
C++ SPECIFIC REQUIREMENTS - CRITICAL:
- Use Google Test (gtest) framework: #include <gtest/gtest.h>
- Test class should inherit from ::testing::Test
- Use TEST() macro for simple tests: TEST(TestSuiteName, TestName)
- Use TEST_F() macro for fixture-based tests: TEST_F(TestFixtureName, TestName)
- Include proper headers: #include <gtest/gtest.h>, #include <gmock/gmock.h>
- Use EXPECT_* and ASSERT_* macros for assertions
- Include the source file being tested: #include "filename.cpp" or #include "filename.h"
- Use proper C++ syntax and modern C++ features
- Include necessary standard library headers: #include <vector>, #include <string>, etc.

🚨 ABSOLUTELY FORBIDDEN FOR C++:
- NO placeholder comments like "// Set up your test here" or "// Test logic here"
- NO generic test templates without actual logic
- NO "// TODO" or "// FIXME" comments
- NO empty test functions with just EXPECT_TRUE(true)
- NO comments like "// Clean up after test here"

✅ REQUIRED FOR C++:
- Write ACTUAL test logic based on the function being tested
- Test the specific functionality with real assertions
- Include meaningful test data and edge cases
- Test both success and failure scenarios
- Use proper C++ test patterns and assertions
- Make tests that actually validate the function behavior
- Write complete SetUp() and TearDown() methods with actual initialization code
"""
        elif language.lower() == 'java':
            language_instructions = """
JAVA SPECIFIC REQUIREMENTS:
- Use JUnit 5: import org.junit.jupiter.api.Test, import org.junit.jupiter.api.BeforeEach
- Use proper JUnit annotations: @Test, @BeforeEach, @AfterEach, @BeforeAll, @AfterAll
- Use Assertions class: import static org.junit.jupiter.api.Assertions.*
- Use proper Java syntax and modern Java features
- Include necessary imports for the class being tested
"""
        elif language.lower() == 'go':
            language_instructions = """
GO SPECIFIC REQUIREMENTS:
- Use Go testing package: import "testing"
- Test functions should be named TestFunctionName
- Use testing.T for test functions: func TestFunctionName(t *testing.T)
- Use proper Go assertions: if got != want { t.Errorf("got %v, want %v", got, want) }
- Use testify if available: import "github.com/stretchr/testify/assert"
- Include necessary imports for the package being tested
"""
        
        return f"""You are a senior test engineer. Analyze this function step by step and then write a COMPLETE, RUNNABLE unit test.

CRITICAL REQUIREMENTS:
- Generate ONLY the test code - NO explanations, NO intro text, NO TODO comments
- The test must be 100% complete and executable without any manual modifications
- Include ALL necessary imports and dependencies
- Test normal cases, edge cases, and error conditions
- Make sure the test runs successfully on the first try
{language_instructions}

Function:
```{language}
{function_code}
```

Analysis Steps:
1. What are the inputs and their types?
2. What is the expected output?
3. What edge cases should be tested?
4. What error conditions should be handled?
5. What dependencies and imports are needed?

Now write the COMPLETE test code using {primary_framework}:
- Include all necessary imports
- Set up proper test fixtures
- Test all identified cases
- Include proper cleanup
- Make it immediately runnable

Output ONLY the complete test code, nothing else. The test should work immediately when executed."""

class PromptStrategy:
    
    def __init__(self):
        self.templates = PromptTemplates()
        self.strategies = {
            "naive": self.templates.naive_prompt,
            "diff-aware": self.templates.diff_aware_prompt,
            "few-shot": self.templates.few_shot_prompt,
            "cot": self.templates.chain_of_thought_prompt,
            # All strategies now use enhanced context processing by default
        }
    
    def get_prompt(self, strategy: str, **kwargs) -> str:
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Get the strategy function
        strategy_func = self.strategies[strategy]
        
        # Handle different parameter requirements for different strategies
        if strategy == "diff-aware":
            return strategy_func(kwargs.get('function_code', ''), kwargs.get('diff_context', ''), kwargs.get('language', 'python'))
        elif strategy == "few-shot":
            return strategy_func(kwargs.get('function_code', ''), kwargs.get('examples', None), kwargs.get('language', 'python'))
        # All strategies now use enhanced context processing by default
        # The enhanced_context_prompt is used internally by the agent
        else:
            return strategy_func(kwargs.get('function_code', ''), kwargs.get('language', 'python'))
    
    def get_all_strategies(self) -> List[str]:
        return list(self.strategies.keys())
    
    def compare_strategies(self, function_code: str, diff_context: str = "", language: str = "python") -> Dict[str, str]:
        prompts = {}
        
        for strategy in self.strategies:
            try:
                if strategy == "diff-aware":
                    prompts[strategy] = self.strategies[strategy](function_code, diff_context, language)
                elif strategy == "few-shot":
                    prompts[strategy] = self.strategies[strategy](function_code, language) # Few-shot doesn't take examples as a separate arg
                # All strategies now use enhanced context processing by default
                else:
                    prompts[strategy] = self.strategies[strategy](function_code, language)
            except Exception as e:
                prompts[strategy] = f"Error generating prompt for {strategy}: {str(e)}"
        
        return prompts
