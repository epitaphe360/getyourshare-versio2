-- ============================================
-- CONTRAINTE: Total retiré ≤ Commissions gagnées
-- ============================================
-- Ce script ajoute une fonction de validation pour garantir
-- que le total des payouts ne dépasse jamais les commissions

-- Fonction pour vérifier le solde avant insertion/update de payout
CREATE OR REPLACE FUNCTION check_payout_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts DECIMAL(10,2);
    new_total_payouts DECIMAL(10,2);
BEGIN
    -- Calculer le total des commissions pour cet influenceur
    SELECT COALESCE(SUM(amount), 0)
    INTO total_commissions
    FROM commissions
    WHERE influencer_id = NEW.influencer_id;
    
    -- Calculer le total des payouts existants (paid et processing)
    SELECT COALESCE(SUM(amount), 0)
    INTO total_payouts
    FROM payouts
    WHERE influencer_id = NEW.influencer_id
    AND id != NEW.id  -- Exclure le payout actuel si c'est un update
    AND status IN ('paid', 'processing', 'pending');
    
    -- Calculer le nouveau total avec ce payout
    new_total_payouts := total_payouts + NEW.amount;
    
    -- RÈGLE OBLIGATOIRE: Vérifier que total_payouts <= total_commissions
    IF new_total_payouts > total_commissions THEN
        RAISE EXCEPTION 
            'Payout refusé: Le total des retraits (%.2f€) dépasserait les commissions gagnées (%.2f€). Solde disponible: %.2f€',
            new_total_payouts,
            total_commissions,
            total_commissions - total_payouts;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Créer le trigger sur la table payouts
DROP TRIGGER IF EXISTS validate_payout_balance ON payouts;

CREATE TRIGGER validate_payout_balance
    BEFORE INSERT OR UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION check_payout_balance();

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE '✅ Contrainte de validation ajoutée sur la table payouts';
    RAISE NOTICE '   Règle: Total retiré ≤ Commissions gagnées';
    RAISE NOTICE '   Trigger: validate_payout_balance';
END $$;
