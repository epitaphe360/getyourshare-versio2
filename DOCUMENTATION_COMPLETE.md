# 📚 DOCUMENTATION COMPLÈTE - ShareYourSales

**Inventaire exhaustif de toutes les fonctions et composants**

---

## 📊 VUE D'ENSEMBLE

| Catégorie | Quantité | Description |
|-----------|----------|-------------|
| **Backend** | | |
| └─ Fonctions DB | 48 | Database helpers (users, products, sales, etc.) |
| └─ API Endpoints | 100+ | Routes FastAPI avec authentification |
| └─ Fonctions Utilitaires | 24+ | Cache, logging, sécurité, optimisation |
| └─ Services | 10+ | Gamification, AI, notifications, KYC |
| └─ Auth Functions | 5 | JWT, vérification rôles |
| **Frontend** | | |
| └─ Pages | 90+ | Dashboards, settings, admin, marketplace |
| └─ Composants | 100+ | Layout, UI, features, modals |
| └─ Hooks Custom | 16+ | Auth, API, WebSocket, animations |
| └─ Services | 4+ | API, payments, fiscal, endpoints |
| └─ Providers Context | 6 | Auth, theme, toast, notifications, WS |
| └─ Utilitaires | 10+ | Helpers, formatage, export, logger |
| **TOTAL** | **450+** | Fonctions et composants |

---

## 🎯 NAVIGATION RAPIDE

