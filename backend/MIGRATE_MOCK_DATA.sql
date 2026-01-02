
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
    