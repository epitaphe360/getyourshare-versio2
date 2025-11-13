-- ============================================
-- SYSTÈME DE PARRAINAGE VIRAL
-- Multi-niveaux avec tracking des gains
-- ============================================

-- Table: referral_codes
-- Stocke les codes de parrainage uniques par utilisateur
CREATE TABLE IF NOT EXISTS public.referral_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT unique_user_referral UNIQUE(user_id)
);

-- Table: referrals
-- Tracking des parrainages et du réseau
CREATE TABLE IF NOT EXISTS public.referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    referred_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    referral_code VARCHAR(20) NOT NULL,
    level INTEGER DEFAULT 1, -- 1 = direct, 2 = indirect
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, inactive

    -- Tracking financier
    total_sales DECIMAL(12,2) DEFAULT 0,
    total_commission DECIMAL(12,2) DEFAULT 0,
    referrer_earnings DECIMAL(12,2) DEFAULT 0, -- Ce que le parrain gagne

    -- Dates
    referred_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    last_sale_at TIMESTAMPTZ,

    CONSTRAINT unique_referral UNIQUE(referrer_id, referred_id),
    CONSTRAINT no_self_referral CHECK (referrer_id != referred_id)
);

-- Table: referral_earnings
-- Historique détaillé des gains de parrainage
CREATE TABLE IF NOT EXISTS public.referral_earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID REFERENCES public.referrals(id) ON DELETE CASCADE NOT NULL,
    referrer_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    referred_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,

    -- Transaction source
    order_id UUID, -- Si lié à une commande
    sale_amount DECIMAL(12,2) NOT NULL,
    commission_amount DECIMAL(12,2) NOT NULL,
    earning_amount DECIMAL(12,2) NOT NULL, -- Ce que le parrain gagne (% de la commission)
    earning_percentage DECIMAL(5,2) NOT NULL, -- 10% niveau 1, 5% niveau 2

    level INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, cancelled

    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Métadonnées
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table: referral_rewards
-- Paliers de récompenses et badges
CREATE TABLE IF NOT EXISTS public.referral_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,

    -- Stats
    total_referrals INTEGER DEFAULT 0,
    active_referrals INTEGER DEFAULT 0,
    total_network_sales DECIMAL(12,2) DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0,

    -- Badges
    badge_level VARCHAR(20) DEFAULT 'bronze', -- bronze, silver, gold, platinum, diamond
    tier INTEGER DEFAULT 1, -- 1-5

    -- Bonus
    bonus_commission_rate DECIMAL(5,2) DEFAULT 0, -- Bonus permanent en %
    featured_on_homepage BOOLEAN DEFAULT false,
    priority_support BOOLEAN DEFAULT false,

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes pour performance
CREATE INDEX IF NOT EXISTS idx_referral_codes_user ON public.referral_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_referral_codes_code ON public.referral_codes(code);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON public.referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON public.referrals(referred_id);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON public.referrals(status);
CREATE INDEX IF NOT EXISTS idx_referral_earnings_referrer ON public.referral_earnings(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referral_earnings_status ON public.referral_earnings(status);
CREATE INDEX IF NOT EXISTS idx_referral_rewards_user ON public.referral_rewards(user_id);

-- Fonction: Générer code de parrainage unique
CREATE OR REPLACE FUNCTION generate_referral_code(p_user_id UUID)
RETURNS TEXT AS $$
DECLARE
    v_code TEXT;
    v_exists BOOLEAN;
    v_username TEXT;
BEGIN
    -- Récupérer nom utilisateur
    SELECT UPPER(SUBSTRING(username FROM 1 FOR 3)) INTO v_username
    FROM public.users WHERE id = p_user_id;

    -- Générer code unique
    LOOP
        v_code := v_username || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');

        SELECT EXISTS(SELECT 1 FROM public.referral_codes WHERE code = v_code) INTO v_exists;

        EXIT WHEN NOT v_exists;
    END LOOP;

    RETURN v_code;
END;
$$ LANGUAGE plpgsql;

-- Fonction: Calculer gains de parrainage
CREATE OR REPLACE FUNCTION calculate_referral_earnings()
RETURNS TRIGGER AS $$
DECLARE
    v_level1_rate DECIMAL := 0.10; -- 10% pour niveau 1
    v_level2_rate DECIMAL := 0.05; -- 5% pour niveau 2
    v_referrer_id UUID;
    v_commission DECIMAL;
BEGIN
    -- Niveau 1: Parrain direct
    SELECT referrer_id INTO v_referrer_id
    FROM public.referrals
    WHERE referred_id = NEW.influencer_id AND level = 1 AND status = 'active'
    LIMIT 1;

    IF v_referrer_id IS NOT NULL THEN
        v_commission := NEW.commission * v_level1_rate;

        INSERT INTO public.referral_earnings (
            referral_id, referrer_id, referred_id,
            order_id, sale_amount, commission_amount, earning_amount,
            earning_percentage, level
        )
        SELECT
            r.id, r.referrer_id, r.referred_id,
            NEW.id, NEW.amount, NEW.commission, v_commission,
            v_level1_rate * 100, 1
        FROM public.referrals r
        WHERE r.referred_id = NEW.influencer_id AND r.level = 1
        LIMIT 1;

        -- Niveau 2: Grand-parrain
        SELECT r2.referrer_id INTO v_referrer_id
        FROM public.referrals r1
        JOIN public.referrals r2 ON r1.referrer_id = r2.referred_id
        WHERE r1.referred_id = NEW.influencer_id AND r2.level = 1
        LIMIT 1;

        IF v_referrer_id IS NOT NULL THEN
            v_commission := NEW.commission * v_level2_rate;

            INSERT INTO public.referral_earnings (
                referral_id, referrer_id, referred_id,
                order_id, sale_amount, commission_amount, earning_amount,
                earning_percentage, level
            )
            SELECT
                r2.id, r2.referrer_id, r1.referred_id,
                NEW.id, NEW.amount, NEW.commission, v_commission,
                v_level2_rate * 100, 2
            FROM public.referrals r1
            JOIN public.referrals r2 ON r1.referrer_id = r2.referred_id
            WHERE r1.referred_id = NEW.influencer_id
            LIMIT 1;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-calcul gains sur nouvelle conversion
-- Note: À activer quand table conversions existe
-- CREATE TRIGGER trigger_calculate_referral_earnings
--     AFTER INSERT ON public.conversions
--     FOR EACH ROW
--     EXECUTE FUNCTION calculate_referral_earnings();

-- Fonction: Mettre à jour stats parrainage
CREATE OR REPLACE FUNCTION update_referral_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Mettre à jour total_referrals du parrain
    UPDATE public.referral_rewards
    SET
        total_referrals = (
            SELECT COUNT(*) FROM public.referrals
            WHERE referrer_id = NEW.referrer_id
        ),
        active_referrals = (
            SELECT COUNT(*) FROM public.referrals
            WHERE referrer_id = NEW.referrer_id AND status = 'active'
        ),
        updated_at = NOW()
    WHERE user_id = NEW.referrer_id;

    -- Créer l'entrée si n'existe pas
    INSERT INTO public.referral_rewards (user_id, total_referrals, active_referrals)
    VALUES (NEW.referrer_id, 1, 0)
    ON CONFLICT (user_id) DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update stats
CREATE TRIGGER trigger_update_referral_stats
    AFTER INSERT ON public.referrals
    FOR EACH ROW
    EXECUTE FUNCTION update_referral_stats();

-- Vue: Dashboard parrainage par utilisateur
CREATE OR REPLACE VIEW public.v_referral_dashboard AS
SELECT
    u.id as user_id,
    u.email,
    u.username,
    rc.code as referral_code,
    rr.total_referrals,
    rr.active_referrals,
    rr.total_earnings,
    rr.badge_level,
    rr.tier,
    COUNT(DISTINCT r.id) as direct_referrals,
    COALESCE(SUM(re.earning_amount), 0) as pending_earnings,
    COALESCE(SUM(CASE WHEN re.status = 'paid' THEN re.earning_amount ELSE 0 END), 0) as paid_earnings
FROM public.users u
LEFT JOIN public.referral_codes rc ON u.id = rc.user_id
LEFT JOIN public.referral_rewards rr ON u.id = rr.user_id
LEFT JOIN public.referrals r ON u.id = r.referrer_id
LEFT JOIN public.referral_earnings re ON u.id = re.referrer_id
GROUP BY u.id, u.email, u.username, rc.code, rr.total_referrals,
         rr.active_referrals, rr.total_earnings, rr.badge_level, rr.tier;

-- Commentaires
COMMENT ON TABLE public.referral_codes IS 'Codes de parrainage uniques par utilisateur';
COMMENT ON TABLE public.referrals IS 'Réseau de parrainage multi-niveaux';
COMMENT ON TABLE public.referral_earnings IS 'Historique détaillé des gains de parrainage';
COMMENT ON TABLE public.referral_rewards IS 'Récompenses et badges parrainage';

-- Données de test
INSERT INTO public.referral_codes (user_id, code)
SELECT id, 'TEST' || LPAD(ROW_NUMBER() OVER ()::TEXT, 4, '0')
FROM public.users
WHERE role IN ('influencer', 'merchant')
LIMIT 10
ON CONFLICT (user_id) DO NOTHING;

-- Vérification
SELECT 'Système de parrainage créé avec succès!' as status;
SELECT COUNT(*) as codes_created FROM public.referral_codes;
