import ast
from pathlib import Path


def resolve_imports(tree):
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                mapping[name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                local_name = alias.asname or alias.name
                mapping[local_name] = module
    return mapping


def get_qualified_calls(tree, module_map):
    calls_map = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parent_class = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in ast.walk(parent):
                    parent_class = parent.name
                    break
            qual_name = f"{parent_class}.{node.name}" if parent_class else node.name
            called = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        local_name = child.func.id
                        resolved = module_map.get(local_name, local_name)
                        called.add(resolved)
                    elif isinstance(child.func, ast.Attribute):
                        attr_str = ast.unparse(child.func)
                        parts = attr_str.split('.')
                        if len(parts) == 2:
                            mod, func = parts
                            if mod in module_map:
                                resolved = f"{module_map[mod]}::{func}"
                            else:
                                resolved = attr_str
                        else:
                            resolved = attr_str
                        called.add(resolved)
            calls_map[qual_name] = list(called)
    return calls_map


def parse_project(root_path):
    files_data = []
    for py_file in Path(root_path).rglob("*.py"):
        relative = py_file.relative_to(root_path)
        file_stem = relative.stem
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        module_map = resolve_imports(tree)
        calls = get_qualified_calls(tree, module_map)
        resumos = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent_class = None
                for p in ast.walk(tree):
                    if isinstance(p, ast.ClassDef) and node in ast.walk(p):
                        parent_class = p.name
                        break
                qname = f"{parent_class}.{node.name}" if parent_class else node.name
                doc = ast.get_docstring(node)
                resumos[qname] = doc.strip() if doc else "Sem descrição"

        files_data.append({
            "file": str(relative),
            "module_name": file_stem,
            "functions": list(calls.keys()),
            "calls": calls,
            "docstrings": resumos,
        })
    return files_data
