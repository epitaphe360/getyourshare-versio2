# 🚨 ACTION REQUISE : Correction de la Base de Données (Mise à jour V3)

Le script précédent a échoué car la table `subscription_plans` manquait de plusieurs colonnes (`price_mad`, `max_team_members`, etc.). J'ai mis à jour le script pour corriger TOUTES les colonnes manquantes potentielles.

## 🛠️ Procédure de correction (À refaire une dernière fois)

1.  Connectez-vous à votre tableau de bord Supabase : [https://supabase.com/dashboard](https://supabase.com/dashboard)
2.  Sélectionnez votre projet (`iamezkmapbhlhhvvsits`).
3.  Allez dans la section **SQL Editor** (icône de terminal `>_` dans la barre latérale gauche).
4.  Cliquez sur **New Query**.
5.  Copiez l'intégralité du contenu du fichier `FIX_DB_SCHEMA_FINAL.sql` (qui vient d'être mis à jour).
6.  Collez le code dans l'éditeur SQL de Supabase.
7.  Cliquez sur le bouton **Run** (en bas à droite ou en haut à droite).

## ✅ Ce que fait ce script (Version Complète et Robuste)

*   Ajoute la colonne `started_at` à la table `subscriptions`.
*   **NOUVEAU** : Ajoute TOUTES les colonnes manquantes à `subscription_plans` :
    *   `code`
    *   `type`
    *   `price_mad`
    *   `max_team_members`
    *   `max_domains`
    *   `features`
*   Ajoute les colonnes `updated_at` et `canceled_at` si elles manquent.
*   Vérifie et corrige la table `notifications` (colonne `is_read`).
*   Recrée la vue `v_active_subscriptions` pour qu'elle fonctionne correctement avec les nouvelles colonnes.

Une fois cette opération effectuée, les erreurs "Network Error" (500 Internal Server Error) sur le tableau de bord devraient disparaître.
