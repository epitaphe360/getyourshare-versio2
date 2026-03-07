# 📊 SCHÉMA VISUEL : FLUX LIVE SHOPPING

## 🔄 VUE D'ENSEMBLE COMPLÈTE

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW LIVE SHOPPING                            │
└─────────────────────────────────────────────────────────────────────┘

        INFLUENCEUR              SYSTÈME              CLIENT
            │                       │                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 1. Choisit     │             │                    │
    │ 3 produits     │             │                    │
    │ dans market    │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
            │ Clique "Créer Live"   │                    │
            ├──────────────────────►│                    │
            │                       │                    │
            │                   ┌───▼─────────────┐      │
            │                   │ 2. Génère:      │      │
            │                   │ • Stream URL    │      │
            │                   │ • Stream Key    │      │
            │                   │ • 3 liens uniques│     │
            │                   │ • Codes promos  │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │ Reçoit infos streaming│                    │
            │◄──────────────────────┤                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 3. Configure   │             │                    │
    │ OBS avec       │             │                    │
    │ URL + Key      │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 4. Annonce     │             │                    │
    │ live sur       │─────────────┼───────────────────►│
    │ TikTok/Insta   │  Post 24h   │                    │
    └────────────────┘   avant     │                    │
            │                       │                    │
            │                       │                    │
    ════════════ JOUR J - HEURE H ═════════════════════════
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 5. Lance OBS   │             │                    │
    │ "Start Stream" │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
            │ Clique "Démarrer Live"│                    │
            ├──────────────────────►│                    │
            │                       │                    │
            │                   ┌───▼─────────────┐      │
            │                   │ Status: 🔴 LIVE │      │
            │                   │ Boost +5% ON    │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │    Dashboard temps réel│                   │
            │◄──────────────────────┤                    │
            │    • 247 viewers      │                    │
            │    • 5 ventes         │                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 6. Présente    │             │                    │
    │ produit 1:     │             │                    │
    │ "Parfum 299 MAD│             │                    │
    │ Code LIVE20!"  │─────────────┼───────────────────►│
    │                │   Stream     │                    │
    │ [Affiche QR]   │   TikTok     │                    │
    └────────────────┘             │            ┌───────▼────────┐
            │                       │            │ 7. Client      │
            │                       │            │ regarde live   │
            │                       │            │ sur TikTok     │
            │                       │            └───────┬────────┘
            │                       │                    │
            │                       │            ┌───────▼────────┐
            │                       │            │ 8. Clique      │
            │                       │            │ "Lien en bio"  │
            │                       │            └───────┬────────┘
            │                       │                    │
            │                       │            ┌───────▼────────┐
            │                       │            │ Redirigé vers: │
            │                       │            │ getyourshare   │
            │                       │            │ .ma/r/PARFUM001│
            │                       │            └───────┬────────┘
            │                       │                    │
            │                       │ Tracking cookie    │
            │                       │◄───────────────────┤
            │                   ┌───▼─────────────┐      │
            │                   │ 9. Crée cookie: │      │
            │                   │ {                │      │
            │                   │  code: PARFUM001│      │
            │                   │  influencer_id  │      │
            │                   │  live_session_id│      │
            │                   │  expires: 30j   │      │
            │                   │ }                │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │                       │  Page produit      │
            │                       │  + Promo -20%      │
            │                       ├───────────────────►│
            │                       │                    │
            │                       │            ┌───────▼────────┐
            │                       │            │ 10. Client     │
            │                       │            │ achète         │
            │                       │            │ 239 MAD        │
            │                       │            └───────┬────────┘
            │                       │                    │
            │                       │  Commande + Cookie │
            │                       │◄───────────────────┤
            │                   ┌───▼─────────────┐      │
            │                   │ 11. Enregistre: │      │
            │                   │ • Vente 239 MAD │      │
            │                   │ • Influencer ID │      │
            │                   │ • Live ID       │      │
            │                   │ • Commission:   │      │
            │                   │   47.80 MAD     │      │
            │                   │   (20% = 15%+5%)│      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │  Notif: "+1 vente!"  │                    │
            │◄──────────────────────┤                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 12. Voit sur   │             │                    │
    │ dashboard:     │             │                    │
    │ "6 ventes      │             │                    │
    │  1,986 MAD"    │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 13. Continue   │             │                    │
    │ avec produit 2,│             │                    │
    │ puis 3...      │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
            │ ... 45 minutes ...    │                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 14. Termine    │             │                    │
    │ "Merci tout    │             │                    │
    │  le monde!"    │             │                    │
    └───────┬────────┘             │                    │
            │                       │                    │
            │ Clique "Terminer Live"│                    │
            ├──────────────────────►│                    │
            │                       │                    │
            │                   ┌───▼─────────────┐      │
            │                   │ 15. Génère      │      │
            │                   │ rapport final:  │      │
            │                   │ • 23 ventes     │      │
            │                   │ • 8,947 MAD     │      │
            │                   │ • Commission:   │      │
            │                   │   1,789.40 MAD  │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │  Rapport complet      │                    │
            │◄──────────────────────┤                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 16. Consulte   │             │                    │
    │ rapport + stats│             │                    │
    │ détaillées     │             │                    │
    └────────────────┘             │                    │
            │                       │                    │
            │                       │                    │
    ════════════ 14 JOURS PLUS TARD ═══════════════════════
            │                       │                    │
            │                   ┌───▼─────────────┐      │
            │                   │ 17. Validation  │      │
            │                   │ automatique     │      │
            │                   │ des ventes      │      │
            │                   │ (délai retours) │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
    ════════════ VENDREDI SUIVANT ═════════════════════════
            │                       │                    │
            │                   ┌───▼─────────────┐      │
            │                   │ 18. Paiement    │      │
            │                   │ automatique     │      │
            │                   │ Virement:       │      │
            │                   │ 1,789.40 MAD    │      │
            │                   └───┬─────────────┘      │
            │                       │                    │
            │  Notif: "💰 Payé!"   │                    │
            │◄──────────────────────┤                    │
            │                       │                    │
    ┌───────▼────────┐             │                    │
    │ 19. Reçoit     │             │                    │
    │ argent sur     │             │                    │
    │ compte bancaire│             │                    │
    └────────────────┘             │                    │
            │                       │                    │
            │                       │                    │
