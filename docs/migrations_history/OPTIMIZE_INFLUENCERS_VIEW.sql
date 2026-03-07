-- View to optimize get_influencers endpoint
-- Aggregates data from users, influencers, commissions, and trackable_links
-- Eliminates N+1 query problem in backend/server.py

DROP VIEW IF EXISTS influencers_stats_view;

CREATE OR REPLACE VIEW influencers_stats_view AS
SELECT 
    u.id as user_id,
    i.id as influencer_id,
    u.email,
    i.username,
    i.full_name,
    i.audience_size,
    i.engagement_rate,
    i.category,
    i.influencer_type,
    i.profile_picture_url,
    i.social_links,
    i.subscription_status as status,
    COALESCE(commissions_stats.total_earnings, 0) as total_earnings,
    COALESCE(links_stats.total_clicks, 0) as total_clicks
FROM 
    users u
JOIN 
    influencers i ON u.id = i.user_id
LEFT JOIN 
    (SELECT influencer_id, SUM(amount) as total_earnings FROM commissions GROUP BY influencer_id) commissions_stats ON i.id = commissions_stats.influencer_id
LEFT JOIN 
    (SELECT influencer_id, SUM(clicks) as total_clicks FROM trackable_links GROUP BY influencer_id) links_stats ON i.id = links_stats.influencer_id
WHERE 
    u.role = 'influencer';
