# SCRIPTS DE CORRECTION - AUDIT DE SÉCURITÉ

Guide pour appliquer les corrections trouvées lors de l'audit de sécurité.

---

## 1️⃣ GÉNÉRATION DU NOUVEAU JWT SECRET

```bash
#!/bin/bash
# Générer un nouveau JWT_SECRET sécurisé

NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

echo "Nouveau JWT_SECRET généré:"
echo "JWT_SECRET=$NEW_SECRET"
echo ""
echo "Ajouter cette ligne à votre fichier .env ou au système de variables d'environnement"
echo ""
echo "IMPORTANT:"
echo "1. Ne pas committer le secret en Git"
echo "2. Ajouter uniquement au fichier .env (ajouté à .gitignore)"
echo "3. Ou utiliser un gestionnaire de secrets (Vault, Railway, etc.)"
```

**Exécution**:
```bash
bash <<'EOF'
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
echo "JWT_SECRET=$NEW_SECRET"
EOF
```

---

## 2️⃣ CORRIGER LES JWT SECRETS HARDCODÉS

### Script Python pour remplacer les fallback

```python
#!/usr/bin/env python3
"""
Script pour remplacer les JWT_SECRET fallback hardcodés
ATTENTION: À exécuter dans le répertoire /backend
"""

import os
import re

files_to_fix = [
    "server.py",
    "auth.py",
    "subscription_middleware.py",
    "server_mock_backup.py",
]

# Pattern à chercher et remplacer
old_pattern = r'JWT_SECRET\s*=\s*os\.getenv\("JWT_SECRET",\s*"fallback-secret-please-set-env-variable"\)'
new_code = '''# JWT_SECRET - DOIT être défini en variable d'environnement
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    import sys
    print("❌ ERREUR CRITIQUE: JWT_SECRET doit être défini dans les variables d'environnement")
    print("   Exécutez et ajoutez à votre .env:")
    print("   python3 -c 'import secrets; print(secrets.token_urlsafe(64))'")
    sys.exit(1)

if len(JWT_SECRET) < 32:
    import sys
    print("❌ ERREUR: JWT_SECRET doit faire au minimum 32 caractères")
    sys.exit(1)'''

for filename in files_to_fix:
    filepath = f"backend/{filename}"
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        # Remplacer le pattern
        new_content = re.sub(old_pattern, new_code, content)

        if content != new_content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"✅ Corrigé: {filepath}")
        else:
            print(f"⚠️  Aucun changement: {filepath}")
    else:
        print(f"❌ Fichier non trouvé: {filepath}")
```

**Exécution**:
```bash
python3 /path/to/script.py
```

---

## 3️⃣ AJOUTER EXCEPTION HANDLER GLOBAL

### Ajouter au backend/server.py

```python
# Ajouter après la création de l'app FastAPI

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import uuid

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Gestionnaire global d'exceptions
    - Log les détails pour debugging
    - Répond avec message générique à l'utilisateur
    """
    # Générer un request ID unique pour le suivi
    request_id = str(uuid.uuid4())

    # Logger les détails complets (pour vous, pas pour l'utilisateur)
    logger.error(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
        },
        exc_info=exc,
        stack_info=True
    )

    # Répondre avec message générique
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "request_id": request_id,  # Pour que l'utilisateur puisse reporter l'erreur
        }
    )

# Pour les HTTPException, aussi renvoyer format générique
from fastapi import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire pour HTTPException"""
    request_id = str(uuid.uuid4())

    # Ne PAS exposer les détails sensibles
    if exc.status_code >= 500:
        logger.error(
            "http_exception",
            extra={
                "request_id": request_id,
                "status": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
            }
        )
        # Message générique pour erreurs serveur
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Server error",
                "message": "An error occurred. Please try again later.",
                "request_id": request_id,
            }
        )
    else:
        # Pour erreurs client (4xx), détail minimal
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Error",
                "message": "Invalid request",
            }
        )
```

---

## 4️⃣ MIGRER TOKENS EN HTTPONLY COOKIES

### Fichier: backend/server.py - Modifier login endpoint

```python
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    """Login avec httpOnly cookies au lieu de localStorage"""
    # ... vérification credentials ...

    user = get_user_by_email(login_data.email)
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Créer les tokens
    access_token = create_access_token(
        {"sub": user["id"]},
        expires_delta=timedelta(minutes=15)  # Court!
    )
    refresh_token = create_refresh_token(user["id"])

    # Préparer la réponse
    response = JSONResponse(
        content={
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "name": user.get("name")
            }
        }
    )

    # Ajouter tokens en httpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="strict",
        max_age=900,  # 15 minutes
        domain=None  # À adapter selon votre domaine
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="strict",
        max_age=604800,  # 7 days
        domain=None
    )

    return response
```

### Fichier: frontend/src/hooks/useAuth.js - Adapter

```javascript
const login = useCallback(async (email, password) => {
  setLoading(true);
  setError(null);

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',  // IMPORTANT: Inclure les cookies
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Login failed');
    }

    const data = await response.json();
    const { user: userData } = data;

    // NE PAS stocker le token en localStorage
    // Le token est dans le cookie httpOnly (envoyé automatiquement)

    // Stocker SEULEMENT les données utilisateur non-sensibles
    sessionStorage.setItem('user', JSON.stringify(userData));

    setUser(userData);
    return userData;
  } catch (err) {
    setError(err.message);
    throw err;
  } finally {
    setLoading(false);
  }
}, []);
```

### Fichier: frontend/src/utils/api.js - Adapter

```javascript
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,  // IMPORTANT: Inclure les cookies automatiquement
});

// Les interceptors n'ont plus besoin de gérer le token
// Il est envoyé automatiquement dans les cookies
```

---

## 5️⃣ CORRIGER LE CSP STRICT

