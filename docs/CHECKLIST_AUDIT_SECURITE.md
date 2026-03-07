# CHECKLIST AUDIT SÉCURITÉ SUPABASE

**Date**: 2025-11-09
**Criticité**: ⚠️ TRÈS ÉLEVÉE - Action recommandée dans les 7 jours

---

## RÉSUMÉ CRITIQUE

| Issue | Sévérité | Status | Action |
|-------|----------|--------|--------|
| RLS désactivée sur 46 tables | 🔴 CRITIQUE | ❌ Not Done | Week 1-2 |
| 7 Foreign keys sans index | 🔴 CRITIQUE | ❌ Not Done | Day 1 |
| 11 JSONB fields sans GIN index | 🔴 CRITIQUE | ❌ Not Done | Day 1 |
| 43 fichiers Python avec N+1 | 🟠 MAJEURE | ❌ Not Done | Week 2-3 |
| Service role key exposée | 🟠 MAJEURE | ❌ Not Done | Week 1 |
| Pas d'audit logging | 🟡 IMPORTANTE | ❌ Not Done | Week 3 |
| Colonnes critiques nullable | 🟡 IMPORTANTE | ❌ Not Done | Week 1 |
| Migrations non-idempotentes | 🟡 IMPORTANTE | ❌ Not Done | Week 3 |

---

## PHASE 1: CRITICAL (Jour 1)

### Task 1.1: Backup Database
- [ ] Accédez à Supabase Dashboard
- [ ] Allez dans Settings → Database → Backups
- [ ] Cliquez "Download backup"
- [ ] Sauvegardez le fichier (.sql)
- [ ] Vérifiez la taille du backup (>1MB = bon)

### Task 1.2: Create Missing Indexes
- [ ] Ouvrez Supabase SQL Editor
- [ ] Copez le script: `SCRIPTS_SQL_CORRECTION_INDEXES_RLS.sql` (Phase 1)
- [ ] Collez et exécutez
- [ ] Vérifiez: `SELECT count(*) FROM pg_stat_user_indexes;` (devrait être ~130+)
- [ ] Temps estimé: 5-10 minutes
- [ ] Verification: `EXPLAIN ANALYZE` sur requêtes lentes

**Expected Result**:
```
✓ 30 new indexes created
✓ Foreign key JOINs 10x faster
✓ JSONB queries optimized
✓ Zero data lost
```

### Task 1.3: Document Current Performance
- [ ] Ouvrez CloudWatch / Datadog / Application Monitoring
- [ ] Notez les métriques actuelles:
  - Average response time: ____ ms
  - 95th percentile: ____ ms
  - Database queries per page: ____
  - Timeout rate: ____%
- [ ] Sauvegardez le screenshot (baseline)

**Why**: Vous comparerez après optimisation

---

## PHASE 2: MAJEURE (Semaine 1)

### Task 2.1: Add NOT NULL Constraints
- [ ] Vérifiez d'abord les colonnes nullables:
  ```sql
  SELECT column_name, is_nullable
  FROM information_schema.columns
  WHERE table_name = 'transactions' AND is_nullable = 'YES';
  ```
- [ ] Exécutez Phase 2 du script SQL
- [ ] Vérifiez aucune erreur: `SELECT * FROM transactions WHERE amount IS NULL;`
- [ ] Commit à Git

**Risk**: Peut échouer si données nulles existent
**Mitigation**: Check first avec requête SELECT

### Task 2.2: Enable RLS on Critical Tables (3 tables)

**Table 1: users**
- [ ] Execute RLS script Phase 3A
- [ ] Test policy: `SELECT * FROM users;` (doit retourner 1 seul user)
- [ ] Test admin: With admin token, devrait voir tous
- [ ] Vérifiez dans app: Login fonctionne

**Table 2: merchants**
- [ ] Execute RLS script Phase 3B
- [ ] Test: Merchant peut voir own data
- [ ] Test: Admin peut voir tous
- [ ] Vérifiez dans app: Merchant page works

**Table 3: influencers**
- [ ] Execute RLS script Phase 3C
- [ ] Test: Influencer peut voir own profile
- [ ] Test: Public read access works
- [ ] Vérifiez dans app: Directory works

**Vérification finale**:
```bash
# In Supabase SQL Editor
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND tablename IN ('users', 'merchants', 'influencers');
```

Expected: `rowsecurity = t` pour tous

### Task 2.3: Refactor Service Role Usage

