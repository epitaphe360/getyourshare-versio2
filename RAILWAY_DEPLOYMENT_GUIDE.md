# 🚂 Guide de Déploiement Railway - GetYourShare

Guide complet pour déployer GetYourShare sur Railway avec sécurité niveau production mondial 400%.

## 📋 Prérequis

- Compte Railway (https://railway.app)
- Compte Supabase configuré
- Compte Stripe (mode live)
- Domaine personnalisé (recommandé)

---

## 🔐 Variables d'Environnement CRITIQUES

### Backend Railway

```bash
# Security (PRIORITÉ MAX)
ENVIRONMENT=production
JWT_SECRET=<générer-32-chars-minimum>
REFRESH_TOKEN_SECRET=<générer-différent-32-chars>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

Voir `.env.production.example` pour la liste complète.

---

## 🚀 Déploiement Rapide

### 1. Backend sur Railway

```bash
# Root Directory: /backend
# Build: pip install -r requirements.txt
# Start: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### 2. Frontend sur Vercel

```bash
cd frontend
vercel --prod

# Variables Vercel:
# REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

### 3. Vérifier Health

```bash
curl https://your-backend.railway.app/health
# → {"status": "healthy"}
```

---

## ✅ Checklist Production

- [ ] JWT_SECRET configuré (32+ chars unique)
- [ ] httpOnly cookies activés
- [ ] CSRF protection ON
- [ ] Security headers activés
- [ ] CORS whitelist stricte
- [ ] HTTPS forcé
- [ ] Supabase RLS activé
- [ ] Stripe en mode live
- [ ] Tests 4 dashboards OK

**Déploiement niveau mondial 400% ✨**
