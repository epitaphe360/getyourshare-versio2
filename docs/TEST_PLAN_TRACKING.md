# ✅ Plan de Tests - Système de Tracking Commercial

## 📋 Vue d'ensemble

Plan de tests complet pour valider le système de tracking des ventes commerciales.

---

## 🧪 Tests Base de Données

### Test 1: Création de la table services_leads

```sql
-- Vérifier que la table existe
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'services_leads'
);

-- Vérifier les colonnes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'services_leads';

-- Test: Créer un lead
INSERT INTO services_leads (
    commercial_id, company_name, contact_name, 
    contact_email, estimated_value, status
)
VALUES (
    (SELECT id FROM users WHERE role = 'commercial' LIMIT 1),
    'Test Corp', 'John Doe', 'john@test.com', 5000, 'nouveau'
)
RETURNING *;
```

**Résultat attendu:** ✅ Lead créé + lien affilié auto-généré

---

### Test 2: Génération automatique de lien (Trigger)

```sql
-- Insérer un lead et vérifier le trigger
INSERT INTO services_leads (
    commercial_id, company_name, contact_name, contact_email
)
VALUES (
    (SELECT id FROM users WHERE role = 'commercial' LIMIT 1),
    'Auto Test Corp', 'Jane Doe', 'jane@autotest.com'
)
RETURNING id;

-- Vérifier qu'un lien a été créé automatiquement
SELECT * FROM commercial_tracking_links 
WHERE lead_id = (SELECT id FROM services_leads WHERE contact_email = 'jane@autotest.com');
```

**Résultat attendu:** ✅ Lien créé automatiquement avec code unique

---

### Test 3: Fonction de génération manuelle

```sql
-- Tester génération manuelle de lien
SELECT * FROM generate_commercial_tracking_link(
    (SELECT id FROM users WHERE role = 'commercial' LIMIT 1),
    NULL,
    'test_campaign_manual'
);
```

**Résultat attendu:** ✅ 
- tracking_link_id: UUID
- unique_code: COM-XXXXX-XXXXXX
- full_url: https://getyourshare.ma/pricing?ref=...
- short_url: https://gys.ma/...

---

### Test 4: Tracking de clic

```sql
-- Récupérer un code de tracking existant
DO $$
DECLARE
    test_code VARCHAR;
BEGIN
    SELECT unique_code INTO test_code 
    FROM commercial_tracking_links 
    LIMIT 1;
    
    -- Tracker un clic
    PERFORM track_commercial_click(test_code, '192.168.1.100', 'Mozilla/5.0');
    
    -- Vérifier l'incrémentation
    RAISE NOTICE 'Clicks après tracking: %', (
        SELECT clicks FROM commercial_tracking_links WHERE unique_code = test_code
    );
END $$;
```

**Résultat attendu:** ✅ Compteur clicks incrémenté + last_clicked_at mis à jour

---

### Test 5: RLS (Row Level Security)

```sql
-- Test: Commercial 1 ne voit pas les leads de Commercial 2
SET ROLE commercial_user_1;

-- Doit retourner uniquement SES leads
SELECT COUNT(*) FROM services_leads;

-- Ne doit PAS voir les liens d'un autre commercial
SELECT COUNT(*) FROM commercial_tracking_links 
WHERE commercial_id != (SELECT id FROM users WHERE email = current_user);
```

**Résultat attendu:** ✅ COUNT = 0 (pas d'accès aux données d'autres commerciaux)

---

### Test 6: Contraintes uniques

```sql
-- Test: Empêcher doublons email par commercial
INSERT INTO services_leads (
    commercial_id, company_name, contact_name, contact_email
)
VALUES (
    (SELECT id FROM users WHERE role = 'commercial' LIMIT 1),
    'Duplicate Corp', 'Test User', 'duplicate@test.com'
);

-- Essayer d'insérer le même email pour le même commercial
INSERT INTO services_leads (
    commercial_id, company_name, contact_name, contact_email
)
VALUES (
    (SELECT id FROM users WHERE role = 'commercial' LIMIT 1),
    'Duplicate Corp 2', 'Test User 2', 'duplicate@test.com'
);
```

