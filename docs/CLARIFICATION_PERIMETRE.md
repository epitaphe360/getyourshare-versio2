# 🎯 CLARIFICATION PÉRIMÈTRE - GETYOURSHARE

**Date:** 7 Décembre 2025

---

## ⚠️ IMPORTANT: CE QUI N'EST PAS GÉRÉ PAR LA PLATEFORME

### 🚫 Hors Périmètre (Géré par le Marchand)

#### 1. Entrepôts (Warehouses)
- ❌ **NON géré par la plateforme**
- ✅ **Géré par le marchand** (son propre système)
- Le marchand maintient son stock dans son propre entrepôt
- La plateforme ne gère PAS de multi-warehouse

#### 2. Expéditions (Shipments)
- ❌ **NON géré par la plateforme**
- ✅ **Géré par le marchand** (son propre transporteur)
- Le marchand choisit et gère son transporteur
- Le marchand génère ses propres étiquettes d'expédition
- La plateforme ne gère PAS de tracking d'expédition

#### 3. Coupons Avancés
- ❌ **NON géré par la plateforme** (coupons conditionnels complexes)
- ✅ **Géré par le marchand** (dans son propre système e-commerce)
- Le marchand peut créer ses propres codes promo
- Les coupons complexes (conditions multiples, règles avancées) restent chez le marchand

---

## ✅ CE QUI EST GÉRÉ PAR LA PLATEFORME

### 📦 Périmètre GetYourShare

#### 1. Produits & Services
- ✅ Catalogue produits
- ✅ Prix et descriptions
- ✅ Catégories
- ✅ Stock simple (disponible/rupture)
- ✅ Variantes basiques (taille, couleur)

#### 2. Affiliation & Tracking
- ✅ Liens d'affiliation uniques
- ✅ Tracking des clics
- ✅ Tracking des conversions
- ✅ Attribution des commissions

#### 3. Commissions & Paiements
- ✅ Calcul des commissions (influenceur, commercial, parrain)
- ✅ Distribution automatique des gains
- ✅ Gestion des retraits (payouts)
- ✅ KYC et vérifications

#### 4. Marketplace & Deals
- ✅ Marketplace style Groupon
- ✅ Deals avec countdown
- ✅ Flash sales
- ✅ Seuils d'activation

#### 5. MLM & Parrainage
- ✅ Système de parrainage multi-niveaux
- ✅ Commissions cascades (3+ niveaux)
- ✅ Arbres de parrainage

#### 6. Services & Leads
- ✅ Services avec recharges
- ✅ Pipeline leads complet
- ✅ Formulaires publics
- ✅ Assignment commerciaux

#### 7. Fiscal & Conformité
- ✅ Calcul TVA multi-pays (MA/FR/US)
- ✅ Génération factures PDF conformes
- ✅ Envoi email automatique
- ✅ Déclarations trimestrielles

#### 8. Analytics & Stats
- ✅ Dashboard par rôle
- ✅ Statistiques conversions
- ✅ Performance influenceurs
- ✅ Rapports financiers

#### 9. GDPR & Sécurité
- ✅ Export données personnelles
- ✅ Suppression compte
- ✅ Rate limiting API
- ✅ Fraud detection

---

## 📊 IMPACT SUR LA ROADMAP

### ❌ À RETIRER DES TESTS

#### Bloc 6 Original (E-commerce Avancé) - MODIFIÉ
- ~~Phase 61: Multi-Warehouse Inventory~~ → **RETIRÉ**
- ~~Phase 62: Shipping & Tracking~~ → **RETIRÉ**
- ~~Phase 63: Advanced Coupons~~ → **RETIRÉ**
- ~~Phase 64: Wishlist Notifications~~ → **GARDÉ** (simple)
- ~~Phase 65: Events Calendar~~ → **GARDÉ** (simple)

### ✅ NOUVEAU BLOC 6 (Features Produits)

#### Phase 61: Invoices Generation
- Génération factures automatiques
- Numérotation conforme
- PDF avec TVA selon pays

#### Phase 62: Invoices Email Distribution
- Envoi facture au client
- Copie au marchand
- Template professionnel

#### Phase 63: Product Variants Management
- Gestion variantes (taille, couleur)
- Prix par variante
- Stock par variante

#### Phase 64: Product Reviews & Ratings
- Avis clients après achat
- Notes 1-5 étoiles
- Modération admin

#### Phase 65: Advanced Product Analytics
- Taux conversion par produit
- Panier moyen
- Performance par influenceur

---

## 🎯 CLARIFICATIONS FONCTIONNELLES

