#!/usr/bin/env python
"""Tester le mot de passe réel"""

import bcrypt

hash_stored = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy"

# Essayer les mots de passe par défaut
passwords = [
    "Test123!",
    "password123",
    "Password123!",
]

print("Vérification des mots de passe...")
print(f"Hash: {hash_stored}\n")

for pwd in passwords:
    result = bcrypt.checkpw(pwd.encode('utf-8'), hash_stored.encode('utf-8'))
    status = "✅ MATCH!" if result else "❌"
    print(f"{status} Password: '{pwd}'")

# Si aucun ne correspond, créer le hash pour "password123" et tester
print("\n" + "="*60)
print("Création du hash pour 'password123':")
hash_pwd123 = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
print(f"Hash généré: {hash_pwd123}")

# Vérifier si le hash stocké correspond à "password123"
result = bcrypt.checkpw(b"password123", hash_stored.encode('utf-8'))
print(f"\nLe hash correspond-il à 'password123'? {result}")

# Vérifier si le hash stocké correspond à "Test123!"
result = bcrypt.checkpw(b"Test123!", hash_stored.encode('utf-8'))
print(f"Le hash correspond-il à 'Test123!'? {result}")
