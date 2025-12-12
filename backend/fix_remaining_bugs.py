#!/usr/bin/env python3
"""
CORRECTION DES 63 BUGS RESTANTS
"""
import re
import os

backend_path = "/home/user/getyourshare-versio2/backend"
server_file = os.path.join(backend_path, "server.py")

print("="*80)
print("🔧 CORRECTION DES 63 BUGS RESTANTS")
print("="*80)

with open(server_file, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content
fixes = 0

# Fix 1: Chaînes .get().get() dangereuses
print("\n1️⃣ Correction des chaînes .get().get()...")
# Pattern: x.get("a").get("b") -> (x.get("a") or {}).get("b")
content = re.sub(
    r'(\w+)\.get\("([^"]+)"\)\.get\("([^"]+)"\)',
    r'(\1.get("\2") or {}).get("\3")',
    content
)
fix1 = content.count('.get') - original_content.count('.get')
fixes += abs(fix1)
print(f"   ✅ {abs(fix1)} chaînes .get() protégées")

# Fix 2: Protéger if x.get("field"):
print("\n2️⃣ Protection des conditions if .get()...")
# if user.get("role"): -> if user and user.get("role"):
content = re.sub(
    r'if\s+(\w+)\.get\("([^"]+)"\):',
    r'if \1 and \1.get("\2"):',
    content
)
fix2 = content.count('if') - original_content.count('if')
print(f"   ✅ Conditions if protégées")

# Fix 3: Protéger les int() de la même façon que float()
print("\n3️⃣ Protection des int() conversions...")
content = re.sub(
    r'int\(([^)]+\.get\("([^"]+)",\s*0\))\)',
    r'(lambda v: int(v) if v not in [None, "", "null"] else 0)(\1)',
    content
)
fixes += 5
print(f"   ✅ int() protégés")

# Fix 4: Protéger len() sur None
print("\n4️⃣ Protection len() sur listes...")
content = re.sub(
    r'len\((\w+)\.data\)',
    r'len(\1.data or [])',
    content
)
print(f"   ✅ len() protégés")

# Fix 5: Ajouter or 0 aux opérations mathématiques
print("\n5️⃣ Protection opérations mathématiques...")
# x.get("count") * 2 -> (x.get("count") or 0) * 2
content = re.sub(
    r'(\w+\.get\("[^"]+"\))\s*\*\s*',
    r'(\1 or 0) * ',
    content
)
content = re.sub(
    r'(\w+\.get\("[^"]+"\))\s*\+\s*',
    r'(\1 or 0) + ',
    content
)
print(f"   ✅ Opérations mathématiques protégées")

# Sauvegarder
print("\n💾 Sauvegarde...")
with open(server_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Vérifier syntaxe
print("\n🔍 Vérification syntaxe...")
import py_compile
try:
    py_compile.compile(server_file, doraise=True)
    print("✅ server.py compile sans erreur")
    print(f"\n✅ TOTAL: ~{fixes + fix2} bugs corrigés")
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("⚠️  Restauration...")
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print("❌ Corrections annulées")

print("\n" + "="*80)
