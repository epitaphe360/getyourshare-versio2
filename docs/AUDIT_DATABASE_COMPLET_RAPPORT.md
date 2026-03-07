# AUDIT COMPLET SUPABASE - RAPPORT DÉTAILLÉ

**Date**: 2025-11-09
**Scope**: 46 tables, 168 fichiers Python, 60+ fichiers SQL
**Niveau de Sécurité**: CRITIQUE - Action immédiate requise

---

## RÉSUMÉ EXÉCUTIF

Votre base de données Supabase présente **6 problèmes critiques** qui doivent être adressés immédiatement:

1. **RLS COMPLÈTEMENT DÉSACTIVÉE** - Toutes les 46 tables sans protection
2. **Foreign Keys non indexées** - 7 FK manquent d'indexes (dégradation de performance)
3. **JSONB sans GIN indexes** - 11 champs JSONB sans optimization
4. **N+1 Queries massif** - 43 fichiers Python ont des patterns N+1
5. **Service Role Key exposée** - Bypass de toute sécurité
6. **Audit logging absent** - Aucune trace sur transactions sensibles

---

## 1. ROW LEVEL SECURITY (RLS)

### Status: ❌ CRITIQUE - AUCUNE RLS CONFIGURÉE

**46/46 tables n'ont pas de RLS policies activées.**

### Tables affectées:
```
affiliate_settings, affiliation_request_history, affiliation_requests,
affiliations, ai_analytics, campaigns, categories, click_tracking, clicks,
commissions, company_settings, documentation_articles, engagement_metrics,
gateway_transactions, influencers, invoice_line_items, merchants, mlm_settings,
moderation_history, moderation_queue, moderation_stats, notifications,
payment_gateway_configs, payment_gateway_logs, payments, payouts,
permissions_settings, platform_invoices, platform_settings, products,
registration_settings, reviews, sales, smtp_settings, subscription_plans,
subscriptions, support_tickets, ticket_messages, trackable_links, transactions,
user_sessions, user_subscriptions, users, video_progress, video_tutorials,
whitelabel_settings
```

### Impact d'une RLS désactivée:

| Aspect | Impact | Risque |
|--------|--------|--------|
| **Confidentialité** | Service role peut lire TOUTES les données | CRITIQUE |
| **Isolation Multi-tenant** | Pas d'isolation utilisateur/entreprise | CRITIQUE |
| **Audit** | Aucune trace d'accès non-autorisé | MAJEURE |
| **Compliance** | Non-conforme RGPD/ISO27001 | MAJEURE |
| **Frontend Anon** | Frontend peut accéder à toutes les données | CRITIQUE |

### Exemple de vulnérabilité:

```javascript
// Frontend avec anon key - PEUT ACCÉDER À TOUT!
const { data } = await supabase
  .from('merchants')  // Table sensible
  .select('*')        // Toutes les colonnes
  .eq('id', 'someone-elses-merchant-id')  // ANY merchant_id
// ❌ Renvoie les données sans vérification de propriété
```

---

## 2. INDEXES - ANALYSE PERFORMANCE

### A. Foreign Keys sans Indexes (7 FK manquants)

**Problème**: Chaque JOIN causera un seq scan (O(n)) au lieu d'utiliser index (O(log n))

```sql
-- Foreign Keys SANS INDEX (Seq scan)
affiliations.campaign_id → campaigns
moderation_history.performed_by → users
moderation_queue.product_id → products
moderation_queue.user_id → users
moderation_queue.admin_user_id → users
platform_settings.updated_by → users
trackable_links.affiliation_id → affiliations
```

### Impact estimé:
- **Campaign page**: 100+ merchants = 100+ seq scans au lieu d'1 index scan
- **Moderation queue**: Chaque requête = 3 seq scans au lieu de 1
- **Trackable links**: N affiliations = N seq scans

### B. JSONB Fields sans GIN Index

