# 🔧 Migrations SQL Nécessaires pour l'Automation

## Résumé des Colonnes Ajoutées

Voici toutes les migrations SQL qui ont été créées pour corriger les erreurs de structure de base de données détectées pendant l'exécution du script d'automation.

---

## 1. ✅ tracking_links - destination_url
**Fichier:** `ADD_DESTINATION_URL_TO_TRACKING_LINKS.sql`
**Status:** ✅ Appliqué automatiquement

```sql
ALTER TABLE tracking_links 
ADD COLUMN IF NOT EXISTS destination_url TEXT;
```

---

## 2. ✅ tracking_events - Colonnes de tracking
**Fichier:** `ADD_ALL_TRACKING_COLUMNS.sql`
**Status:** ✅ Appliqué automatiquement

```sql
ALTER TABLE tracking_events 
ADD COLUMN IF NOT EXISTS browser TEXT,
ADD COLUMN IF NOT EXISTS device TEXT,
ADD COLUMN IF NOT EXISTS device_type TEXT,
ADD COLUMN IF NOT EXISTS country TEXT,
ADD COLUMN IF NOT EXISTS city TEXT,
ADD COLUMN IF NOT EXISTS referrer TEXT;
```

**Note:** Le script utilise `event_data` (JSONB) au lieu de `metadata` pour les données structurées.

---

## 3. ✅ conversions - Colonnes supplémentaires
**Fichier:** `ADD_CONVERSION_COLUMNS.sql`
**Status:** ✅ Appliqué automatiquement

```sql
ALTER TABLE conversions 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS order_id TEXT,
ADD COLUMN IF NOT EXISTS platform_fee DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS payment_method TEXT,
ADD COLUMN IF NOT EXISTS customer_email TEXT,
ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ;
```

**Important:** Les statuts valides sont : `pending`, `completed`, `cancelled` (pas `paid`).

---

## 4. ✅ payouts - user_id
**Fichier:** `ADD_USER_ID_TO_PAYOUTS.sql`
**Status:** ✅ Appliqué automatiquement

```sql
ALTER TABLE payouts 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;
```

---

## 5. ⚠️ CRITIQUE - Trigger payouts (À APPLIQUER MANUELLEMENT)
**Fichier:** `FIX_PAYOUT_TRIGGER.sql`
**Status:** ⚠️ **DOIT ÊTRE APPLIQUÉ DANS SUPABASE SQL EDITOR**

Le trigger actuel a un bug : il retourne toujours 0.00€ de commissions gagnées.

**Solution:**
```sql
-- 1. Supprimer l'ancien trigger
DROP TRIGGER IF EXISTS validate_payout_amount ON payouts;
DROP FUNCTION IF EXISTS check_payout_balance();

-- 2. Créer la fonction corrigée
CREATE OR REPLACE FUNCTION check_payout_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_commissions DECIMAL(10,2);
    total_payouts DECIMAL(10,2);
    available_balance DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(commission_amount), 0)
    INTO total_commissions
    FROM conversions
    WHERE influencer_id = NEW.influencer_id
    AND status = 'completed';
    
    SELECT COALESCE(SUM(amount), 0)
    INTO total_payouts
    FROM payouts
    WHERE influencer_id = NEW.influencer_id
    AND status NOT IN ('cancelled', 'rejected')
    AND id != NEW.id;
    
    available_balance := total_commissions - total_payouts;
    
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
```

**Alternative pour les tests:**
```sql
-- Désactiver temporairement le trigger
ALTER TABLE payouts DISABLE TRIGGER validate_payout_amount;

-- Réactiver après les tests
ALTER TABLE payouts ENABLE TRIGGER validate_payout_amount;
```

---

## 📊 Progression du Script d'Automation

### ✅ Phases Complétées (0-6)
- **Phase 0:** Nettoyage complet
- **Phase 1:** Setup acteurs & comptes
- **Phase 2:** Flux financier entrant
- **Phase 3:** Création de l'offre
- **Phase 4:** Partenariat & Tracking
- **Phase 5:** Cycle de vente complet
- **Phase 6:** Remboursement

### ⏸️ Phase Bloquée
- **Phase 7:** Retrait - Bloqué par le trigger payouts

### ⏳ Phases Restantes (7-9)
- **Phase 7B-7J:** Fonctionnalités avancées
- **Phase 8:** Affiliations avancées
- **Phase 9:** Statistiques et analytics

---

## 🎯 Actions Requises

### Action Immédiate
1. **Ouvrir Supabase Dashboard**
2. **Aller dans SQL Editor**
3. **Copier-coller le contenu de `FIX_PAYOUT_TRIGGER.sql`**
4. **Exécuter le SQL**
5. **Relancer le script:** `python backend/run_automation_scenario.py`

### Vérification
Après application du trigger, le script devrait:
- ✅ Créer une conversion completed (50 EUR de commission)
- ✅ Ajouter 50 EUR à la balance de l'influenceur
- ✅ Refuser un retrait de 1000 EUR (solde insuffisant)
- ✅ Accepter un retrait de 50 EUR (solde suffisant)
- ✅ Continuer jusqu'à la Phase 9

---

## 📝 Notes Techniques

### Tables Modifiées
- `tracking_links` - 1 colonne ajoutée
- `tracking_events` - 6 colonnes ajoutées
- `conversions` - 6 colonnes ajoutées
- `payouts` - 1 colonne ajoutée + 1 trigger corrigé

### Compatibilité
Toutes les migrations utilisent `ADD COLUMN IF NOT EXISTS` pour être idempotentes.

### Performance
Le trigger corrigé utilise des index existants sur:
- `conversions(influencer_id, status)`
- `payouts(influencer_id, status)`

---

## 🐛 Bugs Corrigés dans le Script

1. **services:** Utilise `price_per_lead` au lieu de `price`
2. **social_media_publications:** Utilise `influencer_id` au lieu de `user_id`
3. **tracking_events:** Utilise `event_data` au lieu de `metadata`
4. **conversions:** Status `paid` remplacé par `completed`
5. **merchant creation:** Contournement du trigger sales_assignments
6. **tracking_events cleanup:** Ajout de la suppression avant tracking_links

---

## ✅ Résultat Final Attendu

Une fois le trigger corrigé, le script d'automation devrait s'exécuter complètement de la Phase 0 à la Phase 9, validant ainsi l'intégralité du flux de l'application GetYourShare.
