# 📡 Documentation API - Services & Leads

## Base URL
```
http://localhost:5000
```

---

## 🔓 Endpoints Publics (Pas d'authentification requise)

### 1. Liste des Services Actifs
```http
GET /api/public/services
```

**Query Parameters :**
- `categorie_id` (optional) - Filtrer par catégorie
- `search` (optional) - Recherche par nom/description

**Réponse (200 OK) :**
```json
{
  "success": true,
  "services": [
    {
      "id": "uuid",
      "nom": "Service Marketing Digital",
      "description": "Description du service",
      "images": ["https://url1.jpg", "https://url2.jpg"],
      "categorie_id": "uuid",
      "categorie_nom": "Marketing Digital",
      "prix_par_lead": 25.00,
      "leads_possibles": 40,
      "depot_actuel": 1000.00,
      "statut": "actif",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### 2. Détails d'un Service Public
```http
GET /api/public/services/{service_id}
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Réponse (200 OK) :**
```json
{
  "success": true,
  "service": {
    "id": "uuid",
    "nom": "Service Marketing Digital",
    "description": "Description complète",
    "images": ["https://url1.jpg"],
    "categorie_id": "uuid",
    "categorie_nom": "Marketing Digital",
    "prix_par_lead": 25.00,
    "leads_possibles": 40,
    "formulaire_champs": ["nom", "email", "telephone", "message"],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 3. Créer un Lead (Demande de Service)
```http
POST /api/leads
```

**Body (JSON) :**
```json
{
  "service_id": "uuid",
  "nom_client": "Jean Dupont",
  "email_client": "jean@example.com",
  "telephone_client": "+212600000000",
  "donnees_formulaire": {
    "message": "Je suis intéressé par ce service",
    "entreprise": "Ma Société"
  }
}
```

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Lead créé avec succès",
  "lead": {
    "id": "uuid",
    "service_id": "uuid",
    "nom_client": "Jean Dupont",
    "email_client": "jean@example.com",
    "telephone_client": "+212600000000",
    "cout_lead": 25.00,
    "statut": "nouveau",
    "created_at": "2024-01-15T14:20:00Z"
  }
}
```

**Erreurs possibles :**
- `400` - Données invalides ou champs manquants
- `404` - Service non trouvé
- `400` - Dépôt insuffisant

---

### 4. Liste des Catégories
```http
GET /api/categories
```

**Réponse (200 OK) :**
```json
{
  "success": true,
  "categories": [
    {
      "id": "uuid",
      "name": "Marketing Digital",
      "description": "Services de marketing en ligne",
      "created_at": "2024-01-10T09:00:00Z"
    },
    {
      "id": "uuid",
      "name": "Design Graphique",
      "description": "Création visuelle et branding",
      "created_at": "2024-01-10T09:00:00Z"
    }
  ]
}
```

---

## 🔐 Endpoints Admin (Authentification requise)

**Header requis pour tous les endpoints admin :**
```http
Authorization: Bearer {JWT_TOKEN}
```

---

### 5. Créer un Service (Admin)
```http
POST /api/admin/services
```