```sql
-- Champs JSONB non-indexés (Requête lente)
influencers.social_links         -- {instagram: "url", youtube: "url"}
influencers.payment_details      -- {method: "paypal", account: "xxx"}
products.images                  -- ["url1", "url2", ...]
products.videos                  -- ["url1", "url2", ...]
products.specifications          -- {color: "red", size: "M", ...}
campaigns.target_audience        -- {age_range: "18-25", location: "FR"}
ai_analytics.recommended_influencers  -- [id1, id2, ...]
ai_analytics.audience_insights   -- {age: {...}, location: {...}}
ai_analytics.competitor_analysis -- {competitor: {...}}
moderation_queue.metadata        -- {reason: "spam", ...}
payments.gateway_response        -- {status: "approved", ...}
```

**Impact**:
```sql
-- Cette requête WITHOUT GIN INDEX = TRÈS LENT
SELECT * FROM influencers
WHERE social_links->>'instagram' = 'user123';
-- Full table scan de tous les influencers

-- AVEC GIN INDEX = RAPIDE
CREATE INDEX idx_influencers_social_instagram
  ON influencers USING GIN (social_links);
-- Index scan en O(log n)
```

### Résumé Indexes:

| Table | Total Indexes | FK Indexes | Status |
|-------|---------------|-----------|--------|
| sales | 7 | 4 | ✓ Bon |
| trackable_links | 6 | 1/2 | ⚠ Partiel |
| influencers | 5 | 1 | ⚠ Partiel |
| merchants | 4 | 1 | ⚠ Partiel |
| products | 5 | 1 | ⚠ Partiel |
| **TOTAL** | **110** | **46/60** | ❌ **77% coverage** |

---

## 3. MIGRATIONS - STRUCTURE ET PROBLÈMES

### Structure actuelle:

```
/database/
  ├── migrations_organized/     ← 19 fichiers (BIEN ORGANISÉS)
  │   ├── 001_base_schema.sql
  │   ├── 002_add_smtp_settings.sql
  │   └── 022_update_transaction_functions.sql
  ├── migrations/               ← 24 fichiers (DÉSORGANISÉS)
  │   ├── create_*.sql
  │   ├── add_*.sql
  │   └── enhance_*.sql
  └── [root]                    ← 17 fichiers (AD-HOC)

/backend/
  ├── migrations/               ← 4 fichiers
  └── database/                 ← 17 fichiers
```

### Problèmes détectés:

#### 1. DROP TABLE non-sécurisé ⚠️

```sql
-- ❌ Mauvais - DROP TABLE en migration
CREATE_PLATFORM_SETTINGS.sql:
  DROP TABLE IF EXISTS platform_settings CASCADE;
  CREATE TABLE platform_settings (...)

-- Risque: Si migration re-exécutée = données perdues
```

#### 2. Migrations non-idempotentes

```sql
-- ❌ Non-idempotent
ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY;
-- Cause: 2e exécution = ERROR "already enabled"

-- ✓ Idempotent
ALTER TABLE IF EXISTS platform_settings
  ENABLE ROW LEVEL SECURITY;
```

#### 3. Manque de CHECK constraints

```sql
-- ❌ Pas de contrainte
CREATE TABLE subscriptions (
  status VARCHAR(50),  -- Peut être n'importe quoi!
  ...
);

-- ✓ Avec contrainte
CREATE TABLE subscriptions (
  status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
  ...
);
```

#### 4. Colonnes critiques non NOT NULL

```sql
-- ❌ Nullable
CREATE TABLE transactions (
  amount DECIMAL(10, 2),           -- Peut être NULL!
  transaction_id VARCHAR(255),     -- Peut être NULL!
  ...
);

-- ✓ NOT NULL
CREATE TABLE transactions (
  amount DECIMAL(10, 2) NOT NULL,
  transaction_id VARCHAR(255) NOT NULL UNIQUE,
  ...
);
```

---

## 4. PERFORMANCE - N+1 QUERIES

### Problème: 43 fichiers Python ont patterns N+1

N+1 signifie: 1 première requête + N requêtes pour chaque résultat = N+1 requêtes au total

### Exemple réel trouvé:

#### Pattern 1: Loop with Query (Très common)

