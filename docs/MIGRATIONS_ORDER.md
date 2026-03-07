# 🔧 ORDRE D'EXÉCUTION MIGRATIONS SQL

## ⚠️ IMPORTANT: Exécuter dans cet ordre exact

Les migrations doivent être appliquées **séquentiellement** via Supabase Dashboard → SQL Editor.

---

## 📋 Migrations Système Fiscal

### ✅ Migration 010 - Base Système Fiscal
**Fichier:** `backend/migrations/010_fiscal_system_simple.sql`

**Contenu:**
- 7 tables fiscales principales
- Taux TVA pré-remplis (MA/FR/US)
- Index optimisation
- Triggers updated_at

**Statut:** ✅ **APPLIQUÉE**

---

### ✅ Migration 013 - Colonnes Paiement
**Fichier:** `backend/migrations/013_add_payment_columns.sql`

**Contenu:**
- Colonnes payment_id, payment_status, etc.
- Tables bank_reconciliations
- Tables payment_links
- Index paiements

**Statut:** ✅ **APPLIQUÉE**

---

### ✅ Migration 014 - Fix fiscal_invoices Vue
**Fichier:** `backend/migrations/014_fix_fiscal_invoices_view.sql`

**Contenu:**
- DROP TABLE fiscal_invoices (si existe)
- Ajout colonnes manquantes invoices
- CREATE VIEW fiscal_invoices
- Contraintes validation

**Statut:** ✅ **APPLIQUÉE**

**Erreurs corrigées:**
- ✅ Syntaxe `ADD CONSTRAINT IF NOT EXISTS` → bloc `DO $$`
- ✅ Table fiscal_invoices (TABLE → VUE)

---

### ⏳ Migration 015 - RLS Policies Hardening
**Fichier:** `backend/migrations/015_rls_policies_hardening.sql`

**Contenu:**
- Suppression anciennes policies permissives
- Nouvelles policies STRICT multi-tenancy
- Fonction check_fiscal_access()
- Trigger prevent_paid_invoice_modification
- Audit logs automatiques

**Dépendances:**
- ⚠️ Requiert `sales_assignments` pour policy commercial
- ✅ Gère absence table avec bloc conditionnel

**Statut:** ⏳ **À APPLIQUER APRÈS 016**

---

### ⏳ Migration 016 - Sales Assignments
**Fichier:** `backend/migrations/016_create_sales_assignments.sql`

**Contenu:**
- Table sales_assignments
- RLS policies assignations
- Auto-assignation commerciaux
- Policy commercial_invoices_assigned

**Statut:** ⏳ **À APPLIQUER MAINTENANT**

---

## 🚀 PROCÉDURE D'APPLICATION

### Option A: Via Supabase Dashboard (Recommandé)

```
1. Ouvrir: https://supabase.com/dashboard/project/YOUR_PROJECT/sql

2. Copier-coller contenu de:
   ✅ 010_fiscal_system_simple.sql      → Run ✅
   ✅ 013_add_payment_columns.sql       → Run ✅
   ✅ 014_fix_fiscal_invoices_view.sql  → Run ✅
   ⏳ 016_create_sales_assignments.sql  → Run (MAINTENANT)
   ⏳ 015_rls_policies_hardening.sql    → Run (APRÈS 016)

3. Vérifier succès messages:
   ✅ "Query executed successfully"
   ✅ Notices PostgreSQL (RAISE NOTICE)
```

### Option B: Via psql (Alternatif)

```powershell
# Configurer DATABASE_URL
$env:DATABASE_URL = "postgresql://user:pass@host:5432/db"

# Appliquer migrations
psql $env:DATABASE_URL -f backend\migrations\016_create_sales_assignments.sql
psql $env:DATABASE_URL -f backend\migrations\015_rls_policies_hardening.sql
```

---

## ✅ VÉRIFICATIONS POST-MIGRATION

### 1. Tables créées

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
  'invoices',
  'fiscal_settings',
  'vat_declarations',
  'withholding_tax',
  'accounting_exports',
  'bank_reconciliations',
  'payment_links',
  'sales_assignments'
)
ORDER BY table_name;
```

**Attendu:** 8 tables

---

### 2. Vue fiscal_invoices

```sql
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_name = 'fiscal_invoices';
```

**Attendu:** `table_type = 'VIEW'`

---

### 3. Colonnes paiement

```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name IN (
  'payment_id',
  'payment_status',
  'stripe_payment_intent_id',
  'paypal_order_id'
)
ORDER BY column_name;
```

**Attendu:** 4 colonnes

---

### 4. RLS activé

```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('invoices', 'sales_assignments', 'fiscal_settings')
ORDER BY tablename;
```

**Attendu:** `rowsecurity = true` pour toutes

---

### 5. Policies créées

```sql
SELECT tablename, policyname 
FROM pg_policies 
WHERE tablename IN ('invoices', 'sales_assignments')
ORDER BY tablename, policyname;
```

**Attendu:** 
- invoices: 4 policies (admin, merchant, influencer, commercial)
- sales_assignments: 3 policies (admin, commercial, merchant)

---

## 🐛 DÉPANNAGE

### Erreur: "relation sales_assignments does not exist"

**Solution:**
```sql
-- Appliquer d'abord migration 016
-- Fichier: 016_create_sales_assignments.sql
-- Puis migration 015
```

---

### Erreur: "syntax error at or near IF NOT EXISTS"

**Cause:** PostgreSQL ne supporte pas `ADD CONSTRAINT IF NOT EXISTS`

**Solution:** Déjà corrigée dans migrations 014 et 015 (bloc `DO $$`)

---

### Erreur: "fiscal_invoices is not a view"

**Cause:** fiscal_invoices existe comme TABLE au lieu de VUE

**Solution:** Migration 014 fait `DROP TABLE` puis `CREATE VIEW`

---

### Erreur: "duplicate key value violates unique constraint"

**Cause:** Données test déjà insérées

**Solution:** Bloc `ON CONFLICT DO NOTHING` gère automatiquement

---

## 📊 ÉTAT ACTUEL

```
Migration 010: ✅ Appliquée
Migration 013: ✅ Appliquée  
Migration 014: ✅ Appliquée
Migration 016: ⏳ À appliquer (MAINTENANT)
Migration 015: ⏳ À appliquer (APRÈS 016)
```

---

## 🎯 PROCHAINE ÉTAPE

**Copier-coller dans Supabase SQL Editor:**

1. `backend/migrations/016_create_sales_assignments.sql`
2. Cliquer **Run**
3. Attendre succès ✅
4. Puis `backend/migrations/015_rls_policies_hardening.sql`
5. Cliquer **Run**
6. ✅ **Système à 100% !**

---

## 📞 Support

Si erreurs persistent:
- Vérifier logs PostgreSQL dans Supabase Dashboard
- Vérifier que users table existe avec colonne `role`
- Vérifier connexion DATABASE_URL correcte

**Fichiers migrations:** `backend/migrations/*.sql`
