import os
import json
import asyncio
from supabase_client import supabase

# --- DATA TO MIGRATE ---

TEMPLATES = [
    {
        "id": "insta_product_1",
        "name": "Product Spotlight",
        "category": "product_showcase",
        "content_type": "post",
        "platforms": ["instagram", "facebook"],
        "thumbnail": "/assets/templates/insta_product_1.jpg",
        "description": "Mise en avant produit avec fond coloré et texte accrocheur",
        "dimensions": {"width": 1080, "height": 1080},
        "elements": [
            {"type": "background", "color": "#FF6B9D", "gradient": True},
            {"type": "image", "placeholder": "product_image", "size": 0.6},
            {"type": "text", "content": "{{product_name}}", "font": "bold", "size": 48},
            {"type": "text", "content": "{{commission}}% Commission", "font": "regular", "size": 32},
            {"type": "badge", "content": "NOUVEAU", "position": "top-right"}
        ]
    },
    {
        "id": "insta_story_promo_1",
        "name": "Story Promo Flash",
        "category": "promotion",
        "content_type": "story",
        "platforms": ["instagram"],
        "thumbnail": "/assets/templates/insta_story_promo_1.jpg",
        "description": "Story avec countdown et prix barré",
        "dimensions": {"width": 1080, "height": 1920},
        "elements": [
            {"type": "background", "image": "gradient_vertical"},
            {"type": "image", "placeholder": "product_image", "size": 0.5, "position": "center"},
            {"type": "text", "content": "PROMO FLASH", "font": "bold", "size": 64, "color": "#FF0000"},
            {"type": "price", "old_price": "{{old_price}}", "new_price": "{{price}}", "size": 48},
            {"type": "countdown", "duration": 24, "position": "bottom"},
            {"type": "cta", "content": "SWIPE UP", "position": "bottom"}
        ]
    },
    {
        "id": "tiktok_review_1",
        "name": "TikTok Review Template",
        "category": "review",
        "content_type": "video",
        "platforms": ["tiktok", "instagram"],
        "thumbnail": "/assets/templates/tiktok_review_1.jpg",
        "description": "Template vidéo review avec rating et points clés",
        "dimensions": {"width": 1080, "height": 1920},
        "elements": [
            {"type": "overlay", "position": "top", "content": "{{product_name}}"},
            {"type": "rating", "stars": "{{rating}}", "position": "top-center"},
            {"type": "text_list", "items": ["{{point_1}}", "{{point_2}}", "{{point_3}}"]},
            {"type": "watermark", "content": "@{{username}}", "position": "bottom-left"}
        ]
    },
    {
        "id": "carousel_tutorial_1",
        "name": "Tutorial Step-by-Step",
        "category": "tutorial",
        "content_type": "carousel",
        "platforms": ["instagram", "linkedin"],
        "thumbnail": "/assets/templates/carousel_tutorial_1.jpg",
        "description": "Carousel explicatif avec numérotation",
        "dimensions": {"width": 1080, "height": 1080, "slides": 5},
        "elements": [
            {"type": "background", "color": "#FFFFFF"},
            {"type": "number", "position": "top-left", "size": 72, "color": "#FF6B9D"},
            {"type": "title", "content": "{{step_title}}", "font": "bold", "size": 42},
            {"type": "image", "placeholder": "step_image", "size": 0.5},
            {"type": "description", "content": "{{step_description}}", "font": "regular", "size": 24}
        ]
    },
    {
        "id": "quote_testimonial_1",
        "name": "Customer Testimonial",
        "category": "testimonial",
        "content_type": "post",
        "platforms": ["instagram", "facebook", "linkedin"],
        "thumbnail": "/assets/templates/quote_testimonial_1.jpg",
        "description": "Témoignage client avec photo et citation",
        "dimensions": {"width": 1080, "height": 1080},
        "elements": [
            {"type": "background", "color": "#F5F5F5"},
            {"type": "quote_icon", "position": "top-left", "size": 64},
            {"type": "text", "content": "{{testimonial}}", "font": "italic", "size": 32, "align": "center"},
            {"type": "avatar", "image": "{{customer_avatar}}", "size": 120, "position": "bottom-center"},
            {"type": "name", "content": "{{customer_name}}", "font": "bold", "size": 24},
            {"type": "rating", "stars": "{{rating}}", "position": "bottom"}
        ]
    },
    {
        "id": "announcement_1",
        "name": "Big Announcement",
        "category": "announcement",
        "content_type": "post",
        "platforms": ["instagram", "facebook", "twitter"],
        "thumbnail": "/assets/templates/announcement_1.jpg",
        "description": "Annonce avec fond dynamique",
        "dimensions": {"width": 1080, "height": 1080},
        "elements": [
            {"type": "background", "pattern": "confetti", "colors": ["#FF6B9D", "#4ECDC4", "#FFE66D"]},
            {"type": "text", "content": "🎉 ANNONCE 🎉", "font": "bold", "size": 56, "position": "top"},
            {"type": "text", "content": "{{announcement_text}}", "font": "regular", "size": 36, "align": "center"},
            {"type": "cta", "content": "EN SAVOIR PLUS", "position": "bottom"}
        ]
    },
    {
        "id": "quote_minimal_1",
        "name": "Minimalist Quote",
        "category": "quote",
        "content_type": "post",
        "platforms": ["instagram", "twitter", "linkedin"],
        "thumbnail": "/assets/templates/quote_minimal_1.jpg",
        "description": "Citation minimaliste élégante",
        "dimensions": {"width": 1080, "height": 1080},
        "elements": [
            {"type": "background", "color": "#FFFFFF"},
            {"type": "text", "content": "{{quote}}", "font": "serif", "size": 38, "align": "center", "color": "#333333"},
            {"type": "divider", "style": "line", "width": 200, "color": "#FF6B9D"},
            {"type": "author", "content": "— {{author}}", "font": "italic", "size": 24, "color": "#666666"}
        ]
    }
]