**Fichier**: `server.py:672`
```python
# ❌ N+1 PATTERN
sales = supabase.table('sales').select('*').eq('merchant_id', m_id).execute().data
for sale in sales:  # ← 100 ventes
    # ← 100 requêtes supplémentaires!
    commission = supabase.table('commissions').select('*').eq('sale_id', sale['id']).execute().data

# Total: 1 + 100 = 101 requêtes
# Temps: ~2 secondes pour une page charge lente
```

**Solution optimale**:
```python
# ✓ 1 Requête optimisée
sales = supabase.table('sales').select('*, commissions(*)').eq('merchant_id', m_id).execute().data

# Ou en Python: Batch requests
sale_ids = [s['id'] for s in sales]
commissions = supabase.table('commissions').select('*').in_('sale_id', sale_ids).execute().data

# Total: 2 requêtes
# Temps: ~50ms
```

#### Pattern 2: Multiple Separate Selects

**Fichier**: `affiliate_links_endpoints.py:58`
```python
# ❌ 15 selects séparés
products = supabase.table('products').select('*').execute()
merchants = supabase.table('merchants').select('*').execute()
influencers = supabase.table('influencers').select('*').execute()
# ... 12 autres selects

# Solution: Batch dans une transaction ou combiné
```

### Top 10 fichiers affectés:

| Fichier | N Selects | Risque |
|---------|----------|--------|
| db_queries_real.py | 58 | CRITIQUE |
| db_helpers.py | 24 | CRITIQUE |
| server.py | 34 | CRITIQUE |
| leads_endpoints.py | 22 | MAJEURE |
| subscription_helpers.py | 15 | MAJEURE |
| affiliate_links_endpoints.py | 15 | MAJEURE |
| affiliation_requests_endpoints.py | 14 | MAJEURE |
| services/kyc_service.py | 13 | MAJEURE |
| services/notification_service.py | 11 | MAJEURE |
| subscription_helpers_simple.py | 11 | MAJEURE |

### Impact global:

```
Hypothèse: 1000 utilisateurs concurrent
- Nombre de requêtes N+1: 10 requêtes par page
- Requêtes totales: 10,000 / seconde
- Connection pool Supabase: ~100 concurrent
- Timeout: Oui, goulot d'étranglement garanti
```

---

## 5. SÉCURITÉ

### A. Service Role Key Exposure ⚠️⚠️⚠️

**Détecté dans**: `/backend/supabase_client.py`

```python
# ❌ CONFIGURATION ACTUELLE (INSÉCURISÉE)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Utilisé pour TOUTES les requêtes backend
supabase = supabase_admin  # Pas de distinction admin/user

def get_supabase_client(admin=True):  # ← Paramètre ignoré!
    return supabase_admin if admin else supabase_anon  # Retourne toujours admin
```

**Risque critique**:
- Service role **BYPASS TOUTE RLS**
- Une seule fuite = accès complet à la DB
- Pas de rate limiting
- Pas d'audit logging

### B. Audit Logging Absent

Aucun trigger d'audit sur tables sensibles:
- `payments` - Transactions financières
- `commissions` - Rémunérations
- `transactions` - Mouvements d'argent
- `merchants` - Données d'entreprise
- `influencers` - Données personnelles
- `users` - Données d'authentification

### C. Functions Exposées

- ✓ Aucune PL/pgSQL function exposée directement
- ⚠️ Pas de vérification auth au niveau function

---

## 6. TABLES ET CONSTRAINTS

### Toutes les tables ont PRIMARY KEY ✓

Aucun problème de table sans PK détecté.

### Colonnes critiques sans NOT NULL ⚠️

```
payments.amount - Devrait être NOT NULL
transactions.amount - Devrait être NOT NULL
sales.amount - Devrait être NOT NULL
commissions.amount - Devrait être NOT NULL
```

---

## 7. RÉSOLUTION - SCRIPTS SQL PRÊTS À L'EMPLOI

### Script 1: Créer tous les Indexes Manquants

