"""
Générateur de contenu LOCAL sans dépendre d'API externes
Permet au Content Studio de fonctionner à 100% même sans OpenAI
"""

import random
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

class LocalContentGenerator:
    """Génère du contenu marketing sans API externe"""
    
    def __init__(self):
        # Templates de textes marketing par catégorie
        self.marketing_templates = {
            "product_description": [
                "Découvrez {product}, l'innovation qui va révolutionner votre quotidien ! ✨",
                "🎯 {product} : La solution parfaite pour tous vos besoins. Commandez maintenant !",
                "💫 Transformez votre vie avec {product}. Qualité premium garantie !",
                "🔥 TENDANCE : {product} - Le produit que tout le monde s'arrache !",
                "⭐ {product} : Excellence et performance réunies. Ne passez pas à côté !"
            ],
            "promotion": [
                "🎉 PROMO EXCLUSIVE ! -{discount}% sur {product} jusqu'à {date} !",
                "⚡ VENTE FLASH : {product} à prix incroyable ! Stocks limités !",
                "💥 OFFRE SPÉCIALE : Profitez de -{discount}% sur {product} !",
                "🎁 CADEAU : Achetez {product} et recevez {gift} OFFERT !",
                "🔥 DERNIÈRE CHANCE : -{discount}% sur {product} - Plus que {hours}h !"
            ],
            "testimonial": [
                "⭐⭐⭐⭐⭐ 'Incroyable ! {product} a dépassé toutes mes attentes !' - {name}",
                "💯 '{product} a changé ma vie ! Je recommande à 100%' - {name}",
                "🌟 'Meilleur achat de l'année ! {product} est parfait' - {name}",
                "❤️ 'Je suis fan de {product} ! Qualité exceptionnelle' - {name}",
                "🎯 '{product} tient toutes ses promesses. Bravo !' - {name}"
            ],
            "call_to_action": [
                "👉 Cliquez sur le lien dans la bio pour commander !",
                "💳 Commandez maintenant et recevez sous 48h !",
                "🛒 Ajoutez au panier avant que le stock s'épuise !",
                "🎁 Offre limitée ! Profitez-en maintenant !",
                "⏰ Ne ratez pas cette opportunité unique !"
            ],
            "hooks": [
                "🚨 ATTENTION : Cette vidéo va changer votre vision de {topic} !",
                "❌ STOP ! Ne faites plus cette erreur avec {topic} !",
                "💡 Le secret que personne ne vous dit sur {topic}...",
                "😱 Vous ne devinerez jamais ce que {topic} peut faire !",
                "🎯 3 astuces pour maîtriser {topic} en 2 minutes !"
            ],
            "story_captions": [
                "✨ Nouveauté ! Swipe up pour découvrir 👆",
                "🔥 Soldes ! Jusqu'à -{discount}% - Lien en bio",
                "💫 Transformation avant/après ! Réagissez avec 🔥",
                "🎁 Concours ! Tag 3 amis pour participer",
                "⭐ Avis clients : {rating}/5 étoiles !"
            ]
        }
        
        # Emojis par catégorie
        self.emoji_sets = {
            "beauty": ["💄", "💅", "✨", "💫", "🌟", "💖", "👑", "💎"],
            "fashion": ["👗", "👠", "👜", "🕶️", "💍", "👑", "✨", "💫"],
            "tech": ["📱", "💻", "⌚", "🎧", "📷", "🖥️", "⚡", "🔋"],
            "food": ["🍕", "🍔", "🍰", "🍫", "☕", "🍷", "🍓", "🥑"],
            "fitness": ["💪", "🏋️", "🧘", "🏃", "⚽", "🥇", "🔥", "💯"],
            "home": ["🏠", "🛋️", "🛏️", "🌿", "🕯️", "🖼️", "💡", "✨"],
            "general": ["✨", "💫", "🎯", "🔥", "💯", "⭐", "🎉", "💪"]
        }
        
        # Hashtags populaires
        self.hashtag_sets = {
            "beauty": ["#beauty", "#makeup", "#skincare", "#cosmetics", "#beautytips"],
            "fashion": ["#fashion", "#style", "#ootd", "#fashionista", "#trendy"],
            "tech": ["#tech", "#gadgets", "#innovation", "#technology", "#techtips"],
            "food": ["#food", "#foodie", "#delicious", "#foodporn", "#yummy"],
            "fitness": ["#fitness", "#workout", "#health", "#gym", "#fitlife"],
            "maroc": ["#maroc", "#morocco", "#casablanca", "#rabat", "#marocain"],
            "general": ["#instagood", "#love", "#photooftheday", "#beautiful", "#happy"]
        }
    
    def generate_post_caption(
        self,
        product_name: str,
        category: str = "general",
        include_promo: bool = False,
        discount: int = 20,
        include_cta: bool = True
    ) -> Dict[str, Any]:
        """
        Générer une légende de post Instagram/Facebook complète
        
        Args:
            product_name: Nom du produit
            category: Catégorie (beauty, fashion, tech, food, fitness, home)
            include_promo: Inclure un message promo
            discount: Pourcentage de réduction
            include_cta: Inclure un call-to-action
        
        Returns:
            Caption complète avec emojis et hashtags
        """
        # Emojis pertinents
        emojis = self.emoji_sets.get(category, self.emoji_sets["general"])
        emoji = random.choice(emojis)
        
        # Template de description
        if include_promo:
            template = random.choice(self.marketing_templates["promotion"])
            caption = template.format(
                product=product_name,
                discount=discount,
                date="31/12",
                gift="cadeau surprise",
                hours="24"
            )
        else:
            template = random.choice(self.marketing_templates["product_description"])
            caption = template.format(product=product_name)
        
        # Ajouter CTA
        if include_cta:
            cta = random.choice(self.marketing_templates["call_to_action"])
            caption += f"\n\n{cta}"
        
        # Ajouter hashtags
        hashtags_cat = self.hashtag_sets.get(category, self.hashtag_sets["general"])
        hashtags_maroc = self.hashtag_sets["maroc"]
        hashtags = random.sample(hashtags_cat, 3) + random.sample(hashtags_maroc, 2)
        
        caption += f"\n\n{' '.join(hashtags)}"
        
        return {
            "caption": caption,
            "character_count": len(caption),
            "hashtag_count": len(hashtags),
            "emoji_used": emoji,
            "includes_cta": include_cta
        }
    
    def generate_story_text(
        self,
        product_name: str,
        discount: int = 20,
        rating: float = 4.8
    ) -> str:
        """Générer texte pour story Instagram"""
        template = random.choice(self.marketing_templates["story_captions"])
        return template.format(
            product=product_name,
            discount=discount,
            rating=rating
        )
    
    def generate_tiktok_script(
        self,
        product_name: str,
        key_features: List[str],
        price: str,
        discount: int = 0
    ) -> Dict[str, str]:
        """
        Générer un script TikTok complet
        
        Returns:
            Dictionnaire avec hook, body, cta
        """
        # Hook (3 premières secondes)
        hook = random.choice(self.marketing_templates["hooks"]).format(
            topic=product_name
        )
        
        # Body (présentation des features)
        body = f"Laissez-moi vous présenter {product_name} :\n\n"
        for i, feature in enumerate(key_features[:3], 1):
            body += f"{i}. {feature}\n"
        
        # Prix et promo
        if discount > 0:
            body += f"\n💰 Prix : {price} MAD (-{discount}%)"
        else:
            body += f"\n💰 Prix : {price} MAD"
        
        # CTA
        cta = random.choice(self.marketing_templates["call_to_action"])
        
        return {
            "hook": hook,
            "body": body,
            "cta": cta,
            "full_script": f"{hook}\n\n{body}\n\n{cta}",
            "duration_estimate": "30-45 secondes"
        }
    
    def generate_testimonial(
        self,
        product_name: str,
        customer_name: str = None
    ) -> str:
        """Générer un témoignage client réaliste"""
        if not customer_name:
            customer_name = random.choice([
                "Sarah M.", "Karim B.", "Fatima Z.", "Youssef A.",
                "Amina K.", "Omar R.", "Salma H.", "Mehdi T."
            ])
        
        template = random.choice(self.marketing_templates["testimonial"])
        return template.format(
            product=product_name,
            name=customer_name
        )
    
    def generate_placeholder_image(
        self,
        width: int = 1080,
        height: int = 1080,
        text: str = "Votre Produit",
        bg_color: str = "#FF6B9D",
        text_color: str = "#FFFFFF"
    ) -> str:
        """
        Générer une image placeholder stylisée
        
        Returns:
            Image en base64
        """
        # Créer l'image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Tenter de charger une police, sinon utiliser la police par défaut
        try:
            font_size = min(width, height) // 10
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        # Calculer la position du texte (centré)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Dessiner le texte avec ombre
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill="#00000080")
        draw.text((x, y), text, font=font, fill=text_color)
        
        # Ajouter des éléments décoratifs
        self._add_decorative_elements(draw, width, height)
        
        # Convertir en base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def _add_decorative_elements(self, draw: ImageDraw.Draw, width: int, height: int):
        """Ajouter des éléments décoratifs à l'image"""
        # Ajouter des cercles décoratifs
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(20, 100)
            opacity = random.randint(20, 60)
            color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}{opacity:02x}"
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    def generate_hashtag_strategy(
        self,
        category: str,
        niche_keywords: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Générer une stratégie de hashtags complète
        
        Returns:
            Hashtags organisés par portée (high, medium, low)
        """
        base_hashtags = self.hashtag_sets.get(category, self.hashtag_sets["general"])
        morocco_hashtags = self.hashtag_sets["maroc"]
        
        strategy = {
            "high_reach": random.sample(self.hashtag_sets["general"], 3),  # Très populaires
            "medium_reach": random.sample(base_hashtags, 3),  # Catégorie spécifique
            "low_reach": random.sample(morocco_hashtags, 2),  # Niche locale
            "branded": []  # À personnaliser
        }
        
        if niche_keywords:
            strategy["low_reach"].extend([f"#{kw.lower().replace(' ', '')}" for kw in niche_keywords[:2]])
        
        return strategy
    
    def generate_content_calendar_week(
        self,
        product_name: str,
        category: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Générer un calendrier de contenu pour une semaine
        
        Returns:
            Liste de 7 posts planifiés
        """
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        content_types = [
            "Product Showcase",
            "Customer Review",
            "Tutorial",
            "Behind the Scenes",
            "Promo Flash",
            "User Generated Content",
            "Inspiration Post"
        ]
        
        calendar = []
        
        for i, day in enumerate(days):
            post = {
                "day": day,
                "day_number": i + 1,
                "content_type": content_types[i],
                "caption": self.generate_post_caption(
                    product_name,
                    category,
                    include_promo=(i == 4),  # Vendredi = promo
                    include_cta=True
                )["caption"],
                "best_time": self._get_best_posting_time(day),
                "platform_priority": self._get_platform_priority(content_types[i])
            }
            calendar.append(post)
        
        return calendar
    
    def _get_best_posting_time(self, day: str) -> str:
        """Déterminer la meilleure heure de publication"""
        weekday_times = ["12:00-14:00", "18:00-20:00"]
        weekend_times = ["10:00-12:00", "15:00-17:00", "20:00-22:00"]
        
        if day in ["Samedi", "Dimanche"]:
            return random.choice(weekend_times)
        return random.choice(weekday_times)
    
    def _get_platform_priority(self, content_type: str) -> List[str]:
        """Déterminer les plateformes prioritaires selon le type de contenu"""
        priorities = {
            "Product Showcase": ["Instagram", "Facebook", "Pinterest"],
            "Customer Review": ["Instagram", "Facebook", "TikTok"],
            "Tutorial": ["TikTok", "Instagram", "YouTube"],
            "Behind the Scenes": ["Instagram Stories", "TikTok"],
            "Promo Flash": ["Instagram", "Facebook", "WhatsApp"],
            "User Generated Content": ["Instagram", "TikTok"],
            "Inspiration Post": ["Instagram", "Pinterest", "Facebook"]
        }
        
        return priorities.get(content_type, ["Instagram", "Facebook"])


# Instance singleton
local_generator = LocalContentGenerator()
