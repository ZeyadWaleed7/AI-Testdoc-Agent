import os
import logging
from typing import Dict, List, Any, Optional
from .llm import PhindCodeLlamaLLM
from .generator import TestGenerator
from .documentation import DocumentationGenerator
from .memory import MemoryModule
from .watcher import get_functions_from_diff_file, analyze_diff_changes
from .prompts import PromptStrategy

class AIAgent:
    def __init__(
        self,
        model_name: str = "h2oai/h2ogpt-16k-codellama-13b-python",
        api_token: Optional[str] = None,
        provider: str = "hf-inference",
    ):
        self.llm = PhindCodeLlamaLLM(model_name, api_token=api_token, provider=provider)
        self.test_generator = TestGenerator(self.llm)
        self.doc_generator = DocumentationGenerator(self.llm)
        self.memory = MemoryModule()
        self.prompt_strategy = PromptStrategy()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def process_diff_file(
        self,
        diff_file_path: str,
        output_dir: str = "generated",
        prompt_strategy: str = "diff-aware",
        generate_docs: bool = True,
    ) -> Dict[str, Any]:
        self.logger.info(f"Processing diff file: {diff_file_path}")

        os.makedirs(output_dir, exist_ok=True)

        with open(diff_file_path, "r", encoding="utf-8") as f:
            diff_content = f.read()

        analysis = analyze_diff_changes(diff_content)
        self.logger.info(f"Analysis: {analysis}")

        functions = get_functions_from_diff_file(diff_file_path)
        self.logger.info(f"Found {len(functions)} functions in diff")

        results = {
            "analysis": analysis,
            "functions": [],
            "generated_tests": {},
            "generated_docs": {},
            "memory_summary": self.memory.get_memory_summary(),
        }

        for function_name, function_code, file_path in functions:
            self.logger.info(f"Processing function: {function_name}")

            self.memory.store_function_context(
                function_name=function_name,
                file_path=file_path,
                diff_context=diff_content[:1000],
            )

            try:
                test_code = self.test_generator.generate_tests_for_function(
                    function_code=function_code,
                    function_name=function_name,
                    diff_context=diff_content,
                    prompt_strategy=prompt_strategy,
                )

                # treat empty/error placeholders as failures (don’t mark success)
                if not test_code or not test_code.strip() or test_code.strip().startswith("# Error"):
                    raise RuntimeError("Empty/errored test generation")

                self.memory.store_test_pattern(
                    function_name=function_name,
                    function_signature=function_code.split("\n")[0],
                    test_code=test_code,
                )

                results["generated_tests"][function_name] = test_code

                test_file_path = os.path.join(output_dir, f"test_{function_name}.py")
                with open(test_file_path, "w") as f:
                    f.write(test_code)

                if generate_docs:
                    try:
                        doc_content = self.doc_generator.generate_documentation(
                            function_code=function_code,
                            function_name=function_name,
                            diff_context=diff_content,
                        )
                        results["generated_docs"][function_name] = doc_content

                        doc_file_path = os.path.join(output_dir, f"doc_{function_name}.md")
                        with open(doc_file_path, "w") as f:
                            f.write(doc_content)

                    except Exception as doc_error:
                        self.logger.error(
                            f"Error generating documentation for {function_name}: {doc_error}"
                        )
                        doc_content = f"# Error generating documentation: {str(doc_error)}"
                        results["generated_docs"][function_name] = doc_content

                results["functions"].append(
                    {
                        "name": function_name,
                        "file_path": file_path,
                        "test_generated": True,
                        "doc_generated": generate_docs,
                    }
                )

                self.logger.info(f"Successfully processed function: {function_name}")

            except Exception as e:
                self.logger.error(f"Error processing function {function_name}: {e}")
                results["functions"].append(
                    {
                        "name": function_name,
                        "file_path": file_path,
                        "test_generated": False,
                        "doc_generated": False,
                        "error": str(e),
                    }
                )

                # fallback: write a minimal placeholder test so the pipeline still produces a file
                try:
                    basic_test = f"""# Basic test for {function_name}
import pytest

def test_{function_name}_basic():
    pass
"""
                    results["generated_tests"][function_name] = basic_test
                    test_file_path = os.path.join(output_dir, f"test_{function_name}.py")
                    with open(test_file_path, "w") as f:
                        f.write(basic_test)
                    self.logger.info(f"Generated basic test for {function_name}")
                except Exception as basic_test_error:
                    self.logger.error(
                        f"Failed to generate basic test for {function_name}: {basic_test_error}"
                    )

        return results

    def compare_prompt_strategies(
        self, diff_file_path: str, output_dir: str = "prompt_comparison"
    ) -> Dict[str, Any]:
        strategies = ["naive", "diff-aware", "few-shot", "cot", "tdd"]
        results: Dict[str, Any] = {}

        for strategy in strategies:
            strategy_dir = os.path.join(output_dir, strategy)
            os.makedirs(strategy_dir, exist_ok=True)

            try:
                strategy_results = self.process_diff_file(
                    diff_file_path=diff_file_path,
                    output_dir=strategy_dir,
                    prompt_strategy=strategy,
                    generate_docs=True,
                )
                results[strategy] = strategy_results

            except Exception as e:
                self.logger.error(f"Error with strategy {strategy}: {e}")
                results[strategy] = {"error": str(e)}

        return results

    def suggest_improvements(self, function_name: str, current_test_code: str) -> List[str]:
        suggestions: List[str] = []

        try:
            messages = [
                {"role": "system", "content": "You are a senior test engineer."},
                {
                    "role": "user",
                    "content": f"""Analyze this test code and suggest improvements:

Function: {function_name}
Test Code:
{current_test_code}

Provide specific, actionable suggestions for improving test coverage, readability, and robustness.""",
                },
            ]

            response = self.llm.generate(messages)
            suggestions = [s.strip() for s in response.split("\n") if s.strip()]

        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            suggestions = ["Unable to generate suggestions due to an error"]

        return suggestions

    def get_memory_insights(self) -> Dict[str, Any]:
        return self.memory.get_insights()

    def clear_memory(self):
        self.memory.clear()
        self.logger.info("Memory cleared")
