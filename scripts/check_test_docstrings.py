import ast
import os
import sys
from typing import List, Tuple

def check_file(filepath: str) -> List[str]:
    """Check a single file for missing docstrings."""
    missing = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        # Check module docstring
        if not ast.get_docstring(tree):
            missing.append(f"Module: {os.path.basename(filepath)}")

        # Check function docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                if not ast.get_docstring(node):
                    missing.append(f"Function: {node.name}")

    except Exception as e:
        missing.append(f"Error parse file: {str(e)}")
    
    return missing

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_test_docstrings.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    files_with_issues = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                path = os.path.join(root, file)
                issues = check_file(path)
                if issues:
                    files_with_issues[path] = issues

    if not files_with_issues:
        print("✅  All tests have docstrings!")
        sys.exit(0)

    print("⚠️  Missing Docstrings Detected:")
    print("==============================")
    count = 0
    for file, issues in sorted(files_with_issues.items()):
        print(f"\n📄 {file}:")
        for issue in issues:
            print(f"  ❌ {issue}")
            count += 1
    
    print(f"\nTotal missing docstrings: {count}")
    sys.exit(1)

if __name__ == "__main__":
    main()
