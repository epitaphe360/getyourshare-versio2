"""
Script pour vérifier les données de balance (commissions et payouts)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.supabase_client import get_supabase_client

def check_balance_data():
    """Vérifier les données de commissions et payouts"""
    try:
        supabase = get_supabase_client()
        
        print("\n=== VÉRIFICATION DES COMMISSIONS ===")
        commissions = supabase.table('commissions').select('*').limit(10).execute()
        
        if commissions.data:
            print(f"\nNombre de commissions trouvées: {len(commissions.data)}")
            total_commissions = sum([float(c.get('amount', 0)) for c in commissions.data])
            print(f"Total commissions (10 premières): {total_commissions:.2f} €")
            
            print("\nDétail des 5 premières commissions:")
            for i, comm in enumerate(commissions.data[:5], 1):
                print(f"{i}. Amount: {comm.get('amount')} €, Influencer ID: {comm.get('influencer_id')}, Date: {comm.get('created_at')}")
        else:
            print("❌ Aucune commission trouvée dans la base de données")
        
        print("\n=== VÉRIFICATION DES PAYOUTS ===")
        payouts = supabase.table('payouts').select('*').limit(10).execute()
        
        if payouts.data:
            print(f"\nNombre de payouts trouvés: {len(payouts.data)}")
            total_paid = sum([float(p.get('amount', 0)) for p in payouts.data if p.get('status') == 'paid'])
            total_pending = sum([float(p.get('amount', 0)) for p in payouts.data if p.get('status') == 'pending'])
            
            print(f"Total payé: {total_paid:.2f} €")
            print(f"Total en attente: {total_pending:.2f} €")
            
            print("\nDétail des 5 premiers payouts:")
            for i, payout in enumerate(payouts.data[:5], 1):
                print(f"{i}. Amount: {payout.get('amount')} €, Status: {payout.get('status')}, Influencer ID: {payout.get('influencer_id')}, Date: {payout.get('created_at')}")
        else:
            print("❌ Aucun payout trouvé dans la base de données")
        
        # Calculer le balance global
        all_commissions = supabase.table('commissions').select('amount').execute()
        all_payouts = supabase.table('payouts').select('amount, status').execute()
        
        total_earnings = sum([float(c.get('amount', 0)) for c in (all_commissions.data or [])])
        total_withdrawn = sum([float(p.get('amount', 0)) for p in (all_payouts.data or []) if p.get('status') == 'paid'])
        
        balance = total_earnings - total_withdrawn
        
        print(f"\n=== CALCUL DU BALANCE GLOBAL ===")
        print(f"Total commissions: {total_earnings:.2f} €")
        print(f"Total retiré (paid): {total_withdrawn:.2f} €")
        print(f"Balance calculé: {balance:.2f} €")
        
        if balance < 0:
            print(f"\n⚠️ ALERTE: Balance négatif détecté! {balance:.2f} €")
            print("Les retraits (payouts 'paid') dépassent les commissions gagnées.")
        
        # Chercher des montants négatifs dans les commissions
        print("\n=== VÉRIFICATION DES MONTANTS NÉGATIFS ===")
        negative_commissions = supabase.table('commissions').select('*').lt('amount', 0).execute()
        if negative_commissions.data:
            print(f"❌ {len(negative_commissions.data)} commissions avec montant négatif trouvées:")
            for comm in negative_commissions.data[:5]:
                print(f"   - ID: {comm.get('id')}, Amount: {comm.get('amount')} €, Influencer: {comm.get('influencer_id')}")
        else:
            print("✅ Aucune commission négative trouvée")
        
        negative_payouts = supabase.table('payouts').select('*').lt('amount', 0).execute()
        if negative_payouts.data:
            print(f"❌ {len(negative_payouts.data)} payouts avec montant négatif trouvés:")
            for payout in negative_payouts.data[:5]:
                print(f"   - ID: {payout.get('id')}, Amount: {payout.get('amount')} €, Status: {payout.get('status')}")
        else:
            print("✅ Aucun payout négatif trouvé")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_balance_data()
