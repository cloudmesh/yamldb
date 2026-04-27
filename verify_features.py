from yamldb import YamlDB
import os
from pathlib import Path
from contextlib import suppress

def test_dot_notation():
    print("Testing dot-notation substitution...")
    filename = "test_dot.yaml"
    with open(filename, "w") as f:
        f.write("a:\n  b: 10\n  c: '{a.b}'\n")
    
    db = YamlDB(filename=filename)
    val = db.get("a.c")
    print(f"Value of a.c: {val}")
    assert val == 10, f"Expected 10, got {val}"
    print("Dot-notation substitution passed!")
    os.remove(filename)
    with suppress(FileNotFoundError):
        os.remove(f"{filename}.lock")

def test_load_directive():
    print("\nTesting #load directive...")
    f1 = "file1.yaml"
    f2 = "file2.yaml"
    with open(f1, "w") as f:
        f.write("key1: value1\n")
    with open(f2, "w") as f:
        f.write(f"#load {f1}\nkey2: value2\n")
    
    db = YamlDB(filename=f2)
    val1 = db.get("key1")
    val2 = db.get("key2")
    print(f"key1: {val1}, key2: {val2}")
    assert val1 == "value1", f"Expected value1, got {val1}"
    assert val2 == "value2", f"Expected value2, got {val2}"
    print("#load directive passed!")
    os.remove(f1)
    os.remove(f2)
    with suppress(FileNotFoundError):
        os.remove(f"{f2}.lock")

def test_combined():
    print("\nTesting combined #load and substitution...")
    f1 = "comb1.yaml"
    f2 = "comb2.yaml"
    with open(f1, "w") as f:
        f.write("a: 10\n")
    with open(f2, "w") as f:
        f.write(f"#load {f1}\nb: '{{a}}'\n")
    
    db = YamlDB(filename=f2)
    val_b = db.get("b")
    print(f"Value of b: {val_b}")
    assert val_b == 10, f"Expected 10, got {val_b}"
    print("Combined functionality passed!")
    os.remove(f1)
    os.remove(f2)
    with suppress(FileNotFoundError):
        os.remove(f"{f2}.lock")

if __name__ == "__main__":
    try:
        test_dot_notation()
        test_load_directive()
        test_combined()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)