import os
import sys
import logging
import argparse
from pathlib import Path
import traceback

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

def list_available_prs():
    """List all available PRs in the data directory"""
    data_dir = Path(BASE_OUTPUT_PATH)
    if not data_dir.exists():
        print(f"Data folder {data_dir} not found. Please run data extraction first.")
        return []
    
    prs = []
    for diff_file in data_dir.rglob("diff.patch"):
        pr_dir = diff_file.parent
        # Extract repo and PR info from path structure: data/repo_name/PR_number/
        try:
            path_parts = pr_dir.relative_to(data_dir).parts
            if len(path_parts) >= 2:
                repo_name = path_parts[0]  # First part is repo name
                pr_id = path_parts[1]      # Second part is PR number
                prs.append({
                    'repo': repo_name,
                    'pr': pr_id,
                    'path': pr_dir,
                    'diff_file': diff_file,
                    'full_name': f"{repo_name}/PR_{pr_id}"
                })
        except Exception as e:
            print(f"Warning: Could not parse path {pr_dir}: {e}")
            continue
    
    # Sort by repo name and PR number for consistent ordering
    prs.sort(key=lambda x: (x['repo'], int(x['pr']) if x['pr'].isdigit() else x['pr']))
    return prs

def select_prs_interactive(available_prs):
    """Interactive PR selection"""
    if not available_prs:
        return []
    
    print(f"\nAvailable PRs ({len(available_prs)} total):")
    print("-" * 60)
    for i, pr in enumerate(available_prs, 1):
        print(f"{i:3d}. {pr['full_name']}")
    
    print("\nSelection options:")
    print("  - Enter numbers separated by commas (e.g., 1,3,5)")
    print("  - Enter range with dash (e.g., 1-5)")
    print("  - Enter 'all' to process all PRs")
    print("  - Enter 'q' to quit")
    
    while True:
        selection = input(f"\nSelect PRs [1-{len(available_prs)}]: ").strip().lower()
        
        if selection == 'q':
            return []
        
        if selection == 'all':
            return available_prs
        
        try:
            selected_prs = []
            
            # Handle ranges and individual numbers
            for part in selection.split(','):
                part = part.strip()
                if '-' in part and part != '-':
                    # Range selection (e.g., "1-5")
                    start, end = map(int, part.split('-'))
                    for idx in range(start - 1, min(end, len(available_prs))):
                        if 0 <= idx < len(available_prs):
                            selected_prs.append(available_prs[idx])
                else:
                    # Individual number
                    idx = int(part) - 1
                    if 0 <= idx < len(available_prs):
                        selected_prs.append(available_prs[idx])
                    else:
                        print(f"Invalid selection: {idx + 1} (max: {len(available_prs)})")
                        break
            else:
                # Remove duplicates while preserving order
                unique_prs = []
                seen = set()
                for pr in selected_prs:
                    if pr['full_name'] not in seen:
                        unique_prs.append(pr)
                        seen.add(pr['full_name'])
                return unique_prs
                
        except ValueError:
            print("Invalid input. Please use format: 1,3,5 or 1-5 or 'all' or 'q'")

def filter_prs_by_criteria(available_prs, repo_filter=None, pr_filter=None, limit=None):
    """Filter PRs based on criteria"""
    filtered = available_prs
    
    if repo_filter:
        filtered = [pr for pr in filtered if repo_filter.lower() in pr['repo'].lower()]
        print(f"Filtered by repo '{repo_filter}': {len(filtered)} PRs")
    
    if pr_filter:
        pr_numbers = [x.strip() for x in pr_filter.split(',')]
        filtered = [pr for pr in filtered if pr['pr'] in pr_numbers]
        print(f"Filtered by PR numbers {pr_numbers}: {len(filtered)} PRs")
    
    if limit:
        filtered = filtered[:limit]
        print(f"Limited to first {limit} PRs")
    
    return filtered

def validate_diff_file(diff_file):
    """Validate that diff file exists and has content"""
    if not diff_file.exists():
        return False, "Diff file does not exist"
    
    try:
        content = diff_file.read_text(encoding='utf-8')
        if not content.strip():
            return False, "Diff file is empty"
        
        # Basic validation - should contain diff markers
        if not any(line.startswith(('diff --git', '@@', '+++', '---')) for line in content.split('\n')):
            return False, "File doesn't appear to be a valid diff"
            
        return True, "Valid"
    except Exception as e:
        return False, f"Error reading file: {e}"

