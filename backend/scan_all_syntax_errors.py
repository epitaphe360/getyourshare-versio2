#!/usr/bin/env python3
"""
Script pour identifier et afficher TOUS les fichiers avec SyntaxError
"""
import os
import py_compile
import sys

errors = []
backend_path = "/home/user/getyourshare-versio2/backend"

print("🔍 Scanning TOUS les fichiers Python pour SyntaxError...")
print("="*70)

for root, dirs, files in os.walk(backend_path):
    # Skip __pycache__ directories
    if '__pycache__' in root:
        continue

    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                relative_path = filepath.replace(backend_path + "/", "")
                errors.append({
                    'file': relative_path,
                    'error': str(e.exc_value),
                    'line': getattr(e.exc_value, 'lineno', 'unknown')
                })

print(f"\n📊 RÉSULTATS:")
print(f"   Fichiers scannés: nombreux")
print(f"   Fichiers avec erreurs: {len(errors)}")
print("="*70)

if errors:
    print("\n❌ FICHIERS AVEC SYNTAXERROR:\n")
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error['file']}")
        print(f"   Ligne {error['line']}: {error['error']}")
        print()
else:
    print("\n✅ AUCUNE SYNTAXERROR TROUVÉE!")
    print("   Le backend peut démarrer sans erreurs de syntaxe.")

sys.exit(len(errors))
