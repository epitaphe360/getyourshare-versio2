"""
AI Content Generator Service
Génère du contenu optimisé pour TikTok, Instagram, YouTube Shorts, etc.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import os
import httpx
from enum import Enum
from utils.logger import logger

# ============================================
# MODELS
# ============================================

class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE_SHORTS = "youtube_shorts"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    EMAIL = "email"
    BLOG = "blog"

class ContentType(str, Enum):
    VIDEO_SCRIPT = "video_script"
    CAROUSEL = "carousel"
    STORY = "story"
    POST_CAPTION = "post_caption"
    REEL_SCRIPT = "reel_script"
    EMAIL_NEWSLETTER = "email_newsletter"
    BLOG_ARTICLE = "blog_article"

class TrendingTopic(BaseModel):
    keyword: str
    volume: int
    region: str = "MA"  # Morocco by default
    category: str

class ContentRequest(BaseModel):
    platform: SocialPlatform
    content_type: ContentType
    product_name: str
    product_description: str
    target_audience: str
    tone: str = "engaging"  # engaging, professional, funny, inspiring
    language: str = "fr"  # fr, ar, en, es
    include_trends: bool = True
    duration_seconds: Optional[int] = None  # Pour les vidéos
    emoji_intensity: str = "standard" # none, minimal, standard, heavy
    hashtag_strategy: str = "mixed" # niche, broad, mixed
    content_length: str = "medium" # short, medium, long

class GeneratedContent(BaseModel):
    platform: SocialPlatform
    content_type: ContentType
    script: str
    hooks: List[str]  # Phrases d'accroche
    hashtags: List[str]
    call_to_action: str
    estimated_engagement: float  # Prediction d'engagement 0-100
    trending_keywords: List[str]
    best_posting_time: str
    tips: List[str]
    created_at: datetime = datetime.now()

# ============================================
# AI CONTENT GENERATOR SERVICE
# ============================================

class AIContentGeneratorService:
    """Service de génération de contenu IA multi-plateforme"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Trending topics cache (à mettre à jour quotidiennement)
        self.morocco_trending_topics = {
            "fashion": ["jalaba moderne", "caftan 2024", "mode casablanca"],
            "food": ["cuisine marocaine", "pastilla", "tajine"],
            "tech": ["maroc tech", "startup maroc", "digital nomad"],
            "beauty": ["beauté naturelle", "argan oil", "soins maroc"]
        }

    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère du contenu optimisé selon la plateforme"""

        if request.platform == SocialPlatform.TIKTOK:
            return await self._generate_tiktok_content(request)
        elif request.platform == SocialPlatform.INSTAGRAM:
            return await self._generate_instagram_content(request)
        elif request.platform == SocialPlatform.YOUTUBE_SHORTS:
            return await self._generate_youtube_shorts_content(request)
        elif request.platform == SocialPlatform.LINKEDIN:
            return await self._generate_linkedin_content(request)
        elif request.platform == SocialPlatform.EMAIL:
            return await self._generate_email_content(request)
        elif request.platform == SocialPlatform.BLOG:
            return await self._generate_blog_content(request)
        else:
            return await self._generate_generic_content(request)

    async def _generate_tiktok_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère un script TikTok viral avec hooks"""

        # Prompt optimisé pour TikTok
        prompt = f"""
Génère un script TikTok viral en {request.language} pour promouvoir ce produit:

Produit: {request.product_name}
Description: {request.product_description}
Audience: {request.target_audience}
Ton: {request.tone}
Durée: {request.duration_seconds or 30} secondes
Longueur du contenu: {request.content_length}
Intensité Emojis: {request.emoji_intensity}

Le script doit:
1. Commencer avec un HOOK puissant (3 premières secondes)
2. Utiliser des tendances marocaines actuelles
3. Inclure des transitions engageantes
4. Finir avec un CTA fort
5. Être facile à filmer
6. Intégrer du storytelling

Format de réponse:
HOOK (0-3s): [phrase d'accroche qui arrête le scroll]
INTRO (3-10s): [introduction du problème/besoin]
SOLUTION (10-20s): [présentation du produit]
PREUVE (20-25s): [bénéfices/témoignage]
CTA (25-30s): [appel à l'action clair]
"""

        # Appeler l'API IA (OpenAI ou Claude)
        ai_response = await self._call_ai_api(prompt)

        # Parser la réponse et extraire les éléments
        script = ai_response

        # Générer des hashtags optimisés
        hashtags = await self._generate_hashtags(request.product_name, "tiktok", request.language, request.hashtag_strategy)

        # Hooks spécifiques TikTok
        hooks = [
            f"🚨 Vous ne croirez jamais ce que {request.product_name} peut faire...",
            f"POV: Tu découvres {request.product_name} au Maroc 🇲🇦",
            f"Attendez la fin... 😱 #{request.product_name}",
            f"Les Marocains adorent ce produit et voici pourquoi 👇"
        ]

        return GeneratedContent(
            platform=SocialPlatform.TIKTOK,
            content_type=request.content_type,
            script=script,
            hooks=hooks,
            hashtags=hashtags,
            call_to_action=f"🔗 Lien en bio pour obtenir {request.product_name} avec -20% !",
            estimated_engagement=self._predict_engagement(script, "tiktok"),
            trending_keywords=self._get_trending_keywords("MA"),
            best_posting_time="18h-21h (après le travail)",
            tips=[
                "📱 Filme en vertical 9:16",
                "🎵 Utilise un son tendance marocain",
                "💃 Ajoute des sous-titres en darija",
                "⏱️ Les 3 premières secondes sont cruciales",
                "🔥 Poste entre 18h-21h pour max engagement"
            ]
        )

    async def _generate_instagram_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère du contenu Instagram (Reels, Carousel, Stories)"""

        if request.content_type == ContentType.CAROUSEL:
            prompt = f"""
