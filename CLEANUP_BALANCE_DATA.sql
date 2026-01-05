-- ============================================
-- NETTOYAGE DES DONNÉES DE BALANCE INCOHÉRENTES
-- ============================================
-- Ce script supprime les payouts "paid" qui dépassent les commissions
-- À exécuter AVANT d'activer le trigger de validation

-- Désactiver temporairement le trigger (si activé)
DROP TRIGGER IF EXISTS validate_payout_balance ON payouts;

-- Afficher l'état actuel
DO $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts_paid DECIMAL(10,2);
    balance DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total_commissions FROM commissions;
    SELECT COALESCE(SUM(amount), 0) INTO total_payouts_paid FROM payouts WHERE status = 'paid';
    balance := total_commissions - total_payouts_paid;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'ÉTAT ACTUEL DES DONNÉES';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total commissions: %.2f€', total_commissions;
    RAISE NOTICE 'Total payouts paid: %.2f€', total_payouts_paid;
    RAISE NOTICE 'Balance global: %.2f€', balance;
    RAISE NOTICE '';
    
    IF balance < 0 THEN
        RAISE NOTICE '⚠️ BALANCE NÉGATIF DÉTECTÉ!';
    ELSE
        RAISE NOTICE '✅ Balance positif';
    END IF;
END $$;

-- Supprimer tous les payouts "paid" (OPTION RADICALE pour tests)
-- ATTENTION: Cette commande supprime TOUTES les données de payouts avec status='paid'
DELETE FROM payouts WHERE status = 'paid';

-- Afficher le résultat
DO $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts_paid DECIMAL(10,2);
    balance DECIMAL(10,2);
    nb_payouts INT;
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO total_commissions FROM commissions;
    SELECT COALESCE(SUM(amount), 0) INTO total_payouts_paid FROM payouts WHERE status = 'paid';
    SELECT COUNT(*) INTO nb_payouts FROM payouts WHERE status = 'paid';
    balance := total_commissions - total_payouts_paid;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'APRÈS NETTOYAGE';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total commissions: %.2f€', total_commissions;
    RAISE NOTICE 'Total payouts paid: %.2f€', total_payouts_paid;
    RAISE NOTICE 'Nombre de payouts paid: %', nb_payouts;
    RAISE NOTICE 'Balance global: %.2f€', balance;
    RAISE NOTICE '';
    
    IF balance < 0 THEN
        RAISE NOTICE '❌ Balance encore négatif!';
    ELSE
        RAISE NOTICE '✅ SUCCÈS - Balance positif!';
    END IF;
END $$;

-- Réactiver le trigger de validation
CREATE OR REPLACE FUNCTION check_payout_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts DECIMAL(10,2);
    new_total_payouts DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(amount), 0)
    INTO total_commissions
    FROM commissions
    WHERE influencer_id = NEW.influencer_id;
    
    SELECT COALESCE(SUM(amount), 0)
    INTO total_payouts
    FROM payouts
    WHERE influencer_id = NEW.influencer_id
    AND id != NEW.id
    AND status IN ('paid', 'processing', 'pending');
    
    new_total_payouts := total_payouts + NEW.amount;
    
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

CREATE TRIGGER validate_payout_balance
    BEFORE INSERT OR UPDATE ON payouts
    FOR EACH ROW
    EXECUTE FUNCTION check_payout_balance();

-- Confirmation
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ NETTOYAGE TERMINÉ';
    RAISE NOTICE '✅ Trigger de validation réactivé';
    RAISE NOTICE '========================================';
END $$;
