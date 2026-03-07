# 📝 PLAN D'ACTION POST-AUDIT (PRIORISÉ)

Ce plan détaille les actions correctives à mener suite à l'Audit Technique Hyper-Avancé.

## 🚨 PRIORITÉ 1 : SÉCURITÉ CRITIQUE (À FAIRE IMMÉDIATEMENT)

- [ ] **FIX 2FA (Backend):**
    - Modifier `backend/server.py` et `backend/twofa_endpoints.py`.
    - Supprimer la vérification `if code == "123456"`.
    - Intégrer Twilio ou utiliser une librairie TOTP (`pyotp`) pour générer et valider des codes uniques.
    - Stocker le code haché temporairement dans Redis ou la DB avec une expiration courte (5 min).

- [ ] **FIX JWT SECRET (Backend):**
    - Dans `backend/auth.py`, modifier la logique de chargement.
    - Si `os.getenv("JWT_SECRET")` est vide ET `ENVIRONMENT == "production"`, lever une `ValueError` bloquante pour empêcher le démarrage non sécurisé.

- [ ] **SANITIZATION DES ERREURS (Backend):**
    - Créer un `exception_handler` global dans FastAPI.
    - Intercepter les erreurs 500 et renvoyer un message générique "Internal Server Error" au client, tout en loggant l'erreur complète (Stack Trace) côté serveur uniquement.

## 🚀 PRIORITÉ 2 : PERFORMANCE & SCALABILITÉ

- [ ] **OPTIMISATION LISTINGS (Backend):**
    - Refactorer `get_merchants` et `get_influencers` dans `backend/server.py`.
    - **Problème:** Boucle `for` qui fait des requêtes N+1 ou des jointures manuelles en Python.
    - **Solution:** Utiliser la puissance de Supabase/Postgres. Créer une VUE SQL (`create view v_merchants_stats as ...`) qui pré-calcule les revenus et stats, et requêter cette vue directement.

- [ ] **CACHE REDIS (Backend):**
    - Ajouter le décorateur `@cache` (via `fastapi-cache` ou `slowapi`) sur les endpoints lourds :
        - `/api/dashboard/stats` (TTL: 5 min)
        - `/api/merchants` (TTL: 10 min)
        - `/api/influencers` (TTL: 10 min)

## ⚖️ PRIORITÉ 3 : CONFORMITÉ & UX

- [ ] **BANNIÈRE COOKIES (Frontend):**
    - Ajouter un composant `CookieConsent` dans `App.js`.
    - Informer l'utilisateur de l'utilisation de cookies techniques (Auth) et analytiques.

- [ ] **PAGES LÉGALES (Frontend):**
    - Vérifier la présence et le contenu des pages `/terms`, `/privacy`, et `/legal`.

## 🧪 PRIORITÉ 4 : TESTS & QA

- [x] **TESTS E2E (Frontend):**
    - Mettre en place Cypress ou Playwright pour tester le parcours critique :
        1. Inscription
        2. Login
        3. Création de campagne (Merchant)
        4. Postulation (Influencer)

- [x] **TESTS DE CHARGE (Backend):**
    - Utiliser `backend/load_test.py` (Script Custom Python) pour simuler 50+ utilisateurs simultanés.
    - Note: Locust n'est pas compatible avec l'environnement actuel (Python 3.14 / Build Tools manquants), une solution native `threading` + `requests` a été implémentée.
    - **Résultat:** Test effectué le 24/11. Performance dégradée sous charge (50 users), confirmant le besoin d'optimisations (Priorité 2).

---

## 📅 ESTIMATION DU TEMPS DE CORRECTION

- **Priorité 1 (Sécurité):** 1 jour
- **Priorité 2 (Perf):** 2 jours
- **Priorité 3 (Conformité):** 0.5 jour
- **Priorité 4 (Tests):** 2 jours

**TOTAL:** ~1 semaine de travail pour une version "Production Ready" blindée.
