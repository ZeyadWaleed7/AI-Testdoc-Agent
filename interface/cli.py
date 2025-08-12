import argparse
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.agent import AIAgent
from ai_agent.memory import MemoryModule

def main():
    parser = argparse.ArgumentParser(
        description="AI Pair Programming Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-agent process data/fastapi_fastapi/PR_13827/diff.patch
  ai-agent compare-strategies data/fastapi_fastapi/PR_13827/diff.patch
  ai-agent memory-insights
  ai-agent suggest-improvements my_function "def my_function(x): return x * 2"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    process_parser = subparsers.add_parser('process', help='Process a diff file')
    process_parser.add_argument('diff_file', help='Path to diff file')
    process_parser.add_argument('--output-dir', default='generated', help='Output directory')
    process_parser.add_argument('--prompt-strategy', default='diff-aware', 
                               choices=['naive', 'diff-aware', 'few-shot', 'cot', 'tdd'],
                               help='Prompt strategy to use')
    process_parser.add_argument('--no-docs', action='store_true', help='Skip documentation generation')
    process_parser.add_argument('--model', default='codellama/CodeLlama-13b-Instruct-hf',
                               help='LLM model to use')
    
    compare_parser = subparsers.add_parser('compare-strategies', help='Compare all prompt strategies')
    compare_parser.add_argument('diff_file', help='Path to diff file')
    compare_parser.add_argument('--output-dir', default='prompt_comparison', help='Output directory')
    compare_parser.add_argument('--model', default='codellama/CodeLlama-13b-Instruct-hf',
                               help='LLM model to use')
    
    memory_parser = subparsers.add_parser('memory-insights', help='Show memory insights')
    
    suggest_parser = subparsers.add_parser('suggest-improvements', help='Suggest test improvements')
    suggest_parser.add_argument('function_name', help='Name of the function')
    suggest_parser.add_argument('test_code', help='Current test code')
    
    clear_parser = subparsers.add_parser('clear-memory', help='Clear agent memory')
    
    list_parser = subparsers.add_parser('list-strategies', help='List available prompt strategies')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'process':
            process_diff_file(args)
        elif args.command == 'compare-strategies':
            compare_strategies(args)
        elif args.command == 'memory-insights':
            show_memory_insights()
        elif args.command == 'suggest-improvements':
            suggest_improvements(args)
        elif args.command == 'clear-memory':
            clear_memory()
        elif args.command == 'list-strategies':
            list_strategies()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def process_diff_file(args):
    print(f"🤖 Processing diff file: {args.diff_file}")
    
    agent = AIAgent(model_name=args.model)
    
    results = agent.process_diff_file(
        diff_file_path=args.diff_file,
        output_dir=args.output_dir,
        prompt_strategy=args.prompt_strategy,
        generate_docs=not args.no_docs
    )
    
    print(f"✅ Processing complete!")
    print(f"Generated {len(results['generated_tests'])} tests")
    if not args.no_docs:
        print(f"Generated {len(results['generated_docs'])} documentation files")
    print(f"Results saved to: {args.output_dir}")

def compare_strategies(args):
    print(f"🤖 Comparing prompt strategies for: {args.diff_file}")
    
    agent = AIAgent(model_name=args.model)
    
    results = agent.compare_prompt_strategies(
        diff_file_path=args.diff_file,
        output_dir=args.output_dir
    )
    
    print(f"✅ Strategy comparison complete!")
    print(f"Results saved to: {args.output_dir}")
    
    for strategy, result in results.items():
        if "error" in result:
            print(f"❌ {strategy}: Error - {result['error']}")
        else:
            print(f"✅ {strategy}: Generated {len(result.get('generated_tests', {}))} tests")

def show_memory_insights():
    print("📊 Memory Insights")
    print("=" * 50)
    
    memory = MemoryModule()
    insights = memory.get_insights()
    
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

def suggest_improvements(args):
    print(f"💡 Suggesting improvements for: {args.function_name}")
    
    agent = AIAgent()
    
    suggestions = agent.suggest_improvements(
        function_name=args.function_name,
        current_test_code=args.test_code
    )
    
    print("Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")

def clear_memory():
    print("🧹 Clearing agent memory...")
    
    memory = MemoryModule()
    memory.clear()
    
    print("✅ Memory cleared")

def list_strategies():
    print("📋 Available Prompt Strategies:")
    print("1. naive - Basic prompt without context")
    print("2. diff-aware - Uses diff context for better tests")
    print("3. few-shot - Provides examples in the prompt")
    print("4. cot - Chain of thought reasoning")
    print("5. tdd - Test-driven development approach")

if __name__ == "__main__":
    main()

