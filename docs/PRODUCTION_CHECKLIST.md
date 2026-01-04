# ✅ CHECKLIST RAPIDE - Mise en Production ShareYourSales

> **Utilisez cette checklist pour suivre votre progression vers la production**

---

## 🔴 BLOQUEURS CRITIQUES (OBLIGATOIRE)

### 1. Configuration Paiements
- [ ] Créer compte Stripe production
- [ ] Obtenir `STRIPE_SECRET_KEY` live
- [ ] Obtenir `STRIPE_WEBHOOK_SECRET`
- [ ] Configurer clés CMI (Maroc)
- [ ] Tester paiement test complet
- [ ] Vérifier webhooks fonctionnent

### 2. Configuration Email
- [ ] Choisir: Resend OU SMTP
- [ ] Obtenir `RESEND_API_KEY` OU configurer SMTP
- [ ] Vérifier domaine shareyoursales.ma
- [ ] Configurer SPF/DKIM
- [ ] Tester email bienvenue
- [ ] Tester réinitialisation mot de passe
- [ ] Tester notifications

### 3. Variables d'Environnement
- [ ] Définir `APP_URL=https://api.shareyoursales.ma`
- [ ] Définir `FRONTEND_URL=https://shareyoursales.ma`
- [ ] Définir `REACT_APP_API_URL=https://api.shareyoursales.ma`
- [ ] Changer `ALLOWED_ORIGINS` (enlever wildcard *)
- [ ] Vérifier toutes les variables .env.production

### 4. Backups Base de Données
- [ ] Activer backups Supabase OU créer script
- [ ] Configurer backup quotidien
- [ ] **TESTER restauration backup** (important!)
- [ ] Documenter procédure de recovery
- [ ] Définir politique rétention (30 jours)

### 5. SSL/HTTPS
- [ ] Configurer certificat SSL (Railway auto)
- [ ] Activer redirection HTTP → HTTPS
- [ ] Tester sur https://www.ssllabs.com/
- [ ] Vérifier certificat wildcard

---

## 🟡 HAUTE PRIORITÉ (RECOMMANDÉ)

### 6. Authentification 2FA
- [ ] Finaliser flow TOTP
- [ ] Ajouter codes de récupération
- [ ] Tester activation/désactivation
- [ ] Documenter pour utilisateurs

### 7. Monitoring
- [ ] Créer compte Sentry.io
- [ ] Configurer `SENTRY_DSN`
- [ ] Tester capture d'erreurs
- [ ] Configurer alertes (email/Slack)

### 8. Tests
- [ ] Exécuter `pytest --cov=backend`
- [ ] Vérifier couverture > 70%
- [ ] Tests E2E sur staging
- [ ] Tests de charge (100 users)

### 9. Redis
- [ ] Provisionner Redis (Railway/Upstash)
- [ ] Configurer `REDIS_URL`
- [ ] Tester rate limiting
- [ ] Tester cache

---

## 🟢 POST-LANCEMENT

### 10. Performance
- [ ] CDN pour images (Cloudinary/Vercel)
- [ ] Compression Gzip/Brotli
- [ ] Optimiser requêtes DB lentes
- [ ] Cache headers HTTP

### 11. Logs
- [ ] ELK Stack ou Loki
- [ ] Politique rétention 30 jours
- [ ] Dashboard monitoring

### 12. Documentation
- [ ] Runbooks incidents
- [ ] Documentation API Swagger
- [ ] Guide utilisateur

### 13. RGPD
- [ ] Export données utilisateur
- [ ] Suppression compte
- [ ] DPA pour B2B

---

## 📊 PROGRESSION

**Cochez les cases ci-dessus et calculez votre score:**

```
Bloqueurs Critiques (5 items):    ☐☐☐☐☐  __/5  (100% requis)
Haute Priorité (4 items):         ☐☐☐☐   __/4  (75% recommandé)
Post-Lancement (4 items):         ☐☐☐☐   __/4  (optionnel)

TOTAL: __/13

Score: ___%
```

### Échelle de Préparation

- **0-40%**: ❌ Pas prêt - Beaucoup de travail
- **40-70%**: ⚠️ En cours - Continuer configuration
- **70-85%**: ⚠️ Presque prêt - Tests finaux
- **85-100%**: ✅ Prêt pour production!

---

## 🚀 READY TO LAUNCH?

**Avant de dire OUI, vérifiez:**

- [x] Tous les bloqueurs critiques résolus (5/5)
- [x] Au moins 3/4 haute priorité complétés
- [x] Tests E2E passent à 100%
- [x] Backup testé et restauration validée
- [x] Équipe d'astreinte disponible 24/7
- [x] Plan de rollback documenté

**Si tous cochés → GO! 🚀**

Sinon → Continuez la préparation! ⏳
