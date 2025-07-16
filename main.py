# Orchestrates everything

from ai_agent.watcher import get_changed_functions
import ast
changed = get_changed_functions("examples/before.py", "examples/after.py")
for name, node in changed.items():
    print(f" Changed function: {name}")
    print(ast.unparse(node))  