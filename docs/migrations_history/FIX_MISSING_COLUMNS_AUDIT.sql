
-- Fix missing columns in commissions
ALTER TABLE public.commissions 
ADD COLUMN IF NOT EXISTS merchant_id UUID REFERENCES public.users(id);

-- Fix missing columns in social_media_stats
ALTER TABLE public.social_media_stats 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.users(id);

-- Fix missing columns in leads (re-applying just in case)
ALTER TABLE public.leads 
ADD COLUMN IF NOT EXISTS lead_status TEXT DEFAULT 'new';

-- Ensure leads has commercial_id if it was missed
ALTER TABLE public.leads 
ADD COLUMN IF NOT EXISTS commercial_id UUID REFERENCES public.users(id);

-- Check if merchants and influencers tables exist and populate them if needed
-- This part is tricky without knowing the exact schema, but we can try to insert if they exist.
-- We will handle the population in a python script to be safer with IDs.
