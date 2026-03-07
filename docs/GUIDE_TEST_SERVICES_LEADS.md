# 🧪 Guide de Test - Système de Gestion des Services et Leads

## 🚀 Démarrage Rapide

### 1. Vérifier la base de données
Les migrations ont déjà été exécutées avec succès dans Supabase ✅

### 2. Démarrer le Backend
```powershell
cd backend
python server.py
```
Le serveur devrait démarrer sur `http://localhost:5000`

### 3. Démarrer le Frontend
```powershell
cd frontend
npm start
```
L'application devrait s'ouvrir sur `http://localhost:3000`

---

## ✅ Tests à Effectuer

### Test 1 : Accès Public - Liste des Services

**URL :** `http://localhost:3000/services`

**Ce que vous devriez voir :**
- Hero section avec titre "Découvrez nos services"
- Barre de recherche fonctionnelle
- Filtres par catégorie
- Grille de cartes de services (si des services existent)
- Message "Aucun service disponible" (si la base est vide)

**Actions à tester :**
1. Taper du texte dans la recherche → Les services se filtrent
2. Sélectionner une catégorie → Les services se filtrent
3. Cliquer sur une carte de service → Redirection vers le formulaire

**Statut attendu :** ✅ Page accessible sans connexion

---

### Test 2 : Accès Public - Demande de Service (Lead)

**URL :** `http://localhost:3000/services/[id-service]`

**Ce que vous devriez voir :**
- Sidebar à droite avec détails du service
- Formulaire à gauche avec champs : Nom, Email, Téléphone, Message
- Images du service
- Badge "Gratuit - Aucun engagement"
- Bouton "Envoyer ma demande"

**Actions à tester :**
1. Remplir tous les champs
2. Cliquer sur "Envoyer ma demande"
3. Vérifier la notification de succès
4. Vérifier que le lead apparaît dans l'admin

**Validations à vérifier :**
- Email invalide → Message d'erreur
- Champs vides → Impossible de soumettre
- Après soumission → Message de confirmation

**Statut attendu :** ✅ Page accessible sans connexion

---

### Test 3 : Accès Admin - Gestion des Services

**URL :** `http://localhost:3000/admin/services`

**Prérequis :** Être connecté avec un compte admin

**Ce que vous devriez voir :**
- 4 cartes de statistiques en haut
- Tableau des services avec colonnes : Nom, Catégorie, Marchand, Dépôt, Leads, Statut, Actions
- Bouton "Nouveau Service" en haut à droite
- Barre de recherche
- Filtres (Statut, Catégorie)

**Actions à tester :**

#### Créer un service
1. Cliquer sur "Nouveau Service"
2. Remplir le formulaire :
   - Nom : "Service Test"
   - Description : "Description du service test"
   - Catégorie : Sélectionner dans la liste
   - Dépôt initial : 1000
   - Prix par lead : 10
   - Commission : 20
   - Images : `https://via.placeholder.com/300`
3. Vérifier que "Leads possibles" affiche 100 (1000 ÷ 10)
4. Sauvegarder
5. Le service doit apparaître dans le tableau

#### Modifier un service
1. Cliquer sur l'icône crayon (Edit)
2. Modifier le nom ou le dépôt
3. Sauvegarder
4. Vérifier les changements dans le tableau

#### Voir les détails
1. Cliquer sur l'icône œil (View)
2. Voir les onglets : Leads / Recharges / Extras
3. Vérifier les statistiques affichées

#### Supprimer un service
1. Cliquer sur l'icône poubelle (Delete)
2. Confirmer la suppression
3. Le service disparaît du tableau

**Statut attendu :** ✅ Accessible uniquement aux admins

---

### Test 4 : Gestion des Leads (Admin)

**Depuis :** Modal "Détails du Service" → Onglet "Leads"

**Actions à tester :**

#### Voir les leads
1. Ouvrir les détails d'un service qui a des leads
2. Onglet "Leads"
3. Voir la liste des leads avec : Client, Contact, Coût, Statut, Date

#### Mettre à jour le statut
1. Sélectionner un lead avec statut "nouveau"
2. Changer le statut en dropdown : "en_cours"
3. Sauvegarder
4. Vérifier que le badge change de couleur
5. Vérifier que le taux de conversion se met à jour

#### Filtrer les leads
1. Utiliser le filtre de statut
2. Sélectionner "Convertis" → Voir uniquement les leads convertis
3. Sélectionner "Tous" → Voir tous les leads

**Statut attendu :** ✅ Leads affichés et modifiables

---

### Test 5 : Recharge du Dépôt

**Depuis :** Modal "Détails du Service" → Onglet "Recharges"

**Actions à tester :**

#### Recharger le dépôt
1. Noter le solde actuel
2. Cliquer sur "Recharger le dépôt"
3. Entrer montant : 500
4. Sauvegarder
5. Vérifier que :
   - Le nouveau solde = ancien solde + 500
   - Les leads possibles ont augmenté
   - L'historique des recharges affiche la nouvelle ligne

#### Vérifier l'historique
1. Voir la liste des recharges précédentes
2. Colonnes : Montant, Ancien solde, Nouveau solde, Leads ajoutés, Date

**Statut attendu :** ✅ Recharge fonctionnelle avec mise à jour automatique

---

### Test 6 : Déduction Automatique (Trigger)

**Test du flux complet :**

1. **Créer un service** avec :
   - Dépôt initial : 500
   - Prix par lead : 50
   - Leads possibles : 10

2. **Créer un lead depuis le public** :
   - Aller sur `/services`
   - Cliquer sur le service
   - Remplir et envoyer une demande

