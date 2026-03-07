# 🔐 COMPTES DE TEST - GetYourShare

## Mot de passe unique pour tous les comptes

```
Test123!
```

---

## 👤 Comptes disponibles

### 1. ADMIN - Accès Total

**Email:** `admin@getyourshare.com`  
**Mot de passe:** `Test123!`  
**Rôle:** Admin  
**Abonnement:** Enterprise (accès complet)

---

### 2. INFLUENCEURS (3 niveaux d'abonnement)

#### Hassan Oudrhiri - STARTER
- **Email:** `hassan.oudrhiri@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Influencer
- **Abonnement:** STARTER
- **Audience:** 67K followers
- **Niche:** Food & Cuisine

#### Sarah Benali - PRO
- **Email:** `sarah.benali@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Influencer
- **Abonnement:** PRO
- **Audience:** 125K followers
- **Niche:** Lifestyle

#### Karim Benjelloun - PRO ⭐
- **Email:** `karim.benjelloun@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Influencer
- **Abonnement:** PRO
- **Audience:** 285K followers
- **Niche:** Tech & Gaming

---

### 3. MARCHANDS (3 niveaux d'abonnement)

#### Boutique Maroc - STARTER
- **Email:** `boutique.maroc@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Merchant
- **Abonnement:** STARTER
- **Secteur:** Artisanat traditionnel marocain

#### Luxury Crafts - PRO
- **Email:** `luxury.crafts@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Merchant
- **Abonnement:** PRO
- **Secteur:** Artisanat Premium

#### ElectroMaroc - ENTERPRISE ⭐
- **Email:** `electro.maroc@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Merchant
- **Abonnement:** ENTERPRISE
- **Secteur:** Électronique & High-Tech

---

### 4. COMMERCIAL

#### Sofia Chakir
- **Email:** `sofia.chakir@getyourshare.com`
- **Mot de passe:** `Test123!`
- **Rôle:** Admin (Commercial)
- **Abonnement:** ENTERPRISE
- **Fonction:** Business Development

---

## ✅ Statut de vérification

Tous les comptes ont été créés dans la base de données Supabase avec :
- ✅ Email vérifié
- ✅ Compte actif
- ✅ 2FA désactivé (pour simplifier les tests)
- ✅ Téléphone non vérifié

---

## 🧪 Test de connexion réussi

Le compte admin a été testé avec succès :
- **URL Backend:** http://localhost:8001
- **Endpoint:** /api/auth/login
- **Status:** 200 OK
- **Token JWT:** Généré avec succès

---

## 📝 Notes importantes

1. **Mot de passe unique** : Tous les comptes utilisent `Test123!` pour faciliter les tests
2. **Structure de la base** :
   - Table `users` : Contient email, password_hash, role
   - Table `influencers` : Profils influenceurs liés à user_id
   - Table `merchants` : Profils marchands liés à user_id
3. **Abonnements** :
   - Influencers : `starter`, `pro` (pas d'enterprise)
   - Merchants : `free`, `starter`, `pro`, `enterprise`
4. **Rôles valides** : `admin`, `merchant`, `influencer` (pas de rôle `commercial` distinct)

---

## 🔧 Scripts utiles

### Vérifier les comptes
```bash
cd backend
python check_test_accounts.py
```

### Recréer les comptes (si nécessaire)
```bash
cd backend
python create_test_accounts.py
```

### Tester la connexion
```bash
cd backend
python test_login.py
```

---

**Dernière mise à jour:** 8 novembre 2025, 01:00 UTC
