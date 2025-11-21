"""
Script pour remplacer verify_token par get_current_user_from_cookie dans server.py
"""
import re

# Lire le fichier
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Compter les occurrences avant
count_before = content.count('Depends(verify_token)')
print(f"[INFO] Trouve {count_before} occurrences de 'Depends(verify_token)'")

# Pattern 1: payload: dict = Depends(verify_token) -> current_user: dict = Depends(get_current_user_from_cookie)
pattern1 = r'payload:\s*dict\s*=\s*Depends\(verify_token\)'
replacement1 = 'current_user: dict = Depends(get_current_user_from_cookie)'
content = re.sub(pattern1, replacement1, content)

# Pattern 2: payload.get("sub") ou payload.get("user_id") -> current_user.get("id")
content = re.sub(r'payload\.get\(["\']sub["\']\)', 'current_user.get("id")', content)
content = re.sub(r'payload\.get\(["\']user_id["\']\)', 'current_user.get("id")', content)

# Pattern 3: payload.get("role") -> current_user.get("role")
content = re.sub(r'payload\.get\(["\']role["\']\)', 'current_user.get("role")', content)

# Pattern 4: payload.get("email") -> current_user.get("email")
content = re.sub(r'payload\.get\(["\']email["\']\)', 'current_user.get("email")', content)

# Pattern 5: Supprimer les lignes 'user = get_user_by_id(user_id)' qui suivent user_id = current_user.get("id")
# Car current_user contient déjà toutes les infos
lines = content.split('\n')
new_lines = []
skip_next_get_user = False

for i, line in enumerate(lines):
    # Si la ligne précédente définit user_id depuis current_user, marquer pour skip
    if i > 0 and 'user_id = current_user.get("id")' in lines[i-1]:
        if 'user = get_user_by_id(user_id)' in line or 'user = db_helpers.get_user_by_id(user_id)' in line:
            # Remplacer par user = current_user
            new_lines.append(line.replace('get_user_by_id(user_id)', 'current_user').replace('db_helpers.', ''))
            continue
    
    new_lines.append(line)

content = '\n'.join(new_lines)

# Compter les occurrences après
count_after = content.count('Depends(verify_token)')
print(f"[OK] Remplace {count_before - count_after} occurrences")
print(f"[WARN] Reste {count_after} occurrences (probablement des cas speciaux)")

# Écrire le fichier
with open('server_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[OK] Fichier sauvegarde dans 'server_fixed.py'")
print("[INFO] Verifiez le fichier, puis renommez-le en 'server.py' si tout est correct")
