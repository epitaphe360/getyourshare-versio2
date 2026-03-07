# 🔧 SOLUTION: fiscal_invoices TABLE → VUE

## ❌ Problèmes identifiés

### Erreur 1:
```
Error: Failed to run sql query: ERROR: 42703: column "payment_id" of relation "fiscal_invoices" does not exist
```

### Erreur 2:
```
Error: Failed to run sql query: ERROR: 42809: "fiscal_invoices" is not a view
```

## 🔍 Analyse

1. **fiscal_invoices existe comme TABLE** (au lieu d'une vue)
2. **Cette table n'a pas les colonnes**: `payment_id`, `payment_status`, `stripe_payment_intent_id`, etc.
3. **Table principale**: `invoices` existe et doit contenir les vraies données
4. **Solution**: Supprimer la table `fiscal_invoices` et la recréer comme VUE vers `invoices`

## ✅ Solution CORRIGÉE

### ÉTAPE UNIQUE: Exécuter migration SQL corrigée

**Via Supabase Dashboard** (OBLIGATOIRE)

1. Ouvrir: https://supabase.com/dashboard/project/YOUR_PROJECT/sql
2. Copier-coller le SQL suivant (corrige fiscal_invoices TABLE → VUE):

```sql
-- ⚠️  IMPORTANT: Supprimer la table fiscal_invoices existante
DROP TABLE IF EXISTS fiscal_invoices CASCADE;

-- Ajouter colonnes paiement à invoices (table principale)
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS payment_id TEXT,
ADD COLUMN IF NOT EXISTS payment_provider TEXT,
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid',
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT,
ADD COLUMN IF NOT EXISTS paypal_order_id TEXT,
ADD COLUMN IF NOT EXISTS payment_link TEXT,
ADD COLUMN IF NOT EXISTS webhook_received_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS refund_reason TEXT,
ADD COLUMN IF NOT EXISTS bank_reconciliation_id UUID,
ADD COLUMN IF NOT EXISTS reminder_sent_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reminder_sent_at TIMESTAMP;

-- Créer fiscal_invoices comme VUE (pas table!)
CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;

-- Index performance
CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON invoices(payment_id);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoices_stripe_intent ON invoices(stripe_payment_intent_id);
CREATE INDEX IF NOT EXISTS idx_invoices_paypal_order ON invoices(paypal_order_id);

-- Tables rapprochement bancaire
CREATE TABLE IF NOT EXISTS bank_reconciliations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bank_name TEXT NOT NULL,
  statement_date DATE NOT NULL,
  total_amount DECIMAL(12,2) DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
  payment_provider TEXT NOT NULL,
  payment_link TEXT NOT NULL,
  payment_id TEXT UNIQUE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  currency TEXT DEFAULT 'MAD',
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Contrainte validation (avec vérification d'existence)
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint 
    WHERE conname = 'check_payment_status' 
    AND conrelid = 'invoices'::regclass
  ) THEN
    ALTER TABLE invoices 
    ADD CONSTRAINT check_payment_status 
    CHECK (payment_status IN ('unpaid', 'pending', 'paid', 'failed', 'refunded', 'partially_refunded'));
  END IF;
END $$;

-- Index nouvelles tables
CREATE INDEX IF NOT EXISTS idx_bank_reconciliations_user ON bank_reconciliations(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_invoice ON payment_links(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payment_links_payment_id ON payment_links(payment_id);
```

3. Cliquer **Run**

**Fichier SQL complet disponible**: `backend/migrations/014_fix_fiscal_invoices_view.sql`

### ÉTAPE 2: Fichiers déjà mis à jour

Les fichiers suivants ont été automatiquement corrigés pour utiliser `invoices` au lieu de `fiscal_invoices`:

✅ `backend/fiscal_email_service.py`  
✅ `backend/payment_webhooks.py`  
✅ `backend/fiscal_endpoints.py`

## 📋 Vérification post-migration

Après avoir exécuté la migration SQL, vérifier:

```python
# Test rapide
from supabase import create_client
import os

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Doit fonctionner sans erreur
result = supabase.table('invoices').select('payment_id, payment_status').limit(1).execute()
print("✅ Colonnes OK!")

# Vérifier la vue
result = supabase.table('fiscal_invoices').select('*').limit(1).execute()
print("✅ Vue fiscal_invoices OK!")
```

## 🎯 Résultat attendu

Après migration:

- ✅ Table `invoices` avec 12 nouvelles colonnes paiement
- ✅ Vue `fiscal_invoices` (alias vers `invoices`)
- ✅ 2 nouvelles tables: `bank_reconciliations`, `payment_links`
- ✅ 4 index optimisation performance
- ✅ Code Python compatible avec nouveau schéma

## 📁 Fichiers créés/modifiés

1. **Nouveaux fichiers:**
   - `backend/migrations/013_add_payment_columns.sql` - Migration complète
   - `backend/apply_payment_columns.py` - Script test/instructions

2. **Fichiers corrigés:**
   - `backend/fiscal_email_service.py` - invoices au lieu de fiscal_invoices
   - `backend/payment_webhooks.py` - invoices au lieu de fiscal_invoices
   - `backend/fiscal_endpoints.py` - invoices au lieu de fiscal_invoices

## 🚀 Prochaines étapes

Une fois la migration exécutée:

1. **Redémarrer serveur backend**
   ```powershell
   cd backend
   python server.py
   ```

2. **Tester webhooks Stripe**
   ```powershell
   stripe listen --forward-to localhost:8003/api/webhooks/stripe/payment
   ```

3. **Tester génération PDF facture**
   ```python
   # POST /api/fiscal/invoices/{id}/generate-pdf
   ```

4. **Tester envoi email**
   ```python
   # POST /api/fiscal/invoices/{id}/send-email
   ```

## 📊 Impact

- **Tables modifiées**: 1 (`invoices`)
- **Vues créées**: 1 (`fiscal_invoices`)
- **Nouvelles tables**: 2 (`bank_reconciliations`, `payment_links`)
- **Nouveaux index**: 4
- **Fichiers Python corrigés**: 3
- **Rétrocompatibilité**: 100% (vue fiscal_invoices)

## ⚡ TL;DR

```sql
-- Copier-coller dans Supabase SQL Editor et cliquer Run
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_id TEXT;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid';
CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;
```

C'est tout ! 🎉
