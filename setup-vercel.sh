#!/bin/bash
# ============================================
# Script de configuration automatique Vercel
# ============================================

echo "🚀 Configuration Vercel pour ShareYourSales Frontend"
echo "=================================================="

# Variables
VERCEL_TOKEN="O0sBOF9tJcu74F9w9yKfuScF"
PROJECT_NAME="shareyoursales-frontend"
BACKEND_URL="https://getyourshare-backend-production.up.railway.app"

# Vérifier si vercel CLI est installé
if ! command -v vercel &> /dev/null; then
    echo "📦 Installation de Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Vercel CLI installé"

# Se déplacer dans le dossier frontend
cd frontend || exit 1

echo "📋 Configuration des variables d'environnement..."

# Configurer les variables d'environnement pour production
vercel env add REACT_APP_API_URL production <<EOF
${BACKEND_URL}/api
EOF

vercel env add REACT_APP_BACKEND_URL production <<EOF
${BACKEND_URL}
EOF

vercel env add REACT_APP_SUPABASE_URL production <<EOF
https://iamezkmapbhlhhvvsits.supabase.co
EOF

vercel env add REACT_APP_SUPABASE_ANON_KEY production <<EOF
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNDQ0MTMsImV4cCI6MjA3NjcyMDQxM30.drzPDA02bKMv-_DxxyWtdwqg0a8nEIdHTu8UXIslgfo
EOF

vercel env add REACT_APP_NAME production <<EOF
ShareYourSales
EOF

vercel env add REACT_APP_VERSION production <<EOF
1.0.0
EOF

vercel env add REACT_APP_ENV production <<EOF
production
EOF

vercel env add REACT_APP_FEATURE_MLM production <<EOF
false
EOF

vercel env add REACT_APP_FEATURE_ANALYTICS production <<EOF
true
EOF

vercel env add REACT_APP_FEATURE_AI_MARKETING production <<EOF
false
EOF

vercel env add DISABLE_ESLINT_PLUGIN production <<EOF
true
EOF

vercel env add REACT_APP_DEBUG production <<EOF
false
EOF

echo "✅ Variables d'environnement configurées"

echo ""
echo "🎉 Configuration terminée !"
echo ""
echo "Pour déployer manuellement :"
echo "  cd frontend"
echo "  vercel --prod"
echo ""
echo "Pour activer le déploiement automatique :"
echo "  1. Allez sur https://vercel.com/dashboard"
echo "  2. Import votre projet GitHub"
echo "  3. Définissez Root Directory : frontend"
echo "  4. Les variables sont déjà configurées !"
