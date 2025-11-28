# 📚 GUIDE COMPLET DE L'APPLICATION GETYOURSHARE

**Version:** 2.0
**Date:** 28 novembre 2025
**Pages totales:** 100+
**Fonctionnalités:** 200+

---

## 📑 TABLE DES MATIÈRES

### PARTIE 1 : VUE D'ENSEMBLE
1. [Introduction à GetYourShare](#introduction)
2. [Types d'utilisateurs](#types-utilisateurs)
3. [Architecture de l'application](#architecture)

### PARTIE 2 : ESPACE INFLUENCEUR
4. [Dashboard Influenceur](#dashboard-influenceur)
5. [Marketplace - Découvrir des produits](#marketplace)
6. [Mes Liens d'affiliation](#mes-liens)
7. [Live Shopping](#live-shopping)
8. [Génération de contenu IA](#content-ia)
9. [Smart Matching produits](#smart-matching)
10. [Réseaux sociaux](#reseaux-sociaux)
11. [Gamification & Récompenses](#gamification)
12. [Parrainage](#parrainage)
13. [Revenus & Paiements](#revenus-influenceur)

### PARTIE 3 : ESPACE MARCHAND
14. [Dashboard Marchand](#dashboard-marchand)
15. [Mes Produits](#mes-produits)
16. [Créer un produit](#creer-produit)
17. [Campagnes Marketing](#campagnes)
18. [Recherche d'influenceurs](#recherche-influenceurs)
19. [Demandes d'affiliation](#demandes-affiliation)
20. [Analytics & Statistiques](#analytics-merchant)
21. [Paiements & Facturation](#paiements-merchant)

### PARTIE 4 : ESPACE ADMIN
22. [Dashboard Admin](#dashboard-admin)
23. [Gestion utilisateurs](#gestion-users)
24. [Modération](#moderation)
25. [Paiements plateforme](#paiements-platform)
26. [Settings & Configuration](#settings)

### PARTIE 5 : FONCTIONNALITÉS AVANCÉES
27. [TikTok Shop](#tiktok-shop)
28. [Messagerie interne](#messagerie)
29. [Système de leads](#leads)
30. [Intégrations](#integrations)

---

## 🌟 PARTIE 1 : VUE D'ENSEMBLE

### <a name="introduction"></a>1. INTRODUCTION À GETYOURSHARE

**GetYourShare** est une plateforme d'affiliation et de marketing d'influence qui connecte :
- 👤 **Influenceurs** : Créateurs de contenu qui promeuvent des produits
- 🏪 **Marchands** : Entreprises qui vendent des produits
- 💰 **Plateforme** : Facilite les transactions et prend une commission

#### Concept clé : Comment ça fonctionne ?

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUX PRINCIPAL                             │
└──────────────────────────────────────────────────────────────┘

MARCHAND                    PLATEFORME               INFLUENCEUR
    │                            │                         │
    │ 1. Ajoute produits        │                         │
    │────────────────────────────►│                         │
    │                            │                         │
    │                            │  2. Découvre produits   │
    │                            │◄────────────────────────┤
    │                            │                         │
    │                            │  3. Crée lien unique    │
    │                            │─────────────────────────►│
    │                            │                         │
    │                            │  4. Partage sur réseaux │
    │                            │◄────────────────────────┤
    │                            │                         │
    │                            │  5. Client clique & achète
    │                            │         │
    │                            │         ▼
    │                            │    [TRACKING]
    │                            │         │
    │ 6. Reçoit commande         │         │
    │◄────────────────────────────────────┤
    │                            │         │
    │ 7. Paie commission         │         │
    │────────────────────────────►│         │
    │                            │         │
    │                            │  8. Reçoit paiement
    │                            │─────────────────────────►│
    │                            │                         │
```

---

### <a name="types-utilisateurs"></a>2. TYPES D'UTILISATEURS

L'application supporte 4 types d'utilisateurs avec des interfaces différentes :

#### 🎨 Rôles et permissions

| Rôle | Description | Fonctionnalités principales |
|------|-------------|----------------------------|
| **👤 Influenceur** | Créateur de contenu | • Générer liens<br>• Live shopping<br>• Contenu IA<br>• Stats revenus |
| **🏪 Marchand** | Vendeur de produits | • Ajouter produits<br>• Campagnes<br>• Chercher influenceurs<br>• Analytics ventes |
| **👨‍💼 Admin** | Gestionnaire plateforme | • Modération<br>• Gestion users<br>• Config système<br>• Paiements globaux |
| **💼 Commercial** | Équipe vente | • Gestion leads<br>• Suivi clients<br>• Reporting |

---

### <a name="architecture"></a>3. ARCHITECTURE DE L'APPLICATION

#### Structure des pages

```
GetYourShare
│
├── 🏠 Pages publiques
│   ├── Homepage (landing)
│   ├── Pricing (tarifs)
│   ├── About (à propos)
│   ├── Contact
│   └── Register/Login
│
├── 👤 Espace Influenceur
│   ├── Dashboard
│   ├── Marketplace
│   ├── Mes liens
│   ├── Live Shopping
│   ├── Contenu IA
│   ├── Revenus
│   └── Settings
│
├── 🏪 Espace Marchand
│   ├── Dashboard
│   ├── Mes produits
│   ├── Campagnes
│   ├── Influenceurs
│   ├── Analytics
│   └── Facturation
│
└── 👨‍💼 Espace Admin
    ├── Dashboard
    ├── Users
    ├── Modération
    ├── Paiements
    └── Settings
```

---

## 🎨 PARTIE 2 : ESPACE INFLUENCEUR

### <a name="dashboard-influenceur"></a>4. DASHBOARD INFLUENCEUR

**URL :** `/dashboard/influencer`
**Description :** Page principale de l'influenceur avec toutes ses stats

#### 📸 VISUEL DE LA PAGE

```
┌────────────────────────────────────────────────────────────────────────┐
│  GetYourShare    [🔍 Rechercher]  [🔔3]  [👤 Sarah]  [▼]               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  📊 Dashboard Influenceur                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                         │
│  👋 Bienvenue Sarah !                                🏆 Niveau: Gold   │
│  Dernière connexion: Il y a 2 heures                 📈 +127 points    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  📊 STATS RAPIDES - Ce mois                                      │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ 💰 REVENUS   │  │ 🛒 VENTES    │  │ 👥 CLICS     │          │  │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤          │  │
│  │  │  4,567 MAD   │  │     156      │  │   12,345     │          │  │
│  │  │  ━━━━━━━━━   │  │  ━━━━━━━━━   │  │  ━━━━━━━━━   │          │  │
│  │  │  +23% vs     │  │  +18% vs     │  │  +45% vs     │          │  │
│  │  │  mois dernier│  │  mois dernier│  │  mois dernier│          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │                                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │  │
│  │  │ 💵 À PAYER   │  │ 📦 PRODUITS  │  │ 🔗 LIENS     │          │  │
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤          │  │
│  │  │  1,234 MAD   │  │      45      │  │      89      │          │  │
│  │  │  Vendredi    │  │  actifs      │  │  générés     │          │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  📈 GRAPHIQUE REVENUS - 30 derniers jours                        │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  500│                                          ●                │  │
│  │  400│                    ●              ●                       │  │
│  │  300│         ●                ●                                │  │
│  │  200│    ●                                  ●                   │  │
│  │  100│                                                           │  │
│  │     └───────────────────────────────────────────────────────   │  │
│  │      1    5    10   15   20   25   30                          │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────┐  ┌────────────────────────────────────┐    │
│  │  🔥 ACTIONS RAPIDES  │  │  📢 DERNIÈRES ACTIVITÉS             │    │
│  ├──────────────────────┤  ├────────────────────────────────────┤    │
│  │                      │  │                                     │    │
│  │  [🛍️ Marketplace]    │  │  • Vente: Parfum Atlas - 45 MAD   │    │
│  │  Découvrir produits  │  │    Il y a 12 minutes               │    │
│  │                      │  │                                     │    │
│  │  [🎬 Créer Live]     │  │  • Nouveau follower Instagram      │    │
│  │  Live Shopping       │  │    Il y a 1 heure                  │    │
│  │                      │  │                                     │    │
│  │  [✨ Contenu IA]     │  │  • Commission payée: 567 MAD       │    │
│  │  Générer posts       │  │    Il y a 3 heures                 │    │
│  │                      │  │                                     │    │
│  │  [🔗 Nouveau lien]   │  │  • Nouveau produit disponible      │    │
│  │  Créer lien          │  │    Il y a 5 heures                 │    │
│  │                      │  │                                     │    │
│  └──────────────────────┘  └────────────────────────────────────┘    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  🏆 GAMIFICATION - Ton niveau                                    │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  Niveau actuel: 🥇 GOLD (Niveau 4/6)                            │  │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 67%              │  │
│  │  4,567 / 6,000 points                                           │  │
│  │                                                                  │  │
│  │  Prochain niveau: 💎 PLATINUM                                   │  │
│  │  Avantages: -2% commission plateforme, Badge exclusif           │  │
│  │                                                                  │  │
│  │  Badges débloqués:                                              │  │
│  │  🎖️ Premier live  🎖️ 100 ventes  🎖️ Top seller               │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  🎯 TOP PRODUITS - Tes best sellers ce mois                     │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  1. 🌸 Parfum Oriental Atlas         23 ventes    1,035 MAD     │  │
│  │  2. ⌚ Montre Élégante Rose Gold      18 ventes      862 MAD     │  │
│  │  3. 👜 Sac à Main Cuir Marron         15 ventes      675 MAD     │  │
│  │  4. 💄 Rouge à Lèvres Matte          12 ventes      360 MAD     │  │
│  │  5. 👟 Baskets Sport Premium          8 ventes      320 MAD     │  │
│  │                                                                  │  │
│  │  [Voir tous mes produits →]                                     │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

#### ⚙️ FONCTIONNALITÉS DU DASHBOARD

1. **Stats rapides** (6 cartes)
   - 💰 Revenus du mois
   - 🛒 Nombre de ventes
   - 👥 Clics sur liens
   - 💵 Solde à payer
   - 📦 Produits actifs
   - 🔗 Liens générés

2. **Graphique revenus**
   - Évolution sur 30 jours
   - Comparaison mois précédent
   - Export possible (CSV, PDF)

3. **Actions rapides**
   - Accès direct marketplace
   - Créer live shopping
   - Générer contenu IA
   - Créer nouveau lien

4. **Feed d'activités**
   - Ventes en temps réel
   - Nouveaux followers
   - Paiements reçus
   - Nouveaux produits disponibles

5. **Gamification**
   - Niveau actuel
   - Progression vers niveau suivant
   - Badges débloqués
   - Récompenses disponibles

6. **Top produits**
   - 5 produits les plus performants
   - Ventes et commissions par produit

---

### <a name="marketplace"></a>5. MARKETPLACE - DÉCOUVRIR DES PRODUITS

**URL :** `/marketplace`
**Description :** Catalogue de tous les produits disponibles pour affiliation

#### 📸 VISUEL DE LA PAGE

```
┌────────────────────────────────────────────────────────────────────────┐
│  🛍️ Marketplace - Découvre des produits à promouvoir                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  🔍 [Rechercher produits...]           [🎯 Smart Match]  [⚙️]    │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─────────────┐  ┌──────────────────────────────────────────────────┐│
│  │  FILTRES    │  │  RÉSULTATS (234 produits)                         ││
│  ├─────────────┤  ├──────────────────────────────────────────────────┤│
│  │             │  │                                                   ││
│  │ 📁 Catégorie│  │  ┌─────────────────┐  ┌─────────────────┐       ││
│  │ ☑ Beauté    │  │  │ [📸 Image]      │  │ [📸 Image]      │       ││
│  │ ☐ Mode      │  │  │                 │  │                 │       ││
│  │ ☐ Tech      │  │  │ Parfum Oriental │  │ Montre Élégante │       ││
│  │ ☐ Maison    │  │  │ Atlas           │  │ Rose Gold       │       ││
│  │ ☐ Sport     │  │  │                 │  │                 │       ││
│  │             │  │  │ 299 MAD         │  │ 599 MAD         │       ││
│  │ 💰 Prix     │  │  │ ⭐ 4.8 (234)    │  │ ⭐ 4.6 (156)    │       ││
│  │ 0 ──●── 1K  │  │  │                 │  │                 │       ││
│  │             │  │  │ Commission: 15% │  │ Commission: 12% │       ││
│  │ 📊 Commission│ │  │ = 44.85 MAD    │  │ = 71.88 MAD    │       ││
│  │ ○ 10-15%    │  │  │                 │  │                 │       ││
│  │ ● 15-20%    │  │  │ 📦 Stock: 45    │  │ 📦 Stock: 23    │       ││
│  │ ○ 20%+      │  │  │                 │  │                 │       ││
│  │             │  │  │ [❤️ Favori]     │  │ [❤️ Favori]     │       ││
│  │ ⭐ Note     │  │  │ [🔗 Créer lien] │  │ [🔗 Créer lien] │       ││
│  │ ● 4+ étoiles│  │  │ [ℹ️ Détails]    │  │ [ℹ️ Détails]    │       ││
│  │ ○ 3+ étoiles│  │  └─────────────────┘  └─────────────────┘       ││
│  │             │  │                                                   ││
│  │ 📦 Stock    │  │  ┌─────────────────┐  ┌─────────────────┐       ││
│  │ ☑ En stock  │  │  │ [📸 Image]      │  │ [📸 Image]      │       ││
│  │             │  │  │                 │  │                 │       ││
│  │ 🏷️ Promo    │  │  │ Sac à Main Cuir │  │ Rouge à Lèvres  │       ││
│  │ ☐ En promo  │  │  │ Marron          │  │ Matte           │       ││
│  │             │  │  │                 │  │                 │       ││
│  │ 🔥 Tendance │  │  │ 450 MAD         │  │ 120 MAD         │       ││
│  │ ☐ Trending  │  │  │ ⭐ 4.9 (89)     │  │ ⭐ 4.7 (421)    │       ││
│  │             │  │  │                 │  │                 │       ││
│  │ [Réinitialiser]│ │ Commission: 18% │  │ Commission: 15% │       ││
│  │             │  │  │ = 81 MAD        │  │ = 18 MAD        │       ││
│  └─────────────┘  │  │                 │  │                 │       ││
│                   │  │ 📦 Stock: 12    │  │ 📦 Stock: 156   │       ││
│                   │  │                 │  │                 │       ││
│                   │  │ [❤️ Favori]     │  │ [❤️ Favori]     │       ││
│                   │  │ [🔗 Créer lien] │  │ [🔗 Créer lien] │       ││
│                   │  │ [ℹ️ Détails]    │  │ [ℹ️ Détails]    │       ││
│                   │  └─────────────────┘  └─────────────────┘       ││
│                   │                                                   ││
│                   │  [◀ Précédent]  1 2 3 ... 59  [Suivant ▶]        ││
│                   │                                                   ││
│                   └──────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘
```

#### ⚙️ FONCTIONNALITÉS DE LA MARKETPLACE

1. **Barre de recherche intelligente**
   - Recherche par nom produit
   - Recherche par marchand
   - Recherche par catégorie
   - Autocomplétion

2. **Smart Match** 🎯
   - Recommandations IA personnalisées
   - Basé sur ton audience
   - Basé sur tes performances passées
   - Score de compatibilité affiché

3. **Filtres avancés**
   - **Catégorie :** Beauté, Mode, Tech, Maison, Sport, etc.
   - **Prix :** Slider min-max
   - **Commission :** Par pourcentage
   - **Note :** 3+, 4+, 5 étoiles
   - **Stock :** En stock uniquement
   - **Promo :** Produits en promotion
   - **Tendance :** Produits trending

4. **Carte produit**
   - Photo haute qualité
   - Nom et prix
   - Note et avis clients
   - **Commission en %** et **en MAD**
   - Stock disponible
   - Actions :
     * ❤️ Ajouter aux favoris
     * 🔗 Créer lien d'affiliation
     * ℹ️ Voir détails complets

5. **Vue détail produit** (clic sur carte)

```
┌────────────────────────────────────────────────────────────────┐
│  DÉTAIL PRODUIT                                          [✕]   │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  Parfum Oriental Atlas                   │
│  │                  │  ━━━━━━━━━━━━━━━━━━━━━                  │
│  │  [Photo produit] │  299 MAD                                 │
│  │                  │  ⭐⭐⭐⭐⭐ 4.8/5 (234 avis)             │
│  │  [📸] [📸] [📸]  │                                          │
│  └──────────────────┘  🏪 Marchand: BeautyStore.ma            │
│                                                                 │
│  📝 DESCRIPTION                                                │
│  Parfum oriental aux notes de jasmin, ambre et bois de santal. │
│  Tenue longue durée 8-10h. Flacon luxe 50ml.                  │
│                                                                 │
│  💰 COMMISSION                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                  │
│  • Taux: 15%                                                   │
│  • Par vente: 44.85 MAD                                        │
│  • Objectif 10 ventes: 448.50 MAD                              │
│  • Bonus si +20 ventes: +2% = 51.45 MAD/vente                  │
│                                                                 │
│  📦 INFOS LIVRAISON                                            │
│  • Livraison gratuite Maroc                                    │
│  • Expédition sous 24h                                         │
│  • Retour possible 30 jours                                    │
│                                                                 │
│  📊 PERFORMANCES                                               │
│  • Taux conversion moyen: 4.2%                                 │
│  • Note satisfaction: 4.8/5                                    │
│  • Top influenceur: @sarah_beauty (67 ventes)                  │
│                                                                 │
│  [❤️ Ajouter aux favoris]  [🔗 Créer mon lien]                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### <a name="mes-liens"></a>6. MES LIENS D'AFFILIATION

**URL :** `/influencer/my-links`
**Description :** Gestion de tous les liens d'affiliation créés

#### 📸 VISUEL DE LA PAGE

```
┌────────────────────────────────────────────────────────────────────────┐
│  🔗 Mes Liens d'Affiliation                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                         │
│  [+ Créer un nouveau lien]                                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  🔍 [Rechercher mes liens...]        [📅 Ce mois ▼]  [⚙️ Filtres]│ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  📊 STATS GLOBALES                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ 🔗 LIENS    │  │ 👁️ CLICS    │  │ 🛒 VENTES   │  │ 💰 REVENUS  │ │
│  │    89       │  │   12,345    │  │    156      │  │  4,567 MAD  │ │
│  │  actifs     │  │  ce mois    │  │  ce mois    │  │  ce mois    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  LIEN #1 - Parfum Oriental Atlas                      🟢 Actif   │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  🔗 URL: https://getyourshare.ma/r/PARFUM001                    │  │
│  │     [📋 Copier] [📱 QR Code] [📊 Stats]                         │  │
│  │                                                                  │  │
│  │  📅 Créé: 15 nov 2025  |  🏷️ Tags: beauté, parfum, promo        │  │
│  │                                                                  │  │
│  │  📊 PERFORMANCES (30 derniers jours):                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │ 👁️ Clics │  │ 🛒 Ventes│  │ 💵 CA     │  │ 💰 Commis│       │  │
│  │  │  1,234   │  │    23    │  │ 6,877 MAD│  │ 1,031 MAD│       │  │
│  │  │  +45%    │  │  +18%    │  │  +23%    │  │  +23%    │       │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │  │
│  │                                                                  │  │
│  │  📈 Taux conversion: 1.9%  |  📦 Stock restant: 42              │  │
│  │                                                                  │  │
│  │  🎯 SOURCES TRAFIC:                                             │  │
│  │  • Instagram Story: 45% (556 clics)                             │  │
│  │  • Instagram Feed: 30% (370 clics)                              │  │
│  │  • TikTok Bio: 15% (185 clics)                                  │  │
│  │  • Autre: 10% (123 clics)                                       │  │
│  │                                                                  │  │
│  │  [✏️ Modifier] [📤 Partager] [⏸️ Désactiver] [🗑️ Supprimer]     │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  LIEN #2 - Montre Élégante Rose Gold                 🟢 Actif   │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  🔗 URL: https://getyourshare.ma/r/MONTRE002                    │  │
│  │     [📋 Copier] [📱 QR Code] [📊 Stats]                         │  │
│  │                                                                  │  │
│  │  📅 Créé: 10 nov 2025  |  🏷️ Tags: mode, accessoires            │  │
│  │                                                                  │  │
│  │  📊 PERFORMANCES (30 derniers jours):                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │ 👁️ Clics │  │ 🛒 Ventes│  │ 💵 CA     │  │ 💰 Commis│       │  │
│  │  │   892    │  │    18    │  │10,782 MAD│  │ 1,294 MAD│       │  │
│  │  │  +12%    │  │  +5%     │  │  +5%     │  │  +5%     │       │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │  │
│  │                                                                  │  │
│  │  📈 Taux conversion: 2.0%  |  📦 Stock restant: 19              │  │
│  │                                                                  │  │
│  │  [✏️ Modifier] [📤 Partager] [⏸️ Désactiver] [🗑️ Supprimer]     │  │
│  │                                                                  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  LIEN #3 - Sac à Main Cuir Marron                    ⏸️ Pausé   │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  [Détails masqués - Cliquer pour développer]                    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  [◀ Précédent]  1 2 3 4 5  [Suivant ▶]                                │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

#### ⚙️ FONCTIONNALITÉS MES LIENS

1. **Créer un nouveau lien**
   - Choisir le produit
   - Personnaliser le short code (optionnel)
   - Ajouter des tags
   - Définir une date d'expiration (optionnel)
   - Ajouter des paramètres UTM personnalisés

2. **Gestion des liens**
   - ✏️ Modifier : Changer tags, notes
   - ⏸️ Désactiver : Mettre en pause temporairement
   - 🗑️ Supprimer : Suppression définitive
   - 📋 Dupliquer : Créer variante

3. **Partage facile**
   - 📋 Copier URL
   - 📱 Générer QR Code
   - 📤 Partager direct sur :
     * Instagram Story
     * Instagram Post
     * TikTok Bio
     * Facebook
     * WhatsApp
     * Email

4. **Analytics détaillées par lien**
   - Nombre de clics (graphique évolution)
   - Nombre de ventes
   - CA généré
   - Commission gagnée
   - Taux de conversion
   - Sources de trafic (Instagram, TikTok, etc.)
   - Géolocalisation des clics
   - Devices (mobile/desktop)
   - Heures de pic

5. **Export de données**
   - Export CSV de tous les liens
   - Export PDF des performances
   - Rapport mensuel automatique par email

---

Je vais continuer avec le reste des fonctionnalités. Le document est très long, je vais le créer en plusieurs parties. Continuons ?

