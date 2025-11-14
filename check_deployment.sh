#!/bin/bash

# Script de vérification du déploiement Vercel + Railway

echo "🔍 VÉRIFICATION DU DÉPLOIEMENT GETYOURSHARE"
echo "=========================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKEND_URL="https://getyourshare-backend-production.up.railway.app"
VERCEL_URL="https://getyourshare-7h1z5006j-getyourshares-projects.vercel.app"

echo "📡 TEST 1 : Vérification du backend Railway"
echo "-------------------------------------------"
echo "URL testée : $BACKEND_URL/health"
echo ""

HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BACKEND_URL/health" 2>&1)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Backend Railway est EN LIGNE${NC}"
    echo "Réponse : $HEALTH_BODY"
else
    echo -e "${RED}❌ Backend Railway est DOWN ou inaccessible${NC}"
    echo "HTTP Code: $HTTP_CODE"
    echo "Réponse : $HEALTH_BODY"
fi

echo ""
echo "=========================================="
echo ""

echo "🔐 TEST 2 : Vérification CORS"
echo "-------------------------------------------"
echo "Test : Requête OPTIONS depuis Vercel URL"
echo ""

CORS_RESPONSE=$(curl -s -i -X OPTIONS \
  "$BACKEND_URL/api/auth/login" \
  -H "Origin: $VERCEL_URL" \
  -H "Access-Control-Request-Method: POST" 2>&1)

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin: $VERCEL_URL"; then
    echo -e "${GREEN}✅ CORS configuré correctement${NC}"
    echo "Access-Control-Allow-Origin: $VERCEL_URL"
else
    echo -e "${RED}❌ CORS PAS configuré pour Vercel${NC}"
    echo "L'URL Vercel n'est pas dans la whitelist CORS"
    echo ""
    echo "Headers CORS reçus :"
    echo "$CORS_RESPONSE" | grep -i "access-control"
fi

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-credentials: true"; then
    echo -e "${GREEN}✅ CORS Allow Credentials activé${NC}"
else
    echo -e "${YELLOW}⚠️  CORS Allow Credentials non trouvé${NC}"
fi

echo ""
echo "=========================================="
echo ""

echo "🔑 TEST 3 : Test de connexion API"
echo "-------------------------------------------"
echo "Test : POST /api/auth/login avec credentials de test"
echo ""

LOGIN_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -H "Origin: $VERCEL_URL" \
  -d '{"email":"test@test.com","password":"wrongpassword"}' 2>&1)

LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$LOGIN_CODE" = "401" ] || [ "$LOGIN_CODE" = "422" ]; then
    echo -e "${GREEN}✅ Endpoint login accessible${NC}"
    echo "HTTP Code: $LOGIN_CODE (attendu - mauvais credentials)"
    echo "Réponse : $LOGIN_BODY"
elif [ "$LOGIN_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Endpoint login accessible (connexion réussie!)${NC}"
    echo "Réponse : $LOGIN_BODY"
else
    echo -e "${RED}❌ Endpoint login inaccessible ou erreur${NC}"
    echo "HTTP Code: $LOGIN_CODE"
    echo "Réponse : $LOGIN_BODY"
fi

echo ""
echo "=========================================="
echo ""

echo "📊 TEST 4 : Test endpoint products"
echo "-------------------------------------------"
echo "Test : GET /api/products"
echo ""

PRODUCTS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  -X GET "$BACKEND_URL/api/products?limit=5" \
  -H "Origin: $VERCEL_URL" 2>&1)

PRODUCTS_CODE=$(echo "$PRODUCTS_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
PRODUCTS_BODY=$(echo "$PRODUCTS_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$PRODUCTS_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Endpoint products accessible${NC}"
    echo "Nombre de caractères dans la réponse : ${#PRODUCTS_BODY}"
    if [ ${#PRODUCTS_BODY} -gt 100 ]; then
        echo -e "${GREEN}✅ Données présentes${NC}"
    else
        echo -e "${YELLOW}⚠️  Réponse courte, vérifier les données${NC}"
        echo "Réponse : $PRODUCTS_BODY"
    fi
elif [ "$PRODUCTS_CODE" = "401" ]; then
    echo -e "${YELLOW}⚠️  Endpoint nécessite authentification${NC}"
    echo "HTTP Code: 401 (normal si endpoint protégé)"
else
    echo -e "${RED}❌ Endpoint products inaccessible${NC}"
    echo "HTTP Code: $PRODUCTS_CODE"
    echo "Réponse : $PRODUCTS_BODY"
fi

echo ""
echo "=========================================="
echo ""

echo "📋 RÉSUMÉ"
echo "-------------------------------------------"
echo ""
echo "Commits récents :"
git log --oneline -3
echo ""

echo "🎯 PROCHAINES ÉTAPES :"
echo ""
echo "1. Si le backend est DOWN (Test 1) :"
echo "   → Vérifier les logs Railway"
echo "   → Redéployer Railway si nécessaire"
echo ""
echo "2. Si CORS échoue (Test 2) :"
echo "   → Railway n'a pas redéployé avec les corrections"
echo "   → Forcer un redéploiement Railway"
echo ""
echo "3. Configurer les variables Vercel :"
echo "   → Aller sur Vercel Dashboard"
echo "   → Settings → Environment Variables"
echo "   → Ajouter REACT_APP_BACKEND_URL=$BACKEND_URL"
echo "   → Redéployer Vercel"
echo ""
echo "4. Lire VERCEL_DEBUG_GUIDE.md pour plus de détails"
echo ""
echo "=========================================="
