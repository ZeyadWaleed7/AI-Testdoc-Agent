from __future__ import annotations

import os
import json
import logging
import time
import random
import requests
from typing import List, Dict, Union, Optional

from huggingface_hub import InferenceClient

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def _env(key: str, default: str = "") -> str:
    """Get environment variable with default"""
    return os.environ.get(key, default)


class PhindCodeLlamaLLM:
    """
    provider:
      - "hf-inference" -> Hugging Face Inference API
      - "local"        -> transformers (CPU by default to avoid MPS crashes)
      - "ollama"       -> Ollama local models (e.g., deepseek-coder)
    """

    def __init__(
        self,
        model_name: str = "h2oai/h2ogpt-16k-codellama-13b-python",
        api_token: Optional[str] = None,
        provider: str = "hf-inference",
    ):
        self.model_name = model_name
        self.provider = provider.lower().strip()
        self.api_token = api_token or _env("HF_TOKEN", "")
        os.environ["HF_TOKEN"] = self.api_token

        logging.info(f"Initializing LLM with provider={self.provider}")
        logging.info(f"Using model: {self.model_name}")
        logging.info(f"Using HF_TOKEN: {self.api_token[:10]}...")

        if self.provider == "local":
            self._init_local()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            self._init_remote()

    # ---------------------------
    # Remote (HF Inference API)
    # ---------------------------
    def _init_remote(self):
        try:
            self.client = InferenceClient(
                model=self.model_name,
                token=self.api_token,
                provider="hf-inference",
            )
            logging.info("✅ InferenceClient (hf-inference) initialized.")
        except Exception as e:
            logging.error(f"❌ Failed to init InferenceClient: {e}")
            raise

    # ---------------------------
    # Local (Transformers)
    # ---------------------------
    def _init_local(self):
        # Default to CPU; MPS can crash with 4GB NDArray assertion on Mac.
        wanted = _env("AI_AGENT_DEVICE", "cpu").lower()
        if wanted not in {"cpu", "cuda", "mps"}:
            wanted = "cpu"

        if wanted == "cuda" and not torch.cuda.is_available():
            logging.warning("CUDA not available; falling back to CPU.")
            wanted = "cpu"
        if wanted == "mps" and not torch.backends.mps.is_available():
            logging.warning("MPS not available; falling back to CPU.")
            wanted = "cpu"

        self.local_device = wanted
        logging.info(f"Local backend device: {self.local_device}")

        dtype = torch.float32
        if self.local_device == "cuda":
            dtype = torch.float16

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True,
            trust_remote_code=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            device_map=self.local_device if self.local_device != "cpu" else None,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            attn_implementation="eager",
        )

        if self.local_device == "cpu":
            self.model.to("cpu")

        # Conservative defaults to constrain memory
        self.gen_defaults = {
            "temperature": 0.2,
            "top_p": 0.9,
            "do_sample": True,
            "repetition_penalty": 1.05,
        }

        # Truncate long prompts to avoid big tensors
        self.max_input_tokens = int(_env("AI_AGENT_MAX_INPUT_TOKENS", "1024"))

        # Optional CPU threading
        torch.set_num_threads(int(_env("AI_AGENT_TORCH_THREADS", "4")))

        logging.info("✅ Local Transformers pipeline initialized.")

    # ---------------------------
    # Ollama
    # ---------------------------
    def _init_ollama(self):
        try:
            import requests
            self.ollama_url = _env("OLLAMA_URL", "http://localhost:11434")
            self.ollama_model = self.model_name
            
            # Test connection to Ollama
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=30)
            if response.status_code == 200:
                logging.info(f"Ollama connection established at {self.ollama_url}")
                logging.info(f"Using model: {self.ollama_model}")
                
                # Check if the specific model is available and loaded
                models_response = requests.get(f"{self.ollama_url}/api/tags", timeout=30)
                if models_response.status_code == 200:
                    models = models_response.json().get("models", [])
                    model_found = any(model.get("name") == self.ollama_model for model in models)
                    if model_found:
                        logging.info(f"Model {self.ollama_model} is available")
                    else:
                        logging.warning(f"Model {self.ollama_model} not found in available models")
                        logging.info("Available models: " + ", ".join([m.get("name", "unknown") for m in models]))
                else:
                    logging.warning("Could not check available models")
                
                # Warm up the model with a simple request to ensure it's loaded
                try:
                    warmup_payload = {
                        "model": self.ollama_model,
                        "prompt": "Hello",
                        "stream": False,
                        "options": {"num_predict": 10}
                    }
                    warmup_response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=warmup_payload,
                        timeout=60
                    )
                    if warmup_response.status_code == 200:
                        logging.info(f"Model {self.ollama_model} is loaded and responding")
                    else:
                        logging.warning(f"Model warm-up failed with status {warmup_response.status_code}")
                except Exception as warmup_e:
                    logging.warning(f"Model warm-up failed: {warmup_e}")
                    
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
        except Exception as e:
            logging.error(f"Failed to connect to Ollama: {e}")
            logging.error("Make sure Ollama is running: ollama serve")
            logging.error(f"Make sure the model is available: ollama list")
            raise

    # ---------------------------
    # Public generate()
    # ---------------------------
    def generate(
        self,
        messages: Union[str, List[Dict[str, str]]],
        max_new_tokens: int = 512,
        max_retries: int = 3,
        temperature: float = 0.2,
        stop: Optional[List[str]] = None,
    ) -> str:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if self.provider == "local":
            return self._generate_local(messages, max_new_tokens, max_retries, temperature)
        elif self.provider == "ollama":
            return self._generate_ollama(messages, max_new_tokens, max_retries, stop=stop)
        else:
            return self._generate_remote(messages, max_new_tokens, max_retries, temperature)

    # ---------------------------
    # Remote generation
    # ---------------------------
    def _generate_remote(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int,
        max_retries: int,
        temperature: float,
    ) -> str:
        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_new_tokens,
                    temperature=temperature,
                )
                text = resp.choices[0].message.content
                if text:
                    return text.strip()
            except Exception as e:
                last_exc = e
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logging.info(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"All {max_retries} attempts failed. Last error: {e}")
                    return self._generate_fallback_content(messages)
        return "Error: All attempts failed"

    # ---------------------------
    # Local generation
    # ---------------------------
    def _generate_local(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int,
        max_retries: int,
        temperature: float,
    ) -> str:
        # Build chat prompt using tokenizer's chat template
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            parts = []
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                parts.append(f"{role.upper()}: {content}")
            prompt = "\n".join(parts) + "\nASSISTANT:"

        last_exc: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                enc = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.max_input_tokens,
                )
                input_ids = enc["input_ids"]
                if self.local_device == "cuda":
                    input_ids = input_ids.to("cuda")
                elif self.local_device == "mps":
                    input_ids = input_ids.to("mps")
                else:
                    input_ids = input_ids.to("cpu")

                # Merge defaults with call-time args
                gen_kwargs = dict(self.gen_defaults)
                gen_kwargs.update(
                    dict(
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        use_cache=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                    )
                )

                with torch.no_grad():
                    out_ids = self.model.generate(
                        input_ids=input_ids,
                        **gen_kwargs,
                    )

                gen_ids = out_ids[:, input_ids.shape[-1]:]
                text = self.tokenizer.decode(gen_ids[0], skip_special_tokens=True)
                return text.strip() if text else ""

            except AssertionError as e:
                last_exc = e
                # Handle MPS NDArray crash by switching to CPU
                if "MPSTemporaryNDArray" in str(e) and self.local_device == "mps":
                    logging.warning("MPS assertion hit; switching to CPU for generation.")
                    self.local_device = "cpu"
                    self.model.to("cpu")
                    continue
                logging.warning(f"Attempt {attempt + 1} failed with AssertionError: {e}")
            except Exception as e:
                last_exc = e
                logging.warning(f"Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                # For Ollama, use longer delays to allow model to stabilize
                if self.provider == "ollama":
                    wait_time = (5 ** attempt) + random.uniform(2, 5)  # 5s, 25s, 125s + random
                else:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                logging.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"All {max_retries} attempts failed locally. Last error: {last_exc}")
                return self._generate_fallback_content(messages)

        return "Error: All attempts failed"

    # ---------------------------
    # Ollama generation
    # ---------------------------
    def _generate_ollama(self, messages, max_new_tokens=2048, max_retries=3, stop=None, num_predict=None):
        """Generate text using Ollama API with retries and error handling"""
        if not hasattr(self, 'ollama_url') or not self.ollama_url:
            raise RuntimeError("Ollama not initialized. Call _init_ollama() first.")
        
        # Convert messages to prompt format for Ollama
        if hasattr(self, '_messages_to_prompt'):
            prompt = self._messages_to_prompt(messages)
        else:
            # Fallback: use the last user message or concatenate all
            if isinstance(messages, list) and messages:
                prompt = messages[-1].get('content', str(messages))
            else:
                prompt = str(messages)
        
        # Log generation parameters
        logging.info(f"Generating with Ollama - Model: {self.ollama_model}, Max tokens: {max_new_tokens}, Temperature: 0.0")
        logging.info(f"Prompt length: {len(prompt)} characters")
        
        # Prepare the request payload
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,  # User specified: deterministic generation
                "top_p": 1.0,        # User specified: allow full vocabulary
                "repeat_penalty": 1.0,
                "num_predict": 3072  # User specified: max tokens
            }
        }
        
        # Add stop sequences if provided
        if stop:
            payload["options"]["stop"] = stop
            logging.info(f"Using stop sequences: {stop}")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempt {attempt + 1}/{max_retries} - Generating with Ollama (temp=0.0, top_p=1.0, max_tokens=3072)")
                
                # Make the request with reasonable timeout (10 minutes)
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=600,  # 10 minutes timeout - sufficient for focused prompts
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get('response', '')
                    
                    if generated_text and generated_text.strip():
                        logging.info(f"Successfully generated {len(generated_text)} characters")
                        return generated_text
                    else:
                        logging.warning("Generated text is empty, retrying...")
                        last_error = "Empty response"
                        
                else:
                    error_msg = f"status {response.status_code}: {response.text}"
                    logging.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                    last_error = error_msg
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Attempt {attempt + 1} failed: timeout after 10 minutes")
                last_error = "timeout after 10 minutes"
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                last_error = str(e)
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                last_error = str(e)
            
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = 1 + random.random()
                logging.info(f"Waiting {wait_time:.1f} seconds before retry...")
                time.sleep(wait_time)
        
        logging.error(f"All {max_retries} attempts failed. Last error: {last_error}")
        logging.error("This may indicate:")
        logging.error("1. Ollama server is overloaded or slow")
        logging.error("2. The model is too large for your system")
        logging.error("3. Network connectivity issues")
        logging.error("4. The prompt is too complex (consider reducing context or using a smaller model)")
        raise RuntimeError(f"Ollama generation failed after {max_retries} attempts. Last error: {last_error}")

    # ---------------------------
    # Helper: messages -> prompt
    # ---------------------------
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Flatten chat-style messages into a single prompt string for models that require 'prompt'.
        Preference: return the latest user content if present; otherwise, concatenate all contents.
        """
        try:
            # Prefer the last user message content
            for m in reversed(messages):
                if m.get("role") == "user" and m.get("content"):
                    return str(m["content"])  # ensure plain string
            # Fallback: concatenate contents
            parts = []
            for m in messages:
                content = m.get("content", "")
                if not isinstance(content, str):
                    content = str(content)
                parts.append(content)
            return "\n\n".join(parts)
        except Exception:
            # As a last resort, stringify the whole object
            return str(messages)

    def _convert_messages_to_ollama_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Ollama prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"

    def _clean_response(self, response: str) -> str:
        """Clean verbose responses to extract only the code/documentation."""
        if not response:
            return response
        
        # Remove common verbose prefixes
        verbose_prefixes = [
            "Sure, I can provide you with",
            "Here's a comprehensive",
            "I'll help you create",
            "Let me write",
            "This is a simple example",
            "Here's how you can",
            "I'll generate",
            "Sure, here's",
            "Here's the",
            "I can help you",
            "Let me help you",
            "I'll create",
            "Here's what you need",
            "This function",
            "The function",
            "Based on the code",
            "Looking at the function",
            "For this function",
            "To test this function",
            "To document this function"
        ]
        
        cleaned = response
        for prefix in verbose_prefixes:
            if cleaned.startswith(prefix):
                # Find the first line that looks like code (starts with import, def, class, etc.)
                lines = cleaned.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ', 'def ', 'class ', 'test_', 'describe(', 'it(', 'expect(', 'assert ', '#')):
                        cleaned = '\n'.join(lines[i:])
                        break
        
        # Remove trailing explanations
        if '```' in cleaned:
            # Extract content between code blocks
            start = cleaned.find('```')
            if start != -1:
                end = cleaned.rfind('```')
                if end > start:
                    cleaned = cleaned[start+3:end].strip()
        
        return cleaned.strip()

    # ---------------------------
    # Fallback content
    # ---------------------------
    def _generate_fallback_content(self, messages: Union[str, List[Dict[str, str]]]) -> str:
        try:
            user_message = ""
            if isinstance(messages, str):
                user_message = messages
            else:
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break
            return f"[Placeholder response due to generation failure]\n{user_message}"
        except Exception:
            return "[Placeholder response due to generation failure]"

    # ---------------------------
    # Convenience wrappers
    # ---------------------------
    def generate_test(
        self,
        function_code: str,
        diff_context: str = "",
        prompt_strategy: str = "diff-aware",
        language: str = "python",
    ) -> str:
        # Get test framework for the language
        from .language_detector import LanguageDetector
        test_frameworks = LanguageDetector.get_test_frameworks_for_language(language)
        primary_framework = test_frameworks[0] if test_frameworks else "standard"
        
        system_prompt = f"""You are an expert {language} developer. Write ONLY the test code without any explanations, comments, or additional text. Generate clean, properly formatted {primary_framework} tests with correct syntax and indentation. Start directly with the test code."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Write ONLY the test code for this {language} function using {primary_framework}:\n\n"
                    f"{function_code}\n\n"
                    f"Diff context:\n{diff_context}\n\n"
                    f"Generate the test code directly without any explanations or comments."
                ),
            },
        ]
        response = self.generate(messages, max_new_tokens=512, max_retries=3, temperature=0.2)
        return self._clean_response(response)

    def generate_documentation(self, function_code: str, function_name: str) -> str:
        """Generate comprehensive documentation for any programming language"""
        try:
            # Detect programming language from function code
            language = self._detect_language_from_code(function_code)
            
            # Create language-specific documentation prompt
            if language == "python":
                system_prompt = "You are an expert Python technical writer. Generate comprehensive test documentation."
                user_prompt = f"""Generate comprehensive documentation for this Python test file:

{function_code}

Create a complete markdown documentation file with:
1. Overview of what the tests cover
2. Description of each test function
3. Test strategy and coverage
4. Setup and dependencies
5. Running instructions
6. Technical details

Generate ONLY the documentation content, no explanations."""
                
            elif language == "go":
                system_prompt = "You are an expert Go technical writer. Generate comprehensive test documentation."
                user_prompt = f"""Generate comprehensive documentation for this Go test file:

{function_code}

Create a complete markdown documentation file with:
1. Overview of what the tests cover
2. Description of each test function
3. Test strategy and coverage
4. Setup and dependencies
5. Running instructions
6. Technical details

Generate ONLY the documentation content, no explanations."""
                
            else:
                # Generic documentation for other languages
                system_prompt = f"You are an expert {language} technical writer. Generate comprehensive test documentation."
                user_prompt = f"""Generate comprehensive documentation for this {language} test file:

{function_code}

Create a complete markdown documentation file with:
1. Overview of what the tests cover
2. Description of each test function
3. Test strategy and coverage
4. Setup and dependencies
5. Running instructions
6. Technical details

Generate ONLY the documentation content, no explanations."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            response = self.generate(messages, max_new_tokens=1024, max_retries=3, temperature=0.1)
            cleaned_response = self._clean_response(response)
            
            # Ensure we have valid documentation content
            if not cleaned_response or len(cleaned_response.strip()) < 100:
                # Fallback to basic documentation
                return self._generate_fallback_documentation(function_code, function_name, language)
            
            return cleaned_response
            
        except Exception as e:
            # Fallback to basic documentation if anything fails
            return self._generate_fallback_documentation(function_code, function_name, "unknown")
    
    def _detect_language_from_code(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()
        
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'pytest', 'unittest']):
            return "python"
        elif any(keyword in code_lower for keyword in ['func ', 'package ', 'import ', 'testing.']):
            return "go"
        elif any(keyword in code_lower for keyword in ['function ', 'const ', 'let ', 'var ', 'describe(', 'it(']):
            return "javascript"
        elif any(keyword in code_lower for keyword in ['public class', 'public static', 'import java', '@Test']):
            return "java"
        elif any(keyword in code_lower for keyword in ['#include', 'int main', 'class ', 'namespace']):
            return "cpp"
        else:
            return "unknown"
    
    def _generate_fallback_documentation(self, function_code: str, function_name: str, language: str) -> str:
        """Generate basic fallback documentation if the main method fails"""
        try:
            lines = function_code.split('\n')
            test_functions = [line.strip() for line in lines if line.strip().startswith(('def test_', 'func Test', 'function test_', 'public void test'))]
            
            doc_content = f"""# Test File Documentation: {function_name}

