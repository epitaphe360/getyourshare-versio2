import os
import json
import asyncio
from supabase_client import supabase

# --- DATA TO MIGRATE ---

# 1. Smart Match Mock Data
MOCK_INFLUENCERS = [
    {
        "user_id": "inf_1",
        "name": "Sarah Fashion",
        "niches": ["fashion", "beauty"],
        "followers_count": 50000,
        "engagement_rate": 4.5,
        "audience_age": ["young_adult", "adult"],
        "audience_gender": "female",
        "audience_location": ["MA", "FR"],
        "platforms": ["instagram", "tiktok"],
        "average_views": 15000,
        "content_quality_score": 85.0,
        "reliability_score": 92.0,
        "preferred_commission": 10.0,
        "language": ["fr", "ar"]
    },
    {
        "user_id": "inf_2",
        "name": "Tech Morocco",
        "niches": ["tech", "business"],
        "followers_count": 120000,
        "engagement_rate": 3.2,
        "audience_age": ["adult"],
        "audience_gender": "mixed",
        "audience_location": ["MA"],
        "platforms": ["youtube", "instagram"],
        "average_views": 45000,
        "content_quality_score": 90.0,
        "reliability_score": 95.0,
        "preferred_commission": 15.0,
        "language": ["fr", "ar", "en"]
    }
]

MOCK_BRANDS = [
    {
        "company_id": "brand_1",
        "company_name": "Moroccan Beauty Co",
        "product_category": "beauty",
        "target_audience_age": ["young_adult", "adult"],
        "target_audience_gender": "female",
        "target_locations": ["MA"],
        "budget_per_influencer": 3000.0,
        "commission_percentage": 12.0,
        "campaign_description": "Produits de beauté naturels marocains",
        "required_followers_min": 10000,
        "required_engagement_min": 3.0,
        "preferred_platforms": ["instagram", "tiktok"],
        "language": ["fr", "ar"]
    }
]

# 2. Gamification Mock Data (Badges & Missions)
# Note: The gamification endpoints seem to already use Supabase, but we need to ensure the tables are populated.
# The code in gamification_endpoints.py queries 'badges' and 'missions' tables.

BADGES = [
    {
        "id": "badge_first_sale",
        "name": "Première Vente",
        "description": "Réalisez votre première vente",
        "icon_url": "🎉",
        "points_reward": 100,
        "category": "sales",
        "requirements": {"sales": 1},
        "rarity": "common"
    },
    {
        "id": "badge_influencer_pro",
        "name": "Influenceur Pro",
        "description": "Atteignez 1000 clics",
        "icon_url": "🚀",
        "points_reward": 500,
        "category": "traffic",
        "requirements": {"clicks": 1000},
        "rarity": "rare"
    },
    {
        "id": "badge_super_star",
        "name": "Super Star",
        "description": "Générez 10,000 MAD de revenus",
        "icon_url": "⭐",
        "points_reward": 2000,
        "category": "revenue",
        "requirements": {"revenue": 10000},
        "rarity": "legendary"
    }
]

MISSIONS = [
    {
        "id": "mission_complete_profile",
        "title": "Compléter votre profil",
        "description": "Remplissez toutes les informations de votre profil",
        "mission_type": "onboarding",
        "criteria": {"profile_completion": 100},
        "points_reward": 50,
        "start_date": "2025-01-01T00:00:00Z",
        "is_active": True,
        "target_role": None
    },
    {
        "id": "mission_first_share",
        "title": "Premier Partage",
        "description": "Partagez votre premier lien d'affiliation",
        "mission_type": "action",
        "criteria": {"shares": 1},
        "points_reward": 20,
        "start_date": "2025-01-01T00:00:00Z",
        "is_active": True,
        "target_role": None
    },
    {
        "id": "mission_weekly_sales",
        "title": "Ventes Hebdomadaires",
        "description": "Réalisez 5 ventes cette semaine",
        "mission_type": "challenge",
        "criteria": {"sales": 5, "period": "week"},
        "points_reward": 150,
        "start_date": "2025-01-01T00:00:00Z",
        "is_active": True,
        "target_role": None
    },
    # Daily Missions (Merchant)
    {
        "id": "add_3_products",
        "title": "Ajouter 3 nouveaux produits",
        "description": "Enrichissez votre catalogue",
        "mission_type": "daily",
        "criteria": {"target": 3, "action": "add_product"},
        "points_reward": 50,
        "target_role": "merchant",
        "is_active": True
    },
    {
        "id": "make_5_sales",
        "title": "Réaliser 5 ventes",
        "description": "Objectif ventes du jour",
        "mission_type": "daily",
        "criteria": {"target": 5, "action": "sale"},
        "points_reward": 100,
        "target_role": "merchant",
        "is_active": True
    },
    # Daily Missions (Influencer)
    {
        "id": "create_content",
        "title": "Créer 1 contenu promotionnel",
        "description": "Publiez sur vos réseaux",
        "mission_type": "daily",
        "criteria": {"target": 1, "action": "create_content"},
        "points_reward": 30,
        "target_role": "influencer",
        "is_active": True
    },
    {
        "id": "generate_3_sales",
        "title": "Générer 3 ventes",
        "description": "Convertissez votre audience",
        "mission_type": "daily",
        "criteria": {"target": 3, "action": "sale"},
        "points_reward": 75,
        "target_role": "influencer",
        "is_active": True
    },
    # Daily Missions (Commercial)
    {
        "id": "make_20_calls",
        "title": "Passer 20 appels",
        "description": "Prospection active",
        "mission_type": "daily",
        "criteria": {"target": 20, "action": "call"},
        "points_reward": 40,
        "target_role": "commercial",
        "is_active": True
    },
    {
        "id": "close_2_deals",
        "title": "Fermer 2 deals",
        "description": "Objectif closing du jour",
        "mission_type": "daily",
        "criteria": {"target": 2, "action": "close_deal"},
        "points_reward": 150,
        "target_role": "commercial",
        "is_active": True
    }
]

