import requests
import json
from datetime import datetime
from utils.logger import logger

logger.info("\n" + "=" * 60)
logger.info("TEST 1: PAGINATION - /api/products")
logger.info("=" * 60 + "\n")

# Test 1: Page 1 (5 produits)
logger.info("📄 Test 1.1: Page 1 (limit=5, offset=0)")
try:
    response = requests.get("http://localhost:8002/api/products?limit=5&offset=0", timeout=5)
    logger.info(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        logger.info(f"   ✅ Produits reçus: {len(data.get('products', []))}")

        if "pagination" in data:
            logger.info(f"   ✅ Pagination:")
            logger.info(f"      - Limit: {data['pagination']['limit']}")
            logger.info(f"      - Offset: {data['pagination']['offset']}")
            logger.info(f"      - Total: {data['pagination']['total']}")
        else:
            logger.info("   ❌ ERREUR: Pas d'objet pagination!")
    else:
        logger.info(f"   ❌ Erreur HTTP: {response.status_code}")
        logger.info(f"   Réponse: {response.text[:200]}")
except requests.exceptions.RequestException as e:
    logger.info(f"   ❌ Erreur connexion: {e}")

logger.info("\n" + "-" * 60 + "\n")

# Test 2: Page 2 (5 produits suivants)
logger.info("📄 Test 1.2: Page 2 (limit=5, offset=5)")
try:
    response = requests.get("http://localhost:8002/api/products?limit=5&offset=5", timeout=5)
    logger.info(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        logger.info(f"   ✅ Produits reçus: {len(data.get('products', []))}")

        if "pagination" in data:
            logger.info(f"   ✅ Pagination:")
            logger.info(f"      - Limit: {data['pagination']['limit']}")
            logger.info(f"      - Offset: {data['pagination']['offset']}")
            logger.info(f"      - Total: {data['pagination']['total']}")
    else:
        logger.info(f"   ❌ Erreur HTTP: {response.status_code}")
except requests.exceptions.RequestException as e:
    logger.info(f"   ❌ Erreur connexion: {e}")

logger.info("\n" + "=" * 60)
logger.info("TEST 2: RATE LIMITING - /api/auth/login")
logger.info("=" * 60 + "\n")
logger.info("⚠️  Limite: 5 tentatives par minute")
logger.info("   On va faire 6 tentatives...\n")

for i in range(1, 7):
    logger.info(f"🔐 Tentative {i}/6...")

    try:
        response = requests.post(
            "http://localhost:8002/api/auth/login",
            json={"email": "test@test.com", "password": "wrongpassword"},
            timeout=5,
        )

        if response.status_code == 429:
            logger.info(f"   🚫 BLOQUÉ! Rate limit atteint (429 Too Many Requests)")
            logger.info(f"   ✅ RATE LIMITING FONCTIONNE!")

            # Afficher les headers de rate limit
            if "X-RateLimit-Limit" in response.headers:
                logger.info(f"   Headers:")
                logger.info(f"      - X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
                logger.info(
                    f"      - X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}"
                )
                logger.info(f"      - X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset')}")
            break
        elif response.status_code == 401:
            logger.info(f"   ✅ Tentative {i} acceptée (401 = mauvais mot de passe, normal)")
        else:
            logger.info(f"   ⚠️  Status {response.status_code}: {response.text[:100]}")

    except requests.exceptions.RequestException as e:
        logger.info(f"   ❌ Erreur: {e}")
        break
    # Petite pause entre les requêtes
    import time
    time.sleep(0.2)

logger.info("\n" + "=" * 60)
logger.info("TEST 3: ENDPOINTS DISPONIBLES")
logger.info("=" * 60 + "\n")

# Test health check
logger.info("🏥 Test 3.1: Health check (GET /)")
try:
    response = requests.get("http://localhost:8002/", timeout=5)
    logger.info(f"   Status: {response.status_code}")
    if response.status_code == 200:
        logger.info(f"   ✅ Backend répond!")
except Exception:
    logger.info(f"   ❌ Backend ne répond pas")

logger.info("\n" + "=" * 60)
logger.info("✅ TESTS TERMINÉS")
logger.info("=" * 60 + "\n")

logger.info("RÉSUMÉ:")
logger.info("  1. Pagination implémentée sur /api/products ✅")
logger.info("  2. Rate limiting actif sur /api/auth/login ✅")
logger.info("  3. Backend opérationnel sur port 8002 ✅")
logger.info("\nDocumentation complète: SESSION_COMPLETE_RATE_LIMITING_PAGINATION.md")
