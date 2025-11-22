-- ============================================
-- TABLES FOR WOW FEATURES (Referral & AI)
-- ============================================

-- 1. REFERRAL SYSTEM
-- ============================================

CREATE TABLE IF NOT EXISTS referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    referred_id UUID REFERENCES users(id) ON DELETE CASCADE,
    referral_code VARCHAR(50) REFERENCES referral_codes(code),
    level INTEGER DEFAULT 1, -- 1 or 2
    status VARCHAR(50) DEFAULT 'pending', -- pending, active
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    referrer_earnings DECIMAL(15, 2) DEFAULT 0.00,
    referred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(referrer_id, referred_id)
);

CREATE TABLE IF NOT EXISTS referral_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    total_referrals INTEGER DEFAULT 0,
    active_referrals INTEGER DEFAULT 0,
    badge_level VARCHAR(50) DEFAULT 'bronze', -- bronze, silver, gold, platinum, diamond
    tier INTEGER DEFAULT 1,
    bonus_commission_rate DECIMAL(5, 2) DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS referral_earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    referral_id UUID REFERENCES referrals(id) ON DELETE SET NULL,
    sale_id UUID REFERENCES sales(id) ON DELETE SET NULL,
    earning_amount DECIMAL(10, 2) NOT NULL,
    level INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending', -- pending, paid
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to generate referral code
CREATE OR REPLACE FUNCTION generate_referral_code(p_user_id UUID)
RETURNS TEXT AS $$
DECLARE
    new_code TEXT;
    username_part TEXT;
    random_part TEXT;
BEGIN
    -- Get username or email part
    SELECT COALESCE(username, SPLIT_PART(email, '@', 1)) INTO username_part
    FROM users
    LEFT JOIN influencers ON users.id = influencers.user_id
    WHERE users.id = p_user_id;
    
    -- Clean username (alphanumeric only)
    username_part := REGEXP_REPLACE(UPPER(username_part), '[^A-Z0-9]', '', 'g');
    
    -- Generate random suffix
    random_part := SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 4);
    
    new_code := SUBSTRING(username_part FROM 1 FOR 6) || random_part;
    
    RETURN new_code;
END;
$$ LANGUAGE plpgsql;


-- 2. AI FEATURES
-- ============================================

CREATE TABLE IF NOT EXISTS product_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    influencer_id UUID REFERENCES influencers(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    match_score INTEGER, -- 0-100
    match_reasons TEXT[], -- Array of strings
    is_active BOOLEAN DEFAULT TRUE,
    clicked BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    platform VARCHAR(50), -- instagram, tiktok, etc.
    content_type VARCHAR(50), -- post, story, reel
    title TEXT,
    content TEXT,
    hashtags TEXT[],
    call_to_action TEXT,
    language VARCHAR(10) DEFAULT 'fr',
    tone VARCHAR(50),
    best_post_time VARCHAR(20),
    best_post_day VARCHAR(20),
    generated_by VARCHAR(50), -- gpt-4, template
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS live_shopping_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50),
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, live, ended
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    viewers_count INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_sales DECIMAL(15, 2) DEFAULT 0.00,
    commission_boost_percentage DECIMAL(5, 2) DEFAULT 0.00,
    featured_products UUID[], -- Array of product IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS live_shopping_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES live_shopping_sessions(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    display_order INTEGER DEFAULT 0,
    is_highlighted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS live_shopping_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES live_shopping_sessions(id) ON DELETE CASCADE,
    order_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Function to generate product recommendations (Mock logic for now)
CREATE OR REPLACE FUNCTION generate_product_recommendations(p_influencer_id UUID)
RETURNS VOID AS $$
DECLARE
    v_category VARCHAR;
    v_product RECORD;
BEGIN
    -- Get influencer category
    SELECT category INTO v_category FROM influencers WHERE id = p_influencer_id;
    
    -- Find matching products
    FOR v_product IN 
        SELECT id FROM products 
        WHERE category = v_category OR v_category IS NULL
        ORDER BY RANDOM() 
        LIMIT 5
    LOOP
        INSERT INTO product_recommendations (
            influencer_id, 
            product_id, 
            match_score, 
            match_reasons, 
            expires_at
        ) VALUES (
            p_influencer_id,
            v_product.id,
            FLOOR(RANDOM() * 20 + 80), -- 80-100 score
            ARRAY['Correspondance de catégorie', 'Haute commission', 'Tendance actuelle'],
            NOW() + INTERVAL '7 days'
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
