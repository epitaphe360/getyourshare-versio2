"""
Script pour créer des demandes d'inscription d'annonceurs en attente (pending)
"""

import os
import sys
from datetime import datetime, timedelta
from utils.logger import logger

# Importer le client Supabase du module existant
from supabase_client import supabase

def hash_password(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Données des demandes d'inscription en attente
pending_advertisers = [
    {
        "username": "fashionboutique",
        "email": "hello@fashionboutique.com",
        "password": "Test123!",
        "company_name": "Fashion Boutique",
        "country": "FR",
        "phone": "+33 1 23 45 67 89",
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
    },
    {
        "username": "techsolutions",
        "email": "info@techsolutions.com",
        "password": "Test123!",
        "company_name": "Tech Solutions",
        "country": "US",
        "phone": "+1 555 123 4567",
        "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
    },
    {
        "username": "beautystore",
        "email": "contact@beautystore.ma",
        "password": "Test123!",
        "company_name": "Beauty Store Maroc",
        "country": "MA",
        "phone": "+212 6 78 90 12 34",
        "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat()
    },
    {
        "username": "sportsgear",
        "email": "sales@sportsgear.com",
        "password": "Test123!",
        "company_name": "Sports Gear Pro",
        "country": "BE",
        "phone": "+32 2 345 67 89",
        "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat()
    },
    {
        "username": "homelectric",
        "email": "info@homelectric.ch",
        "password": "Test123!",
        "company_name": "Hom Electric Suisse",
        "country": "CH",
        "phone": "+41 22 123 45 67",
        "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()
    }
]

def create_pending_advertiser(advertiser_data):
    """Créer un annonceur avec statut pending"""
    try:
        # Vérifier si l'email existe déjà
        existing = supabase.from_("users").select("id").eq("email", advertiser_data["email"]).execute()
        if existing.data:
            logger.info(f"⚠️  {advertiser_data['email']} existe déjà - ignoré")
            return None
        
        # Hasher le mot de passe
        password_hash = hash_password(advertiser_data["password"])
        
        # Préparer les données
        user_data = {
            "username": advertiser_data["username"],
            "email": advertiser_data["email"],
            "password_hash": password_hash,
            "role": "merchant",
            "status": "pending",  # IMPORTANT: statut en attente
            "company_name": advertiser_data["company_name"],
            "country": advertiser_data["country"],
            "phone": advertiser_data.get("phone"),
            "subscription_plan": "free",  # Plan free par défaut pour les nouvelles inscriptions
            "balance": 0,
            "total_spent": 0,
            "campaigns_count": 0,
            "created_at": advertiser_data.get("created_at", datetime.utcnow().isoformat())
        }
        
        # Insérer dans la base de données
        result = supabase.from_("users").insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            logger.info(f"✅ Demande créée: {user['company_name']} ({user['email']}) - Status: {user['status']}")
            return user
        else:
            logger.info(f"❌ Erreur lors de la création de {advertiser_data['email']}")
            return None
            
    except Exception as e:
        logger.info(f"❌ Erreur pour {advertiser_data['email']}: {str(e)}")
        return None

def main():
    logger.info("\n" + "="*60)
    logger.info("🔄 CRÉATION DES DEMANDES D'INSCRIPTION EN ATTENTE")
    logger.info("="*60 + "\n")
    
    created_count = 0
    
    for advertiser in pending_advertisers:
        result = create_pending_advertiser(advertiser)
        if result:
            created_count += 1
    
    logger.info("\n" + "="*60)
    logger.info(f"✨ RÉSULTAT: {created_count}/{len(pending_advertisers)} demandes créées")
    logger.info("="*60)
    
    # Afficher le résumé
    logger.info("\n📋 RÉSUMÉ DES DEMANDES EN ATTENTE:\n")
    
    # Récupérer toutes les demandes pending
    pending_result = supabase.from_("users").select("*").eq("role", "merchant").eq("status", "pending").execute()
    
    if pending_result.data:
        logger.info(f"Total de demandes en attente: {len(pending_result.data)}\n")
        for user in pending_result.data:
            logger.info(f"  • {user['company_name']}")
            logger.info(f"    Email: {user['email']}")
            logger.info(f"    Pays: {user.get('country', 'N/A')}")
            logger.info(f"    Date: {user.get('created_at', 'N/A')[:10]}")
            logger.info(f"    ID: {user['id']}")
            print()
    else:
        logger.info("Aucune demande en attente trouvée.")
    
    logger.info("\n💡 INSTRUCTIONS:")
    logger.info("   1. Allez sur la page 'Demandes d'Inscription - Annonceurs'")
    logger.info("   2. Vous devriez voir les demandes en attente")
    logger.info("   3. Cliquez sur ✓ pour approuver ou ✗ pour rejeter")
    logger.info("   4. Le statut passera de 'pending' à 'active' ou 'rejected'")
    print()

if __name__ == "__main__":
    main()
