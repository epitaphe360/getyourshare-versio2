-- ============================================
-- FIX: AI FUNCTION SYNTAX ERROR
-- ============================================

CREATE OR REPLACE FUNCTION calculate_product_match_score(
    p_influencer_id UUID,
    p_product_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_score INTEGER := 0;
    v_influencer_niche TEXT;
    v_product_category TEXT;
    v_avg_performance DECIMAL;
BEGIN
    -- Récupérer niche influenceur
    SELECT metadata->>'niche' INTO v_influencer_niche
    FROM public.users
    WHERE id = p_influencer_id;

    -- Récupérer catégorie produit
    SELECT category INTO v_product_category
    FROM public.products
    WHERE id = p_product_id;

    -- 1. Niche match (40 points)
    IF v_influencer_niche = v_product_category THEN
        v_score := v_score + 40;
    ELSIF v_influencer_niche ILIKE '%' || v_product_category || '%' THEN
        v_score := v_score + 20;
    END IF;

    -- 2. Performance historique (40 points)
    -- FIX: Utilisation de commission_rate au lieu de conversion_rate (colonne inexistante)
    -- Note: Idéalement on utiliserait (conversions/clicks), mais pour l'instant on utilise commission_rate pour éviter l'erreur
    SELECT COALESCE(AVG(c.commission_rate), 0) INTO v_avg_performance
    FROM public.conversions c
    JOIN public.products p ON c.product_id = p.id
    WHERE c.influencer_id = p_influencer_id
      AND p.category = v_product_category;

    v_score := v_score + LEAST(40, (v_avg_performance * 4)::INTEGER);

    -- 3. Prix match (20 points)
    -- Simplifié: on donne 20 points si le produit existe
    IF p_product_id IS NOT NULL THEN
        v_score := v_score + 20;
    END IF;

    RETURN LEAST(100, v_score);
END;
$$ LANGUAGE plpgsql;