Crée un carousel Instagram de 10 slides pour promouvoir:

Produit: {request.product_name}
Description: {request.product_description}
Audience: {request.target_audience}

Format:
SLIDE 1: Titre accrocheur qui fait swiper
SLIDE 2-8: Un bénéfice par slide (clair et visuel)
SLIDE 9: Preuve sociale / témoignage
SLIDE 10: CTA fort + code promo

Langue: {request.language}
Ton: {request.tone}
Intensité Emojis: {request.emoji_intensity}
"""
        elif request.content_type == ContentType.REEL_SCRIPT:
            prompt = f"""
Crée un script Reel Instagram de 15-30 secondes:

Produit: {request.product_name}
Description: {request.product_description}
Intensité Emojis: {request.emoji_intensity}

Format:
- Hook visuel puissant (0-2s)
- Transformation/Avant-Après (2-15s)
- Bénéfice principal (15-25s)
- CTA + Lien (25-30s)

Inclus des suggestions de transitions et d'effets visuels.
"""
        else:
            prompt = f"""
Crée une caption Instagram engageante pour:

Produit: {request.product_name}
Description: {request.product_description}
Longueur: {request.content_length}
Intensité Emojis: {request.emoji_intensity}

La caption doit:
1. Commencer par une question ou un fait surprenant
2. Raconter une histoire courte
3. Présenter les bénéfices
4. Inclure un CTA
5. Se terminer par une question pour engagement

Max 2200 caractères.
"""

        ai_response = await self._call_ai_api(prompt)
        hashtags = await self._generate_hashtags(request.product_name, "instagram", request.language, request.hashtag_strategy)

        return GeneratedContent(
            platform=SocialPlatform.INSTAGRAM,
            content_type=request.content_type,
            script=ai_response,
            hooks=[
                "Swipe pour découvrir 👉",
                "Ça va vous changer la vie 🤯",
                "Sauvegarde ce post pour plus tard 📌"
            ],
            hashtags=hashtags,
            call_to_action="💬 Tag quelqu'un qui a besoin de voir ça !",
            estimated_engagement=self._predict_engagement(ai_response, "instagram"),
            trending_keywords=self._get_trending_keywords("MA"),
            best_posting_time="12h-14h ou 19h-21h",
            tips=[
                "📸 Utilise des photos haute qualité",
                "🎨 Garde une cohérence visuelle",
                "💬 Réponds aux commentaires dans l'heure",
                "📊 Utilise max 30 hashtags pertinents",
                "✨ Les carrousels ont 3x plus d'engagement"
            ]
        )

    async def _generate_youtube_shorts_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère un script YouTube Shorts optimisé SEO"""

        prompt = f"""
Crée un script YouTube Shorts (60 secondes max):

Produit: {request.product_name}
Description: {request.product_description}
Intensité Emojis: {request.emoji_intensity}

Structure:
- Hook (0-5s): Question provocante
- Problème (5-15s): Douleur de l'audience
- Solution (15-40s): Démo du produit
- Résultat (40-50s): Transformation
- CTA (50-60s): Abonnez-vous + lien description

Inclus:
- Titre SEO optimisé
- Description YouTube avec timestamps
- Tags recommandés
"""

        ai_response = await self._call_ai_api(prompt)
        hashtags = await self._generate_hashtags(request.product_name, "youtube", request.language, request.hashtag_strategy)

        return GeneratedContent(
            platform=SocialPlatform.YOUTUBE_SHORTS,
            content_type=request.content_type,
            script=ai_response,
            hooks=[
                "Vous faites ENCORE cette erreur ? 😱",
                "Voici comment j'ai résolu ce problème en 24h",
                "Personne ne parle de cette astuce..."
            ],
            hashtags=hashtags,
            call_to_action="👇 Lien en description + Code PROMO20",
            estimated_engagement=self._predict_engagement(ai_response, "youtube"),
            trending_keywords=self._get_trending_keywords("MA"),
            best_posting_time="17h-20h",
            tips=[
                "🎬 Vertical 9:16 obligatoire",
                "📝 Titre avec mots-clés SEO",
                "🔔 Demande les abonnements et likes",
                "💬 Pin ton meilleur commentaire",
                "⏱️ Les Shorts de 30-45s performent mieux"
            ]
        )

    async def _generate_linkedin_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère un post LinkedIn professionnel et engageant"""

        prompt = f"""
