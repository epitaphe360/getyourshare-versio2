"""
Test pour vérifier les conversations
"""

from supabase_client import supabase

try:
    # Test 1: Compter les conversations
    logger.info("📊 Test 1: Vérifier les conversations...")
    result = supabase.from_("conversations").select("*", count="exact").execute()
    logger.info(f"✅ {result.count} conversations trouvées")
    
    if result.data:
        conv = result.data[0]
        logger.info(f"   Première conversation ID: {conv.get('id')}")
        logger.info(f"   Merchant ID: {conv.get('merchant_id')}")
        logger.info(f"   Influencer ID: {conv.get('influencer_id')}")
        logger.info(f"   Last message: {conv.get('last_message')}")
    
    # Test 2: Compter les messages
    logger.info("\n📊 Test 2: Vérifier les messages...")
    result = supabase.from_("messages").select("*", count="exact").execute()
    logger.info(f"✅ {result.count} messages trouvés")
    
    # Test 3: Test avec JOIN
    logger.info("\n📊 Test 3: Test avec JOIN users...")
    result = supabase.from_("conversations").select("""
        *,
        merchant:merchant_id(id, email, company_name),
        influencer:influencer_id(id, email, username)
    """).limit(3).execute()
    
    logger.info(f"✅ {len(result.data)} conversations avec détails")
    if result.data:
        for conv in result.data:
            merchant = conv.get('merchant', {})
            influencer = conv.get('influencer', {})
            logger.info(f"   - {merchant.get('company_name', 'N/A')} ↔ {influencer.get('username', 'N/A')}")
    
    logger.info("\n✨ Tous les tests réussis !")
    
except Exception as e:
    logger.info(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
