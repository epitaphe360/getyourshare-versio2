-- Fix missing columns
DO $$
BEGIN
    -- Add merchant_id to company_deposits if missing
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'company_deposits') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'company_deposits' AND column_name = 'merchant_id') THEN
            ALTER TABLE public.company_deposits ADD COLUMN merchant_id UUID REFERENCES public.merchants(id) ON DELETE CASCADE;
        END IF;
    END IF;

    -- Add category to influencers if missing
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'influencers') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'influencers' AND column_name = 'category') THEN
            ALTER TABLE public.influencers ADD COLUMN category TEXT DEFAULT 'General';
        END IF;
    END IF;
END $$;