ACHIEVEMENTS = [
    {
        "id": "first_sale",
        "title": "🎉 Première Vente",
        "description": "Réalisez votre première conversion",
        "icon": "🎉",
        "rarity": "common",
        "condition_type": "conversions",
        "condition_value": 1
    },
    {
        "id": "century_club",
        "title": "💯 Century Club",
        "description": "Atteignez 100 conversions",
        "icon": "💯",
        "rarity": "rare",
        "condition_type": "conversions",
        "condition_value": 100
    },
    {
        "id": "millionaire",
        "title": "💰 Millionnaire",
        "description": "Générez 1,000,000 MAD de revenus",
        "icon": "💰",
        "rarity": "legendary",
        "condition_type": "revenue",
        "condition_value": 1000000
    },
    {
        "id": "campaign_master",
        "title": "🎯 Campaign Master",
        "description": "Complétez 50 campagnes",
        "icon": "🎯",
        "rarity": "epic",
        "condition_type": "campaigns",
        "condition_value": 50
    }
]

BENCHMARKS = [
    {"metric": "avg_conversion_rate", "value": 2.5},
    {"metric": "avg_monthly_revenue", "value": 1500},
    {"metric": "avg_campaigns_per_month", "value": 5}
]

# --- MIGRATION FUNCTIONS ---

def create_tables():
    print("Creating tables...")
    
    # 1. Content Templates
    # Note: Supabase Python client doesn't support CREATE TABLE directly via RPC usually, 
    # but we can use the SQL editor or a stored procedure. 
    # However, for this task, I'll assume we can run SQL via a helper or just try to insert and fail if not exists.
    # Since I cannot run DDL easily without a specific endpoint or direct connection, 
    # I will try to use the 'rpc' call if a 'exec_sql' function exists, or just hope the user runs the SQL.
    # BUT, I can generate a SQL file and ask the user to run it, OR I can try to use the REST API to insert.
    # If the table doesn't exist, the insert will fail.
    
    # Let's generate a SQL file for the schema first.
    pass

