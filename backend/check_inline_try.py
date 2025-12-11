#!/usr/bin/env python3
"""
Script pour détecter les try: au milieu de chaînes de méthodes
"""
import os
import re

def check_file_for_inline_try(filepath):
    """Vérifier un fichier pour des try au milieu de chaînes"""
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Chercher les lignes qui se terminent par un backslash (continuation)
            if line.rstrip().endswith('\\'):
                # Vérifier si la ligne suivante contient "try:"
                if i < len(lines):
                    next_line = lines[i].strip()
                    if next_line == 'try:' or next_line.startswith('try:'):
                        errors.append({
                            'file': filepath,
                            'line': i + 1,
                            'prev_line': line.rstrip(),
                            'problem_line': lines[i].rstrip()
                        })

    except Exception as e:
        print(f"❌ Erreur lecture {filepath}: {e}")

    return errors

def main():
    """Chercher dans tous les fichiers Python"""
    backend_dir = '/home/user/getyourshare-versio2/backend'
    all_errors = []

    # Chercher tous les fichiers .py
    for root, dirs, files in os.walk(backend_dir):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py') and file not in ['check_indentation.py', 'fix_all_indentation.py', 'check_inline_try.py']:
                filepath = os.path.join(root, file)
                errors = check_file_for_inline_try(filepath)
                all_errors.extend(errors)

    if all_errors:
        print(f"\n🚨 TROUVÉ {len(all_errors)} TRY AU MILIEU DE CHAÎNES:\n")

        for error in all_errors:
            rel_path = error['file'].replace('/home/user/getyourshare-versio2/backend/', '')
            print(f"❌ {rel_path}:{error['line']}")
            print(f"   {error['prev_line']}")
            print(f"   {error['problem_line']}")
            print()
    else:
        print("✅ Aucun try au milieu de chaînes trouvé!")

    return len(all_errors)

if __name__ == '__main__':
    exit(main())
