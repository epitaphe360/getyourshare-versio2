#!/usr/bin/env python3
"""
Script pour SUPPRIMER les try/except au milieu de chaînes de méthodes
"""
import os
import re

def remove_inline_try(filepath):
    """Supprimer les try au milieu de chaînes dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            original_lines = content.splitlines(keepends=True)

        lines = content.splitlines(keepends=True)
        modified = False
        fixed_count = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Chercher ligne se terminant par backslash suivie de "try:"
            if i + 1 < len(lines) and line.rstrip().endswith('\\'):
                next_line = lines[i + 1]

                if next_line.strip() in ['try:', 'try:']:
                    # Trouver et supprimer le bloc try/except/pass
                    # Les lignes à supprimer sont:
                    # - La ligne "try:"
                    # - La ligne "except Exception:"
                    # - La ligne "pass"

                    # Supprimer "try:"
                    del lines[i + 1]

                    # Chercher et supprimer "except Exception:" et "pass"
                    j = i + 1
                    while j < len(lines):
                        if 'except Exception:' in lines[j]:
                            del lines[j]
                            # Supprimer aussi le "pass" suivant
                            if j < len(lines) and 'pass' in lines[j]:
                                del lines[j]
                            break
                        j += 1

                    modified = True
                    fixed_count += 1
                    print(f"  ✅ Supprimé try/except inline ligne {i + 2}")

            i += 1

        # Sauvegarder si modifié
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return fixed_count

    except Exception as e:
        print(f"  ❌ Erreur: {e}")

    return 0

def main():
    """Corriger tous les fichiers Python"""
    backend_dir = '/home/user/getyourshare-versio2/backend'
    total_fixed = 0

    # Chercher tous les fichiers .py
    for root, dirs, files in os.walk(backend_dir):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.py') and file not in ['check_indentation.py', 'fix_all_indentation.py', 'check_inline_try.py', 'fix_inline_try.py', 'remove_inline_try.py']:
                filepath = os.path.join(root, file)
                rel_path = filepath.replace(backend_dir + '/', '')

                fixed = remove_inline_try(filepath)
                if fixed > 0:
                    total_fixed += fixed
                    print(f"✅ {rel_path} ({fixed} corrections)")

    print(f"\n🎉 {total_fixed} try/except inline supprimés!")

    return 0

if __name__ == '__main__':
    exit(main())
