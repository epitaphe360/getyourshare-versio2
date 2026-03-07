# 🚨 ACTION REQUISE : CORRECTION DE LA BASE DE DONNÉES

L'audit du système a révélé des incohérences critiques dans le schéma de la base de données qui empêchent le fonctionnement correct de l'application et des tests.

## 🔴 Problèmes identifiés

1.  **Trigger cassé sur la table `users`** : Un trigger (`trg_auto_assign_sales_rep`) tente d'accéder à la colonne `commercial_id` lors de la création d'un utilisateur, mais cette colonne **n'existe pas** dans la table `users`. Cela empêche toute création de compte (Admin, Marchand, Influenceur).
2.  **Colonnes manquantes dans `leads`** : La table `leads` manque les colonnes `commercial_id` et `sales_rep_id`, ce qui provoque des erreurs 500 lors de l'accès aux fonctionnalités commerciales.
3.  **Rôle manquant** : Le rôle `commercial` n'est pas autorisé dans la contrainte `users_role_check`.

## ✅ Solution

Vous devez exécuter le script SQL de correction que j'ai généré.

### Étapes à suivre :

1.  Ouvrez le fichier `FIX_DB_SCHEMA.sql` situé à la racine du projet.
2.  Copiez tout son contenu.
3.  Allez dans votre tableau de bord Supabase > **SQL Editor**.
4.  Créez une nouvelle requête ("New Query").
5.  Collez le code et cliquez sur **RUN**.

Une fois cela fait, vous pourrez relancer l'audit complet avec la commande :

```bash
python backend/test_ultra_audit.py
```

## ⚠️ Note importante

J'ai appliqué un patch temporaire sur le backend (`backend/server.py`) pour éviter certains crashs, mais la correction de la base de données est indispensable pour rétablir toutes les fonctionnalités.
