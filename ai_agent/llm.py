from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any
import logging

class CodeLlamaLLM:
    """CodeLlama model for text generation."""
    
    def __init__(self, model_name: str = "codellama/CodeLlama-13b-Instruct-hf", auth_token: str = None):
        self.model_name = model_name
        self.auth_token = auth_token
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        try:
            logging.info(f"Loading CodeLlama model: {self.model_name}")
            
            if self.auth_token:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    use_auth_token=self.auth_token
                )
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            model_kwargs = {
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None
            }
            
            if self.auth_token:
                model_kwargs["use_auth_token"] = self.auth_token
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            logging.info("Model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise
    
    def generate(self, messages: List[Dict[str, str]], max_new_tokens: int = 512) -> str:
        try:
            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[-1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logging.error(f"Error generating text: {e}")
            return f"Error: {str(e)}"
    
    def generate_test(self, function_code: str, diff_context: str = "", prompt_strategy: str = "diff-aware") -> str:
        messages = [
            {"role": "system", "content": "You are an expert Python developer who writes high-quality unit tests."},
            {"role": "user", "content": f"Generate comprehensive unit tests for this function:\n\n{function_code}\n\nDiff context:\n{diff_context}"}
        ]
        
        return self.generate(messages, max_new_tokens=1024)
    
    def generate_documentation(self, function_code: str, function_name: str) -> str:
        messages = [
            {"role": "system", "content": "You are an expert technical writer who creates clear documentation."},
            {"role": "user", "content": f"Generate documentation for this function:\n\n{function_code}"}
        ]
        
        return self.generate(messages, max_new_tokens=512) 