-- ============================================
-- FIX REFERRAL SYSTEM
-- Corrige la fonction de génération de code et la vue dashboard
-- ============================================

-- 1. Corriger la fonction generate_referral_code pour gérer les usernames NULL ou manquants
CREATE OR REPLACE FUNCTION generate_referral_code(p_user_id UUID)
RETURNS TEXT AS $$
DECLARE
    v_code TEXT;
    v_exists BOOLEAN;
    v_base TEXT;
BEGIN
    -- Récupérer une base pour le code (username, ou full_name, ou email)
    -- On essaie de récupérer username si la colonne existe, sinon on utilise email
    -- Comme on ne peut pas faire de condition sur l'existence de colonne dans PL/PGSQL facilement sans SQL dynamique,
    -- on va utiliser email qui est sûr d'exister.
    
    SELECT UPPER(SUBSTRING(email FROM 1 FOR 3)) INTO v_base
    FROM public.users WHERE id = p_user_id;
    
    -- Si on a un full_name, on peut l'utiliser de préférence
    -- Mais pour l'instant restons simple et robuste avec l'email
    
    -- Nettoyer v_base (garder seulement lettres et chiffres)
    v_base := REGEXP_REPLACE(v_base, '[^A-Z0-9]', 'X', 'g');
    
    IF LENGTH(v_base) < 3 THEN
        v_base := RPAD(v_base, 3, 'X');
    END IF;

    -- Générer code unique
    LOOP
        v_code := v_base || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');

        SELECT EXISTS(SELECT 1 FROM public.referral_codes WHERE code = v_code) INTO v_exists;

        EXIT WHEN NOT v_exists;
    END LOOP;

    RETURN v_code;
END;
$$ LANGUAGE plpgsql;

-- 2. Corriger la vue v_referral_dashboard
-- On recrée la vue en évitant de dépendre de la colonne username si elle n'existe pas
-- Note: Si la colonne username existe, on peut l'utiliser, sinon on utilise email/full_name
-- Pour être sûr, on va dropper la vue et la recréer avec une définition robuste

DROP VIEW IF EXISTS public.v_referral_dashboard;

CREATE OR REPLACE VIEW public.v_referral_dashboard AS
SELECT
    u.id as user_id,
    u.email,
    COALESCE(u.full_name, u.email) as username, -- Fallback robuste
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
GROUP BY u.id, u.email, u.full_name, rc.code, rr.total_referrals,
         rr.active_referrals, rr.total_earnings, rr.badge_level, rr.tier;

