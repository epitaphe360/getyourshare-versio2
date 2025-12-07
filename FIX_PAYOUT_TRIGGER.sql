-- Correction du trigger de validation des payouts
-- Date: 2024-12-06
-- Problème: Le trigger refuse les payouts même quand les commissions existent

-- 1. Supprimer l'ancien trigger s'il existe
DROP TRIGGER IF EXISTS validate_payout_amount ON payouts;
DROP FUNCTION IF EXISTS check_payout_balance() CASCADE;

-- 2. Créer une fonction de validation corrigée
CREATE OR REPLACE FUNCTION check_payout_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts DECIMAL(10,2);
    available_balance DECIMAL(10,2);
BEGIN
    -- Calculer le total des commissions gagnées (conversions completed)
    SELECT COALESCE(SUM(commission_amount), 0)
    INTO total_commissions
    FROM conversions
    WHERE influencer_id = NEW.influencer_id
    AND status = 'completed';
    
    -- Calculer le total des payouts déjà effectués (tous statuts sauf cancelled/rejected)
    SELECT COALESCE(SUM(amount), 0)
    INTO total_payouts
    FROM payouts
    WHERE influencer_id = NEW.influencer_id
    AND status NOT IN ('cancelled', 'rejected')
    AND id != NEW.id;  -- Exclure le payout en cours d'insertion
    
    -- Calculer le solde disponible
    available_balance := total_commissions - total_payouts;
    
    -- Vérifier si le montant demandé est disponible
    IF NEW.amount > available_balance THEN
        RAISE EXCEPTION 'Payout refusé: Le total des retraits (%.2f€) dépasserait les commissions gagnées (%.2f€). Solde disponible: %.2f€',
            NEW.amount, total_commissions, available_balance
            USING ERRCODE = 'P0001';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Créer le trigger
CREATE TRIGGER validate_payout_amount
    BEFORE INSERT OR UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION check_payout_balance();

-- 4. Commentaire
COMMENT ON FUNCTION check_payout_balance() IS 
'Valide que le montant du payout ne dépasse pas les commissions disponibles (conversions completed - payouts existants)';