**Résultat attendu:** ❌ ERROR: duplicate key value violates constraint "unique_email_per_commercial"

---

### Test 7: Vues statistiques

```sql
-- Test: Vue commercial_tracking_stats
SELECT * FROM commercial_tracking_stats LIMIT 5;

-- Test: Vue commercial_leads_enriched_stats
SELECT * FROM commercial_leads_enriched_stats LIMIT 5;
```

**Résultat attendu:** ✅ Données agrégées correctes avec toutes les colonnes

---

## 🔌 Tests API Backend

### Test 8: Endpoint - Générer lien affilié

```bash
curl -X POST http://localhost:8000/api/commercial/tracking/generate-link \
  -H "Authorization: Bearer YOUR_COMMERCIAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"campaign": "test_api"}'
```

**Résultat attendu:**
```json
{
  "success": true,
  "data": {
    "tracking_link_id": "uuid",
    "unique_code": "COM-XXXXX-XXXXXX",
    "full_url": "https://getyourshare.ma/pricing?ref=...",
    "short_url": "https://gys.ma/..."
  }
}
```

---

### Test 9: Endpoint - Lister les liens

```bash
curl -X GET "http://localhost:8000/api/commercial/tracking/links?active_only=true" \
  -H "Authorization: Bearer YOUR_COMMERCIAL_TOKEN"
```

**Résultat attendu:**
```json
{
  "success": true,
  "data": {
    "links": [...],
    "total": 10,
    "stats": {
      "total_clicks": 234,
      "total_conversions": 12,
      "conversion_rate": 5.13,
      "total_commission": 2400.00
    }
  }
}
```

---

### Test 10: Endpoint - Tracker clic (PUBLIC)

```bash
# Redirection automatique
curl -L http://localhost:8000/api/track/COM-JOHN-A3F2D9
```

**Résultat attendu:** 
- Status: 302 Redirect
- Location: https://getyourshare.ma/pricing?ref=COM-JOHN-A3F2D9
- Compteur clicks incrémenté en BDD

---

### Test 11: Endpoint - Statistiques

```bash
curl -X GET "http://localhost:8000/api/commercial/tracking/stats?period=30d" \
  -H "Authorization: Bearer YOUR_COMMERCIAL_TOKEN"
```

**Résultat attendu:**
```json
{
  "success": true,
  "data": {
    "total_links": 15,
    "active_links": 12,
    "total_clicks": 456,
    "total_conversions": 23,
    "conversion_rate": 5.04,
    "total_revenue": 15600.00,
    "total_commission": 3120.00,
    "top_performing_links": [...]
  }
}
```

---

### Test 12: Endpoint - Créer code promo

```bash
curl -X POST http://localhost:8000/api/commercial/promo-codes \
  -H "Authorization: Bearer YOUR_COMMERCIAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "TESTPROMO20",
    "discount_type": "percentage",
    "discount_value": 20,
    "max_usage": 50
  }'
```

**Résultat attendu:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "code": "TESTPROMO20",
    "discount_type": "percentage",
    "discount_value": 20,
    "is_active": true
  }
}
```

---

### Test 13: Endpoint - Lister commissions

```bash
curl -X GET "http://localhost:8000/api/commercial/commissions?status=all" \
  -H "Authorization: Bearer YOUR_COMMERCIAL_TOKEN"
