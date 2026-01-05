# 🚀 Architecture du Module d'Automation Média Multi-Plateformes

## Vue d'ensemble

Module complet d'automation des réseaux sociaux permettant la génération automatique de contenu via IA, la planification intelligente et la publication multi-plateformes.

---

## 🎯 Plateformes Supportées

1. **Instagram** - Posts, Stories, Reels
2. **Twitter/X** - Tweets, Threads
3. **LinkedIn** - Posts, Articles
4. **Facebook** - Posts, Stories
5. **TikTok** - Vidéos courtes

---

## 📊 Architecture Technique

### Stack Technologique

#### Backend
- **Framework**: FastAPI (Python) - déjà utilisé dans l'application
- **Base de données**: PostgreSQL (tables avec préfixe `media_`)
- **Queue**: Redis pour les tâches asynchrones
- **Scheduler**: APScheduler pour les publications planifiées
- **IA**: OpenAI GPT-4 pour la génération de contenu

#### Frontend
- **Framework**: React (déjà utilisé)
- **UI**: Material-UI (déjà utilisé)
- **Calendar**: FullCalendar pour le calendrier éditorial
- **Drag & Drop**: react-beautiful-dnd
- **Charts**: Recharts pour les analytics

---

## 🗄️ Modèles de Données

### 1. `media_platforms`
Stockage des connexions aux plateformes sociales

```sql
CREATE TABLE media_platforms (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'instagram', 'twitter', 'linkedin', 'facebook', 'tiktok'
    account_name VARCHAR(255),
    account_id VARCHAR(255),
    access_token TEXT, -- Encrypted
    refresh_token TEXT, -- Encrypted
    token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    metadata JSONB, -- Platform-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, platform, account_id)
);
```

### 2. `media_templates`
Templates de prompts pour la génération de contenu

