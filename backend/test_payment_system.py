"""
Script de test pour le système de paiement automatique
Crée des données de test et exécute les fonctions
"""

from datetime import datetime, timedelta
from supabase_client import supabase
from auto_payment_service import AutoPaymentService
import uuid
from utils.logger import logger


def create_test_data():
    """Crée des données de test"""
    logger.info("\n🧪 CRÉATION DES DONNÉES DE TEST")
    logger.info("=" * 60)

    try:
        # 1. Créer un influenceur de test
        test_user = {
            "email": f"test_influencer_{uuid.uuid4().hex[:8]}@test.com",
            "password_hash": "$2b$12$test",
            "role": "influencer",
            "is_active": True,
        }

        user_result = supabase.table("users").insert(test_user).execute()
        user_id = user_result.data[0]["id"]
        logger.info(f"✅ Utilisateur créé: {user_id}")

        # 2. Créer le profil influenceur
        test_influencer = {
            "user_id": user_id,
            "username": f"test_user_{uuid.uuid4().hex[:6]}",
            "full_name": "Test Influencer",
            "balance": 0.0,
            "total_earnings": 0.0,
            "payment_method": "paypal",
            "payment_details": {"email": "test@paypal.com"},
        }

        inf_result = supabase.table("influencers").insert(test_influencer).execute()
        influencer_id = inf_result.data[0]["id"]
        logger.info(f"✅ Influenceur créé: {influencer_id}")

        # 3. Créer un produit de test
        test_product = {
            "name": "Produit Test",
            "price": 100.00,
            "commission_rate": 15.00,
            "is_available": True,
        }

        prod_result = supabase.table("products").insert(test_product).execute()
        product_id = prod_result.data[0]["id"]
        logger.info(f"✅ Produit créé: {product_id}")

        # 4. Créer des ventes de test
        logger.info("\n📦 Création de ventes de test...")

        # Vente 1: Ancienne (sera validée)
        old_date = (datetime.now() - timedelta(days=20)).isoformat()
        sale1 = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "amount": 100.00,
            "influencer_commission": 15.00,
            "platform_commission": 5.00,
            "merchant_revenue": 80.00,
            "status": "pending",
            "payment_status": "pending",
            "created_at": old_date,
        }

        supabase.table("sales").insert(sale1).execute()
        logger.info(f"  ✅ Vente ancienne créée (sera validée)")

        # Vente 2: Récente (ne sera pas validée)
        recent_date = (datetime.now() - timedelta(days=5)).isoformat()
        sale2 = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "amount": 80.00,
            "influencer_commission": 12.00,
            "platform_commission": 4.00,
            "merchant_revenue": 64.00,
            "status": "pending",
            "payment_status": "pending",
            "created_at": recent_date,
        }

        supabase.table("sales").insert(sale2).execute()
        logger.info(f"  ✅ Vente récente créée (ne sera pas validée)")

        # Vente 3: Ancienne (sera validée)
        sale3 = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "amount": 120.00,
            "influencer_commission": 18.00,
            "platform_commission": 6.00,
            "merchant_revenue": 96.00,
            "status": "pending",
            "payment_status": "pending",
            "created_at": old_date,
        }

        supabase.table("sales").insert(sale3).execute()
        logger.info(f"  ✅ Vente ancienne 2 créée (sera validée)")

        # Vente 4: Déjà complète (pour le solde)
        sale4 = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "amount": 150.00,
            "influencer_commission": 22.50,
            "platform_commission": 7.50,
            "merchant_revenue": 120.00,
            "status": "completed",
            "payment_status": "pending",
            "created_at": old_date,
        }

        supabase.table("sales").insert(sale4).execute()

        # Mettre à jour le solde de l'influenceur avec la vente déjà complète
        supabase.table("influencers").update({"balance": 22.50, "total_earnings": 22.50}).eq(
            "id", influencer_id
        ).execute()

        logger.info(f"  ✅ Vente complète créée (solde initial: 22.50€)")

        logger.info(f"\n✅ Données de test créées avec succès!")
        logger.info(f"\n📊 Résumé:")
        logger.info(f"   - Influenceur ID: {influencer_id}")
        logger.info(f"   - Solde initial: 22.50€")
        logger.info(f"   - Ventes en attente: 2 (33€ total)")
        logger.info(f"   - Après validation: 55.50€ (≥ 50€ = éligible paiement)")

        return {"user_id": user_id, "influencer_id": influencer_id, "product_id": product_id}

    except Exception as e:
        logger.info(f"❌ Erreur création données test: {e}")
        return None


def test_validation():
    """Test de la validation automatique"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: VALIDATION AUTOMATIQUE DES VENTES")
    logger.info("=" * 60)

    service = AutoPaymentService()
    result = service.validate_pending_sales()

    if result.get("success"):
        logger.info(f"\n✅ TEST RÉUSSI")
        logger.info(f"   - Ventes validées: {result.get('validated_sales', 0)}")
        logger.info(f"   - Commission totale: {result.get('total_commission', 0)}€")
        logger.info(f"   - Influenceurs mis à jour: {result.get('influencers_updated', 0)}")
    else:
        logger.info(f"\n❌ TEST ÉCHOUÉ")
        logger.error(f"   Erreur: {result.get('error')}")

    return result


def test_payouts():
    """Test des paiements automatiques"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: PAIEMENTS AUTOMATIQUES")
    logger.info("=" * 60)

    service = AutoPaymentService()
    result = service.process_automatic_payouts()

    if result.get("success"):
        logger.info(f"\n✅ TEST RÉUSSI")
        logger.info(f"   - Paiements traités: {result.get('processed_count', 0)}")
        logger.info(f"   - Montant total: {result.get('total_paid', 0)}€")
        logger.error(f"   - Échecs: {result.get('failed_count', 0)}")

        if result.get("failed_count", 0) > 0:
            logger.info(f"\n⚠️  PAIEMENTS ÉCHOUÉS:")
            for failure in result.get("failed_payments", []):
                logger.info(f"      - {failure}")
    else:
        logger.info(f"\n❌ TEST ÉCHOUÉ")
        logger.error(f"   Erreur: {result.get('error')}")

    return result