```

**Résultat attendu:**
```json
{
  "success": true,
  "data": {
    "commissions": [...],
    "summary": {
      "total_pending": 1240.00,
      "total_approved": 3600.00,
      "total_paid": 8900.00,
      "count_pending": 7,
      "count_approved": 18,
      "count_paid": 45
    }
  }
}
```

---

## 🎨 Tests Frontend

### Test 14: Composant - Générateur de liens

**Actions:**
1. Ouvrir `/dashboard/commercial/tracking`
2. Cliquer sur onglet "Générer"
3. Entrer campagne "test_ui"
4. Cliquer "Générer le lien"
5. Copier le lien généré
6. Ouvrir le lien dans nouvel onglet

**Résultat attendu:**
- ✅ Lien généré en < 2 secondes
- ✅ Toast "Lien généré !"
- ✅ 3 champs affichés (code, full_url, short_url)
- ✅ Boutons copie fonctionnels
- ✅ Redirection vers pricing page

---

### Test 15: Composant - Table des liens

**Actions:**
1. Aller sur onglet "Mes liens"
2. Vérifier statistiques en haut
3. Scroller la table
4. Cliquer "Copier" sur un lien

**Résultat attendu:**
- ✅ Stats affichées (clics, conversions, taux, commission)
- ✅ Table avec toutes les colonnes
- ✅ Badge campagne visible
- ✅ Copie lien fonctionne
- ✅ Toast "Copié !"

---

### Test 16: Composant - Tableau commissions

**Actions:**
1. Aller sur onglet "Commissions"
2. Vérifier résumé (pending, approved, paid)
3. Vérifier table historique
4. Vérifier badges statut

**Résultat attendu:**
- ✅ 3 cartes résumé avec montants
- ✅ Table historique avec toutes colonnes
- ✅ Badges colorés selon statut
- ✅ Tri par date (plus récent en haut)

---

### Test 17: Responsive Design

**Actions:**
1. Ouvrir sur mobile (375px)
2. Tester tous les composants
3. Vérifier tables scrollables
4. Tester dark mode

**Résultat attendu:**
- ✅ Composants empilés verticalement
- ✅ Tables scroll horizontal
- ✅ Boutons accessibles
- ✅ Dark mode correct

---

## 🔄 Tests End-to-End

### Test 18: Workflow complet

**Scénario:**
1. Commercial crée un lead "E-commerce Test"
2. Système auto-génère un lien affilié
3. Commercial copie le lien
4. Prospect clique sur le lien
5. Prospect s'inscrit avec plan Pro
6. Système attribue la vente au commercial
7. Commercial voit sa commission

**Steps détaillés:**

```bash
# 1. Créer le lead
curl -X POST http://localhost:8000/api/commercial/leads \
  -H "Authorization: Bearer COMMERCIAL_TOKEN" \
  -d '{
    "company_name": "E-commerce Test",
    "contact_name": "Prospect Test",
    "contact_email": "prospect@test.com",
    "estimated_value": 800
  }'

# 2. Récupérer le lien auto-généré
curl -X GET http://localhost:8000/api/commercial/tracking/links \
  -H "Authorization: Bearer COMMERCIAL_TOKEN"

# 3. Simuler clic sur lien
curl -L http://localhost:8000/api/track/COM-XXXXX-XXXXXX

# 4. Vérifier incrémentation clicks
# (vérifier en BDD ou via API stats)

# 5. Simuler inscription (via API users ou UI)
# 6. Vérifier attribution dans subscription_attributions
# 7. Vérifier commission visible dans dashboard
```

**Résultat attendu:**
- ✅ Lead créé avec ID
- ✅ Lien auto-généré visible immédiatement
- ✅ Clic enregistré (compteur +1)
- ✅ Inscription attribuée au commercial
- ✅ Commission calculée automatiquement
- ✅ Visible dans dashboard commissions

---

### Test 19: Multi-touch Attribution

**Scénario:**
1. Prospect clique sur lien Commercial A
2. Prospect clique sur lien Commercial B
3. Prospect s'inscrit
4. Système attribue selon règle (last_touch)

**Résultat attendu:**
- ✅ Vente attribuée à Commercial B (last touch)
- ✅ Attribution_type = 'last_touch'

---

## 📊 Tests de Performance

### Test 20: Requêtes lourdes

```sql
-- Test: Dashboard avec 10 000 leads
EXPLAIN ANALYZE
SELECT * FROM commercial_leads_enriched_stats
WHERE commercial_id = 'test-uuid';

