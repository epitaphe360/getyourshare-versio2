# Script de Peuplement de Données de Test

Ce script génère des données de test réalistes pour tous les systèmes de l'application GetYourShare.

## 📋 Prérequis

- Python 3.8+
- Accès à la base de données Supabase
- Service Key Supabase (avec permissions admin)

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements-seed.txt
```

## ⚙️ Configuration

Exporter les variables d'environnement Supabase :

```bash
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_SERVICE_KEY='your-service-key-here'
```

## 🎯 Exécution

```bash
# Depuis le dossier scripts
python seed_test_data.py
```

## 📊 Données Générées

Le script crée :
- **36 utilisateurs** : 1 admin, 10 merchants, 20 influencers, 5 commercials
- **10 profils merchants** avec données complètes
- **50-150 produits** répartis entre les merchants
- **10-25 services** pour quelques merchants
- **36 abonnements** (un par utilisateur)
- **0-50 transactions** par utilisateur
- **15 demandes d'inscription** avec statuts variés

## 🔐 Comptes de Test

Après exécution, vous pouvez vous connecter avec :

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Admin | admin@getyourshare.com | Admin123! |
| Merchant | merchant1@example.com | Merchant123! |
| Influencer | influencer1@example.com | Influencer123! |
| Commercial | commercial1@example.com | Commercial123! |

## ⚠️ Avertissement

Ce script est destiné **uniquement aux environnements de développement et de test**.
Ne jamais exécuter en production !

## 🔄 Réinitialisation

Pour réinitialiser et regénérer les données :

```bash
# 1. Vider les tables (via Supabase Dashboard)
# 2. Relancer le script
python seed_test_data.py
```

## 📝 Structure des Données

### Utilisateurs
- Emails uniques avec pattern `role{N}@example.com`
- Mots de passe hashés avec bcrypt
- Dates de création aléatoires (1-180 jours)
- Données Faker françaises

### Produits
- Catégories variées (Électronique, Mode, Maison, etc.)
- Prix entre 10€ et 500€
- Commissions entre 5% et 20%
- Stocks aléatoires

### Transactions
- Types : commission, payout, refund, subscription
- Statuts : completed, pending, failed
- Montants réalistes

### Abonnements
- Plans influencers : free, basic, pro, elite, premium
- Plans merchants : freemium, standard, premium, enterprise
- Plans commercials : starter, pro, enterprise
- Dates de période réalistes

## 🐛 Dépannage

### Erreur de connexion Supabase
```
❌ Erreur: Veuillez configurer SUPABASE_URL et SUPABASE_SERVICE_KEY
```
**Solution :** Vérifier que les variables d'environnement sont correctement exportées

### Erreur de contrainte unique
```
❌ Erreur création utilisateurs: duplicate key value
```
**Solution :** La table contient déjà des données. Vider les tables d'abord.

### Erreur de permissions
```
❌ Erreur: insufficient privileges
```
**Solution :** Utiliser la Service Key (pas la Anon Key) avec permissions admin

## 📖 Ressources

- [Documentation Supabase Python](https://github.com/supabase-community/supabase-py)
- [Documentation Faker](https://faker.readthedocs.io/)
