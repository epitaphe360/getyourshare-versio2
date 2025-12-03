"""
Script pour injecter des données de démonstration pour les campagnes
Crée 20 campagnes avec des performances réalistes et variées
"""

import os
from datetime import datetime, timedelta
import random
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Données de référence
CAMPAIGN_TYPES = [
    "Soldes",
    "Lancement Produit",
    "Saisonnière",
    "Flash",
    "Event Spécial"
]

CATEGORIES = [
    "Mode & Fashion",
    "High-Tech",
    "Sport & Fitness",
    "Beauté & Cosmétiques",
    "Maison & Déco",
    "Alimentation & Gastronomie",
    "Voyages & Tourisme",
    "Gaming & Esport"
]

CAMPAIGN_NAMES = [
    "Black Friday 2024",
    "Cyber Monday Tech",
    "Soldes d'Hiver",
    "Lancement iPhone 15 Pro",
    "Collection Printemps",
    "Promo Noël",
    "Flash Sale Weekend",
    "Saint-Valentin Love",
    "Soldes d'Été",
    "Rentrée Scolaire",
    "Halloween Special",
    "Gaming Week",
    "Beauty Days",
    "Sport Challenge",
    "Home & Living",
    "Voyage de Rêve",
    "Fashion Week Paris",
    "Tech Innovation",
    "Wellness Month",
    "Gourmet Festival"
]

STATUSES = ["active", "scheduled", "completed", "paused"]

def get_or_create_merchant():
    """Récupère ou crée un marchand de test"""
    # Chercher un utilisateur marchand existant
    merchants = supabase.table('users').select('*').eq('role', 'merchant').limit(1).execute()
    
    if merchants.data and len(merchants.data) > 0:
        return merchants.data[0]['id']
    
    # Créer un marchand de test si aucun n'existe
    merchant_data = {
        "email": "merchant_demo@getyourshare.com",
        "role": "merchant",
        "company_name": "TechStore Pro",
        "created_at": datetime.utcnow().isoformat()
    }
    result = supabase.table('users').insert(merchant_data).execute()
    return result.data[0]['id']

def generate_campaign_data(index, merchant_id):
    """Génère les données d'une campagne de démonstration"""
    
    # Déterminer le statut et les dates en fonction
    status = random.choice(STATUSES)
    now = datetime.now()
    
    if status == "active":
        start_date = now - timedelta(days=random.randint(1, 15))
        end_date = now + timedelta(days=random.randint(3, 30))
    elif status == "scheduled":
        start_date = now + timedelta(days=random.randint(1, 10))
        end_date = start_date + timedelta(days=random.randint(7, 21))
    elif status == "completed":
        end_date = now - timedelta(days=random.randint(1, 30))
        start_date = end_date - timedelta(days=random.randint(7, 21))
    else:  # paused
        start_date = now - timedelta(days=random.randint(5, 15))
        end_date = now + timedelta(days=random.randint(7, 21))
    
    # Générer les métriques de performance
    budget = random.randint(1000, 50000)
    spent = int(budget * random.uniform(0.2, 0.95)) if status != "scheduled" else 0
    
    clicks = 0
    conversions = 0
    revenue = 0.0
    
    if status in ["active", "completed", "paused"]:
        clicks = random.randint(100, 5000)
        conversions = int(clicks * random.uniform(0.01, 0.08))  # 1-8% conversion
        avg_order = random.uniform(50, 500)
        revenue = conversions * avg_order
    
    commission_rate = random.choice([10, 15, 20, 25, 30, 35])
    category = random.choice(CATEGORIES)
    campaign_type = random.choice(CAMPAIGN_TYPES)
    
    # Nombre d'influenceurs participants
    num_influencers = random.randint(5, 100) if status != "scheduled" else 0
    
    # ROI calculation
    roi = 0
    if spent > 0 and revenue > 0:
        roi = ((revenue - spent) / spent) * 100
    
    # Créer la description avec toutes les métadonnées
    description_meta = {
        "type": campaign_type,
        "category": category,
        "commission_rate": commission_rate,
        "products_count": random.randint(5, 50),
        "performance": {
            "clicks": clicks,
            "conversions": conversions,
            "revenue": round(revenue, 2),
            "spent": spent,
            "roi": round(roi, 1),
            "participants": num_influencers,
            "impressions": clicks * random.randint(3, 8),
            "engagement_rate": round(random.uniform(2.5, 8.5), 2)
        }
    }
    
    campaign = {
        "name": CAMPAIGN_NAMES[index % len(CAMPAIGN_NAMES)] + f" #{index+1}",
        "description": f"Campagne {campaign_type} dans la catégorie {category}. " + 
                      f"Commission: {commission_rate}%. Participants: {num_influencers} influenceurs.",
        "merchant_id": merchant_id,
        "status": status,
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "budget": float(budget),
        "created_at": (now - timedelta(days=random.randint(15, 60))).isoformat(),
        "updated_at": now.isoformat(),
        "target_audience": {
            "age_range": f"{random.choice(['18-24', '25-34', '35-44', '45-54'])}",
            "gender": random.choice(["all", "female", "male"]),
            "interests": [category, "Shopping", "Lifestyle"],
            "metadata": description_meta
        }
    }
    
    return campaign

