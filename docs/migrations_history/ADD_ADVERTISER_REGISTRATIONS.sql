-- Création de la table advertiser_registrations manquante
CREATE TABLE IF NOT EXISTS public.advertiser_registrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_name TEXT NOT NULL,
    email TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    country TEXT,
    website TEXT,
    business_type TEXT,
    estimated_budget NUMERIC,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Activer la sécurité RLS
ALTER TABLE public.advertiser_registrations ENABLE ROW LEVEL SECURITY;

-- Politiques de sécurité
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_policies 
        WHERE tablename = 'advertiser_registrations' 
        AND policyname = 'Enable read access for authenticated users'
    ) THEN
        CREATE POLICY "Enable read access for authenticated users" ON public.advertiser_registrations
            FOR SELECT USING (auth.role() = 'authenticated');
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_policies 
        WHERE tablename = 'advertiser_registrations' 
        AND policyname = 'Enable insert access for everyone'
    ) THEN
        CREATE POLICY "Enable insert access for everyone" ON public.advertiser_registrations
            FOR INSERT WITH CHECK (true);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_policies 
        WHERE tablename = 'advertiser_registrations' 
        AND policyname = 'Enable update for admins'
    ) THEN
        CREATE POLICY "Enable update for admins" ON public.advertiser_registrations
            FOR UPDATE USING (auth.role() = 'authenticated');
    END IF;
END $$;
