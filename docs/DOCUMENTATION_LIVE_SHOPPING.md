# 📺 DOCUMENTATION LIVE SHOPPING - ShareYourSales

## 🎯 QU'EST-CE QUE LE LIVE SHOPPING ?

Le **Live Shopping** est une fonctionnalité révolutionnaire de ShareYourSales qui permet de **vendre en direct** sur vos réseaux sociaux préférés avec **tracking automatique** et **commissions boostées**.

### 🌟 Plateformes supportées

ShareYourSales est LA SEULE plateforme au Maroc qui supporte les 4 principales plateformes de live:

- 📷 **Instagram Live** - Idéal pour lifestyle, beauté, mode
- 🎵 **TikTok Live** - Parfait pour audiences jeunes, produits tendance
- 🎬 **YouTube Live** - Meilleur pour tech reviews, tutoriels détaillés
- 👥 **Facebook Live** - Large audience, tous âges

---

## ✨ AVANTAGES DU LIVE SHOPPING

### Pour les Merchants (Entreprises):

✅ **Boost automatique +5% commission** pendant le live → Motivation max pour influencers
✅ **Tracking temps réel** de toutes les ventes générées pendant le live
✅ **Engagement X10** vs posts statiques
✅ **Taux de conversion 3-5x supérieur** grâce à l'interaction en direct
✅ **Attribution précise** - savoir exactement quelles ventes viennent du live
✅ **Stats détaillées** - viewers, likes, comments, shares, revenus

### Pour les Influenceurs:

✅ **+5% de commission supplémentaire** sur TOUTES les ventes pendant le live
✅ **Génération automatique de liens** de tracking pour chaque produit présenté
✅ **Dashboard temps réel** montrant vos gains pendant le live
✅ **Stats engagement** - viewers actuels, peak viewers, engagement rate
✅ **Multi-plateformes** - choisissez où votre audience est la plus active
✅ **Mode DEMO** pour tester sans vraies credentials API

---

## 🚀 COMMENT UTILISER LE LIVE SHOPPING

### 📋 PRÉ-REQUIS

#### Pour Merchants:

1. **Compte Merchant actif** sur ShareYourSales
2. **Produits ajoutés** dans votre catalogue (minimum 1 produit)
3. **Plan Pro ou Enterprise** recommandé (accès complet aux analytics live)

#### Pour Influenceurs:

1. **Compte Influencer actif** sur ShareYourSales
2. **Compte vérifié** sur au moins une plateforme (Instagram/TikTok/YouTube/Facebook)
3. **Liens de tracking** créés pour les produits à promouvoir
4. **Logiciel de streaming** (OBS Studio, Streamlabs, etc.) - GRATUIT

---

## 📱 ÉTAPE 1: CONNECTER VOS COMPTES SOCIAUX

### Instagram Live

