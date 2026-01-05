# 🚀 Connexion Rapide - GetYourShare

## 🔑 Identifiants de Test

**Mot de passe universel:** `Test123!`

### 👤 Comptes Disponibles

| Email | Rôle | Plan | Description |
|-------|------|------|-------------|
| `admin@getyourshare.com` | Admin | Enterprise | Accès complet administrateur |
| `hassan.oudrhiri@getyourshare.com` | Influencer | Starter | Influenceur Food & Cuisine (67K followers) |
| `sarah.benali@getyourshare.com` | Influencer | Pro | Influenceuse Lifestyle (125K followers) |
| `karim.benjelloun@getyourshare.com` | Influencer | Pro | Influenceur Tech & Gaming (285K followers) |
| `boutique.maroc@getyourshare.com` | Merchant | Starter | Artisanat traditionnel marocain |
| `luxury.crafts@getyourshare.com` | Merchant | Pro | Artisanat Premium |
| `electro.maroc@getyourshare.com` | Merchant | Enterprise | Électronique & High-Tech |
| `sofia.chakir@getyourshare.com` | Commercial | Enterprise | Compte commercial/admin |

## 📝 Instructions

### Option 1: Exécuter le script SQL (Recommandé)

1. Va sur ton **dashboard Supabase**
2. Clique sur **SQL Editor** dans le menu de gauche
3. Copie le contenu du fichier `backend/update_passwords.sql`
4. Colle et exécute la requête SQL
5. Vérifie que les comptes ont été mis à jour

### Option 2: Utiliser le script Python

```bash
cd backend
python3 create_test_accounts.py  # Si les comptes n'existent pas encore
```

## 🔐 Sécurité

⚠️ **IMPORTANT:** Ces identifiants sont pour le **développement uniquement**!

En production:
- Change tous les mots de passe
- Active la vérification 2FA
- Utilise des mots de passe forts et uniques
- Révoque ces comptes de test

## ✅ Connexion

### Frontend Vercel
1. Va sur: https://getyourshare-version-final-6sc7t2oaj-getyourshares-projects.vercel.app
2. Utilise n'importe quel email ci-dessus
3. Mot de passe: `Test123!`

### Backend Railway
- URL API: https://getyourshare-backend-production.up.railway.app
- Docs API: https://getyourshare-backend-production.up.railway.app/docs

## 🎯 Tests Rapides

### Admin
```
Email: admin@getyourshare.com
Password: Test123!
```

### Influencer
```
Email: hassan.oudrhiri@getyourshare.com
Password: Test123!
```

### Merchant
```
Email: boutique.maroc@getyourshare.com
Password: Test123!
```

---

**Dernière mise à jour:** $(date)
**Environnement:** Development
**Backend:** Railway (server.py avec httpOnly cookies)
**Frontend:** Vercel