def process_pr(pr_data_dir: str, provider: str, model: str, prompt_strategy: str = "naive", generate_docs: bool = True):
    """Process a specific PR using enhanced context"""
    print(f"Processing PR from: {pr_data_dir}")
    
    # Check if enhanced context is available
    enhanced_patches_path = os.path.join(pr_data_dir, "enhanced_patches.json")
    if not os.path.exists(enhanced_patches_path):
        print(f"Error: No enhanced context found in {pr_data_dir}")
        return
    
    # Initialize the agent
    agent = AIAgent(provider=provider, model_name=model)
    
    # Process with enhanced context using the correct method
    try:
        # Use the new method that saves files to deepseek_coder/{strategy}/
        agent._process_enhanced_context(pr_data_dir, prompt_strategy)
        
        print(f"Processing completed!")
        print(f"Enhanced context used: True")
        print(f"PR Title: {agent.enhanced_context.get_pr_title() if hasattr(agent, 'enhanced_context') else 'Unknown'}")
        
        # Check what files were generated
        strategy_dir = os.path.join(pr_data_dir, "deepseek_coder", prompt_strategy)
        if os.path.exists(strategy_dir):
            generated_files = os.listdir(strategy_dir)
            print(f"Generated {len(generated_files)} test files in {strategy_dir}:")
            for file in generated_files:
                print(f"  - {file}")
        else:
            print(f"No test files generated in {strategy_dir}")
            
    except Exception as e:
        print(f"Error processing PR: {e}")
        import traceback
        traceback.print_exc()

def compare_strategies(pr_data_dir: str, provider: str, model: str):
    """Compare all prompt strategies using enhanced context"""
    print(f"Comparing all strategies for PR: {pr_data_dir}")
    
    strategies = ["naive", "diff-aware", "few-shot", "cot"]
    
    for strategy in strategies:
        print(f"\n{'='*50}")
        print(f"Testing strategy: {strategy}")
        print(f"{'='*50}")
        
        strategy_dir = f"generated_{strategy}"
        os.makedirs(strategy_dir, exist_ok=True)
        
        try:
            process_pr(pr_data_dir, provider, model, strategy, generate_docs=True)
            
            # Move generated files to strategy-specific directory
            if os.path.exists("generated"):
                import shutil
                for item in os.listdir("generated"):
                    src = os.path.join("generated", item)
                    dst = os.path.join(strategy_dir, item)
                    if os.path.isfile(src):
                        shutil.move(src, dst)
                        
        except Exception as e:
            print(f"Error with strategy {strategy}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nStrategy comparison completed. Check the generated_* directories for results.")

