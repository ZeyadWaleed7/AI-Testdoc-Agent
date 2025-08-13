# ai_agent/llm.py
from __future__ import annotations

import os
import time
import random
import logging
from typing import List, Dict, Union, Optional

from huggingface_hub import InferenceClient

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None else default


class PhindCodeLlamaLLM:
    """
    provider:
      - "hf-inference" -> Hugging Face Inference API
      - "local"        -> transformers (CPU by default to avoid MPS crashes)
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
    # Public generate()
    # ---------------------------
    def generate(
        self,
        messages: Union[str, List[Dict[str, str]]],
        max_new_tokens: int = 512,
        max_retries: int = 3,
        temperature: float = 0.2,
    ) -> str:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if self.provider == "local":
            return self._generate_local(messages, max_new_tokens, max_retries, temperature)
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
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logging.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"All {max_retries} attempts failed locally. Last error: {last_exc}")
                return self._generate_fallback_content(messages)

        return "Error: All attempts failed"

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
    ) -> str:
        messages = [
            {"role": "system", "content": "You are an expert Python developer who writes high-quality unit tests."},
            {
                "role": "user",
                "content": (
                    "Generate comprehensive unit tests for this function:\n\n"
                    f"{function_code}\n\n"
                    f"Diff context:\n{diff_context}"
                ),
            },
        ]
        return self.generate(messages, max_new_tokens=512, max_retries=3, temperature=0.2)

    def generate_documentation(self, function_code: str, function_name: str) -> str:
        messages = [
            {"role": "system", "content": "You are an expert technical writer who creates clear documentation."},
            {"role": "user", "content": f"Generate documentation for this function:\n\n{function_code}"},
        ]
        return self.generate(messages, max_new_tokens=400, max_retries=3, temperature=0.2)