-- Test: 1 000 liens affiliés
EXPLAIN ANALYZE
SELECT * FROM commercial_tracking_links
WHERE commercial_id = 'test-uuid'
ORDER BY created_at DESC
LIMIT 50;
```

**Résultat attendu:**
- ✅ Temps < 100ms grâce aux index
- ✅ Index scan (pas seq scan)

---

### Test 21: Charge concurrente

```bash
# Tester 100 clics simultanés
for i in {1..100}; do
  curl http://localhost:8000/api/track/COM-XXXXX-XXXXXX &
done
wait
```

**Résultat attendu:**
- ✅ 100 clics enregistrés
- ✅ Pas de perte de données
- ✅ Temps réponse < 500ms

---

## 🔒 Tests de Sécurité

### Test 22: RLS - Commercial ne voit pas autres données

```bash
# Commercial 1 essaie d'accéder aux liens de Commercial 2
curl -X GET http://localhost:8000/api/commercial/tracking/links \
  -H "Authorization: Bearer COMMERCIAL_1_TOKEN"

# Vérifier que seuls SES liens apparaissent
```

**Résultat attendu:**
- ✅ Uniquement liens du commercial connecté
- ✅ Pas de fuite de données

---

### Test 23: Validation inputs

```bash
# Test injection SQL
curl -X POST http://localhost:8000/api/commercial/tracking/generate-link \
  -H "Authorization: Bearer COMMERCIAL_TOKEN" \
  -d '{"campaign": "test'; DROP TABLE commercial_tracking_links;--"}'
```

**Résultat attendu:**
- ✅ Erreur de validation
- ✅ Table pas supprimée
- ✅ Log d'alerte créé

---

### Test 24: Rate limiting

```bash
# Tester 1000 requêtes en 1 minute
for i in {1..1000}; do
  curl http://localhost:8000/api/commercial/tracking/generate-link \
    -H "Authorization: Bearer COMMERCIAL_TOKEN" \
    -X POST
done
```

**Résultat attendu:**
- ✅ Après 100 requêtes: HTTP 429 (Too Many Requests)
- ✅ Retry-After header présent

---

## 📝 Checklist Finale

### Base de données
- [ ] Table services_leads créée
- [ ] Table commercial_tracking_links créée
- [ ] Table promo_codes créée
- [ ] Table subscription_attributions créée
- [ ] Table tasks créée
- [ ] Toutes fonctions créées
- [ ] Trigger auto-génération actif
- [ ] 20+ index créés
- [ ] RLS activé sur toutes tables
- [ ] Vues statistiques fonctionnelles

### Backend
- [ ] Endpoint générer lien
- [ ] Endpoint lister liens
- [ ] Endpoint tracker clic (PUBLIC)
- [ ] Endpoint stats
- [ ] Endpoint codes promo
- [ ] Endpoint commissions
- [ ] Tous endpoints authentifiés sauf /track
- [ ] Validation inputs
- [ ] Gestion erreurs

### Frontend
- [ ] Composant AffiliateLinksGenerator
- [ ] Composant AffiliateLinksTable
- [ ] Composant CommissionsTable
- [ ] Page tracking complète
- [ ] Navigation ajoutée
- [ ] Responsive design
- [ ] Dark mode
- [ ] Toasts notifications
- [ ] Loading states
- [ ] Messages erreurs

### Tests
- [ ] Tests SQL (1-7) ✅
- [ ] Tests API (8-13) ✅
- [ ] Tests UI (14-17) ✅
- [ ] Tests E2E (18-19) ✅
- [ ] Tests performance (20-21) ✅
- [ ] Tests sécurité (22-24) ✅

---

## 🚀 Commande de test rapide

```bash
# Exécuter TOUS les tests SQL
psql $DATABASE_URL -f TEST_TRACKING_SYSTEM.sql

# Tester API avec script
./test_api_tracking.sh

# Tester UI manuellement
npm run dev
# Ouvrir http://localhost:3000/dashboard/commercial/tracking
```

---

**SUCCÈS = Tous les tests passent ✅**