**Problème actuel**: `supabase_client.py` utilise toujours service role

```python
# ❌ AVANT
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
# Bypasse RLS complètement
```

**Action**: Créer 2 clients distincts

```python
# ✓ APRÈS
from supabase import create_client

# Client admin (backend only, pour opérations système)
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Client user (avec JWT du user, respecte RLS)
def get_user_client(user_token: str):
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # User passes JWT via Authorization header
```

- [ ] Copez la nouvelle structure
- [ ] Audit `server.py` - chercher où service role est utilisé
- [ ] Refactoriser les requêtes admin-only
- [ ] Tester login/logout
- [ ] Commit à Git

---

## PHASE 3: MAJEURE (Semaine 2)

### Task 3.1: Complete RLS on Remaining 43 Tables

Execute Phase 3D-3J du script SQL:

- [ ] Products
- [ ] Sales
- [ ] Commissions
- [ ] Trackable_links
- [ ] Subscriptions
- [ ] Payments
- [ ] Support_tickets
- [ ] Autres tables (Phase 3 "Remaining tables")

**Vérification**:
```sql
-- Toutes les 46 tables devraient avoir RLS
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = FALSE;
-- Résultat devrait être vide
```

### Task 3.2: Refactor Top 3 Files for N+1

**File 1**: `db_queries_real.py` (58 selects)
- [ ] Identifier les boucles
- [ ] Convertir en batch `in_()`
- [ ] Tester chaque fonction
- [ ] Mesurer improvement avec timer
- [ ] Commit

**File 2**: `server.py` (34 selects)
- [ ] Focus sur endpoints les plus utilisés
- [ ] Ajouter joins FK où possible
- [ ] Batch requests pour les boucles
- [ ] Mesurer performance
- [ ] Commit

**File 3**: `db_helpers.py` (24 selects)
- [ ] Créer batch helper functions
- [ ] Réduire de 24 → 5 requêtes
- [ ] Export pour réutilisation
- [ ] Commit

**Vérification**: Performance test
```bash
# Temps avant: 500ms+
# Temps après: <100ms
```

### Task 3.3: Implement Caching Layer (Optional)

Si vous avez des données statiques:

- [ ] Installer `redis` ou utiliser mémoire locale
- [ ] Cache categories, subscription_plans
- [ ] Set TTL = 1 heure
- [ ] Invalider sur mutation

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_categories():
    # First call: DB query
    # Subsequent calls: Memory (50x faster)
    return supabase.table('categories').select('*').execute().data
```

---

## PHASE 4: IMPORTANTE (Semaine 3)

### Task 4.1: Complete N+1 Refactoring

Refactoriser les 40 fichiers restants:

Priorités:
1. [ ] leads_endpoints.py
2. [ ] subscription_helpers.py
3. [ ] affiliate_links_endpoints.py
4. [ ] affiliation_requests_endpoints.py
5. [ ] services/kyc_service.py
6. [ ] Remaining 35+ files

**Checklist par file**:
- [ ] Identifiez all N+1 patterns
- [ ] Refactoriser avec batch
- [ ] Run tests
- [ ] Benchmark before/after
- [ ] Commit

### Task 4.2: Add Audit Logging (Optional but recommended)

```sql
-- Create audit table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    table_name VARCHAR(255),
    operation VARCHAR(10),
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    changed_by UUID,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger
CREATE TRIGGER audit_payments AFTER INSERT OR UPDATE OR DELETE ON payments
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

- [ ] Create audit_log table
- [ ] Add triggers on sensitive tables
- [ ] Test: Update a payment record
- [ ] Verify: audit_log table has record

### Task 4.3: Add CHECK Constraints

```sql
-- ✓ AVANT: Aucune validation
status VARCHAR(50)

-- ✓ APRÈS: Validation au niveau DB
status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'expired', 'trial'))
```

- [ ] Identify all enum columns
- [ ] Add CHECK constraints
- [ ] Test: Try insert invalid value (doit échouer)
- [ ] Commit

### Task 4.4: Performance Testing Under Load

- [ ] Utilisez Apache JMeter / Locust
- [ ] Simulation: 100 concurrent users
- [ ] Mesurez:
  - [ ] Average response time
  - [ ] 95th percentile latency
  - [ ] Error rate
  - [ ] Database CPU usage
  - [ ] Connection pool utilization