### Backend
- [Fonctions Base de Données](#backend-fonctions-base-de-données) (48)
- [API Endpoints](#backend-api-endpoints) (100+)
- [Fonctions Utilitaires](#backend-fonctions-utilitaires) (24+)
- [Services](#backend-services) (10+)
- [Authentication](#backend-authentication) (5)

### Frontend
- [Pages](#frontend-pages) (90+)
- [Composants](#frontend-composants) (100+)
- [Hooks](#frontend-hooks) (16+)
- [Services](#frontend-services) (4+)
- [Context Providers](#frontend-context-providers) (6)
- [Utilitaires](#frontend-utilitaires) (10+)

---

# 🔧 BACKEND

## BACKEND: Fonctions Base de Données

**Fichier:** `/backend/db_helpers.py` (48 fonctions)

### 👤 USERS (6 fonctions)

#### `get_user_by_email(email: str) -> Optional[Dict]`
- **Description:** Récupère un utilisateur par son email
- **Paramètres:**
  - `email` (str): Email de l'utilisateur
- **Retour:** Dictionnaire utilisateur ou None
- **Usage:** Login, vérification email

#### `get_user_by_id(user_id: str) -> Optional[Dict]`
- **Description:** Récupère un utilisateur par son ID
- **Paramètres:**
  - `user_id` (str): UUID de l'utilisateur
- **Retour:** Dictionnaire utilisateur ou None
- **Usage:** Authentification, profil

#### `create_user(email: str, password: str, role: str, **kwargs) -> Optional[Dict]`
- **Description:** Crée un nouvel utilisateur avec hash du mot de passe
- **Paramètres:**
  - `email` (str): Email unique
  - `password` (str): Mot de passe en clair (sera hashé)
  - `role` (str): 'merchant', 'influencer', 'commercial', 'admin'
  - `**kwargs`: Champs optionnels (full_name, phone, etc.)
- **Retour:** Utilisateur créé ou None si erreur
- **Usage:** Inscription, création admin

#### `get_user_by_verification_token(token: str) -> Optional[Dict]`
- **Description:** Récupère un utilisateur via son token de vérification email
- **Paramètres:**
  - `token` (str): Token de vérification
- **Retour:** Utilisateur ou None
- **Usage:** Vérification email

#### `set_verification_token(user_id: str, token: str, expires_at: str, sent_at: str) -> bool`
- **Description:** Met à jour le token de vérification pour un utilisateur
- **Paramètres:**
  - `user_id` (str): ID utilisateur
  - `token` (str): Token généré
  - `expires_at` (str): Date d'expiration ISO
  - `sent_at` (str): Date d'envoi ISO
- **Retour:** True si succès
- **Usage:** Envoi email de vérification

#### `mark_email_verified(user_id: str) -> bool`
- **Description:** Marque l'email d'un utilisateur comme vérifié
- **Paramètres:**
  - `user_id` (str): ID utilisateur
- **Retour:** True si succès
- **Usage:** Confirmation email

---

### 🔐 AUTHENTICATION (3 fonctions)

#### `verify_password(plain_password: str, hashed_password: str) -> bool`
- **Description:** Vérifie si le mot de passe correspond au hash bcrypt
- **Paramètres:**
  - `plain_password` (str): Mot de passe en clair
  - `hashed_password` (str): Hash bcrypt stocké
- **Retour:** True si correspondance
- **Usage:** Login

#### `hash_password(password: str) -> str`
- **Description:** Hash un mot de passe avec bcrypt (rounds=12)
- **Paramètres:**
  - `password` (str): Mot de passe en clair
- **Retour:** Hash bcrypt
- **Usage:** Création/modification de mot de passe

#### `update_user_last_login(user_id: str) -> None`
- **Description:** Met à jour la date de dernière connexion
- **Paramètres:**
  - `user_id` (str): ID utilisateur
- **Retour:** None
- **Usage:** Login réussi (background task)

---

### 👥 USER MANAGEMENT (2 fonctions)

#### `update_user(user_id: str, updates: Dict[str, Any]) -> bool`
- **Description:** Met à jour les informations d'un utilisateur
- **Paramètres:**
  - `user_id` (str): ID utilisateur
  - `updates` (dict): Champs à mettre à jour
- **Retour:** True si succès
- **Usage:** Mise à jour profil, admin

#### `log_user_activity(user_id: str, action: str, details: Optional[Dict]) -> bool`
- **Description:** Enregistre une activité utilisateur (audit)
- **Paramètres:**
  - `user_id` (str): ID utilisateur
  - `action` (str): Type d'action
  - `details` (dict, optional): Détails supplémentaires
- **Retour:** True si succès
- **Usage:** Audit trail, sécurité

---

### 🏪 MERCHANTS (3 fonctions)

#### `get_all_merchants() -> List[Dict]`
- **Description:** Récupère tous les merchants depuis la table users
- **Paramètres:** Aucun
- **Retour:** Liste de dictionnaires merchant
- **Usage:** Admin, liste merchants

#### `get_merchant_by_id(merchant_id: str) -> Optional[Dict]`
- **Description:** Récupère un merchant par ID avec relations
- **Paramètres:**
  - `merchant_id` (str): ID merchant
- **Retour:** Merchant avec produits/campagnes ou None
- **Usage:** Détails merchant

#### `get_merchant_by_user_id(user_id: str) -> Optional[Dict]`
- **Description:** Récupère un merchant par user_id
- **Paramètres:**
  - `user_id` (str): ID utilisateur
- **Retour:** Merchant ou None
- **Usage:** Dashboard merchant

---

### 📸 INFLUENCERS (3 fonctions)

#### `get_all_influencers() -> List[Dict]`
- **Description:** Récupère tous les influencers depuis la table users
- **Paramètres:** Aucun
- **Retour:** Liste de dictionnaires influencer
- **Usage:** Admin, recherche influencers

#### `get_influencer_by_id(influencer_id: str) -> Optional[Dict]`
- **Description:** Récupère un influencer par ID avec relations
- **Paramètres:**
  - `influencer_id` (str): ID influencer
- **Retour:** Influencer avec liens/commissions ou None
- **Usage:** Détails influencer

#### `get_influencer_by_user_id(user_id: str) -> Optional[Dict]`
- **Description:** Récupère un influencer par user_id
- **Paramètres:**
  - `user_id` (str): ID utilisateur
- **Retour:** Influencer ou None
- **Usage:** Dashboard influencer

---

### 🛍️ PRODUCTS (5 fonctions)

#### `get_all_products(category: Optional[str] = None, merchant_id: Optional[str] = None) -> List[Dict]`
- **Description:** Récupère tous les produits avec filtres optionnels
- **Paramètres:**
  - `category` (str, optional): Filtrer par catégorie
  - `merchant_id` (str, optional): Filtrer par merchant
- **Retour:** Liste de produits
- **Usage:** Marketplace, catalogue

#### `get_product_by_id(product_id: str) -> Optional[Dict]`
- **Description:** Récupère un produit par ID
- **Paramètres:**
  - `product_id` (str): ID produit
- **Retour:** Produit ou None
- **Usage:** Détails produit

#### `create_product(product_data: Dict) -> Optional[Dict]`
- **Description:** Crée un nouveau produit
- **Paramètres:**
  - `product_data` (dict): Données produit (name, price, merchant_id, etc.)
- **Retour:** Produit créé ou None
- **Usage:** Ajout produit merchant

#### `update_product(product_id: str, updates: Dict) -> bool`
- **Description:** Met à jour un produit
- **Paramètres:**
  - `product_id` (str): ID produit
  - `updates` (dict): Champs à mettre à jour
- **Retour:** True si succès
- **Usage:** Modification produit

#### `delete_product(product_id: str) -> bool`
- **Description:** Supprime un produit (soft delete)
- **Paramètres:**
  - `product_id` (str): ID produit
- **Retour:** True si succès
- **Usage:** Suppression produit

---

### 🔧 SERVICES (3 fonctions)

#### `get_all_services(category: Optional[str] = None, merchant_id: Optional[str] = None) -> List[Dict]`
- **Description:** Récupère tous les services avec filtres
- **Paramètres:**
  - `category` (str, optional): Filtrer par catégorie
  - `merchant_id` (str, optional): Filtrer par merchant
- **Retour:** Liste de services
- **Usage:** Marketplace services

#### `get_service_by_id(service_id: str) -> Optional[Dict]`
- **Description:** Récupère un service par ID
- **Paramètres:**
  - `service_id` (str): ID service
- **Retour:** Service ou None
- **Usage:** Détails service

#### `get_services_stats() -> Dict`
- **Description:** Récupère les statistiques globales des services
- **Paramètres:** Aucun
- **Retour:** Dict avec stats (total_services, active_services, etc.)
- **Usage:** Dashboard admin

---

### 📋 LEADS & SERVICE OPERATIONS (8 fonctions)

#### `create_lead(lead_data: Dict) -> Optional[Dict]`
- **Description:** Crée un nouveau lead (demande client)
- **Paramètres:**
  - `lead_data` (dict): Données lead (service_id, client_name, etc.)
- **Retour:** Lead créé ou None
- **Usage:** Demande service

#### `get_leads_by_service(service_id: str) -> List[Dict]`
- **Description:** Récupère tous les leads d'un service
- **Paramètres:**
  - `service_id` (str): ID service
- **Retour:** Liste de leads
- **Usage:** Gestion leads merchant

#### `get_leads_by_marchand(marchand_id: str) -> List[Dict]`
- **Description:** Récupère tous les leads d'un marchand
- **Paramètres:**
  - `marchand_id` (str): ID marchand
- **Retour:** Liste de leads
- **Usage:** Dashboard marchand

#### `get_all_leads(filters: Optional[Dict] = None) -> List[Dict]`
- **Description:** Récupère tous les leads avec filtres optionnels
- **Paramètres:**
  - `filters` (dict, optional): Filtres (status, date_range, etc.)
- **Retour:** Liste de leads
- **Usage:** Admin, rapports

#### `update_lead_status(lead_id: str, statut: str, notes: Optional[str] = None) -> bool`
- **Description:** Met à jour le statut d'un lead
- **Paramètres:**
  - `lead_id` (str): ID lead
  - `statut` (str): Nouveau statut
  - `notes` (str, optional): Notes
- **Retour:** True si succès
- **Usage:** Workflow leads

#### `create_service_recharge(recharge_data: Dict) -> Optional[Dict]`
- **Description:** Crée une recharge de dépôt pour un service
- **Paramètres:**
  - `recharge_data` (dict): Données recharge (service_id, amount, etc.)
- **Retour:** Recharge créée ou None
- **Usage:** Recharge solde service

#### `get_service_recharges(service_id: str) -> List[Dict]`
- **Description:** Récupère l'historique des recharges d'un service
- **Paramètres:**
  - `service_id` (str): ID service
- **Retour:** Liste de recharges
- **Usage:** Historique transactions

#### `create_service_extra(extra_data: Dict) -> Optional[Dict]`
- **Description:** Crée un extra/boost pour un service
- **Paramètres:**
  - `extra_data` (dict): Données extra
- **Retour:** Extra créé ou None
- **Usage:** Boost service

#### `get_service_extras(service_id: str) -> List[Dict]`
- **Description:** Récupère les extras d'un service
- **Paramètres:**
  - `service_id` (str): ID service
- **Retour:** Liste d'extras
- **Usage:** Affichage extras

---

### 🔗 AFFILIATE LINKS & CAMPAIGNS (4 fonctions)

#### `get_affiliate_links(influencer_id: Optional[str] = None) -> List[Dict]`
- **Description:** Récupère les liens d'affiliation avec relations
- **Paramètres:**
  - `influencer_id` (str, optional): Filtrer par influencer
- **Retour:** Liste de liens avec product/influencer
- **Usage:** Dashboard influencer

#### `create_affiliate_link(product_id: str, influencer_id: str, unique_code: str) -> Optional[Dict]`
- **Description:** Crée un nouveau lien d'affiliation ou retourne l'existant
- **Paramètres:**
  - `product_id` (str): ID produit
  - `influencer_id` (str): ID influencer
  - `unique_code` (str): Code unique de tracking
- **Retour:** Lien créé ou existant
- **Usage:** Génération lien tracking

#### `get_all_campaigns(merchant_id: Optional[str] = None) -> List[Dict]`
- **Description:** Récupère toutes les campagnes avec enrichissement
- **Paramètres:**
  - `merchant_id` (str, optional): Filtrer par merchant
- **Retour:** Liste de campagnes
- **Usage:** Gestion campagnes

#### `create_campaign(merchant_id: str, name: str, **kwargs) -> Optional[Dict]`
- **Description:** Crée une nouvelle campagne
- **Paramètres:**
  - `merchant_id` (str): ID merchant
  - `name` (str): Nom campagne
  - `**kwargs`: Paramètres optionnels (budget, dates, etc.)
- **Retour:** Campagne créée ou None
- **Usage:** Création campagne

---

### 📊 ANALYTICS & CONVERSIONS (4 fonctions)

#### `get_dashboard_stats(role: str, user_id: str) -> Dict`
- **Description:** Récupère les statistiques pour le dashboard selon le rôle
- **Paramètres:**
  - `role` (str): 'merchant', 'influencer', 'commercial', 'admin'
  - `user_id` (str): ID utilisateur
- **Retour:** Dict avec stats personnalisées par rôle
- **Usage:** Dashboard principal

#### `get_conversions(limit: int = 20) -> List[Dict]`
- **Description:** Récupère les conversions récentes avec relations
- **Paramètres:**
  - `limit` (int): Nombre max de résultats
- **Retour:** Liste de conversions avec details
- **Usage:** Analytics conversions

#### `get_clicks(limit: int = 50) -> List[Dict]`
- **Description:** Récupère les clics récents avec relations imbriquées
- **Paramètres:**
  - `limit` (int): Nombre max de résultats
- **Retour:** Liste de clics avec affiliate_link/product/influencer
- **Usage:** Tracking clics

#### `get_payouts() -> List[Dict]`
- **Description:** Récupère tous les payouts avec relations
- **Paramètres:** Aucun
- **Retour:** Liste de payouts avec influencer/merchant
- **Usage:** Gestion paiements

---

### 💰 PAYOUT MANAGEMENT (1 fonction)

#### `update_payout_status(payout_id: str, status: str) -> tuple[bool, str]`
- **Description:** Met à jour le statut d'un payout (fallback Python)
- **Paramètres:**
  - `payout_id` (str): ID payout
  - `status` (str): Nouveau statut ('pending', 'approved', 'paid', 'rejected')
- **Retour:** (success: bool, message: str)
- **Usage:** Validation payout admin

---

## BACKEND: Fonctions Utilitaires

**Fichier:** `/backend/utils/` (24+ fonctions/méthodes)

### 📝 LOGGER (StructuredLogger)

**Fichier:** `/backend/utils/logger.py`

**Classe:** `StructuredLogger`

#### `__init__(name: str = "app")`
- **Description:** Initialise le logger structuré avec filtrage PII
- **Paramètres:**
  - `name` (str): Nom du logger
- **Features:** Masquage automatique password/token/key

#### Méthodes de logging:
- `debug(message: str, **kwargs)` - Log niveau DEBUG
- `info(message: str, **kwargs)` - Log niveau INFO
- `warning(message: str, **kwargs)` - Log niveau WARNING
- `error(message: str, **kwargs)` - Log niveau ERROR
- `critical(message: str, **kwargs)` - Log niveau CRITICAL

#### `api_call(endpoint: str, method: str, status_code: int, duration_ms: float)`
- **Description:** Log appel API structuré
- **Usage:** Monitoring API

#### `database_query(query: str, duration_ms: float, rows: int)`
- **Description:** Log requête database sécurisée (masque données sensibles)
- **Usage:** Performance tracking

---

### 🗃️ CACHE

**Fichier:** `/backend/utils/cache.py`

#### `@cache(ttl_seconds: int = 300)`
- **Description:** Décorateur pour cacher les résultats de fonction avec TTL
- **Paramètres:**
  - `ttl_seconds` (int): Durée de vie du cache en secondes
- **Retour:** Décorateur
- **Usage:**
```python
@cache(ttl_seconds=600)
def get_expensive_data():
    return expensive_calculation()
```

#### `clear_cache()`
- **Description:** Efface tout le cache en mémoire
- **Usage:** Invalidation manuelle

---

### 🛡️ DB SAFE (Sécurité SQL)

**Fichier:** `/backend/utils/db_safe.py` (7 fonctions)

#### `sanitize_like_pattern(value: str) -> str`
- **Description:** Sanitise une valeur pour ILIKE (échappe %, _, \\)
- **Usage:** Recherche sécurisée

#### `sanitize_sql_identifier(value: str) -> str`
- **Description:** Sanitise un identifiant SQL (table, colonne)
- **Retour:** Identifier safe avec validation whitelist

#### `safe_ilike(query, column: str, search_value: Optional[str], wildcard: str = "both")`
- **Description:** Effectue un ILIKE sécurisé avec sanitisation
- **Paramètres:**
  - `wildcard`: 'both', 'start', 'end', 'none'
- **Usage:** Recherche texte sécurisée

#### `build_or_search(query, columns: List[str], search_value: Optional[str])`
- **Description:** Construit recherche OR multi-colonnes sécurisée
- **Usage:** Recherche globale

#### `validate_sort_field(field: str, allowed_fields: List[str], default: str) -> str`
- **Description:** Valide un champ de tri contre whitelist
- **Usage:** Tri sécurisé

#### `validate_order(order: str, default: str = "desc") -> str`
- **Description:** Valide l'ordre de tri (asc/desc)
- **Retour:** 'asc' ou 'desc'

#### `safe_numeric_filter(value: any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]`
- **Description:** Valide et sanitise une valeur numérique
- **Usage:** Filtres numériques

---

### ⚡ DB OPTIMIZED (Optimisation Requêtes)

**Fichier:** `/backend/utils/db_optimized.py`

**Classe:** `DBOptimizer` (9 méthodes)

#### `__init__(supabase_client)`
- **Description:** Initialise l'optimiseur avec client Supabase

#### `fetch_with_relations(table: str, filters: Optional[Dict] = None, relations: Optional[List[str]] = None, limit: Optional[int] = None, order_by: Optional[str] = None, desc: bool = True) -> List[Dict]`
- **Description:** Eager loading pour éviter N+1 queries
- **Paramètres:**
  - `relations`: Liste de relations à charger (ex: ['merchant', 'product'])
- **Usage:** SELECT avec JOIN optimisé

#### `batch_fetch(table: str, ids: List[str], columns: str = '*', chunk_size: int = 50) -> Dict[str, Dict]`
- **Description:** Récupère N items en une seule requête
- **Retour:** Dict indexé par ID
- **Usage:** Charger plusieurs items d'un coup

#### `batch_fetch_related(table: str, foreign_key: str, related_ids: List[str], columns: str = '*', chunk_size: int = 50) -> List[Dict]`
- **Description:** Récupère items liés à plusieurs parents
- **Usage:** Charger enfants de multiples parents

#### `@cache(ttl_seconds: int = 300, key_prefix: Optional[str] = None)`
- **Description:** Décorateur pour cacher résultats avec TTL
- **Usage:** Optimisation requêtes répétées

#### `clear_cache(pattern: Optional[str] = None)`
- **Description:** Efface le cache (globalement ou par pattern regex)
- **Usage:** Invalidation ciblée

#### `bulk_update(table: str, updates: List[Dict], id_field: str = 'id', chunk_size: int = 100) -> int`
- **Description:** Met à jour plusieurs items en un seul appel
- **Retour:** Nombre d'items mis à jour
- **Usage:** Bulk operations

#### `bulk_insert(table: str, items: List[Dict], chunk_size: int = 100) -> int`
- **Description:** Insère plusieurs items en un seul appel
- **Retour:** Nombre d'items insérés
- **Usage:** Import massif

#### `count_by_field(table: str, field: str, filters: Optional[Dict] = None) -> Dict[Any, int]`
- **Description:** Compte occurrences par valeur de champ
- **Retour:** Dict {valeur: count}
- **Usage:** Statistiques groupées

---

### 🖼️ IMAGE PROCESSING

**Fichier:** `/backend/utils/image_processing.py`

#### `validate_image(image_data: bytes, filename: str, max_size: int = 5_000_000, allowed_formats: Optional[List[str]] = None) -> Dict[str, Any]`
- **Description:** Valide une image uploadée
- **Paramètres:**
  - `max_size`: Taille max en bytes (défaut 5MB)
  - `allowed_formats`: ['JPEG', 'PNG', 'WEBP', ...]
- **Retour:** Dict avec 'valid', 'error', 'image', 'format', 'size', 'dimensions'
- **Usage:** Upload image sécurisé

---

### 🔧 HELPER FUNCTIONS (2 fonctions)

#### `merge_with_relations(items: List[Dict], related_items: Dict[str, Dict], item_id_field: str, relation_field: str) -> List[Dict]`
- **Description:** Fusionner items avec relations après batch_fetch
- **Usage:** Post-processing après batch

#### `transform_to_dict(items: List[Dict], key_field: str = 'id') -> Dict[Any, Dict]`
- **Description:** Transformer liste en dictionnaire indexé
- **Retour:** Dict {key: item}
- **Usage:** Indexation rapide

---

## BACKEND: API Endpoints

**Fichier:** `/backend/server.py` (100+ routes)

### 🏥 HEALTH & ROOT (3 routes)

| Route | Méthode | Auth | Description |
|-------|---------|------|-------------|
| `/` | GET | Non | Health check root |
| `/health` | GET | Non | Health check détaillé |
| `/api/health` | GET | Non | Health check API (alias) |

---

### 🔐 AUTHENTICATION (8 routes)

| Route | Méthode | Auth | Description | Body/Query |
|-------|---------|------|-------------|------------|
| `/api/auth/login` | POST | Non | Login avec email/password | `{email, password}` |
| `/api/auth/refresh` | POST | Cookie | Rafraîchir access token | None (utilise refresh_token cookie) |
| `/api/auth/logout` | POST | Oui | Déconnexion (clear cookies) | None |
| `/api/auth/verify-2fa` | POST | Temp | Vérifier code 2FA | `{temp_token, code}` |
| `/api/auth/register` | POST | Non | Enregistrement nouvel utilisateur | `{email, password, role, full_name, ...}` |
| `/api/auth/me` | GET | Oui | Infos utilisateur courant | None |
| `/api/users/me` | GET | Oui | Profil utilisateur courant (alias) | None |
| `/api/auth/profile` | PUT | Oui | Mise à jour profil | `{full_name, phone, ...}` |

---

### 📊 DASHBOARD & ANALYTICS (4 routes)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/dashboard/stats` | GET | Oui | Stats dashboard selon rôle | None |
| `/api/analytics/overview` | GET | Oui | Vue d'ensemble analytics | `?period=30d` |
| `/api/analytics/admin/revenue-chart` | GET | Admin | Graphique revenus admin | `?start_date=...&end_date=...` |

---

### 🏪 MERCHANTS (2 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/merchants` | GET | Oui | Liste des merchants | None |
| `/api/merchants/{merchant_id}` | GET | Oui | Détails d'un merchant | `merchant_id` (path) |

---

### 📸 INFLUENCERS (3 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/influencers` | GET | Oui | Liste des influencers | None |
| `/api/influencers/{influencer_id}` | GET | Oui | Détails d'un influencer | `influencer_id` (path) |
| `/api/influencers/{influencer_id}/stats` | GET | Oui | Statistiques influencer | `influencer_id` (path) |

---

### 🛍️ PRODUCTS & SERVICES (6 routes)

| Route | Méthode | Auth | Description | Query/Body |
|-------|---------|------|-------------|------------|
| `/api/products_OLD` | GET | Non | Liste produits (legacy) | `?category=...&merchant_id=...` |
| `/api/products_OLD/{product_id}` | GET | Non | Détails produit (legacy) | `product_id` (path) |
| `/api/products/stats` | GET | Merchant | Stats produits merchant | None |
| `/api/products/upload-image` | POST | Merchant | Upload image produit | File upload |
| `/api/services_OLD` | GET | Non | Liste services (legacy) | `?category=...&merchant_id=...` |
| `/api/services_OLD/{service_id}` | GET | Non | Détails service (legacy) | `service_id` (path) |

---

### 🔗 AFFILIATE LINKS (3 routes)

| Route | Méthode | Auth | Description | Body |
|-------|---------|------|-------------|------|
| `/api/affiliate-links` | GET | Influencer | Liste liens d'affiliation | None |
| `/api/affiliate-links` | POST | Influencer | Créer lien d'affiliation | `{product_id}` |
| `/api/affiliate-links/generate` | POST | Influencer | Générer lien avec code unique | `{product_id, custom_code?}` |

---

### 💳 SUBSCRIPTIONS (4 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/subscriptions` | GET | Admin | Liste abonnements | None |
| `/api/subscriptions/current` | GET | Oui | Abonnement courant | None |
| `/api/subscriptions/{subscription_id}/history` | GET | Oui | Historique abonnement | `subscription_id` (path) |

---

### 📢 CAMPAIGNS (7 routes)

| Route | Méthode | Auth | Description | Body/Params |
|-------|---------|------|-------------|-------------|
| `/api/campaigns` | GET | Merchant | Liste campagnes | None |
| `/api/campaigns` | POST | Merchant | Créer campagne | `{name, budget, start_date, end_date, ...}` |
| `/api/campaigns/{campaign_id}` | GET | Oui | Détails campagne | `campaign_id` (path) |
| `/api/campaigns/{campaign_id}/stats` | GET | Oui | Stats campagne | `campaign_id` (path) |
| `/api/campaigns/{campaign_id}/influencers` | GET | Merchant | Influencers campagne | `campaign_id` (path) |
| `/api/campaigns/{campaign_id}` | PUT | Merchant | Mettre à jour campagne | `{name, budget, ...}` |
| `/api/campaigns/{campaign_id}/status` | PUT | Merchant | Changer statut | `{status}` ('active', 'paused', 'ended') |

---

### 📊 CONVERSIONS, LEADS & CLICKS (3 routes)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/conversions` | GET | Oui | Liste conversions | `?limit=20` |
| `/api/leads` | GET | Oui | Liste leads | `?status=...&limit=50` |
| `/api/clicks` | GET | Oui | Liste clics trackés | `?limit=50` |

---

### 👥 ADMIN: USER MANAGEMENT (6 routes)

| Route | Méthode | Auth | Description | Body/Params |
|-------|---------|------|-------------|-------------|
| `/api/admin/users` | GET | Admin | Liste utilisateurs | `?role=...&search=...&page=1&limit=50` |
| `/api/admin/users` | POST | Admin | Créer utilisateur | `{email, password, role, ...}` |
| `/api/admin/users/{user_id}` | PUT | Admin | Mettre à jour utilisateur | `{full_name, role, is_active, ...}` |
| `/api/admin/users/{user_id}` | DELETE | Admin | Supprimer utilisateur | `user_id` (path) |
| `/api/admin/users/{user_id}/permissions` | PUT | Admin | Changer permissions | `{permissions: [...]}` |

---

### 🏪 ADMIN: MERCHANT MANAGEMENT (2 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/admin/merchants/stats` | GET | Admin | Stats merchants globales | None |
| `/api/admin/merchants/{merchant_id}/details` | GET | Admin | Détails complets merchant | `merchant_id` (path) |

---

### 📝 ADMIN: REGISTRATION MANAGEMENT (5 routes)

| Route | Méthode | Auth | Description | Body/Params |
|-------|---------|------|-------------|-------------|
| `/api/admin/registration-requests` | GET | Admin | Demandes enregistrement | `?status=pending&page=1` |
| `/api/admin/registration-requests/stats` | GET | Admin | Stats enregistrements | None |
| `/api/admin/registration-requests/{registration_id}/approve` | POST | Admin | Approuver enregistrement | `{notes?}` |
| `/api/admin/registration-requests/{registration_id}/reject` | POST | Admin | Rejeter enregistrement | `{reason}` |
| `/api/admin/registration-requests/bulk-action` | POST | Admin | Actions en masse | `{action, registration_ids: [...]}` |

---

### 🛡️ ADMIN: MODERATION (3 routes)

| Route | Méthode | Auth | Description | Query/Body |
|-------|---------|------|-------------|------------|
| `/api/admin/moderation/pending` | GET | Admin | Contenus en attente | `?type=...&page=1` |
| `/api/admin/moderation/stats` | GET | Admin | Stats modération | None |
| `/api/admin/moderation/review` | POST | Admin | Examiner contenu | `{content_id, action, notes?}` ('approve', 'reject') |

---

### 📢 ADVERTISERS (3 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/advertiser-registrations` | GET | Admin | Enregistrements annonceurs | None |
| `/api/advertiser-registrations/{registration_id}/approve` | POST | Admin | Approuver annonceur | `registration_id` (path) |
| `/api/advertiser-registrations/{registration_id}/reject` | POST | Admin | Rejeter annonceur | `registration_id` (path) |

---

### 🧾 INVOICES (4 routes)

| Route | Méthode | Auth | Description | Body/Params |
|-------|---------|------|-------------|-------------|
| `/api/invoices` | GET | Oui | Liste factures | `?start_date=...&end_date=...` |
| `/api/invoices` | POST | Merchant | Créer facture | `{client_name, items: [...], ...}` |
| `/api/invoices/{invoice_id}` | GET | Oui | Détails facture | `invoice_id` (path) |
| `/api/invoices/{invoice_id}/download` | GET | Oui | Télécharger PDF | `invoice_id` (path) |

---

### 🔧 SERVICES MANAGEMENT (7 routes)

| Route | Méthode | Auth | Description | Query/Body |
|-------|---------|------|-------------|------------|
| `/api/services_OLD/{service_id}/leads` | GET | Merchant | Leads d'un service | `service_id` (path) |
| `/api/services/admin/leads` | GET | Admin | Tous les leads | `?status=...&page=1` |
| `/api/services/admin/leads/stats` | GET | Admin | Stats leads | None |
| `/api/services/admin/services` | GET | Admin | Tous les services | `?category=...&page=1` |
| `/api/services/admin/leads/analytics` | GET | Admin | Analytics leads | `?period=30d` |
| `/api/services/admin/leads/{lead_id}/send-email` | POST | Admin | Envoyer email lead | `{template, subject, body}` |
| `/api/services/admin/leads/export` | GET | Admin | Exporter leads CSV | `?format=csv&filters=...` |

---

### 💼 FISCAL MANAGEMENT (4 routes)

| Route | Méthode | Auth | Description | Query/Body |
|-------|---------|------|-------------|------------|
| `/api/fiscal/countries` | GET | Oui | Pays fiscaux disponibles | None |
| `/api/fiscal/rates/{country_code}` | GET | Oui | Taux fiscaux par pays | `country_code` (path: 'MA', 'FR', 'US') |
| `/api/fiscal/settings` | GET | Oui | Paramètres fiscaux utilisateur | None |
| `/api/fiscal/settings` | PUT | Oui | Mettre à jour params fiscaux | `{country, vat_number, tax_regime, ...}` |

---

### 🏪 MERCHANT DASHBOARD (7 routes)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/merchant/dashboard/stats` | GET | Merchant | Stats générales | None |
| `/api/merchant/dashboard/products` | GET | Merchant | Produits merchant | `?limit=10` |
| `/api/merchant/dashboard/sales` | GET | Merchant | Ventes merchant | `?period=30d` |
| `/api/merchant/dashboard/campaigns` | GET | Merchant | Campagnes actives | None |
| `/api/merchant/dashboard/affiliates` | GET | Merchant | Affiliés actifs | None |
| `/api/merchant/dashboard/revenue` | GET | Merchant | Revenus | `?start_date=...&end_date=...` |
| `/api/merchant/dashboard/analytics` | GET | Merchant | Analytics détaillées | `?period=30d` |

---

### 💰 PAYOUTS (1 route)

| Route | Méthode | Auth | Description | Body |
|-------|---------|------|-------------|------|
| `/api/payouts/request` | POST | Influencer | Demander retrait | `{amount, payment_method, account_details}` |

---

### 📱 SOCIAL MEDIA (6 routes)

| Route | Méthode | Auth | Description | Body/Query |
|-------|---------|------|-------------|------------|
| `/api/social-media/connections` | GET | Influencer | Connexions réseaux sociaux | None |
| `/api/social-media/connections/{connection_id}` | DELETE | Influencer | Supprimer connexion | `connection_id` (path) |
| `/api/social-media/dashboard` | GET | Influencer | Dashboard réseaux | None |
| `/api/social-media/sync` | POST | Influencer | Synchroniser données | None |
| `/api/social-media/stats/history` | GET | Influencer | Historique stats | `?days=30` |
| `/api/social-media/posts/top` | GET | Influencer | Posts populaires | `?limit=10` |

---

### 📋 REGISTRATIONS (2 routes)

| Route | Méthode | Auth | Description | Params |
|-------|---------|------|-------------|--------|
| `/api/registrations_OLD` | GET | Admin | Enregistrements (legacy) | None |
| `/api/registrations_OLD/{registration_id}/timeline` | GET | Admin | Timeline enregistrement | `registration_id` (path) |

---

### 💼 SALES (4 routes)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/sales/dashboard/me` | GET | Commercial | Dashboard sales rep | None |
| `/api/sales/leads/me` | GET | Commercial | Leads sales rep | `?status=...` |
| `/api/sales/deals/me` | GET | Commercial | Deals sales rep | `?status=...` |
| `/api/sales/leaderboard` | GET | Commercial | Classement sales | `?period=month` |

---

### 📧 INVITATIONS (1 route)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/invitations` | GET | Oui | Invitations utilisateur | None |

---

### 📁 CATEGORIES (1 route)

| Route | Méthode | Auth | Description | Query |
|-------|---------|------|-------------|-------|
| `/api/categories_OLD` | GET | Non | Catégories (legacy) | None |

---

## BACKEND: Services

**Fichier:** `/backend/services/`

### 🎮 GAMIFICATION SERVICE

**Fichier:** `services/gamification_service.py`

**Classe:** `GamificationService`

#### Configuration Niveaux:
- **Bronze**: 0-999 points, +5% commissions
- **Silver**: 1000-2499 points, +10% commissions
- **Gold**: 2500-4999 points, +15% commissions, accès VIP
- **Platinum**: 5000-9999 points, +20% commissions, support prioritaire
- **Diamond**: 10000-19999 points, +25% commissions, accès beta
- **Legend**: 20000+ points, +30% commissions, tous avantages

#### Points par Action:
**Merchants:**
- Produit ajouté: 100 pts
- Vente: 50 pts
- Campagne créée: 200 pts
- Service ajouté: 150 pts

**Influencers:**
- Lien créé: 50 pts
- Click: 10 pts
- Conversion: 500 pts
- Post social: 75 pts

**Commerciaux:**
- Lead créé: 100 pts
- Lead converti: 1000 pts
- Deal: 500 pts

#### Méthodes Principales:
- `add_points(user_id, points, action)` - Ajouter points
- `get_user_level(points)` - Calculer niveau
- `check_level_up(user_id)` - Vérifier montée niveau
- `get_leaderboard(role, limit)` - Classement
- `award_badge(user_id, badge_type)` - Attribuer badge

---

### 🤖 AI BOT SERVICE

**Fichier:** `services/ai_bot_service.py`

**Classe:** `AIBotService`

#### `chat(user_message: str, user_context: Dict) -> Dict`
- **Description:** Conversation intelligente avec détection d'intentions
- **Intentions Détectées:**
  - Salutations (bonjour, hi, hello)
  - Demande stats (performance, revenue, conversions)
  - Création affiliation (créer lien, générer code)
  - Aide/support (aide, help, comment)
  - Statut abonnement (plan, subscription)
  - Recommandations produits (recommande, suggest)
  - Analyse sentiments (comment ça va, mood)
- **Features:**
  - Support multilingue (FR, EN, AR)
  - RAG pour documents
  - Actions automatiques
  - Analyse sentiment
- **Retour:** `{response, intent, actions?, suggested_commands?}`

---

### 🔔 NOTIFICATION SERVICE

**Fichier:** `services/notification_service.py`

**Classe:** `NotificationService`

#### `__init__()`
- **Description:** Initialise avec Twilio, Slack, Firebase
- **Channels:** Email, SMS, Slack, Push

#### `send_low_balance_alert(service_id: str, balance: float, threshold: float = 200.0)`
- **Description:** Alerte solde bas multi-canal
- **Seuils:**
  - < 200 DHS: Alerte CRITIQUE (tous canaux)
  - < 500 DHS: Alerte WARNING (email + push)
  - < 1000 DHS: Alerte INFO (email)
- **Channels:**
  - Email (Resend)
  - SMS (Twilio)
  - Slack (Webhook)
  - Push (Firebase Cloud Messaging)

---

### 📊 ADVANCED ANALYTICS SERVICE

**Fichier:** `services/advanced_analytics_service.py`

**Classe:** `AdvancedAnalyticsService`

#### Méthodes:
- `calculate_trend(current, previous)` - Calcul tendance %
- `get_period_data(metric, start_date, end_date)` - Données période
- `compare_periods(metric, current_period, previous_period)` - Comparaison

---

## BACKEND: Authentication

**Fichier:** `/backend/auth.py` (5 fonctions)

#### `get_current_user_from_cookie(request: Request) -> dict`
- **Description:** Récupère user courant du cookie/JWT
- **Usage:** Dépendance FastAPI pour routes protégées
- **Raises:** HTTPException 401 si token invalide

#### `get_optional_user_from_cookie(request: Request) -> Optional[dict]`
- **Description:** Récupère user optionnel (pas d'erreur si absent)
- **Usage:** Routes publiques avec contenu personnalisé si connecté

#### `verify_token(credentials: Union[HTTPAuthorizationCredentials, str]) -> dict`
- **Description:** Vérifie et parse le JWT token
- **Retour:** Payload du token
- **Raises:** HTTPException si invalide/expiré

#### `require_role(required_role: str) -> Callable`
- **Description:** Dépendance pour vérifier un rôle spécifique
- **Usage:**
```python
@app.get("/api/admin/users", dependencies=[Depends(require_role("admin"))])
```

#### `require_roles(allowed_roles: list) -> Callable`
- **Description:** Dépendance pour vérifier plusieurs rôles
- **Usage:**
```python
@app.get("/api/products", dependencies=[Depends(require_roles(["merchant", "admin"]))])
```

---

# 🎨 FRONTEND

## FRONTEND: Context Providers

**Fichier:** `/frontend/src/context/`

### 🔐 AuthContext

**Fichier:** `context/AuthContext.js`

**Component:** `AuthProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** Gestion état authentification global
- **Features:**
  - Login/logout
  - Token storage (localStorage + cookies)
  - Session auto-refresh (5 min intervals)
  - Support 2FA
  - Auto-redirect sur 401

**Hook:** `useAuth()`
- **Returns:**
```javascript
{
  user: object | null,
  loading: boolean,
  login: (email, password) => Promise,
  logout: () => void,
  verifySession: () => Promise,
  refreshSession: () => Promise,
  isAuthenticated: boolean,
  hasRole: (role) => boolean,
  getToken: () => string
}
```

---

### 🎨 ThemeContext

**Fichier:** `context/ThemeContext.jsx`

**Component:** `ThemeProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** Dark/Light mode management
- **Features:**
  - Toggle light/dark/system
  - localStorage persistence
  - prefers-color-scheme support
  - CSS transitions

**Hook:** `useTheme()`
- **Returns:**
```javascript
{
  theme: 'light' | 'dark' | 'system',
  resolvedTheme: 'light' | 'dark',
  isDark: boolean,
  toggleTheme: () => void,
  setLightTheme: () => void,
  setDarkTheme: () => void,
  setSystemTheme: () => void
}
```

---

### 🔔 NotificationContext

**Fichier:** `context/NotificationContext.jsx`

**Component:** `NotificationProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** Real-time notifications via Socket.io
- **Features:**
  - Socket.io integration
  - Browser notifications
  - Sound notifications
  - IndexedDB persistence
  - Unread count

**Hook:** `useNotifications()`
- **Returns:**
```javascript
{
  notifications: Array,
  unreadCount: number,
  markAsRead: (id) => void,
  markAllAsRead: () => void,
  deleteNotification: (id) => void,
  requestBrowserPermission: () => void,
  toggleSound: () => void
}
```

---

### 🌐 WebSocketContext

**Fichier:** `context/WebSocketContext.js`

**Component:** `WebSocketProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** WebSocket connection management
- **Features:**
  - Auto-reconnection
  - Event routing (commissions, payments, sales)
  - Query invalidation integration

**Hook:** `useWebSocketContext()`
- **Returns:**
```javascript
{
  socket: Socket | null,
  connected: boolean,
  on: (event, callback) => void,
  off: (event, callback) => void,
  emit: (event, data) => void
}
```

---

### 💰 CurrencyContext

**Fichier:** `context/CurrencyContext.js`

**Component:** `CurrencyProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** Multi-currency support
- **Currencies:** MAD, EUR, USD

**Hook:** `useCurrency()`
- **Returns:**
```javascript
{
  currency: 'MAD' | 'EUR' | 'USD',
  changeCurrency: (code) => void,
  formatPrice: (amount, currencyCode?) => string,
  symbol: string,
  locale: string
}
```

---

### 🍞 ToastContext

**Fichier:** `context/ToastContext.js`

**Component:** `ToastProvider`
- **Props:** `{ children: ReactNode }`
- **Purpose:** Toast notifications
- **Features:**
  - Auto-dismiss (customizable)
  - Toast stacking
  - Type variants (success, error, info, warning)

**Hook:** `useToast()`
- **Returns:**
```javascript
{
  toasts: Array,
  success: (message, options?) => void,
  error: (message, options?) => void,
  info: (message, options?) => void,
  warning: (message, options?) => void
}
```

---

## FRONTEND: Hooks

**Fichier:** `/frontend/src/hooks/`

### 🔐 useAuth

**Fichier:** `hooks/useAuth.js`

- **Returns:**
```javascript
{
  user: object | null,
  loading: boolean,
  error: string | null,
  login: (email, password) => Promise,
  register: (userData) => Promise,
  logout: () => void,
  updateProfile: (updates) => Promise,
  hasRole: (role) => boolean,
  isAuthenticated: () => boolean,
  getToken: () => string
}
```

---

### 🌐 useWebSocket

**Fichier:** `hooks/useWebSocket.js`

**Parameters:** `(url: string, options?: object)`

- **Returns:**
```javascript
{
  readyState: number,
  lastMessage: object | null,
  sendMessage: (data) => void,
  connect: () => void,
  disconnect: () => void,
  on: (event, callback) => void,
  authenticate: (token) => void,
  isConnected: boolean
}
```

**Features:**
- Auto-reconnect
- Heartbeat/ping-pong
- Event listeners
- Connection state

---

### 📝 useForm

**Fichier:** `hooks/useForm.js`

**Parameters:** `(initialValues?: object, validationSchema?: object)`

- **Returns:**
```javascript
{
  values: object,
  errors: object,
  touched: object,
  isSubmitting: boolean,
  isDirty: boolean,
  handleChange: (e) => void,
  handleBlur: (e) => void,
  handleSubmit: (callback) => (e) => void,
  setFieldValue: (field, value) => void,
  resetForm: () => void,
  getFieldProps: (field) => object
}
```

**Validators:**
- `required(message?)`
- `email(message?)`
- `minLength(min, message?)`
- `maxLength(max, message?)`
- `pattern(regex, message?)`
- `custom(fn, message?)`

---

### 🔍 useDebounce

**Fichier:** `hooks/useDebounce.js`

**Parameters:** `(value: any, delay?: number = 500)`

- **Returns:** Debounced value

**Variant:** `useDebouncedCallback(callback, delay)`
- **Returns:** Debounced function

---

### 📱 useMobile (Collection)

**Fichier:** `hooks/useMobile.js`

#### `useIsMobile()`
- **Returns:** `{ isMobile: boolean, isTablet: boolean, isDesktop: boolean }`

#### `useOnlineStatus()`
- **Returns:** `{ isOnline: boolean, wasOffline: boolean }`

#### `usePWAInstall()`
- **Returns:** `{ isInstallable: boolean, promptInstall: () => void }`

#### `useOrientation()`
- **Returns:** `{ orientation: 'portrait' | 'landscape', angle: number }`

#### `useVibrate()`
- **Returns:** `{ vibrate: (pattern) => void, isSupported: boolean }`

#### `useNetworkInfo()`
- **Returns:** `{ type: string, effectiveType: string, downlink: number, rtt: number }`

---

### 🎨 useAnimations (Collection)

**Fichier:** `hooks/useAnimations.js`

#### `useInView(options?)`
- **Description:** Trigger animation on scroll into view
- **Returns:** `{ ref, inView: boolean }`

#### `useHover(options?)`
- **Returns:** `{ ref, isHovered: boolean }`

#### `useSpring(from, to, options?)`
- **Description:** Physics-based animation
- **Returns:** `{ value: number, animate: () => void }`

#### `useGesture(handlers)`
- **Description:** Swipe/pinch detection
- **Returns:** `{ bind: () => object }`

#### `usePrefersReducedMotion()`
- **Returns:** `boolean` (accessibility)

---

### 💾 useLocalStorage

**Fichier:** `hooks/useLocalStorage.js`

**Parameters:** `(key: string, initialValue: any)`

- **Returns:** `[value, setValue, removeValue]`
- **Features:**
  - Auto JSON serialization
  - Cross-tab sync
  - SSR-safe
  - Error handling

---

### 📶 useOfflineStatus

**Fichier:** `hooks/useOfflineStatus.js`

- **Returns:**
```javascript
{
  isOnline: boolean,
  isOffline: boolean,
  wasOffline: boolean,
  connectionType: string,
  queuedRequests: Array,
  isSyncing: boolean,
  queueRequest: (request) => void,
  syncQueuedRequests: () => Promise,
  clearQueue: () => void,
  retryRequest: (id) => Promise
}
```

**Features:**
- IndexedDB queue persistence
- Service Worker integration
- Auto-sync on reconnect

---

### 🔌 useApi

**Fichier:** `hooks/useApi.js`

- **Returns:**
```javascript
{
  loading: boolean,
  error: string | null,
  data: any,
  execute: (params?) => Promise,
  reset: () => void
}
```

**Variants:**
- `usePagination(fetchFunction, initialParams)`
- `useSearch(searchFunction, delay = 500)`

---

## FRONTEND: Services

**Fichier:** `/frontend/src/services/`

### 🌐 API Service

**Fichier:** `services/api.js`

**Instance Axios:**
- **Base URL:** `process.env.REACT_APP_API_URL` ou `http://127.0.0.1:5000`
- **Features:**
  - Token injection automatique
  - httpOnly cookies (`withCredentials: true`)
  - Intercepteurs erreur (401, 403, 404, 5xx)
  - Auto-redirect login sur 401

**Exports:**
- `api` (instance axios)
- `checkAPIHealth()` - Health check utility

---

### 💳 Payment Service

**Fichier:** `services/paymentService.js`

**Classe:** `PaymentService`

#### Méthodes Subscription:
- `initiateSubscriptionPayment(subscriptionData, provider)` - CMI/Stripe/PayPal
- `checkPaymentStatus(paymentId)` - Vérifier statut
- `cancelSubscription()` - Annuler abonnement
- `getPaymentHistory()` - Historique paiements
- `requestRefund(paymentId, reason)` - Demander remboursement

#### Méthodes Commissions:
- `payCommission(commissionData)` - Payer commission affilié
- `requestPayout(amount, method)` - Demander retrait influencer

#### Méthodes Providers:
- `getAvailablePaymentMethods()` - Liste providers
- Supports: **CMI** (Maroc), **Stripe**, **PayPal**

---

### 💼 Fiscal Service

**Fichier:** `services/fiscalService.js`

**Classe:** `FiscalService`

#### Modules Invoices:
- `createInvoice(invoiceData)` - Créer facture
- `getInvoices(filters?)` - Liste factures
- `getInvoiceById(id)` - Détails facture
- `updateInvoice(id, updates)` - Modifier facture
- `deleteInvoice(id)` - Supprimer facture
- `generateInvoicePDF(id)` - Générer PDF
- `sendInvoiceEmail(id, email)` - Envoyer par email

#### Calculs VAT:
- `calculateMoroccoVAT(amount, rate)` - TVA Maroc (20%)
- `calculateFranceVAT(amount, rate)` - TVA France (20%, 10%, 5.5%)
- `calculateUSASalesTax(amount, state)` - Sales Tax USA (variable par état)

#### Calculs Tax:
- `calculateMoroccoIR(revenue)` - IR Maroc (barème progressif)
- `calculateFranceURSSAF(revenue)` - URSSAF France (auto-entrepreneur)
- `calculateUSAFederalTax(income)` - Federal Tax USA
- `calculateUSASelfEmploymentTax(income)` - Self-Employment Tax USA

#### Déclarations & Exports:
- `createVATDeclaration(period, data)` - Créer déclaration TVA
- `getVATDeclarations(year)` - Historique déclarations
- `exportFranceFEC(year)` - Export FEC France (comptabilité)
- `exportCSV(data, filename)` - Export CSV

#### Settings:
- `getFiscalSettings()` - Paramètres fiscaux utilisateur
- `updateFiscalSettings(settings)` - Mettre à jour
- `getFiscalStats(period)` - Statistiques fiscales

---

### 🚀 New Endpoints API

**Fichier:** `services/newEndpointsAPI.js`

**Modules:**

#### AI Recommendations:
- `getRecommendationsForYou()` - Recommandations personnalisées
- `getSimilarProducts(productId)` - Produits similaires
- `chatWithBot(message, context)` - Chat AI
- `getInsights()` - Insights business

#### Advanced Analytics:
- `getCohortAnalysis(params)` - Analyse cohortes
- `getRFMAnalysis()` - Segmentation RFM
- `getCustomerSegments()` - Segments clients
- `createABTest(testData)` - Créer test A/B
- `getABTests()` - Liste tests A/B
- `getABTestResults(testId)` - Résultats test

#### Support:
- `createTicket(ticketData)` - Créer ticket
- `getTickets(filters?)` - Liste tickets
- `replyToTicket(ticketId, message)` - Répondre
- `updateTicketStatus(ticketId, status)` - Changer statut
- `closeTicket(ticketId)` - Fermer ticket
- `getSupportStats()` - Statistiques support

#### Live Chat:
- `createRoom(participants)` - Créer room chat
- `getRooms()` - Liste rooms
- `getRoomHistory(roomId)` - Historique messages
- `markAsRead(roomId)` - Marquer comme lu
- `getWebSocketURL()` - URL WebSocket

#### E-commerce Integration:
- `connectShopify(credentials)` - Connecter Shopify
- `syncShopifyProducts()` - Sync produits Shopify
- `connectWooCommerce(credentials)` - Connecter WooCommerce
- `connectPrestaShop(credentials)` - Connecter PrestaShop
- `getConnectedStores()` - Liste stores connectés
- `disconnectPlatform(platform)` - Déconnecter

#### Payments:
- `createStripeCheckout(items)` - Checkout Stripe
- `createPayPalOrder(items)` - Ordre PayPal
- `createCryptoPayment(amount, currency)` - Paiement crypto
- `getTransactions(filters?)` - Historique transactions

#### KYC:
- `uploadDocuments(files)` - Upload documents KYC
- `getStatus()` - Statut vérification
- `verifyKYC(userId)` - Vérifier KYC (admin)
- `approveKYC(userId)` - Approuver (admin)
- `rejectKYC(userId, reason)` - Rejeter (admin)

#### Content Studio:
- `generateCaption(imageUrl, style)` - Générer caption AI
- `schedulePost(postData, platforms)` - Programmer post
- `uploadMedia(file)` - Upload média
- `createTemplate(templateData)` - Créer template

#### Mobile:
- `sendWhatsAppMessage(number, message)` - Envoyer WhatsApp
- `createOrangeMoneyPayment(amount, phone)` - Paiement Orange Money
- `createInwiMoneyPayment(amount, phone)` - Paiement Inwi Money
- `createMarocTelecomPayment(amount, phone)` - Paiement Maroc Telecom

---

## FRONTEND: Utilities

**Fichier:** `/frontend/src/utils/`

### 🛠️ Helpers

**Fichier:** `utils/helpers.js`

#### Fonctions:

##### `formatCurrency(amount: number, currency?: string = 'MAD') -> string`
- **Description:** Formatage devise avec Intl.NumberFormat
- **Exemples:**
  - `formatCurrency(1234.56, 'MAD')` → `"1 234,56 DH"`
  - `formatCurrency(1234.56, 'EUR')` → `"1 234,56 €"`

##### `formatDate(dateString: string) -> string`
- **Description:** Format date/time complet
- **Exemple:** `"12 janvier 2024 à 14:30"`

##### `formatDateShort(dateString: string) -> string`
- **Description:** Format date court
- **Exemple:** `"12/01/2024"`

##### `formatNumber(num: number) -> string`
- **Description:** Formatage nombre avec espaces
- **Exemple:** `1234567` → `"1 234 567"`

##### `getStatusColor(status: string) -> string`
- **Description:** Classe CSS pour badge statut
- **Retour:** Classes Tailwind
- **Exemples:**
  - `'pending'` → `"bg-yellow-100 text-yellow-800"`
  - `'active'` → `"bg-green-100 text-green-800"`
  - `'rejected'` → `"bg-red-100 text-red-800"`

##### `truncateText(text: string, maxLength: number = 50) -> string`
- **Description:** Tronquer texte avec "..."
- **Exemple:** `truncateText("Long text...", 10)` → `"Long text..."`

##### `formatPercentage(value: number, decimals: number = 1) -> string`
- **Description:** Formatage pourcentage
- **Exemple:** `formatPercentage(0.1234, 2)` → `"12.34%"`

##### `formatRelativeTime(dateString: string) -> string`
- **Description:** Temps relatif ("il y a X")
- **Exemples:**
  - `"il y a 2 heures"`
  - `"il y a 3 jours"`
  - `"il y a 1 mois"`

##### `exportToCSV(data: Array, filename: string)`
- **Description:** Export données en CSV
- **Télécharge:** Fichier CSV automatiquement

---

### 🚨 Error Handler

**Fichier:** `utils/errorHandler.js`

#### Fonctions:

##### `getErrorMessage(error: any, fallbackMessage?: string) -> string`
- **Description:** Extrait message d'erreur user-friendly
- **Sources:** `error.response.data.detail`, `error.message`, fallback

##### `getValidationErrors(error: any) -> object`
- **Description:** Parse erreurs validation FastAPI (422)
- **Retour:** `{ field: "message" }`

##### `isErrorStatus(error: any, statusCode: number) -> boolean`
- **Description:** Vérifie code HTTP

##### `isAuthError(error: any) -> boolean`
- **Description:** Vérifie si erreur auth (401/403)

##### `isValidationError(error: any) -> boolean`
- **Description:** Vérifie si erreur validation (422)

---

### 📊 Logger

**Fichier:** `utils/logger.js`

**Classe:** `Logger`

#### Méthodes:
- `debug(message, ...args)` - Log niveau DEBUG (dev only)
- `info(message, ...args)` - Log niveau INFO
- `warning(message, ...args)` - Log niveau WARNING
- `error(message, ...args)` - Log niveau ERROR
- `log(level, message, ...args)` - Log générique

**Features:**
- Conditional logging basé sur `NODE_ENV`
- Console styling en dev
- Silencieux en production (sauf errors)

---

## FRONTEND: Pages

**Total:** 90+ pages

### Dashboards (15 pages)

| Page | Route | Rôle | Description |
|------|-------|------|-------------|
| Dashboard | `/dashboard` | Tous | Router basé sur rôle |
| AdminDashboardComplete | `/dashboard` | Admin | Vue admin complète |
| MerchantDashboard | `/dashboard` | Merchant | Analytics merchant |
| InfluencerDashboard | `/dashboard` | Influencer | Stats influencer |
| CommercialDashboard | `/dashboard` | Commercial | Leads & deals |

### Settings (20+ pages)

- AccountSettings
- ProfileSettings
- SecuritySettings
- NotificationSettings
- BillingSettings
- IntegrationSettings
- APISettings
- TeamSettings
- PrivacySettings
- PreferencesSettings
- (+ 10 autres...)

### Affiliate (8 pages)

- AffiliatesList
- AffiliateDetails
- AffiliateLinks
- AffiliateEarnings
- AffiliatePayouts
- AffiliateRequests
- AffiliateContracts
- AffiliateStats

### Merchant (10 pages)

- ProductsList
- ProductDetails
- CreateProduct
- EditProduct
- CampaignsList
- CreateCampaign
- SalesList
- OrderManagement
- InventoryDashboard
- MerchantAnalytics

### Admin (12 pages)

- UserManagement
- MerchantApprovals
- InfluencerApprovals
- ModerationType
- SystemSettings
- AuditLogs
- ReportsCenter
- AnalyticsAdmin
- FinanceAdmin
- SupportTickets
- (+ 2 autres...)

### Autres (25+ pages)

- Login
- Register
- ForgotPassword
- ResetPassword
- EmailVerification
- Marketplace
- ProductDetail
- ServiceDetail
- TaxDashboard
- ContactSupport
- AboutUs
- TermsOfService
- PrivacyPolicy
- FAQ
- (+ 11 autres...)

---

## FRONTEND: Composants

**Total:** 100+ composants

### Layout Components (6)

| Composant | Props | Description |
|-----------|-------|-------------|
| Layout | `{ children }` | Wrapper principal avec sidebar |
| PublicLayout | `{ children }` | Layout pages publiques |
| Sidebar | `{ collapsed }` | Navigation sidebar |
| Navigation | `{ transparent }` | Top navbar |
| Footer | None | Footer global |
| NotificationBell | None | Dropdown notifications |

---

### Common/UI Components (20+)

| Composant | Props | Description |
|-----------|-------|-------------|
| Button | `{ variant, size, disabled, onClick, children, type }` | Bouton stylisé |
| Modal | `{ isOpen, onClose, title, children, size }` | Modal accessible |
| Card | `{ title, children, className }` | Content card |
| Table | `{ columns, data, onRowClick }` | Data table |
| FileUpload | `{ onUpload, accept, multiple }` | Upload fichier |
| Badge | `{ variant, children }` | Status badge |
| Toast | `{ toasts, removeToast }` | Toast notifications |
| StatCard | `{ label, value, icon, trend }` | Carte statistique |
| SkeletonLoader | `{ count, height }` | Loading skeleton |
| EmptyState | `{ icon, title, description }` | État vide |
| LazyImage | `{ src, alt, placeholder }` | Image lazy-loading |
| GlobalSearch | None | Barre recherche globale |
| LanguageSelector | None | Sélecteur langue i18n |
| ThemeToggle | None | Toggle dark/light |
| CookieConsent | None | Bandeau cookies |
| ErrorBoundary | `{ children, fallback }` | Error boundary |
| InstallPrompt | None | Prompt installation PWA |
| LoadingFallback | None | Fallback chargement |
| OfflineBanner | None | Indicateur hors ligne |
| PageTransition | `{ children }` | Animation transition page |

---

### Dashboard Components (15+)

| Composant | Props | Description |
|-----------|-------|-------------|
| DashboardCard | `{ title, children, icon }` | Widget dashboard |
| StatCard | `{ label, value, icon, trend }` | Carte stat |
| AISuggestions | None | Recommandations AI |
| LeadScoring | `{ lead }` | Score qualité lead |
| AdvancedFilters | `{ onFiltersChange }` | UI filtres |
| SubscriptionBanner | None | Bannière upgrade plan |
| PeriodComparison | `{ period1, period2 }` | Comparaison périodes |
| CalendarIntegration | None | Widget calendrier |
| EmailTracker | `{ emailId }` | Tracking email |
| ClickToCall | `{ number }` | Bouton appel |
| AIForecasting | None | Prévisions ventes AI |
| DashboardSkeleton | None | Skeleton chargement |

---

### Form Components (10+)

| Composant | Props | Description |
|-----------|-------|-------------|
| CreateCampaign | `{ onSubmit }` | Form campagne |
| CreateProduct | `{ onSubmit, initialProduct }` | Form produit |
| CreateLeadModal | `{ isOpen, onClose, onSubmit }` | Modal lead |
| CreateLinkModal | `{ isOpen, onClose }` | Modal lien affilié |
| ProductFormModal | `{ isOpen, onClose, onSubmit, product }` | Modal CRUD produit (admin) |
| UserFormModal | `{ isOpen, onClose, onSubmit, user }` | Modal user (admin) |
| ServiceFormModal | `{ isOpen, onClose }` | Modal service |

---

### Feature Components (15+)

| Composant | Props | Description |
|-----------|-------|-------------|
| AIRecommendationsWidget | None | Widget recommandations AI |
| AIChatbotWidget | None | Interface chatbot |
| SimilarProductsWidget | `{ productId }` | Produits similaires |
| AIInsightsPanel | None | Insights analytics |
| ProductRecommendations | `{ userId }` | Moteur recommandations |
| SwipeMatching | `{ items, onSwipe }` | Matching Tinder-style |
| ContentStudio | None | Outils création contenu |
| LiveShoppingStudio | None | Interface live shopping |
| ReferralDashboard | None | Tracking parrainage |
| GamificationWidget | None | Features gamification |

---

### Chat & Support (7)

| Composant | Props | Description |
|-----------|-------|-------------|
| LiveChatWidget | None | Widget chat live |
| ChatWindow | `{ roomId }` | Fenêtre chat |
| ChatRoomsList | None | Liste rooms |
| SupportTicketsList | None | Liste tickets |
| TicketDetailView | `{ ticketId }` | Détails ticket |
| CreateTicketForm | `{ onSubmit }` | Form ticket |
| SupportStatsWidget | None | Stats support |

---

### Analytics (4)

| Composant | Props | Description |
|-----------|-------|-------------|
| CohortAnalysisView | None | Charts cohortes |
| RFMSegmentationView | None | Segmentation RFM |
| CustomerSegmentsPanel | None | Segments clients |
| ABTestingManager | None | Gestion tests A/B |

---

### Mobile Components (5)

| Composant | Props | Description |
|-----------|-------|-------------|
| MobileLayout | `{ children }` | Layout mobile |
| MobileDashboard | None | Dashboard mobile |
| BottomNavigation | None | Nav bottom tabs |
| QuickActions | None | Boutons actions rapides |
| PWAInstallPrompt | None | Dialog install PWA |

---

### Autres Composants (40+)

- ProductDetailHeader, ProductDetailInfo, ProductDetailActions, ProductDetailReviews
- CollaborationRequestModal, ContractModal, InvitationModal
- AffiliateLinksGenerator, AffiliateLinksTable, CommissionsTable
- MobilePaymentWidget
- TikTokProductSync, TikTokAnalyticsDashboard
- WhatsAppShareButton, WhatsAppFloatingButton
- SEOHead, OptimizedImage
- NotificationCenter
- AnimatedCard
- EcommerceIntegrationsPanel
- CreateLeadForm, PendingLeadsTable, DepositBalanceCard
- TrialCountdown, SubscriptionLimitAlert
- UserDetailsDrawer, PlanChangeModal, RefundModal
- InfluencerSearch
- ContentStudioDashboard
- SocialPublishModal
- RequestAffiliationModal
- TemplatesModal
- (+ 20 autres...)

---

## 📊 STATISTIQUES FINALES

| Catégorie | Backend | Frontend | Total |
|-----------|---------|----------|-------|
| **Fonctions/Méthodes** | 100+ | - | 100+ |
| **API Endpoints** | 100+ | - | 100+ |
| **Pages** | - | 90+ | 90+ |
| **Composants** | - | 100+ | 100+ |
| **Hooks** | - | 16+ | 16+ |
| **Services** | 10+ | 4+ | 14+ |
| **Utilitaires** | 24+ | 10+ | 34+ |
| **Context Providers** | - | 6 | 6 |
| **TOTAL GLOBAL** | **234+** | **226+** | **460+** |

---

## 🎯 PATTERNS ARCHITECTURAUX

### Backend
1. **Layered Architecture**
   - Database Layer (db_helpers)
   - Service Layer (services/)
   - API Layer (server.py)
   - Utility Layer (utils/)

2. **Security First**
   - JWT authentication
   - httpOnly cookies
   - SQL injection protection
   - Input sanitization

3. **Performance Optimization**
   - Caching (TTL-based)
   - Batch operations
   - Eager loading (N+1 prevention)
   - Database optimization

### Frontend
1. **Component-Based Architecture**
   - Atomic design (atoms → molecules → organisms)
   - Reusable components
   - Props composition

2. **State Management**
   - Context API (Auth, Theme, Notifications)
   - React Hooks (useState, useEffect, custom)
   - React Query (server state)

3. **Code Splitting**
   - Lazy loading
   - Route-based splitting
   - Component lazy loading

4. **Accessibility**
   - ARIA labels
   - Keyboard navigation
   - Screen reader support
   - Reduced motion support

5. **Offline Support**
   - Service Workers
   - IndexedDB persistence
   - Request queueing
   - Auto-sync

---

## 🗂️ ORGANISATION FICHIERS

### Backend
```
backend/
├── server.py (100+ endpoints)
├── db_helpers.py (48 fonctions)
├── auth.py (5 fonctions)
├── utils/
│   ├── cache.py
│   ├── logger.py
│   ├── db_safe.py (7 fonctions)
│   ├── db_optimized.py (9 méthodes)
│   └── image_processing.py
├── services/
│   ├── gamification_service.py
│   ├── ai_bot_service.py
│   ├── notification_service.py
│   └── advanced_analytics_service.py
└── middleware/
    └── security.py
```

### Frontend
```
frontend/src/
├── pages/ (90+ pages)
├── components/ (100+ composants)
├── hooks/ (16+ hooks)
├── services/
│   ├── api.js
│   ├── paymentService.js
│   ├── fiscalService.js
│   └── newEndpointsAPI.js
├── context/ (6 providers)
├── utils/ (10+ utilities)
└── config/
```

---

**Dernière mise à jour :** 2026-01-04
**Version :** 1.0
**Total Items Documentés :** 460+
