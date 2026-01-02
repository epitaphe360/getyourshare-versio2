#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour créer des services de démonstration"""

import os
import uuid
from datetime import datetime
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
    
    # Services de marketplace pour marchands
    services_demo = [
        {
            "id": str(uuid.uuid4()),
            "merchant_id": "22222222-2222-2222-2222-222222222222",  # Merchant existant
            "name": "Gestion de Campagne Instagram",
            "description": "Service complet de gestion de campagnes Instagram incluant la création de contenu, l'analyse des performances et l'optimisation.",
            "category": "Marketing Digital",
            "price_per_lead": 2500.00,
            "currency": "MAD",
            "is_available": True,
            "capacity_per_month": 10
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Création de Contenu TikTok",
            "description": "Production de vidéos TikTok professionnelles avec montage, musique et effets pour maximiser l'engagement.",
            "type": "Création de Contenu",
            "tarif": 1800.00,
            "duree": "5 vidéos",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Stratégie Influence Marketing",
            "description": "Développement d'une stratégie complète d'influence marketing incluant l'identification des influenceurs et la gestion des partenariats.",
            "type": "Consulting",
            "tarif": 3500.00,
            "duree": "2 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Audit de Présence Digitale",
            "description": "Analyse complète de la présence en ligne de votre marque avec recommandations stratégiques et plan d'action.",
            "type": "Audit",
            "tarif": 1500.00,
            "duree": "2 semaines",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Pack Animation Réseaux Sociaux",
            "description": "Animation quotidienne de vos réseaux sociaux avec publication de contenu, interaction avec la communauté et reporting mensuel.",
            "type": "Community Management",
            "tarif": 2000.00,
            "duree": "1 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Formation Marketing d'Influence",
            "description": "Formation complète sur le marketing d'influence pour les équipes marketing : stratégies, outils et best practices.",
            "type": "Formation",
            "tarif": 4500.00,
            "duree": "3 jours",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Shooting Photo Produits",
            "description": "Séance photo professionnelle pour vos produits avec retouches et optimisation pour e-commerce et réseaux sociaux.",
            "type": "Production Visuelle",
            "tarif": 1200.00,
            "duree": "1 journée",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Campagne Publicité Facebook Ads",
            "description": "Création et gestion de campagnes publicitaires Facebook Ads optimisées pour la conversion avec suivi des KPIs.",
            "type": "Publicité Digitale",
            "tarif": 2800.00,
            "duree": "1 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Optimisation SEO E-commerce",
            "description": "Optimisation complète du référencement naturel de votre boutique en ligne pour améliorer la visibilité sur Google.",
            "type": "SEO",
            "tarif": 3200.00,
            "duree": "3 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Analyse de Performance Marketing",
            "description": "Tableau de bord personnalisé avec analyse des performances marketing, ROI et recommandations d'optimisation.",
            "type": "Analytics",
            "tarif": 1900.00,
            "duree": "Configuration + 1 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Design Identité de Marque",
            "description": "Création complète de l'identité visuelle de votre marque : logo, charte graphique, templates réseaux sociaux.",
            "type": "Design",
            "tarif": 5000.00,
            "duree": "1 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Partenariat Micro-Influenceurs",
            "description": "Identification et mise en place de partenariats avec 10 micro-influenceurs ciblés pour votre marque.",
            "type": "Partenariats",
            "tarif": 4200.00,
            "duree": "2 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Création Site Web Vitrine",
            "description": "Développement d'un site web vitrine moderne et responsive avec hébergement et maintenance inclus pour 1 an.",
            "type": "Développement Web",
            "tarif": 6500.00,
            "duree": "6 semaines",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Email Marketing Automatisé",
            "description": "Mise en place de campagnes d'email marketing automatisées avec segmentation et personnalisation avancée.",
            "type": "Email Marketing",
            "tarif": 2300.00,
            "duree": "Setup + 1 mois",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nom": "Live Shopping Experience",
            "description": "Organisation et animation de sessions de live shopping sur Instagram et TikTok avec promotion et suivi des ventes.",
            "type": "Live Commerce",
            "tarif": 3800.00,
            "duree": "4 sessions",
            "statut": "actif",
            "commercial_id": "33333333-3333-3333-3333-333333333333",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    ]
    
    try:
        # Insérer les services
        print(f"\n📤 Insertion de {len(services_demo)} services...")
        
        for service in services_demo:
            result = supabase.table('services').insert(service).execute()
            print(f"  ✅ Service créé: {service['nom']}")
        
        print(f"\n✅ SUCCÈS: {len(services_demo)} services créés avec succès!")
        
        # Vérification
        print("\n🔍 Vérification...")
        count_result = supabase.table('services').select('id', count='exact', head=True).execute()
        print(f"✅ Total de services dans la BD: {count_result.count}")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
