# 📚 Documentation API GetYourShare

## Table des Matières

- [Introduction](#introduction)
- [Authentification](#authentification)
- [Endpoints](#endpoints)
- [Modèles de Données](#modèles-de-données)
- [Codes d'Erreur](#codes-derreur)
- [Rate Limiting](#rate-limiting)
- [Webhooks](#webhooks)
- [Exemples](#exemples)

## 🎯 Introduction

L'API GetYourShare est une API RESTful qui permet d'accéder à toutes les fonctionnalités de la plateforme d'affiliation.

**Base URL:** `https://api.getyourshare.com/api`  
**Version:** v1  
**Format:** JSON  
**Protocol:** HTTPS only

### Authentification

Toutes les requêtes API nécessitent un token JWT dans le header `Authorization`.

```bash
Authorization: Bearer <your_jwt_token>
```

#### Obtenir un Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Réponse:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "role": "merchant",
      "subscription_tier": "pro"
    }
  }
}
```

#### Rafraîchir un Token

```http
POST /api/auth/refresh
Authorization: Bearer <your_jwt_token>
```

## 📡 Endpoints

### Authentification

#### POST /auth/register
Créer un nouveau compte utilisateur.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "role": "merchant",
  "company_name": "Ma Boutique"
}
```

**Réponse:** `201 Created`

#### POST /auth/login
Se connecter avec email et mot de passe.

#### POST /auth/logout
Déconnexion (invalide le token).

#### POST /auth/forgot-password
Demander un lien de réinitialisation.

#### POST /auth/reset-password
Réinitialiser le mot de passe avec le token.

---

### Produits

#### GET /products
Liste tous les produits.

**Query Parameters:**
- `page` (int): Numéro de page (défaut: 1)
- `page_size` (int): Taille de page (défaut: 20, max: 100)
- `category` (string): Filtrer par catégorie
- `min_price` (float): Prix minimum
- `max_price` (float): Prix maximum
- `search` (string): Recherche texte

**Exemple:**
```http
GET /api/products?page=1&page_size=20&category=electronics&min_price=10&max_price=100
Authorization: Bearer <token>
```

**Réponse:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "prod_123",
      "name": "iPhone 15 Pro",
      "description": "Dernier iPhone d'Apple",
      "price": 1199.99,
      "commission_rate": 5.0,
      "category": "electronics",
      "image_url": "https://cdn.getyourshare.com/products/iphone15.jpg",
      "stock": 50,
      "merchant": {
        "id": "user_456",
        "company_name": "Apple Store FR"
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### GET /products/:id
Obtenir un produit par ID.

**Réponse:** `200 OK`

#### POST /products
Créer un nouveau produit (Merchant only).

**Body:**
```json
{
  "name": "Nouveau Produit",
  "description": "Description détaillée",
  "price": 49.99,
  "commission_rate": 10.0,
  "category": "fashion",
  "stock": 100,
  "image_url": "https://example.com/image.jpg"
}
```

**Réponse:** `201 Created`

#### PUT /products/:id
Mettre à jour un produit.

#### DELETE /products/:id
Supprimer un produit.

---

### Campagnes

#### GET /campaigns
Liste toutes les campagnes.

**Query Parameters:**
- `status` (string): active, paused, completed
- `merchant_id` (string): Filtrer par marchand

**Réponse:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "camp_789",
      "name": "Black Friday 2024",
      "description": "Promotion spéciale Black Friday",
      "merchant_id": "user_456",
      "start_date": "2024-11-24T00:00:00Z",
      "end_date": "2024-11-30T23:59:59Z",
      "budget": 10000.00,
      "spent": 4500.00,
      "commission_rate": 15.0,
      "status": "active",
      "products": ["prod_123", "prod_456"],
      "stats": {
        "clicks": 5430,
        "conversions": 234,
        "revenue": 28950.00
      }
    }
  ]
}
```

#### POST /campaigns
Créer une campagne.

#### GET /campaigns/:id
Détails d'une campagne.

#### PUT /campaigns/:id
Modifier une campagne.

#### DELETE /campaigns/:id
Supprimer une campagne.

---

### Liens d'Affiliation

#### POST /affiliate-links
Générer un lien d'affiliation.

**Body:**
```json
{
  "campaign_id": "camp_789",
  "product_id": "prod_123",
  "custom_params": {
    "source": "instagram",
    "post_id": "12345"
  }
}
```

**Réponse:** `201 Created`
```json
{
  "success": true,
  "data": {
    "id": "link_abc123",
    "short_code": "xyz789",
    "full_url": "https://getyourshare.com/r/xyz789",
    "campaign_id": "camp_789",
    "product_id": "prod_123",
    "influencer_id": "user_999",
    "created_at": "2024-01-15T14:30:00Z"
  }
}
```

#### GET /affiliate-links
Liste des liens d'affiliation de l'utilisateur.

#### GET /affiliate-links/:id/stats
Statistiques d'un lien.

**Réponse:** `200 OK`
```json
{
  "success": true,
  "data": {
    "link_id": "link_abc123",
    "clicks": 1234,
    "unique_clicks": 890,
    "conversions": 45,
    "conversion_rate": 5.06,
    "revenue": 2250.00,
    "commission": 337.50,
    "clicks_by_date": [
      {"date": "2024-01-15", "clicks": 120},
      {"date": "2024-01-16", "clicks": 145}
    ]
  }
}
```

---

### Analytics

#### GET /analytics/dashboard
Tableau de bord analytics.

**Query Parameters:**
- `start_date` (ISO 8601): Date de début
- `end_date` (ISO 8601): Date de fin

**Réponse:** `200 OK`
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_revenue": 125000.00,
      "total_commission": 18750.00,
      "total_clicks": 45320,
      "total_conversions": 2134,
      "conversion_rate": 4.71
    },
    "mrr": 15000.00,
    "arr": 180000.00,
    "churn_rate": 2.5,
    "active_campaigns": 12,
    "active_influencers": 234
  }
}
```

#### GET /analytics/reports
Générer un rapport personnalisé.

**Query Parameters:**
- `type` (string): sales, commissions, clicks, users
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)
- `group_by` (string): day, week, month

---

### Transactions

#### GET /transactions
Liste des transactions.

**Query Parameters:**
- `status` (string): pending, completed, failed
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)

**Réponse:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "id": "txn_123456",
      "link_id": "link_abc123",
      "campaign_id": "camp_789",
      "product_id": "prod_123",
      "influencer_id": "user_999",
      "merchant_id": "user_456",
      "amount": 99.99,
      "commission": 14.99,
      "commission_rate": 15.0,
      "status": "completed",
      "created_at": "2024-01-15T16:45:30Z",
      "paid_at": "2024-01-20T10:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### GET /transactions/:id
Détails d'une transaction.

---

### Paiements

#### POST /payouts/request
Demander un paiement.

**Body:**
```json
{
  "amount": 500.00,
  "method": "bank_transfer",
  "bank_details": {
    "iban": "FR76XXXXXXXXXXXXXXXX",
    "bic": "BNPAFRPP"
  }
}
```

**Réponse:** `201 Created`

#### GET /payouts
Historique des paiements.

---

### Utilisateurs (Admin only)

#### GET /admin/users
Liste tous les utilisateurs.

**Query Parameters:**
- `role` (string): admin, merchant, influencer, commercial
- `subscription_tier` (string): free, basic, pro, enterprise
- `search` (string)

#### GET /admin/users/:id
Détails d'un utilisateur.

#### PUT /admin/users/:id
Modifier un utilisateur.

#### DELETE /admin/users/:id
Supprimer un utilisateur.

---

### Notifications

#### GET /notifications
Liste des notifications.

#### PUT /notifications/:id/read
Marquer comme lue.

#### DELETE /notifications/:id
Supprimer une notification.

#### WebSocket /ws/notifications/:user_id
Connexion WebSocket temps réel.

```javascript
const ws = new WebSocket('wss://api.getyourshare.com/ws/notifications/user_123?token=jwt_token');

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};
```

---

### Leads

#### GET /leads
Liste des leads.

#### POST /leads
Créer un lead.

#### PUT /leads/:id
Mettre à jour un lead.

#### GET /leads/stats
Statistiques des leads.

---

## 📦 Modèles de Données

### User

```typescript
interface User {
  id: string;
  email: string;
  role: 'admin' | 'merchant' | 'influencer' | 'commercial';
  company_name?: string;
  subscription_tier: 'free' | 'basic' | 'pro' | 'enterprise';
  subscription_status: 'active' | 'cancelled' | 'expired';
  metadata: {
    phone?: string;
    country?: string;
    company_size?: string;
  };
  created_at: string;
  last_login: string;
}
```

### Product

```typescript
interface Product {
  id: string;
  merchant_id: string;
  name: string;
  description: string;
  price: number;
  commission_rate: number;
  category: string;
  image_url: string;
  stock: number;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
}
```

### Campaign

```typescript
interface Campaign {
  id: string;
  merchant_id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  budget: number;
  spent: number;
  commission_rate: number;
  status: 'draft' | 'active' | 'paused' | 'completed';
  products: string[];
  created_at: string;
}
```

### Transaction

```typescript
interface Transaction {
  id: string;
  link_id: string;
  campaign_id: string;
  product_id: string;
  influencer_id: string;
  merchant_id: string;
  amount: number;
  commission: number;
  commission_rate: number;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  created_at: string;
  paid_at?: string;
}
```

---

## ⚠️ Codes d'Erreur

| Code | Description |
|------|-------------|
| 200 | OK - Requête réussie |
| 201 | Created - Ressource créée |
| 400 | Bad Request - Paramètres invalides |
| 401 | Unauthorized - Token manquant ou invalide |
| 403 | Forbidden - Permissions insuffisantes |
| 404 | Not Found - Ressource introuvable |
| 409 | Conflict - Conflit (ex: email déjà utilisé) |
| 422 | Unprocessable Entity - Validation échouée |
| 429 | Too Many Requests - Rate limit dépassé |
| 500 | Internal Server Error - Erreur serveur |
| 503 | Service Unavailable - Service indisponible |

**Format d'Erreur:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is required",
    "details": {
      "field": "email",
      "constraint": "required"
    }
  }
}
```

---

## 🚦 Rate Limiting

Les limites de requêtes varient selon le plan d'abonnement:

| Plan | Requêtes/heure | Requêtes/jour |
|------|----------------|---------------|
| Free | 100 | 1,000 |
| Basic | 1,000 | 10,000 |
| Pro | 10,000 | 100,000 |
| Enterprise | Illimité | Illimité |

**Headers de Rate Limit:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705334400
```

