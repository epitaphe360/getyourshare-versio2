#!/usr/bin/env python3
"""
Script pour détecter les blocs try avec indentation incorrecte
"""
import os
import re
from pathlib import Path

def check_file(filepath):
    """Vérifier un fichier Python pour des erreurs d'indentation après try"""
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            # Chercher les lignes qui contiennent "try:" avec indentation
            if re.match(r'^(\s+)try:\s*$', line):
                # Calculer l'indentation du try
                try_indent = len(line) - len(line.lstrip())

                # Vérifier la ligne suivante
                if i < len(lines):
                    next_line = lines[i]

                    # Ignorer les lignes vides et commentaires
                    if next_line.strip() == '' or next_line.strip().startswith('#'):
                        continue

                    # Calculer l'indentation de la ligne suivante
                    next_indent = len(next_line) - len(next_line.lstrip())

                    # La ligne suivante DOIT avoir plus d'indentation que le try
                    if next_indent <= try_indent:
                        errors.append({
                            'file': filepath,
                            'line': i,
                            'try_indent': try_indent,
                            'next_indent': next_indent,
                            'try_line': line.rstrip(),
                            'next_line': next_line.rstrip()
                        })

    except Exception as e:
        print(f"❌ Erreur lecture {filepath}: {e}")

    return errors

def main():
    """Chercher dans tous les fichiers Python"""
    backend_dir = Path(__file__).resolve().parent
    all_errors = []

    # Chercher tous les fichiers .py
    for root, dirs, files in os.walk(backend_dir):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                errors = check_file(filepath)
                all_errors.extend(errors)

    if all_errors:
        print(f"\n🚨 TROUVÉ {len(all_errors)} ERREURS D'INDENTATION:\n")

        for error in all_errors:
            rel_path = error['file'].replace('/home/user/getyourshare-versio2/backend/', '')
            print(f"❌ {rel_path}:{error['line']}")
            print(f"   try indent: {error['try_indent']} | next indent: {error['next_indent']}")
            print(f"   {error['try_line']}")
            print(f"   {error['next_line']}")
            print()
    else:
        print("✅ Aucune erreur d'indentation trouvée!")

    return len(all_errors)

if __name__ == '__main__':
    exit(main())
