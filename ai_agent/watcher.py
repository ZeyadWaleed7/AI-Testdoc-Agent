import ast

def get_changed_functions(before_file: str, after_file: str) -> dict:
    with open(before_file, "r") as f:
        before_code_tree = ast.parse(f.read())
    with open(after_file, "r") as f:
        after_code_tree = ast.parse(f.read())

    funcs_before = {f.name: f for f in before_code_tree.body if isinstance(f, ast.FunctionDef)}
    funcs_after = {f.name: f for f in after_code_tree.body if isinstance(f, ast.FunctionDef)}

    changed_funcs = {}
    for name in funcs_after:
        if name not in funcs_before or ast.dump(funcs_before[name]) != ast.dump(funcs_after[name]):
            changed_funcs[name] = funcs_after[name]

    return changed_funcs



