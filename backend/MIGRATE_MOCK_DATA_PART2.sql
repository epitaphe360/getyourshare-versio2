
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
    