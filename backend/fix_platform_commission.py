"""
Script pour vérifier et corriger les commissions de la plateforme dans la table sales
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def check_sales_data():
    """Vérifier l'état actuel des ventes"""
    print("=" * 80)
    print("📊 VÉRIFICATION DES DONNÉES SALES")
    print("=" * 80)
    
    # Récupérer toutes les ventes
    response = supabase.table('sales').select('*').execute()
    sales = response.data
    
    print(f"\n✅ Nombre total de ventes: {len(sales)}")
    
    # Vérifier combien ont platform_commission
    with_commission = [s for s in sales if s.get('platform_commission') and float(s.get('platform_commission', 0)) > 0]
    without_commission = [s for s in sales if not s.get('platform_commission') or float(s.get('platform_commission', 0)) == 0]
    
    print(f"✅ Ventes avec platform_commission > 0: {len(with_commission)}")
    print(f"⚠️  Ventes avec platform_commission = 0 ou NULL: {len(without_commission)}")
    
    # Vérifier les statuts
    completed = [s for s in sales if s.get('status') == 'completed']
    print(f"✅ Ventes avec statut 'completed': {len(completed)}")
    
    # Afficher quelques exemples
    if sales:
        print("\n📋 Exemples de ventes:")
        for sale in sales[:5]:
            print(f"\nID: {sale.get('id')}")
            print(f"  Amount: {sale.get('amount')} MAD")
            print(f"  Platform Commission: {sale.get('platform_commission')} MAD")
            print(f"  Influencer Commission: {sale.get('influencer_commission')} MAD")
            print(f"  Merchant Revenue: {sale.get('merchant_revenue')} MAD")
            print(f"  Status: {sale.get('status')}")
    
    return sales, without_commission

def fix_platform_commissions(sales_to_fix):
    """Corriger les commissions de plateforme"""
    print("\n" + "=" * 80)
    print("🔧 CORRECTION DES COMMISSIONS PLATEFORME")
    print("=" * 80)
    
    if not sales_to_fix:
        print("\n✅ Aucune correction nécessaire - toutes les ventes ont déjà une commission!")
        return
    
    print(f"\n⚙️  Correction de {len(sales_to_fix)} ventes...")
    
    platform_rate = 0.05  # 5% de commission plateforme
    influencer_rate = 0.10  # 10% de commission influenceur
    
    fixed_count = 0
    for sale in sales_to_fix:
        try:
            sale_id = sale['id']
            amount = float(sale.get('amount', 0))
            
            if amount == 0:
                continue
            
            # Calculer les commissions
            platform_commission = round(amount * platform_rate, 2)
            influencer_commission = round(amount * influencer_rate, 2)
            merchant_revenue = round(amount - platform_commission - influencer_commission, 2)
            
            # Mettre à jour la vente
            update_data = {
                'platform_commission': platform_commission,
                'influencer_commission': influencer_commission,
                'merchant_revenue': merchant_revenue,
                'status': 'completed'  # S'assurer que le statut est completed
            }
            
            supabase.table('sales').update(update_data).eq('id', sale_id).execute()
            
            print(f"✅ Vente {sale_id[:8]}... : {amount} MAD → Commission: {platform_commission} MAD")
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Erreur pour vente {sale_id}: {e}")
    
    print(f"\n✅ {fixed_count} ventes corrigées avec succès!")

def create_test_sales_if_empty():
    """Créer des ventes de test si la table est vide"""
    print("\n" + "=" * 80)
    print("🎲 CRÉATION DE VENTES DE TEST")
    print("=" * 80)
    
    # Récupérer un merchant et un influencer
    merchants = supabase.table('users').select('id').eq('role', 'merchant').limit(1).execute()
    influencers = supabase.table('users').select('id').eq('role', 'influencer').limit(1).execute()
    
    if not merchants.data or not influencers.data:
        print("⚠️  Pas de merchant ou influencer trouvé - impossible de créer des ventes de test")
        return
    
    merchant_id = merchants.data[0]['id']
    influencer_id = influencers.data[0]['id']
    
    # Créer 10 ventes de test
    test_sales = []
    amounts = [150, 250, 350, 450, 550, 650, 750, 850, 950, 1050]
    
    for i, amount in enumerate(amounts):
        platform_commission = round(amount * 0.05, 2)
        influencer_commission = round(amount * 0.10, 2)
        merchant_revenue = round(amount - platform_commission - influencer_commission, 2)
        
        sale_data = {
            'merchant_id': merchant_id,
            'influencer_id': influencer_id,
            'amount': amount,
            'platform_commission': platform_commission,
            'influencer_commission': influencer_commission,
            'merchant_revenue': merchant_revenue,
            'status': 'completed',
            'payment_status': 'paid'
        }
        test_sales.append(sale_data)
    
    # Insérer les ventes
    result = supabase.table('sales').insert(test_sales).execute()
    
    print(f"✅ {len(result.data)} ventes de test créées avec succès!")
    for sale in result.data:
        print(f"  - {sale['amount']} MAD → Commission: {sale['platform_commission']} MAD")

def main():
    print("\n🚀 SCRIPT DE VÉRIFICATION ET CORRECTION DES COMMISSIONS PLATEFORME\n")
    
    # 1. Vérifier les données actuelles
    sales, to_fix = check_sales_data()
    
    # 2. Si la table est vide, créer des données de test
    if not sales:
        response = input("\n❓ La table sales est vide. Créer des ventes de test? (oui/non): ")
        if response.lower() in ['oui', 'o', 'yes', 'y']:
            create_test_sales_if_empty()
            # Revérifier après création
            sales, to_fix = check_sales_data()
    
    # 3. Corriger les ventes sans commission
    if to_fix:
        response = input(f"\n❓ Corriger les {len(to_fix)} ventes sans commission? (oui/non): ")
        if response.lower() in ['oui', 'o', 'yes', 'y']:
            fix_platform_commissions(to_fix)
            # Revérifier après correction
            print("\n" + "=" * 80)
            print("📊 VÉRIFICATION FINALE")
            print("=" * 80)
            check_sales_data()
    
    print("\n✅ Script terminé!")

if __name__ == "__main__":
    main()