```

---

## 🎯 LES 3 MOMENTS CLÉS

### ⏰ MOMENT 1 : AVANT LE LIVE (24-48h)

```
INFLUENCEUR                              FOLLOWERS
    │                                        │
    │ Crée live dans app                    │
    │ Reçoit liens produits                 │
    │                                        │
    │ Poste annonce sur TikTok ────────────►│ "Live demain 20h!"
    │ Met liens en bio          ────────────►│ Cliquent sur profil
    │                                        │ Sauvegardent les liens
    │                                        │ Mettent une alerte 🔔
```

### 🔴 MOMENT 2 : PENDANT LE LIVE (30-60min)

```
INFLUENCEUR              VIEWERS                 SYSTÈME
    │                       │                       │
    │ Présente produits    │                       │
    │───────────────────►  │                       │
    │                       │                       │
    │ "Lien en bio!"       │ Clique lien          │
    │                       │──────────────────────►│
    │                       │                       │
    │                       │ Achète               │ Track vente
    │                       │──────────────────────►│────┐
    │                       │                       │    │
    │ Voit "+1 vente"      │                       │    │
    │◄──────────────────────────────────────────────────┘
    │ en temps réel!       │                       │
```

### 💰 MOMENT 3 : APRÈS LE LIVE (14 jours + paiement)

```
JOUR J+14                          VENDREDI SUIVANT
    │                                   │
    │ Validation automatique            │
    │ des ventes                        │
    │                                   │
    │                                   ▼
    │                              Paiement auto
    │                              1,789.40 MAD
    │                                   │
    │                                   ▼
    │                              Influenceur
    │                              reçoit argent ✅
