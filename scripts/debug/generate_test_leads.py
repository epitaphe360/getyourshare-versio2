"""
Script pour générer des données de test pour le système de LEADS
Crée des leads de démonstration dans la base de données
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Ajouter le dossier backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv('backend/.env')

from utils.supabase_client import get_supabase_client

def generate_test_leads():
    """Génère des leads de test"""
    try:
        supabase = get_supabase_client()
        print("✅ Client Supabase initialisé")
        
        # 1. Récupérer un merchant existant
        print("\n🔍 Recherche d'un merchant...")
        merchants_response = supabase.table('merchants').select('id, company_name, user_id').limit(1).execute()
        if not merchants_response.data:
            print("❌ Aucun merchant trouvé. Créez d'abord un merchant.")
            return
        merchant = merchants_response.data[0]
        print(f"✅ Merchant trouvé: {merchant['company_name']} (ID: {merchant['id']})")
        
        # 2. Récupérer une campagne existante
        print("\n🔍 Recherche d'une campagne...")
        campaigns_response = supabase.table('campaigns').select('id, name').eq('merchant_id', merchant['id']).limit(1).execute()
        if not campaigns_response.data:
            print("⚠️ Aucune campagne trouvée pour ce merchant. Création d'une campagne de test...")
            # Créer une campagne de test
            campaign_data = {
                'name': 'Campagne Test Leads',
                'description': 'Campagne de test pour la génération de leads',
                'merchant_id': merchant['id'],
                'status': 'active',
                'type': 'service_leads',
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).isoformat()
            }
            campaign_response = supabase.table('campaigns').insert(campaign_data).execute()
            campaign = campaign_response.data[0]
            print(f"✅ Campagne créée: {campaign['name']} (ID: {campaign['id']})")
        else:
            campaign = campaigns_response.data[0]
            print(f"✅ Campagne trouvée: {campaign['name']} (ID: {campaign['id']})")
        
        # 3. Récupérer un influenceur existant
        print("\n🔍 Recherche d'un influenceur...")
        influencers_response = supabase.table('influencers').select('id, full_name').limit(1).execute()
        influencer = None
        if influencers_response.data:
            influencer = influencers_response.data[0]
            print(f"✅ Influenceur trouvé: {influencer['full_name']} (ID: {influencer['id']})")
        else:
            print("⚠️ Aucun influenceur trouvé (optionnel)")
        
        # 4. Vérifier si la table 'leads' existe
        print("\n🔍 Vérification de la table 'leads'...")
        try:
            test_query = supabase.table('leads').select('id').limit(1).execute()
            print("✅ Table 'leads' existe")
        except Exception as e:
            print(f"❌ Table 'leads' n'existe pas: {e}")
            print("📝 Exécutez d'abord le fichier SQL: database/migrations/leads_system.sql")
            return
        
        # 5. Générer les leads de test
        print("\n📝 Génération de 10 leads de test...")
        
        statuses = ['pending', 'validated', 'rejected', 'converted']
        sources = ['instagram', 'tiktok', 'whatsapp', 'direct']
        
        leads_created = 0
        
        for i in range(10):
            # Valeur estimée aléatoire entre 300 et 2000 dhs
            estimated_value = round(random.uniform(300, 2000), 2)
            
            # Calculer la commission (10% si < 800 dhs, sinon 80 dhs fixe)
            if estimated_value < 800:
                commission_amount = round(estimated_value * 0.10, 2)
                commission_type = 'percentage'
            else:
                commission_amount = 80.00
                commission_type = 'fixed'
            
            # Commission influenceur (30% de la commission totale)
            influencer_commission = round(commission_amount * 0.30, 2) if influencer else 0
            
            lead_data = {
                'campaign_id': campaign['id'],
                'merchant_id': merchant['id'],
                'influencer_id': influencer['id'] if influencer else None,
                'customer_name': f'Client Test {i+1}',
                'customer_email': f'client.test{i+1}@example.com',
                'customer_phone': f'+212 6{random.randint(10000000, 99999999)}',
                'customer_company': f'Entreprise {i+1}' if random.choice([True, False]) else None,
                'customer_notes': f'Lead généré automatiquement pour test #{i+1}',
                'source': random.choice(sources),
                'estimated_value': estimated_value,
                'commission_amount': commission_amount,
                'commission_type': commission_type,
                'influencer_percentage': 30.00 if influencer else None,
                'influencer_commission': influencer_commission if influencer else None,
                'status': random.choice(statuses),
                'quality_score': random.randint(6, 10),
                'created_at': (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat()
            }
            
            try:
                result = supabase.table('leads').insert(lead_data).execute()
                if result.data:
                    leads_created += 1
                    status_emoji = {
                        'pending': '🟡',
                        'validated': '🟢',
                        'rejected': '🔴',
                        'converted': '💰'
                    }
                    emoji = status_emoji.get(lead_data['status'], '⚪')
                    print(f"  {emoji} Lead {i+1}: {lead_data['customer_name']} - {estimated_value} dhs - {lead_data['status']}")
            except Exception as e:
                print(f"  ❌ Erreur création lead {i+1}: {e}")
        
        print(f"\n✅ {leads_created}/10 leads créés avec succès!")
        
        # 6. Afficher un résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DES LEADS CRÉÉS")
        print("="*60)
        
        all_leads = supabase.table('leads').select('*').eq('merchant_id', merchant['id']).execute()
        total = len(all_leads.data) if all_leads.data else 0
        
        stats = {
            'pending': 0,
            'validated': 0,
            'rejected': 0,
            'converted': 0
        }
        total_value = 0
        total_commission = 0
        
        for lead in (all_leads.data or []):
            stats[lead['status']] = stats.get(lead['status'], 0) + 1
            total_value += float(lead['estimated_value'])
            total_commission += float(lead['commission_amount'])
        
        print(f"Total leads: {total}")
        print(f"  🟡 En attente: {stats['pending']}")
        print(f"  🟢 Validés: {stats['validated']}")
        print(f"  🔴 Rejetés: {stats['rejected']}")
        print(f"  💰 Convertis: {stats['converted']}")
        print(f"\n💵 Valeur totale estimée: {total_value:.2f} dhs")
        print(f"💸 Commissions totales: {total_commission:.2f} dhs")
        print("\n✅ Données de test générées! Actualisez la page Leads dans l'application.")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("🚀 GÉNÉRATION DE DONNÉES DE TEST - SYSTÈME LEADS")
    print("="*60)
    generate_test_leads()
