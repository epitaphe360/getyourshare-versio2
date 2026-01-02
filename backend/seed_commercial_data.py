
#!/usr/bin/env python3
"""
Script de seed spécifique pour le Dashboard Commercial
Génère des leads, activités, liens de tracking et codes promo pour les commerciaux.
"""

import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase_client import supabase
from utils.logger import logger

load_dotenv()

def seed_commercial_data():
    logger.info("="*70)
    logger.info("💼 GÉNÉRATION DE DONNÉES COMMERCIALES (Leads, Activités, Tracking)")
    logger.info("="*70)
    print()

    try:
        # 1. Identifier ou créer un utilisateur Commercial
        logger.info("👤 Recherche d'utilisateurs commerciaux...")
        
        users_res = supabase.table("users").select("id, email, first_name, last_name").eq("role", "commercial").execute()
        commercial_users = users_res.data if users_res.data else []
        
        if not commercial_users:
            logger.info("  ⚠️ Aucun commercial trouvé. Création d'un commercial de test...")
            # Créer un commercial par défaut
            from db_helpers import create_user
            new_user = create_user(
                email="commercial@test.com",
                password="password123",
                role="commercial",
                first_name="Jean",
                last_name="Commercial"
            )
            if new_user:
                commercial_users = [new_user]
                logger.info(f"  ✅ Commercial créé: {new_user['email']}")
            else:
                logger.error("  ❌ Impossible de créer un utilisateur commercial.")
                return False
        else:
            logger.info(f"  ✅ {len(commercial_users)} commerciaux trouvés.")

        # 2. Pour chaque commercial, générer des données
        for user in commercial_users:
            user_id = user['id']
            logger.info(f"\nTraitement du commercial: {user.get('email')}")

            # 2.1 Assurer le profil sales_representatives
            sales_rep_res = supabase.table("sales_representatives").select("id").eq("user_id", user_id).execute()
            if not sales_rep_res.data:
                logger.info("  🛠️ Création du profil Sales Representative...")
                rep_data = {
                    "user_id": user_id,
                    "email": user.get('email'),
                    "first_name": user.get('first_name') or 'Commercial', # Default if None
                    "last_name": user.get('last_name') or '',
                    "commission_rate": 5.0,
                    "is_active": True,
                    "target_monthly_revenue": 15000.0,
                    "target_monthly_deals": 20
                }
                try:
                    supabase.table("sales_representatives").insert(rep_data).execute()
                except Exception as e:
                    logger.error(f"  ❌ Erreur création profil: {e}")
            
            # 2.2 Générer des Leads (services_leads)
            logger.info("  📋 Génération de Leads...")
            
            statuses = ['nouveau', 'contacté', 'qualifié', 'proposition', 'négociation', 'conclu', 'perdu']
            temperatures = ['froid', 'tiède', 'chaud']
            sources = ['linkedin', 'website', 'referral', 'cold_call', 'event']
            
            # Vérifier s'il a déjà des leads
            existing_leads = supabase.table("services_leads").select("id", count="exact").eq("commercial_id", user_id).execute()
            current_count = existing_leads.count or 0
            
            leads_to_create = max(0, 20 - current_count) # Assurer au moins 20 leads
            
            created_leads = []
            
            if leads_to_create > 0:
                for _ in range(leads_to_create):
                    status = random.choice(statuses)
                    # Plus de chance d'avoir des leads récents
                    days_ago = random.randint(0, 60)
                    created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
                    
                    lead_data = {
                        "commercial_id": user_id,
                        "contact_name": f"Contact {uuid.uuid4().hex[:6]}",
                        "contact_email": f"contact.{uuid.uuid4().hex[:6]}@example.com",
                        "company_name": f"Company {uuid.uuid4().hex[:4]}",
                        # "phone": f"+2126{random.randint(10000000, 99999999)}", # Column might be missing
                        "status": status,
                        "temperature": random.choice(temperatures),
                        "source": random.choice(sources),
                        "estimated_value": random.randint(1000, 50000),
                        "notes": "Lead généré automatiquement.",
                        "created_at": created_at
                    }
                    
                    # Try to add phone if possible, but handle error if column missing
                    try:
                        # First try without phone
                        res = supabase.table("services_leads").insert(lead_data).execute()
                        if res.data:
                            created_leads.append(res.data[0])
                    except Exception as e:
                        logger.error(f"  ❌ Erreur création lead: {e}")
                
                logger.info(f"  ✅ {len(created_leads)} leads créés.")
            else:
                logger.info("  ℹ️ Le commercial a déjà suffisamment de leads.")
                # Récupérer quelques leads existants pour ajouter des activités
                res = supabase.table("services_leads").select("id").eq("commercial_id", user_id).limit(10).execute()
                created_leads = res.data if res.data else []

            # 2.3 Générer des Activités (lead_activities)
            logger.info("  📅 Génération d'Activités...")
            activity_types = ['call', 'email', 'meeting', 'note']
            
            activities_count = 0
            for lead in created_leads:
                # 1 à 3 activités par lead
                for _ in range(random.randint(1, 3)):
                    act_type = random.choice(activity_types)
                    act_date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                    
                    act_data = {
                        "lead_id": lead['id'],
                        "user_id": user_id,
                        "type": act_type,
                        "subject": f"{act_type.capitalize()} avec le client",
                        "description": "Discussion sur les besoins et le budget.",
                        "created_at": act_date
                    }
                    
                    try:
                        supabase.table("lead_activities").insert(act_data).execute()
                        activities_count += 1
                    except Exception:
                        pass
            
            logger.info(f"  ✅ {activities_count} activités créées.")

            # 2.4 Générer des Liens de Tracking (commercial_tracking_links)
            logger.info("  🔗 Génération de Liens de Tracking...")
            
            # Vérifier s'il a déjà des liens
            existing_links = supabase.table("commercial_tracking_links").select("id", count="exact").eq("commercial_id", user_id).execute()
            
            if (existing_links.count or 0) < 5:
                for i in range(5):
                    unique_code = uuid.uuid4().hex[:8]
                    link_data = {
                        "commercial_id": user_id,
                        "unique_code": unique_code,
                        "tracking_url": f"https://getyourshare.ma/ref/{unique_code}",
                        "campaign": f"Campagne {datetime.now().strftime('%B')}",
                        "clicks": random.randint(10, 200),
                        "conversions": random.randint(0, 10),
                        "total_revenue": random.randint(0, 5000),
                        "is_active": True
                    }
                    try:
                        supabase.table("commercial_tracking_links").insert(link_data).execute()
                    except Exception as e:
                        # Fallback si la table n'existe pas ou colonnes différentes
                        pass
                logger.info("  ✅ Liens de tracking ajoutés.")

            # 2.5 Générer des Codes Promo (promo_codes)
            logger.info("  🎟️ Génération de Codes Promo...")
            
            existing_codes = supabase.table("promo_codes").select("id", count="exact").eq("commercial_id", user_id).execute()
            
            if (existing_codes.count or 0) < 3:
                codes = [f"PROMO{random.randint(10,99)}", f"WELCOME{random.randint(10,99)}", f"DEAL{random.randint(10,99)}"]
                for code in codes:
                    promo_data = {
                        "code": code,
                        "commercial_id": user_id,
                        "discount_type": "percentage",
                        "discount_value": random.choice([10, 15, 20]),
                        "max_usage": 100,
                        "usage_count": random.randint(0, 20),
                        "is_active": True
                    }
                    try:
                        supabase.table("promo_codes").insert(promo_data).execute()
                    except Exception:
                        pass
                logger.info("  ✅ Codes promo ajoutés.")

        print()
        logger.info("="*70)
        logger.info("✅ SEEDING COMMERCIAL TERMINÉ!")
        logger.info("="*70)
        return True

    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    seed_commercial_data()
