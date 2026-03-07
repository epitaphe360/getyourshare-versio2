# TESTS DE SÉCURITÉ RECOMMANDÉS

Guide pour tester et valider les corrections de sécurité apportées.

---

## 1️⃣ TESTS MANUELS RAPIDES

### Test 1: Vérifier JWT Secret
```bash
# Vérifier qu'aucun fallback secret n'existe
grep -r "fallback-secret" /backend/

# Résultat attendu: Aucun résultat (grep retourne code 1)
```

### Test 2: Vérifier httpOnly Cookies
```bash
# Faire un login et vérifier le header Set-Cookie
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  -v 2>&1 | grep -i "set-cookie"

# Résultat attendu:
# Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Strict
# Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict
```

### Test 3: Vérifier Tokens NOT en localStorage
```javascript
// Dans la console du navigateur
localStorage.getItem('token')       // Résultat: null
localStorage.getItem('auth_token')  // Résultat: null
sessionStorage.getItem('user')      // Résultat: "{"id":"...","email":"..."}"
```

### Test 4: Vérifier Messages d'Erreur Génériques
```bash
# Envoyer une requête invalide
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer invalid_token" \
  2>&1 | grep -i "error"

# Résultat attendu: Message générique type:
# {"error":"Internal server error","message":"An unexpected error occurred..."}
# PAS de stack trace, PAS de détails techniques
```

### Test 5: Vérifier CSP Headers
```bash
# Vérifier CSP (pas unsafe-inline/unsafe-eval)
curl -I https://yoursite.com | grep -i "content-security-policy"

# Résultat attendu: AUCUN 'unsafe-inline' ou 'unsafe-eval'
# Exemple:
# content-security-policy: default-src 'self'; script-src 'self' 'nonce-...'; ...
```

### Test 6: Vérifier HSTS Header
```bash
curl -I https://yoursite.com | grep -i "strict-transport-security"

# Résultat attendu:
# strict-transport-security: max-age=31536000; includeSubDomains; preload
```

### Test 7: Vérifier X-Frame-Options
```bash
curl -I https://yoursite.com | grep -i "x-frame-options"

# Résultat attendu:
# x-frame-options: DENY
```

---

## 2️⃣ TESTS AVEC OUTILS

### OWASP ZAP - Scan Automatisé

```bash
# Installation
docker pull owasp/zap2docker-stable

# Scan baseline (rapide)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://your-api.com \
  -r report.html

# Scan plus approfondi
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://your-api.com \
  -r report.html

# Résultats attendus:
# - Pas de "CRITICAL" findings
# - "Missing CSP header" = RÉSOLU après correction
# - "Token sent in URL" = N/A (token en cookie)
```

### npm audit - Dépendances Frontend

```bash
cd /frontend

# Vérifier les vulnérabilités
npm audit

# Fixer automatiquement
npm audit fix

# Résultats attendus:
# 0 vulnerabilities found
```

### pip-audit - Dépendances Backend

```bash
cd /backend

# Vérifier les vulnérabilités
pip-audit

# Ou avec requirements.txt
pip-audit -r requirements.txt

# Résultats attendus:
# Found 0 known vulnerabilities
```

### Semgrep - SAST (Static Code Analysis)

```bash
# Installation
brew install semgrep  # ou voir https://semgrep.dev/r/install

# Scan sécurité
semgrep --config=p/security-audit

# Scan OWASP Top 10
semgrep --config=p/owasp-top-ten

# Scan CWE Top 25
semgrep --config=p/cwe-top-25
```

---

## 3️⃣ TESTS D'API AVEC BURP SUITE

### Configuration Proxy

```
1. Démarrer Burp Suite Community Edition
2. Configurer navigateur: Proxy → 127.0.0.1:8080
3. Aller à: http://burp
4. CA Certificate → Télécharger et installer
```

### Tests Manuels dans Burp

#### Test 1: CSRF Protection
```
1. Envoyer une requête POST /api/auth/login
2. Vérifier absence de X-CSRF-Token header
3. Résultat: CSRF protection OK (httpOnly cookies suffisent)
```

#### Test 2: Authentication Bypass
```
1. Intercepter une requête authentifiée
2. Supprimer le header Authorization
3. Modifier access_token cookie en invalide
4. Résultat: 401 Unauthorized (OK)
```

#### Test 3: Token Manipulation
```
1. Copier un token d'accès valide
2. Changer un caractère du payload (JWT)
3. Envoyer la requête
4. Résultat: 401 Unauthorized (signature invalide) (OK)
```

#### Test 4: CORS Misconfiguration
```
Envoyer requête CORS:
Origin: https://attacker.com

curl -H "Origin: https://attacker.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://your-api.com/api/users \
  -v

# Résultat attendu:
# Access-Control-Allow-Origin: NOT attacker.com
# OU absence du header (OK)
```

---

## 4️⃣ TESTS DE SÉCURITÉ SPÉCIFIQUES

### Test XSS - localStorage Token

```javascript
// Dans la console (après correction)
// localStorage ne devrait pas contenir de token

// Test 1: localStorage vide
Object.keys(localStorage)
// Résultat attendu: Aucune clé contenant 'token'

// Test 2: Cookie HttpOnly non accessible
document.cookie
// Résultat attendu: Pas de access_token (car HttpOnly)

// Test 3: Vérifier que les requests incluent le token
// Les cookies sont automatiquement envoyés (withCredentials: true)
```

### Test Upload Validation

