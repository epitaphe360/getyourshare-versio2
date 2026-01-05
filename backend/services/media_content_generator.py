"""
Service de Génération de Contenu IA pour Médias Sociaux
Support: Instagram, Twitter/X, LinkedIn, Facebook, TikTok
"""

import os
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import openai
from openai import AsyncOpenAI

from models.media_models import (
    PlatformType,
    ToneVoice,
    ContentCategory,
    ContentGenerationRequest,
    BatchContentGenerationRequest,
    GeneratedContent,
    GeneratedContentCreate
)


class MediaContentGeneratorService:
    """
    Service de génération de contenu pour réseaux sociaux
    Utilise OpenAI GPT-4 Turbo pour créer du contenu adapté à chaque plateforme
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            self.has_api_key = True
        else:
            self.client = None
            self.has_api_key = False

    # ============================================
    # PLATFORM-SPECIFIC CONFIGURATIONS
    # ============================================

    PLATFORM_CONFIGS = {
        PlatformType.INSTAGRAM: {
            "max_caption_length": 2200,
            "optimal_caption_length": 125,
            "max_hashtags": 30,
            "optimal_hashtags": 10,
            "supports_emojis": True,
            "supports_links": False,  # Only in bio or stories
            "post_types": ["feed", "story", "reel"],
            "best_times": ["08:00", "12:00", "17:00", "19:00"]
        },
        PlatformType.TWITTER: {
            "max_length": 280,
            "optimal_length": 240,
            "max_hashtags": 3,
            "optimal_hashtags": 2,
            "supports_emojis": True,
            "supports_links": True,
            "post_types": ["tweet", "thread"],
            "best_times": ["08:00", "12:00", "15:00", "18:00"]
        },
        PlatformType.LINKEDIN: {
            "max_length": 3000,
            "optimal_length": 150,
            "max_hashtags": 5,
            "optimal_hashtags": 3,
            "supports_emojis": True,
            "supports_links": True,
            "post_types": ["post", "article"],
            "best_times": ["07:00", "08:00", "12:00", "17:00"]
        },
        PlatformType.FACEBOOK: {
            "max_length": 63206,
            "optimal_length": 250,
            "max_hashtags": 10,
            "optimal_hashtags": 3,
            "supports_emojis": True,
            "supports_links": True,
            "post_types": ["post", "story"],
            "best_times": ["09:00", "13:00", "15:00", "19:00"]
        },
        PlatformType.TIKTOK: {
            "max_caption_length": 2200,
            "optimal_caption_length": 150,
            "max_hashtags": 10,
            "optimal_hashtags": 5,
            "supports_emojis": True,
            "supports_links": True,
            "post_types": ["video"],
            "best_times": ["06:00", "10:00", "19:00", "22:00"]
        }
    }

    # ============================================
    # PROMPT TEMPLATES PAR PLATEFORME
    # ============================================

    PLATFORM_PROMPTS = {
        PlatformType.INSTAGRAM: """
Crée un post Instagram {tone} et engageant.

Sujet: {topic}
Variables: {variables}

Instructions:
- Hook accrocheur dans les premiers 125 caractères
- Structure: Hook court → Développement → CTA
- {emoji_instruction}
- {hashtag_instruction}
- Style visuel et authentique
- Encourage les interactions (likes, commentaires, partages)
- Max {max_length} caractères

Format de réponse:
[Caption complète ici]
""",

        PlatformType.TWITTER: """
Rédige un tweet {tone} et impactant.

Sujet: {topic}
Variables: {variables}

Instructions:
- Hook puissant dès le début
- Message clair et concis
- {emoji_instruction}
- {hashtag_instruction}
- Appel à l'action si pertinent
- Max {max_length} caractères (idéalement 240)

Format de réponse:
[Tweet complet ici]
""",

        PlatformType.LINKEDIN: """
Écris un post LinkedIn {tone} et professionnel.

