# 🚀 Optimisation des Performances Backend

J'ai optimisé les endpoints critiques `get_merchants` et `get_influencers` pour éliminer les problèmes de performance (N+1 queries) et corriger des bugs de logique.

## 🛠️ Actions Requises

Pour que ces optimisations fonctionnent, vous devez créer deux Vues SQL dans votre base de données Supabase.

### Étape 1 : Ouvrir l'éditeur SQL Supabase
Allez dans votre projet Supabase > SQL Editor.

### Étape 2 : Créer la vue Merchants
Copiez le contenu du fichier `OPTIMIZE_MERCHANTS_VIEW.sql` et exécutez-le.
Cela va créer la vue `merchants_stats_view`.

### Étape 3 : Créer la vue Influencers
Copiez le contenu du fichier `OPTIMIZE_INFLUENCERS_VIEW.sql` et exécutez-le.
Cela va créer la vue `influencers_stats_view`.

## 📈 Gains de Performance
- **Avant** : Le backend faisait des centaines de requêtes (1 requête par merchant/influencer pour compter les produits, ventes, etc.).
- **Après** : Le backend fait **1 seule requête** optimisée vers la vue SQL.
- **Correction de Bug** : Correction d'un problème où les statistiques (produits, clics) n'étaient pas correctement associées aux utilisateurs à cause d'une confusion entre `user_id` et `merchant_id`/`influencer_id`.

## ✅ Tests
Une fois les vues créées, les endpoints `/api/merchants` et `/api/influencers` utiliseront automatiquement la nouvelle logique optimisée.
Si jamais la vue n'existe pas, le code a un mécanisme de "fallback" pour utiliser l'ancienne méthode (plus lente) sans planter.
