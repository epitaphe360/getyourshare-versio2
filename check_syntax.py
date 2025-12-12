import os
import py_compile

def check_syntax(start_path):
    print(f"Checking syntax for Python files in {start_path}...")
    errors = []
    for root, dirs, files in os.walk(start_path):
        if "node_modules" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    py_compile.compile(full_path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(str(e))
                except Exception as e:
                    errors.append(f"Error checking {full_path}: {str(e)}")
    
    if errors:
        print(f"Found {len(errors)} syntax errors:")
        for error in errors:
            print(error)
    else:
        print("No syntax errors found.")

if __name__ == "__main__":
    check_syntax(".")