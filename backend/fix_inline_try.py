#!/usr/bin/env python3
"""
Script pour corriger TOUS les try: au milieu de chaînes de méthodes
"""
import os
import re

def fix_inline_try(filepath):
    """Corriger les try au milieu de chaînes dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        i = 0
        while i < len(lines):
            line = lines[i]

            # Chercher ligne se terminant par backslash
            if line.rstrip().endswith('\\') and i + 1 < len(lines):
                next_line = lines[i + 1]

                # Si la ligne suivante est "try:", c'est le problème
                if next_line.strip() in ['try:', 'try:']:
                    # Trouver le début de la chaîne de méthodes
                    start_idx = i
                    while start_idx > 0:
                        prev_line = lines[start_idx - 1]
                        if '=' in prev_line and not prev_line.rstrip().endswith('\\'):
                            break
                        if not prev_line.rstrip().endswith('\\'):
                            break
                        start_idx -= 1

                    # Trouver la fin de la chaîne (après except)
                    end_idx = i + 1
                    found_except = False
                    while end_idx < len(lines):
                        if 'except' in lines[end_idx]:
                            found_except = True
                        if found_except and not lines[end_idx].rstrip().endswith('\\'):
                            break
                        end_idx += 1

                    if found_except and end_idx < len(lines):
                        # Extraire l'indentation de base
                        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

                        # Ligne d'assignation
                        assign_line = lines[start_idx]
                        var_name = assign_line.split('=')[0].strip() if '=' in assign_line else 'result'

                        # Construire le nouveau code
                        new_lines = []

                        # try:
                        new_lines.append(' ' * base_indent + 'try:\n')

                        # Toutes les lignes de la chaîne (sans le try et except)
                        for idx in range(start_idx, end_idx + 1):
                            if idx == i + 1:  # Skip la ligne "try:"
                                continue
                            if 'except' in lines[idx] and idx > i + 1:  # Skip les lignes except/pass
                                continue
                            if 'pass' in lines[idx] and idx > i + 1:
                                continue

                            # Indenter correctement
                            line_content = lines[idx]
                            line_indent = len(line_content) - len(line_content.lstrip())
                            new_lines.append(' ' * 4 + line_content)

                        # except Exception:
                        new_lines.append(' ' * base_indent + 'except Exception:\n')

                        # Appel sans .single()
                        fallback_lines = []
                        for idx in range(start_idx, i + 1):
                            line_content = lines[idx]
                            fallback_lines.append(' ' * 4 + line_content)

                        # Ligne .execute() sans .single()
                        if end_idx < len(lines):
                            exec_line = lines[end_idx]
                            if '.execute()' in exec_line:
                                fallback_lines.append(' ' * 4 + exec_line)

                        new_lines.extend(fallback_lines)

                        # Remplacer dans lines
                        lines[start_idx:end_idx + 1] = new_lines
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

    # Liste des fichiers problématiques
    problem_files = [
        'admin_payouts_endpoints.py',
        'collaboration_endpoints.py',
        'commercial_endpoints.py',
        'commercials_directory_endpoints.py',
        'company_links_management.py',
        'db_queries_real.py',
        'domain_endpoints.py',
        'gamification_endpoints.py',
        'influencers_directory_endpoints.py',
        'stripe_webhook_handler.py',
        'subscription_helpers_simple.py',
        'team_endpoints.py',
        'services/commercial_invoice_service.py',
        'services/influencer_invoice_service.py'
    ]

    print("⚠️ Cette correction est complexe.")
    print("⚠️ Il est plus sûr de les corriger manuellement.")
    print("⚠️ Je vais juste supprimer les try/except au milieu des chaînes.")
    print()

    return 0  # Ne pas exécuter automatiquement

if __name__ == '__main__':
    exit(main())