Crée un post LinkedIn viral pour:

Produit/Service: {request.product_name}
Description: {request.product_description}
Audience Cible: {request.target_audience}
Ton: {request.tone} (mais professionnel)
Longueur: {request.content_length}
Intensité Emojis: {request.emoji_intensity}

Structure:
1. Hook (Question ou Statistique surprenante)
2. Le Problème (Storytelling court)
3. L'Insight/Solution (Valeur ajoutée)
4. Présentation de {request.product_name}
5. Preuve sociale ou Résultat
6. CTA (Question pour engager les commentaires)

Formatage:
- Utilise des sauts de ligne pour aérer
- Utilise des bullet points si nécessaire
- Emojis professionnels (pas trop)
"""

        ai_response = await self._call_ai_api(prompt)
        hashtags = await self._generate_hashtags(request.product_name, "linkedin", request.language, request.hashtag_strategy)

        return GeneratedContent(
            platform=SocialPlatform.LINKEDIN,
            content_type=request.content_type,
            script=ai_response,
            hooks=[
                "J'ai appris une leçon importante aujourd'hui...",
                "Arrêtez de faire cette erreur dans votre business 🛑",
                "Le secret que personne ne vous dit sur..."
            ],
            hashtags=hashtags,
            call_to_action="👇 Dites-moi en commentaire ce que vous en pensez !",
            estimated_engagement=self._predict_engagement(ai_response, "linkedin"),
            trending_keywords=self._get_trending_keywords("MA"),
            best_posting_time="Mardi-Jeudi, 8h-10h",
            tips=[
                "👔 Garde un ton professionnel mais authentique",
                "📝 Les posts longs (storytelling) fonctionnent bien",
                "💬 Réponds à tous les commentaires pour l'algo",
                "🏷️ Tag des personnes pertinentes (avec modération)",
                "📄 Ajoute un PDF/Carrousel pour plus de portée"
            ]
        )

    async def _generate_email_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère un email marketing ou newsletter"""

        prompt = f"""
Rédige un email marketing performant pour:

Produit: {request.product_name}
Description: {request.product_description}
Audience: {request.target_audience}
Ton: {request.tone}
Longueur: {request.content_length}
Intensité Emojis: {request.emoji_intensity}

Éléments requis:
1. Objet (Subject Line) : Court, intrigant, < 50 caractères
2. Preheader : Complément de l'objet
3. Corps de l'email :
   - Salutation personnalisée
   - Hook (Pourquoi je reçois ça ?)
   - Storytelling / Problème
   - Solution ({request.product_name})
   - Bénéfices (Bullet points)
   - CTA Principal (Bouton)
   - P.S. (Urgence ou Bonus)

Langue: {request.language}
"""

        ai_response = await self._call_ai_api(prompt)
        
        return GeneratedContent(
            platform=SocialPlatform.EMAIL,
            content_type=ContentType.EMAIL_NEWSLETTER,
            script=ai_response,
            hooks=["Objet: Vous avez oublié ça ?", "Objet: Invitation exclusive ✉️"],
            hashtags=[],
            call_to_action="Cliquez ici pour profiter de l'offre",
            estimated_engagement=25.0, # Open rate estimé
            trending_keywords=[],
            best_posting_time="Mardi ou Jeudi, 10h",
            tips=[
                "📧 Personnalise avec le prénom",
                "📱 Vérifie l'affichage mobile",
                "A/B Test tes objets",
                "Nettoie ta liste régulièrement"
            ]
        )

    async def _generate_blog_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère un article de blog optimisé SEO"""

        prompt = f"""
