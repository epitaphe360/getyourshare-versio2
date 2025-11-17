"""
Test simple des conversations dans Supabase
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service role pour bypass RLS

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    logger.info("🔍 Test 1: Compter les conversations...")
    result = supabase.from_("conversations").select("*", count="exact").execute()
    logger.info(f"✅ {result.count} conversations trouvées\n")
    
    logger.info("🔍 Test 2: Compter les messages...")
    result = supabase.from_("messages").select("*", count="exact").execute()
    logger.info(f"✅ {result.count} messages trouvés\n")
    
    logger.info("🔍 Test 3: Détails des conversations...")
    result = supabase.from_("conversations").select("""
        *,
        merchant:merchant_id(id, email, company_name),
        influencer:influencer_id(id, email, username)
    """).limit(5).execute()
    
    if result.data:
        for i, conv in enumerate(result.data, 1):
            merchant = conv.get('merchant', {})
            influencer = conv.get('influencer', {})
            logger.info(f"Conversation {i}:")
            logger.info(f"  Marchand: {merchant.get('company_name', 'N/A')}")
            logger.info(f"  Influenceur: {influencer.get('username', 'N/A')}")
            logger.info(f"  Dernier message: {conv.get('last_message', '')[:60]}...")
            logger.info(f"  Non lus (marchand): {conv.get('unread_count_merchant')}")
            logger.info(f"  Non lus (influenceur): {conv.get('unread_count_influencer')}")
            print()
    else:
        logger.info("⚠️ Aucune conversation avec détails\n")
    
    logger.info("✅ Tests terminés!")
    
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
