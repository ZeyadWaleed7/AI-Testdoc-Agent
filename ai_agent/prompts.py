from typing import Dict, List, Any

class PromptTemplates:
    """Collection of prompt templates for different strategies."""
    
    @staticmethod
    def naive_prompt(function_code: str) -> str:
        """Simple naive prompt for test generation."""
        return f"""Write a comprehensive unit test for this function:

{function_code}

Please include:
- Test cases for normal operation
- Edge cases
- Error conditions
- Clear test names and descriptions"""


    @staticmethod
    def diff_aware_prompt(function_code: str, diff_context: str) -> str:
        """Diff-aware prompt that includes context about what changed."""
        return f"""Write a comprehensive unit test for this function. 
Here's the function code:
{function_code}

Here's what changed in the diff:
{diff_context}

Please write tests that:
- Cover the new functionality added in the diff
- Test the specific changes made
- Include edge cases related to the modifications
- Ensure backward compatibility if applicable
- Test error conditions that might arise from the changes"""
    


    @staticmethod
    def few_shot_prompt(function_code: str, examples: List[Dict[str, str]] = None) -> str:
        """Few-shot prompt with examples."""
        if not examples:
            examples = [
                {
                    "function": """def add(a: int, b: int) -> int:
    return a + b""",
                    "test": """def test_add():
    # Test normal operation
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    
    # Test edge cases
    assert add(0, 0) == 0
    assert add(1000000, 1000000) == 2000000
    
    # Test with negative numbers
    assert add(-5, -3) == -8"""
                },
                {
                    "function": """def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))""",
                    "test": """def test_validate_email():
    # Test valid emails
    assert validate_email("user@example.com") == True
    assert validate_email("test.email+tag@domain.co.uk") == True
    
    # Test invalid emails
    assert validate_email("invalid-email") == False
    assert validate_email("@domain.com") == False
    assert validate_email("user@") == False
    assert validate_email("") == False"""
                }
            ]
        
        examples_text = ""
        for i, example in enumerate(examples, 1):
            examples_text += f"""
Example {i}:
Function:
{example['function']}

Test:
{example['test']}
"""
        
        return f"""Here are some examples of functions and their tests:

{examples_text}

Now write a comprehensive test for this function:
{function_code}

Follow the same pattern as the examples above."""






    @staticmethod
    def chain_of_thought_prompt(function_code: str) -> str:
        """Chain of thought prompt that encourages step-by-step analysis."""
        return f"""Analyze this function step by step and then write comprehensive unit tests.

Function:
{function_code}

Step 1: What are the inputs and their types?
Step 2: What is the expected output?
Step 3: What edge cases should be tested?
Step 4: What error conditions might occur?
Step 5: What are the different code paths that need coverage?

Now write comprehensive unit tests based on your analysis above."""




    @staticmethod
    def tdd_prompt(function_spec: str) -> str:
        """Test-driven development prompt."""
        return f"""Write unit tests for this function specification before the implementation:

Function Specification:
{function_spec}

Please write tests that:
- Define the expected behavior
- Cover all requirements from the specification
- Include edge cases and error conditions
- Follow TDD principles (test first, then implement)
- Use descriptive test names that explain the requirement being tested"""




    @staticmethod
    def documentation_prompt(function_code: str, function_name: str) -> str:
        """Prompt for generating documentation."""
        return  f"""Write comprehensive documentation for this function:

{function_code}

Please provide:
1. Parameter descriptions with types and constraints
2. Return value description with type and meaning
3. Usage examples showing typical use cases
4. Any important notes, warnings, or dependencies
5. Edge cases and error conditions to be aware of

Make the documentation clear, complete, and helpful for developers using this function."""
    


    @staticmethod
    def readme_prompt(module_name: str, functions: List[Dict[str, str]]) -> str:
        """Prompt for generating documentation."""
        functions_text = ""
        for func in functions:
            functions_text += f"- `{func['name']}`: {func['description']}\n"
        
        return f"""Generate a README section for the {module_name} module.

Functions in this module:
{functions_text}

Please provide:
1. A brief overview of what this module does and its purpose
2. Installation/usage instructions if relevant
3. API documentation for each function with examples
4. Common use cases and examples
5. Any important notes, dependencies, or requirements
6. Troubleshooting section if applicable

Make it comprehensive and developer-friendly."""
    



class PromptStrategy:
    """Manages different prompting strategies."""
    
    def __init__(self):
        self.templates = PromptTemplates()
        self.strategies = {
            "naive": self.templates.naive_prompt,
            "diff-aware": self.templates.diff_aware_prompt,
            "few-shot": self.templates.few_shot_prompt,
            "cot": self.templates.chain_of_thought_prompt,
            "tdd": self.templates.tdd_prompt
        }
    
    def get_prompt(self, strategy: str, **kwargs) -> str:
        """
        Get a prompt for the specified strategy.
        
        Args:
            strategy: Name of the strategy
            **kwargs: Arguments for the prompt template
            
        Returns:
            Generated prompt text
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return self.strategies[strategy](**kwargs)
    
    def get_all_strategies(self) -> List[str]:
        """Get list of all available strategies."""
        return list(self.strategies.keys())
    
    def compare_strategies(self, function_code: str, diff_context: str = "") -> Dict[str, str]:
        """
        Generate prompts for all strategies for comparison.
        
        Args:
            function_code: The function code
            diff_context: Git diff context
            
        Returns:
            Dictionary mapping strategy names to prompts
        """
        prompts = {}
        
        for strategy in self.strategies:
            try:
                if strategy == "diff-aware":
                    prompts[strategy] = self.strategies[strategy](function_code, diff_context)
                elif strategy == "few-shot":
                    prompts[strategy] = self.strategies[strategy](function_code)
                else:
                    prompts[strategy] = self.strategies[strategy](function_code)
            except Exception as e:
                prompts[strategy] = f"Error generating prompt for {strategy}: {str(e)}"
        
        return prompts
