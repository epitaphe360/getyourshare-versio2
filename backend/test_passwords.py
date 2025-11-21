#!/usr/bin/env python
"""Tester différents mots de passe possibles"""

import bcrypt

hash_stored = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5BI8bVp3G5UNy"

# Essayer des mots de passe courants
passwords_to_try = [
    "TestPassword123!",
    "Password123!",
    "Admin123!",
    "admin123",
    "password123",
    "123456",
    "Getyourshare123!",
    "ShareYourSales123!",
]

print("Vérification des mots de passe possibles...")
print(f"Hash: {hash_stored}\n")

for pwd in passwords_to_try:
    try:
        result = bcrypt.checkpw(pwd.encode('utf-8'), hash_stored.encode('utf-8'))
        status = "✅ MATCH!" if result else "❌"
        print(f"{status} Password: '{pwd}'")
    except Exception as e:
        print(f"Erreur avec '{pwd}': {e}")
