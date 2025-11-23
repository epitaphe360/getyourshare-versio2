# Installation des Fonctionnalités "Wow Effect"

Les fonctionnalités suivantes ont été implémentées :
1. **Calculateur ROI** (Public)
2. **Système de Parrainage Viral** (Multi-niveaux)
3. **IA Marketing** (Générateur de contenu & Recommandations)

## ⚠️ Étape Critique : Base de Données

Avant que ces fonctionnalités ne soient opérationnelles, vous devez créer les tables nécessaires dans Supabase.

### 1. Accédez à Supabase
Allez dans votre projet Supabase > SQL Editor.

### 2. Exécutez le script SQL
Copiez le contenu du fichier `backend/sql/create_wow_features_tables.sql` et exécutez-le dans l'éditeur SQL.

Ce script va créer :
- `referral_codes` : Stockage des codes de parrainage
- `referrals` : Suivi des parrainages (qui a invité qui)
- `referral_rewards` : Récompenses et niveaux (Gamification)
- `referral_earnings` : Historique des gains
- `product_recommendations` : Cache des recommandations IA
- `ai_generated_content` : Historique du contenu généré
- `live_shopping_events` : Événements de live shopping

### 3. Vérification
Une fois le script exécuté, vous pouvez vérifier que tout fonctionne en lançant le backend :

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

Et le frontend :
```bash
cd frontend
npm start
```

## Accès aux Fonctionnalités

- **Calculateur ROI** : `http://localhost:3000/roi-calculator`
- **Hub Fonctionnalités** : `http://localhost:3000/features`
- **Dashboard Influenceur** : `http://localhost:3000/dashboard/influencer` (nécessite un compte influenceur)

## Tests

Des tests unitaires ont été créés pour valider la logique backend :
```bash
cd backend
python -m unittest test_wow_features.py
```
