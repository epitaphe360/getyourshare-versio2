"""
Script simple pour nettoyer les payouts "paid" incohérents
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.supabase_client import get_supabase_client

def simple_cleanup():
    """Supprime tous les payouts 'paid' pour réinitialiser les données de test"""
    try:
        supabase = get_supabase_client()
        
        print("\n" + "="*60)
        print("🔧 NETTOYAGE SIMPLE DES PAYOUTS")
        print("="*60)
        
        # 1. Afficher l'état actuel
        print("\n📊 ÉTAT ACTUEL:")
        commissions = supabase.table('commissions').select('amount').execute()
        payouts_paid = supabase.table('payouts').select('amount').eq('status', 'paid').execute()
        
        total_commissions = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
        total_paid = sum([float(p.get('amount', 0)) for p in (payouts_paid.data or [])])
        balance = total_commissions - total_paid
        
        print(f"   Commissions totales: {total_commissions:.2f}€")
        print(f"   Payouts paid: {total_paid:.2f}€")
        print(f"   Balance: {balance:.2f}€")
        
        if balance >= 0:
            print("\n✅ Balance déjà positif! Aucun nettoyage nécessaire.")
            return
        
        print(f"\n⚠️ Balance négatif détecté: {balance:.2f}€")
        
        # 2. Demander confirmation
        nb_payouts = len(payouts_paid.data or [])
        print(f"\n❗ Cette opération va supprimer {nb_payouts} payouts 'paid'")
        confirm = input("Confirmer? (oui/non): ").strip().lower()
        
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
        
        # 3. Supprimer tous les payouts 'paid'
        print("\n🔄 Suppression en cours...")
        result = supabase.table('payouts').delete().eq('status', 'paid').execute()
        
        print(f"✅ {nb_payouts} payouts supprimés")
        
        # 4. Vérifier le nouveau balance
        print("\n📊 NOUVEAU BALANCE:")
        new_payouts = supabase.table('payouts').select('amount').eq('status', 'paid').execute()
        new_total_paid = sum([float(p.get('amount', 0)) for p in (new_payouts.data or [])])
        new_balance = total_commissions - new_total_paid
        
        print(f"   Commissions totales: {total_commissions:.2f}€")
        print(f"   Payouts paid: {new_total_paid:.2f}€")
        print(f"   Balance: {new_balance:.2f}€")
        
        if new_balance >= 0:
            print("\n✅ SUCCÈS! Balance maintenant positif")
        else:
            print("\n❌ Balance encore négatif, problème avec les commissions?")
        
        print("\n" + "="*60)
        print("✅ NETTOYAGE TERMINÉ")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_cleanup()