Sujet: {topic}
Variables: {variables}

Instructions:
- Hook qui capte l'attention des professionnels
- Structure: Problème → Insight → Solution → CTA
- Apporte de la valeur business
- {emoji_instruction}
- {hashtag_instruction}
- Ton expert mais accessible
- Encourage les discussions professionnelles
- Longueur optimale: 150-250 caractères pour le hook, puis développement

Format de réponse:
[Post complet ici]
""",

        PlatformType.FACEBOOK: """
Crée un post Facebook {tone} et conversationnel.

Sujet: {topic}
Variables: {variables}

Instructions:
- Ton authentique et proche de la communauté
- Structure narrative engageante
- {emoji_instruction}
- {hashtag_instruction}
- Termine par une question pour encourager les commentaires
- Crée un sentiment de communauté
- Longueur optimale: 250 caractères

Format de réponse:
[Post complet ici]
""",

        PlatformType.TIKTOK: """
Écris un script TikTok {tone} et créatif.

Sujet: {topic}
Variables: {variables}

Instructions:
- Format: Hook (3 sec) → Contenu principal (15 sec) → CTA (2 sec)
- Langage jeune et dynamique
- {emoji_instruction}
- {hashtag_instruction}
- Encourage les trends et challenges
- Style énergique et rapide
- Max {max_length} caractères