def process_diff_files(agent: AIAgent, strategies: list[str] = None, compare_strategies: bool = False, 
                      selected_prs=None, repo_filter=None, pr_filter=None, limit=None, interactive=False,
                      skip_on_error=True):
    print(f"\nStep 2: Processing diff files with strategies: {strategies}")

    strategies = strategies or ["diff-aware"]  # default if None

    data_dir = Path(BASE_OUTPUT_PATH)
    if not data_dir.exists():
        print(f"❌ Data folder {data_dir} not found. Please run data extraction first.")
        return

    # Get available PRs
    available_prs = list_available_prs()
    if not available_prs:
        print("❌ No PRs found to process.")
        return

    print(f"Found {len(available_prs)} total PRs in data directory")

    # Select which PRs to process
    if selected_prs:
        # Use pre-selected PRs
        prs_to_process = selected_prs
    elif interactive:
        # Interactive selection
        prs_to_process = select_prs_interactive(available_prs)
        if not prs_to_process:
            print("No PRs selected. Exiting.")
            return
    else:
        # Filter based on criteria or process all
        prs_to_process = filter_prs_by_criteria(available_prs, repo_filter, pr_filter, limit)
        if not prs_to_process:
            prs_to_process = available_prs  # Process all if no filters

    print(f"\n📋 Processing {len(prs_to_process)} PR(s):")
    for pr in prs_to_process:
        print(f"  ✓ {pr['full_name']}")

    processed_count = 0
    failed_count = 0
    results_summary = []

    for i, pr_info in enumerate(prs_to_process, 1):
        diff_file = pr_info['diff_file']
        pr_name = pr_info['full_name']
        
        print(f"\n{'='*60}")
        print(f"[{i}/{len(prs_to_process)}] Processing: {pr_name}")
        print(f"{'='*60}")
        
        # Validate diff file first
        is_valid, validation_msg = validate_diff_file(diff_file)
        if not is_valid:
            print(f"❌ Skipping {pr_name}: {validation_msg}")
            failed_count += 1
            continue

        pr_dir = diff_file.parent
        pr_results = {
            'pr_name': pr_name,
            'strategies': {},
            'success': False
        }

        for strategy_idx, prompt_strategy in enumerate(strategies, 1):
            print(f"\n[Strategy {strategy_idx}/{len(strategies)}] Using: {prompt_strategy}")
            
            # Safe folder names
            safe_model_name = agent.model_name.replace("/", "_").replace("-", "_")
            safe_strategy = prompt_strategy.replace("/", "_").replace("-", "_")
            output_dir = pr_dir / safe_model_name / safe_strategy
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                if compare_strategies:
                    results = agent.compare_prompt_strategies(
                        diff_file_path=str(diff_file),
                        output_dir=str(output_dir)
                    )
                    print(f"✅ Strategy comparison complete for {pr_name} [{prompt_strategy}]")
                    pr_results['strategies'][prompt_strategy] = {
                        'success': True,
                        'type': 'comparison',
                        'output_dir': str(output_dir)
                    }
                else:
                    results = agent.process_diff_file(
                        diff_file_path=str(diff_file),
                        output_dir=str(output_dir),
                        prompt_strategy=prompt_strategy,
                        generate_docs=True
                    )
                    
                    num_tests = len(results.get('generated_tests', []))
                    num_docs = len(results.get('generated_docs', []))
                    
                    print(f"✅ Processing complete for {pr_name} [{prompt_strategy}]")
                    print(f"   📄 Generated: {num_tests} tests, {num_docs} docs")
                    
                    pr_results['strategies'][prompt_strategy] = {
                        'success': True,
                        'type': 'processing',
                        'tests_generated': num_tests,
                        'docs_generated': num_docs,
                        'output_dir': str(output_dir)
                    }

                processed_count += 1
                pr_results['success'] = True

            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error processing {pr_name} [{prompt_strategy}]: {error_msg}")
                
                # Log full traceback for debugging
                logging.error(f"Full traceback for {pr_name} [{prompt_strategy}]:")
                logging.error(traceback.format_exc())
                
                pr_results['strategies'][prompt_strategy] = {
                    'success': False,
                    'error': error_msg,
                    'output_dir': str(output_dir)
                }
                
                failed_count += 1
                
                if skip_on_error:
                    print(f"⚠️  Skipping remaining strategies for {pr_name}")
                    break
                else:
                    continue

        results_summary.append(pr_results)

    # Print final summary
    print(f"\n{'='*60}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total PRs: {len(prs_to_process)}")
    print(f"Successfully processed: {len([r for r in results_summary if r['success']])}")
    print(f"Failed: {len([r for r in results_summary if not r['success']])}")
    print(f"Total strategy runs: {processed_count}")
    print(f"Failed strategy runs: {failed_count}")
    
    # Detailed results
    for result in results_summary:
        status = "✅" if result['success'] else "❌"
        print(f"\n{status} {result['pr_name']}")
        for strategy, details in result['strategies'].items():
            if details['success']:
                if details['type'] == 'processing':
                    print(f"   {strategy}: {details['tests_generated']} tests, {details['docs_generated']} docs")
                else:
                    print(f"   {strategy}: comparison complete")
            else:
                print(f"   {strategy}: FAILED - {details['error']}")

