#!/usr/bin/env python3
"""
AI Pair Programming Agent for Automated Test Writing and Documentation
"""

import os
import sys
import logging
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_prs import REPOS, BASE_OUTPUT_PATH, extract_data
from ai_agent.agent import AIAgent

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def process_diff_files(agent: AIAgent, prompt_strategy: str = "diff-aware", compare_strategies: bool = False):
    print(f"\nStep 2: Processing diff files with strategy: {prompt_strategy}")
    
    data_dir = Path(BASE_OUTPUT_PATH)
    if not data_dir.exists():
        print(f"Data folder {data_dir} not found. Please run data extraction first.")
        return
    
    processed_count = 0
    
    for diff_file in data_dir.rglob("diff.patch"):
        print(f"\nProcessing: {diff_file}")
        
        pr_dir = diff_file.parent
        output_dir = pr_dir / "generated"
        
        try:
            if compare_strategies:
                results = agent.compare_prompt_strategies(
                    diff_file_path=str(diff_file),
                    output_dir=str(output_dir)
                )
                print(f"Strategy comparison complete for {diff_file}")
            else:
                results = agent.process_diff_file(
                    diff_file_path=str(diff_file),
                    output_dir=str(output_dir),
                    prompt_strategy=prompt_strategy,
                    generate_docs=True
                )
                print(f"Processing complete for {diff_file}")
                print(f"Generated {len(results['generated_tests'])} tests and {len(results['generated_docs'])} docs")
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {diff_file}: {e}")
            continue
    
    print(f"\nProcessed {processed_count} diff files")

def main():
    parser = argparse.ArgumentParser(description="AI Pair Programming Agent")
    parser.add_argument("--extract-only", action="store_true", help="Only extract PR data")
    parser.add_argument("--process-only", action="store_true", help="Only process existing diff files")
    parser.add_argument("--prompt-strategy", default="diff-aware", 
                       choices=["naive", "diff-aware", "few-shot", "cot", "tdd"],
                       help="Prompt strategy to use")
    parser.add_argument("--compare-strategies", action="store_true", 
                       help="Compare all prompt strategies")
    parser.add_argument("--model", default="codellama/CodeLlama-7b-Instruct-hf",
                       help="LLM model to use")
    parser.add_argument("--hf-token", default=None,
                       help="Hugging Face access token (or set HF_TOKEN env var)")
    parser.add_argument("--memory-insights", action="store_true",
                       help="Show memory insights")
    parser.add_argument("--clear-memory", action="store_true",
                       help="Clear agent memory")
    
    args = parser.parse_args()
    
    setup_logging()
    
    print("🤖 AI Pair Programming Agent for Automated Test Writing and Documentation")
    print("=" * 70)
    
    if not args.extract_only:
        print("Starting AI Agent...")
        try:
            hf_token = args.hf_token or os.getenv("HF_TOKEN", "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")
            agent = AIAgent(model_name=args.model, auth_token=hf_token)
            print("AI Agent started successfully!")
        except Exception as e:
            print(f"Error starting AI Agent: {e}")
            print("Please make sure you have installed the required packages:")
            print("pip install transformers accelerate torch")
            return
    
    if not args.process_only:
        print("Step 1: Extracting PR data...")
        extract_data()
    
    if not args.extract_only:
        process_diff_files(agent, args.prompt_strategy, args.compare_strategies)
        
        if args.memory_insights:
            print("\n📊 Memory Insights:")
            insights = agent.get_memory_insights()
            print(f"Total test patterns: {insights['summary']['total_test_patterns']}")
            print(f"Total function contexts: {insights['summary']['total_function_contexts']}")
            print(f"Total diff patterns: {insights['summary']['total_diff_patterns']}")
            
            if insights['best_strategies']:
                print("\nBest performing strategies:")
                for func_type, strategies in insights['best_strategies'].items():
                    print(f"  {func_type}:")
                    for strategy, metrics in strategies.items():
                        print(f"    {strategy}: Quality={metrics['avg_quality']:.2f}, "
                              f"Coverage={metrics['avg_coverage']:.2f}")
        
        if args.clear_memory:
            agent.clear_memory()
            print("Memory cleared")
    
    print("\n✅ Workflow complete!")

if __name__ == "__main__":
    main()  