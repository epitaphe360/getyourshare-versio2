"""
============================================
SCRIPT DE CRÉATION DE PRODUITS EN MODÉRATION
Crée des produits de test avec différents niveaux de risque
============================================
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from utils.logger import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.info("❌ Erreur: Variables d'environnement Supabase manquantes")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ============================================
# PRODUITS DE TEST
# ============================================

test_products = [
    {
        "product_name": "iPhone 15 Pro Max - Prix Exceptionnel",
        "product_description": "iPhone 15 Pro Max 256GB neuf, scellé. Prix imbattable! Livraison gratuite partout au Maroc. Garantie internationale. Ne ratez pas cette offre exceptionnelle!",
        "product_category": "Électronique",
        "product_price": 4500.00,
        "product_images": ["https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=400"],
        "ai_decision": "rejected",
        "ai_confidence": 0.95,
        "ai_risk_level": "critical",
        "ai_flags": ["prix_suspect", "description_exageree", "possible_contrefaçon"],
        "ai_reason": "Prix anormalement bas pour un iPhone 15 Pro Max neuf (prix marché: 14000-16000 MAD). Description contient des superlatifs suspects ('imbattable', 'exceptionnel'). Risque élevé de contrefaçon ou arnaque.",
        "ai_recommendation": "Rejeter - Prix incompatible avec le marché, forte suspicion de contrefaçon"
    },
    {
        "product_name": "Parfum Chanel N°5 - Original",
        "product_description": "Authentique parfum Chanel N°5 100ml. Importé directement de France. Certificat d'authenticité fourni.",
        "product_category": "Beauté",
        "product_price": 2800.00,
        "product_images": ["https://images.unsplash.com/photo-1541643600914-78b084683601?w=400"],
        "ai_decision": "rejected",
        "ai_confidence": 0.72,
        "ai_risk_level": "high",
        "ai_flags": ["marque_luxe", "authenticite_douteuse"],
        "ai_reason": "Produit de luxe haute gamme nécessitant vérification approfondie. Le prix est dans la fourchette mais nécessite validation du certificat d'authenticité et des documents d'importation.",
        "ai_recommendation": "Révision manuelle - Vérifier certificat d'authenticité et documents d'importation"
    },
    {
        "product_name": "Caftan Marocain Fait Main",
        "product_description": "Magnifique caftan traditionnel marocain, broderie à la main, tissu premium. Parfait pour les occasions spéciales. Disponible en plusieurs tailles et couleurs.",
        "product_category": "Mode",
        "product_price": 1200.00,
        "product_images": ["https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=400"],
        "ai_decision": "approved",
        "ai_confidence": 0.88,
        "ai_risk_level": "medium",
        "ai_flags": ["artisanat_local"],
        "ai_reason": "Produit artisanal marocain typique. Prix cohérent avec le marché. Description claire et professionnelle. Confiance élevée mais nécessite validation photos pour confirmer qualité.",
        "ai_recommendation": "Approuver après vérification des photos"
    },
    {
        "product_name": "Montre Rolex Submariner - Occasion Excellente",
        "product_description": "Rolex Submariner Date 116610LN en excellent état. Papiers et boîte d'origine. Service complet récent. Une opportunité rare pour les collectionneurs.",
        "product_category": "Accessoires",
        "product_price": 85000.00,
        "product_images": ["https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=400"],
        "ai_decision": "rejected",
        "ai_confidence": 0.91,
        "ai_risk_level": "critical",
        "ai_flags": ["marque_luxe_premium", "valeur_elevee", "verification_requise"],
        "ai_reason": "Montre de luxe de très haute valeur. Nécessite vérification exhaustive: certificat d'authenticité Rolex, numéro de série, facture d'achat originale, historique du service. Risque très élevé de contrefaçon sur ce segment.",
        "ai_recommendation": "Révision manuelle obligatoire - Authentification par expert horloger requis"
    },
    {
        "product_name": "Ordinateur Portable Dell XPS 15",
        "product_description": "Dell XPS 15 9530, Intel Core i7-13700H, 16GB RAM, 512GB SSD, RTX 4050, écran 15.6' OLED 3.5K. État neuf, sous garantie constructeur 2 ans. Idéal pour professionnels et créatifs.",
        "product_category": "Électronique",
        "product_price": 16500.00,
        "product_images": ["https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400"],
        "ai_decision": "approved",
        "ai_confidence": 0.94,
        "ai_risk_level": "low",
        "ai_flags": [],
        "ai_reason": "Produit légitime avec description technique détaillée. Prix cohérent avec le marché marocain (Dell XPS 15 neuf). Spécifications précises et vérifiables. Mention de garantie constructeur renforce la crédibilité.",
        "ai_recommendation": "Approuver - Produit conforme et description professionnelle"
    },
    {
        "product_name": "Sac à Main Guess - Collection 2025",
        "product_description": "Nouveau sac à main Guess de la collection printemps 2025. Design élégant et moderne. Cuir synthétique de qualité, plusieurs compartiments. Livraison rapide.",
        "product_category": "Accessoires",
        "product_price": 650.00,
        "product_images": ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"],
        "ai_decision": "approved",
        "ai_confidence": 0.81,
        "ai_risk_level": "low",
        "ai_flags": [],
        "ai_reason": "Accessoire de mode marque moyenne gamme. Prix raisonnable et cohérent. Description honnête (mentionne 'cuir synthétique'). Risque faible.",
        "ai_recommendation": "Approuver - Produit standard conforme"
    },
    {
        "product_name": "Console PlayStation 5 + Jeux",
        "product_description": "PS5 édition standard (lecteur disque) avec 3 jeux: FIFA 24, Spider-Man 2, God of War Ragnarök. Console en excellent état, achetée il y a 6 mois. Facture disponible.",
        "product_category": "Électronique",
        "product_price": 5200.00,
        "product_images": ["https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400"],
        "ai_decision": "approved",
        "ai_confidence": 0.86,
        "ai_risk_level": "low",
        "ai_flags": [],
        "ai_reason": "Bundle console + jeux d'occasion. Prix légèrement sous le marché mais raisonnable pour de l'occasion 6 mois. Mention de facture disponible est un bon signal. Produit crédible.",
        "ai_recommendation": "Approuver - Prix et description cohérents"
    },
    {
        "product_name": "Nike Air Jordan 1 Retro High - Édition Limitée",
        "product_description": "Baskets Nike Air Jordan 1 Retro High OG 'Chicago Lost & Found'. Neuves, jamais portées. Taille 42 EU. Box d'origine avec tous les accessoires. Pièce collector rare!",
        "product_category": "Chaussures",
        "product_price": 3800.00,
        "product_images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"],
        "ai_decision": "rejected",
        "ai_confidence": 0.78,
        "ai_risk_level": "high",
        "ai_flags": ["edition_limitee", "marque_contrefaite_frequente", "verification_authenticite"],
        "ai_reason": "Sneakers édition limitée très recherchées. Marché saturé de contrefaçons de haute qualité pour ce modèle. Prix élevé mais cohérent avec le marché resell. Nécessite vérification authentification (photo tag, numéro série, code-barres box).",
        "ai_recommendation": "Révision manuelle - Vérifier authenticité via photos détaillées"
    }
]

async def create_moderation_products():
    """Crée des produits de test dans la queue de modération"""
    
    logger.info("\n" + "="*60)
    logger.info("🔍 CRÉATION DE PRODUITS EN MODÉRATION")
    logger.info("="*60 + "\n")
    
    # 1. Récupérer les merchants disponibles
    try:
        merchants_response = supabase.table("merchants").select("id, company_name, user_id").limit(5).execute()
        merchants = merchants_response.data
        
        if not merchants:
            logger.info("❌ Aucun merchant trouvé dans la base de données")
            return
        
        logger.info(f"✅ {len(merchants)} merchants trouvés\n")
        
    except Exception as e:
        logger.info(f"❌ Erreur lors de la récupération des merchants: {e}")
        return
    
    # 2. Créer les produits dans la queue de modération
    created_count = 0
    
    for i, product in enumerate(test_products):
        # Assigner un merchant en rotation
        merchant = merchants[i % len(merchants)]
        
        try:
            # Préparer les données
            moderation_data = {
                "merchant_id": merchant["id"],
                "user_id": merchant["user_id"],
                "product_name": product["product_name"],
                "product_description": product["product_description"],
                "product_category": product["product_category"],
                "product_price": product["product_price"],
                "product_images": product["product_images"],
                "status": "pending",  # Tous en attente de révision admin
                "ai_decision": product["ai_decision"],
                "ai_confidence": product["ai_confidence"],
                "ai_risk_level": product["ai_risk_level"],
                "ai_flags": product["ai_flags"],
                "ai_reason": product["ai_reason"],
                "ai_recommendation": product["ai_recommendation"],
                "moderation_method": "ai",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insérer dans moderation_queue
            response = supabase.table("moderation_queue").insert(moderation_data).execute()
            
            # Afficher avec emoji selon risque
            risk_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }
            
            emoji = risk_emoji.get(product["ai_risk_level"], "⚪")
            status_text = "APPROVED ✓" if product["ai_decision"] == "approved" else "REJECTED ✗"
            
            logger.info(f"{emoji} {product['product_name'][:50]}")
            logger.info(f"   Prix: {product['product_price']:.2f} MAD | Risque: {product['ai_risk_level'].upper()}")
            logger.info(f"   Décision IA: {status_text} (confiance: {product['ai_confidence']:.0%})")
            logger.info(f"   Merchant: {merchant['company_name']}\n")
            
            created_count += 1
            
        except Exception as e:
            logger.info(f"❌ Erreur lors de la création du produit '{product['product_name']}': {e}\n")
            continue
    
    # 3. Récapitulatif
    logger.info("="*60)
    logger.info(f"✅ {created_count}/{len(test_products)} PRODUITS CRÉÉS EN MODÉRATION!")
    logger.info("="*60 + "\n")
    
    # Compter par niveau de risque
    risk_counts = {}
    for product in test_products[:created_count]:
        risk = product["ai_risk_level"]
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    logger.info("📊 RÉPARTITION PAR NIVEAU DE RISQUE:")
    logger.error(f"   🔴 Critical: {risk_counts.get('critical', 0)}")
    logger.info(f"   🟠 High: {risk_counts.get('high', 0)}")
    logger.info(f"   🟡 Medium: {risk_counts.get('medium', 0)}")
    logger.info(f"   🟢 Low: {risk_counts.get('low', 0)}")
    
    logger.info(f"\n🌐 Accédez à: http://localhost:3000/admin/moderation")
    logger.info(f"📝 Rafraîchissez la page pour voir les produits en attente!\n")
    logger.info("="*60)

if __name__ == "__main__":
    asyncio.run(create_moderation_products())
