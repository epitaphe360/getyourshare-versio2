# Intégration Complète des Tableaux de Bord - Affiliation Services

## Résumé
L'intégration de l'affiliation pour les Services (en plus des Produits) est terminée sur l'ensemble de la plateforme (Backend & Frontend).

## Modifications Effectuées

### 1. Base de Données
- Ajout de la colonne `service_id` aux tables :
  - `affiliation_requests`
  - `affiliate_links`
  - `social_media_publications`
  - `tracking_links`
- Mise à jour des contraintes pour permettre l'affiliation soit sur un Produit, soit sur un Service.

### 2. Backend (API)
- **Affiliation Links** (`/api/affiliate/*`) :
  - Support de `service_id` pour la génération de liens.
  - Support de `service_id` pour la récupération des liens (`/my-links`).
  - Support de `service_id` pour la publication sur les réseaux sociaux.
- **Affiliation Requests** (`/api/affiliation-requests/*`) :
  - Création de demande supporte désormais `service_id`.
  - Approbation/Refus gère correctement les services.
- **Tracking Service** :
  - Création de liens de tracking pour les services.
  - Redirection vers la page du service.
- **Endpoints Dashboard** :
  - Ajout de `/api/merchant/affiliation-requests` (Liste complète pour le marchand).
  - Ajout de `/api/merchant/affiliation-requests/{id}/approve` & `/reject`.
  - Ajout de `/api/influencer/affiliate-links` (Pour le dashboard influenceur).

### 3. Frontend (Dashboards)
- **Influencer Dashboard** :
  - `MyLinks.js` : Affiche désormais les Services avec leurs détails (Titre, Prix).
  - `SocialPublishModal.js` : Adapté pour afficher les infos du Service lors de la publication.
  - `InfluencerDashboard.jsx` : Tableau des liens compatible avec les Services.
- **Merchant Dashboard** :
  - `MerchantAffiliationRequests.js` : Affiche les demandes pour les Services.
- **Marketplace** :
  - `MarketplaceV2.js` : Le bouton "Demander l'affiliation" fonctionne pour les Services (appelle le nouvel endpoint).

## Vérification
- Les influenceurs peuvent désormais voir et partager des liens pour des Services.
- Les marchands peuvent voir et approuver les demandes pour leurs Services.
- Les QR Codes sont générés localement pour tous les liens.
- La publication sur les réseaux sociaux inclut les métadonnées des Services.

## Prochaines Étapes
- Vérifier que les images des services s'affichent correctement (si disponibles).
- Tester le flux complet : Demande -> Approbation -> Publication -> Clic -> Tracking.
