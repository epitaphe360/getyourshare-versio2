"""
Service de Traduction Intelligent avec Cache en Base de Données
- Traduit automatiquement avec OpenAI pour les nouveaux textes
- Stocke les traductions en base de données
- Cache les traductions existantes pour éviter les coûts
"""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Modèle le moins cher

# Langues supportées
SUPPORTED_LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'ar': 'العربية (Arabic)',
    'darija': 'الدارجة المغربية (Moroccan Darija)'
}

class TranslationService:
    """Service de traduction intelligent avec cache DB et OpenAI"""
    
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self.openai_client = None
        
        # Initialiser OpenAI si la clé existe
        if OPENAI_API_KEY and OPENAI_API_KEY != "VOTRE_NOUVELLE_CLE_APRES_REVOCATION":
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info("✅ OpenAI Translation Service initialized")
            except Exception as e:
                logger.error(f"⚠️ OpenAI initialization failed: {e}")
                self.openai_client = None
        else:
            logger.info("⚠️ OpenAI API key not configured - translations will use fallback")
    
    async def get_translation(
        self, 
        key: str, 
        language: str, 
        context: Optional[str] = None,
        auto_translate: bool = True
    ) -> Optional[str]:
        """
        Récupère une traduction depuis le cache DB ou traduit avec OpenAI
        
        Args:
            key: Clé de traduction (ex: 'nav_dashboard')
            language: Code langue ('fr', 'en', 'ar', 'darija')
            context: Contexte optionnel pour améliorer la traduction
            auto_translate: Si True, traduit automatiquement si manquant
        
        Returns:
            Texte traduit ou None si non trouvé
        """
        
        # 1. Vérifier dans le cache DB
        if self.supabase:
            try:
                result = self.supabase.table('translations') \
                    .select('value, last_used') \
                    .eq('key', key) \
                    .eq('language', language) \
                    .execute()
                
                if result.data and len(result.data) > 0:
                    translation = result.data[0]['value']
                    
                    # Mettre à jour last_used
                    self.supabase.table('translations') \
                        .update({'last_used': datetime.now().isoformat()}) \
                        .eq('key', key) \
                        .eq('language', language) \
                        .execute()
                    
                    return translation
            except Exception as e:
                logger.error(f"⚠️ DB cache lookup failed: {e}")
        
        # 2. Si pas trouvé et auto_translate activé, traduire avec OpenAI
        if auto_translate and self.openai_client:
            try:
                # Récupérer la version française (langue source)
                source_text = await self._get_source_text(key)
                
                if source_text:
                    translated = await self._translate_with_openai(
                        source_text, 
                        language, 
                        context
                    )
                    
                    # Stocker en DB
                    if translated and self.supabase:
                        await self._save_translation(key, language, translated, context)
                    
                    return translated
            except Exception as e:
                logger.error(f"⚠️ Auto-translation failed for {key}: {e}")
        
        return None
    
    async def _get_source_text(self, key: str) -> Optional[str]:
        """Récupère le texte source (français) pour une clé"""
        
        if not self.supabase:
            return None
        
        try:
            result = self.supabase.table('translations') \
                .select('value') \
                .eq('key', key) \
                .eq('language', 'fr') \
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['value']
        except Exception as e:
            logger.error(f"⚠️ Source text lookup failed: {e}")
        
        return None
    
    async def _translate_with_openai(
        self, 
        text: str, 
        target_language: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """Traduit un texte avec OpenAI"""
        
        if not self.openai_client:
            return None
        
        language_name = SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        # Construire le prompt selon la langue cible
        if target_language == 'darija':
            prompt = f"""Traduire ce texte en Darija marocaine (dialecte populaire du Maroc).
Utiliser l'alphabet arabe mais avec un style conversationnel marocain.

Texte à traduire: "{text}"
{f'Contexte: {context}' if context else ''}

Traduction en Darija:"""
        
        elif target_language == 'ar':
            prompt = f"""Traduire ce texte en arabe standard moderne (MSA).
Utiliser un style formel et professionnel.

Texte à traduire: "{text}"
{f'Contexte: {context}' if context else ''}

Traduction en arabe:"""
        
        else:
            prompt = f"""Translate this text to {language_name}.
Use professional and appropriate tone for a business application.

Text to translate: "{text}"
{f'Context: {context}' if context else ''}

Translation in {language_name}:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator specializing in business and e-commerce terminology. Provide accurate, natural translations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Basse température pour plus de précision
                max_tokens=150
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            # Log du coût approximatif
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (input_tokens * 0.00015 + output_tokens * 0.0006) / 1000  # Prix gpt-4o-mini
            logger.info(f"✅ Translated '{text}' → {target_language} (Cost: ${cost:.6f})")
            
            return translated_text
        
        except Exception as e:
            logger.error(f"❌ OpenAI translation error: {e}")
            return None
    
    async def _save_translation(
        self, 
        key: str, 
        language: str, 
        value: str,
        context: Optional[str] = None
    ) -> bool:
        """Sauvegarde une traduction en base de données"""
        
        if not self.supabase:
            return False
        
        try:
            data = {
                'key': key,
                'language': language,
                'value': value,
                'context': context,
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'source': 'openai'
            }
            
            # Upsert (insert ou update si existe)
            self.supabase.table('translations').upsert(
                data,
                on_conflict='key,language'
            ).execute()
            
            logger.info(f"💾 Saved translation: {key} [{language}] = {value}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Save translation error: {e}")
            return False
    
    async def batch_translate(
        self, 
        keys: List[str], 
        target_language: str,
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Traduit plusieurs clés en une seule fois (optimisé)
        
        Args:
            keys: Liste de clés à traduire
            target_language: Langue cible
            context: Contexte optionnel
        
        Returns:
            Dictionnaire {key: traduction}
        """
        
        translations = {}
        missing_keys = []
        
        # 1. Récupérer les traductions existantes en une seule requête
        if self.supabase:
            try:
                result = self.supabase.table('translations') \
                    .select('key, value') \
                    .eq('language', target_language) \
                    .in_('key', keys) \
                    .execute()
                
                for row in result.data:
                    translations[row['key']] = row['value']
                
                # Identifier les clés manquantes
                missing_keys = [k for k in keys if k not in translations]
            except Exception as e:
                logger.error(f"⚠️ Batch lookup failed: {e}")
                missing_keys = keys
        else:
            missing_keys = keys
        
        # 2. Traduire les clés manquantes
        if missing_keys and self.openai_client:
            logger.info(f"🔄 Translating {len(missing_keys)} missing keys...")
            
            for key in missing_keys:
                translated = await self.get_translation(
                    key, 
                    target_language, 
                    context, 
                    auto_translate=True
                )
                
                if translated:
                    translations[key] = translated
        
        return translations
    
    async def get_all_translations(
        self, 
        language: str
    ) -> Dict[str, str]:
        """
        Récupère toutes les traductions pour une langue
        Utilisé pour le chargement initial du frontend
        
        Returns:
            Dictionnaire {key: value} de toutes les traductions
        """
        
        if not self.supabase:
            return {}
        
        try:
            result = self.supabase.table('translations') \
                .select('key, value') \
                .eq('language', language) \
                .execute()
            
            translations = {row['key']: row['value'] for row in result.data}
            
            logger.info(f"📦 Loaded {len(translations)} translations for {language}")
            return translations
        
        except Exception as e:
            logger.error(f"❌ Load all translations error: {e}")
            return {}
    
    async def import_static_translations(
        self, 
        translations_dict: Dict[str, str], 
        language: str
    ) -> int:
        """
        Importe des traductions statiques en masse
        Utilisé pour initialiser la DB avec les fichiers existants
        
        Args:
            translations_dict: {key: value}
            language: Code langue
        
        Returns:
            Nombre de traductions importées
        """
        
        if not self.supabase:
            return 0
        
        imported = 0
        
        try:
            for key, value in translations_dict.items():
                await self._save_translation(key, language, value, context='static_import')
                imported += 1
            
            logger.info(f"✅ Imported {imported} translations for {language}")
            return imported
        
        except Exception as e:
            logger.error(f"❌ Import error: {e}")
            return imported


# Instance globale
translation_service = None

def init_translation_service(supabase_client):
    """Initialise le service de traduction avec le client Supabase"""
    global translation_service
    translation_service = TranslationService(supabase_client)
    return translation_service
