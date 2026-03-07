# 🗄️ GUIDE CRÉATION TABLES SUPABASE - TOP 5 FEATURES

## 📋 ÉTAPES RAPIDES

### Étape 1: Ouvrir Supabase Dashboard

1. Allez sur https://supabase.com
2. Connectez-vous à votre projet
3. Dans le menu latéral, cliquez sur **"SQL Editor"**

---

### Étape 2: Créer les Tables Gamification

1. Dans SQL Editor, créez une nouvelle requête
2. Copiez le contenu complet du fichier `CREATE_GAMIFICATION_TABLES.sql`
3. Collez dans l'éditeur
4. Cliquez sur **"Run"** (ou Ctrl+Enter)

**Tables créées** (8 tables):
- ✅ `user_gamification` - Statistiques utilisateur
- ✅ `badges` - Définitions badges
- ✅ `user_badges` - Badges obtenus
- ✅ `missions` - Missions disponibles
- ✅ `user_missions` - Progressions missions
- ✅ `rewards` - Récompenses shop
- ✅ `user_rewards` - Récompenses réclamées
- ✅ `points_history` - Historique points

---

### Étape 3: Créer les Tables Matching

1. Créez une **nouvelle** requête dans SQL Editor
2. Copiez le contenu du fichier `CREATE_MATCHING_TABLES.sql`
3. Collez dans l'éditeur
4. Cliquez sur **"Run"**

**Tables créées** (4 tables):
- ✅ `influencer_profiles_extended` - Profils enrichis
- ✅ `matching_swipes` - Historique swipes
- ✅ `matches` - Matches confirmés
- ✅ `match_preferences` - Préférences marchands

---

### Étape 4: Insérer les Données de Test

Une fois les tables créées, revenez au terminal et exécutez:

```powershell
cd backend
..\.venv\Scripts\python.exe init_top5_data.py
```

Ce script va:
- ✅ Créer des profils gamification pour 6 utilisateurs
- ✅ Insérer 5 badges de test
- ✅ Créer 4 missions actives
- ✅ Générer des progressions missions
- ✅ Enrichir les profils influenceurs
- ✅ Créer des préférences matching

---

## 🔍 VÉRIFICATION

### Vérifier que les tables existent

Dans Supabase Dashboard → **Table Editor**, vous devriez voir:

**Gamification:**
```
├── user_gamification (6 lignes)
├── badges (5 lignes)
├── user_badges (vide au départ)
├── missions (4 lignes)
├── user_missions (4 lignes)
├── rewards (vide au départ)
├── user_rewards (vide au départ)
└── points_history (vide au départ)
```

**Matching:**
```
├── influencer_profiles_extended (10 lignes)
├── matching_swipes (vide au départ)
├── matches (vide au départ)
└── match_preferences (3 lignes)
```

---

## 🧪 TESTER LES ENDPOINTS

Une fois les données insérées, testez:

```powershell
# Terminal 1 - Backend
cd backend
..\.venv\Scripts\python.exe -m uvicorn server:app --reload --port 8000

# Terminal 2 - Test
cd backend
..\.venv\Scripts\python.exe test_top5_integration.py
```

**Résultats attendus:**
- ✅ `GET /api/gamification/{user_id}` → 200 (avec données)
- ✅ `GET /api/matching/get-recommendations` → 200 (avec liste influenceurs)
- ✅ `GET /api/analytics/merchant/{id}` → 200 (avec analytics)

---

## ⚠️ TROUBLESHOOTING

### Erreur: "relation does not exist"
**Solution:** Vous n'avez pas exécuté les scripts SQL. Retournez à l'Étape 2.

### Erreur: "duplicate key value"
**Solution:** Les tables existent déjà. Ignorez cette erreur ou supprimez d'abord:
```sql
DROP TABLE IF EXISTS user_gamification CASCADE;
DROP TABLE IF EXISTS badges CASCADE;
-- etc.
```

### Erreur: "foreign key constraint"
**Solution:** Assurez-vous que les tables `users`, `merchants`, `influencers` existent avant de créer les nouvelles tables.

### Données vides après init_top5_data.py
**Solution:** Vérifiez que vous avez des utilisateurs/influenceurs dans votre base. Le script utilise les données existantes.

---

## 📊 SCRIPT SQL COMPLET (COPIER-COLLER)

Si vous préférez tout en une fois, voici le SQL complet:

### 1. Gamification (à exécuter en premier)

```sql
-- Copiez le contenu de CREATE_GAMIFICATION_TABLES.sql
```

### 2. Matching (à exécuter ensuite)

```sql
-- Copiez le contenu de CREATE_MATCHING_TABLES.sql
```

---

## 🎯 RÉSULTAT FINAL

Après avoir suivi ce guide, vous aurez:

✅ **12 nouvelles tables** créées dans Supabase
✅ **~30 lignes de données test** insérées
✅ **Tous les endpoints TOP 5** fonctionnels
✅ **GamificationWidget** avec vraies données
✅ **Matching Tinder** avec profils réels
✅ **Analytics Pro** avec métriques

---

## 🚀 PROCHAINES ÉTAPES

1. ✅ Créer tables (ce guide)
2. ✅ Insérer données test (`init_top5_data.py`)
3. ✅ Démarrer backend (`uvicorn server:app`)
4. ✅ Tester frontend (boutons Analytics Pro, Matching, etc.)
5. 📈 Implémenter calculs réels dans services
6. 🎨 Personnaliser UI selon vos besoins

---

**Temps estimé:** 10 minutes

**Dernière mise à jour:** 11 novembre 2025
