"""
Fonctions helpers pour interagir avec Supabase
Simplifie les opérations CRUD
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime
import bcrypt

# ============================================
# USERS
# ============================================


def get_user_by_email(email: str) -> Optional[Dict]:
    """Récupère un utilisateur par email"""
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Récupère un utilisateur par ID"""
    try:
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user by id: {e}")
        return None


def create_user(email: str, password: str, role: str, **kwargs) -> Optional[Dict]:
    """Crée un nouvel utilisateur"""
    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "phone": kwargs.get("phone"),
            "two_fa_enabled": kwargs.get("two_fa_enabled", False),
            "is_active": kwargs.get("is_active", True),
        }

        if "email_verified" in kwargs:
            user_data["email_verified"] = kwargs.get("email_verified")
        if kwargs.get("verification_token"):
            user_data["verification_token"] = kwargs.get("verification_token")
        if kwargs.get("verification_expires"):
            user_data["verification_expires"] = kwargs.get("verification_expires")
        if kwargs.get("verification_sent_at"):
            user_data["verification_sent_at"] = kwargs.get("verification_sent_at")

        result = supabase.table("users").insert(user_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None


def get_user_by_verification_token(token: str) -> Optional[Dict]:
    """Récupère un utilisateur via son token de vérification"""
    try:
        result = (
            supabase.table("users").select("*").eq("verification_token", token).limit(1).execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user by verification token: {e}")
        return None


def set_verification_token(user_id: str, token: str, expires_at: str, sent_at: str) -> bool:
    """Met à jour le token de vérification pour un utilisateur"""
    try:
        supabase.table("users").update(
            {
                "verification_token": token,
                "verification_expires": expires_at,
                "verification_sent_at": sent_at,
                "email_verified": False,
            }
        ).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error setting verification token: {e}")
        return False


def mark_email_verified(user_id: str) -> bool:
    """Marque l'email d'un utilisateur comme vérifié"""
    try:
        supabase.table("users").update(
            {
                "email_verified": True,
                "verification_token": None,
                "verification_expires": None,
                "verification_sent_at": None,
            }
        ).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error marking email as verified: {e}")
        return False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def update_user(user_id: str, updates: Dict[str, Any]) -> bool:
    """Met à jour les informations d'un utilisateur"""
    try:
        # Ajouter updated_at automatiquement
        updates["updated_at"] = datetime.now().isoformat()

        # Exécuter la mise à jour
        supabase.table("users").update(updates).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return False


def update_user_last_login(user_id: str):
    """Met à jour la date de dernière connexion"""
    try:
        supabase.table("users").update({"last_login": datetime.now().isoformat()}).eq(
            "id", user_id
        ).execute()
    except Exception as e:
        logger.error(f"Error updating last login: {e}")


# ============================================
# MERCHANTS
# ============================================


def get_all_merchants() -> List[Dict]:
    """Récupère tous les merchants depuis la table users"""
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("role", "merchant")
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error getting merchants: {e}")
        return []


def get_merchant_by_id(merchant_id: str) -> Optional[Dict]:
    """Récupère un merchant par ID"""
    try:
        result = (
            supabase.table("merchants")
            .select(
                """
            *,
            users:user_id (
                id,
                email,
                phone
            )
        """
            )
            .eq("id", merchant_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting merchant: {e}")
        return None


def get_merchant_by_user_id(user_id: str) -> Optional[Dict]:
    """Récupère un merchant par user_id"""
    try:
        result = supabase.table("merchants").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting merchant by user_id: {e}")
        return None


# ============================================
# INFLUENCERS
# ============================================


def get_all_influencers() -> List[Dict]:
    """Récupère tous les influencers depuis la table users"""
    try:
        result = (
            supabase.table("users")
            .select("*")
            .eq("role", "influencer")
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Error getting influencers: {e}")
        return []


def get_influencer_by_id(influencer_id: str) -> Optional[Dict]:
    """Récupère un influencer par ID"""
    try:
        result = (
            supabase.table("influencers")
            .select(
                """
            *,
            users:user_id (
                id,
                email
            )
        """
            )
            .eq("id", influencer_id)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting influencer: {e}")
        return None


def get_influencer_by_user_id(user_id: str) -> Optional[Dict]:
    """Récupère un influencer par user_id"""
    try:
        result = supabase.table("influencers").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting influencer by user_id: {e}")
        return None


# ============================================
# PRODUCTS
# ============================================


def get_all_products(
    category: Optional[str] = None, merchant_id: Optional[str] = None
) -> List[Dict]:
    """Récupère tous les produits avec filtres optionnels"""
    try:
        # Simple query sans jointure complexe
        query = supabase.table("products").select("*")

        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        
        # Ajouter les infos merchant manuellement si besoin
        products = result.data if result.data else []
        
        # Pour chaque produit, récupérer le nom du merchant
        for product in products:
            if product.get("merchant_id"):
                try:
                    user_result = supabase.table("users").select("company_name, email").eq("id", product["merchant_id"]).single().execute()
                    if user_result.data:
                        product["merchant"] = {
                            "company_name": user_result.data.get("company_name"),
                            "email": user_result.data.get("email")
                        }
                except Exception:
                    pass
        
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return []


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Récupère un produit par ID"""
    try:
        result = supabase.table("products").select("*").eq("id", product_id).execute()
        
        if result.data:
            product = result.data[0]
            # Ajouter les infos merchant
            if product.get("merchant_id"):
                try:
                    user_result = supabase.table("users").select("company_name, email").eq("id", product["merchant_id"]).single().execute()
                    if user_result.data:
                        product["merchant"] = {
                            "company_name": user_result.data.get("company_name"),
                            "email": user_result.data.get("email")
                        }
                except Exception:
                    pass
            return product
        return None
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return None


# ==================== SERVICES ====================

def get_all_services(
    category: Optional[str] = None, merchant_id: Optional[str] = None
) -> List[Dict]:
    """Récupère tous les services avec filtres optionnels"""
    try:
        query = supabase.table("services").select("*")

        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        
        services = result.data if result.data else []
        
        # Pour chaque service, récupérer les infos du merchant
        for service in services:
            if service.get("merchant_id"):
                try:
                    user_result = supabase.table("users").select("company_name, email").eq("id", service["merchant_id"]).single().execute()
                    if user_result.data:
                        service["merchant"] = {
                            "company_name": user_result.data.get("company_name"),
                            "email": user_result.data.get("email")
                        }
                except Exception:
                    pass
        
        return services
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        return []


def get_service_by_id(service_id: str) -> Optional[Dict]:
    """Récupère un service par ID"""
    try:
        result = supabase.table("services").select("*").eq("id", service_id).execute()
        
        if result.data:
            service = result.data[0]
            # Ajouter les infos merchant
            if service.get("merchant_id"):
                try:
                    user_result = supabase.table("users").select("company_name, email").eq("id", service["merchant_id"]).single().execute()
                    if user_result.data:
                        service["merchant"] = {
                            "company_name": user_result.data.get("company_name"),
                            "email": user_result.data.get("email")
                        }
                except Exception:
                    pass
            return service
        return None
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        return None


# ============================================
# TRACKABLE LINKS (Affiliate Links)
# ============================================


def get_affiliate_links(influencer_id: Optional[str] = None) -> List[Dict]:
    """Récupère les liens d'affiliation"""
    try:
        query = supabase.table("trackable_links").select(
            """
            *,
            products:product_id (
                name,
                category,
                price
            ),
            influencers:influencer_id (
                username,
                full_name
            )
        """
        )

        if influencer_id:
            query = query.eq("influencer_id", influencer_id)

        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting affiliate links: {e}")
        return []


def create_affiliate_link(product_id: str, influencer_id: str, unique_code: str) -> Optional[Dict]:
    """Crée un nouveau lien d'affiliation ou retourne le lien existant"""
    try:
        # Check if link already exists
        existing_link = (
            supabase.table("trackable_links")
            .select("*")
            .eq("product_id", product_id)
            .eq("influencer_id", influencer_id)
            .execute()
        )

        if existing_link.data:
            logger.info(f"Link already exists for product {product_id} and influencer {influencer_id}")
            return existing_link.data[0]

        # Create new link if it doesn't exist
        link_data = {
            "product_id": product_id,
            "influencer_id": influencer_id,
            "unique_code": unique_code,
            "full_url": f"https://shareyoursales.com/track/{unique_code}",
            "short_url": f"shs.io/{unique_code[:8]}",
            "is_active": True,
        }

        result = supabase.table("trackable_links").insert(link_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating affiliate link: {e}")
        return None


# ============================================
# CAMPAIGNS
# ============================================


def get_all_campaigns(merchant_id: Optional[str] = None) -> List[Dict]:
    """Récupère toutes les campagnes"""
    try:
        query = supabase.table("campaigns").select(
            """
            *,
            merchants:merchant_id (
                company_name
            )
        """
        )

        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        return []


def create_campaign(merchant_id: str, name: str, **kwargs) -> Optional[Dict]:
    """Crée une nouvelle campagne"""
    try:
        campaign_data = {
            "merchant_id": merchant_id,
            "name": name,
            "description": kwargs.get("description"),
            "budget": kwargs.get("budget"),
            "start_date": kwargs.get("start_date"),
            "end_date": kwargs.get("end_date"),
            "status": kwargs.get("status", "draft"),
        }

        result = supabase.table("campaigns").insert(campaign_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return None


# ============================================
# ANALYTICS
# ============================================


def get_dashboard_stats(role: str, user_id: str) -> Dict:
    """Récupère les statistiques pour le dashboard selon le rôle"""
    try:
        if role == "admin":
            # Stats admin depuis la table users
            users_count = supabase.table("users").select("id", count="exact").execute().count or 0
            
            # Compter les merchants
            merchants_count = (
                supabase.table("users").select("id", count="exact").eq("role", "merchant").execute().count or 0
            )
            
            # Compter les influencers
            influencers_count = (
                supabase.table("users").select("id", count="exact").eq("role", "influencer").execute().count or 0
            )
            
            # Compter les produits
            products_count = supabase.table("products").select("id", count="exact").execute().count or 0

            # Compter les services
            services_count = supabase.table("services").select("id", count="exact").execute().count or 0

            # Revenue total (sum des sales)
            sales = supabase.table("sales").select("amount").eq("status", "completed").execute()
            total_revenue = sum([float(s.get("amount", 0)) for s in sales.data]) if sales.data else 0

            return {
                "total_users": users_count,
                "total_merchants": merchants_count,
                "total_influencers": influencers_count,
                "total_products": products_count,
                "total_services": services_count,
                "total_revenue": total_revenue,
            }

        elif role == "merchant":
            # Stats merchant
            merchant = get_merchant_by_user_id(user_id)
            if not merchant:
                return {}

            products_count = (
                supabase.table("products")
                .select("id", count="exact")
                .eq("merchant_id", merchant["id"])
                .execute()
                .count
            )

            sales = (
                supabase.table("sales")
                .select("amount")
                .eq("merchant_id", merchant["id"])
                .eq("status", "completed")
                .execute()
            )
            total_sales = sum([s["amount"] for s in sales.data]) if sales.data else 0

            return {
                "total_sales": total_sales,
                "products_count": products_count,
                "affiliates_count": 0,  # À implémenter
                "roi": 320.5,
            }

        elif role == "influencer":
            # Stats influencer - CORRIGÉ pour utiliser les vraies tables
            try:
                # Récupérer l'influencer_id depuis la table users (colonne influencer_id)
                user_result = supabase.table("users").select("influencer_id, id").eq("id", user_id).single().execute()
                if not user_result.data:
                    return {}
                
                influencer_id = user_result.data.get("influencer_id") or user_result.data.get("id")
                
                # Stats depuis la table conversions (remplace click_tracking)
                conversions_result = supabase.table("conversions").select("*").eq("influencer_id", influencer_id).execute()
                conversions = conversions_result.data if conversions_result.data else []
                
                # Compter les clics (chaque conversion = 1 clic)
                total_clicks = len(conversions)
                
                # Compter les ventes (conversions avec status = 'completed')
                total_sales = len([c for c in conversions if c.get("status") == "completed"])
                
                # Calculer les earnings depuis les conversions
                total_earnings = sum([float(c.get("commission_amount", 0)) for c in conversions if c.get("status") == "completed"])
                
                # Calculer le balance: earnings - payouts payés
                payouts_result = supabase.table("payouts").select("amount").eq("influencer_id", influencer_id).eq("status", "paid").execute()
                payouts = payouts_result.data if payouts_result.data else []
                total_paid = sum([float(p.get("amount", 0)) for p in payouts])
                balance = total_earnings - total_paid
                
                # Calculer les croissances (comparaison 30 derniers jours vs 30 jours précédents)
                from datetime import datetime, timedelta
from utils.logger import logger
                now = datetime.now()
                thirty_days_ago = now - timedelta(days=30)
                sixty_days_ago = now - timedelta(days=60)
                
                # Conversions des 30 derniers jours
                recent_conversions = [c for c in conversions if datetime.fromisoformat(c.get("created_at", "1970-01-01").replace("Z", "+00:00")) >= thirty_days_ago]
                previous_conversions = [c for c in conversions if sixty_days_ago <= datetime.fromisoformat(c.get("created_at", "1970-01-01").replace("Z", "+00:00")) < thirty_days_ago]
                
                # Calcul des croissances
                earnings_growth = 0
                if len(previous_conversions) > 0:
                    recent_earnings = sum([float(c.get("commission_amount", 0)) for c in recent_conversions if c.get("status") == "completed"])
                    previous_earnings = sum([float(c.get("commission_amount", 0)) for c in previous_conversions if c.get("status") == "completed"])
                    if previous_earnings > 0:
                        earnings_growth = ((recent_earnings - previous_earnings) / previous_earnings) * 100
                
                clicks_growth = 0
                if len(previous_conversions) > 0:
                    clicks_growth = ((len(recent_conversions) - len(previous_conversions)) / len(previous_conversions)) * 100
                
                sales_growth = 0
                recent_sales = len([c for c in recent_conversions if c.get("status") == "completed"])
                previous_sales = len([c for c in previous_conversions if c.get("status") == "completed"])
                if previous_sales > 0:
                    sales_growth = ((recent_sales - previous_sales) / previous_sales) * 100
                
                return {
                    "total_earnings": total_earnings,
                    "total_clicks": total_clicks,
                    "total_sales": total_sales,
                    "balance": balance,
                    "earnings_growth": round(earnings_growth, 2),
                    "clicks_growth": round(clicks_growth, 2),
                    "sales_growth": round(sales_growth, 2)
                }
            except Exception as e:
                logger.error(f"Error getting influencer stats: {e}")
                return {
                    "total_earnings": 0,
                    "total_clicks": 0,
                    "total_sales": 0,
                    "balance": 0,
                    "earnings_growth": 0,
                    "clicks_growth": 0,
                    "sales_growth": 0
                }

        return {}

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return {}


# ============================================
# CONVERSIONS & SALES
# ============================================


def get_conversions(limit: int = 20) -> List[Dict]:
    """Récupère les conversions récentes"""
    try:
        result = (
            supabase.table("sales")
            .select(
                """
            *,
            products:product_id (
                name
            ),
            influencers:influencer_id (
                full_name,
                username
            ),
            merchants:merchant_id (
                company_name
            )
        """
            )
            .order("sale_timestamp", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data
    except Exception as e:
        logger.error(f"Error getting conversions: {e}")
        return []


# ============================================
# CLICKS TRACKING
# ============================================


def get_clicks(limit: int = 50) -> List[Dict]:
    """Récupère les clics récents"""
    try:
        result = (
            supabase.table("click_tracking")
            .select(
                """
            *,
            trackable_links:link_id (
                unique_code,
                products:product_id (
                    name
                ),
                influencers:influencer_id (
                    username
                )
            )
        """
            )
            .order("clicked_at", desc=True)
            .limit(limit)
            .execute()
        )

        return result.data
    except Exception as e:
        logger.error(f"Error getting clicks: {e}")
        return []


# ============================================
# PAYOUTS
# ============================================


def get_payouts() -> List[Dict]:
    """Récupère tous les payouts"""
    try:
        result = (
            supabase.table("commissions")
            .select(
                """
            *,
            influencers:influencer_id (
                full_name,
                username
            )
        """
            )
            .execute()
        )

        return result.data
    except Exception as e:
        logger.error(f"Error getting payouts: {e}")
        return []


def update_payout_status(payout_id: str, status: str) -> bool:
    """Met à jour le statut d'un payout"""
    try:
        if status in {"approved", "paid", "rejected", "pending"}:
            result = supabase.rpc(
                "approve_payout_transaction", {"p_commission_id": payout_id, "p_status": status}
            ).execute()
            data = result.data
            if isinstance(data, list):
                return bool(data and data[0])
            return bool(data)

        update_data = {"status": status}
        supabase.table("commissions").update(update_data).eq("id", payout_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating payout status: {e}")
        return False