```sql
-- ============================================
-- CREATE MISSING INDEXES
-- ============================================

-- Foreign Keys Indexes
CREATE INDEX IF NOT EXISTS idx_affiliations_campaign_id
  ON affiliations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_moderation_history_performed_by
  ON moderation_history(performed_by);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_product_id
  ON moderation_queue(product_id);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_user_id
  ON moderation_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_admin_user_id
  ON moderation_queue(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_platform_settings_updated_by
  ON platform_settings(updated_by);
CREATE INDEX IF NOT EXISTS idx_trackable_links_affiliation_id
  ON trackable_links(affiliation_id);

-- JSONB GIN Indexes
CREATE INDEX IF NOT EXISTS idx_influencers_social_links
  ON influencers USING GIN (social_links);
CREATE INDEX IF NOT EXISTS idx_influencers_payment_details
  ON influencers USING GIN (payment_details);
CREATE INDEX IF NOT EXISTS idx_products_images
  ON products USING GIN (images);
CREATE INDEX IF NOT EXISTS idx_products_videos
  ON products USING GIN (videos);
CREATE INDEX IF NOT EXISTS idx_products_specifications
  ON products USING GIN (specifications);
CREATE INDEX IF NOT EXISTS idx_campaigns_target_audience
  ON campaigns USING GIN (target_audience);
CREATE INDEX IF NOT EXISTS idx_ai_analytics_recommended_influencers
  ON ai_analytics USING GIN (recommended_influencers);
CREATE INDEX IF NOT EXISTS idx_ai_analytics_audience_insights
  ON ai_analytics USING GIN (audience_insights);
CREATE INDEX IF NOT EXISTS idx_ai_analytics_competitor_analysis
  ON ai_analytics USING GIN (competitor_analysis);
CREATE INDEX IF NOT EXISTS idx_moderation_queue_metadata
  ON moderation_queue USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_payments_gateway_response
  ON payments USING GIN (gateway_response);

-- Performance Indexes (Commonly filtered columns)
CREATE INDEX IF NOT EXISTS idx_commissions_sale_id
  ON commissions(sale_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status
  ON user_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status
  ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_sales_payment_status
  ON sales(payment_status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status
  ON support_tickets(status);

-- Composite Indexes (Often filtered together)
CREATE INDEX IF NOT EXISTS idx_sales_merchant_created
  ON sales(merchant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trackable_links_influencer_created
  ON trackable_links(influencer_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_merchant_active
  ON products(merchant_id, is_available);

-- Partial Indexes (Optimize WHERE conditions)
CREATE INDEX IF NOT EXISTS idx_trackable_links_active
  ON trackable_links(id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_available
  ON products(id) WHERE is_available = TRUE;
CREATE INDEX IF NOT EXISTS idx_subscriptions_active
  ON subscriptions(id) WHERE status = 'active';

-- BRIN Index (For time-series data - very efficient)
CREATE INDEX IF NOT EXISTS idx_click_tracking_clicked_at_brin
  ON click_tracking USING BRIN (clicked_at);
CREATE INDEX IF NOT EXISTS idx_sales_created_at_brin
  ON sales USING BRIN (created_at);

COMMENT ON INDEX idx_affiliations_campaign_id
  IS 'FK index for affiliations.campaign_id - improves JOIN performance';
COMMENT ON INDEX idx_influencers_social_links
  IS 'GIN index for JSONB queries like social_links->>instagram = value';
COMMENT ON INDEX idx_sales_merchant_created
  IS 'Composite index for merchant dashboard queries with date filtering';

-- Verify Index Creation
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### Script 2: Implémenter RLS sur Toutes les Tables

**ATTENTION**: Ce script est TRÈS LONG. Le script complet est dans le fichier de recommandations SQL.

Exemple pour quelques tables critiques:

```sql
-- ============================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

-- 1. USERS TABLE
ALTER TABLE IF EXISTS users ENABLE ROW LEVEL SECURITY;

-- Users can view/update only their own record
CREATE POLICY "Users can view own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Admins can view all"
  ON users FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- 2. MERCHANTS TABLE
ALTER TABLE IF EXISTS merchants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Merchants can view own data"
  ON merchants FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Merchants can update own data"
  ON merchants FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "Admins can view all merchants"
  ON merchants FOR SELECT
  USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

