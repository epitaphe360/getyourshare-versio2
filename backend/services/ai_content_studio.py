"""
AI Content Studio - Service Complet
Génération automatique de contenu avec GPT-4, DALL-E, traduction
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI
import requests
from io import BytesIO

from utils.logger import logger


class AIContentStudio:
    """Studio de création de contenu IA avancé"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - AI features disabled")
            self.client = None
            self.enabled = False
        else:
            self.client = OpenAI(api_key=self.openai_api_key)
            self.enabled = True

    def generate_product_description(
        self,
        product_name: str,
        category: str,
        features: List[str],
        target_audience: str = "general",
        tone: str = "professional",
        length: int = 300
    ) -> Dict[str, Any]:
        """
        Génère une description produit optimisée SEO

        Args:
            product_name: Nom du produit
            category: Catégorie
            features: Liste des caractéristiques
            target_audience: Public cible
            tone: Ton (professional, casual, enthusiastic)
            length: Longueur max en mots

        Returns:
            {
                'description': str,
                'short_description': str,
                'seo_keywords': List[str],
                'meta_description': str
            }
        """
        if not self.enabled:
            return self._generate_fallback_description(product_name, features)

        try:
            features_text = "\n".join([f"- {f}" for f in features])

            prompt = f"""Créer une description de produit persuasive et optimisée SEO pour:

Produit: {product_name}
Catégorie: {category}
Caractéristiques:
{features_text}

Public cible: {target_audience}
Ton: {tone}
Longueur: environ {length} mots

Générer:
1. Description complète (persuasive, bénéfices client)
2. Description courte (2-3 phrases)
3. 10 mots-clés SEO pertinents
4. Meta description (155 caractères max)

Format JSON:
{{
    "description": "...",
    "short_description": "...",
    "seo_keywords": ["...", "..."],
    "meta_description": "..."
}}
"""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un expert en rédaction marketing et SEO."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            # Parser le JSON de la réponse
            result = json.loads(content)

            logger.info(f"AI description generated for: {product_name}")
            return result

        except Exception as e:
            logger.error(f"AI description generation failed: {e}")
            return self._generate_fallback_description(product_name, features)

    def generate_social_posts(
        self,
        product_id: int,
        product_name: str,
        product_url: str,
        image_url: str,
        platforms: List[str] = ["facebook", "instagram", "twitter", "linkedin", "tiktok"]
    ) -> Dict[str, Dict[str, str]]:
        """
        Génère des posts optimisés pour chaque réseau social

        Returns:
            {
                'facebook': {'text': '...', 'hashtags': ['...']},
                'instagram': {...},
                ...
            }
        """
        if not self.enabled:
            return self._generate_fallback_social_posts(product_name)

        try:
            platform_specs = {
                'facebook': {'max_length': 500, 'style': 'conversational'},
                'instagram': {'max_length': 2200, 'style': 'visual, emoji-rich'},
                'twitter': {'max_length': 280, 'style': 'concise, impactful'},
                'linkedin': {'max_length': 700, 'style': 'professional, B2B'},
                'tiktok': {'max_length': 150, 'style': 'trending, Gen-Z'}
            }

            results = {}

            for platform in platforms:
                spec = platform_specs.get(platform, {'max_length': 300, 'style': 'general'})

                prompt = f"""Créer un post {platform} engageant pour:

Produit: {product_name}
URL: {product_url}

Style: {spec['style']}
Longueur max: {spec['max_length']} caractères

Générer:
1. Texte du post (persuasif, call-to-action clair)
2. 5-10 hashtags pertinents

Format JSON:
{{
    "text": "...",
    "hashtags": ["hashtag1", "hashtag2", ...]
}}
"""

                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": f"Tu es un expert en social media marketing pour {platform}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=500
                )

                content = response.choices[0].message.content
                results[platform] = json.loads(content)

            logger.info(f"Social posts generated for {len(platforms)} platforms")
            return results

        except Exception as e:
            logger.error(f"Social posts generation failed: {e}")
            return self._generate_fallback_social_posts(product_name)

    def translate_content(
        self,
        text: str,
        target_languages: List[str] = ["en", "es", "ar", "fr", "de"]
    ) -> Dict[str, str]:
        """
        Traduit du contenu en plusieurs langues

        Args:
            text: Texte à traduire
            target_languages: Langues cibles (ISO codes)

        Returns:
            {'en': 'translated text', 'es': '...', ...}
        """
        if not self.enabled:
            return {lang: text for lang in target_languages}

        try:
            language_names = {
                'en': 'English',
                'es': 'Spanish',
                'ar': 'Arabic',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'zh': 'Chinese'
            }

            results = {}

            for lang in target_languages:
                lang_name = language_names.get(lang, lang)

                prompt = f"""Translate the following text to {lang_name}.
Maintain the tone, style, and marketing appeal.

Text:
{text}

Translation:"""

                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": f"Tu es un traducteur professionnel expert en {lang_name}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

                results[lang] = response.choices[0].message.content.strip()

            logger.info(f"Content translated to {len(target_languages)} languages")
            return results

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {lang: text for lang in target_languages}

    def generate_product_image(
        self,
        product_name: str,
        description: str,
        style: str = "realistic, product photography",
        size: str = "1024x1024"
    ) -> Optional[str]:
        """
        Génère une image produit avec DALL-E 3

        Returns:
            URL de l'image générée ou None
        """
        if not self.enabled:
            return None

        try:
            prompt = f"""Professional product photography of {product_name}.
{description}

Style: {style}
High quality, well-lit, clean background, commercial use."""

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="hd",
                n=1
            )

            image_url = response.data[0].url

            logger.info(f"Product image generated with DALL-E: {product_name}")
            return image_url

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None

    def enhance_image_description(
        self,
        image_url: str
    ) -> Dict[str, Any]:
        """
        Analyse une image et génère des descriptions optimisées

        Returns:
            {
                'alt_text': str,
                'caption': str,
                'tags': List[str],
                'description': str
            }
        """
        if not self.enabled:
            return self._generate_fallback_image_description()

        try:
            # GPT-4 Vision pour analyser l'image
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this product image and provide:
1. SEO-optimized alt text (125 chars max)
2. Engaging caption for social media
3. 10 relevant tags/keywords
4. Detailed description (2-3 sentences)

