# 🚀 MIGRATION DES TABLES INFLUENCERS ET MERCHANTS

## 📋 Vue d'ensemble

Cette migration crée les tables `influencers` et `merchants` avec toutes les colonnes nécessaires pour stocker les profils complets des influenceurs et marchands.

## ✅ Que fait cette migration ?

### 1. **Suppression des anciennes tables** (si elles existent)
   - `public.influencers`
   - `public.merchants`

### 2. **Création de la table `merchants`**
   Colonnes principales :
   - `id` (UUID, clé primaire)
   - `user_id` (référence à `users.id`)
   - `company_name` (nom de l'entreprise)
   - `industry` (secteur d'activité)
   - `category` (catégorie : E-commerce, Mode, Tech, etc.)
   - `address`, `tax_id`, `website`, `logo_url`
   - `description` (présentation de l'entreprise)
   - `subscription_plan` (free, starter, pro, enterprise)
   - `subscription_status` (statut de l'abonnement)
   - `commission_rate` (taux de commission plateforme)
   - `monthly_fee` (frais mensuels)
   - `total_sales`, `total_commission_paid` (statistiques)
   - `created_at`, `updated_at` (horodatage)

### 3. **Création de la table `influencers`**
   Colonnes principales :
   - `id` (UUID, clé primaire)
   - `user_id` (référence à `users.id`)
   - `username` (nom d'utilisateur unique)
   - `full_name` (nom complet)
   - `bio` (biographie)
   - `profile_picture_url` (photo de profil)
   - `category` (niche : Mode, Beauté, Tech, etc.)
   - `influencer_type` (nano, micro, macro, mega)
   - `audience_size` (taille de l'audience)
   - `engagement_rate` (taux d'engagement)
   - `subscription_plan` (starter, pro)
   - `subscription_status` (statut de l'abonnement)
   - `platform_fee_rate` (frais plateforme)
   - `monthly_fee` (frais mensuels)
   - `social_links` (JSONB - liens réseaux sociaux)
   - `total_clicks`, `total_sales`, `total_earnings` (statistiques)
   - `balance` (solde disponible)
   - `payment_method`, `payment_details` (informations de paiement)
   - `created_at`, `updated_at` (horodatage)

### 4. **Index pour performances**
   - Index sur `user_id` pour les deux tables
   - Index sur `category` pour les deux tables
   - Index sur `subscription_plan` pour les deux tables
   - Index sur `username`, `influencer_type` pour influencers

### 5. **Sécurité RLS (Row Level Security)**
   - Politiques pour que les users ne voient que leur propre profil
   - Politiques pour que les admins aient accès total
   - Politiques de modification restreintes au propriétaire

### 6. **Triggers automatiques**
   - Mise à jour automatique de `updated_at` lors des modifications

## 🎯 Comment appliquer la migration ?

### Option 1 : Via Supabase Dashboard (RECOMMANDÉ)

1. **Ouvrez votre projet Supabase**
   - Allez sur https://supabase.com/dashboard
   - Sélectionnez votre projet GetYourShare

2. **Accédez au SQL Editor**
   - Cliquez sur "SQL Editor" dans le menu latéral
   - Ou utilisez le raccourci dans la barre de recherche

3. **Créez une nouvelle requête**
   - Cliquez sur "+ New query"
   - Donnez un nom : "Migration Influencers Merchants"

4. **Copiez-collez le SQL**
   - Ouvrez le fichier `MIGRATION_TABLES_COPY_PASTE.sql` à la racine du projet
   - Copiez tout le contenu
   - Collez dans l'éditeur Supabase

5. **Exécutez la migration**
   - Cliquez sur "Run" (ou appuyez sur Ctrl+Enter / Cmd+Enter)
   - Attendez quelques secondes

6. **Vérifiez le résultat**
   - Vous devriez voir des messages de succès :
     ```
     ✅ Tables merchants et influencers créées avec succès !
     ✅ Index créés pour améliorer les performances
     ✅ RLS activé avec policies appropriées
     ✅ Triggers updated_at configurés
     ```

7. **Vérifiez les tables**
   - Allez dans "Table Editor"
   - Vous devriez voir les tables `merchants` et `influencers`

### Option 2 : Via psql (Pour utilisateurs avancés)

```bash
psql -h <SUPABASE_HOST> -U postgres -d postgres -f MIGRATION_TABLES_COPY_PASTE.sql
```

## 🔍 Vérification post-migration

Après avoir appliqué la migration, vérifiez que tout fonctionne :

```bash
# Dans le terminal, depuis le dossier backend/
python check_tables_structure.py
```

Ou créez un script de vérification rapide :

```python
from supabase_client import supabase

# Vérifier que les tables existent
merchants = supabase.table("merchants").select("*").limit(1).execute()
influencers = supabase.table("influencers").select("*").limit(1).execute()

print("✅ Tables créées avec succès!")
```

## 📝 Prochaines étapes

Une fois la migration appliquée :

1. **Créer les comptes de test complets**
   ```bash
   python backend/create_test_accounts.py
   ```

2. **Vérifier les comptes**
   ```bash
   python backend/check_test_users.py
   ```

3. **Relancer les tests**
   ```bash
   .\run_tests.ps1
   ```

## ⚠️ Notes importantes

- Cette migration **supprime et recrée** les tables influencers et merchants
- **Toutes les données existantes dans ces tables seront perdues**
- Les utilisateurs de la table `users` ne sont PAS affectés
- Si vous avez des données importantes, faites un backup avant

## 🆘 En cas de problème

Si la migration échoue :

1. **Vérifiez les permissions**
   - Assurez-vous d'utiliser un compte avec droits admin sur Supabase

2. **Vérifiez les dépendances**
   - La table `users` doit exister (référence `user_id`)
   - La fonction `gen_random_uuid()` doit être disponible

3. **Consultez les logs**
   - Regardez les messages d'erreur dans le SQL Editor
   - Cherchez les contraintes qui pourraient bloquer

4. **Réessayez étape par étape**
   - Exécutez d'abord uniquement les DROP TABLE
   - Puis exécutez les CREATE TABLE séparément

## 📞 Support

Si vous avez des questions ou des problèmes, vérifiez :
- La documentation Supabase : https://supabase.com/docs
- Les logs d'erreur dans le SQL Editor
- La console du navigateur pour les erreurs
