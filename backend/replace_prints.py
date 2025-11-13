#!/usr/bin/env python3
"""
Script to replace all print() statements with logger calls
"""
import os
import re
from pathlib import Path

files_modified = 0
prints_replaced = 0

def determine_log_level(print_content):
    """Determine appropriate log level based on content"""
    content_lower = print_content.lower()

    if any(word in content_lower for word in ['error', 'failed', 'exception', 'critical', 'fatal']):
        return 'logger.error'
    elif any(word in content_lower for word in ['warning', 'warn', 'caution']):
        return 'logger.warning'
    elif any(word in content_lower for word in ['debug', 'trace']):
        return 'logger.debug'
    else:
        return 'logger.info'

def has_logger_import(content):
    """Check if file already imports logger"""
    return bool(re.search(r'from utils\.logger import.*logger', content))

def add_logger_import(content):
    """Add logger import at the top of the file after other imports"""
    lines = content.split('\n')

    # Find the last import line
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')) and 'logger' not in line:
            last_import_idx = i

    # Insert after last import or at beginning
    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, 'from utils.logger import logger')
    else:
        # No imports found, add at top (after docstring/comments)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''"):
                insert_idx = i
                break
        lines.insert(insert_idx, 'from utils.logger import logger')

    return '\n'.join(lines)

def replace_prints_in_file(file_path):
    """Replace print statements with logger calls in a single file"""
    global files_modified, prints_replaced

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count prints before
    before_count = len(re.findall(r'\bprint\s*\(', content))

    if before_count == 0:
        return

    # Replace print( with logger
    new_content = content
    modified = False

    # Pattern to match print statements (simple cases)
    # print("something") or print('something') or print(variable) or print(f"...")
    def replace_print(match):
        nonlocal modified
        modified = True

        full_match = match.group(0)
        print_content = match.group(1)

        # Determine log level
        log_method = determine_log_level(print_content)

        # Replace print with logger
        return f"{log_method}({print_content})"

    # Replace print statements
    new_content = re.sub(r'\bprint\s*\(([^)]+(?:\([^)]*\))*[^)]*)\)', replace_print, new_content)

    if not modified:
        return

    # Add logger import if not present
    if not has_logger_import(new_content):
        new_content = add_logger_import(new_content)

    # Count prints after
    after_count = len(re.findall(r'\bprint\s*\(', new_content))
    replaced = before_count - after_count

    if replaced > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        files_modified += 1
        prints_replaced += replaced
        print(f"✓ {file_path}: Replaced {replaced} print(s)")

def process_directory(directory):
    """Process all Python files in directory recursively"""
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py') and file != 'replace_prints.py':
                file_path = os.path.join(root, file)
                try:
                    replace_prints_in_file(file_path)
                except Exception as e:
                    print(f"✗ Error processing {file_path}: {e}")

if __name__ == '__main__':
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Starting print() replacement in {backend_dir}...\n")

    process_directory(backend_dir)

    print(f"\n✅ Done! Modified {files_modified} files, replaced {prints_replaced} print() statements.")
