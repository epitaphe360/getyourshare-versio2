#!/usr/bin/env python3
"""
Script pour corriger automatiquement les SyntaxErrors les plus courants
"""
import os
import re

backend_path = "/home/user/getyourshare-versio2/backend"

files_to_fix = [
    "check_test_accounts.py",
    "create_tables.py",
    "seed_demo_data.py",
    "test_2fa_status.py",
    "test_api_format.py",
    "test_conversations.py",
    "test_conversations_simple.py",
    "test_features.py",
    "test_invoices.py",
    "tous_les_endpoints_partie1.py",
    "tests/conftest_real_db.py",
    "tests/test_database_setup.py"
]

fixes_applied = 0

for filename in files_to_fix:
    filepath = os.path.join(backend_path, filename)

    if not os.path.exists(filepath):
        print(f"⚠️  {filename} n'existe pas")
        continue

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix 1: Backslash in f-string - déjà fait manuellement pour certains

        # Fix 2: Mauvaise indentation après try:
        # Chercher "try:\n" suivi d'une ligne non-indentée
        content = re.sub(
            r'try:\n(\S)',
            r'try:\n    \1',
            content
        )

        # Fix 3: Triple-quoted string non terminée - difficile à fix automatiquement
        # On va juste logger

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename} - Fix d'indentation appliqué")
            fixes_applied += 1
        else:
            print(f"⚠️  {filename} - Aucun fix automatique disponible (vérification manuelle requise)")

    except Exception as e:
        print(f"❌ {filename} - Erreur: {e}")

print(f"\n📊 {fixes_applied} fichiers corrigés automatiquement")
print("⚠️  Les fichiers restants nécessitent une correction manuelle")