### Workflow Commande Typique

```
1. CLIENT visite lien affiliation influenceur
   └─> Tracking: platform ✅

2. CLIENT achète produit sur site marchand
   └─> Conversion: platform ✅
   └─> Commissions: platform ✅
   └─> Facture: platform ✅

3. MARCHAND reçoit notification commande
   └─> Prépare colis: marchand 🏪
   └─> Choisit transporteur: marchand 🏪
   └─> Crée étiquette: marchand 🏪
   └─> Expédie: marchand 🏪

4. CLIENT reçoit tracking transporteur
   └─> Tracking transporteur: marchand 🏪
   └─> PAS géré par platform ❌

5. CLIENT reçoit colis
   └─> Livraison: transporteur marchand 🏪
```

### Points Clés
- **Platform = Affiliation + Commissions + Factures**
- **Marchand = Stock + Expédition + Tracking physique**
- **Séparation claire des responsabilités**

---

## 📈 MÉTRIQUES MISES À JOUR

### Couverture Tests Ajustée

#### Avant Clarification
```
Phases: 75 (36-75 à implémenter)
Bloc 6: Multi-warehouse, Shipping, Coupons avancés
Couverture cible: 95%
```

#### Après Clarification
```
Phases: 75 (36-75 à implémenter)
Bloc 6: Invoices, Variants, Reviews, Analytics
Couverture cible: 95% (du périmètre plateforme)
Couverture hors-scope: 0% (volontairement)
```

### Endpoints Retirés
- ~~POST /api/warehouses/create~~
- ~~PUT /api/warehouses/{id}/stock~~
- ~~POST /api/shipments/create~~
- ~~GET /api/shipments/{id}/track~~
- ~~POST /api/coupons/advanced~~

### Endpoints Ajoutés
- ✅ GET /api/invoices/generate
- ✅ POST /api/invoices/send
- ✅ GET /api/products/{id}/variants
- ✅ POST /api/products/{id}/reviews
- ✅ GET /api/analytics/products/advanced

---

## 🔄 INTÉGRATIONS POSSIBLES

### Avec Systèmes Marchands

Si le marchand utilise:
- **Shopify/WooCommerce**: Intégration via API (commissions)
- **Stock propre**: Webhook notification vente
- **Transporteur (DHL/Colissimo)**: Géré par marchand
- **Système facturation**: Platform génère factures pour plateforme

### Ce que Platform Fournit au Marchand
1. ✅ Notification vente (webhook)
2. ✅ Infos client (nom, adresse)
3. ✅ Facture plateforme (commission déduite)
4. ✅ Tracking affiliation (quel influenceur)

### Ce que Marchand Gère
1. 🏪 Stock dans son entrepôt
2. 🏪 Préparation colis
3. 🏪 Choix transporteur
4. 🏪 Étiquette expédition
5. 🏪 Tracking livraison
6. 🏪 SAV/Retours

---

## 📝 RECOMMANDATIONS

### Pour la Documentation
- ✅ Mettre à jour tous les documents avec cette clarification
- ✅ Ajouter note "Hors périmètre" sur sections concernées
- ✅ Remplacer phases warehouse/shipping par invoices/variants

### Pour les Tests
- ✅ Retirer tests warehouse/shipping/coupons avancés
- ✅ Ajouter tests invoices/variants/reviews
- ✅ Maintenir 75 phases totales
- ✅ Garder objectif 95% couverture (du périmètre)

### Pour le Code
- ✅ Tables `warehouses`, `shipments`, `coupons` → INFO uniquement
- ✅ Tables existent mais features optionnelles
- ✅ Pas d'erreur si tables vides
- ✅ Focus sur features core platform

---

## ✅ CONCLUSION

### Périmètre Clarifié
- **Platform = Affiliation + Commissions + Factures + Analytics**
- **Marchand = Stock + Expédition + Logistique physique**

### Impact Roadmap
- Bloc 6 redéfini avec features pertinentes
- 75 phases maintenues
- 95% couverture du périmètre platform
- Documentation mise à jour

### Prochaines Étapes
1. Mettre à jour PLAN_ENRICHISSEMENT_TEST.md
2. Mettre à jour ANALYSE_ULTRA_COMPLETE_FONCTIONNALITES.md
3. Mettre à jour tous documents de livraison
4. Commiter changements

---

**Date:** 7 Décembre 2025  
**Status:** ✅ CLARIFICATION VALIDÉE  
**Impact:** Bloc 6 redéfini, périmètre clarifié

---

*Clarification périmètre - GetYourShare Platform*
