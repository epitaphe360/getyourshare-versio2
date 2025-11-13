"""
Créer la table services via Python/Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.logger import logger

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

logger.info("\n" + "="*50)
logger.info("📦 CRÉATION TABLE SERVICES")
logger.info("="*50 + "\n")

# SQL simplifié
sql = """
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price_per_lead DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    lead_requirements JSONB DEFAULT '{}',
    images JSONB DEFAULT '[]',
    videos JSONB DEFAULT '[]',
    is_available BOOLEAN DEFAULT true,
    capacity_per_month INTEGER,
    total_leads INTEGER DEFAULT 0,
    total_leads_qualified INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    slug VARCHAR(255) UNIQUE,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

try:
    result = supabase.rpc('exec_sql', {'sql': sql}).execute()
    logger.info("✅ Table services créée avec succès !")
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    logger.info("\n💡 Essai avec requête directe...")
    
    # Essayer d'insérer directement un service de test pour forcer la création
    try:
        # Récupérer un merchant
        merchant = supabase.table("users").select("id").eq("role", "merchant").limit(1).execute()
        if merchant.data:
            merchant_id = merchant.data[0]["id"]
            
            test_service = {
                "merchant_id": merchant_id,
                "name": "Consultation Marketing Test",
                "description": "Service de test",
                "category": "Marketing Digital",
                "price_per_lead": 50.00,
                "currency": "EUR"
            }
            
            result = supabase.table("services").insert(test_service).execute()
            logger.info("✅ Table services existe et fonctionne !")
            logger.info(f"   Service test créé: {result.data[0]['id']}")
    except Exception as e2:
        logger.info(f"❌ La table n'existe pas encore: {e2}")
        logger.info("\n⚠️  Veuillez exécuter le SQL directement dans Supabase SQL Editor")

logger.info("\n" + "="*50)
