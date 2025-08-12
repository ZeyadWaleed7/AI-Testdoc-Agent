import logging
from typing import List, Dict, Any
from huggingface_hub import InferenceClient
import os
import time
import random

class PhindCodeLlamaLLM:
    """h2oai/h2ogpt-16k-codellama-13b-python model for text generation using Hugging Face InferenceClient with multiple provider options."""
    
    def __init__(self, model_name: str = "h2oai/h2ogpt-16k-codellama-13b-python", api_token: str = None, provider: str = "featherless-ai"):
        self.model_name = model_name
        self.provider = provider
        # Use provided token or default to the hardcoded one
        self.api_token = api_token or "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"
        
        # Set environment variable for the token
        os.environ["HF_TOKEN"] = self.api_token
        
        logging.info(f"Initializing Hugging Face InferenceClient with {provider} provider")
        logging.info(f"Using model: {model_name}")
        logging.info(f"Using HF_TOKEN: {self.api_token[:10]}...")
        
        try:
            # Initialize the InferenceClient with specified provider
            self.client = InferenceClient(provider=provider, api_key=self.api_token)
            logging.info(f"✅ InferenceClient initialized successfully with {provider}!")
        except Exception as e:
            logging.error(f"❌ Failed to initialize InferenceClient with {provider}: {e}")
            # Try fallback to default provider
            try:
                logging.info("Trying fallback to default provider...")
                self.client = InferenceClient(api_key=self.api_token)
                self.provider = "default"
                logging.info("✅ InferenceClient initialized with default provider!")
            except Exception as fallback_error:
                logging.error(f"❌ Fallback also failed: {fallback_error}")
                raise
    
    def generate(self, messages: List[Dict[str, str]], max_new_tokens: int = 512, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                # Convert messages to Alpaca/Vicuna format as specified in the model documentation
                prompt = self._messages_to_alpaca_format(messages)
                
                # Generate text using the remote InferenceClient
                result = self.client.text_generation(
                    prompt, 
                    model=self.model_name, 
                    max_new_tokens=max_new_tokens
                )
                
                # Extract the generated text from the result
                if hasattr(result, 'generated_text'):
                    generated_text = result.generated_text
                elif isinstance(result, str):
                    generated_text = result
                else:
                    generated_text = str(result)
                
                # Remove the input prompt from the response if it's included
                if prompt in generated_text:
                    generated_text = generated_text.replace(prompt, "").strip()
                
                return generated_text
                    
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"All {max_retries} attempts failed. Last error: {e}")
                    # Generate fallback content when API fails
                    return self._generate_fallback_content(messages)
        
        return "Error: All attempts failed"
    
    def _generate_fallback_content(self, messages: List[Dict[str, str]]) -> str:
        """Generate basic fallback content when the API fails."""
        try:
            # Extract the last user message to understand what was requested
            user_message = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_message = msg["content"]
                    break
            
            if "test" in user_message.lower():
                return """# Basic Test Template
import pytest

def test_function_basic():
    \"\"\"Basic test template - please implement specific test cases\"\"\"
    # TODO: Add proper test cases based on the function
    pass

def test_function_edge_cases():
    \"\"\"Test edge cases and error conditions\"\"\"
    # TODO: Add edge case tests
    pass"""
            elif "documentation" in user_message.lower():
                return """# Function Documentation

## Overview
This function needs proper documentation. Please review the code and add:

## Parameters
- Add parameter descriptions

## Returns
- Add return value description

## Examples
- Add usage examples

## Notes
- Add any important notes or warnings"""
            else:
                return "# Content generation failed. Please review and add content manually."
                
        except Exception as e:
            logging.error(f"Error generating fallback content: {e}")
            return "# Error: Unable to generate content. Please add manually."
    
    def _messages_to_alpaca_format(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Alpaca/Vicuna instruction format as specified in the model documentation."""
        prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt += f"### System Prompt\n{content}\n\n"
            elif role == "user":
                prompt += f"### User Message\n{content}\n\n"
            elif role == "assistant":
                prompt += f"### Assistant\n{content}\n\n"
        
        prompt += "### Assistant\n"
        return prompt
    
    def generate_test(self, function_code: str, diff_context: str = "", prompt_strategy: str = "diff-aware") -> str:
        messages = [
            {"role": "system", "content": "You are an expert Python developer who writes high-quality unit tests."},
            {"role": "user", "content": f"Generate comprehensive unit tests for this function:\n\n{function_code}\n\nDiff context:\n{diff_context}"}
        ]
        
        return self.generate(messages, max_new_tokens=1024, max_retries=3)
    
    def generate_documentation(self, function_code: str, function_name: str) -> str:
        messages = [
            {"role": "system", "content": "You are an expert technical writer who creates clear documentation."},
            {"role": "user", "content": f"Generate documentation for this function:\n\n{function_code}"}
        ]
        
        return self.generate(messages, max_new_tokens=512, max_retries=3) 