## Overview
This test file contains {len(test_functions)} test functions for the {function_name} module.

## Test Functions
"""
            
            for func in test_functions[:10]:  # Limit to first 10 functions
                doc_content += f"- {func}\n"
            
            doc_content += f"""
## Language
{language.capitalize()}

## Running Tests
Run the tests using the appropriate test runner for {language}.

## Notes
This is automatically generated documentation. Please review and enhance as needed.
"""
            
            return doc_content
            
        except Exception:
            return f"# Test File Documentation: {function_name}\n\n## Overview\nThis test file contains tests for {function_name}.\n\n## Language\n{language.capitalize()}\n\n## Running Tests\nRun the tests using the appropriate test runner for {language}."

    def _build_prompt_from_messages(self, messages: List[Dict[str, str]]) -> str:
        """Build a prompt string from a list of messages"""
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        prompt = "\n".join(parts) + "\nASSISTANT:"
        return prompt





                





    def _convert_messages_to_ollama_prompt(self, messages: List[Dict[str, str]]) -> str:

        """Convert chat messages to Ollama prompt format."""

        prompt_parts = []

        

        for message in messages:

            role = message.get("role", "user")

            content = message.get("content", "")

            

            if role == "system":

                prompt_parts.append(f"System: {content}")

            elif role == "user":

                prompt_parts.append(f"User: {content}")

            elif role == "assistant":

                prompt_parts.append(f"Assistant: {content}")

        

        return "\n\n".join(prompt_parts) + "\n\nAssistant:"



    def _clean_response(self, response: str) -> str:

        """Clean verbose responses to extract only the code/documentation."""

        if not response:

            return response

        

        # Remove common verbose prefixes

        verbose_prefixes = [

            "Sure, I can provide you with",

            "Here's a comprehensive",

            "I'll help you create",

            "Let me write",

            "This is a simple example",

            "Here's how you can",

            "I'll generate",

            "Sure, here's",

            "Here's the",

            "I can help you",

            "Let me help you",

            "I'll create",

            "Here's what you need",

            "This function",

            "The function",

            "Based on the code",

            "Looking at the function",

            "For this function",

            "To test this function",

            "To document this function"

        ]

        

        cleaned = response

        for prefix in verbose_prefixes:

            if cleaned.startswith(prefix):

                # Find the first line that looks like code (starts with import, def, class, etc.)

                lines = cleaned.split('\n')

                for i, line in enumerate(lines):

                    if line.strip().startswith(('import ', 'from ', 'def ', 'class ', 'test_', 'describe(', 'it(', 'expect(', 'assert ', '#')):

                        cleaned = '\n'.join(lines[i:])

                        break

        

        # Remove trailing explanations

        if '```' in cleaned:

            # Extract content between code blocks

            start = cleaned.find('```')

            if start != -1:

                end = cleaned.rfind('```')

                if end > start:

                    cleaned = cleaned[start+3:end].strip()

        

        return cleaned.strip()



    # ---------------------------

    # Fallback content

    # ---------------------------

    def _generate_fallback_content(self, messages: Union[str, List[Dict[str, str]]]) -> str:

        try:

            user_message = ""

            if isinstance(messages, str):

                user_message = messages

            else:

                for msg in reversed(messages):

                    if msg.get("role") == "user":

                        user_message = msg.get("content", "")

                        break

            return f"[Placeholder response due to generation failure]\n{user_message}"

        except Exception:

            return "[Placeholder response due to generation failure]"



    # ---------------------------

    # Convenience wrappers

    # ---------------------------




