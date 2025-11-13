"""
Tester l'API conversations pour voir le format exact des données
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

try:
    logger.info("🔍 Test: Récupérer conversations avec format admin...\n")
    
    result = supabase.from_("conversations").select("""
        *,
        merchant:merchant_id(id, username, email, company_name),
        influencer:influencer_id(id, username, email)
    """).order("last_message_at", desc=True).limit(3).execute()
    
    if result.data:
        logger.info(f"✅ {len(result.data)} conversations récupérées\n")
        
        for i, conv in enumerate(result.data, 1):
            logger.info(f"{'='*60}")
            logger.info(f"Conversation {i} - ID: {conv.get('id')}")
            logger.info(f"{'='*60}")
            
            merchant = conv.get('merchant', {})
            influencer = conv.get('influencer', {})
            
            logger.info(f"\n📦 MERCHANT:")
            logger.info(f"   - ID: {merchant.get('id')}")
            logger.info(f"   - Username: {merchant.get('username')}")
            logger.info(f"   - Company: {merchant.get('company_name')}")
            logger.info(f"   - Email: {merchant.get('email')}")
            
            logger.info(f"\n👤 INFLUENCER:")
            logger.info(f"   - ID: {influencer.get('id')}")
            logger.info(f"   - Username: {influencer.get('username')}")
            logger.info(f"   - Email: {influencer.get('email')}")
            
            logger.info(f"\n💬 MESSAGE:")
            logger.info(f"   - Dernier: {conv.get('last_message')[:60]}...")
            logger.info(f"   - Date: {conv.get('last_message_at')}")
            logger.info(f"   - Non lus (merchant): {conv.get('unread_count_merchant')}")
            logger.info(f"   - Non lus (influencer): {conv.get('unread_count_influencer')}")
            print()
    else:
        logger.info("⚠️ Aucune conversation trouvée")
    
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    import traceback
from utils.logger import logger
    traceback.print_exc()
