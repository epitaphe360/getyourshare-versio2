"""
Fonctions helpers pour interagir avec Supabase
Simplifie les opérations CRUD
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime
import bcrypt
from utils.logger import logger

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
        # Optimized query with join
        query = supabase.table("products").select("*, merchants:merchant_id(company_name, email)")

        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        products = result.data if result.data else []
        
        # Map 'merchants' to 'merchant' for compatibility
        for product in products:
            if product.get("merchants"):
                product["merchant"] = product["merchants"]
                # del product["merchants"] # Keep it just in case
        
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
        # Optimized query with join
        query = supabase.table("services").select("*, merchants:merchant_id(company_name, email)")

        if category:
            query = query.eq("category", category)
        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        
        services = result.data if result.data else []
        
        # Pour chaque service, mapper les champs pour le frontend
        for service in services:
            # Mapping des champs pour compatibilité frontend
            service["price_per_lead"] = service.get("price", 0)
            service["is_available"] = service.get("is_active", True)
            
            # Gestion des images
            if service.get("image_url"):
                service["images"] = [service["image_url"]]
            else:
                service["images"] = []
                
            # Champs manquants dans la DB mais attendus par le frontend
            service["capacity_per_month"] = service.get("capacity", 100) # Valeur par défaut
            service["total_leads"] = 0 # À calculer via une jointure avec la table leads si elle existe
            
            if service.get("merchants"):
                service["merchant"] = service["merchants"]
        
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
                    user_result = supabase.table("users").select("id, company_name, email, phone, username").eq("id", service["merchant_id"]).single().execute()
                    if user_result.data:
                        service["merchant"] = {
                            "id": user_result.data.get("id"),
                            "company_name": user_result.data.get("company_name"),
                            "email": user_result.data.get("email"),
                            "phone": user_result.data.get("phone"),
                            "username": user_result.data.get("username")
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
            # Stats influencer - OPTIMIZED
            try:
                influencer_id = user_id
                
                # 1. Total Clicks (Count only)
                clicks_query = supabase.table("conversions").select("id", count="exact", head=True).eq("influencer_id", influencer_id).execute()
                total_clicks = clicks_query.count or 0
                
                # 2. Total Sales & Earnings (Fetch only necessary columns for completed sales)
                sales_query = supabase.table("conversions").select("commission_amount").eq("influencer_id", influencer_id).eq("status", "completed").execute()
                sales_data = sales_query.data if sales_query.data else []
                total_sales = len(sales_data)
                total_earnings = sum([float(s.get("commission_amount", 0)) for s in sales_data])
                
                # 3. Balance (Earnings - Paid Payouts)
                payouts_query = supabase.table("payouts").select("amount").eq("influencer_id", influencer_id).eq("status", "paid").execute()
                total_paid = sum([float(p.get("amount", 0)) for p in payouts_query.data]) if payouts_query.data else 0
                balance = total_earnings - total_paid
                
                # 4. Growth Stats (Fetch only last 60 days)
                from datetime import datetime, timedelta, timezone
                now = datetime.now(timezone.utc)
                sixty_days_ago = (now - timedelta(days=60)).isoformat()
                
                # Fetch recent conversions (last 60 days only)
                recent_query = supabase.table("conversions").select("created_at, status, commission_amount").eq("influencer_id", influencer_id).gte("created_at", sixty_days_ago).execute()
                recent_data = recent_query.data if recent_query.data else []
                
                # Process in Python (much smaller dataset)
                thirty_days_ago_dt = now - timedelta(days=30)
                
                recent_conversions = []
                previous_conversions = []
                
                for c in recent_data:
                    try:
                        created_at_str = c.get("created_at")
                        if isinstance(created_at_str, str):
                            created_at_str = created_at_str.replace("Z", "+00:00")
                            created_at = datetime.fromisoformat(created_at_str)
                        else:
                            created_at = created_at_str
                            
                        if created_at.tzinfo is None:
                            created_at = created_at.replace(tzinfo=timezone.utc)
                            
                        if created_at >= thirty_days_ago_dt:
                            recent_conversions.append(c)
                        else:
                            previous_conversions.append(c)
                    except Exception:
                        continue

                # Calculate Growth %
                earnings_growth = 0
                recent_earnings_val = sum([float(c.get("commission_amount", 0)) for c in recent_conversions if c.get("status") == "completed"])
                previous_earnings_val = sum([float(c.get("commission_amount", 0)) for c in previous_conversions if c.get("status") == "completed"])
                
                if previous_earnings_val > 0:
                    earnings_growth = ((recent_earnings_val - previous_earnings_val) / previous_earnings_val) * 100
                
                clicks_growth = 0
                if len(previous_conversions) > 0:
                    clicks_growth = ((len(recent_conversions) - len(previous_conversions)) / len(previous_conversions)) * 100
                
                sales_growth = 0
                recent_sales_count = len([c for c in recent_conversions if c.get("status") == "completed"])
                previous_sales_count = len([c for c in previous_conversions if c.get("status") == "completed"])
                
                if previous_sales_count > 0:
                    sales_growth = ((recent_sales_count - previous_sales_count) / previous_sales_count) * 100
                
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
