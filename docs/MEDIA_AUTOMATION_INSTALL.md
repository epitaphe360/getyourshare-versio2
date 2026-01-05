# 📦 Installation du Module d'Automation Média

Guide d'installation et de configuration rapide pour le module d'automation média multi-plateformes.

---

## 🚀 Démarrage Rapide

### 1. Variables d'Environnement

Ajoutez ces variables à votre fichier `.env`:

```bash
# ============================================
# MEDIA AUTOMATION MODULE
# ============================================

# OpenAI (Génération de contenu IA)
OPENAI_API_KEY=sk-proj-VOTRE_CLE_API_OPENAI

# Chiffrement des tokens (IMPORTANT!)
# Générer avec: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=VOTRE_CLE_CHIFFREMENT_BASE64

# ============================================
# INSTAGRAM
# ============================================
INSTAGRAM_CLIENT_ID=votre_client_id
INSTAGRAM_CLIENT_SECRET=votre_client_secret

# ============================================
# TWITTER/X
# ============================================
TWITTER_CLIENT_ID=votre_client_id
TWITTER_CLIENT_SECRET=votre_client_secret

# ============================================
# LINKEDIN
# ============================================
LINKEDIN_CLIENT_ID=votre_client_id
LINKEDIN_CLIENT_SECRET=votre_client_secret

# ============================================
# FACEBOOK
# ============================================
FACEBOOK_APP_ID=votre_app_id
FACEBOOK_APP_SECRET=votre_app_secret

# ============================================
# TIKTOK
# ============================================
TIKTOK_CLIENT_KEY=votre_client_key
TIKTOK_CLIENT_SECRET=votre_client_secret
```

### 2. Dépendances Python

Installez les dépendances nécessaires:

```bash
pip install openai aiohttp cryptography apscheduler redis
```

### 3. Dépendances NPM (Frontend)

Si nécessaire pour les fonctionnalités avancées:

```bash
npm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
npm install react-beautiful-dnd
npm install recharts
npm install date-fns
```

### 4. Configuration Base de Données

Les tables SQL sont définies dans l'architecture (`docs/MEDIA_AUTOMATION_ARCHITECTURE.md`).

**Tables à créer** (préfixe `media_`):
- `media_platforms` - Connexions aux plateformes
- `media_templates` - Templates de prompts
- `media_generated_content` - Contenu généré
- `media_scheduled_posts` - Publications planifiées
- `media_analytics` - Métriques de performance
- `media_publishing_queue` - File d'attente de publication
- `media_oauth_states` - États OAuth

**Script SQL** (à adapter selon votre base de données):
Consultez `docs/MEDIA_AUTOMATION_ARCHITECTURE.md` section "Modèles de Données" pour les scripts CREATE TABLE complets.

### 5. Génération de la Clé de Chiffrement

**IMPORTANT**: Générez une clé de chiffrement sécurisée pour les tokens:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f"ENCRYPTION_KEY={key.decode()}")
```

Ajoutez cette clé dans votre fichier `.env`.

---

## 📝 Configuration des APIs Sociales

### Instagram

1. Allez sur [Facebook Developers](https://developers.facebook.com/)
2. Créez une nouvelle app
3. Ajoutez le produit "Instagram Basic Display"
4. Configurez les OAuth Redirect URIs: `https://votreapp.com/api/media/platforms/callback`
5. Récupérez le Client ID et Client Secret

### Twitter/X

