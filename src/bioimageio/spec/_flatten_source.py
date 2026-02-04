import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Set


# --------------------------
# AST helpers
# --------------------------
class NameCollector(ast.NodeVisitor):
    """Collect all top-level names used in an AST."""

    def __init__(self):
        super().__init__()
        self.names: Set[str] = set()

    def visit_Name(self, node: ast.Name):
        self.names.add(node.id)

    def visit_Attribute(self, node: ast.Attribute):
        if isinstance(node.value, ast.Name):  # TODO: reduntant??
            self.names.add(node.value.id)
        self.generic_visit(node)


class ImportStripper(ast.NodeTransformer):
    """Remove forbidden imports from AST."""

    def __init__(self, forbidden: Set[str]):
        super().__init__()
        self.forbidden = forbidden

    def visit_Import(self, node: ast.Import):
        names = [n for n in node.names if n.name.split(".")[0] not in self.forbidden]
        return ast.Import(names=names) if names else None

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module and node.module.split(".")[0] in self.forbidden:
            return None
        return node


def strip_forbidden_imports(source: str, forbidden: Set[str]) -> str:
    tree = ast.parse(source)
    tree = ImportStripper(forbidden).visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def find_imports(tree: ast.AST) -> Set[str]:
    imports: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def get_module_source(module_name: str) -> Optional[Path]:
    spec = importlib.util.find_spec(module_name)
    if not spec or not spec.origin or not spec.origin.endswith(".py"):
        return None
    return Path(spec.origin)


def is_stdlib(module_path: Path) -> bool:
    return "site-packages" not in str(module_path)


# --------------------------
# Core flattening
# --------------------------
def collect_needed_definitions(
    source_file: Path, obj_name: str, known_third_party: Set[str]
) -> Dict[Path, Set[str]]:
    """
    Collect which definitions are needed from which dependency files.
    Returns a dict mapping file paths to sets of definition names needed from those files.
    """
    needed: Dict[Path, Set[str]] = {}
    to_process = [(source_file, {obj_name})]
    visited: Set[tuple[Path, str]] = set()
    while to_process:
        file_path, names = to_process.pop(0)

        for name in names:
            if (file_path, name) in visited:
                continue
            visited.add((file_path, name))

            # Find the definition
            try:
                src = file_path.read_text()
                tree = ast.parse(src)
            except Exception:
                continue

            # Find the definition in the file
            for node in tree.body:
                if not (
                    isinstance(node, (ast.FunctionDef, ast.ClassDef))
                    and node.name == name
                ):
                    continue

                # Collect names referenced in this definition
                collector = NameCollector()
                collector.visit(node)
                referenced = collector.names
                # Check imports in the file to find where referenced names come from
                for imp_node in tree.body:
                    if not isinstance(imp_node, ast.ImportFrom):
                        continue

                    if imp_node.level > 0:  # Relative import
                        # Relative import
                        module_name = imp_node.module or ""
                        module_path = file_path.parent / f"{module_name}.py"
                        if module_path.exists():
                            imported_names = {
                                alias.name
                                for alias in imp_node.names
                                if alias.name in referenced
                            }
                            if imported_names:
                                needed.setdefault(module_path, set()).update(
                                    imported_names
                                )
                                to_process.append((module_path, imported_names))
                break
    return needed


def extract_definitions_with_imports(
    file_path: Path, definition_names: Set[str], known_third_party: Set[str]
) -> str:
    """
    Extract specific definitions from a file, including necessary imports.
    """
    src = file_path.read_text()
    tree = ast.parse(src)

    # Collect imports needed by the definitions
    needed_imports: Set[str] = set()
    definitions: list[ast.stmt] = []

    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.ClassDef))
            and node.name in definition_names
        ):
            definitions.append(node)
            # Collect referenced names
            collector = NameCollector()
            collector.visit(node)
            needed_imports.update(collector.names)

    # Collect import statements for needed names
    import_stmts: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Check if the imported name or its alias is referenced
                ref_name = alias.asname if alias.asname else alias.name.split(".")[0]
                if ref_name in needed_imports:
                    import_stmts.append(node)
                    break
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                # Check if any imported names are needed
                for alias in node.names:
                    ref_name = alias.asname if alias.asname else alias.name
                    if ref_name in needed_imports:
                        import_stmts.append(node)
                        break

    # Reconstruct source with a blank line between imports and definitions
    imports_src = "\n".join(ast.unparse(node) for node in import_stmts)
    defs_src = "\n".join(ast.unparse(node) for node in definitions)
    if imports_src and defs_src:
        return f"{imports_src}\n\n{defs_src}"
    return imports_src or defs_src


def generate_flat_source_from_object(
    obj: Any,
    *,
    var_name: Optional[str] = None,
    known_third_party: Set[str],
    output_file: Path,
):
    src_file = inspect.getsourcefile(obj)
    if src_file is None:
        raise RuntimeError(f"Cannot locate source file for object, {obj}")

    src_file = Path(src_file)
    obj_name = str(obj.__name__)
    obj_src = inspect.getsource(obj)

    # Step 1: collect needed definitions from dependencies
    needed_defs = collect_needed_definitions(src_file, obj_name, known_third_party)

    # Step 2: write flat file
    with output_file.open("w") as f:
        _ = f.write("# Auto-generated flat dependency file\n\n")

        # Write dependency definitions
        for dep_file in sorted(needed_defs.keys()):
            try:
                origin = dep_file.relative_to(src_file.parent.parent)
            except Exception:
                try:
                    origin = dep_file.relative_to(src_file.parent)
                except Exception:
                    origin = dep_file

            _ = f.write(f"# ===== From {origin.as_posix()} =====\n")
            dep_src = extract_definitions_with_imports(
                dep_file, needed_defs[dep_file], known_third_party
            )
            _ = f.write(dep_src)
            _ = f.write("\n\n\n")

        # Write the main object
        _ = f.write("# ===== Exported object =====\n")
        _ = f.write(obj_src)
        _ = f.write("\n\n")

        if var_name is not None:
            _ = f.write(f"{var_name} = {obj_name}\n")

    print(f"Written {output_file}")


# --------------------------
# CLI support
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: flatten.py <input.py> <object_name> <known_lib1,known_lib2> <output.py>"
        )
        sys.exit(1)

    input_file = Path(sys.argv[1])
    object_name = sys.argv[2]
    known_libs = set(sys.argv[3].split(","))
    output_file = Path(sys.argv[4])

    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("mod", input_file)
    assert spec is not None, f"failed to load spec from {input_file}"
    assert spec.loader is not None, f"failed to load loader from {input_file}"
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    obj = getattr(mod, object_name)

    generate_flat_source_from_object(
        obj, var_name=object_name, known_third_party=known_libs, output_file=output_file
    )
