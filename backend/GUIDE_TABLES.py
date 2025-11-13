from utils.logger import logger
logger.info("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🗄️  GUIDE CRÉATION TABLES - TOP 5 FEATURES          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📋 INSTRUCTIONS RAPIDES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ÉTAPE 1: Ouvrir Supabase Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Allez sur: https://supabase.com/dashboard
   2. Sélectionnez votre projet
   3. Cliquez sur "SQL Editor" dans le menu

ÉTAPE 2: Créer Tables Gamification 🏆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Dans SQL Editor, cliquez "New query"
   2. Ouvrez le fichier: CREATE_GAMIFICATION_TABLES.sql
   3. Copiez TOUT le contenu (Ctrl+A, Ctrl+C)
   4. Collez dans Supabase SQL Editor (Ctrl+V)
   5. Cliquez "Run" (ou Ctrl+Enter)
   
   ✅ Si succès: "Success. No rows returned"
   ❌ Si erreur: Lisez le message, souvent c'est "already exists" (normal)

ÉTAPE 3: Créer Tables Matching 💘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Créez une NOUVELLE query
   2. Ouvrez: CREATE_MATCHING_TABLES.sql
   3. Copiez tout et collez
   4. Cliquez "Run"
   
   ✅ Tables créées: 12 nouvelles tables

ÉTAPE 4: Insérer Données Test 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Dans ce terminal, exécutez:
   
   cd backend
   ..\.venv\Scripts\python.exe init_top5_data.py
   
   ✅ Cela va créer ~30 lignes de données test

ÉTAPE 5: Tester 🧪
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Terminal 1 - Backend:
      cd backend
      ..\.venv\Scripts\python.exe -m uvicorn server:app --reload --port 8000
   
   Terminal 2 - Test:
      cd backend
      ..\.venv\Scripts\python.exe test_top5_integration.py
   
   ✅ Vous devriez voir: Status 200 (au lieu de 500)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 FICHIERS IMPORTANTS:
   ├── CREATE_GAMIFICATION_TABLES.sql  (Étape 2)
   ├── CREATE_MATCHING_TABLES.sql      (Étape 3)
   ├── init_top5_data.py               (Étape 4)
   └── test_top5_integration.py        (Étape 5)

💡 ASTUCES:
   • Les tables utilisent "IF NOT EXISTS" → pas d'erreur si déjà créées
   • Les données test utilisent vos users/influencers existants
   • Si erreur foreign key → créez d'abord users, merchants, influencers

⏱️  TEMPS ESTIMÉ: 5-10 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ APRÈS CE GUIDE, VOUS AUREZ:
   ✅ 12 nouvelles tables Supabase
   ✅ Données test prêtes
   ✅ Endpoints TOP 5 fonctionnels (status 200)
   ✅ GamificationWidget avec vraies données
   ✅ Matching avec profils réels

╔══════════════════════════════════════════════════════════════╗
║  🎯 COMMENCEZ PAR OUVRIR SUPABASE DASHBOARD MAINTENANT!     ║
╚══════════════════════════════════════════════════════════════╝
""")
