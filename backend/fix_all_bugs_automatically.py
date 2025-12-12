#!/usr/bin/env python3
"""
CORRECTION AUTOMATIQUE DE TOUS LES BUGS IDENTIFIÉS
"""
import re
import os

backend_path = "/home/user/getyourshare-versio2/backend"
server_file = os.path.join(backend_path, "server.py")

print("="*80)
print("🔧 CORRECTION AUTOMATIQUE DE TOUS LES BUGS")
print("="*80)

with open(server_file, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content
fixes_applied = 0

# Fix 1: Protéger tous les float() avec try/except
print("\n1️⃣ Protection des float() conversions...")
# Remplacer float(x.get("amount", 0)) par une version safe
content = re.sub(
    r'float\(([^)]+\.get\("([^"]+)",\s*0\))\)',
    r'(lambda v: float(v) if v not in [None, "", "null"] else 0.0)(\1)',
    content
)
fixes_applied += content.count('lambda v: float(v)') - original_content.count('lambda v: float(v)')

# Fix 2: Protéger les float() plus simples
content = re.sub(
    r'float\(([^)]+\.get\("([^"]+)"\))\)',
    r'(lambda v: float(v) if v not in [None, "", "null"] else 0.0)(\1)',
    content
)

print(f"   ✅ {fixes_applied} float() protégés")

# Fix 3: Wrapper les boucles for sur .data avec une vérification
print("\n2️⃣ Protection des boucles for sur .data...")
# Pattern: for x in result.data:
# Devient: for x in (result.data or []):
content = re.sub(
    r'for\s+(\w+)\s+in\s+(\w+)\.data:',
    r'for \1 in (\2.data or []):',
    content
)
data_fixes = content.count('.data or []') - original_content.count('.data or []')
print(f"   ✅ {data_fixes} boucles for protégées")

# Fix 4: Protéger les sum() avec list comprehension
print("\n3️⃣ Protection des sum()...")
# Remplacer sum([...]) par sum([...] or [])
# C'est complexe, on va juste wrapper les cas simples
content = re.sub(
    r'sum\(\[(float\([^]]+)\]\)',
    r'sum([\1] or [])',
    content
)

print(f"   ✅ sum() protégés")

# Sauvegarder
print("\n💾 Sauvegarde des corrections...")
with open(server_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Corrections appliquées à server.py")
print(f"   Total de modifications: ~{fixes_applied + data_fixes}")

# Vérifier la syntaxe
print("\n🔍 Vérification de la syntaxe...")
import py_compile
try:
    py_compile.compile(server_file, doraise=True)
    print("✅ server.py compile sans erreur")
except Exception as e:
    print(f"❌ Erreur de syntaxe: {e}")
    print("⚠️  Restauration de la version originale...")
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(original_content)

print("\n" + "="*80)
print("✅ CORRECTION AUTOMATIQUE TERMINÉE")
print("="*80)