3. **Vérifier la déduction automatique** :
   - Retourner dans l'admin `/admin/services`
   - Ouvrir les détails du service
   - Vérifier que :
     - Dépôt actuel = 450 (500 - 50)
     - Leads possibles = 9 (10 - 1)
     - Leads reçus = 1
     - Le lead apparaît dans l'onglet "Leads"

**Statut attendu :** ✅ Déduction automatique fonctionne

---

### Test 7 : Calcul du Taux de Conversion

**Actions :**

1. Service avec 10 leads
2. Mettre à jour les statuts :
   - 5 leads → "converti"
   - 3 leads → "perdu"
   - 2 leads → "en_cours"

3. Vérifier que le taux de conversion = 50% (5 convertis / 10 total)

**Statut attendu :** ✅ Calcul automatique du taux

---

### Test 8 : Filtres et Recherche

**Dans la page admin :**

#### Test recherche
1. Taper un nom de service dans la barre de recherche
2. Le tableau se filtre en temps réel
3. Effacer la recherche → Tous les services réapparaissent

#### Test filtres
1. Filtre Statut : Sélectionner "Actif" → Voir uniquement les services actifs
2. Filtre Catégorie : Sélectionner une catégorie → Voir uniquement cette catégorie
3. Combiner les filtres → Voir l'intersection des résultats

**Statut attendu :** ✅ Filtres réactifs

---

### Test 9 : Validation des Formulaires

**Test erreurs :**

#### Formulaire de création de service (Admin)
1. Laisser des champs vides → Voir les messages d'erreur
2. Entrer un dépôt négatif → Voir l'erreur
3. Entrer un prix par lead de 0 → Voir l'erreur

#### Formulaire de demande de lead (Public)
1. Entrer un email invalide (ex: "test") → Voir l'erreur
2. Laisser le téléphone vide → Impossible de soumettre
3. Entrer des données valides → Soumission réussie

**Statut attendu :** ✅ Validations fonctionnelles

---

### Test 10 : Endpoints API

**Tester directement avec curl ou Postman :**

#### Endpoint public - Liste des services
```powershell
curl http://localhost:5000/api/public/services
```
**Réponse attendue :** JSON avec liste des services actifs

#### Endpoint public - Catégories
```powershell
curl http://localhost:5000/api/categories
```
**Réponse attendue :** JSON avec liste des catégories

#### Endpoint admin - Créer un service (avec token)
```powershell
curl -X POST http://localhost:5000/api/admin/services `
  -H "Authorization: Bearer YOUR_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    "nom": "Service API Test",
    "description": "Test depuis API",
    "categorie_id": "UUID_CATEGORIE",
    "marchand_id": "UUID_MARCHAND",
    "depot_initial": 1000,
    "prix_par_lead": 20,
    "statut": "actif"
  }'
```
**Réponse attendue :** JSON avec le service créé

---

## 🐛 Checklist de Débogage

Si quelque chose ne fonctionne pas, vérifier :

### Backend
- [ ] Le serveur est démarré (`python backend/server.py`)
- [ ] Pas d'erreurs dans la console backend
- [ ] Supabase est accessible (vérifier les credentials)
- [ ] Les tables existent dans Supabase
- [ ] Le router est bien inclus dans `server.py`

### Frontend
- [ ] Le serveur de dev est démarré (`npm start`)
- [ ] Pas d'erreurs dans la console navigateur (F12)
- [ ] Les routes sont bien définies dans `App.js`
- [ ] Les imports des composants sont corrects
- [ ] L'API URL est configurée (vérifier `utils/api.js`)

### Base de données
- [ ] Tables créées : `categories`, `services`, `leads`, `service_recharges`, `service_extras`
- [ ] Triggers activés : `deduct_lead_cost`, `update_conversion_rate`, etc.
- [ ] Des catégories existent dans la table `categories`
- [ ] Vérifier les contraintes et foreign keys

---

## 📊 Données de Test

### Créer des catégories (SQL)
```sql
INSERT INTO categories (id, name, description) VALUES
  (gen_random_uuid(), 'Marketing Digital', 'Services de marketing en ligne'),
  (gen_random_uuid(), 'Design Graphique', 'Création visuelle et branding'),
  (gen_random_uuid(), 'Développement Web', 'Sites web et applications'),
  (gen_random_uuid(), 'Consulting', 'Conseil et stratégie')
ON CONFLICT (name) DO NOTHING;
```

### Créer un service de test (SQL)
```sql
INSERT INTO services (
  id, nom, description, categorie_id, marchand_id,
  depot_initial, depot_actuel, prix_par_lead, statut
) VALUES (
  gen_random_uuid(),
  'Service Test Initial',
  'Description du service pour les tests',
  (SELECT id FROM categories LIMIT 1),
  (SELECT id FROM users WHERE role = 'merchant' LIMIT 1),
  1000, 1000, 25, 'actif'
);
```

---

## ✅ Critères de Succès

Le système est considéré comme fonctionnel si :

1. ✅ Les pages publiques sont accessibles sans connexion
2. ✅ Les pages admin sont protégées (redirection si non connecté)
3. ✅ Un client peut soumettre une demande de service (lead)
4. ✅ Le dépôt du marchand est déduit automatiquement
5. ✅ L'admin peut créer/modifier/supprimer des services
6. ✅ L'admin peut voir et gérer les leads
7. ✅ Les recharges fonctionnent et mettent à jour le solde
8. ✅ Les filtres et recherches sont réactifs
9. ✅ Les statistiques se calculent correctement
10. ✅ Les validations de formulaires fonctionnent

---

## 🎯 Prochaines Actions

Si tous les tests passent :
1. ✅ Système prêt pour la production
2. 💾 Faire un backup de la base de données
3. 📝 Documenter les processus métier
4. 🎨 Ajustements visuels si nécessaire
5. 🚀 Déploiement en production

---

**Bon test ! 🚀**
