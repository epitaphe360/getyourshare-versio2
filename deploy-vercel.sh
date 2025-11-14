#!/bin/bash
# ========================================
# Script de déploiement Vercel automatique
# ========================================

set -e

echo "🚀 Déploiement de ShareYourSales sur Vercel..."

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Token Vercel (fourni via variable d'environnement)
VERCEL_TOKEN="${VERCEL_TOKEN:-}"

# Vérifier que le token est défini
if [ -z "$VERCEL_TOKEN" ]; then
    echo -e "${RED}❌ Erreur : VERCEL_TOKEN n'est pas défini${NC}"
    echo ""
    echo "Pour obtenir un token :"
    echo "  1. Allez sur https://vercel.com/account/tokens"
    echo "  2. Créez un nouveau token"
    echo "  3. Exportez-le : export VERCEL_TOKEN='votre_token'"
    echo ""
    echo "Ou utilisez : vercel login"
    exit 1
fi

# Vérifier si Vercel CLI est installé
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI n'est pas installé. Installation...${NC}"
    npm install -g vercel
fi

echo -e "${BLUE}📦 Préparation du projet...${NC}"

# Aller dans le dossier frontend
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Installation des dépendances npm...${NC}"
    npm install
fi

echo -e "${BLUE}🔧 Configuration de Vercel...${NC}"

# Créer le fichier .vercelignore si nécessaire
cat > .vercelignore << 'EOF'
node_modules
.git
.env.local
.env.development
*.log
.DS_Store
EOF

echo -e "${GREEN}✅ Fichiers de configuration créés${NC}"

# Déployer sur Vercel (production)
echo -e "${BLUE}🚀 Déploiement en production...${NC}"

# Exporter le token
export VERCEL_ORG_ID="getyourshare"
export VERCEL_PROJECT_ID="getyourshare-versio2"

# Déployer avec le token
vercel --token "$VERCEL_TOKEN" --prod --yes \
  --name getyourshare-versio2 \
  --build-env REACT_APP_API_URL="https://getyourshare-backend-production.up.railway.app/api" \
  --build-env REACT_APP_SUPABASE_URL="https://iamezkmapbhlhhvvsits.supabase.co" \
  --build-env REACT_APP_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo" \
  --build-env REACT_APP_NAME="ShareYourSales" \
  --build-env REACT_APP_VERSION="1.0.0" \
  --build-env REACT_APP_ENV="production" \
  --build-env REACT_APP_FEATURE_MLM="false" \
  --build-env REACT_APP_FEATURE_ANALYTICS="true" \
  --build-env REACT_APP_FEATURE_AI_MARKETING="false" \
  --build-env DISABLE_ESLINT_PLUGIN="true"

echo -e "${GREEN}✅ Déploiement terminé avec succès !${NC}"
echo -e "${BLUE}🌐 Votre application est maintenant disponible sur Vercel${NC}"
