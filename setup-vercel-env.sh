#!/bin/bash

# ========================================
# 🚀 VERCEL ENVIRONMENT VARIABLES SETUP
# ShareYourSales - Automatic Configuration
# ========================================

set -e

echo "======================================"
echo "🚀 ShareYourSales - Vercel Env Setup"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI n'est pas installé${NC}"
    echo ""
    echo "Installation:"
    echo "  npm install -g vercel"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Vercel CLI détecté${NC}"
echo ""

# Ask for environment
echo "Sélectionnez l'environnement:"
echo "  1) Production"
echo "  2) Preview"
echo "  3) Development"
echo "  4) Tous les environnements"
echo ""
read -p "Votre choix (1-4): " env_choice

case $env_choice in
    1) ENV="production" ;;
    2) ENV="preview" ;;
    3) ENV="development" ;;
    4) ENV="production preview development" ;;
    *)
        echo -e "${RED}❌ Choix invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📝 Configuration pour: ${ENV}${NC}"
echo ""

# Function to add env variable
add_env() {
    local key=$1
    local value=$2
    local environments=$3

    echo -e "${YELLOW}⏳ Configuration de ${key}...${NC}"

    for env in $environments; do
        echo "$value" | vercel env add "$key" "$env" 2>/dev/null || echo -e "${YELLOW}⚠️  ${key} existe déjà pour ${env}${NC}"
    done
}

echo -e "${GREEN}🔧 Ajout des variables d'environnement...${NC}"
echo ""

# API Configuration
add_env "REACT_APP_API_URL" "https://getyourshare-backend-production.up.railway.app/api" "$ENV"
add_env "REACT_APP_BACKEND_URL" "https://getyourshare-backend-production.up.railway.app" "$ENV"

# Supabase
add_env "REACT_APP_SUPABASE_URL" "https://iamezkmapbhlhhvvsits.supabase.co" "$ENV"
add_env "REACT_APP_SUPABASE_ANON_KEY" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo" "$ENV"

# Application Settings
add_env "REACT_APP_NAME" "ShareYourSales" "$ENV"
add_env "REACT_APP_VERSION" "1.0.0" "$ENV"

# Environment-specific
if [[ "$ENV" == *"production"* ]]; then
    add_env "REACT_APP_ENV" "production" "production"
    add_env "REACT_APP_DEBUG" "false" "production"
fi

if [[ "$ENV" == *"development"* ]]; then
    add_env "REACT_APP_ENV" "development" "development"
    add_env "REACT_APP_DEBUG" "true" "development"
fi

if [[ "$ENV" == *"preview"* ]]; then
    add_env "REACT_APP_ENV" "preview" "preview"
    add_env "REACT_APP_DEBUG" "false" "preview"
fi

# Feature Flags
add_env "REACT_APP_FEATURE_MLM" "false" "$ENV"
add_env "REACT_APP_FEATURE_ANALYTICS" "true" "$ENV"
add_env "REACT_APP_FEATURE_AI_MARKETING" "false" "$ENV"

# Build Configuration
add_env "DISABLE_ESLINT_PLUGIN" "true" "$ENV"

echo ""
echo -e "${GREEN}✅ Configuration terminée!${NC}"
echo ""
echo "======================================"
echo "📋 Vérification des variables:"
echo "======================================"
echo ""

vercel env ls

echo ""
echo "======================================"
echo "🚀 Prochaines étapes:"
echo "======================================"
echo ""
echo "1. Vérifiez les variables ci-dessus"
echo "2. Redéployez votre application:"
echo ""
echo "   vercel --prod"
echo ""
echo "3. Ou attendez le prochain push Git"
echo ""
echo -e "${GREEN}🎉 Tout est prêt!${NC}"
echo ""
