"""
Script de test pour le service email Resend
Teste l'envoi d'email avec le domaine info@shareyoursales.ma
"""

import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.resend_email_service import resend_service
from utils.logger import logger


def test_simple_email():
    """Test basique d'envoi d'email"""
    logger.info("🧪 Test 1: Email simple...")
    logger.info("-" * 50)

    result = resend_service.send_email(
        to_email="epitaphemarket@gmail.com",
        subject="✅ Test ShareYourSales - Email configuré!",
        html_content="""
        <h1>🎉 Félicitations!</h1>
        <p>Votre service email Resend fonctionne parfaitement avec le domaine <strong>info@shareyoursales.ma</strong>!</p>
        <ul>
            <li>✅ API Resend configurée</li>
            <li>✅ Domaine personnalisé actif</li>
            <li>✅ Emails prêts pour la production</li>
        </ul>
        <p><em>Envoyé depuis ShareYourSales Platform</em></p>
        """
    )

    if result["success"]:
        logger.info(f"✅ Email envoyé avec succès!")
        logger.info(f"   Message ID: {result.get('message_id')}")
        logger.info(f"   FROM: ShareYourSales <info@shareyoursales.ma>")
        logger.info(f"   TO: epitaphemarket@gmail.com")
    else:
        logger.error(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_welcome_email():
    """Test email de bienvenue"""
    logger.info("🧪 Test 2: Email de bienvenue...")
    logger.info("-" * 50)

    result = resend_service.send_welcome_email(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        role="influencer"
    )

    if result["success"]:
        logger.info(f"✅ Email de bienvenue envoyé!")
        logger.info(f"   Message ID: {result.get('message_id')}")
    else:
        logger.error(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_affiliate_request():
    """Test email de demande d'affiliation"""
    logger.info("🧪 Test 3: Email demande d'affiliation...")
    logger.info("-" * 50)

    result = resend_service.send_affiliate_request_confirmation(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        product_name="Ordinateur Gaming HP",
        company_name="TechStore Maroc"
    )

    if result["success"]:
        logger.info(f"✅ Email d'affiliation envoyé!")
        logger.info(f"   Message ID: {result.get('message_id')}")
    else:
        logger.error(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def test_2fa_code():
    """Test email avec code 2FA"""
    logger.info("🧪 Test 4: Email code 2FA...")
    logger.info("-" * 50)

    result = resend_service.send_2fa_code(
        to_email="epitaphemarket@gmail.com",
        user_name="Samuel",
        code="123456"
    )

    if result["success"]:
        logger.info(f"✅ Email 2FA envoyé!")
        logger.info(f"   Message ID: {result.get('message_id')}")
    else:
        logger.error(f"❌ Erreur: {result.get('error')}")

    print()
    return result["success"]


def main():
    """Exécuter tous les tests"""
    logger.info("=" * 50)
    logger.info("🚀 TEST SERVICE EMAIL RESEND")
    logger.info("   Domaine: info@shareyoursales.ma")
    logger.info("   API: Resend")
    logger.info("=" * 50)
    print()

    # Vérifier la configuration
    if not resend_service.api_key:
        logger.info("❌ ERREUR: Clé API Resend non configurée!")
        logger.info("   Vérifiez votre fichier .env")
        return

    logger.info(f"✅ Configuration détectée:")
    logger.info(f"   FROM: {resend_service.from_name} <{resend_service.from_address}>")
    logger.info(f"   API Key: {resend_service.api_key[:20]}...")
    print()

    # Exécuter les tests
    tests = [
        ("Email simple", test_simple_email),
        ("Email de bienvenue", test_welcome_email),
        ("Email affiliation", test_affiliate_request),
        ("Email 2FA", test_2fa_code)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.info(f"❌ Erreur lors du test: {str(e)}")
            results.append((test_name, False))

    # Résumé
    logger.info("=" * 50)
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")

    print()
    logger.info(f"Résultat: {passed}/{total} tests réussis")

    if passed == total:
        print()
        logger.info("🎉 TOUS LES TESTS SONT PASSÉS!")
        logger.info("✅ Votre service email Resend est prêt pour la production")
        logger.info(f"✅ Domaine {resend_service.from_address} configuré et fonctionnel")
    else:
        print()
        logger.info("⚠️ Certains tests ont échoué. Vérifiez la configuration.")


if __name__ == "__main__":
    main()
