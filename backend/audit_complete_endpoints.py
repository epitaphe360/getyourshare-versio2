#!/usr/bin/env python3
"""
AUDIT COMPLET DE TOUS LES ENDPOINTS
Identifie tous les bugs potentiels qui peuvent causer des crashes en production
"""
import re
import os

backend_path = "/home/user/getyourshare-versio2/backend"
server_file = os.path.join(backend_path, "server.py")

print("="*80)
print("🔍 AUDIT COMPLET DES ENDPOINTS - IDENTIFICATION DE TOUS LES BUGS")
print("="*80)

with open(server_file, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

bugs_found = []

# Pattern 1: float() sans protection
print("\n1️⃣ Recherche: float() sans protection contre None/ValueError...")
float_pattern = r'float\([^)]+\.get\([^)]+\)\)'
matches = re.finditer(float_pattern, content)
float_bugs = []
for match in matches:
    # Trouver le numéro de ligne
    line_num = content[:match.start()].count('\n') + 1
    line_content = lines[line_num - 1].strip()
    if 'try:' not in line_content and 'except' not in line_content:
        float_bugs.append({
            'line': line_num,
            'code': line_content[:100],
            'type': 'UNSAFE_FLOAT_CONVERSION'
        })

print(f"   ⚠️  Trouvé {len(float_bugs)} conversions float() non protégées")

# Pattern 2: .get() sur None sans vérification
print("\n2️⃣ Recherche: .get() sans vérification None...")
get_chain_pattern = r'\.get\([^)]+\)\.get\('
matches = re.finditer(get_chain_pattern, content)
chained_get_bugs = []
for match in matches:
    line_num = content[:match.start()].count('\n') + 1
    line_content = lines[line_num - 1].strip()
    chained_get_bugs.append({
        'line': line_num,
        'code': line_content[:100],
        'type': 'CHAINED_GET_WITHOUT_NONE_CHECK'
    })

print(f"   ⚠️  Trouvé {len(chained_get_bugs)} chaînes .get() dangereuses")

# Pattern 3: for loop sur result.data sans vérifier if result.data
print("\n3️⃣ Recherche: for loop sur .data sans vérification...")
for_data_pattern = r'for\s+\w+\s+in\s+\w+\.data:'
matches = re.finditer(for_data_pattern, content)
for_data_bugs = []
for match in matches:
    line_num = content[:match.start()].count('\n') + 1
    # Vérifier s'il y a un "if result.data:" avant
    prev_lines = '\n'.join(lines[max(0, line_num-5):line_num])
    if 'if' not in prev_lines or '.data' not in prev_lines:
        line_content = lines[line_num - 1].strip()
        for_data_bugs.append({
            'line': line_num,
            'code': line_content[:100],
            'type': 'FOR_LOOP_WITHOUT_DATA_CHECK'
        })

print(f"   ⚠️  Trouvé {len(for_data_bugs)} boucles for sans vérification .data")

# Pattern 4: Endpoints sans try/except
print("\n4️⃣ Recherche: Endpoints sans try/except...")
endpoint_pattern = r'@app\.(get|post|put|patch|delete)\(["\']([^"\']+)["\']\)\s*\nasync def (\w+)'
matches = re.finditer(endpoint_pattern, content, re.MULTILINE)
endpoints_no_try = []

for match in matches:
    method = match.group(1)
    path = match.group(2)
    func_name = match.group(3)
    line_num = content[:match.start()].count('\n') + 1

    # Chercher le bloc de fonction (approximatif)
    func_start = match.end()
    # Chercher jusqu'à la prochaine définition de fonction ou fin de fichier
    next_func = re.search(r'\n@app\.|^\ndef |^async def ', content[func_start:], re.MULTILINE)
    if next_func:
        func_end = func_start + next_func.start()
    else:
        func_end = len(content)

    func_body = content[func_start:func_end]

    # Vérifier si try/except existe
    if 'try:' not in func_body:
        endpoints_no_try.append({
            'line': line_num,
            'method': method.upper(),
            'path': path,
            'function': func_name,
            'type': 'ENDPOINT_WITHOUT_TRY_CATCH'
        })

print(f"   ⚠️  Trouvé {len(endpoints_no_try)} endpoints sans try/except")

# Pattern 5: sum() sur liste qui peut être None
print("\n5️⃣ Recherche: sum() sans vérification...")
sum_pattern = r'sum\(\[[^\]]+\]\)'
matches = re.finditer(sum_pattern, content)
sum_bugs = []
for match in matches:
    line_num = content[:match.start()].count('\n') + 1
    line_content = lines[line_num - 1].strip()
    sum_bugs.append({
        'line': line_num,
        'code': line_content[:100],
        'type': 'SUM_WITHOUT_NONE_CHECK'
    })

print(f"   ⚠️  Trouvé {len(sum_bugs)} sum() potentiellement dangereux")

# RÉSUMÉ FINAL
print("\n" + "="*80)
print("📊 RÉSUMÉ DES BUGS TROUVÉS:")
print("="*80)

total_bugs = (
    len(float_bugs) +
    len(chained_get_bugs) +
    len(for_data_bugs) +
    len(endpoints_no_try) +
    len(sum_bugs)
)

print(f"\n🔴 TOTAL: {total_bugs} bugs potentiels identifiés\n")
print(f"   • Conversions float() non protégées: {len(float_bugs)}")
print(f"   • Chaînes .get() dangereuses: {len(chained_get_bugs)}")
print(f"   • Boucles for sans vérification .data: {len(for_data_bugs)}")
print(f"   • Endpoints sans try/except: {len(endpoints_no_try)}")
print(f"   • sum() sans protection: {len(sum_bugs)}")

# Sauvegarder les détails
print("\n📝 Génération du rapport détaillé...")

with open('AUDIT_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("RAPPORT D'AUDIT COMPLET DES ENDPOINTS\n")
    f.write("="*80 + "\n\n")

    f.write(f"TOTAL BUGS TROUVÉS: {total_bugs}\n\n")

    if float_bugs:
        f.write("\n" + "="*80 + "\n")
        f.write("1. CONVERSIONS FLOAT() NON PROTÉGÉES\n")
        f.write("="*80 + "\n")
        for bug in float_bugs[:20]:  # Limiter à 20 pour lisibilité
            f.write(f"\nLigne {bug['line']}:\n")
            f.write(f"  {bug['code']}\n")

    if endpoints_no_try:
        f.write("\n" + "="*80 + "\n")
        f.write("2. ENDPOINTS SANS TRY/EXCEPT\n")
        f.write("="*80 + "\n")
        for bug in endpoints_no_try[:20]:
            f.write(f"\nLigne {bug['line']}: {bug['method']} {bug['path']}\n")
            f.write(f"  Fonction: {bug['function']}\n")

print("✅ Rapport sauvegardé dans: AUDIT_REPORT.txt")
print("\n" + "="*80)
