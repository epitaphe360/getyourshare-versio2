"""
Analyse complète de toutes les données dans la base de données
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

def analyze_table(table_name, columns="*", limit=5):
    """Analyse une table: compte total + échantillon"""
    try:
        # Compte total
        count_result = supabase.table(table_name).select("*", count='exact').execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
        
        # Échantillon
        sample_result = supabase.table(table_name).select(columns).limit(limit).execute()
        sample = sample_result.data
        
        return {
            'total': total,
            'sample': sample,
            'columns': list(sample[0].keys()) if sample else []
        }
    except Exception as e:
        return {
            'total': 0,
            'sample': [],
            'columns': [],
            'error': str(e)
        }

def main():
    print("=" * 80)
    print("ANALYSE COMPLÈTE DES DONNÉES - TOUS LES TABLEAUX")
    print("=" * 80)
    print()
    
    # Tables à analyser
    tables = {
        'users': 'id, email, role, username, company_name, subscription_tier, created_at',
        'campaigns': 'id, merchant_id, name, budget, status, product_type, created_at',
        'products': 'id, merchant_id, name, price, commission_rate, status, created_at',
        'commissions': 'id, influencer_id, amount, status, campaign_id, created_at',
        'payouts': 'id, influencer_id, amount, status, created_at',
        'conversations': 'id, participant_ids, last_message, last_message_at, created_at',
        'messages': 'id, conversation_id, sender_id, content, is_read, created_at',
        'leads': 'id, commercial_id, merchant_id, status, budget, created_at',
        'invoices': 'id, merchant_id, amount, status, created_at',
        'campaign_influencers': '*',
        'product_views': '*',
    }
    
    results = {}
    
    for table_name, columns in tables.items():
        print(f"\n{'='*80}")
        print(f"TABLE: {table_name.upper()}")
        print('='*80)
        
        result = analyze_table(table_name, columns)
        results[table_name] = result
        
        if 'error' in result:
            print(f"❌ ERREUR: {result['error']}")
            continue
        
        print(f"📊 Total enregistrements: {result['total']}")
        
        if result['columns']:
            print(f"📋 Colonnes: {', '.join(result['columns'])}")
        
        if result['sample']:
            print(f"\n🔍 Échantillon ({len(result['sample'])} enregistrements):")
            for i, row in enumerate(result['sample'], 1):
                print(f"\n  [{i}]")
                for key, value in row.items():
                    # Tronquer les longues valeurs
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    print(f"    {key}: {value}")
        else:
            print("⚠️  TABLE VIDE - AUCUNE DONNÉE")
    
    # Résumé global
    print("\n" + "=" * 80)
    print("RÉSUMÉ GLOBAL")
    print("=" * 80)
    
    empty_tables = [name for name, result in results.items() if result['total'] == 0]
    filled_tables = [name for name, result in results.items() if result['total'] > 0]
    
    print(f"\n✅ Tables avec données ({len(filled_tables)}):")
    for table in filled_tables:
        print(f"   - {table}: {results[table]['total']} enregistrements")
    
    if empty_tables:
        print(f"\n❌ Tables VIDES ({len(empty_tables)}):")
        for table in empty_tables:
            print(f"   - {table}")
    
    # Analyse par rôle utilisateur
    print("\n" + "=" * 80)
    print("ANALYSE PAR RÔLE UTILISATEUR")
    print("=" * 80)
    
    if results['users']['total'] > 0:
        users_by_role = supabase.table('users').select('role').execute()
        roles = {}
        for user in users_by_role.data:
            role = user.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        print("\n👥 Répartition des utilisateurs:")
        for role, count in sorted(roles.items()):
            print(f"   - {role}: {count}")
    
    # Analyse par subscription_tier
    print("\n" + "=" * 80)
    print("ANALYSE PAR TYPE ABONNEMENT (MERCHANTS)")
    print("=" * 80)
    
    if results['users']['total'] > 0:
        merchants = supabase.table('users').select('subscription_tier, role').eq('role', 'merchant').execute()
        tiers = {}
        for merchant in merchants.data:
            tier = merchant.get('subscription_tier', 'unknown')
            tiers[tier] = tiers.get(tier, 0) + 1
        
        print("\n💳 Répartition des abonnements merchants:")
        for tier, count in sorted(tiers.items()):
            print(f"   - {tier}: {count}")
    
    # Relations clés
    print("\n" + "=" * 80)
    print("ANALYSE DES RELATIONS CLÉS")
    print("=" * 80)
    
    # Campaigns par merchant
    if results['campaigns']['total'] > 0:
        campaigns = supabase.table('campaigns').select('merchant_id').execute()
        merchant_campaigns = {}
        for camp in campaigns.data:
            mid = camp.get('merchant_id', 'unknown')
            merchant_campaigns[mid] = merchant_campaigns.get(mid, 0) + 1
        
        print(f"\n📢 Campaigns par merchant:")
        print(f"   - Total merchants avec campaigns: {len(merchant_campaigns)}")
        print(f"   - Moyenne campaigns par merchant: {results['campaigns']['total'] / max(len(merchant_campaigns), 1):.1f}")
    
    # Commissions par influencer
    if results['commissions']['total'] > 0:
        commissions = supabase.table('commissions').select('influencer_id, amount').execute()
        influencer_commissions = {}
        influencer_amounts = {}
        for comm in commissions.data:
            iid = comm.get('influencer_id', 'unknown')
            influencer_commissions[iid] = influencer_commissions.get(iid, 0) + 1
            influencer_amounts[iid] = influencer_amounts.get(iid, 0) + float(comm.get('amount', 0))
        
        print(f"\n💰 Commissions par influencer:")
        print(f"   - Total influencers avec commissions: {len(influencer_commissions)}")
        print(f"   - Moyenne commissions par influencer: {results['commissions']['total'] / max(len(influencer_commissions), 1):.1f}")
        if influencer_amounts:
            print(f"   - Montant moyen par influencer: {sum(influencer_amounts.values()) / len(influencer_amounts):.2f}€")
    
    # Leads par commercial
    if results['leads']['total'] > 0:
        leads = supabase.table('leads').select('commercial_id, status').execute()
        commercial_leads = {}
        lead_status = {}
        for lead in leads.data:
            cid = lead.get('commercial_id', 'unknown')
            commercial_leads[cid] = commercial_leads.get(cid, 0) + 1
            status = lead.get('status', 'unknown')
            lead_status[status] = lead_status.get(status, 0) + 1
        
        print(f"\n🎯 Leads par commercial:")
        print(f"   - Total commerciaux avec leads: {len(commercial_leads)}")
        print(f"   - Moyenne leads par commercial: {results['leads']['total'] / max(len(commercial_leads), 1):.1f}")
        print(f"\n   Status des leads:")
        for status, count in sorted(lead_status.items()):
            print(f"     - {status}: {count}")
    
    print("\n" + "=" * 80)
    print("RECOMMANDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    if results['users']['total'] < 20:
        recommendations.append("⚠️  Trop peu d'utilisateurs - créer au moins 20 utilisateurs de test")
    
    if results['campaigns']['total'] < 10:
        recommendations.append("⚠️  Trop peu de campaigns - créer au moins 10 campaigns de test")
    
    if results['products']['total'] < 20:
        recommendations.append("⚠️  Trop peu de produits - créer au moins 20 produits de test")
    
    if results['commissions']['total'] < 30:
        recommendations.append("⚠️  Trop peu de commissions - créer au moins 30 commissions de test")
    
    if results['leads']['total'] < 15:
        recommendations.append("⚠️  Trop peu de leads - créer au moins 15 leads de test")
    
    if results['conversations']['total'] < 10:
        recommendations.append("⚠️  Trop peu de conversations - créer au moins 10 conversations de test")
    
    if empty_tables:
        recommendations.append(f"❌ {len(empty_tables)} table(s) complètement vide(s): {', '.join(empty_tables)}")
    
    if recommendations:
        print("\n📋 Actions nécessaires:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("\n✅ Base de données bien peuplée!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