1. Allez sur [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Créez un projet et une app
3. Activez OAuth 2.0
4. Configurez le Callback URL: `https://votreapp.com/api/media/platforms/callback`
5. Activez les permissions: tweet.read, tweet.write, users.read, offline.access

### LinkedIn

1. Allez sur [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Créez une nouvelle app
3. Ajoutez les permissions: r_liteprofile, r_emailaddress, w_member_social
4. Configurez OAuth 2.0 Redirect URLs
5. Récupérez les credentials

### Facebook

1. Utilisez la même app Facebook que pour Instagram
2. Ajoutez le produit "Pages"
3. Demandez les permissions: pages_manage_posts, pages_read_engagement
4. Configurez les Redirect URIs

### TikTok

1. Allez sur [TikTok for Developers](https://developers.tiktok.com/)
2. Créez une app
3. Activez l'API "Content Posting"
4. Configurez les Redirect URIs
5. Récupérez le Client Key et Client Secret

---

## 🔧 Configuration Serveur

### Option 1: Déploiement Simple (sans worker)

Le module fonctionne sans worker de planification. La publication se fait manuellement ou immédiatement.

**Aucune configuration supplémentaire requise.**

### Option 2: Avec Worker de Planification (Recommandé)

Pour activer la publication automatique planifiée:

```bash
# Installer APScheduler
pip install apscheduler

# Démarrer le worker (à créer)
python backend/workers/media_publisher_worker.py
```

**Note**: Le worker n'est pas encore implémenté dans cette version. À développer selon vos besoins.

---

## ✅ Vérification de l'Installation

### 1. Test Backend

```bash
# Démarrer le serveur
uvicorn backend.server:app --reload

# Tester le health check
curl http://localhost:8000/api/media/health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T...",
  "services": {
    "content_generator": true,
    "oauth": true,
    "publishing": true
  }
}
```

### 2. Test Frontend

1. Connectez-vous à l'application
2. Naviguez vers `/media-automation`
3. Vous devriez voir le dashboard avec 4 onglets:
   - Génération
   - Plateformes
   - Calendrier
   - Analytics

### 3. Test de Génération de Contenu

Dans l'onglet "Génération":
1. Sélectionnez une plateforme (ex: Instagram)
2. Entrez un sujet (ex: "Lancement nouveau produit")
3. Choisissez un ton (ex: "inspirational")
4. Cliquez sur "Générer du Contenu"

**Avec API Key OpenAI**: Vous obtiendrez du contenu généré par IA
**Sans API Key**: Vous obtiendrez du contenu basé sur des templates

---

## 🔐 Sécurité

### Checklist Sécurité

- [ ] ✅ Clé de chiffrement générée et sécurisée dans `.env`
- [ ] ✅ Fichier `.env` ajouté à `.gitignore`
- [ ] ✅ Tokens OAuth chiffrés en base de données
- [ ] ✅ HTTPS activé en production
- [ ] ✅ Rate limiting configuré
- [ ] ✅ CORS configuré correctement
- [ ] ✅ Validation des tokens avant expiration

### Bonnes Pratiques

1. **Ne jamais commiter les tokens** dans le code
2. **Rotation des secrets** tous les 90 jours
3. **Logs sécurisés** - Ne pas logger les tokens
4. **Monitoring** - Surveiller les tentatives d'accès

---

## 📊 Monitoring et Logs

### Logs à Surveiller

```python
# Backend logs
tail -f backend/logs/media_automation.log

# Worker logs (si activé)
tail -f backend/logs/media_publisher_worker.log
```

### Métriques Importantes

- Nombre de publications par jour
- Taux de succès de publication
- Temps de génération de contenu
- Erreurs OAuth / Refresh token

---

## 🐛 Dépannage

### Problème: "Invalid or expired state token"

**Cause**: Le state OAuth a expiré (> 10 minutes)

**Solution**: Recommencez le flux de connexion

### Problème: "Failed to refresh token"

**Cause**: Le refresh token est invalide ou expiré

**Solution**:
1. Déconnecter la plateforme
2. Reconnecter avec OAuth

### Problème: "Content generation failed"

**Cause**: Pas d'OPENAI_API_KEY ou quota dépassé

**Solution**:
1. Vérifier que l'API key est dans `.env`
2. Vérifier le quota OpenAI
3. Le système utilise des templates en fallback

### Problème: "Platform API rate limit exceeded"

**Cause**: Trop de publications en peu de temps

**Solution**:
- Instagram: Max 25/heure
- Twitter: Max 50/heure
- LinkedIn: Max 20/heure
- Facebook: Max 50/heure
- TikTok: Max 10/heure

Espacer les publications.

---

## 📚 Documentation Complète

- **Architecture**: `docs/MEDIA_AUTOMATION_ARCHITECTURE.md`
- **API Reference**: Accéder à `/api/media/docs` dans l'application
- **Modèles**: `backend/models/media_models.py`
- **Services**: `backend/services/media_*.py`

---

## 🆘 Support

En cas de problème:

1. Vérifier les logs backend
2. Vérifier la console navigateur (F12)
3. Vérifier la configuration `.env`
4. Consulter l'architecture complète
5. Tester avec le health check endpoint

---

## 📦 Fichiers Créés

### Backend (2,990 lignes)
```
backend/
├── models/media_models.py (400 lignes)
├── services/
│   ├── media_content_generator.py (640 lignes)
│   ├── media_oauth_service.py (520 lignes)
│   └── media_publishing_service.py (480 lignes)
└── media_automation_endpoints.py (950 lignes)
```

### Frontend (450 lignes)
```
frontend/src/pages/
└── MediaAutomationDashboard.jsx (450 lignes)
```

### Documentation (2,100 lignes)
```
docs/
├── MEDIA_AUTOMATION_ARCHITECTURE.md (1,800 lignes)
└── MEDIA_AUTOMATION_INSTALL.md (300 lignes)
```

**Total: ~5,540 lignes de code + documentation**

---

## 🎯 Prochaines Étapes

### Phase 1 (Actuel) - ✅ Complété
- [x] Architecture complète
- [x] Génération de contenu IA
- [x] Connexions OAuth
- [x] API endpoints
- [x] Dashboard React
- [x] Intégration au système

### Phase 2 (À venir)
- [ ] Worker de planification automatique
- [ ] Calendrier drag & drop (FullCalendar)
- [ ] Analytics temps réel
- [ ] Templates communautaires
- [ ] Export de rapports PDF

### Phase 3 (Futur)
- [ ] IA pour suggestion d'horaires optimaux
- [ ] Génération automatique d'images (DALL-E)
- [ ] Analyse de sentiment des commentaires
- [ ] A/B Testing automatique
- [ ] Intégration avec plus de plateformes (YouTube, Pinterest, etc.)

---

**Version**: 1.0
**Date**: 2026-01-05
**Statut**: Production Ready (sans worker)