---

## 🪝 Webhooks

Configurez des webhooks pour recevoir des notifications en temps réel.

### Événements Disponibles

- `transaction.completed` - Transaction terminée
- `transaction.failed` - Transaction échouée
- `payout.processed` - Paiement traité
- `campaign.started` - Campagne démarrée
- `campaign.ended` - Campagne terminée
- `user.registered` - Nouvel utilisateur

### Configuration

```http
POST /api/webhooks
Authorization: Bearer <token>

{
  "url": "https://votre-site.com/webhook",
  "events": ["transaction.completed", "payout.processed"],
  "secret": "webhook_secret_key"
}
```

### Payload Webhook

```json
{
  "event": "transaction.completed",
  "timestamp": "2024-01-15T18:30:00Z",
  "data": {
    "transaction_id": "txn_123456",
    "amount": 99.99,
    "commission": 14.99
  },
  "signature": "sha256=abcdef123456..."
}
```

### Vérification Signature

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 💡 Exemples

### Python

```python
import requests

API_BASE = "https://api.getyourshare.com/api"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Obtenir les produits
response = requests.get(f"{API_BASE}/products", headers=headers)
products = response.json()["data"]

# Créer un lien d'affiliation
link_data = {
    "campaign_id": "camp_123",
    "product_id": "prod_456"
}
response = requests.post(
    f"{API_BASE}/affiliate-links",
    json=link_data,
    headers=headers
)
link = response.json()["data"]
print(f"Lien créé: {link['full_url']}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_BASE = 'https://api.getyourshare.com/api';
const TOKEN = 'your_jwt_token';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Obtenir les transactions
async function getTransactions() {
  try {
    const response = await api.get('/transactions', {
      params: {
        status: 'completed',
        start_date: '2024-01-01'
      }
    });
    return response.data.data;
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// Créer un produit
async function createProduct(productData) {
  const response = await api.post('/products', productData);
  return response.data.data;
}
```

