-- ============================================
-- OPTIMISATION DASHBOARD - RPC FUNCTIONS
-- ============================================

-- 1. Get Influencer Stats
CREATE OR REPLACE FUNCTION get_influencer_dashboard_stats(p_influencer_id UUID)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_earnings DECIMAL(15, 2) := 0;
    v_total_clicks INTEGER := 0;
    v_total_sales INTEGER := 0;
    v_total_paid DECIMAL(15, 2) := 0;
    v_balance DECIMAL(15, 2) := 0;
    
    -- Growth vars
    v_recent_earnings DECIMAL(15, 2) := 0;
    v_previous_earnings DECIMAL(15, 2) := 0;
    v_earnings_growth DECIMAL(5, 2) := 0;
    
    v_recent_clicks INTEGER := 0;
    v_previous_clicks INTEGER := 0;
    v_clicks_growth DECIMAL(5, 2) := 0;
    
    v_recent_sales INTEGER := 0;
    v_previous_sales INTEGER := 0;
    v_sales_growth DECIMAL(5, 2) := 0;
    
    v_now TIMESTAMP := NOW();
    v_30_days_ago TIMESTAMP := NOW() - INTERVAL '30 days';
    v_60_days_ago TIMESTAMP := NOW() - INTERVAL '60 days';
BEGIN
    -- 1. Basic Stats from conversions
    -- Assuming 'conversions' table contains all events (clicks and sales)
    -- Adjust table name if necessary (e.g. if clicks are in click_tracking)
    
    -- Total Clicks (All rows in conversions for this influencer)
    SELECT COUNT(*) INTO v_total_clicks
    FROM conversions
    WHERE influencer_id = p_influencer_id;
    
    -- Total Sales (Completed conversions)
    SELECT COUNT(*), COALESCE(SUM(commission_amount), 0)
    INTO v_total_sales, v_total_earnings
    FROM conversions
    WHERE influencer_id = p_influencer_id AND status = 'completed';
    
    -- 2. Balance Calculation
    SELECT COALESCE(SUM(amount), 0) INTO v_total_paid
    FROM payouts
    WHERE influencer_id = p_influencer_id AND status = 'paid';
    
    v_balance := v_total_earnings - v_total_paid;
    
    -- 3. Growth Calculations (30 days)
    
    -- Recent Period (Last 30 days)
    SELECT 
        COUNT(*), 
        COUNT(*) FILTER (WHERE status = 'completed'),
        COALESCE(SUM(commission_amount) FILTER (WHERE status = 'completed'), 0)
    INTO v_recent_clicks, v_recent_sales, v_recent_earnings
    FROM conversions
    WHERE influencer_id = p_influencer_id 
    AND created_at >= v_30_days_ago;
    
    -- Previous Period (30-60 days ago)
    SELECT 
        COUNT(*), 
        COUNT(*) FILTER (WHERE status = 'completed'),
        COALESCE(SUM(commission_amount) FILTER (WHERE status = 'completed'), 0)
    INTO v_previous_clicks, v_previous_sales, v_previous_earnings
    FROM conversions
    WHERE influencer_id = p_influencer_id 
    AND created_at >= v_60_days_ago AND created_at < v_30_days_ago;
    
    -- Calculate Growth %
    IF v_previous_earnings > 0 THEN
        v_earnings_growth := ((v_recent_earnings - v_previous_earnings) / v_previous_earnings) * 100;
    END IF;
    
    IF v_previous_clicks > 0 THEN
        v_clicks_growth := ((v_recent_clicks - v_previous_clicks) / v_previous_clicks::DECIMAL) * 100;
    END IF;
    
    IF v_previous_sales > 0 THEN
        v_sales_growth := ((v_recent_sales - v_previous_sales) / v_previous_sales::DECIMAL) * 100;
    END IF;

    RETURN json_build_object(
        'total_earnings', v_total_earnings,
        'total_clicks', v_total_clicks,
        'total_sales', v_total_sales,
        'balance', v_balance,
        'earnings_growth', ROUND(v_earnings_growth, 2),
        'clicks_growth', ROUND(v_clicks_growth, 2),
        'sales_growth', ROUND(v_sales_growth, 2)
    );
END;
$$;

-- 2. Get Merchant Stats
CREATE OR REPLACE FUNCTION get_merchant_dashboard_stats(p_merchant_id UUID)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_sales DECIMAL(15, 2) := 0;
    v_products_count INTEGER := 0;
BEGIN
    -- Total Sales
    SELECT COALESCE(SUM(amount), 0) INTO v_total_sales
    FROM sales
    WHERE merchant_id = p_merchant_id AND status = 'completed';
    
    -- Products Count
    SELECT COUNT(*) INTO v_products_count
    FROM products
    WHERE merchant_id = p_merchant_id;
    
    RETURN json_build_object(
        'total_sales', v_total_sales,
        'products_count', v_products_count,
        'affiliates_count', 0, -- Placeholder
        'roi', 320.5 -- Placeholder
    );
END;
$$;

-- 3. Get Admin Stats
CREATE OR REPLACE FUNCTION get_admin_dashboard_stats()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_users INTEGER := 0;
    v_total_merchants INTEGER := 0;
    v_total_influencers INTEGER := 0;
    v_total_products INTEGER := 0;
    v_total_services INTEGER := 0;
    v_total_revenue DECIMAL(15, 2) := 0;
BEGIN
    -- Users Counts
    SELECT COUNT(*) INTO v_total_users FROM users;
    SELECT COUNT(*) INTO v_total_merchants FROM users WHERE role = 'merchant';
    SELECT COUNT(*) INTO v_total_influencers FROM users WHERE role = 'influencer';
    
    -- Products & Services
    SELECT COUNT(*) INTO v_total_products FROM products;
    SELECT COUNT(*) INTO v_total_services FROM services;
    
    -- Total Revenue
    SELECT COALESCE(SUM(amount), 0) INTO v_total_revenue
    FROM sales
    WHERE status = 'completed';
    
    RETURN json_build_object(
        'total_users', v_total_users,
        'total_merchants', v_total_merchants,
        'total_influencers', v_total_influencers,
        'total_products', v_total_products,
        'total_services', v_total_services,
        'total_revenue', v_total_revenue
    );
END;
$$;