def seed_campaigns():
    """Injecte les campagnes de démonstration"""
    print("🚀 Démarrage de l'injection des campagnes de démonstration...")
    
    # Récupérer ou créer un marchand
    merchant_id = get_or_create_merchant()
    print(f"✅ Marchand ID: {merchant_id}")
    
    # Supprimer les anciennes campagnes de démo (optionnel)
    print("🗑️  Suppression des anciennes campagnes de démo...")
    try:
        # Supprimer uniquement celles créées par script (avec pattern #)
        existing = supabase.table('campaigns').select('id, name').execute()
        for camp in existing.data:
            if '#' in camp['name'] or 'demo' in camp['name'].lower():
                supabase.table('campaigns').delete().eq('id', camp['id']).execute()
    except Exception as e:
        print(f"⚠️  Avertissement lors de la suppression: {e}")
    
    # Créer 20 campagnes
    print("📝 Création de 20 nouvelles campagnes...")
    campaigns_created = 0
    
    for i in range(20):
        try:
            campaign_data = generate_campaign_data(i, merchant_id)
            result = supabase.table('campaigns').insert(campaign_data).execute()
            
            if result.data:
                campaigns_created += 1
                status_emoji = {
                    'active': '🟢',
                    'scheduled': '🟡',
                    'completed': '🔴',
                    'paused': '⏸️'
                }
                emoji = status_emoji.get(campaign_data['status'], '⚪')
                print(f"  {emoji} {campaign_data['name']} - {campaign_data['campaign_type']} - {campaign_data['status']}")
        except Exception as e:
            print(f"  ❌ Erreur pour la campagne {i+1}: {e}")
    
    print(f"\n✨ Injection terminée! {campaigns_created}/20 campagnes créées avec succès")
    
    # Afficher des statistiques
    print("\n📊 Statistiques:")
    all_campaigns = supabase.table('campaigns').select('status, target_audience').execute()
    
    status_count = {}
    type_count = {}
    total_revenue = 0
    
    for camp in all_campaigns.data:
        # Compter par statut
        status = camp.get('status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
        
        # Compter par type depuis target_audience.metadata
        target_aud = camp.get('target_audience', {})
        if isinstance(target_aud, dict):
            metadata = target_aud.get('metadata', {})
            camp_type = metadata.get('type', 'unknown')
            type_count[camp_type] = type_count.get(camp_type, 0) + 1
            
            # Revenue total depuis metadata.performance
            perf = metadata.get('performance', {})
            total_revenue += float(perf.get('revenue', 0) or 0)
    
    print("\n  Par statut:")
    for status, count in status_count.items():
        emoji = {'active': '🟢', 'scheduled': '🟡', 'completed': '🔴', 'paused': '⏸️', 'draft': '⚪'}.get(status, '⚪')
        print(f"    {emoji} {status}: {count}")
    
    print("\n  Par type:")
    for camp_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
        if camp_type != 'unknown':
            print(f"    • {camp_type}: {count}")
    
    print(f"\n  💰 CA Total Généré: {total_revenue:,.2f} €")
    print("\n🎉 Base de données prête pour la démonstration!")

if __name__ == "__main__":
    seed_campaigns()