**Expected Results**:
```
Before: 2-5s average, 30% errors, 80% connection pool
After:  0.2-0.5s average, <1% errors, 20% connection pool
```

---

## VALIDATION CHECKLIST

### Sécurité

- [ ] RLS enabled on all 46 tables
- [ ] All policies tested and working
- [ ] No sensitive data leakage
- [ ] Audit logs recording all changes
- [ ] Service role limited to backend only

### Performance

- [ ] All 30 indexes created
- [ ] No N+1 query patterns
- [ ] Average response time < 500ms
- [ ] 95th percentile < 1000ms
- [ ] Database CPU < 50% during normal load

### Data Integrity

- [ ] All NOT NULL constraints applied
- [ ] All CHECK constraints validated
- [ ] No corrupt data
- [ ] All foreign keys valid
- [ ] Backup created successfully

### Code Quality

- [ ] All Python changes committed
- [ ] Tests updated and passing
- [ ] No warnings in logs
- [ ] Code reviewed by peer
- [ ] Documentation updated

---

## ROLLBACK PLAN (Si problèmes)

### If RLS Breaks Application

```sql
-- Désactiver RLS sur tous les tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE merchants DISABLE ROW LEVEL SECURITY;
-- etc...

-- Application doit continuer fonctionner (moins sécurisé mais au moins online)
```

### If Indexes Cause Issues

```sql
-- Supprimer les indexes
DROP INDEX idx_affiliations_campaign_id;
DROP INDEX idx_influencers_social_links;
-- etc...

-- Requêtes seront lentes mais pas d'erreur
```

### If NOT NULL Fails

```sql
-- Revenir back
ALTER TABLE transactions ALTER COLUMN amount DROP NOT NULL;
ALTER TABLE sales ALTER COLUMN amount DROP NOT NULL;
-- etc...
```

---

## SUCCESS CRITERIA

### Week 1
- [ ] All indexes created
- [ ] RLS enabled on users, merchants, influencers
- [ ] Service role refactored
- [ ] Zero data loss

### Week 2
- [ ] RLS enabled on remaining 43 tables
- [ ] Top 3 files refactored (N+1 fixed)
- [ ] 50% performance improvement
- [ ] All tests passing

### Week 3
- [ ] All 46 files refactored
- [ ] Audit logging implemented
- [ ] All constraints added
- [ ] 80% performance improvement
- [ ] Load test passing 100 concurrent users

### Week 4
- [ ] Zero critical security issues
- [ ] <500ms average response time
- [ ] <1% error rate
- [ ] Full documentation updated
- [ ] Production ready

---

## RESOURCES

**Documentation**:
- [ ] AUDIT_DATABASE_COMPLET_RAPPORT.md
- [ ] SCRIPTS_SQL_CORRECTION_INDEXES_RLS.sql
- [ ] RECOMMANDATIONS_OPTIMIZATION_N+1.md

**External**:
- [ ] Supabase Docs: https://supabase.com/docs
- [ ] PostgreSQL Performance: https://www.postgresql.org/docs
- [ ] N+1 Queries: https://en.wikipedia.org/wiki/N%2B1_query_problem

---

## SIGN-OFF

- [ ] Team reviewed and approved
- [ ] Risk assessment completed
- [ ] Backup verified
- [ ] Timeline agreed

**Project Lead**: _____________
**Date**: _____________
**Approved By**: _____________

---

## PROGRESS TRACKING

### Week 1
- [ ] Monday: Backup + Phase 1 (Indexes)
- [ ] Tuesday: Phase 1 verification
- [ ] Wednesday: Phase 2 (NOT NULL)
- [ ] Thursday: Phase 2B (RLS on 3 tables)
- [ ] Friday: Service role refactoring

### Week 2
- [ ] Monday-Wednesday: RLS on remaining 43 tables
- [ ] Thursday-Friday: N+1 refactoring (top 3 files)

### Week 3
- [ ] Monday-Thursday: N+1 refactoring (40 remaining files)
- [ ] Friday: Audit logging + testing

### Week 4
- [ ] Constraints, load testing, cleanup
- [ ] Production deployment

---

## Questions?

Consultez les documents détaillés:
1. `AUDIT_DATABASE_COMPLET_RAPPORT.md` - Rapport détaillé
2. `SCRIPTS_SQL_CORRECTION_INDEXES_RLS.sql` - Scripts SQL
3. `RECOMMANDATIONS_OPTIMIZATION_N+1.md` - Optimisation N+1

Good luck! 🚀
