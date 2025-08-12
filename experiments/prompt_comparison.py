import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.agent import AIAgent
from ai_agent.prompts import PromptStrategy

class PromptComparisonExperiment:
    
    def __init__(self, model_name: str = "codellama/CodeLlama-7b-Instruct-hf"):
        self.agent = AIAgent(model_name=model_name)
        self.prompt_strategy = PromptStrategy()
        self.results = {
            "experiment_info": {
                "model": model_name,
                "strategies": self.prompt_strategy.get_all_strategies(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": {}
        }
    
    def run_experiment(self, diff_file_path: str, output_dir: str = "experiment_results") -> Dict[str, Any]:
        print(f"🔬 Running prompt comparison experiment on: {diff_file_path}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(diff_file_path, 'r', encoding='utf-8') as f:
            diff_content = f.read()
        
        from ai_agent.watcher import get_functions_from_diff_file
        functions = get_functions_from_diff_file(diff_file_path)
        
        print(f"📊 Found {len(functions)} functions to test")
        
        for i, (function_name, function_code, file_path) in enumerate(functions, 1):
            print(f"\n🔍 Testing function {i}/{len(functions)}: {function_name}")
            
            function_results = {
                "function_name": function_name,
                "file_path": file_path,
                "function_code": function_code,
                "strategies": {}
            }
            
            for strategy in self.prompt_strategy.get_all_strategies():
                print(f"  Testing strategy: {strategy}")
                
                start_time = time.time()
                
                try:
                    test_code = self.agent.test_generator.generate_tests_for_function(
                        function_code=function_code,
                        function_name=function_name,
                        diff_context=diff_content,
                        prompt_strategy=strategy
                    )
                    
                    generation_time = time.time() - start_time
                    
                    quality_metrics = self._analyze_test_quality(test_code, function_code)
                    
                    function_results["strategies"][strategy] = {
                        "test_code": test_code,
                        "generation_time": generation_time,
                        "quality_metrics": quality_metrics,
                        "success": True
                    }
                    
                    print(f"    ✅ Generated test in {generation_time:.2f}s")
                    
                except Exception as e:
                    generation_time = time.time() - start_time
                    
                    function_results["strategies"][strategy] = {
                        "test_code": f"Error: {str(e)}",
                        "generation_time": generation_time,
                        "quality_metrics": {},
                        "success": False,
                        "error": str(e)
                    }
                    
                    print(f"    ❌ Error: {e}")
            
            self.results["results"][function_name] = function_results
            
            function_file = os.path.join(output_dir, f"function_{function_name}_results.json")
            with open(function_file, 'w') as f:
                json.dump(function_results, f, indent=2)
        
        self._calculate_summary_statistics()
        
        results_file = os.path.join(output_dir, "prompt_comparison_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self._generate_report(output_dir)
        
        print(f"\n✅ Experiment complete! Results saved to: {output_dir}")
        return self.results
    
    def _analyze_test_quality(self, test_code: str, function_code: str) -> Dict[str, Any]:
        metrics = {
            "test_length": len(test_code.split('\n')),
            "has_assertions": "assert" in test_code.lower(),
            "has_test_functions": "def test_" in test_code.lower(),
            "has_docstrings": '"""' in test_code or "'''" in test_code,
            "has_comments": "#" in test_code,
            "function_mentions": function_code.split('\n')[0].split('(')[0].replace('def ', '').replace('async def ', '') in test_code
        }
        
        assertion_count = test_code.lower().count('assert')
        metrics["assertion_count"] = assertion_count
        
        lines_in_function = len([line for line in function_code.split('\n') if line.strip()])
        metrics["estimated_coverage"] = min(assertion_count / max(lines_in_function, 1), 1.0)
        
        return metrics
    
    def _calculate_summary_statistics(self):
        summary = {
            "total_functions": len(self.results["results"]),
            "strategies": {},
            "overall_best_strategy": None,
            "overall_best_score": 0
        }
        
        for strategy in self.prompt_strategy.get_all_strategies():
            summary["strategies"][strategy] = {
                "success_rate": 0,
                "avg_generation_time": 0,
                "avg_assertion_count": 0,
                "avg_estimated_coverage": 0,
                "total_successful": 0,
                "total_tests": 0
            }
        
        for function_name, function_data in self.results["results"].items():
            for strategy, strategy_data in function_data["strategies"].items():
                stats = summary["strategies"][strategy]
                stats["total_tests"] += 1
                
                if strategy_data["success"]:
                    stats["total_successful"] += 1
                    stats["avg_generation_time"] += strategy_data["generation_time"]
                    stats["avg_assertion_count"] += strategy_data["quality_metrics"].get("assertion_count", 0)
                    stats["avg_estimated_coverage"] += strategy_data["quality_metrics"].get("estimated_coverage", 0)
        
        for strategy, stats in summary["strategies"].items():
            if stats["total_successful"] > 0:
                stats["success_rate"] = stats["total_successful"] / stats["total_tests"]
                stats["avg_generation_time"] /= stats["total_successful"]
                stats["avg_assertion_count"] /= stats["total_successful"]
                stats["avg_estimated_coverage"] /= stats["total_successful"]
        
        for strategy, stats in summary["strategies"].items():
            if stats["total_successful"] > 0:
                score = (stats["success_rate"] * 0.4 + 
                        stats["avg_estimated_coverage"] * 0.4 + 
                        (1 / (1 + stats["avg_generation_time"])) * 0.2)
                
                if score > summary["overall_best_score"]:
                    summary["overall_best_score"] = score
                    summary["overall_best_strategy"] = strategy
        
        self.results["summary"] = summary
    
    def _generate_report(self, output_dir: str):
        report_lines = [
            "# Prompt Strategy Comparison Experiment Report",
            "",
            f"**Experiment Date:** {self.results['experiment_info']['timestamp']}",
            f"**Model Used:** {self.results['experiment_info']['model']}",
            f"**Functions Tested:** {self.results['summary']['total_functions']}",
            "",
            "## Summary Statistics",
            "",
            "| Strategy | Success Rate | Avg Generation Time | Avg Assertions | Avg Coverage |",
            "|----------|--------------|-------------------|----------------|--------------|"
        ]
        
        for strategy, stats in self.results["summary"]["strategies"].items():
            report_lines.append(
                f"| {strategy} | {stats['success_rate']:.2%} | {stats['avg_generation_time']:.2f}s | "
                f"{stats['avg_assertion_count']:.1f} | {stats['avg_estimated_coverage']:.2%} |"
            )
        
        report_lines.extend([
            "",
            f"**Best Overall Strategy:** {self.results['summary']['overall_best_strategy']}",
            f"**Best Score:** {self.results['summary']['overall_best_score']:.3f}",
            "",
            "## Detailed Results",
            ""
        ])
        
        for function_name, function_data in self.results["results"].items():
            report_lines.append(f"### {function_name}")
            report_lines.append(f"**File:** {function_data['file_path']}")
            report_lines.append("")
            
            for strategy, strategy_data in function_data["strategies"].items():
                status = "✅" if strategy_data["success"] else "❌"
                report_lines.append(f"**{strategy}:** {status}")
                
                if strategy_data["success"]:
                    metrics = strategy_data["quality_metrics"]
                    report_lines.append(f"- Generation time: {strategy_data['generation_time']:.2f}s")
                    report_lines.append(f"- Assertions: {metrics.get('assertion_count', 0)}")
                    report_lines.append(f"- Estimated coverage: {metrics.get('estimated_coverage', 0):.2%}")
                else:
                    report_lines.append(f"- Error: {strategy_data.get('error', 'Unknown error')}")
                
                report_lines.append("")
        
        report_file = os.path.join(output_dir, "experiment_report.md")
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Report generated: {report_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Prompt Strategy Comparison Experiment")
    parser.add_argument("diff_file", help="Path to diff file to test")
    parser.add_argument("--output-dir", default="experiment_results", help="Output directory")
    parser.add_argument("--model", default="codellama/CodeLlama-7b-Instruct-hf", help="LLM model to use")
    
    args = parser.parse_args()
    
    experiment = PromptComparisonExperiment(model_name=args.model)
    results = experiment.run_experiment(args.diff_file, args.output_dir)
    
    print("\n📊 Experiment Summary:")
    print(f"Best strategy: {results['summary']['overall_best_strategy']}")
    print(f"Best score: {results['summary']['overall_best_score']:.3f}")

if __name__ == "__main__":
    main()

