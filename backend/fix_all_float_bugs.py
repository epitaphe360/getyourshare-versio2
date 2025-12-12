#!/usr/bin/env python3
"""
CORRECTION FINALE - TOUS LES float() RESTANTS
"""
import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

original = content

print("🔧 Correction FINALE des float() restants...")

# Fix: float(x.get("field", 0)) -> float(x.get("field", 0) or 0)
# Seulement si "or 0" n'est pas déjà présent
content = re.sub(
    r'float\((\w+\.get\([^)]+\))\)(?!\s+or)',
    r'float(\1 or 0)',
    content
)

fixes = content.count('float(') - original.count('float(')

print(f"✅ Ajout de 'or 0' aux float() non protégés")

# Sauvegarder
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Vérifier
import py_compile
try:
    py_compile.compile('server.py', doraise=True)
    print("✅ Syntaxe OK")
    print(f"✅ Modifications appliquées")
except Exception as e:
    print(f"❌ Erreur: {e}")
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(original)
    print("❌ Annulé")
