# 🚀 Guide de Déploiement GetYourShare

## Table des Matières

- [Prérequis](#prérequis)
- [Déploiement Local](#déploiement-local)
- [Déploiement Docker](#déploiement-docker)
- [Déploiement Cloud](#déploiement-cloud)
- [Configuration Production](#configuration-production)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Sécurité](#sécurité)
- [Troubleshooting](#troubleshooting)

## 📋 Prérequis

### Environnement de Développement

- **Node.js** 18+ LTS
- **Python** 3.9+
- **PostgreSQL** 14+ ou compte Supabase
- **Redis** 6+ (optionnel, pour cache)
- **Git** 2.40+
- **Docker** 20+ et Docker Compose (optionnel)

### Environnement de Production

- **Serveur Linux** (Ubuntu 22.04 LTS recommandé)
- **4GB RAM minimum** (8GB recommandé)
- **2 vCPU minimum** (4+ recommandé)
- **20GB disque** (SSD recommandé)
- **Nom de domaine** avec certificat SSL

## 💻 Déploiement Local

### 1. Clone du Projet

```bash
git clone https://github.com/epitaphe360/getyourshare-versio2.git
cd getyourshare-versio2
```

### 2. Configuration Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv .venv

# Activer environnement
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Windows CMD
.venv\Scripts\activate.bat
# Linux/Mac
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

### 3. Configuration Frontend

```bash
cd frontend

# Installer dépendances
npm install
# ou
yarn install
```

### 4. Variables d'Environnement

**Backend (.env)**

```env
# Supabase Database
SUPABASE_URL=https://xxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT Security
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=noreply@getyourshare.com

# Application
ENVIRONMENT=development
DEBUG=True
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Paiements (Production uniquement)
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
CMI_MERCHANT_ID=xxxxx
CMI_API_KEY=xxxxx

# Storage (optionnel)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=getyourshare-uploads

# Monitoring (Production)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

**Frontend (.env)**

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_SUPABASE_URL=https://xxxxxxxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_xxxxx
REACT_APP_ENVIRONMENT=development
```

### 5. Initialisation Base de Données

```bash
# Si utilisation de Supabase
# 1. Créer un nouveau projet sur https://app.supabase.com
# 2. Copier l'URL et les clés dans .env
# 3. Exécuter le schéma SQL dans l'éditeur Supabase

# Ou via psql
cd database
psql -U postgres -d getyourshare -f schema.sql
psql -U postgres -d getyourshare -f migrations/*.sql
```

### 6. Démarrage des Services

**Terminal 1 - Backend**

```bash
cd backend
python run.py

# OU avec uvicorn directement
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**

```bash
cd frontend
npm start

# L'app démarre sur http://localhost:3000
```

**Terminal 3 - Redis (optionnel)**

```bash
# Windows: Télécharger Redis depuis https://github.com/microsoftarchive/redis/releases
# Linux/Mac
redis-server

# OU avec Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 7. Vérification

```bash
# Backend health check
curl http://localhost:8000/health

# Backend API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:3000
```

## 🐳 Déploiement Docker

### 1. Build des Images

**Dockerfile Backend** (`Dockerfile.backend`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Dockerfile Frontend** (`Dockerfile.frontend`)

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY frontend/ .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: gys-backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - gys-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: gys-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    restart: unless-stopped
    networks:
      - gys-network

  redis:
    image: redis:7-alpine
    container_name: gys-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - gys-network

networks:
  gys-network:
    driver: bridge

volumes:
  redis-data:
```

### 2. Build et Lancement

```bash
# Build images
docker-compose build

# Démarrer services
docker-compose up -d

# Vérifier status
docker-compose ps

# Voir logs
docker-compose logs -f

# Arrêter services
docker-compose down
```

### 3. Configuration Nginx (Production)

**nginx.conf**

```nginx
server {
    listen 80;
    server_name getyourshare.com www.getyourshare.com;
    
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files cache
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

## ☁️ Déploiement Cloud

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Vercel (Frontend)

```bash
# 1. Installer Vercel CLI
npm i -g vercel

# 2. Login
vercel login

# 3. Déployer
cd frontend
vercel

# 4. Configuration
# Ajouter variables d'environnement dans Vercel Dashboard
# - REACT_APP_API_URL
# - REACT_APP_SUPABASE_URL
# - REACT_APP_SUPABASE_ANON_KEY

# 5. Production deploy
vercel --prod
```

**vercel.json**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### Railway (Backend)

```bash
# 1. Installer Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Init projet
cd backend
railway init

# 4. Ajouter variables d'environnement
railway variables set SUPABASE_URL=xxx
railway variables set SUPABASE_KEY=xxx
railway variables set SECRET_KEY=xxx

# 5. Deploy
railway up
```

**railway.json**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Option 2: DigitalOcean App Platform

```yaml
# .do/app.yaml
name: getyourshare
region: fra
services:
  - name: backend
    github:
      repo: epitaphe360/getyourshare-versio2
      branch: main
      deploy_on_push: true
    source_dir: backend
    run_command: uvicorn server:app --host 0.0.0.0 --port 8080
    environment_slug: python
    instance_size_slug: basic-xxs
    instance_count: 2
    http_port: 8080
    health_check:
      http_path: /health
    envs:
      - key: SUPABASE_URL
        scope: RUN_TIME
        value: ${SUPABASE_URL}
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
        value: ${SECRET_KEY}
  
  - name: frontend
    github:
      repo: epitaphe360/getyourshare-versio2
      branch: main
    source_dir: frontend
    build_command: npm run build
    run_command: npm start
    environment_slug: node-js
    instance_size_slug: basic-xxs
    routes:
      - path: /
    envs:
      - key: REACT_APP_API_URL
        scope: RUN_AND_BUILD_TIME
        value: ${backend.PUBLIC_URL}

databases:
  - name: redis
    engine: REDIS
    production: true
```

### Option 3: AWS (EC2 + RDS + S3)

#### 1. Setup EC2

```bash
# 1. Créer instance EC2 (Ubuntu 22.04 LTS)
# Type: t3.medium (2 vCPU, 4GB RAM)

# 2. SSH dans instance
ssh -i key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 3. Installer dépendances
sudo apt update
sudo apt install -y python3-pip nodejs npm nginx certbot python3-certbot-nginx redis-server

# 4. Clone projet
git clone https://github.com/epitaphe360/getyourshare-versio2.git
cd getyourshare-versio2

# 5. Setup backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 6. Setup frontend
cd ../frontend
npm install
npm run build

# 7. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/getyourshare
sudo ln -s /etc/nginx/sites-available/getyourshare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 8. SSL avec Let's Encrypt
sudo certbot --nginx -d getyourshare.com -d www.getyourshare.com

# 9. Setup systemd service
sudo nano /etc/systemd/system/getyourshare-backend.service
```

**getyourshare-backend.service**

```ini
[Unit]
Description=GetYourShare Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/getyourshare-versio2/backend
Environment="PATH=/home/ubuntu/getyourshare-versio2/backend/.venv/bin"
ExecStart=/home/ubuntu/getyourshare-versio2/backend/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl enable getyourshare-backend
sudo systemctl start getyourshare-backend
sudo systemctl status getyourshare-backend
```

## 🔧 Configuration Production

### 1. Variables d'Environnement

```env
# CRITIQUE: Toujours utiliser des valeurs FORTES en production
SECRET_KEY=$(openssl rand -hex 32)
SUPABASE_SERVICE_KEY=  # Jamais exposer au frontend
STRIPE_SECRET_KEY=sk_live_xxx  # Pas sk_test

# Sécurité
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://getyourshare.com,https://www.getyourshare.com

# Performance
REDIS_URL=redis://production-redis:6379
DATABASE_POOL_SIZE=20
```

### 2. Sécurité Checklist

- [ ] Utiliser HTTPS (certificat SSL valide)
- [ ] Changer toutes les clés/secrets par défaut
- [ ] Activer rate limiting
- [ ] Configurer CORS correctement
- [ ] Activer 2FA pour comptes admin
- [ ] Sauvegardes automatiques journalières
- [ ] Monitoring des erreurs (Sentry)
- [ ] Logs centralisés
- [ ] Firewall configuré (UFW ou Security Groups)
- [ ] Mises à jour sécurité automatiques

### 3. Performance Checklist

- [ ] Activer compression Gzip/Brotli
- [ ] Cache Redis configuré
- [ ] CDN pour assets statiques
- [ ] Database connection pooling
- [ ] Image optimization
- [ ] Code splitting frontend
- [ ] Lazy loading composants
- [ ] Service Worker PWA

## 📊 Monitoring

### Setup Prometheus + Grafana

**docker-compose.monitoring.yml**

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
```

**prometheus.yml**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Logs avec Loki

```bash
# Installer Loki
docker run -d --name=loki -p 3100:3100 grafana/loki:latest

# Configurer backend pour envoyer logs
# Voir logging_config.py
```

## 💾 Backup & Recovery

### Backup Automatique

**backup.sh**

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="getyourshare"

# Créer dossier backup
mkdir -p $BACKUP_DIR

# Backup PostgreSQL (via Supabase)
# Utiliser Supabase Dashboard ou API

# Backup Redis
redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup fichiers uploads (si local)
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /app/uploads

# Nettoyer anciens backups (>30 jours)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Cron Job**

```bash
# Ajouter au crontab
crontab -e

# Backup quotidien à 2h du matin
0 2 * * * /home/ubuntu/backup.sh >> /var/log/backup.log 2>&1
```

### Recovery

```bash
# Restore PostgreSQL
psql -U postgres -d getyourshare -f backup_20240101.sql

# Restore Redis
redis-cli --rdb /backups/redis_20240101.rdb

# Restore uploads
tar -xzf uploads_20240101.tar.gz -C /app/
```

## 🔍 Troubleshooting

### Problèmes Courants

#### Backend ne démarre pas

```bash
# Vérifier logs
docker-compose logs backend

# Vérifier port
netstat -tulpn | grep 8000

# Tester connexion DB
python -c "from supabase_client import supabase; print(supabase.table('users').select('count').execute())"
```

#### Frontend erreur 502

```bash
# Vérifier Nginx
sudo nginx -t
sudo systemctl status nginx

# Vérifier proxy backend
curl http://localhost:8000/health
```

#### Connexion DB lente

```bash
# Analyser queries lentes
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Activer query logging
ALTER DATABASE getyourshare SET log_min_duration_statement = 1000;
```

#### Cache Redis issues

```bash
# Vérifier connexion
redis-cli ping

# Vider cache
redis-cli FLUSHDB

# Vérifier mémoire
redis-cli INFO memory
```

### Logs Utiles

```bash
# Backend logs
tail -f backend/logs/app.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Systemd service logs
journalctl -u getyourshare-backend -f
```

---

**📝 Checklist Déploiement Final**

- [ ] Tests passent localement
- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée
- [ ] Migrations appliquées
- [ ] SSL/TLS configuré
- [ ] Monitoring actif
- [ ] Backups configurés
- [ ] Documentation à jour
- [ ] DNS configuré
- [ ] Health checks OK
- [ ] Performance testée (load test)
- [ ] Sécurité auditée

**🚀 Production Ready!**
