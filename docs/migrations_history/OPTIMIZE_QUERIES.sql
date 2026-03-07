-- Optimization: Create Views to avoid N+1 queries in API endpoints

-- View for Merchants Stats
CREATE OR REPLACE VIEW merchants_stats_view AS
SELECT 
    u.id as user_id,
    COALESCE(m.company_name, u.company_name, u.username, 'Inconnu') as company_name,
    COALESCE(m.industry, 'General') as category,
    u.email,
    u.country,
    u.balance,
    COALESCE(SUM(s.amount), 0) as total_revenue,
    u.campaigns_count,
    u.status,
    u.created_at
FROM users u
LEFT JOIN merchants m ON u.id = m.user_id
LEFT JOIN sales s ON u.id = s.merchant_id
WHERE u.role = 'merchant'
GROUP BY u.id, m.company_name, u.company_name, u.username, m.industry, u.email, u.country, u.balance, u.campaigns_count, u.status, u.created_at;

-- View for Influencers Stats
CREATE OR REPLACE VIEW influencers_stats_view AS
SELECT 
    u.id as user_id,
    COALESCE(ip.display_name, CONCAT(u.first_name, ' ', u.last_name), u.username, 'Inconnu') as full_name,
    COALESCE(ip.instagram_handle, u.company_name, u.username) as username,
    u.email,
    COALESCE(ip.instagram_followers, u.followers_count, 0) as audience_size,
    COALESCE(ip.instagram_engagement_rate, u.engagement_rate, 0) as engagement_rate,
    COALESCE(SUM(c.amount), 0) as total_earnings,
    COALESCE(i.total_clicks, 0) as total_clicks,
    COALESCE(i.influencer_type, 'micro') as influencer_type,
    -- Handle array indexing safely or just take the first element if it's an array
    -- Assuming niches is JSONB for ip and TEXT[] for u
    COALESCE(ip.niches ->> 0, u.niche[1], u.category, 'Lifestyle') as category,
    u.profile_picture_url,
    COALESCE(i.social_links, '{}'::jsonb) as social_links,
    u.status
FROM users u
LEFT JOIN influencer_profiles ip ON u.id = ip.user_id
LEFT JOIN influencers i ON u.id = i.user_id
LEFT JOIN commissions c ON u.id = c.influencer_id
WHERE u.role = 'influencer'
GROUP BY u.id, ip.display_name, u.first_name, u.last_name, u.username, ip.instagram_handle, u.company_name, u.email, ip.instagram_followers, u.followers_count, ip.instagram_engagement_rate, u.engagement_rate, i.total_clicks, i.influencer_type, ip.niches, u.niche, u.category, u.profile_picture_url, i.social_links, u.status;
