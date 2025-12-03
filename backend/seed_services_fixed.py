#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour créer des services de démonstration - VERSION CORRIGÉE"""

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    print("=" * 70)
    print("CRÉATION DE SERVICES DE DÉMONSTRATION")
    print("=" * 70)
    
    # Services avec la bonne structure de la table
    services_demo = [
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Gestion de Campagne Instagram",
            "description": "Service complet de gestion de campagnes Instagram incluant création de contenu, analyse performances et optimisation.",
            "category": "Marketing Digital",
            "price_per_lead": 250.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 20,
            "tags": '["instagram", "social media", "marketing"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Création de Contenu TikTok",
            "description": "Production de vidéos TikTok professionnelles avec montage, musique et effets pour maximiser engagement.",
            "category": "Création de Contenu",
            "price_per_lead": 180.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 30,
            "tags": '["tiktok", "video", "content"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Stratégie Influence Marketing",
            "description": "Développement stratégie complète d'influence marketing incluant identification influenceurs et gestion partenariats.",
            "category": "Consulting",
            "price_per_lead": 350.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 10,
            "tags": '["influence", "stratégie", "consulting"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Audit de Présence Digitale",
            "description": "Analyse complète de présence en ligne avec recommandations stratégiques et plan d'action détaillé.",
            "category": "Audit",
            "price_per_lead": 150.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 25,
            "tags": '["audit", "digital", "analyse"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Pack Animation Réseaux Sociaux",
            "description": "Animation quotidienne réseaux sociaux avec publication contenu, interaction communauté et reporting mensuel.",
            "category": "Community Management",
            "price_per_lead": 200.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 15,
            "tags": '["social media", "community", "animation"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Formation Marketing d'Influence",
            "description": "Formation complète sur marketing d'influence pour équipes marketing : stratégies, outils et best practices.",
            "category": "Formation",
            "price_per_lead": 450.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 8,
            "tags": '["formation", "marketing", "influence"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Shooting Photo Produits",
            "description": "Séance photo professionnelle produits avec retouches et optimisation pour e-commerce et réseaux sociaux.",
            "category": "Production Visuelle",
            "price_per_lead": 120.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 40,
            "tags": '["photo", "produits", "visuel"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Campagne Facebook Ads",
            "description": "Création et gestion campagnes publicitaires Facebook Ads optimisées pour conversion avec suivi KPIs.",
            "category": "Publicité Digitale",
            "price_per_lead": 280.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 12,
            "tags": '["facebook", "ads", "publicité"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Optimisation SEO E-commerce",
            "description": "Optimisation complète référencement naturel boutique en ligne pour améliorer visibilité sur Google.",
            "category": "SEO",
            "price_per_lead": 320.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 10,
            "tags": '["seo", "ecommerce", "référencement"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Analyse Performance Marketing",
            "description": "Tableau de bord personnalisé avec analyse performances marketing, ROI et recommandations optimisation.",
            "category": "Analytics",
            "price_per_lead": 190.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 20,
            "tags": '["analytics", "performance", "roi"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Design Identité de Marque",
            "description": "Création complète identité visuelle marque : logo, charte graphique, templates réseaux sociaux.",
            "category": "Design",
            "price_per_lead": 500.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 5,
            "tags": '["design", "branding", "identité"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Partenariat Micro-Influenceurs",
            "description": "Identification et mise en place partenariats avec micro-influenceurs ciblés pour votre marque.",
            "category": "Partenariats",
            "price_per_lead": 420.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 8,
            "tags": '["influenceurs", "partenariats", "micro"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Création Site Web Vitrine",
            "description": "Développement site web vitrine moderne et responsive avec hébergement et maintenance inclus.",
            "category": "Développement Web",
            "price_per_lead": 650.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 3,
            "tags": '["web", "développement", "site"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Email Marketing Automatisé",
            "description": "Mise en place campagnes email marketing automatisées avec segmentation et personnalisation avancée.",
            "category": "Email Marketing",
            "price_per_lead": 230.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 15,
            "tags": '["email", "marketing", "automation"]'
        },
        {
            "merchant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Live Shopping Experience",
            "description": "Organisation et animation sessions live shopping sur Instagram et TikTok avec promotion et suivi ventes.",
            "category": "Live Commerce",
            "price_per_lead": 380.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 6,
            "tags": '["live", "shopping", "ecommerce"]'
        }
    ]
    
    try:
        print(f"\n📤 Insertion de {len(services_demo)} services...")
        
        for service in services_demo:
            result = supabase.table('services').insert(service).execute()
            print(f"  ✅ Service créé: {service['name']}")
        
        print(f"\n✅ SUCCÈS: {len(services_demo)} services créés!")
        
        # Vérification
        print("\n🔍 Vérification...")
        count_result = supabase.table('services').select('id', count='exact', head=True).execute()
        print(f"✅ Total services dans la BD: {count_result.count}")
        
        print("\n📋 Quelques services créés:")
        services_list = supabase.table('services').select('name, category, price_per_lead').limit(5).execute()
        for svc in services_list.data:
            print(f"  - {svc['name']}: {svc['price_per_lead']} MAD/lead ({svc['category']})")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
