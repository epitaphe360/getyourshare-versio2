#!/usr/bin/env python3
"""
Correction automatique des bare except clauses
Remplace 'except:' par 'except Exception as e:' avec logging
"""

import re
from pathlib import Path

# Fichiers prioritaires à corriger
PRIORITY_FILES = [
    'backend/server.py',
    'backend/marketplace_endpoints.py',
    'backend/services/lead_service.py',
    'backend/server_complete.py',
]

def fix_bare_except_in_file(file_path):
    """Remplacer bare except par Exception avec logging"""
    
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"⚠️  {file_path}: Fichier introuvable, ignoré")
        return 0
    
    with open(file_path_obj, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modifications = 0
    new_lines = []
    i = 0
    has_logging = False
    
    # Vérifier si logging/structlog existe déjà
    content_str = ''.join(lines)
    has_logging = 'import logging' in content_str or 'import structlog' in content_str
    
    while i < len(lines):
        line = lines[i]
        
        # Détecter "except:" ou "except: pass"
        if re.match(r'^(\s+)except:\s*$', line):
            match = re.match(r'^(\s+)except:\s*$', line)
            indent = match.group(1)
            
            # Vérifier si ligne suivante est "pass"
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            is_pass_only = next_line.strip() == "pass"
            
            # Remplacer par Exception avec logging
            new_lines.append(f"{indent}except Exception as e:\n")
            
            if is_pass_only:
                new_lines.append(f"{indent}    logger.error(f'Unexpected error: {{e}}', exc_info=True)\n")
                new_lines.append(f"{indent}    # TODO: Gérer cette erreur correctement\n")
                i += 1  # Skip la ligne "pass"
            else:
                new_lines.append(f"{indent}    logger.error(f'Error in operation: {{e}}', exc_info=True)\n")
            
            modifications += 1
        else:
            new_lines.append(line)
        
        i += 1
    
    if modifications > 0:
        # Ajouter import logging si nécessaire
        if not has_logging:
            # Trouver où insérer l'import
            for idx, line in enumerate(new_lines):
                if line.startswith('import ') or line.startswith('from '):
                    # Chercher la fin du bloc d'imports
                    for j in range(idx, len(new_lines)):
                        if not (new_lines[j].startswith('import ') or 
                                new_lines[j].startswith('from ') or 
                                new_lines[j].strip() == ''):
                            new_lines.insert(j, '\nimport logging\n')
                            new_lines.insert(j + 1, 'logger = logging.getLogger(__name__)\n\n')
                            break
                    break
        
        with open(file_path_obj, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ {file_path}: {modifications} bare except corrigés")
        return modifications
    
    print(f"ℹ️  {file_path}: Aucun bare except trouvé")
    return 0

def main():
    print("🐛 CORRECTION BARE EXCEPT CLAUSES")
    print("="*60)
    print()
    
    total_fixes = 0
    
    for file_path in PRIORITY_FILES:
        print(f"▶ {file_path}")
        fixes = fix_bare_except_in_file(file_path)
        total_fixes += fixes
        print()
    
    print("="*60)
    print(f"✅ Total: {total_fixes} bare except clauses corrigées")
    print("="*60)
    
    return total_fixes

if __name__ == "__main__":
    try:
        total = main()
        exit(0)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