def test_refund(test_data):
    """Test du système de remboursement"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: REMBOURSEMENT")
    logger.info("=" * 60)

    if not test_data:
        logger.info("❌ Pas de données de test disponibles")
        return

    try:
        # Récupérer une vente complétée
        sales = (
            supabase.table("sales")
            .select("id, influencer_commission")
            .eq("influencer_id", test_data["influencer_id"])
            .eq("status", "completed")
            .limit(1)
            .execute()
        )

        if not sales.data:
            logger.info("⚠️  Aucune vente complétée trouvée pour test de remboursement")
            return

        sale_id = sales.data[0]["id"]
        commission = sales.data[0]["influencer_commission"]

        logger.info(f"\n📦 Test de remboursement pour vente: {sale_id}")
        logger.info(f"   Commission à annuler: {commission}€")

        service = AutoPaymentService()
        result = service.process_refund(sale_id, "test_refund")

        if result.get("success"):
            logger.info(f"\n✅ TEST RÉUSSI")
            logger.info(f"   - Vente remboursée: {sale_id}")
            logger.info(f"   - Commission annulée: {result.get('commission_cancelled')}€")
        else:
            logger.info(f"\n❌ TEST ÉCHOUÉ")
            logger.error(f"   Erreur: {result.get('error')}")

    except Exception as e:
        logger.info(f"❌ Erreur test remboursement: {e}")


def cleanup_test_data(test_data):
    """Nettoie les données de test"""
    logger.info("\n" + "=" * 60)
    logger.info("NETTOYAGE DES DONNÉES DE TEST")
    logger.info("=" * 60)

    if not test_data:
        logger.info("⚠️  Pas de données à nettoyer")
        return

    try:
        # Supprimer en ordre inverse des dépendances

        # 1. Supprimer les ventes
        supabase.table("sales").delete().eq("influencer_id", test_data["influencer_id"]).execute()
        logger.info("✅ Ventes supprimées")

        # 2. Supprimer les commissions
        supabase.table("commissions").delete().eq(
            "influencer_id", test_data["influencer_id"]
        ).execute()
        logger.info("✅ Commissions supprimées")

        # 3. Supprimer les payouts
        supabase.table("payouts").delete().eq("influencer_id", test_data["influencer_id"]).execute()
        logger.info("✅ Payouts supprimés")

        # 4. Supprimer l'influenceur
        supabase.table("influencers").delete().eq("id", test_data["influencer_id"]).execute()
        logger.info("✅ Influenceur supprimé")

        # 5. Supprimer l'utilisateur
        supabase.table("users").delete().eq("id", test_data["user_id"]).execute()
        logger.info("✅ Utilisateur supprimé")

        # 6. Supprimer le produit
        supabase.table("products").delete().eq("id", test_data["product_id"]).execute()
        logger.info("✅ Produit supprimé")

        logger.info("\n✅ Nettoyage terminé")

    except Exception as e:
        logger.info(f"❌ Erreur nettoyage: {e}")


def main():
    """Fonction principale de test"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 TESTS DU SYSTÈME DE PAIEMENT AUTOMATIQUE")
    logger.info("=" * 60)
    logger.info("\nCe script va:")
    logger.info("1. Créer des données de test")
    logger.info("2. Tester la validation automatique")
    logger.info("3. Tester les paiements automatiques")
    logger.info("4. Tester le système de remboursement")
    logger.info("5. Nettoyer les données de test")

    input("\nAppuyez sur ENTRÉE pour continuer...")

    # Créer les données
    test_data = create_test_data()

    if not test_data:
        logger.info("\n❌ Impossible de créer les données de test. Arrêt.")
        return

    input("\n\nAppuyez sur ENTRÉE pour tester la validation...")

    # Test 1: Validation
    validation_result = test_validation()

    input("\n\nAppuyez sur ENTRÉE pour tester les paiements...")

    # Test 2: Paiements
    payout_result = test_payouts()

    input("\n\nAppuyez sur ENTRÉE pour tester le remboursement...")

    # Test 3: Remboursement
    test_refund(test_data)

    # Proposer le nettoyage
    logger.info("\n" + "=" * 60)
    cleanup = input("\nVoulez-vous nettoyer les données de test ? (o/N): ")

    if cleanup.lower() == "o":
        cleanup_test_data(test_data)
    else:
        logger.info("\n⚠️  Données de test conservées")
        logger.info(f"   Influenceur ID: {test_data.get('influencer_id')}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTS TERMINÉS")
    logger.info("=" * 60 + "\n")


if __name__ == "__main__":
    main()