```

---

## 🔗 COMMENT LE TRACKING FONCTIONNE

### Méthode 1 : Cookie (Principal)

```
┌─────────────────────────────────────────────────────────┐
│                    COOKIE TRACKING                       │
└─────────────────────────────────────────────────────────┘

Client clique: getyourshare.ma/r/PARFUM001
            │
            ▼
    ┌───────────────────┐
    │ Cookie créé:      │
    │ ───────────────── │
    │ Code: PARFUM001   │
    │ Influencer: UUID  │
    │ Live ID: UUID     │
    │ Expire: 30 jours  │
    └───────┬───────────┘
            │
            ▼
    Client achète (maintenant ou dans 30j)
            │
            ▼
    ┌───────────────────┐
    │ Système vérifie:  │
    │ ───────────────── │
    │ ✅ Cookie existe  │
    │ ✅ Live actif?    │
    │ ✅ <2h après?     │
    │ ✅ Boost +5%?     │
    └───────┬───────────┘
            │
            ▼
    Vente attribuée ✅
    Commission calculée ✅
```

### Méthode 2 : Code Promo (Backup)

```
┌─────────────────────────────────────────────────────────┐
│                  CODE PROMO TRACKING                     │
└─────────────────────────────────────────────────────────┘

Influenceur dit: "Code LIVE20"
            │
            ▼
Client note le code
            │
            ▼
Client va sur site (sans lien)
            │
            ▼
Au checkout, entre: LIVE20
            │
            ▼
    ┌───────────────────┐
    │ Système check:    │
    │ ───────────────── │
    │ Code: LIVE20      │
    │   ↓               │
    │ Live ID: UUID     │
    │   ↓               │
    │ Influencer: UUID  │
    └───────┬───────────┘
            │
            ▼
    Attribution ✅
```

### Méthode 3 : Paramètres UTM (Fallback)

```
┌─────────────────────────────────────────────────────────┐
│                    UTM TRACKING                          │
└─────────────────────────────────────────────────────────┘

URL: getyourshare.ma/r/PARFUM001
     ?utm_source=PARFUM001
     &utm_medium=live_shopping
     &utm_campaign=tiktok_live_301125
            │
            ▼
    Système détecte paramètres
            │
            ▼
    PARFUM001 → Influencer UUID
            │
            ▼
    Attribution ✅
```

---

## 📊 CALCUL COMMISSION EN TEMPS RÉEL

```
┌─────────────────────────────────────────────────────────┐
│              CALCUL AUTOMATIQUE COMMISSION               │
└─────────────────────────────────────────────────────────┘

Vente: Parfum Oriental Atlas
Prix: 299 MAD
Promo live: -20% → 239 MAD

    ┌─────────────────────────┐
    │ Commission de base: 15% │
    │ 239 × 0.15 = 35.85 MAD  │
    └────────┬────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Boost live: +5%         │
    │ 239 × 0.05 = 11.95 MAD  │
    └────────┬────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ TOTAL INFLUENCEUR:      │
    │ 35.85 + 11.95           │
    │ = 47.80 MAD ✅          │
    └─────────────────────────┘

    Commission plateforme: 5%
    239 × 0.05 = 11.95 MAD

    Revenue marchand:
    239 - 47.80 - 11.95 = 179.25 MAD
```

---

## 🎬 EXEMPLE CONCRET : SESSION COMPLÈTE

```
┌─────────────────────────────────────────────────────────┐
│        EXEMPLE: LIVE TikTok de @beaute_maroc            │
└─────────────────────────────────────────────────────────┘

📅 Date: 30 nov 2025
⏰ Heure: 20:00 - 20:45 (45 min)
📱 Plateforme: TikTok
👤 Influenceur: Sarah (@beaute_maroc, 45K followers)

