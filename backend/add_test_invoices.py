"""
Script pour ajouter des factures de test dans la table invoices
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Importer le client Supabase du module existant
from supabase_client import supabase
from utils.logger import logger

def get_merchants():
    """Récupérer les marchands actifs"""
    try:
        result = supabase.from_("users").select("id, email, company_name, username").eq("role", "merchant").eq("status", "active").execute()
        return result.data if result.data else []
    except Exception as e:
        logger.info(f"❌ Erreur lors de la récupération des marchands: {e}")
        return []

def create_invoice(merchant, invoice_data):
    """Créer une facture"""
    try:
        # Vérifier si la facture existe déjà
        existing = supabase.from_("invoices").select("id").eq("invoice_number", invoice_data["invoice_number"]).execute()
        if existing.data:
            logger.info(f"⚠️  Facture {invoice_data['invoice_number']} existe déjà - ignorée")
            return None
        
        # Calculer total_amount avec taxes
        amount = invoice_data["amount"]
        tax_rate = 0.20  # TVA 20%
        tax_amount = round(amount * tax_rate, 2)
        total_amount = round(amount + tax_amount, 2)
        
        # Préparer les données de la facture
        invoice = {
            "invoice_number": invoice_data["invoice_number"],
            "merchant_id": merchant["id"],
            "amount": amount,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "currency": "EUR",
            "description": invoice_data["description"],
            "notes": invoice_data.get("notes"),
            "status": invoice_data["status"],
            "created_at": invoice_data["created_at"],
            "due_date": invoice_data["due_date"],
            "paid_at": invoice_data.get("paid_at"),
            "payment_method": invoice_data.get("payment_method"),
            "payment_reference": invoice_data.get("payment_reference")
        }
        
        # Insérer dans la base de données
        result = supabase.from_("invoices").insert(invoice).execute()
        
        if result.data:
            invoice_created = result.data[0]
            status_emoji = "✅" if invoice_created["status"] == "paid" else "⏳"
            logger.info(f"{status_emoji} Facture créée: {invoice_created['invoice_number']} - {merchant['company_name'] or merchant['username']} - {total_amount}€ ({invoice_created['status']})")
            return invoice_created
        else:
            logger.info(f"❌ Erreur lors de la création de la facture pour {merchant['company_name']}")
            return None
            
    except Exception as e:
        logger.info(f"❌ Erreur pour {merchant['company_name']}: {str(e)}")
        return None

# Descriptions de services typiques
SERVICE_DESCRIPTIONS = [
    "Abonnement mensuel plan Professional - Février 2024",
    "Abonnement mensuel plan Starter - Mars 2024",
    "Campagne publicitaire influenceurs - Q1 2024",
    "Abonnement mensuel plan Premium - Mars 2024",
    "Services de marketing digital - Janvier 2024",
    "Abonnement annuel plan Enterprise",
    "Campagne réseaux sociaux - Février 2024",
    "Abonnement mensuel plan Professional - Mars 2024",
    "Services de promotion produits - Mars 2024",
    "Abonnement semestriel plan Premium",
    "Marketing d'influence - Campagne printemps",
    "Abonnement mensuel plan Starter - Avril 2024"
]

def generate_test_invoices():
    """Générer des factures de test pour chaque marchand"""
    
    logger.info("\n" + "="*70)
    logger.info("📄 CRÉATION DES FACTURES DE TEST")
    logger.info("="*70 + "\n")
    
    # Récupérer les marchands
    merchants = get_merchants()
    
    if not merchants:
        logger.info("❌ Aucun marchand trouvé. Exécutez d'abord add_budgets.py")
        return
    
    logger.info(f"✅ {len(merchants)} marchands trouvés\n")
    
    created_count = 0
    current_year = 2024
    invoice_counter = 1
    
    # Créer 2-3 factures pour chaque marchand
    for merchant in merchants:
        num_invoices = random.randint(2, 3)
        
        for i in range(num_invoices):
            # Générer des dates réalistes
            months_ago = random.randint(1, 4)
            created_date = datetime(2024, 3, 1) - timedelta(days=30 * months_ago)
            due_date = created_date + timedelta(days=15)
            
            # 70% des factures sont payées
            is_paid = random.random() < 0.7
            status = "paid" if is_paid else "pending"
            
            # Si payée, date de paiement entre création et échéance
            paid_at = None
            payment_method = None
            payment_reference = None
            
            if is_paid:
                days_until_paid = random.randint(1, 14)
                paid_at = (created_date + timedelta(days=days_until_paid)).isoformat()
                payment_method = random.choice(["card", "bank_transfer", "stripe"])
                payment_reference = f"PAY-{random.randint(10000, 99999)}"
            
            # Montants réalistes selon le type d'abonnement
            amount_options = [299.00, 499.00, 899.00, 1299.00, 1999.00, 2499.00]
            amount = random.choice(amount_options)
            
            invoice_data = {
                "invoice_number": f"INV-{current_year}-{str(invoice_counter).zfill(4)}",
                "amount": amount,
                "description": random.choice(SERVICE_DESCRIPTIONS),
                "notes": "Paiement dû sous 15 jours. Merci de votre confiance.",
                "status": status,
                "created_at": created_date.isoformat(),
                "due_date": due_date.isoformat(),
                "paid_at": paid_at,
                "payment_method": payment_method,
                "payment_reference": payment_reference
            }
            
            result = create_invoice(merchant, invoice_data)
            if result:
                created_count += 1
                invoice_counter += 1
    
    logger.info("\n" + "="*70)
    logger.info(f"✨ RÉSULTAT: {created_count} factures créées")
    logger.info("="*70)
    
    # Afficher le résumé
    logger.info("\n📊 RÉSUMÉ DES FACTURES:\n")
    
    # Récupérer toutes les factures avec les infos des marchands
    # Utiliser merchant_id pour faire le JOIN manuellement
    invoices_result = supabase.from_("invoices").select("*").order("created_at", desc=True).execute()
    
    if invoices_result.data:
        total_invoices = len(invoices_result.data)
        paid_invoices = sum(1 for inv in invoices_result.data if inv["status"] == "paid")
        pending_invoices = sum(1 for inv in invoices_result.data if inv["status"] == "pending")
        total_amount = sum(float(inv["total_amount"]) for inv in invoices_result.data)
        paid_amount = sum(float(inv["total_amount"]) for inv in invoices_result.data if inv["status"] == "paid")
        
        logger.info(f"📈 Total factures: {total_invoices}")
        logger.info(f"✅ Payées: {paid_invoices} ({paid_amount:.2f}€)")
        logger.info(f"⏳ En attente: {pending_invoices} ({total_amount - paid_amount:.2f}€)")
        logger.info(f"💰 Montant total: {total_amount:.2f}€\n")
        
        logger.info("📋 Dernières factures créées:\n")
        
        # Récupérer les infos des merchants séparément
        merchant_ids = [inv["merchant_id"] for inv in invoices_result.data[:10]]
        merchants_result = supabase.from_("users").select("id, company_name, username").in_("id", merchant_ids).execute()
        merchants_dict = {m["id"]: m for m in merchants_result.data} if merchants_result.data else {}
        
        for inv in invoices_result.data[:10]:  # Afficher les 10 dernières
            merchant = merchants_dict.get(inv["merchant_id"], {})
            merchant_name = merchant.get("company_name") or merchant.get("username", "Inconnu")
            status_symbol = "✅" if inv["status"] == "paid" else "⏳"
            logger.info(f"  {status_symbol} {inv['invoice_number']} - {merchant_name}")
            logger.info(f"     Montant: {inv['total_amount']}€ | Statut: {inv['status']}")
            logger.info(f"     Créée: {inv['created_at'][:10]} | Échéance: {inv['due_date'][:10]}")
            if inv.get('paid_at'):
                logger.info(f"     Payée le: {inv['paid_at'][:10]}")
            print()
    else:
        logger.info("Aucune facture trouvée.")
    
    logger.info("\n💡 INSTRUCTIONS:")
    logger.info("   1. Allez sur la page 'Facturation - Annonceurs'")
    logger.info("   2. Vous verrez toutes les factures créées")
    logger.info("   3. Cliquez sur 'Nouvelle Facture' pour en créer d'autres")
    logger.info("   4. Les factures sont maintenant stockées dans Supabase!")
    print()

if __name__ == "__main__":
    generate_test_invoices()
