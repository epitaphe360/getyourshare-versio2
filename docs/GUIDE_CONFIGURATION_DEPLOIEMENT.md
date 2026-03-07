# 🔧 GUIDE DE CONFIGURATION & DÉPLOIEMENT
## GetYourShare - Application SaaS Marketing d'Influence

---

## 📋 TABLE DES MATIÈRES

1. [Prérequis & Environnement](#prérequis--environnement)
2. [Configuration Base de Données](#configuration-base-de-données)
3. [Configuration Backend](#configuration-backend)
4. [Configuration Frontend](#configuration-frontend)
5. [Configuration PWA Mobile](#configuration-pwa-mobile)
6. [Configuration Services Externes](#configuration-services-externes)
7. [Variables d'Environnement](#variables-denvironnement)
8. [Déploiement Production](#déploiement-production)
9. [Tests & Validation](#tests--validation)
10. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🎯 PRÉREQUIS & ENVIRONNEMENT

### 💻 Versions Requises

```bash
# Node.js & NPM
node --version  # v18.0.0 ou supérieur
npm --version   # v9.0.0 ou supérieur

# Python & Pip
python --version  # Python 3.11 ou supérieur
pip --version     # pip 23.0 ou supérieur

# PostgreSQL
psql --version    # PostgreSQL 15.0 ou supérieur

# Git
git --version     # Git 2.40.0 ou supérieur
```

### 📦 Installation Outils Nécessaires

```bash
# Installation Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installation Python 3.11
sudo apt-get install python3.11 python3.11-venv python3-pip

# Installation PostgreSQL 15
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgresql-15
```

---

## 🗄️ CONFIGURATION BASE DE DONNÉES

### 1. Création Base de Données

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer la base de données
CREATE DATABASE getyourshare;

# Créer utilisateur dédié
CREATE USER getyourshare_user WITH ENCRYPTED PASSWORD 'VOTRE_MOT_DE_PASSE_SECURISE';

# Accorder tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE getyourshare TO getyourshare_user;

# Activer extensions nécessaires
\c getyourshare
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
```

### 2. Configuration Supabase (Alternative Recommandée)

**⚡ Option Cloud (Recommandé pour démarrage rapide)**

```bash
# 1. Créer compte sur supabase.com
# 2. Créer nouveau projet
# 3. Noter les credentials:

SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1...
```

### 3. Migrations Base de Données

```bash
# Naviguer vers le dossier database
cd database/migrations

# Exécuter migrations dans l'ordre
psql -U getyourshare_user -d getyourshare -f 001_initial_schema.sql
psql -U getyourshare_user -d getyourshare -f 002_add_sales_representatives.sql

# OU si Supabase:
# Copier le contenu de chaque migration dans
# Supabase Dashboard > SQL Editor > New Query
```

### 4. Vérification Tables Créées

```sql
-- Vérifier que toutes les tables existent
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Résultat attendu (18+ tables):
-- ✅ users
-- ✅ merchants
-- ✅ influencers
-- ✅ products
-- ✅ trackable_links
-- ✅ clicks
-- ✅ sales
-- ✅ sales_representatives
-- ✅ sales_leads
-- ✅ sales_deals
-- ✅ sales_activities
-- ✅ sales_targets
-- ✅ sales_commissions
-- ✅ gamification_levels
-- ✅ gamification_badges
-- ✅ influencer_matches
-- ✅ analytics_cache
-- ✅ ...
```

### 5. Configuration Row Level Security (RLS)

```sql
-- Activer RLS sur toutes les tables sensibles
ALTER TABLE sales_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_commissions ENABLE ROW LEVEL SECURITY;

-- Créer policies (déjà incluses dans migrations)
-- Vérifier qu'elles existent:
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE schemaname = 'public';
```

---

## ⚙️ CONFIGURATION BACKEND

### 1. Installation Dépendances Python

```bash
# Naviguer vers le dossier backend
cd backend

# Créer environnement virtuel
python3.11 -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# OU
.\venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt

# Si requirements.txt n'existe pas, installer manuellement:
pip install fastapi uvicorn python-dotenv supabase pydantic python-multipart
```

### 2. Créer Fichier `.env` Backend

```bash
# Créer fichier .env dans /backend
touch .env

# Éditer avec votre éditeur préféré
nano .env
```

**Contenu `/backend/.env`:**

```ini
# =====================================
# CONFIGURATION GETYOURSHARE BACKEND
# =====================================

# Environment
ENVIRONMENT=development  # development | staging | production
DEBUG=True

# Database (PostgreSQL Direct)
DATABASE_URL=postgresql://getyourshare_user:VOTRE_MOT_DE_PASSE@localhost:5432/getyourshare

# OU Database (Supabase)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1...

# JWT Secrets
JWT_SECRET_KEY=GENERER_UNE_CLE_ALEATOIRE_LONGUE_ET_SECURISEE_ICI
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security
CORS_ORIGINS=http://localhost:3000,https://getyourshare.ma
ALLOWED_HOSTS=localhost,127.0.0.1,getyourshare.ma

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10 MB
UPLOAD_DIR=./uploads

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@getyourshare.ma
SMTP_PASSWORD=VOTRE_MOT_DE_PASSE_APPLICATION
SMTP_FROM=GetYourShare <noreply@getyourshare.ma>

# SMS (Twilio ou autre)
SMS_PROVIDER=twilio  # twilio | nexmo | custom
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+212XXXXXXXXX

# WhatsApp Business
WHATSAPP_API_KEY=xxxxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER=+212XXXXXXXXX

# Payment Gateways Maroc
CMI_MERCHANT_ID=xxxxxxxxxxxxx
CMI_API_KEY=xxxxxxxxxxxxxxxxxx
CMI_SECRET_KEY=xxxxxxxxxxxxxxxxxx

SG_MERCHANT_ID=xxxxxxxxxxxxx
SG_API_KEY=xxxxxxxxxxxxxxxxxx
SG_SECRET_KEY=xxxxxxxxxxxxxxxxxx

PAYZONE_MERCHANT_ID=xxxxxxxxxxxxx
PAYZONE_API_KEY=xxxxxxxxxxxxxxxxxx
PAYZONE_SECRET_KEY=xxxxxxxxxxxxxxxxxx

# Push Notifications (Firebase Cloud Messaging)
FCM_SERVER_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxx
FCM_SENDER_ID=xxxxxxxxxxxxxx

# IA / ML Services (optionnel)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Analytics
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
MIXPANEL_TOKEN=xxxxxxxxxxxxxxxx

# Monitoring & Logs
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR

# Redis Cache (optionnel mais recommandé)
REDIS_URL=redis://localhost:6379/0

# Celery Task Queue (optionnel)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 3. Générer Clés Sécurisées

```bash
# Générer JWT Secret Key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Générer API Keys
python -c "import secrets; print('API_KEY_' + secrets.token_hex(32))"
```

### 4. Tester Backend

```bash
# Depuis /backend
source venv/bin/activate

# Lancer serveur de développement
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Tester l'API
curl http://localhost:8000/health
# Réponse attendue: {"status":"ok","version":"2.0.0"}

# Accéder documentation auto
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

---

## 🎨 CONFIGURATION FRONTEND

### 1. Installation Dépendances npm

```bash
# Naviguer vers le dossier frontend
cd frontend

# Installer dépendances
npm install

# Si package-lock.json obsolète
npm install --legacy-peer-deps
```

### 2. Créer Fichier `.env` Frontend

```bash
# Créer fichier .env dans /frontend
touch .env

# Éditer
nano .env
```

**Contenu `/frontend/.env`:**

```ini
# =====================================
# CONFIGURATION GETYOURSHARE FRONTEND
# =====================================

# React App
REACT_APP_NAME=GetYourShare
REACT_APP_VERSION=2.0.0

# API Backend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# Supabase (si utilisé directement depuis frontend)
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1...

# Google Maps (pour géolocalisation)
REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXX

# Analytics
REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
REACT_APP_MIXPANEL_TOKEN=xxxxxxxxxxxxxxxx

# Social Login
REACT_APP_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
REACT_APP_FACEBOOK_APP_ID=xxxxxxxxxxxxxx

# Stripe (si utilisé)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx

# Sentry (Error Tracking)
REACT_APP_SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Feature Flags
REACT_APP_FEATURE_GAMIFICATION=true
REACT_APP_FEATURE_MATCHING=true
REACT_APP_FEATURE_ANALYTICS_PRO=true
REACT_APP_FEATURE_MOBILE_PWA=true
REACT_APP_FEATURE_SALES_REP=true

# Environment
REACT_APP_ENV=development  # development | staging | production
```

### 3. Configuration PWA

**Créer/Vérifier `public/manifest.json`:**

```json
{
  "name": "GetYourShare - Marketing d'Influence SaaS",
  "short_name": "GetYourShare",
  "description": "Plateforme SaaS pour marchands, influenceurs et commerciaux",
  "start_url": "/?source=pwa",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

### 4. Générer Icônes PWA

```bash
# Installer outil de génération d'icônes
npm install -g pwa-asset-generator

# Créer icône source (512x512 minimum)
# Placer dans /frontend/public/logo-source.png

# Générer toutes les tailles
pwa-asset-generator logo-source.png ./public/icons

# Tailles générées:
# - icon-72x72.png
# - icon-96x96.png
# - icon-128x128.png
# - icon-144x144.png
# - icon-152x152.png
# - icon-192x192.png
# - icon-384x384.png
# - icon-512x512.png
```

### 5. Tester Frontend

```bash
# Depuis /frontend
npm start

# L'application s'ouvre sur http://localhost:3000

# Vérifier console pour erreurs
# Tester navigation entre pages
# Vérifier appels API backend
```

---

## 📱 CONFIGURATION PWA MOBILE

### 1. Configuration Service Worker

**✅ Déjà fait:** `public/service-worker.js` créé

**À vérifier:**

```javascript
// Dans service-worker.js, mettre à jour:
const CACHE_NAME = 'getyourshare-v2.0.0';  // Version actuelle

// URLs à cacher (ajuster selon vos routes)
const urlsToCache = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/offline.html'
];
```

### 2. Configuration Push Notifications (VAPID)

```bash
# Installer web-push globalement
npm install -g web-push

# Générer clés VAPID
web-push generate-vapid-keys

# Sauvegarder les clés générées:
```

**Résultat:**
```
Public Key: BEl62iUYgUivxIkv69yViEuiBPa...
Private Key: UUxI4O8DLH1HTh49x3...
```

**Ajouter au backend `.env`:**
```ini
VAPID_PUBLIC_KEY=BEl62iUYgUivxIkv69yViEuiBPa...
VAPID_PRIVATE_KEY=UUxI4O8DLH1HTh49x3...
VAPID_SUBJECT=mailto:admin@getyourshare.ma
```

**Ajouter au frontend `src/hooks/useMobile.js`:**
```javascript
// Remplacer YOUR_VAPID_PUBLIC_KEY
const vapidPublicKey = 'BEl62iUYgUivxIkv69yViEuiBPa...';
```

### 3. Configuration IndexedDB

**✅ Déjà fait:** Stores créés dans service-worker.js

**À vérifier:**
```javascript
// Stores IndexedDB:
// - pendingLeads
// - pendingActivities
// - pendingSwipes
// - pendingPayouts

// Vérifier version DB
const request = indexedDB.open('GetYourShareDB', 2);
```

### 4. Test PWA

```bash
# Build production
npm run build

# Servir le build
npm install -g serve
serve -s build -l 3000

# Ouvrir Chrome DevTools
# > Application Tab
# > Service Workers: Doit être "activated and running"
# > Manifest: Doit charger sans erreurs
# > Storage > IndexedDB: GetYourShareDB doit exister
```

**Test Install:**
```
1. Chrome > Menu (⋮) > "Install GetYourShare"
2. Vérifier icône bureau/mobile
3. Lancer app installée (doit ouvrir standalone)
4. Mode avion: App doit fonctionner offline
```

---

## 🔌 CONFIGURATION SERVICES EXTERNES

### 1. Paiements CMI (Maroc)

**Étapes:**
```
1. S'inscrire sur cmi.co.ma
2. Fournir documents:
   - RC (Registre Commerce)
   - Patente
   - RIB bancaire
   - Carte CIN gérant
3. Attendre validation (3-5 jours)
4. Récupérer credentials:
   - Merchant ID
   - API Key
   - Secret Key
5. Ajouter au .env backend
```

**Test en sandbox:**
```ini
CMI_SANDBOX_MODE=true
CMI_MERCHANT_ID=test_merchant_123
CMI_API_KEY=test_api_key_xxx
CMI_SECRET_KEY=test_secret_xxx
```

### 2. Email SMTP (Gmail Business)

```
1. Créer compte Google Workspace
   business.google.com

2. Configurer domaine
   - DNS MX records
   - SPF record
   - DKIM signature

3. Créer compte noreply@getyourshare.ma

4. Activer "Application Passwords"
   - Google Account > Security
   - 2-Step Verification > App passwords
   - Générer mot de passe pour "Mail"

5. Ajouter au .env:
   SMTP_USER=noreply@getyourshare.ma
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

### 3. SMS Twilio

```
1. Créer compte twilio.com
2. Acheter numéro Maroc (+212)
3. Récupérer credentials:
   - Account SID
   - Auth Token
4. Configurer Messaging Service
5. Ajouter au .env
```

### 4. WhatsApp Business API

**Option 1: Twilio WhatsApp**
```
1. Twilio Console > Messaging > WhatsApp
2. Request Access (formulaire)
3. Attendre approbation (7-14 jours)
4. Configurer templates messages
5. Intégrer API
```

**Option 2: 360Dialog (Recommandé pour Maroc)**
```
1. S'inscrire sur 360dialog.com
2. Connecter compte WhatsApp Business
3. Récupérer API Key
4. Test en sandbox
```

### 5. Google Analytics 4

```
1. analytics.google.com
2. Créer propriété "GetYourShare"
3. Créer flux de données "Web"
4. Copier Measurement ID (G-XXXXXXXXX)
5. Ajouter au .env frontend:
   REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXX
```

### 6. Sentry (Error Tracking)

```
1. sentry.io/signup
2. Créer projet "getyourshare-frontend"
3. Créer projet "getyourshare-backend"
4. Récupérer DSN pour chaque:
   - Frontend DSN: https://xxx@sentry.io/111
   - Backend DSN: https://xxx@sentry.io/222
5. Ajouter aux .env respectifs
```

### 7. Firebase Cloud Messaging (Push)

```
1. console.firebase.google.com
2. Créer projet "GetYourShare"
3. Ajouter app Web
4. Activer Cloud Messaging
5. Récupérer:
   - Server Key (pour backend)
   - Sender ID (pour frontend)
   - firebase-messaging-sw.js config
6. Ajouter aux .env
```

---

## 🔐 VARIABLES D'ENVIRONNEMENT COMPLÈTES

### Backend `.env` (Complet)

```ini
# DATABASE
DATABASE_URL=postgresql://user:pass@localhost:5432/getyourshare
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# SECURITY
JWT_SECRET_KEY=xxx  # Générer avec secrets.token_urlsafe(64)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS & HOSTS
CORS_ORIGINS=http://localhost:3000,https://getyourshare.ma
ALLOWED_HOSTS=localhost,getyourshare.ma

# EMAIL
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@getyourshare.ma
SMTP_PASSWORD=xxx
SMTP_FROM=GetYourShare <noreply@getyourshare.ma>

# SMS
TWILIO_ACCOUNT_SID=xxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+212XXXXXXXXX

# WHATSAPP
WHATSAPP_API_KEY=xxx
WHATSAPP_PHONE_NUMBER=+212XXXXXXXXX

# PAYMENTS MAROC
CMI_MERCHANT_ID=xxx
CMI_API_KEY=xxx
CMI_SECRET_KEY=xxx

SG_MERCHANT_ID=xxx
SG_API_KEY=xxx
SG_SECRET_KEY=xxx

PAYZONE_MERCHANT_ID=xxx
PAYZONE_API_KEY=xxx
PAYZONE_SECRET_KEY=xxx

# PUSH NOTIFICATIONS
VAPID_PUBLIC_KEY=xxx
VAPID_PRIVATE_KEY=xxx
VAPID_SUBJECT=mailto:admin@getyourshare.ma

FCM_SERVER_KEY=xxx
FCM_SENDER_ID=xxx

# IA / ML
OPENAI_API_KEY=sk-xxx  # Optionnel
ANTHROPIC_API_KEY=sk-ant-xxx  # Optionnel

# ANALYTICS
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
MIXPANEL_TOKEN=xxx

# MONITORING
SENTRY_DSN=https://xxx@sentry.io/xxx
LOG_LEVEL=INFO

# CACHE & QUEUE
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# FILE STORAGE
AWS_ACCESS_KEY_ID=xxx  # Si S3
AWS_SECRET_ACCESS_KEY=xxx
AWS_BUCKET_NAME=getyourshare-uploads
```

### Frontend `.env` (Complet)

```ini
# API
REACT_APP_API_URL=http://localhost:8000

# SUPABASE
REACT_APP_SUPABASE_URL=https://xxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=xxx

# GOOGLE
REACT_APP_GOOGLE_MAPS_API_KEY=xxx
REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
REACT_APP_GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com

# SOCIAL
REACT_APP_FACEBOOK_APP_ID=xxx

# PAYMENTS
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_xxx

# MONITORING
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx
REACT_APP_MIXPANEL_TOKEN=xxx

# FEATURES
REACT_APP_FEATURE_GAMIFICATION=true
REACT_APP_FEATURE_MATCHING=true
REACT_APP_FEATURE_ANALYTICS_PRO=true
REACT_APP_FEATURE_MOBILE_PWA=true
REACT_APP_FEATURE_SALES_REP=true

# ENVIRONMENT
REACT_APP_ENV=development
```

---

## 🚀 DÉPLOIEMENT PRODUCTION

### Option 1: Serveur VPS (Digital Ocean, AWS EC2)

**1. Préparer Serveur**

```bash
# Se connecter au serveur
ssh root@VOTRE_IP

# Mettre à jour système
apt update && apt upgrade -y

# Installer dépendances
apt install -y nginx certbot python3-certbot-nginx
apt install -y nodejs npm python3 python3-pip postgresql redis-server

# Créer utilisateur dédié
adduser getyourshare
usermod -aG sudo getyourshare
su - getyourshare
```

**2. Cloner Projet**

```bash
# Installer Git
sudo apt install git

# Cloner repository
git clone https://github.com/VOTRE_USERNAME/getyourshare.git
cd getyourshare
```

**3. Configurer Backend**

```bash
cd backend

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Copier .env
cp .env.example .env
nano .env  # Éditer avec vraies valeurs production

# Lancer migrations
python migrate.py

# Tester
uvicorn main:app --host 0.0.0.0 --port 8000
```

**4. Configurer Systemd Service (Backend)**

```bash
# Créer fichier service
sudo nano /etc/systemd/system/getyourshare-backend.service
```

```ini
[Unit]
Description=GetYourShare Backend API
After=network.target

[Service]
Type=notify
User=getyourshare
WorkingDirectory=/home/getyourshare/getyourshare/backend
Environment="PATH=/home/getyourshare/getyourshare/backend/venv/bin"
ExecStart=/home/getyourshare/getyourshare/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl enable getyourshare-backend
sudo systemctl start getyourshare-backend
sudo systemctl status getyourshare-backend
```

**5. Build Frontend**

```bash
cd ../frontend

# Installer dépendances
npm install

# Créer .env production
cp .env.example .env.production
nano .env.production  # Éditer avec vraies valeurs

# Build
npm run build
# Génère dossier /build
```

**6. Configurer Nginx**

```bash
sudo nano /etc/nginx/sites-available/getyourshare
```

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name getyourshare.ma www.getyourshare.ma;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name getyourshare.ma www.getyourshare.ma;

    # SSL Certificates (Certbot auto-génère)
    ssl_certificate /etc/letsencrypt/live/getyourshare.ma/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/getyourshare.ma/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend (React Build)
    root /home/getyourshare/getyourshare/frontend/build;
    index index.html;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Frontend Routes (React Router)
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }

    # Static Assets (Cache 1 year)
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Backend API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket Support (si nécessaire)
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

```bash
# Activer site
sudo ln -s /etc/nginx/sites-available/getyourshare /etc/nginx/sites-enabled/

# Tester configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

**7. SSL Certificate (Let's Encrypt)**

```bash
# Obtenir certificat SSL gratuit
sudo certbot --nginx -d getyourshare.ma -d www.getyourshare.ma

# Certificat se renouvelle auto (cron job créé)
# Tester renouvellement
sudo certbot renew --dry-run
```

**8. Configuration DNS**

```
Chez votre registrar (Namecheap, GoDaddy, etc.):

A Record:
  Host: @
  Value: VOTRE_IP_SERVEUR
  TTL: 3600

A Record:
  Host: www
  Value: VOTRE_IP_SERVEUR
  TTL: 3600

MX Records (pour email):
  Priority: 1
  Value: aspmx.l.google.com

  Priority: 5
  Value: alt1.aspmx.l.google.com

  ... (autres MX selon votre provider)

TXT Record (SPF):
  Host: @
  Value: v=spf1 include:_spf.google.com ~all

TXT Record (DKIM):
  Host: google._domainkey
  Value: [Copier depuis Google Workspace]
```

---

### Option 2: Vercel + Supabase (Sans Serveur)

**1. Deploy Frontend sur Vercel**

```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Depuis /frontend
cd frontend

# Deploy
vercel

# Suivre instructions CLI:
# - Link to existing project? No
# - Project name: getyourshare
# - Directory: ./
# - Want to override settings? No

# Deploy production
vercel --prod
```

**Configuration Vercel:**
```
Project Settings > Environment Variables:
- REACT_APP_API_URL = https://api.getyourshare.ma
- REACT_APP_SUPABASE_URL = xxx
- REACT_APP_SUPABASE_ANON_KEY = xxx
- ... (toutes les variables .env)

Project Settings > Domains:
- Add domain: getyourshare.ma
- Add domain: www.getyourshare.ma
```

**2. Deploy Backend sur Railway/Render**

**Option A: Railway.app**
```
1. railway.app > New Project > Deploy from GitHub
2. Sélectionner repo getyourshare
3. Root directory: backend
4. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Ajouter toutes variables .env
6. Deploy
7. Récupérer URL: https://xxx.railway.app
```

**Option B: Render.com**
```
1. render.com > New Web Service
2. Connect GitHub repo
3. Root directory: backend
4. Build command: pip install -r requirements.txt
5. Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
6. Environment: Python 3.11
7. Ajouter variables .env
8. Create Web Service
```

---

## ✅ TESTS & VALIDATION

### 1. Tests Backend

```bash
cd backend

# Installer pytest
pip install pytest pytest-asyncio httpx

# Créer dossier tests/
mkdir tests
cd tests

# Créer fichier test_api.py
```

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_lead():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {
            "contact_name": "Test Lead",
            "contact_email": "test@example.com",
            "sales_rep_id": "xxx"
        }
        response = await ac.post("/api/sales/leads", json=data)
    assert response.status_code == 201
```

```bash
# Lancer tests
pytest

# Avec coverage
pytest --cov=.
```

### 2. Tests Frontend

```bash
cd frontend

# Tests déjà configurés avec Create React App
npm test

# Coverage
npm test -- --coverage

# End-to-End tests (Cypress)
npm install -D cypress

# Ouvrir Cypress
npx cypress open
```

### 3. Tests PWA

**Lighthouse Audit:**
```bash
# Installer Lighthouse
npm install -g lighthouse

# Build frontend
cd frontend
npm run build
serve -s build -l 3000

# Lancer audit
lighthouse http://localhost:3000 --view

# Score attendu:
# - Performance: 90+
# - Accessibility: 90+
# - Best Practices: 90+
# - SEO: 90+
# - PWA: 100 ✅
```

**Test Offline:**
```
1. Ouvrir Chrome DevTools
2. Application > Service Workers
3. Cocher "Offline"
4. Recharger page
5. ✅ App doit fonctionner
```

### 4. Checklist Validation Complète

```
BACKEND:
☐ API répond sur /health
☐ Base de données connectée
☐ Migrations appliquées
☐ RLS policies activées
☐ JWT authentication fonctionne
☐ Email SMTP configuré
☐ SMS provider configuré
☐ Paiements CMI/SG/PayZone configurés
☐ Push notifications configurées
☐ Logs Sentry activés

FRONTEND:
☐ Build sans erreurs
☐ Appels API backend OK
☐ Login/Register fonctionne
☐ Dashboards s'affichent
☐ Gamification widget OK
☐ Matching interface OK
☐ Analytics dashboard OK
☐ Sales rep dashboard OK

PWA:
☐ Manifest chargé
☐ Service Worker activé
☐ Offline mode fonctionne
☐ Background sync OK
☐ Push notifications OK
☐ Install prompt s'affiche
☐ Icônes toutes générées

PRODUCTION:
☐ HTTPS activé (SSL)
☐ Domaine configuré
☐ DNS propagé
☐ Email pro configuré
☐ Sauvegardes automatiques
☐ Monitoring actif
☐ Error tracking actif
☐ Analytics configuré
```

---

## 📊 MONITORING & MAINTENANCE

### 1. Logs Backend

```bash
# Systemd logs (si déployé sur VPS)
sudo journalctl -u getyourshare-backend -f

# Logs dans fichier
tail -f /var/log/getyourshare/backend.log
```

**Configurer rotation logs:**
```bash
sudo nano /etc/logrotate.d/getyourshare
```

```
/var/log/getyourshare/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 getyourshare getyourshare
    sharedscripts
}
```

### 2. Monitoring Uptime

**UptimeRobot (Gratuit):**
```
1. uptimerobot.com
2. Add Monitor:
   - Type: HTTPS
   - URL: https://getyourshare.ma
   - Interval: 5 minutes
3. Add Monitor:
   - Type: HTTPS
   - URL: https://api.getyourshare.ma/health
   - Interval: 5 minutes
```

### 3. Monitoring Performance

**New Relic (14 jours gratuit puis payant):**
```
1. newrelic.com
2. Install agent backend:
   pip install newrelic
3. newrelic-admin generate-config LICENSE_KEY newrelic.ini
4. Wrapper command:
   NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn main:app
```

### 4. Sauvegardes Automatiques

**PostgreSQL Backup:**
```bash
# Créer script backup
nano /home/getyourshare/scripts/backup_db.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/getyourshare/backups"
DB_NAME="getyourshare"
DB_USER="getyourshare_user"

# Créer backup
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compresser
gzip $BACKUP_DIR/backup_$DATE.sql

# Garder seulement 30 derniers backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload vers S3 (optionnel)
# aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://getyourshare-backups/
```

```bash
# Rendre exécutable
chmod +x /home/getyourshare/scripts/backup_db.sh

# Ajouter au crontab (daily à 2h du matin)
crontab -e
```

```cron
0 2 * * * /home/getyourshare/scripts/backup_db.sh
```

### 5. Maintenance Régulière

**Hebdomadaire:**
```bash
# Mettre à jour dépendances (vérifier changelog d'abord)
cd backend
source venv/bin/activate
pip list --outdated
pip install --upgrade PACKAGE_NAME

cd ../frontend
npm outdated
npm update
```

**Mensuel:**
```bash
# Analyser logs d'erreurs Sentry
# Vérifier métriques Analytics
# Vérifier performance (Lighthouse)
# Optimiser requêtes lentes (PostgreSQL EXPLAIN)
# Nettoyer fichiers uploads anciens
# Vérifier certificat SSL (90 jours Let's Encrypt)
```

---

## 🔍 TROUBLESHOOTING

### Problème: Backend ne démarre pas

```bash
# Vérifier logs
sudo journalctl -u getyourshare-backend -n 50

# Vérifier si port 8000 utilisé
sudo lsof -i :8000

# Tester connexion DB
psql -U getyourshare_user -d getyourshare -c "SELECT 1;"

# Vérifier variables .env
cat .env | grep -v "^#"
```

### Problème: Frontend ne charge pas API

```bash
# Vérifier CORS
curl -H "Origin: https://getyourshare.ma" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  https://api.getyourshare.ma/health

# Doit retourner:
# Access-Control-Allow-Origin: https://getyourshare.ma
```

### Problème: PWA ne s'installe pas

```
1. Chrome DevTools > Application
2. Manifest: Vérifier erreurs
3. Service Worker: Vérifier status "activated"
4. Vérifier HTTPS activé
5. Vérifier manifest.json accessible:
   curl https://getyourshare.ma/manifest.json
```

### Problème: Push notifications ne marchent pas

```
1. Vérifier permission accordée (browser)
2. Vérifier VAPID keys correctes
3. Tester avec curl:

curl -X POST https://fcm.googleapis.com/fcm/send \
  -H "Authorization: key=SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "DEVICE_TOKEN",
    "notification": {
      "title": "Test",
      "body": "Test notification"
    }
  }'
```

---

## 📚 RESSOURCES SUPPLÉMENTAIRES

- **Documentation FastAPI**: https://fastapi.tiangolo.com
- **Documentation React**: https://react.dev
- **Supabase Docs**: https://supabase.com/docs
- **PWA Builder**: https://www.pwabuilder.com
- **Nginx Config Generator**: https://www.digitalocean.com/community/tools/nginx
- **SSL Test**: https://www.ssllabs.com/ssltest/
- **Lighthouse CI**: https://github.com/GoogleChrome/lighthouse-ci

---

**📅 Document créé le:** 10 Novembre 2025
**✍️ Version:** 1.0
**🔄 Dernière mise à jour:** 10 Novembre 2025

---

## ✅ PROCHAINES ÉTAPES

Après avoir suivi ce guide:

1. ✅ Environnement local configuré
2. ✅ Base de données initialisée
3. ✅ Backend lancé et testé
4. ✅ Frontend lancé et testé
5. ✅ PWA configurée
6. ✅ Services externes connectés
7. ⏳ Déploiement production
8. ⏳ Monitoring actif
9. ⏳ Tests end-to-end
10. ⏳ Formation équipe

**Besoin d'aide? contact@getyourshare.ma**
