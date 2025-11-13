#!/usr/bin/env python3
"""
Script to fix bare except statements by replacing them with except Exception:
"""
import os
import re

files_modified = 0
excepts_fixed = 0

def fix_bare_except_in_file(file_path):
    """Fix bare except statements in a single file"""
    global files_modified, excepts_fixed

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count bare excepts before
    before_count = len(re.findall(r'^\s*except:\s*$', content, re.MULTILINE))

    if before_count == 0:
        return

    # Replace bare except: with except Exception:
    new_content = re.sub(
        r'^(\s*)except:\s*$',
        r'\1except Exception:',
        content,
        flags=re.MULTILINE
    )

    # Count after
    after_count = len(re.findall(r'^\s*except:\s*$', new_content, re.MULTILINE))
    fixed = before_count - after_count

    if fixed > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        files_modified += 1
        excepts_fixed += fixed
        print(f"✓ {file_path}: Fixed {fixed} bare except(s)")

def process_directory(directory):
    """Process all Python files in directory recursively"""
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py') and file != 'fix_bare_except.py':
                file_path = os.path.join(root, file)
                try:
                    fix_bare_except_in_file(file_path)
                except Exception as e:
                    print(f"✗ Error processing {file_path}: {e}")

if __name__ == '__main__':
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Starting bare except fix in {backend_dir}...\n")

    process_directory(backend_dir)

    print(f"\n✅ Done! Modified {files_modified} files, fixed {excepts_fixed} bare except statements.")