1. **Aller dans Paramètres > Intégrations > Instagram**
2. Cliquer sur **"Connecter Instagram"**
3. Se connecter avec votre compte Instagram Business/Creator
4. **Autoriser les permissions**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`

**Important**: Vous DEVEZ avoir un compte **Instagram Business** ou **Creator** (pas compte personnel)

### TikTok Live

1. **Aller dans Paramètres > Intégrations > TikTok**
2. Cliquer sur **"Connecter TikTok"**
3. Autoriser l'application ShareYourSales
4. **Vérifier que vous avez accès à TikTok Live**:
   - 1000+ followers (requis par TikTok)
   - Compte en règle (pas de violations)

### YouTube Live

1. **Aller dans Paramètres > Intégrations > YouTube**
2. Cliquer sur **"Connecter YouTube"**
3. Se connecter avec votre compte Google
4. **Activer YouTube Live** (si pas déjà fait):
   - Aller sur YouTube Studio
   - Live > Activer (vérification téléphone nécessaire)
   - Attendre 24h pour activation

### Facebook Live

1. **Aller dans Paramètres > Intégrations > Facebook**
2. Cliquer sur **"Connecter Facebook"**
3. Sélectionner votre Page Facebook (pas profil personnel)
4. Autoriser les permissions de publication

---

## 🎬 ÉTAPE 2: CRÉER UNE SESSION LIVE

### Via l'interface ShareYourSales:

1. **Aller dans Features Hub > Live Shopping** (ou `/features?tab=live`)

2. **Cliquer sur "Nouveau Live"**

3. **Remplir le formulaire**:

   ```
   Titre: "Découverte Nouvelle Collection Été 2024 🔥"
   Description: "Live shopping exclusif avec -30% sur tous les produits présentés!"
   Plateforme: Instagram Live
   Date/Heure: 2025-12-15 20:00
   ```

4. **Sélectionner les produits** à présenter (minimum 1, maximum 20)

5. **Choisir la confidentialité**:
   - 🌍 **Public** - Tout le monde peut regarder
   - 🔗 **Unlisted** - Seulement avec le lien
   - 🔒 **Privé** - Invitations seulement

6. **Cliquer sur "Créer le Live"**

7. **Récupérer vos identifiants de streaming**:
   ```
   Stream URL: rtmps://live-upload.instagram.com/rtmp/...
   Stream Key: live_123456789_abcdefgh
   ```

**💡 IMPORTANT**: Notez bien ces identifiants, vous en aurez besoin pour OBS!

---

## 🎥 ÉTAPE 3: CONFIGURER VOTRE LOGICIEL DE STREAMING (OBS)

### Télécharger OBS Studio (gratuit):

- Site: https://obsproject.com/
- Compatible: Windows, Mac, Linux

### Configuration OBS:

1. **Ouvrir OBS Studio**

2. **Aller dans Paramètres > Stream**

3. **Configurer le streaming**:
   - Service: **Custom**
   - Serveur: Copier le **Stream URL** de ShareYourSales
   - Clé de stream: Copier le **Stream Key** de ShareYourSales

4. **Paramètres vidéo recommandés** (Paramètres > Sortie):
   - Encodeur: **x264**
   - Bitrate vidéo: **2500 Kbps** (Instagram/TikTok) ou **4500 Kbps** (YouTube)
   - Preset: **veryfast**
   - Résolution: **1920x1080** (Full HD) ou **1280x720** (HD)
   - FPS: **30**

5. **Ajouter vos sources**:
   - **Caméra** (Capture d'appareil vidéo)
   - **Overlay produits** (Images des produits à présenter)
   - **Prix et descriptions** (Texte)
   - **Logo ShareYourSales** (facultatif mais recommandé)

6. **Tester votre configuration**:
   - Cliquer sur **"Démarrer l'enregistrement"** (PAS "Démarrer le Stream" encore!)
   - Vérifier qualité audio/vidéo
   - Ajuster éclairage, cadrage, etc.

---

## 🔴 ÉTAPE 4: DÉMARRER LE LIVE

### 1. Dans ShareYourSales:

1. **Aller dans Features Hub > Live Shopping**
2. **Trouver votre session programmée**
3. **Cliquer sur "Préparer le Live"**
4. Vérifier que le statut passe à: ⚡ **"Ready"**

### 2. Dans OBS Studio:

1. **Cliquer sur "Démarrer le Stream"**
2. **Attendre 5-10 secondes** (connexion au serveur)
3. **Vérifier que le voyant est VERT** en bas d'OBS

### 3. Retour dans ShareYourSales:

1. **Cliquer sur "Démarrer le Live" 🔴**
2. Le live passe en statut: 🔴 **"LIVE"**
3. Le boost de commission **+5%** s'active automatiquement!

### 4. Sur votre plateforme (Instagram/TikTok/etc):

- Votre live apparaît instantanément
- Les viewers commencent à arriver
- Vous pouvez interagir avec les commentaires

---

## 💰 PENDANT LE LIVE: MAXIMISER LES VENTES

### 🎯 Bonnes pratiques:

#### Présentation des produits:

1. **Montrer le produit physiquement** (ou à l'écran si digital)
2. **Mentionner le prix** et la réduction pendant le live
3. **Expliquer les bénéfices** (pas juste les features)
4. **Créer l'urgence**: "Seulement pendant le live!", "Stock limité!"

#### Interaction:

1. **Répondre aux commentaires** en direct
2. **Appeler les viewers par leur nom**
3. **Faire des démos en direct**
4. **Répondre aux questions** sur les produits

#### Call-to-Action:

1. **Afficher le lien** dans la description du live
2. **Répéter le lien** verbalement: "Lien en bio!" ou "Lien dans la description!"
3. **Inciter à acheter MAINTENANT** pour profiter du boost
4. **Annoncer combien de personnes ont déjà acheté** (preuve sociale)

### 📊 Dashboard temps réel:

Pendant le live, vous pouvez voir en temps réel dans ShareYourSales:

- 👥 **Viewers actuels**: 234 personnes regardent
- 📈 **Peak viewers**: 567 (maximum atteint)
- ❤️ **Engagement**: 1,234 likes, 456 comments
- 🛒 **Clics sur produits**: 89 clics
- 💵 **Ventes en cours**: 12 ventes = 3,450 MAD
- 💰 **Vos commissions**: 345 MAD (avec boost +5%)

---

## ⏹️ ÉTAPE 5: TERMINER LE LIVE

### 1. Annoncer la fin:

```
"On va terminer dans 5 minutes!"
"Dernière chance pour profiter de -30%!"
"Merci à tous d'avoir été là!"
```

### 2. Récap final:

- **Remercier l'audience**
- **Rappeler les liens** une dernière fois
- **Annoncer le prochain live**
- **Donner un code promo** exclusif pour ceux qui ont regardé

### 3. Dans OBS:

- **Cliquer sur "Arrêter le Stream"**

### 4. Dans ShareYourSales:

1. **Cliquer sur "Terminer le Live" ⏹️**
2. Le live passe en statut: ✅ **"Completed"**
3. Le boost de commission s'arrête
4. Les stats finales sont calculées

---

## 📈 ÉTAPE 6: ANALYSER LES RÉSULTATS

### Stats post-live disponibles:

#### Métriques d'audience:

- 👥 **Total viewers unique**: 1,234 personnes
- ⏱️ **Durée moyenne de visionnage**: 8 min 32s
- 📈 **Peak simultané**: 567 viewers
- 🔥 **Taux de rétention**: 67%

#### Métriques d'engagement:

- ❤️ **Total likes**: 2,345
- 💬 **Total comments**: 567
- 🔄 **Total shares**: 89
- 📊 **Engagement rate**: 12.4%

#### Métriques de ventes:

- 🛒 **Clics sur produits**: 234
- 💵 **Conversions**: 34 ventes
- 🎯 **Taux de conversion**: 14.5% (vs 2-3% normal!)
- 💰 **Revenue total**: 12,450 MAD
- 💸 **Vos commissions**: 1,245 MAD (boost +5% inclus)

#### Produits best-sellers:

1. 🏆 **iPhone 15 Pro** - 8 ventes - 10,392 MAD
2. 🥈 **AirPods Pro** - 12 ventes - 3,348 MAD
3. 🥉 **Apple Watch** - 6 ventes - 2,394 MAD

---

## 🎁 FONCTIONNALITÉS AVANCÉES

### 1. Boost de commission automatique (+5%)

- **Actif uniquement pendant le live**
- S'applique sur TOUTES les ventes générées pendant
- Exemple: Commission normale 10% → **15% pendant live**
- Visible en temps réel dans votre dashboard

### 2. Attribution des ventes

Toute vente effectuée pendant ou dans les **24 heures après** le live est automatiquement attribuée au live si:
- Le client a cliqué sur votre lien pendant le live
- OU a regardé le live pendant au moins 30 secondes

### 3. Replay automatique

- Le live est automatiquement sauvegardé sur la plateforme
- Les liens de tracking restent actifs dans le replay
- Les ventes du replay sont aussi trackées (mais sans boost +5%)

### 4. Mode Co-Live (Coming Soon)

- Inviter un autre influencer en co-host
- Partager les commissions 50/50
- Doubler l'audience

### 5. Live Shopping Schedulé

- Programmer plusieurs lives à l'avance
- Notifications automatiques aux followers
- Countdown avant le début

---

## ❓ FAQ - QUESTIONS FRÉQUENTES

### Q1: Est-ce que je peux faire un live sans connexion API réelle ?

**R:** Oui! ShareYourSales a un **mode DEMO** qui simule un live sans vraies credentials. Idéal pour:
- Tester le système
- Former votre équipe
- Valider votre setup OBS

Pour activer le mode DEMO, ne connectez simplement pas vos comptes sociaux.

---

### Q2: Combien coûte le Live Shopping ?

**R:** Live Shopping est **INCLUS GRATUITEMENT** dans tous les plans:
- ✅ **Plan Free**: 2 lives/mois
- ✅ **Plan Pro**: 10 lives/mois
- ✅ **Plan Enterprise**: Lives illimités

---

### Q3: Quel matériel me faut-il ?

**Minimum**:
- 📱 Smartphone avec bonne caméra (iPhone 8+, Android récent)
- 🎤 Micro correct (casque avec micro OK)
- 💡 Éclairage correct (lumière du jour ou anneau lumineux 20€)
- 🌐 Connexion internet stable (4 Mbps upload minimum)

**Recommandé**:
- 💻 Ordinateur avec webcam HD
- 🎙️ Micro USB dédié (Blue Yeti ~100€)
- 💡 Anneau lumineux LED + trépied (~50€)
- 🌐 Fibre optique ou 4G/5G forte

---

### Q4: Quelle plateforme choisir ?

| Plateforme | Meilleur pour | Audience |
|------------|---------------|----------|
| 📷 **Instagram** | Beauté, Mode, Lifestyle | 18-35 ans, majoritairement femmes |
| 🎵 **TikTok** | Produits tendance, Fun | 16-30 ans, Gen Z |
| 🎬 **YouTube** | Tech, Tutoriels, Reviews | 25-45 ans, mixte |
| 👥 **Facebook** | Tous produits | 30-60 ans, large audience |

**💡 Conseil**: Testez chaque plateforme pour voir où votre audience engage le plus!

---

### Q5: Comment augmenter mes viewers ?

**Avant le live**:
- 📢 Annoncer 48h à l'avance sur tous vos réseaux
- 🎁 Teaser un cadeau/concours pendant le live
- ⏰ Poster des reminders 24h, 1h et 5min avant
- 📧 Envoyer un email à votre liste

**Pendant le live**:
- 🔥 Créer du contenu engageant (pas juste présenter produits)
- 🎭 Être énergique et dynamique
- 💬 Répondre aux commentaires en direct
- 🎁 Faire des jeux/concours pendant

**Après le live**:
- 📊 Partager les highlights
- 🎬 Poster des clips sur TikTok/Reels
- 💌 Remercier les participants
- 📅 Annoncer le prochain live

---

### Q6: Que faire si le live lag/coupe ?

**Problèmes courants**:

❌ **Live coupe régulièrement**
→ Réduire la qualité vidéo dans OBS (1280x720, 2000 Kbps)
→ Vérifier connexion internet (test sur fast.com)
→ Fermer autres applications qui consomment de la bande passante

❌ **Image pixelisée**
→ Augmenter le bitrate dans OBS (mais attention à la connexion!)
→ Améliorer l'éclairage (moins de bruit vidéo)

❌ **Audio désynchronisé**
→ Utiliser un micro USB direct (pas Bluetooth)
→ Réduire le nombre de sources dans OBS

---

### Q7: Est-ce que les ventes sont automatiquement détectées ?

**R:** OUI! 100% automatique:
1. **Pendant le live**: Dès qu'un viewer clique sur votre lien
2. **Tracking en temps réel**: La vente apparaît dans votre dashboard en <5 secondes
3. **Attribution automatique**: La vente est liée au live
4. **Boost +5% appliqué**: Commission majorée calculée automatiquement
5. **Paiement**: Commission versée comme d'habitude (hebdomadaire ou mensuel selon votre plan)

**Aucune action manuelle requise!**

---

### Q8: Puis-je faire des lives sur plusieurs plateformes EN MÊME TEMPS ?

**R:** Techniquement OUI avec un logiciel de "Multistreaming" (Restream.io, StreamYard), MAIS:

⚠️ **Attention**:
- Divise votre attention entre plusieurs chats
- Peut violer les TOS de certaines plateformes
- Complique l'attribution des ventes

**💡 Recommandation**: Faites un live par plateforme, mais programmez-les à différents jours/heures pour maximiser l'audience totale.

---

### Q9: Combien de temps devrait durer un live ?

**Durée recommandée par plateforme**:

- 📷 **Instagram**: 20-45 minutes (audience décroche après)
- 🎵 **TikTok**: 15-30 minutes (rythme rapide)
- 🎬 **YouTube**: 45-90 minutes (audience + patiente)
- 👥 **Facebook**: 30-60 minutes (large audience)

**💡 Règle d'or**: Mieux vaut un live court et dynamique qu'un live long et ennuyeux!

---

### Q10: Comment gérer les commentaires négatifs pendant le live ?

**Stratégies**:

1. **Ignorer les trolls** - Ne leur donnez pas d'attention
2. **Modérer si nécessaire** - Bloquer/masquer les commentaires violents
3. **Rester professionnel** - Répondre calmement aux critiques constructives
4. **Avoir un modérateur** - Quelqu'un qui gère le chat pendant que vous présentez
5. **Mode abonné seulement** (si disponible) - Limite les trolls

**💡 Important**: Les commentaires créent de l'engagement → L'algorithme pousse votre live!

---

## 🛠️ DÉPANNAGE

### Problème: "Erreur de connexion au serveur de streaming"

**Solutions**:
1. Vérifier que Stream URL et Stream Key sont corrects
2. Tester votre connexion internet (minimum 4 Mbps upload)
3. Désactiver VPN si activé
4. Vérifier que port 1935 (RTMP) n'est pas bloqué par firewall
5. Redémarrer OBS

---

### Problème: "Le live n'apparaît pas sur Instagram/TikTok"

**Solutions**:
1. Vérifier que vous avez cliqué sur "Démarrer le Live" dans ShareYourSales (pas juste OBS)
2. Attendre 10-15 secondes (délai de propagation)
3. Vérifier que votre compte n'a pas de restrictions
4. Essayer de se déconnecter/reconnecter du compte social
5. Vérifier les logs dans ShareYourSales

---

### Problème: "Les ventes ne sont pas trackées"

**Solutions**:
1. Vérifier que le live est bien en statut "LIVE" (pas "scheduled" ou "ready")
2. Vérifier que les liens de tracking sont bien créés pour les produits
3. Vérifier que les produits sont "actifs" dans votre catalogue
4. Attendre quelques secondes (tracking temps réel avec léger délai)
5. Contacter le support si le problème persiste

---

## 📞 SUPPORT

### Besoin d'aide ?

- 📧 **Email**: support@shareyoursales.com
- 💬 **Chat**: Depuis votre dashboard (coin inférieur droit)
- 📖 **Documentation**: https://docs.shareyoursales.com
- 🎥 **Tutoriels vidéo**: https://youtube.com/@shareyoursales

### Horaires support:

- 🕐 **Lun-Ven**: 9h-18h (GMT+1)
- 🕐 **Sam**: 10h-14h
- ❌ **Dim**: Fermé (support email seulement)

---

## 🎉 PRÊT À DÉMARRER ?

### Checklist finale:

- [ ] Compte social connecté (Instagram/TikTok/YouTube/Facebook)
- [ ] Produits ajoutés dans ShareYourSales
- [ ] Liens de tracking créés
- [ ] OBS Studio installé et configuré
- [ ] Session live créée dans ShareYourSales
- [ ] Setup testé (éclairage, audio, vidéo)
- [ ] Live annoncé sur vos réseaux
- [ ] Prêt à cartonner! 🚀

---

**🔴 LANCEZ VOTRE PREMIER LIVE MAINTENANT!**

Rendez-vous dans **Features Hub > Live Shopping** et cliquez sur **"Nouveau Live"**!

Bonne vente! 💰🎉

---

**Version**: 1.0
**Dernière mise à jour**: 2025-12-11
**Fichier**: `/DOCUMENTATION_LIVE_SHOPPING.md`
