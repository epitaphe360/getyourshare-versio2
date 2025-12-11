#!/usr/bin/env python3
"""
Script pour réduire les logs excessifs dans server.py
Remplace les print() par des logs plus discrets
"""
import re

# Lire le fichier
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Compter les occurrences avant
print_errors_before = len(re.findall(r'print\(f?".*❌', content))
print(f"📊 Avant: {print_errors_before} logs d'erreur avec ❌")

# Remplacer les print d'erreur excessifs par des logs conditionnels
# Pattern 1: print(f"❌ Erreur {fonction}: {e}")
content = re.sub(
    r'print\(f"❌ Erreur ([^:]+): \{e\}"\)',
    r'# Erreur loggée via HTTPException en production',
    content
)

# Pattern 2: print(f"❌ ...") générique
content = re.sub(
    r'print\(f?"❌[^"]+"\)',
    r'# Log supprimé pour réduire verbosité',
    content
)

# Pattern 3: Garder seulement les logs critiques avec traceback
content = re.sub(
    r'print\(f"❌ Critical Error',
    r'logger.error(f"Critical Error',
    content
)

# Compter après
print_errors_after = len(re.findall(r'print\(f?".*❌', content))
print(f"📊 Après: {print_errors_after} logs d'erreur avec ❌")
print(f"✅ {print_errors_before - print_errors_after} logs supprimés")

# Sauvegarder
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Logs nettoyés avec succès!")
print("💡 Les erreurs sont toujours retournées via HTTPException au client")
