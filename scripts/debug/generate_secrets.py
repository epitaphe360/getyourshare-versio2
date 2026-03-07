#!/usr/bin/env python3
"""
Génération de secrets sécurisés pour l'application
Usage: python generate_secrets.py
"""

import secrets
from datetime import datetime
from pathlib import Path

def generate_secure_secrets():
    """Génère tous les secrets requis avec entropie cryptographique"""
    
    secrets_dict = {
        'JWT_SECRET': secrets.token_urlsafe(64),
        'JWT_SECRET_KEY': secrets.token_urlsafe(64),
        'SESSION_SECRET': secrets.token_urlsafe(64),
        'ENCRYPTION_KEY': secrets.token_urlsafe(64),
        'INSTAGRAM_WEBHOOK_VERIFY_TOKEN': secrets.token_urlsafe(32),
        'WHATSAPP_VERIFY_TOKEN': secrets.token_urlsafe(32),
    }
    
    # Sauvegarder dans .env.secrets
    output_file = Path('.env.secrets')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# ========================================\n")
        f.write("# SECRETS GÉNÉRÉS AUTOMATIQUEMENT\n")
        f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# ========================================\n")
        f.write("#\n")
        f.write("# ⚠️  IMPORTANT: Ces secrets sont CRITIQUES pour la sécurité\n")
        f.write("#\n")
        f.write("# INSTRUCTIONS:\n")
        f.write("# 1. Copier ces valeurs dans votre fichier .env\n")
        f.write("# 2. NE JAMAIS commiter .env dans Git\n")
        f.write("# 3. Utiliser des secrets différents pour dev/staging/prod\n")
        f.write("# 4. Régénérer périodiquement (rotation des secrets)\n")
        f.write("#\n")
        f.write("# ========================================\n\n")
        
        for key, value in secrets_dict.items():
            f.write(f"# {key} ({len(value)} caractères)\n")
            f.write(f"{key}={value}\n\n")
        
        f.write("# ========================================\n")
        f.write("# FIN DES SECRETS GÉNÉRÉS\n")
        f.write("# ========================================\n")
    
    print("✅ Secrets générés avec succès !")
    print(f"📁 Fichier: {output_file.absolute()}")
    print(f"\n📊 Secrets générés:")
    
    for key, value in secrets_dict.items():
        print(f"  ✅ {key}: {len(value)} caractères")
    
    print(f"\n⚠️  PROCHAINES ÉTAPES:")
    print(f"  1. Ouvrir {output_file}")
    print(f"  2. Copier les valeurs dans votre .env")
    print(f"  3. Redémarrer l'application")
    print(f"  4. Supprimer {output_file} après utilisation")
    
    return secrets_dict

if __name__ == "__main__":
    print("🔐 GÉNÉRATION DE SECRETS SÉCURISÉS")
    print("="*60)
    print()
    
    try:
        secrets_dict = generate_secure_secrets()
        print(f"\n{'='*60}")
        print("✅ GÉNÉRATION COMPLÉTÉE")
        print("="*60)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import sys
        sys.exit(1)