```bash
# Test 1: Extension non autorisée
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.exe"
# Résultat attendu: 400 "File type not allowed"

# Test 2: MIME type spooféd (image.jpg qui est en réalité .exe)
# Créer un fichier avec extension .jpg mais contenu .exe
# Résultat attendu: 400 "File content doesn't match" (après correction)

# Test 3: Fichier trop gros
# Uploader fichier > 5MB
# Résultat attendu: 400 "File too large"

# Test 4: Erreur upload ne révèle pas détails
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer invalid"
# Résultat attendu: Message générique (pas de détail d'erreur)
```

### Test Refresh Token

```bash
# Test 1: Obtenir tokens
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  -c cookies.txt)

# Test 2: Vérifier cookies
cat cookies.txt
# Résultat attendu: access_token ET refresh_token

# Test 3: Utiliser refresh token après expiration access_token
sleep 1000  # Attendre expiration (15 min)

curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt
# Résultat attendu: 200 OK + nouveau access_token

# Test 4: Refresh token expiré
sleep 604801  # Attendre 7 jours + 1 sec
curl -X POST http://localhost:8000/api/auth/refresh \
  -b cookies.txt
# Résultat attendu: 401 "Refresh token expired"
```

### Test Rate Limiting

```bash
# Tester limite login (5/min)
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
done

# Résultat attendu:
# Premiers 5: 401
# Après: 429 "Rate limit exceeded" + Retry-After header
```

---

## 5️⃣ TESTS EN PRODUCTION

### Health Check
```bash
curl https://your-api.com/health
# Résultat attendu: 200 OK
```

### HTTPS Redirect
```bash
curl -I http://your-api.com
# Résultat attendu: 301 Moved → https://your-api.com
```

### SSL/TLS Quality
```bash
# Utiliser ssllabs.com
# Ou tester localement:
nmap --script ssl-enum-ciphers -p 443 your-api.com

# Résultat attendu:
# - TLS 1.2+ ONLY
# - Ciphers forts (no RC4, no DES)
# - HSTS activé
# - OCSP stapling
```

### Certificat SSL
```bash
openssl s_client -connect your-api.com:443 -servername your-api.com

# Vérifier:
# - Certificat valide (pas self-signed)
# - Domaines corrects dans CN et SAN
# - Pas expiré
# - Chaîne complète
```

---

## 6️⃣ TESTS DE CHARGE / DOSNOS

### Avec Apache Bench

```bash
# Test normal (100 requêtes)
ab -n 100 -c 10 https://your-api.com/health

# Test avec concurrence élevée
ab -n 1000 -c 100 https://your-api.com/health

# Résultat attendu:
# Pas de crash
# Rate limit respecté (429 pour certaines)
```

### Avec Apache JMeter

```bash
# À configurer via GUI
# Tester endpoints sensibles avec load
# Vérifier que rate limiting fonctionne
```

---

## 7️⃣ TESTS AUTOMATISÉS CI/CD

### Fichier: .github/workflows/security.yml

```yaml
name: Security Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    # npm audit
    - name: Frontend Audit
      run: |
        cd frontend
        npm ci
        npm audit --audit-level=moderate

    # pip-audit
    - name: Backend Audit
      run: |
        cd backend
        pip install pip-audit
        pip-audit

    # Semgrep
    - name: SAST with Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/owasp-top-ten
          p/cwe-top-25

    # Grep secrets
    - name: Check for Hardcoded Secrets
      run: |
        ! grep -r "fallback-secret" backend/
        ! grep -r "password.*=.*['\"]" backend/ | grep -v "password_hash"
        ! grep -r "localStorage.setItem.*token" frontend/

    # Lint
    - name: ESLint Frontend
      run: |
        cd frontend
        npm ci
        npm run lint -- --max-warnings=0

    # Unit Tests
    - name: Unit Tests Frontend
      run: |
        cd frontend
        npm run test -- --coverage

    # Integration Tests
    - name: Integration Tests Backend
      run: |
        cd backend
        pip install -r requirements.txt
        pytest tests/ -v --cov
```

---

## 8️⃣ CHECKLIST FINALE AVANT PRODUCTION

- [ ] npm audit = 0 vulnérabilités
- [ ] pip-audit = 0 vulnérabilités
- [ ] Semgrep = 0 findings
- [ ] Pas de "fallback-secret" en code
- [ ] JWT Secret configuré en variable d'environnement
- [ ] Tokens en httpOnly cookies (NOT localStorage)
- [ ] Messages d'erreur génériques en production
- [ ] CSP headers sans unsafe-inline/unsafe-eval
- [ ] HSTS activé
- [ ] X-Frame-Options: DENY
- [ ] HTTPS redirect configuré
- [ ] Rate limiting testé (429 responses)
- [ ] Upload validation testé
- [ ] CORS restrictif à liste blanche
- [ ] Refresh token endpoint testé
- [ ] Logout invalide tokens
- [ ] Sentry monitoring configuré
- [ ] WAF activé (si disponible)
- [ ] Logs structurés (JSON)
- [ ] Pas d'informations sensibles dans logs
- [ ] SSL/TLS grade A+ (ssllabs.com)

---

## RESSOURCES

### Docs Officielles
- OWASP Top 10 2021: https://owasp.org/www-project-top-ten/
- OWASP API Security Top 10: https://owasp.org/www-project-api-security/
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- React Security: https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml

### Outils Testings
- OWASP ZAP: https://www.zaproxy.org/
- Burp Suite Community: https://portswigger.net/burp/communitydownload
- Semgrep: https://semgrep.dev/
- SSL Labs: https://www.ssllabs.com/ssltest/

### JWT Security
- JWT.io: https://jwt.io/
- RFC 8725: JWT Best Practices https://tools.ietf.org/html/rfc8725

### Références
- CWE Top 25: https://cwe.mitre.org/top25/
- SANS Top 25: https://www.sans.org/
- HackerOne: https://www.hackerone.com/resources
