import os
import sys
from pathlib import Path

# Add src/yamldb to path to import util directly without triggering yamldb/__init__.py
sys.path.append(str(Path("src/yamldb").resolve()))

try:
    import util
    print_yaml_errors = util.print_yaml_errors
    check_yaml_syntax = util.check_yaml_syntax
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_checker():
    # 1. Valid YAML
    with open("test_valid.yaml", "w") as f:
        f.write("name: Gregor\nage: 111\nskills:\n  - python\n  - yaml")
    
    print("Testing valid YAML:")
    print_yaml_errors("test_valid.yaml")
    print("-" * 20)

    # 2. YAML with tabs
    with open("test_tabs.yaml", "w") as f:
        f.write("name: Gregor\n\tage: 111") # Tab at start of line 2
    
    print("Testing YAML with tabs:")
    print_yaml_errors("test_tabs.yaml")
    print("-" * 20)

    # 3. YAML with syntax error
    with open("test_invalid.yaml", "w") as f:
        f.write("name: Gregor\n  invalid_indent: true\n- list_item_without_parent")
    
    print("Testing YAML with syntax error:")
    print_yaml_errors("test_invalid.yaml")
    print("-" * 20)

    # Cleanup
    for f in ["test_valid.yaml", "test_tabs.yaml", "test_invalid.yaml"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    test_checker()