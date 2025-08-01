from typing import Dict, List, Any

class PromptTemplates:
    """Collection of prompt templates for different strategies."""
    
    @staticmethod
    def naive_prompt(function_code: str) -> str:
        """Simple naive prompt for test generation."""
        return 


    @staticmethod
    def diff_aware_prompt(function_code: str, diff_context: str) -> str:
        """Diff-aware prompt that includes context about what changed."""
        return 
    


    @staticmethod
    def few_shot_prompt(function_code: str, examples: List[Dict[str, str]] = None) -> str:
        """Few-shot prompt with examples."""
        
        
        return 






    @staticmethod
    def chain_of_thought_prompt(function_code: str) -> str:
        """Chain of thought prompt that encourages step-by-step analysis."""
        return 




    @staticmethod
    def tdd_prompt(function_spec: str) -> str:
        """Test-driven development prompt."""
        return 




    @staticmethod
    def documentation_prompt(function_code: str, function_name: str) -> str:
        """Prompt for generating documentation."""
        return 
    


    @staticmethod
    def readme_prompt(module_name: str, functions: List[Dict[str, str]]) -> str:
        """Prompt for generating documentation."""
        functions_text = ""
        for func in functions:
            functions_text += f"- `{func['name']}`: {func['description']}\n"
        
        return 
    



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
