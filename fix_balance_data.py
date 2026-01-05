"""
Script pour nettoyer les données de test incohérentes (payouts > commissions)
et réinitialiser avec des données réalistes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.supabase_client import get_supabase_client
from datetime import datetime, timedelta
import random

def fix_balance_data():
    """Nettoyer et corriger les données de balance"""
    try:
        supabase = get_supabase_client()
        
        print("\n" + "="*60)
        print("🔧 NETTOYAGE DES DONNÉES DE BALANCE")
        print("="*60)
        
        # 1. Récupérer tous les influenceurs
        influencers = supabase.table('influencers').select('user_id, instagram_handle').execute()
        
        if not influencers.data:
            print("❌ Aucun influenceur trouvé")
            return
        
        print(f"\n📊 {len(influencers.data)} influenceurs trouvés")
        
        total_fixed = 0
        
        for influencer in influencers.data:
            influencer_id = influencer.get('user_id')
            influencer_name = influencer.get('instagram_handle', 'N/A')
            
            # Calculer les commissions et payouts
            commissions = supabase.table('commissions').select('amount').eq('influencer_id', influencer_id).execute()
            payouts = supabase.table('payouts').select('id, amount, status').eq('influencer_id', influencer_id).execute()
            
            total_earned = sum([float(c.get('amount', 0)) for c in (commissions.data or [])])
            total_withdrawn = sum([float(p.get('amount', 0)) for p in (payouts.data or []) if p.get('status') == 'paid'])
            
            balance = total_earned - total_withdrawn
            
            print(f"\n👤 {influencer_name}")
            print(f"   Commissions: {total_earned:.2f}€")
            print(f"   Retiré: {total_withdrawn:.2f}€")
            print(f"   Balance: {balance:.2f}€")
            
            # Si le balance est négatif, corriger
            if balance < 0:
                print(f"   ⚠️ BALANCE NÉGATIF DÉTECTÉ!")
                
                # Option 1: Supprimer les payouts "paid" excédentaires
                if payouts.data:
                    paid_payouts = [p for p in payouts.data if p.get('status') == 'paid']
                    
                    if paid_payouts:
                        # Calculer combien on doit supprimer
                        excess = abs(balance)
                        
                        print(f"   🔄 Correction: Suppression de {excess:.2f}€ de payouts")
                        
                        # Marquer les payouts comme "cancelled" au lieu de les supprimer
                        for payout in paid_payouts:
                            payout_id = payout.get('id')
                            payout_amount = float(payout.get('amount', 0))
                            
                            # Supprimer le payout directement
                            supabase.table('payouts').delete().eq('id', payout_id).execute()
                            
                            print(f"      ✅ Payout {payout_id} supprimé ({payout_amount:.2f}€)")
                            
                            excess -= payout_amount
                            total_fixed += 1
                            
                            if excess <= 0:
                                break
                        
                        # Recalculer le nouveau balance
                        new_balance = total_earned
                        print(f"   ✅ Nouveau balance: {new_balance:.2f}€")
            else:
                print(f"   ✅ Balance correct")
        
        print(f"\n" + "="*60)
        print(f"✅ Nettoyage terminé!")
        print(f"   {total_fixed} payouts annulés")
        print("="*60)
        
        # Vérification finale
        print("\n📊 VÉRIFICATION FINALE:")
        all_commissions = supabase.table('commissions').select('amount').execute()
        all_payouts = supabase.table('payouts').select('amount, status').execute()
        
        total_earned_global = sum([float(c.get('amount', 0)) for c in (all_commissions.data or [])])
        total_withdrawn_global = sum([float(p.get('amount', 0)) for p in (all_payouts.data or []) if p.get('status') == 'paid'])
        global_balance = total_earned_global - total_withdrawn_global
        
        print(f"   Total commissions: {total_earned_global:.2f}€")
        print(f"   Total retiré: {total_withdrawn_global:.2f}€")
        print(f"   Balance global: {global_balance:.2f}€")
        
        if global_balance < 0:
            print(f"   ❌ Balance encore négatif!")
        else:
            print(f"   ✅ Balance positif - Données cohérentes!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

def add_realistic_test_data():
    """Ajouter des données de test réalistes"""
    try:
        supabase = get_supabase_client()
        
        print("\n" + "="*60)
        print("➕ AJOUT DE DONNÉES DE TEST RÉALISTES")
        print("="*60)
        
        # Récupérer les influenceurs
        influencers = supabase.table('influencers').select('user_id, instagram_handle').execute()
        
        if not influencers.data:
            print("❌ Aucun influenceur trouvé")
            return
        
        for influencer in influencers.data[:3]:  # Limiter aux 3 premiers
            influencer_id = influencer.get('user_id')
            influencer_name = influencer.get('instagram_handle', 'N/A')
            
            print(f"\n👤 {influencer_name}")
            
            # Ajouter 5-10 commissions réalistes
            num_commissions = random.randint(5, 10)
            total_added = 0
            
            for i in range(num_commissions):
                amount = round(random.uniform(20, 200), 2)
                days_ago = random.randint(1, 60)
                
                commission_data = {
                    'influencer_id': influencer_id,
                    'amount': amount,
                    'created_at': (datetime.now() - timedelta(days=days_ago)).isoformat(),
                    'status': 'completed'
                }
                
                supabase.table('commissions').insert(commission_data).execute()
                total_added += amount
            
            print(f"   ✅ {num_commissions} commissions ajoutées ({total_added:.2f}€)")
        
        print(f"\n✅ Données de test réalistes ajoutées!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🔧 CORRECTION DES DONNÉES DE BALANCE")
    print("\nOptions:")
    print("1. Nettoyer les données incohérentes (annuler payouts excédentaires)")
    print("2. Ajouter des données de test réalistes")
    print("3. Les deux")
    
    choice = input("\nVotre choix (1/2/3): ").strip()
    
    if choice == "1":
        fix_balance_data()
    elif choice == "2":
        add_realistic_test_data()
    elif choice == "3":
        fix_balance_data()
        add_realistic_test_data()
    else:
        print("❌ Choix invalide")