Format de réponse:
[Script complet ici]
"""
    }

    # ============================================
    # TONE MAPPING
    # ============================================

    TONE_DESCRIPTIONS = {
        ToneVoice.PROFESSIONAL: "professionnel et expert",
        ToneVoice.CASUAL: "décontracté et accessible",
        ToneVoice.FRIENDLY: "amical et chaleureux",
        ToneVoice.LUXURY: "luxueux et exclusif",
        ToneVoice.PLAYFUL: "joueur et amusant",
        ToneVoice.AUTHORITATIVE: "autoritaire et confiant",
        ToneVoice.EMPATHETIC: "empathique et compréhensif",
        ToneVoice.WITTY: "spirituel et intelligent",
        ToneVoice.INSPIRATIONAL: "inspirant et motivant",
        ToneVoice.EDUCATIONAL: "éducatif et informatif"
    }

    # ============================================
    # MÉTHODES PRINCIPALES
    # ============================================

    async def generate_content(
        self,
        request: ContentGenerationRequest,
        user_id: int
    ) -> List[GeneratedContent]:
        """
        Génère du contenu pour une plateforme spécifique

        Args:
            request: Requête de génération avec tous les paramètres
            user_id: ID de l'utilisateur

        Returns:
            Liste de contenus générés (1 à 5 variantes)
        """
        try:
            # Construire le prompt
            prompt = await self._build_prompt(request)

            # Générer les variantes
            generated_texts = []
            for i in range(request.num_variants):
                if self.has_api_key:
                    text = await self._generate_with_openai(
                        prompt,
                        request.platform,
                        request.ai_model
                    )
                else:
                    text = await self._generate_with_template(
                        request.platform,
                        request.prompt,
                        request.tone
                    )

                generated_texts.append(text)

            # Créer les objets GeneratedContent
            results = []
            for text in generated_texts:
                # Extraire les hashtags
                hashtags = self._extract_hashtags(text) if request.include_hashtags else []

                # Calculer les scores
                quality_score = self._calculate_quality_score(text, request.platform)
                engagement_prediction = self._predict_engagement(text, request.platform, request.tone)

                content = GeneratedContentCreate(
                    platform=request.platform,
                    prompt=request.prompt,
                    generated_text=text,
                    generated_hashtags=hashtags,
                    tone=request.tone,
                    ai_model=request.ai_model,
                    variables_used=request.variables,
                    quality_score=quality_score,
                    engagement_prediction=engagement_prediction
                )

                # Note: Dans une vraie app, on sauvegarderait en DB ici
                # Pour cet exemple, on retourne juste le modèle
                results.append(content)

            return results

        except Exception as e:
            print(f"Erreur lors de la génération de contenu: {str(e)}")
            raise

    async def generate_batch_content(
        self,
        request: BatchContentGenerationRequest,
        user_id: int
    ) -> Dict[PlatformType, List[GeneratedContent]]:
        """
        Génère du contenu pour plusieurs plateformes simultanément

        Args:
            request: Requête batch avec liste de plateformes
            user_id: ID de l'utilisateur

        Returns:
            Dictionnaire {plateforme: liste de contenus}
        """
        results = {}

        # Générer en parallèle pour toutes les plateformes
        tasks = []
        for platform in request.platforms:
            single_request = ContentGenerationRequest(
                platform=platform,
                prompt=request.base_prompt,
                variables=request.variables,
                tone=request.tone,
                include_hashtags=request.include_hashtags,
                include_emojis=request.include_emojis,
                num_variants=request.num_variants
            )
            tasks.append(self.generate_content(single_request, user_id))

        # Attendre toutes les générations
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Organiser les résultats
        for platform, result in zip(request.platforms, all_results):
            if isinstance(result, Exception):
                print(f"Erreur pour {platform}: {str(result)}")
                results[platform] = []
            else:
                results[platform] = result

        return results

    async def generate_hashtags(
        self,
        content: str,
        platform: PlatformType,
        count: int = 10
    ) -> List[str]:
        """
        Génère des hashtags pertinents pour un contenu

        Args:
            content: Le contenu du post
            platform: La plateforme cible
            count: Nombre de hashtags à générer

        Returns:
            Liste de hashtags (avec #)
        """
        config = self.PLATFORM_CONFIGS[platform]
        max_hashtags = min(count, config["max_hashtags"])

        if not self.has_api_key:
            # Mode template: extraire les hashtags existants ou en générer de basiques
            existing = self._extract_hashtags(content)
            if existing:
                return existing[:max_hashtags]
            return self._generate_basic_hashtags(content, max_hashtags)

        try:
            prompt = f"""
Génère {max_hashtags} hashtags pertinents et populaires pour ce contenu {platform.value}:

"{content}"

Instructions:
- Hashtags spécifiques au sujet
- Mix de hashtags populaires et de niche
- Format: #hashtag (sans espaces)
- Pertinents pour {platform.value}

Retourne uniquement la liste de hashtags, un par ligne.
"""

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un expert en social media marketing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [line.strip() for line in hashtags_text.split('\n') if line.strip().startswith('#')]

            return hashtags[:max_hashtags]

        except Exception as e:
            print(f"Erreur lors de la génération de hashtags: {str(e)}")
            return self._generate_basic_hashtags(content, max_hashtags)

    # ============================================
    # MÉTHODES PRIVÉES
    # ============================================

    async def _build_prompt(self, request: ContentGenerationRequest) -> str:
        """Construit le prompt pour la génération"""
        config = self.PLATFORM_CONFIGS[request.platform]
        template = self.PLATFORM_PROMPTS[request.platform]

        # Déterminer la longueur max
        max_length = request.max_length or config["optimal_caption_length"]

        # Instructions pour emojis
        emoji_instruction = "Inclus 3-5 emojis pertinents" if request.include_emojis else "N'utilise pas d'emojis"

        # Instructions pour hashtags
        if request.include_hashtags:
            optimal = config["optimal_hashtags"]
            hashtag_instruction = f"Ajoute {optimal} hashtags stratégiques à la fin"
        else:
            hashtag_instruction = "N'utilise pas de hashtags"

        # Ton
        tone_desc = self.TONE_DESCRIPTIONS.get(request.tone, "professionnel")

        # Variables formatées
        variables_str = "\n".join([f"- {k}: {v}" for k, v in request.variables.items()])
        if not variables_str:
            variables_str = "Aucune"

        # Remplir le template
        prompt = template.format(
            tone=tone_desc,
            topic=request.prompt,
            variables=variables_str,
            emoji_instruction=emoji_instruction,
            hashtag_instruction=hashtag_instruction,
            max_length=max_length
        )

        return prompt

    async def _generate_with_openai(
        self,
        prompt: str,
        platform: PlatformType,
        model: str = "gpt-4-turbo-preview"
    ) -> str:
        """Génère du contenu avec OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Tu es un expert en création de contenu pour {platform.value}. "
                                   f"Tu crées du contenu engageant, authentique et optimisé pour la plateforme."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )

            generated_text = response.choices[0].message.content.strip()

            # Nettoyer le texte (enlever les guillemets de début/fin si présents)
            if generated_text.startswith('"') and generated_text.endswith('"'):
                generated_text = generated_text[1:-1]
            if generated_text.startswith('[') and generated_text.endswith(']'):
                generated_text = generated_text[1:-1]

            return generated_text

        except Exception as e:
            print(f"Erreur OpenAI: {str(e)}")
            raise

    async def _generate_with_template(
        self,
        platform: PlatformType,
        topic: str,
        tone: ToneVoice
    ) -> str:
        """Génère du contenu avec des templates (fallback sans API key)"""
        config = self.PLATFORM_CONFIGS[platform]

        templates = {
            PlatformType.INSTAGRAM: [
                f"✨ {topic}\n\nDécouvrez notre dernière innovation! 🚀\n\n"
                f"👉 En savoir plus (lien en bio)\n\n"
                f"#innovation #business #marketing #entrepreneur #success",

                f"🎯 {topic}\n\nOn vous partage notre secret aujourd'hui 💡\n\n"
                f"Sauvegardez ce post pour plus tard! 📌\n\n"
                f"#tips #conseil #business #reseauxsociaux #croissance"
            ],
            PlatformType.TWITTER: [
                f"🔥 {topic}\n\nC'est exactement ce dont vous avez besoin 👇\n\n"
                f"#business #innovation",

                f"💡 {topic}\n\nLa solution que tout le monde attendait.\n\n"
                f"RT si vous êtes d'accord! 🚀"
            ],
            PlatformType.LINKEDIN: [
                f"{topic}\n\n"
                f"Dans le monde professionnel d'aujourd'hui, l'innovation est clé.\n\n"
                f"Voici 3 insights que j'ai appris:\n"
                f"1. L'adaptation est essentielle\n"
                f"2. L'expertise se construit chaque jour\n"
                f"3. Le réseau est votre meilleur atout\n\n"
                f"Qu'en pensez-vous? 💼\n\n"
                f"#leadership #business #innovation",

                f"Réflexion du jour: {topic}\n\n"
                f"Après 10 ans dans l'industrie, j'ai compris une chose:\n"
                f"Le succès vient de la persévérance et de l'apprentissage continu.\n\n"
                f"Partagez votre expérience en commentaire! 👇\n\n"
                f"#carrière #développementprofessionnel #motivation"
            ],
            PlatformType.FACEBOOK: [
                f"🌟 {topic}\n\n"
                f"Bonjour la communauté! On est ravis de partager ça avec vous aujourd'hui.\n\n"
                f"C'est le fruit de plusieurs mois de travail et on espère que ça va vous plaire! 😊\n\n"
                f"Dites-nous ce que vous en pensez en commentaire! 👇💬\n\n"
                f"#communauté #nouveauté #partage"
            ],
            PlatformType.TIKTOK: [
                f"🎬 [Hook 3 sec] Vous ne croirez jamais ça!\n\n"
                f"📱 [15 sec] {topic}\n"
                f"Voici comment faire en 3 étapes simples!\n\n"
                f"💥 [2 sec] Suivez pour plus d'astuces!\n\n"
                f"#tiktok #astuce #viral #pourtoi #fyp"
            ]
        }

        # Sélectionner un template aléatoire
        import random
        available = templates.get(platform, templates[PlatformType.INSTAGRAM])
        return random.choice(available)

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrait les hashtags d'un texte"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return hashtags

    def _generate_basic_hashtags(self, content: str, count: int) -> List[str]:
        """Génère des hashtags basiques à partir du contenu"""
        # Extraire les mots importants (plus de 4 caractères, pas de mots vides)
        stop_words = {'pour', 'dans', 'avec', 'sans', 'sous', 'sur', 'que', 'qui', 'quoi',
                      'est', 'sont', 'été', 'être', 'avoir', 'fait', 'faire', 'plus', 'moins'}

        words = re.findall(r'\b\w{4,}\b', content.lower())
        keywords = [w for w in words if w not in stop_words]

        # Créer des hashtags uniques
        unique_keywords = []
        seen = set()
        for word in keywords:
            if word not in seen:
                unique_keywords.append(f"#{word}")
                seen.add(word)
            if len(unique_keywords) >= count:
                break

        # Ajouter des hashtags génériques si pas assez
        generic = ["#marketing", "#business", "#innovation", "#success", "#entrepreneur",
                   "#digital", "#socialmedia", "#content", "#growth", "#motivation"]

        while len(unique_keywords) < count and generic:
            tag = generic.pop(0)
            if tag not in unique_keywords:
                unique_keywords.append(tag)

        return unique_keywords[:count]

    def _calculate_quality_score(self, text: str, platform: PlatformType) -> int:
        """Calcule un score de qualité (0-100)"""
        score = 70  # Base score
        config = self.PLATFORM_CONFIGS[platform]

        # Longueur appropriée
        text_length = len(text)
        optimal_length = config["optimal_caption_length"]
        if optimal_length * 0.8 <= text_length <= optimal_length * 1.5:
            score += 10

        # Présence de hashtags
        hashtags = self._extract_hashtags(text)
        if len(hashtags) >= config["optimal_hashtags"]:
            score += 5

        # Présence d'emojis
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        if re.search(emoji_pattern, text):
            score += 5

        # Call-to-action présent
        cta_keywords = ['découvr', 'cliqu', 'visit', 'contact', 'partag', 'comment', 'sauvegard',
                        'suivez', 'abonnez', 'inscrivez', 'en savoir plus']
        if any(keyword in text.lower() for keyword in cta_keywords):
            score += 10

        return min(100, score)

    def _predict_engagement(self, text: str, platform: PlatformType, tone: ToneVoice) -> int:
        """Prédit le potentiel d'engagement (0-100)"""
        score = 60  # Base score

        # Analyse du ton
        tone_scores = {
            ToneVoice.INSPIRATIONAL: 85,
            ToneVoice.WITTY: 80,
            ToneVoice.PLAYFUL: 78,
            ToneVoice.FRIENDLY: 75,
            ToneVoice.EMPATHETIC: 72,
            ToneVoice.PROFESSIONAL: 65,
            ToneVoice.EDUCATIONAL: 70,
            ToneVoice.AUTHORITATIVE: 68,
            ToneVoice.LUXURY: 75,
            ToneVoice.CASUAL: 73
        }

        tone_boost = (tone_scores.get(tone, 65) - 60) // 2
        score += tone_boost

        # Mots puissants
        power_words = ['incroyable', 'secret', 'gratuit', 'nouveau', 'exclusif', 'limité',
                       'découvrez', 'révélation', 'astuce', 'conseil', 'expert', 'garantie']
        power_word_count = sum(1 for word in power_words if word in text.lower())
        score += min(10, power_word_count * 2)

        # Questions (augmente l'engagement)
        if '?' in text:
            score += 8

        # Emojis
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        emoji_count = len(re.findall(emoji_pattern, text))
        score += min(7, emoji_count)

        return min(100, score)
