# Rapport de Mise en Conformité RGPD/CCPA

## 1. Vue d'ensemble
Ce document détaille les modifications techniques et juridiques apportées à la plateforme ShareYourSales pour assurer la conformité avec le RGPD (Règlement Général sur la Protection des Données) et le CCPA (California Consumer Privacy Act).

## 2. Modifications Juridiques (Frontend)

### 2.1 Conditions Générales d'Utilisation (`Terms.js`)
- **Ajout de l'Article 5** : "Protection des Données (RGPD & CCPA)".
- **Contenu** : Explication claire des droits des utilisateurs (accès, rectification, suppression, portabilité) et mention explicite de l'anonymisation des adresses IP.
- **Mise à jour** : Date de dernière mise à jour actualisée au 2 novembre 2024.

### 2.2 Politique de Confidentialité (`Privacy.js`)
- Vérification de la présence des clauses nécessaires concernant la collecte, l'utilisation et la protection des données.
- Confirmation des coordonnées du DPO (Data Protection Officer) ou du point de contact privacy.

### 2.3 Bandeau Cookies (`CookieConsent.js`)
- Vérification du mécanisme de consentement explicite pour les cookies non essentiels.

## 3. Modifications Techniques (Backend)

### 3.1 Anonymisation des Adresses IP (`tracking_service.py`)
- **Problème identifié** : Les adresses IP des utilisateurs cliquant sur les liens d'affiliation étaient stockées en clair.
- **Solution implémentée** : 
  - Création d'une méthode `anonymize_ip(ip_address)` utilisant un hachage SHA-256 avec un sel cryptographique (`sys_gdpr_salt_2025`).
  - Modification de la méthode `track_click` pour hacher l'IP avant tout enregistrement dans la base de données (`click_logs`).
- **Impact** : Il est désormais mathématiquement impossible de retrouver l'IP originale d'un utilisateur à partir des logs, tout en permettant de détecter les clics frauduleux (doublons) via le hash unique.

### 3.2 Protection des Formulaires de Contact (`contact_endpoints.py`)
- **Problème identifié** : Les IP des utilisateurs soumettant le formulaire de contact étaient potentiellement exposées.
- **Solution implémentée** :
  - Injection de la logique d'anonymisation IP dans l'endpoint `/api/contact/submit`.
  - L'IP stockée dans la table `contact_messages` est désormais anonymisée.

### 3.3 Droit à l'Oubli et Portabilité (`server.py`)
- **Endpoint de Suppression** (`DELETE /api/user/delete`) :
  - Supprime le compte utilisateur et toutes les données associées (produits, campagnes, liens).
  - Anonymise les transactions financières pour respecter les obligations légales de conservation comptable tout en protégeant l'identité.
- **Endpoint d'Export** (`GET /api/user/export`) :
  - Génère un fichier JSON contenant l'intégralité des données personnelles détenues sur l'utilisateur (profil, historique, logs).

## 4. Interface Utilisateur (Frontend)

### 4.1 Paramètres de Confidentialité (`PersonalSettings.js`)
- **Nouvelle Section** : "Gestion des Données (RGPD)".
- **Fonctionnalités** :
  - **Bouton "Exporter mes données"** : Déclenche le téléchargement du fichier JSON via l'API.
  - **Bouton "Supprimer mon compte"** : Déclenche la procédure de suppression définitive avec une modale de confirmation de sécurité.

## 5. Conclusion
La plateforme ShareYourSales dispose désormais d'une architecture "Privacy by Design". Les données sensibles (IP) sont anonymisées à la source, et les utilisateurs disposent d'un contrôle total et autonome sur leurs données via leur tableau de bord, conformément aux exigences légales les plus strictes.