### Fichier: backend/middleware/security.py

```python
import secrets

async def security_headers_middleware(request: Request, call_next: Callable):
    """Middleware de sécurité avec CSP STRICT"""

    # Générer un nonce pour les scripts inline de cette requête
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce

    response = await call_next(request)

    # CSP STRICT - Pas d'unsafe-inline ou unsafe-eval
    csp_directives = [
        "default-src 'self'",
        f"script-src 'self' 'nonce-{nonce}' https://js.stripe.com https://cdn.jsdelivr.net",
        f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: https: blob:",
        "connect-src 'self' https://api.stripe.com https://api.anthropic.com https://api.openai.com",
        "frame-src 'self' https://js.stripe.com",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests"
    ]

    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # HSTS - Force HTTPS
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # Autres headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"  # Plus strict que SAMEORIGIN
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(self), usb=()"

    return response
```

---

## 6️⃣ AJOUTER REFRESH TOKEN ENDPOINT

### Fichier: backend/server.py

```python
import redis

# Client Redis (pour token blacklist)
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

@app.post("/api/auth/refresh")
async def refresh_access_token(request: Request):
    """Endpoint pour refresher le token d'accès"""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("sub")

        # Créer nouveau access token
        new_access_token = create_access_token(
            {"sub": user_id},
            expires_delta=timedelta(minutes=15)
        )

        response = JSONResponse({"success": True})
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=os.getenv("ENVIRONMENT") == "production",
            samesite="strict",
            max_age=900
        )

        return response

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout: invalider les tokens"""
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # Ajouter à blacklist
            redis_client.setex(
                f"blacklist:{refresh_token}",
                604800,
                "1"
            )
        except jwt.DecodeError:
            pass

    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie("access_token", httponly=True, secure=True, samesite="strict")
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="strict")

    return response
```

---

## 7️⃣ VALIDER LES UPLOADS CORRECTEMENT

### Fichier: backend/upload_endpoints.py

```python
import magic
import mimetypes

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "general",
    payload: dict = Depends(verify_token)
):
    """Upload avec validation complète"""

    # Extensions blanches
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Taille limite
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    # Vérifier type MIME réel
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(contents)

    allowed_mimes = {
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".png": {"image/png"},
        ".gif": {"image/gif"},
        ".pdf": {"application/pdf"}
    }

    if detected_mime not in allowed_mimes.get(file_extension, set()):
        logger.warning(f"MIME mismatch: {file.filename} detected as {detected_mime}")
        raise HTTPException(status_code=400, detail="File content doesn't match file type")

    # Vérifier magic bytes (file signatures)
    magic_bytes = {
        b'\xff\xd8\xff': '.jpg',
        b'\x89PNG': '.png',
        b'GIF8': '.gif',
        b'%PDF': '.pdf'
    }

    for magic_sig, ext in magic_bytes.items():
        if contents.startswith(magic_sig) and ext != file_extension:
            logger.warning(f"File signature mismatch: {file.filename}")
            raise HTTPException(status_code=400, detail="File signature mismatch")

    # Générer nom unique
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"{folder}/{datetime.now().strftime('%Y/%m')}/{safe_filename}"

    try:
        supabase = get_supabase_client()
        result = supabase.storage.from_("uploads").upload(
            path=file_path,
            file=contents,
            file_options={"content-type": detected_mime}
        )

        public_url = supabase.storage.from_("uploads").get_public_url(file_path)

        return {
            "success": True,
            "filename": safe_filename,
            "path": file_path,
            "url": public_url,
            "size": len(contents),
        }

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")
```

---

## 8️⃣ CORRIGER NGINX POUR HTTPS + HEADERS

### Fichier: frontend/nginx.conf

```nginx
# Redirection HTTP → HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # SSL (à configurer selon votre setup)
    # ssl_certificate /etc/ssl/certs/cert.pem;
    # ssl_certificate_key /etc/ssl/private/key.pem;

    # Sécurité SSL/TLS
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Sécurité générale
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # CSP (adapté à votre contenu)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' https://js.stripe.com https://cdn.jsdelivr.net; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://api.stripe.com; frame-src 'self' https://js.stripe.com; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests" always;

    # Permissions
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(self), usb=()" always;

    location /api/ {
        proxy_pass http://backend:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## CHECKLIST DE MISE EN PLACE

- [ ] Phase 1 - Générer JWT_SECRET
- [ ] Phase 1 - Ajouter Exception handler global
- [ ] Phase 1 - Migrer tokens en httpOnly cookies
- [ ] Phase 2 - Corriger CSP strict
- [ ] Phase 2 - Ajouter endpoint refresh token
- [ ] Phase 2 - Valider uploads (MIME + magic bytes)
- [ ] Phase 2 - Corriger nginx (HTTPS + headers)
- [ ] Phase 3 - Ajouter token blacklist
- [ ] Phase 3 - Valider inputs avec Zod
- [ ] Phase 3 - Tester avec OWASP ZAP
- [ ] Avant production - Tous les tests de sécurité
- [ ] Après déploiement - Monitoring Sentry activé

---

## TESTS APRÈS CORRECTION

```bash
# Vérifier nouveau JWT_SECRET
grep -r "fallback-secret" /backend

# Vérifier localStorage.setItem('token')
grep -r "localStorage.setItem.*token" /frontend

# Tester HTTPS redirect
curl -I http://yoursite.com

# Vérifier CSP
curl -I https://yoursite.com | grep -i content-security

# Npm audit
npm audit

# Pip audit
pip-audit
```

---

## SUPPORT

Si vous avez des questions sur l'application de ces corrections:
1. Consulter le rapport complet: `AUDIT_SECURITE_COMPLET.md`
2. Référence OWASP: https://owasp.org/
3. FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
