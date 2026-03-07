#!/usr/bin/env python3
"""
Correction automatique des imports wildcard
Remplace 'from module import *' par imports explicites
"""

import re
from pathlib import Path

# Mapping manuel des imports utilisés par fichier
MANUAL_IMPORTS = {
    'backend/server.py': {
        'module': 'db_helpers',
        'imports': [
            'get_user_by_id',
            'get_user_by_email',
            'create_user',
            'update_user',
            'hash_password',
        ]
    },
    'backend/seed_all_data.py': {
        'module': 'mock_data',
        'imports': [
            'MOCK_USERS',
            'MOCK_PRODUCTS',
            'MOCK_SALES',
        ]
    },
    'backend/server_mock_backup.py': {
        'module': 'mock_data',
        'imports': [
            'MOCK_USERS',
            'MOCK_PRODUCTS',
        ]
    },
    'backend/server_tracknow_backup.py': {
        'module': 'mock_data',
        'imports': [
            'MOCK_USERS',
        ]
    },
    'backend/setup_supabase.py': {
        'module': 'mock_data',
        'imports': [
            'MOCK_USERS',
            'MOCK_PRODUCTS',
            'MOCK_SALES',
        ]
    },
    'backend/advanced_endpoints.py': {
        'module': 'advanced_helpers',
        'imports': [
            'generate_verification_token',
            'send_verification_email',
        ]
    },
}

def fix_wildcard_import(file_path, module_name, explicit_imports):
    """Remplacer import wildcard par imports explicites"""
    
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"⚠️  {file_path}: Fichier introuvable, ignoré")
        return False
    
    with open(file_path_obj, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si wildcard import existe
    wildcard_pattern = f'from {module_name} import \\*'
    if not re.search(wildcard_pattern, content):
        print(f"ℹ️  {file_path}: Pas d'import wildcard de '{module_name}', ignoré")
        return False
    
    # Construire import explicite
    if len(explicit_imports) <= 3:
        import_line = f"from {module_name} import {', '.join(explicit_imports)}"
    else:
        import_line = f"from {module_name} import (\n"
        for imp in explicit_imports:
            import_line += f"    {imp},\n"
        import_line += ")"
    
    # Remplacer
    new_content = re.sub(wildcard_pattern, import_line, content)
    
    with open(file_path_obj, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {file_path}: {len(explicit_imports)} imports explicites")
    return True

def main():
    print("♻️  CORRECTION IMPORTS WILDCARD")
    print("="*60)
    print()
    
    total_fixed = 0
    total_files = len(MANUAL_IMPORTS)
    
    for file_path, config in MANUAL_IMPORTS.items():
        module = config['module']
        imports = config['imports']
        
        print(f"▶ {file_path}")
        print(f"  Module: {module}")
        print(f"  Imports: {len(imports)}")
        
        if fix_wildcard_import(file_path, module, imports):
            total_fixed += 1
        
        print()
    
    print("="*60)
    print(f"✅ Correction terminée: {total_fixed}/{total_files} fichiers modifiés")
    print("="*60)
    
    return total_fixed

if __name__ == "__main__":
    try:
        total = main()
        exit(0 if total > 0 else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
