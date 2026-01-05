-- Fix missing schema elements identified during audit

-- 0. Ensure team_members table exists with correct schema
CREATE TABLE IF NOT EXISTS public.team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES public.merchants(id),
    member_id UUID REFERENCES public.users(id),
    team_role TEXT,
    status TEXT DEFAULT 'pending_invitation',
    invited_email TEXT,
    invitation_token TEXT,
    invitation_sent_at TIMESTAMP WITH TIME ZONE,
    invitation_accepted_at TIMESTAMP WITH TIME ZONE,
    can_view_all_sales BOOLEAN DEFAULT false,
    can_manage_products BOOLEAN DEFAULT false,
    custom_commission_rate DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add missing columns to team_members if they don't exist (for existing table)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'status') THEN
        ALTER TABLE public.team_members ADD COLUMN status TEXT DEFAULT 'pending_invitation';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'team_role') THEN
        ALTER TABLE public.team_members ADD COLUMN team_role TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'company_id') THEN
        ALTER TABLE public.team_members ADD COLUMN company_id UUID REFERENCES public.merchants(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'member_id') THEN
        ALTER TABLE public.team_members ADD COLUMN member_id UUID REFERENCES public.users(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'invited_email') THEN
        ALTER TABLE public.team_members ADD COLUMN invited_email TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'can_view_all_sales') THEN
        ALTER TABLE public.team_members ADD COLUMN can_view_all_sales BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'can_manage_products') THEN
        ALTER TABLE public.team_members ADD COLUMN can_manage_products BOOLEAN DEFAULT false;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'custom_commission_rate') THEN
        ALTER TABLE public.team_members ADD COLUMN custom_commission_rate DECIMAL(5,2);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'notes') THEN
        ALTER TABLE public.team_members ADD COLUMN notes TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'invitation_token') THEN
        ALTER TABLE public.team_members ADD COLUMN invitation_token TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'invitation_sent_at') THEN
        ALTER TABLE public.team_members ADD COLUMN invitation_sent_at TIMESTAMP WITH TIME ZONE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'team_members' AND column_name = 'invitation_accepted_at') THEN
        ALTER TABLE public.team_members ADD COLUMN invitation_accepted_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- 0.5 Ensure users table has required columns for the view
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'first_name') THEN
        ALTER TABLE public.users ADD COLUMN first_name TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'last_name') THEN
        ALTER TABLE public.users ADD COLUMN last_name TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'profile_picture_url') THEN
        ALTER TABLE public.users ADD COLUMN profile_picture_url TEXT;
    END IF;
END $$;

-- 0.6 Ensure affiliate_links table exists (Moved up)
CREATE TABLE IF NOT EXISTS public.affiliate_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id),
    product_id UUID REFERENCES public.products(id),
    unique_code TEXT UNIQUE NOT NULL,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ensure affiliate_links has product_id
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'affiliate_links' AND column_name = 'product_id') THEN
        ALTER TABLE public.affiliate_links ADD COLUMN product_id UUID REFERENCES public.products(id);
    END IF;
END $$;

-- 0.7 Ensure leads table exists (Moved up)
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES public.merchants(id),
    sales_rep_id UUID REFERENCES public.sales_representatives(id),
    contact_name TEXT,
    contact_email TEXT,
    company_name TEXT,
    lead_status TEXT DEFAULT 'new',
    score INTEGER DEFAULT 0,
    estimated_value DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 1. Create v_team_members_details view
CREATE OR REPLACE VIEW public.v_team_members_details AS
SELECT 
    tm.id,
    tm.company_id,
    tm.member_id,
    tm.team_role,
    tm.can_view_all_sales,
    tm.can_manage_products,
    tm.custom_commission_rate,
    tm.status,
    tm.invited_email,
    tm.invitation_sent_at,
    tm.invitation_accepted_at,
    tm.notes,
    tm.created_at,
    u.email as member_email,
    u.first_name as member_first_name,
    u.last_name as member_last_name,
    u.role as member_role,
    u.profile_picture_url
FROM 
    public.team_members tm
LEFT JOIN 
    public.users u ON tm.member_id = u.id;

