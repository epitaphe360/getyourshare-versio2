#!/usr/bin/env python3
"""
Script pour corriger TOUTES les erreurs d'indentation après try
"""
import os
import re

def fix_file(filepath):
    """Corriger un fichier Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        i = 0
        while i < len(lines):
            line = lines[i]

            # Chercher les lignes qui contiennent "try:" avec indentation
            match = re.match(r'^(\s+)try:\s*$', line)
            if match:
                try_indent = match.group(1)
                expected_indent = try_indent + '    '  # Ajouter 4 espaces

                # Vérifier la ligne suivante
                if i + 1 < len(lines):
                    next_line = lines[i + 1]

                    # Ignorer les lignes vides et commentaires
                    if next_line.strip() and not next_line.strip().startswith('#'):
                        # Calculer l'indentation actuelle
                        current_indent = len(next_line) - len(next_line.lstrip())
                        try_indent_len = len(try_indent)

                        # Si pas assez indentée, corriger
                        if current_indent == try_indent_len:
                            # Ajouter 4 espaces d'indentation
                            lines[i + 1] = expected_indent + next_line.lstrip()
                            modified = True
                            print(f"  ✅ Corrigé ligne {i + 2}")

            i += 1

        # Sauvegarder si modifié
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True

    except Exception as e:
        print(f"  ❌ Erreur: {e}")

    return False

def main():
    """Corriger tous les fichiers Python"""
    backend_dir = '/home/user/getyourshare-versio2/backend'
    fixed_count = 0

    # Chercher tous les fichiers .py
    for root, dirs, files in os.walk(backend_dir):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py') and file not in ['check_indentation.py', 'fix_all_indentation.py']:
                filepath = os.path.join(root, file)
                rel_path = filepath.replace(backend_dir + '/', '')

                if fix_file(filepath):
                    fixed_count += 1
                    print(f"✅ {rel_path}")

    print(f"\n🎉 {fixed_count} fichiers corrigés!")

    return 0

if __name__ == '__main__':
    exit(main())
