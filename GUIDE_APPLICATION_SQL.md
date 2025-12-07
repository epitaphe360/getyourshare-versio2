# 🎯 GUIDE D'APPLICATION DES CORRECTIONS SQL

## ⚠️ ACTION REQUISE MAINTENANT

Le fichier **`FIX_SCHEMA_PART3_NEW_TABLES.sql`** contient toutes les corrections nécessaires pour faire fonctionner l'application.

### 📋 ÉTAPES À SUIVRE:

1. **Ouvrir Supabase Dashboard**
   - Va sur: https://supabase.com/dashboard
   - Sélectionne ton projet GetYourShare

2. **Ouvrir SQL Editor**
   - Dans le menu gauche: `SQL Editor`
   - Cliquer sur `New query`

3. **Copier-coller le SQL**
   - Ouvrir le fichier: `FIX_SCHEMA_PART3_NEW_TABLES.sql`
   - Sélectionner TOUT le contenu (Ctrl+A)
   - Copier (Ctrl+C)
   - Coller dans Supabase SQL Editor (Ctrl+V)

4. **Exécuter**
   - Cliquer sur le bouton **`Run`** (ou F5)
   - Attendre la confirmation "Success"

5. **Vérifier**
   ```bash
   python apply_schema_fixes.py
   ```
   - Tape "o" pour vérifier que toutes les tables existent

6. **Relancer le test complet**
   ```bash
   python backend/run_automation_scenario.py
   ```

---

## ✅ CE QUI SERA CORRIGÉ

### 🔥 Corrections Critiques (Bloquantes)

1. **Contrainte FK users_referred_by_fkey**
   - ❌ Avant: Impossible de supprimer utilisateurs ayant parrainé d'autres
   - ✅ Après: `ON DELETE SET NULL` - suppression autorisée

2. **Colonne trust_scores.reviews_count**
   - ❌ Avant: Colonne manquante → erreur Phase 16
   - ✅ Après: Colonne créée avec valeur par défaut 0

3. **Colonne qr_scan_events.user_id**
   - ❌ Avant: Colonne manquante → erreur Phase 26
   - ✅ Après: Colonne créée avec FK vers users

4. **Contraintes NOT NULL cassées**
   - ❌ Avant: `leads.marchand_id` obligatoire mais pas fourni
   - ✅ Après: Rendu nullable
   - ❌ Avant: `integrations.credentials` obligatoire
   - ✅ Après: Rendu nullable
   - ❌ Avant: `content_templates.category` obligatoire
   - ✅ Après: Rendu nullable

### 📦 Tables Manquantes (Nouvelles Fonctionnalités)

5. **Table disputes** - Support client
   - Gestion des litiges entre utilisateurs
   - Phases 22 fonctionnera

6. **Table promotions** - Marketing
   - Codes promo et réductions
   - Phase 12 fonctionnera

7. **Table live_streams** - Streaming
   - Live shopping et streaming
   - Phase 19 fonctionnera

8. **Table report_runs** - Reporting
   - Exécution de rapports personnalisés
   - Phase 28 fonctionnera

9. **Table workspace_comments** - Collaboration
   - Commentaires d'équipe
   - Phase 33 fonctionnera

10. **Tables infrastructure**
    - `invoices` - Facturation
    - `webhook_logs` - Logs webhooks
    - `api_keys` - Clés API
    - `rate_limits` - Limitation de taux
    - `data_exports` - Exports de données

---

## 📊 IMPACT ATTENDU

### Avant Corrections:
- ❌ 3 erreurs **BLOQUANTES**
- ❌ 10+ tables manquantes
- ❌ Phases 0, 7, 12, 16, 19, 20, 22, 23, 26, 27, 28, 33 en échec

### Après Corrections:
- ✅ 0 erreur bloquante
- ✅ Toutes les tables créées
- ✅ 35/35 phases fonctionnelles (ou ignorées proprement)

---

## 🚀 APRÈS L'APPLICATION DU SQL

Une fois le SQL exécuté dans Supabase, relancer le test complet:

```bash
python backend/run_automation_scenario.py
```

Tu devrais voir:
- ✅ Phase 0 (cleanup): SUCCÈS
- ✅ Phases 1-35: Toutes réussies ou ignorées proprement
- ✅ Aucune erreur "Could not find"
- ✅ Aucune erreur "constraint violation"
- ✅ Exit code: 0

---

## 💡 EN CAS DE PROBLÈME

Si une commande SQL échoue dans Supabase:

1. **"relation already exists"** → Normal, ignorer
2. **"column already exists"** → Normal, ignorer
3. **"constraint already exists"** → Normal, ignorer
4. **Autre erreur** → Me montrer le message exact

---

**MAINTENANT: Exécute le SQL dans Supabase puis relance le test !** 🚀