-- 3. Add foreign key between affiliate_links and products
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_affiliate_links_product') THEN
        ALTER TABLE public.affiliate_links 
        ADD CONSTRAINT fk_affiliate_links_product 
        FOREIGN KEY (product_id) 
        REFERENCES public.products(id);
    END IF;
END $$;

-- 4. Add foreign key between leads and merchants
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_leads_merchant') THEN
        -- Clean up orphaned leads first to avoid constraint violation
        DELETE FROM public.leads 
        WHERE merchant_id IS NOT NULL 
        AND merchant_id NOT IN (SELECT id FROM public.merchants);

        ALTER TABLE public.leads 
        ADD CONSTRAINT fk_leads_merchant 
        FOREIGN KEY (merchant_id) 
        REFERENCES public.merchants(id);
    END IF;
END $$;

-- 5. Add link column to notifications if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'link') THEN
        ALTER TABLE public.notifications ADD COLUMN link TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notifications' AND column_name = 'user_type') THEN
        ALTER TABLE public.notifications ADD COLUMN user_type TEXT;
    END IF;
END $$;

-- 6. Create v_active_subscriptions view
CREATE OR REPLACE VIEW public.v_active_subscriptions AS
SELECT 
    s.id,
    s.user_id,
    s.status,
    s.plan_id,
    s.current_period_start as started_at,
    s.current_period_end as ends_at,
    s.created_at,
    sp.name as plan_name,
    sp.price as plan_price,
    NULL::numeric as plan_commission_rate,
    NULL::integer as plan_max_team_members,
    sp.max_campaigns as plan_max_campaigns,
    sp.max_tracking_links as plan_max_tracking_links,
    NULL::boolean as plan_instant_payout,
    NULL::text as plan_analytics_level,
    NULL::boolean as plan_priority_support
FROM 
    public.subscriptions s
LEFT JOIN 
    public.subscription_plans sp ON s.plan_id = sp.id
WHERE 
    s.status = 'active';

-- 7. Create increment function
CREATE OR REPLACE FUNCTION public.increment(column_name text, id_value uuid, table_name text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('UPDATE public.%I SET %I = %I + 1 WHERE id = $1', table_name, column_name, column_name)
    USING id_value;
END;
$$;

-- 8. Create check_subscription_limit function
CREATE OR REPLACE FUNCTION public.check_subscription_limit(
    p_user_id UUID,
    p_limit_type VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    v_subscription_id UUID;
    v_plan_max INTEGER;
    v_current_count INTEGER;
BEGIN
    -- Récupérer l'abonnement actif
    SELECT s.id,
           CASE
               WHEN p_limit_type = 'campaigns' THEN sp.max_campaigns
               WHEN p_limit_type = 'tracking_links' THEN sp.max_tracking_links
               WHEN p_limit_type = 'products' THEN sp.max_products
               ELSE NULL
           END as plan_max
    INTO v_subscription_id, v_plan_max
    FROM subscriptions s
    JOIN subscription_plans sp ON s.plan_id = sp.id
    WHERE s.user_id = p_user_id
      AND s.status IN ('active', 'trialing')
    LIMIT 1;

    -- Si pas d'abonnement, refuser
    IF v_subscription_id IS NULL THEN
        RETURN FALSE;
    END IF;

    -- Si max_limit NULL ou -1 = illimité
    IF v_plan_max IS NULL OR v_plan_max = -1 THEN
        RETURN TRUE;
    END IF;

    -- Compter l'utilisation actuelle
    v_current_count := 0;
    
    IF p_limit_type = 'campaigns' THEN
        SELECT count(*) INTO v_current_count FROM campaigns WHERE merchant_id = (SELECT id FROM merchants WHERE user_id = p_user_id);
    ELSIF p_limit_type = 'tracking_links' THEN
        SELECT count(*) INTO v_current_count FROM tracking_links WHERE influencer_id = p_user_id;
    ELSIF p_limit_type = 'products' THEN
        SELECT count(*) INTO v_current_count FROM products WHERE merchant_id = (SELECT id FROM merchants WHERE user_id = p_user_id);
    END IF;

    -- Vérifier si limite atteinte
    RETURN v_current_count < v_plan_max;
END;
$$ LANGUAGE plpgsql;

