"""Tester la connexion avec un compte de test"""
import requests
import json
from utils.logger import logger

# URL du backend
API_URL = "http://localhost:8001"

# Compte de test
TEST_EMAIL = "admin@getyourshare.com"
TEST_PASSWORD = "Test123!"

logger.info(f"=== TEST DE CONNEXION ===")
logger.info(f"Email: {TEST_EMAIL}")
logger.info(f"Password: {TEST_PASSWORD}\n")

# Requête de connexion
try:
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        },
        headers={"Content-Type": "application/json"}
    )
    
    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        logger.info("✅ CONNEXION RÉUSSIE!")
        logger.info(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        logger.info(f"User: {data.get('user', {})}")
    else:
        logger.info(f"❌ ÉCHEC DE CONNEXION")
        logger.info(f"Response: {response.text}")
        
except Exception as e:
    logger.info(f"❌ ERREUR: {e}")