**Body (JSON) :**
```json
{
  "nom": "Service Marketing Digital",
  "description": "Description complète du service",
  "images": ["https://url1.jpg", "https://url2.jpg"],
  "categorie_id": "uuid",
  "marchand_id": "uuid",
  "depot_initial": 1000.00,
  "prix_par_lead": 25.00,
  "commission_rate": 20.00,
  "formulaire_champs": {
    "champs": ["nom", "email", "telephone", "message"]
  },
  "statut": "actif"
}
```

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Service créé avec succès",
  "service": {
    "id": "uuid",
    "nom": "Service Marketing Digital",
    "depot_initial": 1000.00,
    "depot_actuel": 1000.00,
    "prix_par_lead": 25.00,
    "leads_possibles": 40,
    "leads_recus": 0,
    "statut": "actif",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 6. Liste de Tous les Services (Admin)
```http
GET /api/admin/services
```

**Query Parameters :**
- `statut` (optional) - Filtrer par statut (actif, pause, termine, archive)
- `categorie_id` (optional) - Filtrer par catégorie
- `marchand_id` (optional) - Filtrer par marchand
- `search` (optional) - Recherche par nom/description

**Réponse (200 OK) :**
```json
{
  "success": true,
  "services": [
    {
      "id": "uuid",
      "nom": "Service Marketing Digital",
      "description": "Description",
      "categorie_nom": "Marketing Digital",
      "marchand_nom": "Société ABC",
      "depot_initial": 1000.00,
      "depot_actuel": 750.00,
      "prix_par_lead": 25.00,
      "leads_possibles": 30,
      "leads_recus": 10,
      "taux_conversion": 60.00,
      "statut": "actif",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### 7. Détails d'un Service (Admin)
```http
GET /api/admin/services/{service_id}
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Réponse (200 OK) :**
```json
{
  "success": true,
  "service": {
    "id": "uuid",
    "nom": "Service Marketing Digital",
    "description": "Description complète",
    "images": ["https://url1.jpg"],
    "categorie_id": "uuid",
    "categorie_nom": "Marketing Digital",
    "marchand_id": "uuid",
    "marchand_nom": "Société ABC",
    "depot_initial": 1000.00,
    "depot_actuel": 750.00,
    "prix_par_lead": 25.00,
    "commission_rate": 20.00,
    "leads_possibles": 30,
    "leads_recus": 10,
    "taux_conversion": 60.00,
    "formulaire_champs": ["nom", "email", "telephone"],
    "statut": "actif",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T14:20:00Z"
  }
}
```

---

### 8. Modifier un Service (Admin)
```http
PUT /api/admin/services/{service_id}
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Body (JSON) - Tous les champs sont optionnels :**
```json
{
  "nom": "Nouveau nom",
  "description": "Nouvelle description",
  "images": ["https://newurl.jpg"],
  "prix_par_lead": 30.00,
  "statut": "pause"
}
```

**Réponse (200 OK) :**
```json
{
  "success": true,
  "message": "Service mis à jour avec succès",
  "service": {
    "id": "uuid",
    "nom": "Nouveau nom",
    "updated_at": "2024-01-16T15:00:00Z"
  }
}
```

---

### 9. Supprimer un Service (Admin)
```http
DELETE /api/admin/services/{service_id}
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Réponse (200 OK) :**
```json
{
  "success": true,
  "message": "Service supprimé avec succès"
}
```

**Note :** La suppression est en CASCADE - tous les leads, recharges et extras associés seront également supprimés.

---

### 10. Liste de Tous les Leads (Admin)
```http
GET /api/admin/leads
```

**Query Parameters :**
- `service_id` (optional) - Filtrer par service
- `marchand_id` (optional) - Filtrer par marchand
- `statut` (optional) - Filtrer par statut (nouveau, en_cours, converti, perdu, spam)

**Réponse (200 OK) :**
```json
{
  "success": true,
  "leads": [
    {
      "id": "uuid",
      "service_id": "uuid",
      "service_nom": "Service Marketing Digital",
      "marchand_id": "uuid",
      "marchand_nom": "Société ABC",
      "nom_client": "Jean Dupont",
      "email_client": "jean@example.com",
      "telephone_client": "+212600000000",
      "donnees_formulaire": {"message": "Intéressé"},
      "cout_lead": 25.00,
      "statut": "nouveau",
      "created_at": "2024-01-16T14:20:00Z",
      "notes_marchand": null
    }
  ]
}
```

---

### 11. Détails d'un Lead (Admin)
```http
GET /api/admin/leads/{lead_id}
```

**Path Parameters :**
- `lead_id` (required) - UUID du lead

**Réponse (200 OK) :**
```json
{
  "success": true,
  "lead": {
    "id": "uuid",
    "service_id": "uuid",
    "service_nom": "Service Marketing Digital",
    "marchand_id": "uuid",
    "marchand_nom": "Société ABC",
    "nom_client": "Jean Dupont",
    "email_client": "jean@example.com",
    "telephone_client": "+212600000000",
    "donnees_formulaire": {
      "message": "Je suis intéressé",
      "entreprise": "Ma Société"
    },
    "cout_lead": 25.00,
    "statut": "nouveau",
    "created_at": "2024-01-16T14:20:00Z",
    "updated_at": "2024-01-16T14:20:00Z",
    "notes_marchand": "Client très intéressé"
  }
}
```

---

### 12. Mettre à Jour le Statut d'un Lead (Admin)
```http
PUT /api/admin/leads/{lead_id}/status
```

**Path Parameters :**
- `lead_id` (required) - UUID du lead

**Body (JSON) :**
```json
{
  "statut": "converti",
  "notes_marchand": "Client converti, contrat signé"
}
```

**Statuts autorisés :**
- `nouveau`
- `en_cours`
- `converti`
- `perdu`
- `spam`

**Réponse (200 OK) :**
```json
{
  "success": true,
  "message": "Statut du lead mis à jour",
  "lead": {
    "id": "uuid",
    "statut": "converti",
    "notes_marchand": "Client converti, contrat signé",
    "updated_at": "2024-01-16T16:00:00Z"
  }
}
```

**Note :** Le trigger `update_conversion_rate` recalcule automatiquement le taux de conversion du service.

---

### 13. Recharger le Dépôt d'un Service (Admin)
```http
POST /api/admin/services/{service_id}/recharge
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Body (JSON) :**
```json
{
  "montant": 500.00,
  "payment_method": "carte_bancaire",
  "payment_reference": "REF123456"
}
```

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Recharge effectuée avec succès",
  "recharge": {
    "id": "uuid",
    "service_id": "uuid",
    "montant": 500.00,
    "ancien_solde": 750.00,
    "nouveau_solde": 1250.00,
    "leads_ajoutes": 20,
    "created_at": "2024-01-16T16:30:00Z"
  }
}
```

**Note :** Le trigger `add_recharge_to_deposit` met automatiquement à jour `depot_actuel` du service.

---

### 14. Historique des Recharges (Admin)
```http
GET /api/admin/services/{service_id}/recharges
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Réponse (200 OK) :**
```json
{
  "success": true,
  "recharges": [
    {
      "id": "uuid",
      "montant": 500.00,
      "ancien_solde": 750.00,
      "nouveau_solde": 1250.00,
      "leads_ajoutes": 20,
      "payment_method": "carte_bancaire",
      "payment_reference": "REF123456",
      "created_at": "2024-01-16T16:30:00Z"
    }
  ]
}
```

---

### 15. Ajouter un Extra à un Service (Admin)
```http
POST /api/admin/services/{service_id}/extras
```

**Path Parameters :**
- `service_id` (required) - UUID du service

**Body (JSON) :**
```json
{
  "type": "boost",
  "nom": "Boost 7 jours",
  "description": "Service mis en avant pendant 7 jours",
  "prix": 50.00,
  "date_debut": "2024-01-17T00:00:00Z",
  "date_fin": "2024-01-24T23:59:59Z",
  "actif": true
}
```

**Types d'extras :**
- `boost` - Mise en avant
- `featured` - Service vedette
- `priority` - Priorité dans les résultats

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Extra ajouté avec succès",
  "extra": {
    "id": "uuid",
    "service_id": "uuid",
    "type": "boost",
    "nom": "Boost 7 jours",
    "prix": 50.00,
    "actif": true,
    "created_at": "2024-01-16T17:00:00Z"
  }
}
```

---

### 16. Statistiques Globales des Services (Admin)
```http
GET /api/admin/services/stats
```

**Réponse (200 OK) :**
```json
{
  "success": true,
  "stats": {
    "total_services": 25,
    "services_actifs": 18,
    "depot_total": 45000.00,
    "leads_total": 1250,
    "leads_convertis": 780,
    "taux_conversion_global": 62.40,
    "revenue_total": 31250.00
  }
}
```

---

## 📊 Codes de Statut HTTP

- `200 OK` - Requête réussie
- `201 Created` - Ressource créée avec succès
- `400 Bad Request` - Données invalides ou manquantes
- `401 Unauthorized` - Token manquant ou invalide
- `403 Forbidden` - Permissions insuffisantes
- `404 Not Found` - Ressource non trouvée
- `500 Internal Server Error` - Erreur serveur

---

## 🔒 Authentification

**Obtenir un token JWT :**
```http
POST /api/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "password123"
}
```

**Réponse :**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**Utiliser le token :**
```http
GET /api/admin/services
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🧪 Exemples avec cURL

### Créer un lead (public)
```bash
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "uuid-du-service",
    "nom_client": "Jean Dupont",
    "email_client": "jean@example.com",
    "telephone_client": "+212600000000",
    "donnees_formulaire": {"message": "Intéressé"}
  }'
```

### Lister les services (admin)
```bash
curl http://localhost:5000/api/admin/services \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Recharger un service (admin)
```bash
curl -X POST http://localhost:5000/api/admin/services/uuid-du-service/recharge \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "montant": 500,
    "payment_method": "carte_bancaire",
    "payment_reference": "REF123"
  }'
```

---

## 📝 Notes Importantes

1. **Déduction automatique** : Quand un lead est créé, le dépôt est déduit automatiquement par le trigger `deduct_lead_cost`

2. **Conversion rate** : Le taux de conversion se calcule automatiquement quand le statut d'un lead change

3. **Leads possibles** : Calculé automatiquement : `FLOOR(depot_actuel / prix_par_lead)`

4. **Cascade delete** : Supprimer un service supprime aussi tous ses leads, recharges et extras

5. **Statuts de service** :
   - `actif` : Visible publiquement
   - `pause` : Masqué temporairement
   - `termine` : Plus de dépôt
   - `archive` : Archivé définitivement

6. **Validation** : Tous les endpoints valident les données avec Pydantic

---

**Version API :** 1.0.0  
**Dernière mise à jour :** Janvier 2024
