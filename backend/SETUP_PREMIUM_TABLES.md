# 🚀 Installation des Tables Premium - Dashboards 10/10

Ce guide explique comment créer les tables nécessaires pour les 3 nouvelles features premium dans Supabase.

## 📋 Tables à Créer

Les 3 nouvelles features nécessitent les tables suivantes:

1. **`content_posts`** - Calendrier éditorial pour influenceurs
2. **`unified_messages`** - Boîte de réception unifiée pour commerciaux
3. **`reviews`** - Gestion des avis avec modération IA pour marchands

## 🔧 Méthode 1: Via Supabase Dashboard (Recommandé)

### Étapes:

1. **Connectez-vous à Supabase**
   - Allez sur https://app.supabase.com/
   - Sélectionnez votre projet

2. **Ouvrez SQL Editor**
   - Dans le menu de gauche, cliquez sur "SQL Editor"
   - Cliquez sur "New query"

3. **Copiez le contenu du fichier SQL**
   - Ouvrez le fichier: `backend/CREATE_PREMIUM_TABLES.sql`
   - Copiez tout le contenu (environ 500 lignes)

4. **Collez et exécutez**
   - Collez le contenu dans l'éditeur SQL
   - Cliquez sur "Run" (ou appuyez sur Ctrl+Enter)

5. **Vérifiez le succès**
   - Vous devriez voir un message de succès
   - Allez dans "Table Editor" pour voir les nouvelles tables

## 🐍 Méthode 2: Via Script Python (Alternative)

Si vous voulez utiliser un script:

```bash
# Installer psycopg2
pip install psycopg2-binary

# Ajouter la variable d'environnement dans .env
# SUPABASE_DB_PASSWORD=votre_mot_de_passe_postgresql

# Exécuter le script
cd backend
python init_premium_tables.py
```

## ✅ Vérification

Après avoir créé les tables, vérifiez qu'elles existent:

1. Allez dans "Table Editor" dans Supabase
2. Vous devriez voir 3 nouvelles tables:
   - `content_posts`
   - `unified_messages`
   - `reviews`

## 🔐 Sécurité (RLS)

Le script SQL configure automatiquement:
- ✅ Row Level Security (RLS) activé
- ✅ Policies pour que chaque utilisateur ne voie que ses données
- ✅ Indexes pour optimiser les performances

## 📊 Structure des Tables

### `content_posts`
- Gestion complète des posts multi-plateformes (Instagram, TikTok, YouTube, etc.)
- Métriques de performance (vues, likes, engagement)
- Planification et auto-publication
- Tracking des revenus

### `unified_messages`
- Messages multi-canaux (Email, SMS, WhatsApp, Messenger, LinkedIn)
- Analyse de sentiment par IA
- Priorisation automatique
- Threading des conversations

### `reviews`
- Modération automatique par IA
- Détection de spam et profanité
- Analyse de sentiment
- Réponses personnalisées
- Métriques de satisfaction

## 🚨 Troubleshooting

### Erreur: "relation already exists"
- Les tables existent déjà, c'est OK!
- Vous pouvez commencer à utiliser les dashboards

### Erreur: "permission denied"
- Assurez-vous d'utiliser le bon compte Supabase
- Vérifiez que vous avez les droits admin sur le projet

### Erreur: "syntax error"
- Assurez-vous d'avoir copié TOUT le contenu du fichier SQL
- Ne modifiez pas le SQL avant de l'exécuter

## 📞 Support

Si vous rencontrez des problèmes, vérifiez:
1. Que vous êtes connecté au bon projet Supabase
2. Que vous avez les droits admin
3. Que le fichier SQL est complet

---

**Note**: Une fois les tables créées, les dashboards seront immédiatement fonctionnels! 🎉