### cURL

```bash
# Login
curl -X POST https://api.getyourshare.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Obtenir les produits
curl -X GET "https://api.getyourshare.com/api/products?page=1&page_size=20" \
  -H "Authorization: Bearer your_jwt_token"

# Créer un lien d'affiliation
curl -X POST https://api.getyourshare.com/api/affiliate-links \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"campaign_id":"camp_123","product_id":"prod_456"}'
```

---

## 🔐 Sécurité

### Best Practices

1. **Stockage des Tokens**
   - Ne jamais stocker en clair dans le code
   - Utiliser des variables d'environnement
   - Renouveler régulièrement

2. **HTTPS Uniquement**
   - Toujours utiliser HTTPS en production
   - Ne jamais envoyer de tokens via HTTP

3. **Validation**
   - Valider toutes les entrées côté client ET serveur
   - Échapper les données avant affichage

4. **Rate Limiting**
   - Respecter les limites de requêtes
   - Implémenter un système de retry avec backoff

---

## 📞 Support

- 📧 **Email:** api@getyourshare.com
- 💬 **Discord:** https://discord.gg/getyourshare
- 📚 **Documentation:** https://docs.getyourshare.com
- 🐛 **Issues:** https://github.com/epitaphe360/getyourshare-versio2/issues

---

**Version:** 1.0.0  
**Dernière mise à jour:** Janvier 2024