def main():
    parser = argparse.ArgumentParser(description="AI Pair Programming Agent")
    parser.add_argument("--extract-only", action="store_true", help="Only extract PR data")
    parser.add_argument("--process-only", action="store_true", help="Only process existing diff files")
    parser.add_argument("--prompt-strategy", default="naive",
                       choices=["naive", "diff-aware", "few-shot", "cot"],
                       help="Prompt strategy to use (all strategies now use enhanced context processing)")
    parser.add_argument("--compare-strategies", action="store_true", 
                       help="Compare all prompt strategies")
    parser.add_argument("--model", default="h2oai/h2ogpt-16k-codellama-13b-python",
                       help="LLM model to use. For Ollama, use model name like 'deepseek-coder'")
    parser.add_argument("--hf-token", default=None,
                       help="Hugging Face API token for remote inference")
    parser.add_argument("--provider", default="hf-inference",
                       choices=["hf-inference", "huggingface", "featherless-ai", "default", "local", "ollama"],
                       help="Backend provider. Use 'local' for offline Transformers inference, 'ollama' for local Ollama models.")
    parser.add_argument("--memory-insights", action="store_true",
                       help="Show memory insights")
    parser.add_argument("--clear-memory", action="store_true",
                       help="Clear agent memory")
    
    # New PR selection arguments
    parser.add_argument("--list-prs", action="store_true",
                       help="List available PRs and exit")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive PR selection")
    parser.add_argument("--repo-filter", 
                       help="Filter PRs by repository name (case-insensitive partial match)")
    parser.add_argument("--pr-filter", type=str, help="Filter PRs by number or name")
    parser.add_argument("--limit", type=int,
                       help="Limit number of PRs to process")
    parser.add_argument("--continue-on-error", action="store_true",
                       help="Continue processing other strategies even if one fails")
    
    # Enhanced context options
    parser.add_argument("--pr-data-dir", type=str, help="Process specific PR data directory")
    
    # Enhanced context processing
    parser.add_argument("--enhanced-context", action="store_true", help="Use enhanced context for better test generation")
    
    args = parser.parse_args()
    
    setup_logging()
    
    print("🤖 AI Pair Programming Agent for Automated Test Writing and Documentation")
    print("=" * 70)
    
    # Handle enhanced context processing
    if args.pr_data_dir:
        if args.compare_strategies:
            compare_strategies(args.pr_data_dir, args.provider, args.model)
        else:
            process_pr(args.pr_data_dir, args.provider, args.model, args.prompt_strategy, args.enhanced_context)
        return

    # Handle list-prs command
    if args.list_prs:
        available_prs = list_available_prs()
        if available_prs:
            print(f"\n📋 Found {len(available_prs)} PRs:")
            print("-" * 60)
            for i, pr in enumerate(available_prs, 1):
                print(f"{i:3d}. {pr['full_name']}")
                # Show diff file size for additional info
                try:
                    size = pr['diff_file'].stat().st_size
                    print(f"     Diff size: {size:,} bytes")
                except:
                    print(f"     Diff size: unknown")
        else:
            print("❌ No PRs found. Run data extraction first.")
        return
    
    if not args.extract_only:
        print("🚀 Starting AI Agent...")
        try:
            hf_token = args.hf_token or os.getenv("HF_TOKEN")
            if args.provider == "local":
                print("➡️  Provider: LOCAL (Transformers). No HF API credits will be used.")
            elif args.provider == "ollama":
                print("➡️  Provider: OLLAMA (Local). No API credits will be used.")
            else:
                if not hf_token:
                    print("⚠️  No HF token detected. Remote providers may fail or be rate-limited.")
            
            agent = AIAgent(model_name=args.model, api_token=hf_token, provider=args.provider)
            print("✅ AI Agent started successfully!")
            print(f"   Model: {args.model}")
            print(f"   Provider: {args.provider}")
            print(f"   Strategy: {args.prompt_strategy}")
            
        except Exception as e:
            print(f"❌ Error starting AI Agent: {e}")
            print("Please make sure you have installed the required packages:")
            print("pip install huggingface_hub")
            logging.error(f"Agent initialization failed: {traceback.format_exc()}")
            return
    
    if not args.process_only:
        print("\n📥 Step 1: Extracting PR data...")
        try:
            extract_data()
            print("✅ Data extraction completed")
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")
            logging.error(f"Data extraction failed: {traceback.format_exc()}")
            return
    
    if not args.extract_only:
        process_diff_files(
            agent, 
            strategies=[args.prompt_strategy], 
            compare_strategies=args.compare_strategies,
            repo_filter=args.repo_filter,
            pr_filter=args.pr_filter,
            limit=args.limit,
            interactive=args.interactive,
            skip_on_error=not args.continue_on_error
        )
        
        if args.memory_insights:
            print("\n📊 Memory Insights:")
            try:
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
            except Exception as e:
                print(f"❌ Error getting memory insights: {e}")
        
        if args.clear_memory:
            try:
                agent.clear_memory()
                print("✅ Memory cleared")
            except Exception as e:
                print(f"❌ Error clearing memory: {e}")
    
    print("\n🎉 Workflow complete!")

if __name__ == "__main__":
    main()