def generate_sql_schema():
    sql = """
    -- Content Templates Table
    CREATE TABLE IF NOT EXISTS content_templates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        content_type TEXT NOT NULL,
        platforms JSONB,
        thumbnail TEXT,
        description TEXT,
        dimensions JSONB,
        elements JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Achievement Definitions Table
    CREATE TABLE IF NOT EXISTS achievement_definitions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT,
        rarity TEXT,
        condition_type TEXT,
        condition_value INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- User Achievements Table (to track progress)
    CREATE TABLE IF NOT EXISTS user_achievements (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id),
        achievement_id TEXT REFERENCES achievement_definitions(id),
        unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        progress FLOAT DEFAULT 0,
        UNIQUE(user_id, achievement_id)
    );

    -- Platform Benchmarks Table
    CREATE TABLE IF NOT EXISTS platform_benchmarks (
        metric TEXT PRIMARY KEY,
        value FLOAT NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Scheduled Posts Table
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        id TEXT PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id),
        content JSONB NOT NULL,
        platforms JSONB NOT NULL,
        scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Media Library Table
    CREATE TABLE IF NOT EXISTS media_library (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id),
        type TEXT NOT NULL,
        url TEXT NOT NULL,
        thumbnail TEXT,
        name TEXT,
        tags TEXT[],
        size INTEGER,
        dimensions JSONB,
        duration FLOAT,
        uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    with open("MIGRATE_MOCK_DATA.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print("SQL Schema file created: MIGRATE_MOCK_DATA.sql")

async def migrate_data():
    print("Migrating data to Supabase...")
    
    # 1. Templates
    print(f"Migrating {len(TEMPLATES)} templates...")
    for template in TEMPLATES:
        try:
            # Check if exists
            res = supabase.table("content_templates").select("id").eq("id", template["id"]).execute()
            if not res.data:
                supabase.table("content_templates").insert(template).execute()
                print(f"Inserted template: {template['id']}")
            else:
                # Update
                supabase.table("content_templates").update(template).eq("id", template["id"]).execute()
                print(f"Updated template: {template['id']}")
        except Exception as e:
            print(f"Error migrating template {template['id']}: {e}")

    # 2. Achievements
    print(f"Migrating {len(ACHIEVEMENTS)} achievements...")
    for achievement in ACHIEVEMENTS:
        try:
            res = supabase.table("achievement_definitions").select("id").eq("id", achievement["id"]).execute()
            if not res.data:
                supabase.table("achievement_definitions").insert(achievement).execute()
                print(f"Inserted achievement: {achievement['id']}")
            else:
                supabase.table("achievement_definitions").update(achievement).eq("id", achievement["id"]).execute()
                print(f"Updated achievement: {achievement['id']}")
        except Exception as e:
            print(f"Error migrating achievement {achievement['id']}: {e}")

    # 3. Benchmarks
    print(f"Migrating {len(BENCHMARKS)} benchmarks...")
    for benchmark in BENCHMARKS:
        try:
            res = supabase.table("platform_benchmarks").select("metric").eq("metric", benchmark["metric"]).execute()
            if not res.data:
                supabase.table("platform_benchmarks").insert(benchmark).execute()
                print(f"Inserted benchmark: {benchmark['metric']}")
            else:
                supabase.table("platform_benchmarks").update(benchmark).eq("metric", benchmark["metric"]).execute()
                print(f"Updated benchmark: {benchmark['metric']}")
        except Exception as e:
            print(f"Error migrating benchmark {benchmark['metric']}: {e}")

if __name__ == "__main__":
    generate_sql_schema()
    # We can't run the migration until the tables exist.
    # The user needs to run the SQL first.
    print("\nIMPORTANT: Please run the SQL commands in 'MIGRATE_MOCK_DATA.sql' in your Supabase SQL Editor first.")
    print("Then run this script again to populate the data.")
    
    # Try to run migration anyway, maybe tables exist?
    try:
        asyncio.run(migrate_data())
    except Exception as e:
        print(f"\nMigration failed (probably tables don't exist yet): {e}")
