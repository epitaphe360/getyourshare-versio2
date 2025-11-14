#!/bin/bash
# ============================================
# Script de vérification du token Vercel
# ============================================

echo "🔍 Diagnostic du Token Vercel"
echo "============================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Tokens à tester
TOKEN_USER="W0DgOUylwRSEHitnRR3E81YM"
TOKEN_SCRIPT="O0sBOF9tJcu74F9w9yKfuScF"

echo "📋 Tokens à tester :"
echo "  1. Token utilisateur : ${TOKEN_USER:0:10}...${TOKEN_USER: -5}"
echo "  2. Token script      : ${TOKEN_SCRIPT:0:10}...${TOKEN_SCRIPT: -5}"
echo ""

# Fonction pour tester un token
test_token() {
    local TOKEN=$1
    local NAME=$2

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${BLUE}🔐 Test du token : $NAME${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Test 1: Authentification de base
    echo -n "  [1/5] Vérification de l'authentification... "
    RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" https://api.vercel.com/v2/user)
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        USERNAME=$(echo "$BODY" | grep -o '"username":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
        EMAIL=$(echo "$BODY" | grep -o '"email":"[^"]*"' | cut -d'"' -f4 || echo "N/A")
        echo -e "     ${GREEN}Username: $USERNAME${NC}"
        echo -e "     ${GREEN}Email: $EMAIL${NC}"
        TOKEN_VALID=true
    elif [ "$HTTP_CODE" = "403" ]; then
        echo -e "${RED}❌ ÉCHEC (403 Forbidden)${NC}"
        echo -e "     ${RED}Le token n'est pas valide ou a expiré${NC}"
        TOKEN_VALID=false
    elif [ "$HTTP_CODE" = "401" ]; then
        echo -e "${RED}❌ ÉCHEC (401 Unauthorized)${NC}"
        echo -e "     ${RED}Le token n'est pas reconnu${NC}"
        TOKEN_VALID=false
    else
        echo -e "${RED}❌ ÉCHEC (HTTP $HTTP_CODE)${NC}"
        echo -e "     ${YELLOW}$BODY${NC}"
        TOKEN_VALID=false
    fi

    if [ "$TOKEN_VALID" = false ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Token invalide - Tests suivants ignorés${NC}"
        return 1
    fi

    # Test 2: Liste des projets
    echo -n "  [2/5] Récupération de la liste des projets... "
    RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://api.vercel.com/v9/projects")
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        PROJECT_COUNT=$(echo "$BODY" | grep -o '"id":"[^"]*"' | wc -l)
        echo -e "     ${GREEN}Nombre de projets: $PROJECT_COUNT${NC}"

        # Afficher les noms de projets
        PROJECTS=$(echo "$BODY" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$PROJECTS" ]; then
            echo -e "     ${GREEN}Projets:${NC}"
            echo "$PROJECTS" | while read -r proj; do
                echo -e "       - $proj"
            done
        fi
    else
        echo -e "${RED}❌ ÉCHEC (HTTP $HTTP_CODE)${NC}"
    fi

    # Test 3: Vérification du projet spécifique
    echo -n "  [3/5] Recherche du projet 'getyourshare-versio2'... "
    if echo "$BODY" | grep -q '"name":"getyourshare-versio2"'; then
        echo -e "${GREEN}✅ TROUVÉ${NC}"
        PROJECT_ID=$(echo "$BODY" | grep -A5 '"name":"getyourshare-versio2"' | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo -e "     ${GREEN}Project ID: $PROJECT_ID${NC}"
    else
        echo -e "${YELLOW}⚠️  NON TROUVÉ${NC}"
        echo -e "     ${YELLOW}Le projet 'getyourshare-versio2' n'existe pas sur ce compte${NC}"
    fi

    # Test 4: Permissions du token
    echo -n "  [4/5] Vérification des permissions... "
    RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://api.vercel.com/v2/user/tokens")
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        echo -e "     ${GREEN}Le token peut lister les autres tokens${NC}"
    else
        echo -e "${YELLOW}⚠️  Permissions limitées${NC}"
    fi

    # Test 5: Essai de déploiement (simulation)
    echo -n "  [5/5] Test de capacité de déploiement... "
    RESPONSE=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://api.vercel.com/v6/deployments")
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)

    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        DEPLOY_COUNT=$(echo "$RESPONSE" | head -n -1 | grep -o '"uid":"[^"]*"' | wc -l)
        echo -e "     ${GREEN}Nombre de déploiements: $DEPLOY_COUNT${NC}"
    else
        echo -e "${RED}❌ ÉCHEC (HTTP $HTTP_CODE)${NC}"
    fi

    echo ""
    return 0
}

# Tester les deux tokens
test_token "$TOKEN_USER" "Token Utilisateur (W0Dg...)"
USER_TOKEN_RESULT=$?

test_token "$TOKEN_SCRIPT" "Token Script (O0sB...)"
SCRIPT_TOKEN_RESULT=$?

# Résumé
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📊 RÉSUMÉ DU DIAGNOSTIC${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $USER_TOKEN_RESULT -eq 0 ]; then
    echo -e "✅ Token utilisateur (W0Dg...) : ${GREEN}VALIDE${NC}"
elif [ $SCRIPT_TOKEN_RESULT -eq 0 ]; then
    echo -e "⚠️  Token utilisateur (W0Dg...) : ${RED}INVALIDE${NC}"
    echo -e "✅ Token script (O0sB...) : ${GREEN}VALIDE${NC}"
else
    echo -e "❌ Token utilisateur (W0Dg...) : ${RED}INVALIDE${NC}"
    echo -e "❌ Token script (O0sB...) : ${RED}INVALIDE${NC}"
    echo ""
    echo -e "${YELLOW}🔧 SOLUTIONS :${NC}"
    echo ""
    echo "1. Générer un nouveau token sur Vercel :"
    echo -e "   ${BLUE}https://vercel.com/account/tokens${NC}"
    echo ""
    echo "2. Se connecter via CLI :"
    echo "   $ vercel login"
    echo ""
    echo "3. Utiliser l'interface web Vercel (RECOMMANDÉ) :"
    echo -e "   ${BLUE}https://vercel.com/dashboard${NC}"
    echo "   - Import Git Repository"
    echo "   - Sélectionner 'epitaphe360/getyourshare-versio2'"
    echo "   - Configurer Root Directory : 'frontend'"
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}📝 INFORMATIONS SUPPLÉMENTAIRES${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Configuration actuelle dans les fichiers :"
echo "  - vercel.json : Configuration du projet"
echo "  - setup-vercel.sh : Token hardcodé (O0sB...)"
echo "  - deploy-vercel.sh : Token hardcodé (O0sB...)"
echo ""
echo "Recommandation :"
echo "  - NE PAS hardcoder les tokens dans les fichiers"
echo "  - Utiliser 'vercel login' pour l'authentification"
echo "  - Ou utiliser des variables d'environnement : VERCEL_TOKEN"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Diagnostic terminé"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
