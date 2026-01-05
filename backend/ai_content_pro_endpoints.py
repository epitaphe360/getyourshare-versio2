"""
🚀 API Endpoints pour AI Content Generator PRO
Routes FastAPI pour génération de contenu professionnel
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from services.ai_content_generator_pro import (
    AIContentGeneratorPro,
    ContentRequest,
    GeneratedContent,
    ContentType,
    ToneVoice,
    ContentLength,
    ai_generator_pro
)

router = APIRouter(prefix="/api/ai-content-pro", tags=["AI Content Generator PRO"])


@router.post("/generate", response_model=GeneratedContent)
async def generate_professional_content(
    request: ContentRequest,
    use_claude: bool = False
):
    """
    🎨 Génère du contenu professionnel avec IA

    Fonctionnalités:
    - GPT-4 Turbo ou Claude 3.5 Sonnet
    - 3-5 variantes de contenu
    - Scoring SEO, lisibilité, engagement
    - Suggestions d'amélioration
    - Optimisation automatique

    Args:
        request: Paramètres de génération
        use_claude: Utiliser Claude au lieu de GPT-4

    Returns:
        Contenu généré avec métriques et recommandations

    Example:
        ```json
        {
          "content_type": "social_post",
          "topic": "Lancement nouveau produit écologique",
          "keywords": ["écologie", "innovation", "durable"],
          "tone": "inspirational",
          "length": "medium",
          "target_audience": "millennials écolos",
          "language": "fr",
          "num_variants": 3,
          "seo_optimize": true
        }
        ```
    """
    try:
        result = await ai_generator_pro.generate_content(request, use_claude=use_claude)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@router.get("/content-types")
async def get_content_types():
    """
    📋 Liste tous les types de contenu disponibles

    Returns:
        Liste des types de contenu avec descriptions
    """
    content_types = [
        {
            "value": "social_post",
            "label": "Publication Réseaux Sociaux",
            "description": "Posts Instagram, Facebook, LinkedIn, Twitter",
            "icon": "📱",
            "platforms": ["Instagram", "Facebook", "LinkedIn", "Twitter", "TikTok"]
        },
        {
            "value": "product_description",
            "label": "Description Produit",
            "description": "Descriptions e-commerce optimisées conversion",
            "icon": "🛍️",
            "best_for": "E-commerce, marketplaces"
        },
        {
            "value": "blog_article",
            "label": "Article de Blog",
            "description": "Articles SEO optimisés 500-2000 mots",
            "icon": "📝",
            "best_for": "Content marketing, SEO"
        },
        {
            "value": "email_marketing",
            "label": "Email Marketing",
            "description": "Emails promotionnels, newsletters",
            "icon": "📧",
            "best_for": "Campagnes email, automation"
        },
        {
            "value": "ad_copy",
            "label": "Publicité (Ad Copy)",
            "description": "Google Ads, Facebook Ads, annonces",
            "icon": "📢",
            "best_for": "Publicité payante, PPC"
        },
        {
            "value": "video_script",
            "label": "Script Vidéo",
            "description": "Scripts YouTube, TikTok, Reels",
            "icon": "🎥",
            "best_for": "Vidéos courtes, tutoriels"
        },
        {
            "value": "landing_page",
            "label": "Page de Destination",
            "description": "Copy de landing page conversion",
            "icon": "🌐",
            "best_for": "Lead generation, ventes"
        },
        {
            "value": "seo_meta",
            "label": "Méta SEO",
            "description": "Titres et descriptions SEO",
            "icon": "🔍",
            "best_for": "Optimisation moteurs recherche"
        },
        {
            "value": "press_release",
            "label": "Communiqué de Presse",
            "description": "Annonces médias professionnelles",
            "icon": "📰",
            "best_for": "Relations publiques"
        },
        {
            "value": "sales_letter",
            "label": "Lettre de Vente",
            "description": "Long-form sales copy",
            "icon": "💰",
            "best_for": "Ventes directes, webinaires"
        }
    ]

    return {
        "content_types": content_types,
        "total": len(content_types)
    }


@router.get("/tones")
async def get_available_tones():
    """
    🎭 Liste tous les tons de voix disponibles

    Returns:
        Liste des tons avec descriptions et cas d'usage
    """
    tones = [
        {
            "value": "professional",
            "label": "Professionnel",
            "description": "Formel, crédible, autoritaire",
            "icon": "👔",
            "best_for": "B2B, services professionnels, finance",
            "example": "Nos solutions innovantes permettent d'optimiser vos processus métier."
        },
        {
            "value": "casual",
            "label": "Décontracté",
            "description": "Relaxé, conversationnel, accessible",
            "icon": "😊",
            "best_for": "Lifestyle, mode, technologie grand public",
            "example": "Hey ! On a quelque chose de cool à te montrer."
        },
        {
            "value": "friendly",
            "label": "Amical",
            "description": "Chaleureux, accueillant, personnel",
            "icon": "🤗",
            "best_for": "Services client, communauté, éducation",
            "example": "On est super contents de t'aider à réussir !"
        },
        {
            "value": "luxury",
            "label": "Luxe",
            "description": "Sophistiqué, premium, exclusif",
            "icon": "💎",
            "best_for": "Marques haut de gamme, joaillerie, immobilier luxe",
            "example": "Découvrez l'excellence à l'état pur."
        },
        {
            "value": "playful",
            "label": "Joueur",
            "description": "Fun, énergique, léger",
            "icon": "🎉",
            "best_for": "Jeune public, gaming, divertissement",
            "example": "Prêt à vivre une aventure incroyable ? C'est parti ! 🚀"
        },
        {
            "value": "authoritative",
            "label": "Autoritaire",
            "description": "Expert, confiant, leader",
            "icon": "🎯",
            "best_for": "Thought leadership, consulting, formation",
            "example": "Voici la stratégie éprouvée que les leaders utilisent."
        },
        {
            "value": "empathetic",
            "label": "Empathique",
            "description": "Compréhensif, compatissant, soutien",
            "icon": "❤️",
            "best_for": "Santé, bien-être, services sociaux",
            "example": "On comprend vos défis, et on est là pour vous aider."
        },
        {
            "value": "witty",
            "label": "Spirituel",
            "description": "Intelligent, humoristique, divertissant",
            "icon": "😄",
            "best_for": "Marketing créatif, startups, médias",
            "example": "Qui a dit que [industrie] devait être ennuyeux ?"
        },
        {
            "value": "inspirational",
            "label": "Inspirant",
            "description": "Motivant, édifiant, encourageant",
            "icon": "✨",
            "best_for": "Coaching, développement personnel, fitness",
            "example": "Votre succès commence aujourd'hui. Osez rêver grand !"
        },
        {
            "value": "educational",
            "label": "Éducatif",
            "description": "Informatif, clair, instructif",
            "icon": "📚",
            "best_for": "Formations, tutoriels, guides",
            "example": "Voici comment maîtriser [compétence] en 5 étapes simples."
        }
    ]

    return {
        "tones": tones,
        "total": len(tones),
        "recommendation": "Choisissez le ton qui correspond le mieux à votre marque et audience"
    }


@router.get("/templates/{content_type}")
async def get_content_templates(content_type: ContentType):
    """
    📑 Récupère les templates pour un type de contenu

    Args:
        content_type: Type de contenu

    Returns:
        Templates et frameworks disponibles
    """
    templates_data = {
        ContentType.SOCIAL_POST: {
            "frameworks": [
                {
                    "name": "Problem → Solution → CTA",
                    "description": "Identifie un problème, propose une solution, appel à l'action",
                    "example": "Vous perdez du temps avec X ? Notre solution Y permet de Z. Commencez maintenant !"
                },
                {
                    "name": "Question → Answer → Benefit",
                    "description": "Pose une question engageante, répond, montre le bénéfice",
                    "example": "Comment doubler votre productivité ? En automatisant X. Résultat: +2h par jour."
                },
                {
                    "name": "Story → Lesson → Action",
                    "description": "Raconte une histoire, extrait une leçon, incite à l'action",
                    "example": "Client X avait ce défi. Il a appris Y. Voici comment vous pouvez faire pareil..."
                },
                {
                    "name": "Stat → Insight → Invitation",
                    "description": "Donnée chiffrée, insight, invitation à en savoir plus",
                    "example": "85% des entreprises échouent à X. Voici pourquoi, et comment l'éviter..."
                }
            ],
            "hook_types": [
                "Question provocatrice",
                "Statistique surprenante",
                "Citation inspirante",
                "Défi ou teaser",
                "Fait contre-intuitif"
            ]
        },
        ContentType.PRODUCT_DESCRIPTION: {
            "frameworks": [
                {
                    "name": "FAB (Features, Advantages, Benefits)",
                    "description": "Caractéristiques → Avantages → Bénéfices clients",
                    "structure": "1. Ce que c'est, 2. Comment ça marche, 3. Ce que ça vous apporte"
                },
                {
                    "name": "AIDA (Attention, Interest, Desire, Action)",
                    "description": "Captez l'attention, créez l'intérêt, suscitez le désir, appelez à l'action",
                    "structure": "Accroche → Détails intéressants → Bénéfices désirables → CTA"
                },
                {
                    "name": "PAS (Problem, Agitate, Solution)",
                    "description": "Problème, amplification du problème, solution proposée",
                    "structure": "Douleur client → Aggravation → Votre produit comme solution"
                }
            ]
        },
        ContentType.EMAIL_MARKETING: {
            "subject_formulas": [
                "[Emoji] {Bénéfice} pour {Audience}",
                "Question rapide sur {Sujet}...",
                "{Nombre} {Délai} pour {Résultat}",
                "Vous êtes invité: {Événement/Offre}",
                "Dernière chance: {Deadline} pour {Offre}"
            ],
            "structures": [
                "Salutation personnalisée → Proposition de valeur → CTA",
                "Curiosité hook → Histoire → Offre → CTA",
                "Preuve sociale → Bénéfices → Temps limité → CTA"
            ]
        }
    }

    if content_type not in templates_data:
        return {
            "templates": [],
            "message": f"Pas de templates spécifiques pour {content_type.value}"
        }

    return {
        "content_type": content_type.value,
        "templates": templates_data[content_type]
    }


@router.post("/optimize")
async def optimize_existing_content(
    content: str,
    content_type: ContentType,
    optimization_goals: List[str] = ["seo", "readability", "engagement"]
):
    """
    ⚡ Optimise du contenu existant

    Args:
        content: Contenu à optimiser
        content_type: Type de contenu
        optimization_goals: Objectifs d'optimisation

    Returns:
        Version optimisée avec suggestions
    """
    # Cette fonctionnalité nécessiterait une intégration GPT-4
    # Pour l'instant, retourner des suggestions basiques

    suggestions = []

    content_lower = content.lower()
    word_count = len(content.split())

    # Suggestions SEO
    if "seo" in optimization_goals:
        if word_count < 300:
            suggestions.append("📝 Augmentez la longueur à 300+ mots pour un meilleur SEO")
        if "?" not in content:
            suggestions.append("❓ Ajoutez une question pour améliorer l'engagement")

    # Suggestions lisibilité
    if "readability" in optimization_goals:
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        if avg_sentence_length > 20:
            suggestions.append("✂️ Raccourcissez vos phrases (moyenne actuelle: {:.0f} mots)".format(avg_sentence_length))

    # Suggestions engagement
    if "engagement" in optimization_goals:
        if not any(cta in content_lower for cta in ["cliquez", "découvrez", "rejoignez", "achetez"]):
            suggestions.append("📣 Ajoutez un appel à l'action clair")
        emoji_count = sum(1 for char in content if ord(char) > 127000)
        if emoji_count == 0 and content_type == ContentType.SOCIAL_POST:
            suggestions.append("😊 Ajoutez 2-3 emojis pour augmenter l'engagement")

    return {
        "original_content": content,
        "suggestions": suggestions,
        "optimization_score": len(suggestions) == 0 and 100 or max(50, 100 - len(suggestions) * 10),
        "next_steps": [
            "Appliquez les suggestions ci-dessus",
            "Testez avec A/B testing",
            "Mesurez les résultats"
        ]
    }


@router.get("/usage-stats")
async def get_usage_statistics():
    """
    📊 Statistiques d'utilisation du générateur

    Returns:
        Métriques d'usage et quotas
    """
    # Cette fonctionnalité nécessiterait une vraie DB pour tracker l'usage
    # Pour l'instant, retourner des données mock

    return {
        "usage": {
            "this_month": 127,
            "limit": 1000,
            "percentage_used": 12.7
        },
        "most_used_types": [
            {"type": "social_post", "count": 45},
            {"type": "product_description", "count": 32},
            {"type": "email_marketing", "count": 28},
            {"type": "ad_copy", "count": 22}
        ],
        "avg_generation_time": 2.3,  # seconds
        "success_rate": 98.5,  # percentage
        "recommendations": [
            "Vous utilisez 12.7% de votre quota mensuel",
            "Les posts réseaux sociaux sont votre type le plus fréquent",
            "Temps de génération moyen: 2.3 secondes"
        ]
    }


@router.get("/best-practices/{content_type}")
async def get_best_practices(content_type: ContentType):
    """
    💡 Bonnes pratiques pour un type de contenu

    Args:
        content_type: Type de contenu

    Returns:
        Liste de bonnes pratiques et conseils d'experts
    """
    best_practices = {
        ContentType.SOCIAL_POST: [
            "📱 Commencez fort: les 3 premières secondes sont critiques",
            "❓ Posez des questions pour encourager les commentaires",
            "🎯 Un post = une idée principale",
            "🖼️ Toujours inclure un visuel accrocheur",
            "⏰ Meilleurs moments: 9h-11h et 18h-21h en semaine",
            "#️⃣ 5-10 hashtags max, mix de populaires et niche",
            "💬 Répondez aux commentaires dans les 60 premières minutes",
            "📊 Analysez les insights et ajustez votre stratégie"
        ],
        ContentType.PRODUCT_DESCRIPTION: [
            "✨ Commencez par le bénéfice principal, pas les caractéristiques",
            "📏 Longueur idéale: 150-300 mots pour produits simples",
            "🎯 Utilisez des bullet points pour scanner facilement",
            "💭 Adressez les objections courantes",
            "📸 Décrivez le produit comme si le client ne voyait pas l'image",
            "🔍 Incluez mots-clés SEO naturellement",
            "⚡ Terminez avec urgence ou exclusivité",
            "📱 Pensez mobile-first (60% achètent sur mobile)"
        ],
        ContentType.EMAIL_MARKETING: [
            "📧 Sujet: 6-10 mots, évitez SPAM words",
            "👤 Personnalisez (prénom, intérêts, historique)",
            "📱 Design responsive (50%+ ouvrent sur mobile)",
            "🎯 Un email = un objectif = un CTA",
            "⏰ Envoyez mardi-jeudi, 10h ou 14h",
            "A/B testez toujours (sujet, CTA, timing)",
            "📊 Taux d'ouverture cible: >20%, clic: >2.5%",
            "✅ Respectez RGPD: lien désabonnement visible"
        ],
        ContentType.BLOG_ARTICLE: [
            "🎯 Titre accrocheur avec mot-clé principal",
            "📊 H1 unique, H2-H3 pour structure",
            "📏 Longueur optimale SEO: 1500-2500 mots",
            "🖼️ Images optimisées avec alt text",
            "🔗 Liens internes (3-5) et externes (2-3)",
            "📱 Paragraphes courts (3-4 lignes max)",
            "💡 Conclusion avec CTA clair",
            "🔍 Meta description unique 150-160 caractères"
        ],
        ContentType.AD_COPY: [
            "⚡ Hook puissant dans les 3 premiers mots",
            "🎯 Bénéfice clair et immédiat",
            "📊 Chiffres et stats si possible",
            "🚀 Urgence ou rareté",
            "✅ CTA explicite et action-oriented",
            "📏 Google Ads: 30 chars titre, 90 description",
            "🎨 Facebook: image = 80% du succès",
            "💰 ROI: testez 3-5 variantes minimum"
        ],
        ContentType.VIDEO_SCRIPT: [
            "🎬 Hook dans les 3 premières secondes",
            "📱 Format vertical pour TikTok/Reels",
            "⏱️ Durée idéale: 15-60 secondes",
            "🗣️ Parlez naturellement, pas de jargon",
            "🎯 Structure: Problem → Solution → CTA",
            "📝 Sous-titres obligatoires (85% sans son)",
            "🎵 Musique trending pour algorithme",
            "💬 Question finale pour commentaires"
        ]
    }

    practices = best_practices.get(content_type, [
        "Soyez authentique et cohérent avec votre marque",
        "Connaissez votre audience cible",
        "Testez et optimisez en continu",
        "Mesurez les résultats et ajustez"
    ])

    return {
        "content_type": content_type.value,
        "best_practices": practices,
        "total": len(practices)
    }