Format as JSON:
{
    "alt_text": "...",
    "caption": "...",
    "tags": ["...", "..."],
    "description": "..."
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            logger.info("Image description enhanced with AI")
            return result

        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return self._generate_fallback_image_description()

    def generate_email_campaign(
        self,
        product_name: str,
        offer_details: str,
        target_segment: str,
        campaign_goal: str = "sales"
    ) -> Dict[str, str]:
        """
        Génère une campagne email complète

        Returns:
            {
                'subject': str,
                'preheader': str,
                'body_html': str,
                'body_text': str,
                'cta': str
            }
        """
        if not self.enabled:
            return self._generate_fallback_email()

        try:
            prompt = f"""Create a high-converting email campaign for:

Product: {product_name}
Offer: {offer_details}
Target: {target_segment}
Goal: {campaign_goal}

Generate:
1. Compelling subject line (50 chars max)
2. Preheader text (100 chars max)
3. Email body (HTML format, mobile-responsive)
4. Plain text version
5. Call-to-action button text

Focus on: urgency, social proof, clear benefits, strong CTA.

Format as JSON:
{{
    "subject": "...",
    "preheader": "...",
    "body_html": "...",
    "body_text": "...",
    "cta": "..."
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Tu es un expert en email marketing avec un taux de conversion élevé."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            logger.info(f"Email campaign generated for: {product_name}")
            return result

        except Exception as e:
            logger.error(f"Email generation failed: {e}")
            return self._generate_fallback_email()

    # Méthodes fallback
    def _generate_fallback_description(self, name: str, features: List[str]) -> Dict[str, Any]:
        """Génère une description basique si l'IA n'est pas disponible"""
        return {
            'description': f"{name} - " + " ".join(features),
            'short_description': name,
            'seo_keywords': [name.lower()] + features[:5],
            'meta_description': f"Découvrez {name}. {' '.join(features[:2])}"[:155]
        }

    def _generate_fallback_social_posts(self, name: str) -> Dict[str, Dict[str, str]]:
        """Posts basiques si l'IA n'est pas disponible"""
        base_text = f"Découvrez {name}! Disponible maintenant 🚀"
        base_hashtags = ["shopping", "nouveauté", "promo"]

        return {
            platform: {
                'text': base_text,
                'hashtags': base_hashtags
            }
            for platform in ["facebook", "instagram", "twitter", "linkedin", "tiktok"]
        }

    def _generate_fallback_image_description(self) -> Dict[str, Any]:
        """Description image basique"""
        return {
            'alt_text': 'Product image',
            'caption': 'Check out this amazing product!',
            'tags': ['product', 'shopping', 'ecommerce'],
            'description': 'High quality product image.'
        }

    def _generate_fallback_email(self) -> Dict[str, str]:
        """Email basique"""
        return {
            'subject': 'Special Offer Inside!',
            'preheader': 'Don\'t miss out on this exclusive deal',
            'body_html': '<p>Check out our amazing offer!</p>',
            'body_text': 'Check out our amazing offer!',
            'cta': 'Shop Now'
        }


# Instance globale
ai_content_studio = AIContentStudio()
