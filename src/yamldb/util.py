try:
    import oyaml as yaml
except ImportError:
    import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

def check_yaml_syntax(filename: str) -> List[Dict[str, Any]]:
    """
    Checks a YAML file for syntax errors, including forbidden tab characters.
    
    Args:
        filename (str): Path to the YAML file.
        
    Returns:
        List[Dict[str, Any]]: A list of errors found. Each error is a dict with 
                              'line', 'column', 'message', and 'type'.
    """
    errors = []
    path = Path(filename)
    
    if not path.exists():
        return [{"line": 0, "column": 0, "message": f"File {filename} not found", "type": "FileNotFound"}]

    # 1. Check for tabs manually
    try:
        with open(path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if "\t" in line:
                    col_num = line.find("\t") + 1
                    errors.append({
                        "line": line_num,
                        "column": col_num,
                        "message": "Tab characters are not allowed in YAML",
                        "type": "TabError"
                    })
    except Exception as e:
        errors.append({"line": 0, "column": 0, "message": str(e), "type": "ReadError"})

    # 2. Check for other YAML syntax errors using the parser
    try:
        with open(path, "rb") as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        mark = getattr(e, 'problem_mark', None)
        if mark:
            errors.append({
                "line": mark.line + 1,
                "column": mark.column + 1,
                "message": str(e),
                "type": "YamlSyntaxError"
            })
        else:
            errors.append({
                "line": 0,
                "column": 0,
                "message": str(e),
                "type": "YamlSyntaxError"
            })
    except Exception as e:
        errors.append({"line": 0, "column": 0, "message": str(e), "type": "UnknownError"})

    return errors

def print_yaml_errors(filename: str) -> None:
    """
    Checks YAML syntax and prints errors in a readable format.
    """
    errors = check_yaml_syntax(filename)
    if not errors:
        print(f"No syntax errors found in {filename}")
        return

    print(f"Syntax errors found in {filename}:")
    for err in errors:
        print(f"Line {err['line']}, Col {err['column']} [{err['type']}]: {err['message']}")