┌─────────────────────────────────────────────────────────┐
│ PRODUITS SÉLECTIONNÉS:                                   │
├─────────────────────────────────────────────────────────┤
│ 1. Parfum Oriental Atlas     299 MAD  Commission: 15%   │
│ 2. Montre Élégante           599 MAD  Commission: 12%   │
│ 3. Sac à Main Cuir           450 MAD  Commission: 18%   │
│                                                          │
│ Promo live: -20% (Code LIVE20)                          │
│ Bonus commission: +5%                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TIMELINE DU LIVE:                                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 20:00 ┃ Démarrage                                       │
│       ┃ - Sarah lance OBS                               │
│       ┃ - Clique "Démarrer" dans app                    │
│       ┃ - Status: 🔴 LIVE                               │
│       ┃ - 47 viewers connectés                          │
│                                                          │
│ 20:05 ┃ Présentation produit 1: Parfum                  │
│       ┃ - Montre le flacon                              │
│       ┃ - Fait sentir                                   │
│       ┃ - "299 MAD → 239 MAD avec LIVE20!"              │
│       ┃ - Affiche QR code                               │
│       ┃ - "Lien en bio!"                                │
│       ┃ → 156 viewers                                   │
│       ┃ → +3 ventes en 2 minutes! 🎉                    │
│                                                          │
│ 20:15 ┃ Présentation produit 2: Montre                  │
│       ┃ - Montre au poignet                             │
│       ┃ - Zoom sur détails                              │
│       ┃ - "599 MAD → 479 MAD!"                          │
│       ┃ - QR code + lien                                │
│       ┃ → 312 viewers (peak!)                           │
│       ┃ → +5 ventes! 🔥                                 │
│                                                          │
│ 20:30 ┃ Présentation produit 3: Sac                     │
│       ┃ - Montre intérieur                              │
│       ┃ - Met objets dedans                             │
│       ┃ - "450 MAD → 360 MAD!"                          │
│       ┃ → 287 viewers                                   │
│       ┃ → +4 ventes                                     │
│                                                          │
│ 20:40 ┃ Récap des 3 produits                            │
│       ┃ - Rappel codes promos                           │
│       ┃ - "Plus que 20 minutes pour profiter!"          │
│       ┃ → +8 ventes de dernière minute                  │
│                                                          │
│ 20:45 ┃ Fin du live                                     │
│       ┃ - "Merci à tous!"                               │
│       ┃ - Clique "Terminer"                             │
│       ┃ - Rapport généré                                │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ RÉSULTATS FINAUX:                                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 ENGAGEMENT:                                           │
│ • Total viewers: 1,847                                  │
│ • Peak viewers: 312                                     │
│ • Durée moyenne: 8 min                                  │
│ • Likes: 4,562                                          │
│ • Commentaires: 289                                     │
│ • Partages: 87                                          │
│ • Engagement rate: 18.5%                                │
│                                                          │
│ 💰 VENTES:                                               │
│ • Parfum: 8 ventes × 239 MAD = 1,912 MAD               │
│ • Montre: 9 ventes × 479 MAD = 4,311 MAD               │
│ • Sac: 6 ventes × 360 MAD = 2,160 MAD                  │
│ ─────────────────────────────────────                   │
│ • TOTAL: 23 ventes = 8,383 MAD                         │
│ • Panier moyen: 365 MAD                                 │
│ • Taux conversion: 1.25%                                │
│                                                          │
│ 💎 COMMISSION SARAH:                                     │
│ • Parfum: 8 × 47.80 MAD = 382.40 MAD                   │
│ • Montre: 9 × 95.80 MAD = 862.20 MAD                   │
│ • Sac: 6 × 90.00 MAD = 540.00 MAD                      │
│ ─────────────────────────────────────                   │
│ • TOTAL: 1,784.60 MAD 🎉                               │
│                                                          │
│ (Payé le vendredi 14 décembre)                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**RÉSUMÉ :**

✅ **L'influenceur** présente les produits en live
✅ **Les clients** achètent via les liens
✅ **Le système** track automatiquement tout
✅ **L'influenceur** est payé automatiquement

**AUCUNE intervention manuelle nécessaire ! 🚀**
