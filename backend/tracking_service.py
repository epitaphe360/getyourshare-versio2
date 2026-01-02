"""
Service de Tracking - Gestion des clics et attribution des ventes
Gère les cookies, redirections et attribution des influenceurs

Optimisé pour éviter les N+1 queries avec eager loading
"""

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from supabase_client import supabase
from typing import Optional, Dict
import hashlib
import secrets
import logging
import os
import json

logger = logging.getLogger(__name__)

# Configuration
COOKIE_NAME = "systrack"  # ShareYourSales tracking
COOKIE_EXPIRY_DAYS = 30  # Durée d'attribution (30 jours)
SHORT_CODE_LENGTH = 8


class TrackingService:
    """Service de tracking des clics et attribution"""

    def __init__(self):
        self.supabase = supabase

    # ============================================
    # 1. GÉNÉRATION DE LIENS TRACKÉS
    # ============================================

    def generate_short_code(self, link_id: str = None) -> str:
        """Génère un code court unique pour un lien"""
        # Utiliser hash + timestamp pour unicité
        if link_id:
            raw = f"{link_id}-{datetime.now().isoformat()}-{secrets.token_hex(4)}"
        else:
            raw = f"{datetime.now().isoformat()}-{secrets.token_hex(4)}"
            
        hash_obj = hashlib.sha256(raw.encode())
        short_code = hash_obj.hexdigest()[:SHORT_CODE_LENGTH]
        return short_code.upper()

    def anonymize_ip(self, ip_address: str) -> str:
        """Anonymise une adresse IP avec SHA-256 (GDPR compliance)"""
        if not ip_address or ip_address == "unknown":
            return "unknown"
        # Salt avec une valeur fixe pour permettre le comptage des uniques, 
        # mais empêcher de retrouver l'IP originale
        salt = "sys_gdpr_salt_2025" 
        return hashlib.sha256(f"{ip_address}{salt}".encode()).hexdigest()

    async def create_tracking_link(
        self,
        influencer_id: str,
        product_id: Optional[str],
        merchant_url: str,
        campaign_id: Optional[str] = None,
        service_id: Optional[str] = None,
    ) -> Dict:
        """
        Crée un lien tracké pour un influenceur

        Args:
            influencer_id: ID de l'influenceur
            product_id: ID du produit (optionnel si service_id présent)
            merchant_url: URL de destination (boutique marchand)
            campaign_id: ID de campagne optionnel
            service_id: ID du service (optionnel si product_id présent)

        Returns:
            {
                "link_id": "uuid",
                "short_code": "ABC12345",
                "tracking_url": "https://share.io/r/ABC12345",
                "destination_url": "https://merchant.com/product"
            }
        """
        try:
            # 1. Générer un code court unique
            short_code = self.generate_short_code()
            # 3. Construire l'URL de tracking
            base_url = os.getenv("API_URL", "http://localhost:8000")
            tracking_url = f"{base_url}/r/{short_code}"

            # 2. Créer l'entrée affiliate_links (Unified with affiliate_links_endpoints.py)
            link_data = {
                "influencer_id": influencer_id,
                "product_id": product_id,
                "service_id": service_id,
                # "campaign_id": campaign_id, # Not in affiliate_links schema apparently
                "unique_code": short_code,
                "url": tracking_url, # affiliate_links uses 'url', tracking_links used 'full_url'
                "created_at": datetime.now().isoformat(),
            }

            result = supabase.table("affiliate_links").insert(link_data).execute()
            link_id = result.data[0]["id"]

            logger.info(f"✅ Lien créé: {tracking_url} → {merchant_url}")

            return {
                "success": True,
                "link_id": link_id,
                "short_code": short_code,
                "tracking_url": tracking_url,
                "destination_url": merchant_url,
            }

        except Exception as e:
            logger.error(f"Erreur création lien: {e}")
            return {"success": False, "error": str(e)}

    # ============================================
    # 2. TRACKING DES CLICS
    # ============================================

    async def track_click(
        self, short_code: str, request: Request, response: Response
    ) -> Optional[str]:
        """
        Enregistre un clic et retourne l'URL de destination

        Args:
            short_code: Code du lien (ex: "ABC12345")
            request: Requête FastAPI (pour IP, User-Agent, etc.)
            response: Réponse FastAPI (pour set cookie)

        Returns:
            URL de destination ou None si lien invalide
        """
        try:
            # 1. Récupérer le lien depuis la BDD (affiliate_links)
            link_result = (
                supabase.table("affiliate_links").select("*").eq("unique_code", short_code).execute()
            )

            if not link_result.data:
                logger.warning(f"⚠️ Lien introuvable: {short_code}")
                return None

            link = link_result.data[0]

            # Vérifier que le lien est actif (if column exists, otherwise assume active)
            if link.get("is_active") is False:
                logger.warning(f"⚠️ Lien inactif: {short_code}")
                return None

            # 2. Extraire les métadonnées du visiteur
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            referer = request.headers.get("referer", "")

            # Anonymisation IP (GDPR)
            anonymized_ip = self.anonymize_ip(client_ip)

            # 3. Enregistrer le clic dans la table tracking_events (Unified with affiliate_links_endpoints.py)
            click_data = {
                "tracking_link_id": link["id"],
                "event_type": "click",
                "event_data": { # JSONB column
                    "ip_address": anonymized_ip,
                    "user_agent": user_agent,
                    "referer": referer,
                    "influencer_id": link["influencer_id"]
                },
                "created_at": datetime.now().isoformat(),
            }

            click_result = supabase.table("tracking_events").insert(click_data).execute()
            click_id = click_result.data[0]["id"]

            # 4. Incrémenter le compteur de clics -> Not needed as we count events

            # 5. Créer le cookie d'attribution (expire dans 30 jours)
            cookie_value = self._generate_attribution_cookie(
                link_id=link["id"], influencer_id=link["influencer_id"], click_id=click_id
            )

            response.set_cookie(
                key=COOKIE_NAME,
                value=cookie_value,
                max_age=COOKIE_EXPIRY_DAYS * 24 * 60 * 60,  # 30 jours en secondes
                httponly=True,  # Sécurité: pas accessible via JavaScript
                samesite="lax",  # Protection CSRF
            )

            logger.info(f"🖱️ Clic tracké: {short_code} → Cookie: {cookie_value[:20]}...")

            # 6. Retourner l'URL de destination
            # affiliate_links doesn't have destination_url, so we fetch from product/service
            destination_url = None
            
            if link.get('product_id'):
                try:
                    product = supabase.table('products').select('url').eq('id', link['product_id']).single().execute()
                    destination_url = product.data.get('url')
                    if not destination_url:
                         destination_url = f"https://merchant.com/product/{link['product_id']}"
                except Exception:
                    pass
            elif link.get('service_id'):
                try:
                    # Assuming services have url or we construct it
                    destination_url = f"https://merchant.com/service/{link['service_id']}"
                except Exception:
                    pass

            if not destination_url:
                 destination_url = "https://shareyoursales.ma" # Fallback home

            return destination_url

        except Exception as e:
            logger.error(f"Erreur tracking clic: {e}")
            return None

    def _generate_attribution_cookie(self, link_id: str, influencer_id: str, click_id: str) -> str:
        """
        Génère la valeur du cookie d'attribution
        Format: link_id|influencer_id|click_id|timestamp
        """
        timestamp = datetime.now().isoformat()
        cookie_parts = [link_id, influencer_id, click_id, timestamp]
        return "|".join(cookie_parts)

    # ============================================
    # 3. ATTRIBUTION DES VENTES
    # ============================================

    def parse_attribution_cookie(self, cookie_value: str) -> Optional[Dict]:
        """
        Parse le cookie d'attribution

        Returns:
            {
                "link_id": "uuid",
                "influencer_id": "uuid",
                "click_id": "uuid",
                "timestamp": "2025-10-23T..."
            }
        """
        try:
            parts = cookie_value.split("|")
            if len(parts) != 4:
                return None

            return {
                "link_id": parts[0],
                "influencer_id": parts[1],
                "click_id": parts[2],
                "timestamp": parts[3],
            }
        except Exception as e:
            logger.error(f"Erreur parse cookie: {e}")
            return None

    async def get_attribution_from_request(self, request: Request) -> Optional[Dict]:
        """
        Récupère l'attribution depuis le cookie de la requête

        Returns:
            {
                "influencer_id": "uuid",
                "link_id": "uuid",
                "click_id": "uuid"
            }
            ou None si pas de cookie
        """
        cookie_value = request.cookies.get(COOKIE_NAME)

        if not cookie_value:
            return None

        attribution = self.parse_attribution_cookie(cookie_value)

        if not attribution:
            return None

        # Vérifier que le cookie n'a pas expiré (30 jours)
        try:
            cookie_timestamp = datetime.fromisoformat(attribution["timestamp"])
            age_days = (datetime.now() - cookie_timestamp).days

            if age_days > COOKIE_EXPIRY_DAYS:
                logger.warning(f"⚠️ Cookie expiré ({age_days} jours)")
                return None

            logger.info(f"✅ Attribution trouvée: Influenceur {attribution['influencer_id']}")
            return attribution

        except Exception as e:
            logger.error(f"Erreur vérification cookie: {e}")
            return None

    # ============================================
    # 4. STATISTIQUES
    # ============================================

    async def get_link_stats(self, link_id: str) -> Dict:
        """Récupère les statistiques d'un lien"""
        try:
            # Lien principal
            link = supabase.table("affiliate_links").select("*").eq("id", link_id).execute()

            if not link.data:
                return {"error": "Lien introuvable"}

            link_data = link.data[0]

            # Clics (tracking_events)
            clicks = (
                supabase.table("tracking_events").select("id", count="exact").eq("link_id", link_id).eq("event_type", "click").execute()
            )
            clicks_count = clicks.count or 0

            # Conversions
            sales = supabase.table("conversions").select("*").eq("link_id", link_id).execute()
            sales_count = len(sales.data) if sales.data else 0
            
            # Revenue (assuming conversions table has amount or commission_amount)
            # conversions table usually has sale_amount or commission_amount
            total_revenue = 0.0
            if sales.data:
                for s in sales.data:
                    total_revenue += float(s.get("commission_amount", 0))

            # Taux de conversion
            conversion_rate = (
                (sales_count / clicks_count * 100) if clicks_count > 0 else 0
            )

            return {
                "link_id": link_id,
                "short_code": link_data.get("unique_code"),
                "clicks_total": clicks_count,
                "clicks_unique": clicks_count, # Simplified for now
                "conversions": sales_count,
                "conversion_rate": round(conversion_rate, 2),
                "revenue": round(total_revenue, 2),
                "status": "active", # affiliate_links doesn't have status, assume active
                "created_at": link_data.get("created_at"),
            }

        except Exception as e:
            logger.error(f"Erreur stats lien: {e}")
            return {"error": str(e)}


# Instance globale
tracking_service = TrackingService()