# --- MIGRATION FUNCTIONS ---

def generate_sql_schema_part2():
    sql = """
    -- Drop existing tables to ensure schema compatibility (TEXT ids vs UUID)
    DROP TABLE IF EXISTS user_missions CASCADE;
    DROP TABLE IF EXISTS user_gamification CASCADE;
    DROP TABLE IF EXISTS missions CASCADE;
    DROP TABLE IF EXISTS badges CASCADE;
    DROP TABLE IF EXISTS smart_match_brands CASCADE;
    DROP TABLE IF EXISTS smart_match_influencers CASCADE;

    -- Smart Match Tables
    CREATE TABLE smart_match_influencers (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        niches TEXT[],
        followers_count INTEGER,
        engagement_rate FLOAT,
        audience_age TEXT[],
        audience_gender TEXT,
        audience_location TEXT[],
        platforms TEXT[],
        average_views INTEGER,
        content_quality_score FLOAT,
        reliability_score FLOAT,
        preferred_commission FLOAT,
        language TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE TABLE smart_match_brands (
        company_id TEXT PRIMARY KEY,
        company_name TEXT,
        product_category TEXT,
        target_audience_age TEXT[],
        target_audience_gender TEXT,
        target_locations TEXT[],
        budget_per_influencer FLOAT,
        commission_percentage FLOAT,
        campaign_description TEXT,
        required_followers_min INTEGER,
        required_engagement_min FLOAT,
        preferred_platforms TEXT[],
        language TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Gamification Tables
    CREATE TABLE badges (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        icon_url TEXT,
        points_reward INTEGER,
        category TEXT,
        requirements JSONB,
        rarity TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE TABLE missions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        mission_type TEXT,
        criteria JSONB,
        points_reward INTEGER,
        badge_id TEXT REFERENCES badges(id),
        start_date TIMESTAMP WITH TIME ZONE,
        end_date TIMESTAMP WITH TIME ZONE,
        is_active BOOLEAN DEFAULT TRUE,
        target_role TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE TABLE user_gamification (
        user_id UUID PRIMARY KEY REFERENCES auth.users(id),
        total_points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        achievements TEXT[],
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    CREATE TABLE user_missions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id),
        mission_id TEXT REFERENCES missions(id),
        status TEXT DEFAULT 'in_progress',
        progress INTEGER DEFAULT 0,
        points_earned INTEGER DEFAULT 0,
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    with open("MIGRATE_MOCK_DATA_PART2.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print("SQL Schema file created: MIGRATE_MOCK_DATA_PART2.sql")

async def migrate_data_part2():
    print("Migrating Part 2 data to Supabase...")
    
    # 1. Smart Match Influencers
    print(f"Migrating {len(MOCK_INFLUENCERS)} smart match influencers...")
    for inf in MOCK_INFLUENCERS:
        try:
            res = supabase.table("smart_match_influencers").select("user_id").eq("user_id", inf["user_id"]).execute()
            if not res.data:
                supabase.table("smart_match_influencers").insert(inf).execute()
                print(f"Inserted influencer: {inf['user_id']}")
            else:
                supabase.table("smart_match_influencers").update(inf).eq("user_id", inf["user_id"]).execute()
                print(f"Updated influencer: {inf['user_id']}")
        except Exception as e:
            print(f"Error migrating influencer {inf['user_id']}: {e}")

    # 2. Smart Match Brands
    print(f"Migrating {len(MOCK_BRANDS)} smart match brands...")
    for brand in MOCK_BRANDS:
        try:
            res = supabase.table("smart_match_brands").select("company_id").eq("company_id", brand["company_id"]).execute()
            if not res.data:
                supabase.table("smart_match_brands").insert(brand).execute()
                print(f"Inserted brand: {brand['company_id']}")
            else:
                supabase.table("smart_match_brands").update(brand).eq("company_id", brand["company_id"]).execute()
                print(f"Updated brand: {brand['company_id']}")
        except Exception as e:
            print(f"Error migrating brand {brand['company_id']}: {e}")

    # 3. Badges
    print(f"Migrating {len(BADGES)} badges...")
    for badge in BADGES:
        try:
            res = supabase.table("badges").select("id").eq("id", badge["id"]).execute()
            if not res.data:
                supabase.table("badges").insert(badge).execute()
                print(f"Inserted badge: {badge['id']}")
            else:
                supabase.table("badges").update(badge).eq("id", badge["id"]).execute()
                print(f"Updated badge: {badge['id']}")
        except Exception as e:
            print(f"Error migrating badge {badge['id']}: {e}")

    # 4. Missions
    print(f"Migrating {len(MISSIONS)} missions...")
    for mission in MISSIONS:
        try:
            res = supabase.table("missions").select("id").eq("id", mission["id"]).execute()
            if not res.data:
                supabase.table("missions").insert(mission).execute()
                print(f"Inserted mission: {mission['id']}")
            else:
                supabase.table("missions").update(mission).eq("id", mission["id"]).execute()
                print(f"Updated mission: {mission['id']}")
        except Exception as e:
            print(f"Error migrating mission {mission['id']}: {e}")

if __name__ == "__main__":
    generate_sql_schema_part2()
    print("\nIMPORTANT: Please run the SQL commands in 'MIGRATE_MOCK_DATA_PART2.sql' in your Supabase SQL Editor first.")
    print("Then run this script again to populate the data.")
    
    try:
        asyncio.run(migrate_data_part2())
    except Exception as e:
        print(f"\nMigration failed (probably tables don't exist yet): {e}")