```sql
CREATE TABLE media_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50) NOT NULL,
    category VARCHAR(100), -- 'promotional', 'educational', 'engagement', 'story'
    prompt_template TEXT NOT NULL,
    variables JSONB, -- Liste des variables utilisables: {"brand_name", "product", "cta"}
    tone VARCHAR(50), -- 'professional', 'casual', 'friendly', 'luxury', etc.
    max_length INTEGER,
    include_hashtags BOOLEAN DEFAULT true,
    include_emojis BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false, -- Pour partager entre utilisateurs
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. `media_generated_content`
Contenu généré par l'IA

```sql
CREATE TABLE media_generated_content (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES media_templates(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    generated_hashtags TEXT[], -- Array of hashtags
    media_urls TEXT[], -- URLs des images/vidéos générées ou uploadées
    ai_model VARCHAR(100), -- 'gpt-4-turbo', 'claude-3.5-sonnet'
    tone VARCHAR(50),
    variables_used JSONB,
    quality_score INTEGER, -- 0-100
    engagement_prediction INTEGER, -- 0-100
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'approved', 'scheduled', 'published'
    approved_at TIMESTAMP,
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. `media_scheduled_posts`
Publications planifiées

```sql
CREATE TABLE media_scheduled_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER REFERENCES media_generated_content(id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES media_platforms(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    optimal_time_suggested BOOLEAN DEFAULT false,
    post_text TEXT NOT NULL,
    media_urls TEXT[],
    hashtags TEXT[],
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'publishing', 'published', 'failed', 'cancelled'
    published_at TIMESTAMP,
    platform_post_id VARCHAR(255), -- ID du post sur la plateforme
    platform_post_url TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    metadata JSONB, -- Platform-specific options
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. `media_analytics`
Métriques de performance des publications

```sql
CREATE TABLE media_analytics (
    id SERIAL PRIMARY KEY,
    scheduled_post_id INTEGER NOT NULL REFERENCES media_scheduled_posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2), -- Calculated: (likes + comments + shares) / views * 100
    reach INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0, -- Instagram specific
    video_views INTEGER DEFAULT 0, -- For video content
    fetch_count INTEGER DEFAULT 0,
    last_fetched_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6. `media_publishing_queue`
File d'attente pour les publications massives

```sql
CREATE TABLE media_publishing_queue (
    id SERIAL PRIMARY KEY,
    scheduled_post_id INTEGER NOT NULL REFERENCES media_scheduled_posts(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 5, -- 1 (highest) to 10 (lowest)
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    next_attempt_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_log TEXT,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. `media_oauth_states`
États OAuth pour la sécurité des connexions

```sql
CREATE TABLE media_oauth_states (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    state_token VARCHAR(255) NOT NULL UNIQUE,
    code_verifier VARCHAR(255), -- For PKCE
    redirect_uri TEXT,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Services Backend

### 1. `MediaContentGeneratorService`
**Fichier**: `backend/services/media_content_generator.py`

**Responsabilités**:
- Génération de contenu via OpenAI GPT-4
- Application des templates avec variables
- Adaptation du contenu selon la plateforme
- Génération de hashtags pertinents
- Scoring de qualité du contenu

**Méthodes principales**:
```python
async def generate_content(
    user_id: int,
    platform: str,
    prompt: str,
    template_id: Optional[int] = None,
    variables: Optional[dict] = None,
    tone: str = "professional",
    include_hashtags: bool = True,
    include_emojis: bool = True
) -> GeneratedContent

async def generate_batch_content(
    user_id: int,
    platforms: List[str],
    base_prompt: str,
    num_variants: int = 3
) -> List[GeneratedContent]

async def apply_template(
    template_id: int,
    variables: dict
) -> str

async def generate_hashtags(
    content: str,
    platform: str,
    count: int = 10
) -> List[str]
```

### 2. `MediaOAuthService`
**Fichier**: `backend/services/media_oauth_service.py`

**Responsabilités**:
- Gestion des flux OAuth2 pour chaque plateforme
- Stockage sécurisé des tokens (chiffrement)
- Rafraîchissement automatique des tokens
- Révocation des accès

**Méthodes principales**:
```python
async def initiate_oauth_flow(
    user_id: int,
    platform: str,
    redirect_uri: str
) -> OAuthInitResponse

async def complete_oauth_flow(
    user_id: int,
    platform: str,
    code: str,
    state: str
) -> PlatformConnection

async def refresh_access_token(
    platform_id: int
) -> PlatformConnection

async def disconnect_platform(
    user_id: int,
    platform_id: int
) -> bool
```

### 3. `MediaPublishingService`
**Fichier**: `backend/services/media_publishing_service.py`

**Responsabilités**:
- Publication sur chaque plateforme sociale
- Gestion des formats spécifiques à chaque plateforme
- Upload de médias (images/vidéos)
- Gestion des erreurs et retry logic

**Méthodes principales**:
```python
async def publish_to_instagram(
    platform_connection: PlatformConnection,
    content: ScheduledPost
) -> PublishResult

async def publish_to_twitter(
    platform_connection: PlatformConnection,
    content: ScheduledPost
) -> PublishResult

async def publish_to_linkedin(
    platform_connection: PlatformConnection,
    content: ScheduledPost
) -> PublishResult

async def publish_to_facebook(
    platform_connection: PlatformConnection,
    content: ScheduledPost
) -> PublishResult

async def publish_to_tiktok(
    platform_connection: PlatformConnection,
    content: ScheduledPost
) -> PublishResult

async def publish_post(
    scheduled_post_id: int
) -> PublishResult
```

### 4. `MediaSchedulerService`
**Fichier**: `backend/services/media_scheduler_service.py`

**Responsabilités**:
- Planification des publications
- Calcul des horaires optimaux (analyse des données historiques)
- Gestion du calendrier éditorial
- Vérification des conflits de planning

**Méthodes principales**:
```python
async def schedule_post(
    user_id: int,
    content_id: int,
    platform_id: int,
    scheduled_time: datetime,
    auto_optimize: bool = False
) -> ScheduledPost

async def get_optimal_posting_times(
    user_id: int,
    platform: str,
    date_range: Tuple[datetime, datetime]
) -> List[datetime]

async def get_calendar(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    platforms: Optional[List[str]] = None
) -> List[ScheduledPost]

async def reschedule_post(
    post_id: int,
    new_time: datetime
) -> ScheduledPost

async def cancel_scheduled_post(
    post_id: int
) -> bool
```

### 5. `MediaAnalyticsService`
**Fichier**: `backend/services/media_analytics_service.py`

**Responsabilités**:
- Récupération des métriques depuis les APIs des plateformes
- Calcul des taux d'engagement
- Génération de rapports de performance
- Recommandations basées sur les données

**Méthodes principales**:
```python
async def fetch_post_analytics(
    scheduled_post_id: int
) -> Analytics

async def fetch_platform_analytics(
    user_id: int,
    platform: str,
    date_range: Tuple[datetime, datetime]
) -> PlatformAnalytics

async def get_performance_report(
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> PerformanceReport

async def get_best_performing_content(
    user_id: int,
    platform: str,
    limit: int = 10
) -> List[Analytics]

async def get_recommendations(
    user_id: int
) -> ContentRecommendations
```

---

## 🔌 Endpoints API

**Fichier**: `backend/media_automation_endpoints.py`

### Content Generation
```python
POST   /api/media/generate                  # Générer du contenu
POST   /api/media/generate/batch            # Générer plusieurs variantes
GET    /api/media/content                   # Liste du contenu généré
GET    /api/media/content/{id}              # Détail d'un contenu
PUT    /api/media/content/{id}              # Modifier un contenu
DELETE /api/media/content/{id}              # Supprimer un contenu
POST   /api/media/content/{id}/approve      # Approuver un contenu
```

### Templates
```python
GET    /api/media/templates                 # Liste des templates
POST   /api/media/templates                 # Créer un template
GET    /api/media/templates/{id}            # Détail d'un template
PUT    /api/media/templates/{id}            # Modifier un template
DELETE /api/media/templates/{id}            # Supprimer un template
GET    /api/media/templates/default         # Templates par défaut
```

### Platform Connections
```python
GET    /api/media/platforms                 # Liste des connexions
POST   /api/media/platforms/{platform}/connect  # Initier OAuth
GET    /api/media/platforms/callback        # Callback OAuth
DELETE /api/media/platforms/{id}            # Déconnecter
POST   /api/media/platforms/{id}/refresh    # Rafraîchir token
```

### Scheduling
```python
POST   /api/media/schedule                  # Planifier une publication
GET    /api/media/schedule                  # Liste des publications planifiées
GET    /api/media/schedule/calendar         # Calendrier éditorial
PUT    /api/media/schedule/{id}             # Modifier planning
DELETE /api/media/schedule/{id}             # Annuler publication
POST   /api/media/schedule/{id}/reschedule  # Reprogrammer
GET    /api/media/schedule/optimal-times    # Heures optimales
```

### Publishing
```python
POST   /api/media/publish/{id}              # Publier immédiatement
GET    /api/media/publish/status/{id}       # Statut de publication
POST   /api/media/publish/{id}/retry        # Réessayer une publication échouée
```

### Analytics
```python
GET    /api/media/analytics/posts/{id}      # Analytics d'un post
GET    /api/media/analytics/platform        # Analytics par plateforme
GET    /api/media/analytics/report          # Rapport de performance
GET    /api/media/analytics/recommendations # Recommandations
GET    /api/media/analytics/best-content    # Meilleur contenu
```

---

## ⚙️ Worker de Publication

**Fichier**: `backend/workers/media_publisher_worker.py`

### Responsabilités
1. Vérifier toutes les 60 secondes les publications dues
2. Récupérer les posts dont `scheduled_time <= NOW()`
3. Ajouter à la queue de publication
4. Traiter la queue avec rate limiting
5. Mettre à jour les statuts
6. Gérer les retry en cas d'échec

### Configuration
```python
CHECK_INTERVAL = 60  # secondes
MAX_CONCURRENT_PUBLISHES = 10
RATE_LIMITS = {
    'instagram': 25/hour,  # 25 posts par heure
    'twitter': 50/hour,
    'linkedin': 20/hour,
    'facebook': 50/hour,
    'tiktok': 10/hour
}
```

---

## 🎨 Composants Frontend

### 1. `MediaAutomationDashboard`
**Fichier**: `frontend/src/pages/MediaAutomationDashboard.jsx`

Tableau de bord principal avec 5 onglets:
- **Génération**: Créer du contenu avec IA
- **Calendrier**: Planifier les publications
- **Plateformes**: Gérer les connexions
- **Templates**: Gérer les templates
- **Analytics**: Voir les performances

### 2. `ContentGeneratorTab`
**Fichier**: `frontend/src/components/media/ContentGeneratorTab.jsx`

- Sélection de plateforme(s)
- Éditeur de prompt avec variables
- Sélection de template
- Prévisualisation en temps réel
- Génération de variantes
- Approbation/modification du contenu

### 3. `EditorialCalendarTab`
**Fichier**: `frontend/src/components/media/EditorialCalendarTab.jsx`

- Vue mensuelle/hebdomadaire/journalière
- Drag & drop pour reprogrammer
- Filtres par plateforme
- Indicateurs d'heures optimales
- Aperçu rapide du contenu
- Statuts visuels (planifié, publié, échoué)

### 4. `PlatformConnectionsTab`
**Fichier**: `frontend/src/components/media/PlatformConnectionsTab.jsx`

- Cartes pour chaque plateforme
- Boutons "Connecter" avec OAuth flow
- Statut de connexion
- Dernière utilisation
- Gestion des tokens
- Déconnexion

### 5. `TemplatesManagerTab`
**Fichier**: `frontend/src/components/media/TemplatesManagerTab.jsx`

- Liste des templates par plateforme
- Créer/éditer/supprimer templates
- Éditeur de variables
- Prévisualisation avec exemples
- Templates par défaut (publics)
- Statistiques d'utilisation

### 6. `AnalyticsDashboardTab`
**Fichier**: `frontend/src/components/media/AnalyticsDashboardTab.jsx`

- KPIs globaux (vues, engagement, reach)
- Graphiques de performance
- Comparaison par plateforme
- Meilleur contenu
- Recommandations IA
- Export de rapports

---

## 🔐 Sécurité

### Chiffrement des Tokens
```python
# backend/utils/encryption.py
from cryptography.fernet import Fernet

def encrypt_token(token: str, key: str) -> str:
    f = Fernet(key.encode())
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str, key: str) -> str:
    f = Fernet(key.encode())
    return f.decrypt(encrypted_token.encode()).decode()
```

### Rate Limiting
```python
# Par utilisateur
RATE_LIMITS = {
    'content_generation': 100/day,
    'api_calls': 1000/day,
    'publications': 200/day
}
```

### OAuth Security
- State tokens avec expiration (10 minutes)
- PKCE pour les flux publics
- Validation stricte des redirect URIs
- Stockage sécurisé des tokens

---

## 📦 Structure des Fichiers

```
backend/
├── services/
│   ├── media_content_generator.py       (640 lignes)
│   ├── media_oauth_service.py           (520 lignes)
│   ├── media_publishing_service.py      (800 lignes)
│   ├── media_scheduler_service.py       (450 lignes)
│   └── media_analytics_service.py       (580 lignes)
├── workers/
│   ├── media_publisher_worker.py        (320 lignes)
│   └── media_analytics_worker.py        (280 lignes)
├── models/
│   └── media_models.py                  (400 lignes)
├── utils/
│   ├── encryption.py                    (80 lignes)
│   └── platform_helpers.py              (200 lignes)
└── media_automation_endpoints.py        (950 lignes)

frontend/src/
├── pages/
│   └── MediaAutomationDashboard.jsx     (450 lignes)
├── components/media/
│   ├── ContentGeneratorTab.jsx          (580 lignes)
│   ├── EditorialCalendarTab.jsx         (720 lignes)
│   ├── PlatformConnectionsTab.jsx       (420 lignes)
│   ├── TemplatesManagerTab.jsx          (510 lignes)
│   └── AnalyticsDashboardTab.jsx        (640 lignes)
└── hooks/
    └── useMediaAutomation.js            (180 lignes)

Total estimé: ~8,700 lignes de code
```

---

## 🚀 Instructions d'Installation

### 1. Variables d'Environnement
```bash
# .env
OPENAI_API_KEY=sk-...
ENCRYPTION_KEY=base64_encoded_key

# Instagram
INSTAGRAM_CLIENT_ID=your_client_id
INSTAGRAM_CLIENT_SECRET=your_client_secret

# Twitter/X
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret

# LinkedIn
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# Facebook
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# TikTok
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
```

### 2. Dépendances Python
```bash
pip install openai
pip install cryptography
pip install apscheduler
pip install redis
pip install aiohttp
```

### 3. Dépendances NPM
```bash
npm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction
npm install react-beautiful-dnd
npm install recharts
npm install date-fns
```

### 4. Migration Base de Données
```bash
python backend/scripts/create_media_tables.py
```

---

## 📋 Exemples de Prompts par Plateforme

### Instagram
```
Crée un post Instagram engageant pour {brand_name} sur {topic}.
Ton: {tone}
Inclus 3-5 emojis pertinents et termine avec un appel à l'action.
Format: Caption courte (max 125 caractères) suivie d'une description plus détaillée.
```

### Twitter/X
```
Rédige un tweet impactant pour {brand_name} sur {topic}.
Ton: {tone}
Max 280 caractères, inclus 1-2 hashtags stratégiques.
Commence par un hook puissant.
```

### LinkedIn
```
Écris un post LinkedIn professionnel pour {brand_name} sur {topic}.
Ton: {tone}
Structure: Hook → Développement → Conclusion avec CTA
Inclus des insights business et de la valeur pour les professionnels.
```

### Facebook
```
Crée un post Facebook conversationnel pour {brand_name} sur {topic}.
Ton: {tone}
Encourage l'interaction et les commentaires.
Inclus une question à la fin.
```

### TikTok
```
Écris un script TikTok créatif pour {brand_name} sur {topic}.
Ton: {tone}
Format: Hook (3 sec) → Contenu (15 sec) → CTA (2 sec)
Style jeune et dynamique avec emojis.
```

---

## 🎯 Phases d'Implémentation

### Phase 1: Infrastructure (Jours 1-2)
- ✅ Modèles de base de données
- ✅ Service de chiffrement
- ✅ Configuration de base

### Phase 2: Génération de Contenu (Jours 3-4)
- ✅ Service de génération IA
- ✅ Système de templates
- ✅ Endpoints de génération

### Phase 3: OAuth et Connexions (Jours 5-6)
- ✅ Service OAuth multi-plateformes
- ✅ Gestion des tokens
- ✅ Interface de connexion

### Phase 4: Publication et Scheduling (Jours 7-9)
- ✅ Service de publication
- ✅ Service de planification
- ✅ Worker de publication
- ✅ Calendrier éditorial

### Phase 5: Analytics (Jours 10-11)
- ✅ Service d'analytics
- ✅ Worker de récupération des métriques
- ✅ Dashboard analytics

### Phase 6: Frontend (Jours 12-15)
- ✅ Tous les composants React
- ✅ Intégration au menu
- ✅ Tests et polish

---

## 📊 Métriques de Succès

- **Performance**: Support de 1000+ publications simultanées
- **Fiabilité**: Taux de succès de publication > 98%
- **Vitesse**: Génération de contenu < 5 secondes
- **UX**: Interface responsive et intuitive
- **Sécurité**: Chiffrement AES-256, OAuth2 sécurisé

---

**Version**: 1.0
**Dernière mise à jour**: 2026-01-05
**Auteur**: Claude AI Assistant