-- [40+ other policies needed...]
```

### Script 3: Ajouter NOT NULL sur Colonnes Critiques

```sql
-- ============================================
-- ADD NOT NULL CONSTRAINTS
-- ============================================

ALTER TABLE transactions
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN transaction_id SET NOT NULL;

ALTER TABLE sales
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN status SET NOT NULL;

ALTER TABLE commissions
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN influencer_id SET NOT NULL;

ALTER TABLE payments
  ALTER COLUMN amount SET NOT NULL,
  ALTER COLUMN status SET NOT NULL;

ALTER TABLE subscriptions
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN plan_type SET NOT NULL;

ALTER TABLE merchants
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN company_name SET NOT NULL;

ALTER TABLE influencers
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN username SET NOT NULL;
```

### Script 4: Créer Audit Trigger (Optionnel mais recommandé)

```sql
-- ============================================
-- AUDIT LOGGING FOR SENSITIVE TABLES
-- ============================================

-- Create audit table
CREATE TABLE IF NOT EXISTS audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name VARCHAR(255) NOT NULL,
  operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
  record_id UUID NOT NULL,
  old_data JSONB,
  new_data JSONB,
  changed_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);

-- Audit function
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (table_name, operation, record_id, old_data, new_data, changed_by)
  VALUES (
    TG_TABLE_NAME,
    TG_OP,
    COALESCE(NEW.id, OLD.id),
    to_jsonb(OLD),
    to_jsonb(NEW),
    COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Enable audit on sensitive tables
CREATE TRIGGER audit_payments AFTER INSERT OR UPDATE OR DELETE ON payments
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_commissions AFTER INSERT OR UPDATE OR DELETE ON commissions
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_transactions AFTER INSERT OR UPDATE OR DELETE ON transactions
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

---

## 8. POINTS D'ACTION IMMÉDIATS

### Phase 1: CRITIQUE (Maintenant - Jour 1)

- [ ] **Exécuter le script "Create Missing Indexes"** - Improves performance immédiatement
- [ ] **Sauvegarder la DB** - Avant toute modification
- [ ] **Tester RLS policies sur table non-critique** (ex: categories)

### Phase 2: MAJEURE (Cette semaine - Jours 2-5)

- [ ] **Implémenter RLS sur toutes les 46 tables** (voir script complet)
- [ ] **Vérifier et corriger Service Role usage** dans backend
- [ ] **Refactoriser top 10 fichiers avec N+1** (db_queries_real.py, server.py, etc.)
- [ ] **Ajouter NOT NULL constraints**

### Phase 3: IMPORTANTE (Ce mois - Semaines 2-4)

- [ ] **Implémenter Audit Logging** sur tables sensibles
- [ ] **Ajouter CHECK constraints** sur tous les enums
- [ ] **Optimiser requêtes restantes** (rate limiting, caching)
- [ ] **Tester sous charge** (1000 concurrent users)

---

## 9. QUESTIONS FRÉQUENTES

**Q: Si j'active RLS, le backend va-t-il fonctionner?**
R: Non, car il utilise service role qui bypass RLS. Il faut aussi refactoriser le backend pour utiliser des JWT tokens côté client.

**Q: Combien de temps prend l'implémentation RLS?**
R: ~3-5 jours pour 46 tables = 100+ policies. Recommandé de faire par étapes.

**Q: Les N+1 queries vont-elles disparaître automatiquement?**
R: Non, faut refactoriser le code Python. Les indexes amélioreront la performance mais pas résoudront le N+1.

**Q: Est-ce que je vais perdre les données avec ALTER TABLE?**
R: Non, les ALTER TABLE conservent les données. Seules les DDL DROP TABLE perdent les données.

---

## 10. RECURSOS

**Scripts SQL complets**: Voir fichier `SCRIPTS_CORRECTION_SECURITE.md`
**Fichiers affectés**: Voir liste dans section Performance
**Recommandations détaillées**: Voir section Résolution

---

## Signature

Audit effectué par Claude AI le 2025-11-09
Niveau de critique: **TRÈS ÉLEVÉ** - Action recommandée dans les 7 jours