Écris un article de blog optimisé SEO pour:

Sujet/Produit: {request.product_name}
Description: {request.product_description}
Audience: {request.target_audience}
Ton: {request.tone}
Longueur: {request.content_length}

Structure SEO:
1. Titre H1 (avec mot-clé principal)
2. Introduction (Hook + Problématique)
3. H2 (Premier sous-titre)
4. Paragraphes
5. H2 (Deuxième sous-titre)
6. Liste à puces
7. H2 (Troisième sous-titre)
8. Conclusion
9. CTA

Mots-clés à inclure: {request.product_name}, avis, prix, bienfaits, Maroc.
Langue: {request.language}
"""

        ai_response = await self._call_ai_api(prompt)
        
        return GeneratedContent(
            platform=SocialPlatform.BLOG,
            content_type=ContentType.BLOG_ARTICLE,
            script=ai_response,
            hooks=[],
            hashtags=[],
            call_to_action="Laissez un commentaire ci-dessous",
            estimated_engagement=15.0, # Temps de lecture / partage
            trending_keywords=self._get_trending_keywords("MA"),
            best_posting_time="Lundi matin",
            tips=[
                "🔍 Utilise des mots-clés longue traîne",
                "🖼️ Ajoute des images avec balises ALT",
                "🔗 Fais des liens internes",
                "📱 Optimise pour la lecture mobile"
            ]
        )

    async def _generate_generic_content(self, request: ContentRequest) -> GeneratedContent:
        """Génère du contenu pour d'autres plateformes"""

        prompt = f"""
Crée du contenu {request.content_type} pour {request.platform}:

Produit: {request.product_name}
Description: {request.product_description}
Audience: {request.target_audience}
Ton: {request.tone}
Langue: {request.language}
"""

        ai_response = await self._call_ai_api(prompt)
        hashtags = await self._generate_hashtags(request.product_name, request.platform, request.language)

        return GeneratedContent(
            platform=request.platform,
            content_type=request.content_type,
            script=ai_response,
            hooks=["Découvrez la nouveauté", "Ne manquez pas cette offre"],
            hashtags=hashtags,
            call_to_action="Cliquez sur le lien pour en savoir plus",
            estimated_engagement=65.0,
            trending_keywords=[],
            best_posting_time="Variable selon la plateforme",
            tips=["Adaptez votre contenu à votre audience"]
        )

    async def _call_ai_api(self, prompt: str) -> str:
        """Appelle l'API IA (OpenAI ou Claude)"""

        # Prioriser Claude si disponible (meilleur pour le contenu créatif)
        if self.anthropic_api_key:
            return await self._call_claude_api(prompt)
        elif self.openai_api_key:
            return await self._call_openai_api(prompt)
        else:
            # Fallback: template simple
            return self._generate_template_content(prompt)

    async def _call_claude_api(self, prompt: str) -> str:
        """Appelle l'API Claude (Anthropic)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 2000,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["content"][0]["text"]
                else:
                    logger.error(f"Claude API Error: {response.status_code}")
                    return self._generate_template_content(prompt)

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return self._generate_template_content(prompt)

    async def _call_openai_api(self, prompt: str) -> str:
        """Appelle l'API OpenAI GPT-4"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4-turbo-preview",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Tu es un expert en marketing digital et création de contenu viral pour les réseaux sociaux, spécialisé dans le marché marocain."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.8
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API Error: {response.status_code}")
                    return self._generate_template_content(prompt)

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._generate_template_content(prompt)

    def _generate_template_content(self, prompt: str) -> str:
        """Template de contenu quand l'API IA n'est pas disponible"""
        return """
🎯 HOOK (0-3s):
"Attendez de voir ça ! 😱"

📖 INTRODUCTION (3-10s):
Vous cherchez une solution pour [problème] ?

💡 SOLUTION (10-20s):
Découvrez [produit] - la solution parfaite qui va transformer votre quotidien.

✨ BÉNÉFICES (20-25s):
✅ Gain de temps
✅ Économies
✅ Résultats garantis

🔥 CTA (25-30s):
Cliquez sur le lien en bio pour profiter de -20% aujourd'hui !
"""

    async def _generate_hashtags(self, product: str, platform: str, language: str, strategy: str = "mixed") -> List[str]:
        """Génère des hashtags pertinents et tendances"""

        base_hashtags = {
            "tiktok": [
                "#MarocTikTok", "#TikTokMaroc", "#FYP", "#ForYou", "#Viral",
                "#Casablanca", "#Rabat", "#Marrakech", "#MarocShopping"
            ],
            "instagram": [
                "#Morocco", "#Maroc", "#MarocStyle", "#InstaMorocco",
                "#MoroccanLife", "#VisitMorocco", "#MoroccoTravel"
            ],
            "youtube": [
                "#Shorts", "#YouTubeShorts", "#Morocco", "#Maroc"
            ],
            "linkedin": [
                "#Maroc", "#BusinessMaroc", "#Entrepreneuriat", "#MarketingDigital", "#Innovation"
            ]
        }

        # Ajouter des hashtags spécifiques au produit
        product_words = product.lower().split()
        product_hashtags = [f"#{word.capitalize()}" for word in product_words if len(word) > 3]

        platform_hashtags = base_hashtags.get(platform, [])
        
        # Stratégie de hashtags
        if strategy == "niche":
            # Focus sur le produit spécifique
            selected_hashtags = product_hashtags + platform_hashtags[:2]
        elif strategy == "broad":
            # Focus sur la portée large
            selected_hashtags = platform_hashtags[:7] + product_hashtags[:1]
        else: # mixed
            # Mélange équilibré
            selected_hashtags = platform_hashtags[:5] + product_hashtags[:3]

        return selected_hashtags[:15]  # Max 15 hashtags

    def _predict_engagement(self, script: str, platform: str) -> float:
        """Prédit le taux d'engagement basé sur le contenu (ML simple)"""

        score = 50.0  # Score de base

        # Facteurs qui augmentent l'engagement
        engagement_boosters = {
            "?": 5,  # Questions
            "!": 3,  # Exclamations
            "😱": 4, "🔥": 4, "💰": 4, "🚨": 5,  # Emojis forts
            "gratuit": 8, "offre": 6, "promo": 7,
            "nouveau": 5, "exclusif": 6, "limité": 7
        }

        script_lower = script.lower()

        for keyword, boost in engagement_boosters.items():
            if keyword in script_lower:
                score += boost

        # Plateforme bonus
        platform_multipliers = {
            "tiktok": 1.2,
            "instagram": 1.1,
            "youtube": 1.15
        }

        score *= platform_multipliers.get(platform, 1.0)

        # Cap à 95 max (100 impossible à garantir)
        return min(score, 95.0)

    def _get_trending_keywords(self, region: str = "MA") -> List[str]:
        """Récupère les mots-clés tendances pour une région"""

        # À remplacer par une vraie API de trending topics
        trending_morocco = [
            "ramadan 2024",
            "coupe afrique",
            "mode marocaine",
            "recettes marocaines",
            "business maroc",
            "tech maroc",
            "startup casablanca"
        ]

        return trending_morocco[:5]

# ============================================
# TRENDING TOPICS ANALYZER
# ============================================

class TrendingTopicsAnalyzer:
    """Analyse les tendances en temps réel pour le Maroc"""

    async def get_morocco_trends(self) -> List[TrendingTopic]:
        """Récupère les tendances marocaines actuelles"""

        # À intégrer avec Google Trends API ou TikTok Trends API
        mock_trends = [
            TrendingTopic(
                keyword="caftan moderne 2024",
                volume=12000,
                region="MA",
                category="fashion"
            ),
            TrendingTopic(
                keyword="business en ligne maroc",
                volume=8500,
                region="MA",
                category="business"
            ),
            TrendingTopic(
                keyword="cuisine marocaine facile",
                volume=15000,
                region="MA",
                category="food"
            )
        ]

        return mock_trends

    async def analyze_content_trend_fit(self, content: str, trends: List[TrendingTopic]) -> float:
        """Analyse si le contenu match avec les tendances (score 0-100)"""

        score = 0
        content_lower = content.lower()

        for trend in trends:
            if trend.keyword.lower() in content_lower:
                score += (trend.volume / 1000)  # Plus le volume est élevé, plus le score augmente

        return min(score, 100.0)
