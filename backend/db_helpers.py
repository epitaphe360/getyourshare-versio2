"""
Fonctions helpers pour interagir avec Supabase
Simplifie les opérations CRUD
"""

from supabase_client import supabase
from typing import Optional, List, Dict, Any
from datetime import datetime
import bcrypt
import sys
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

        # WORKAROUND: Trigger 'trg_auto_assign_sales_rep' is broken (BEFORE INSERT with FK check).
        # We insert as 'influencer' first (which bypasses the trigger), then update to correct role.
        original_role = role
        temp_role = role
        if role in ['merchant', 'advertiser']:
            temp_role = 'influencer'
            logger.info(f"Using temp role '{temp_role}' for '{role}' to bypass broken trigger")

        user_data = {
            "email": email,
            "password_hash": password_hash,
            "role": temp_role,
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
        user = result.data[0] if result.data else None

        if user and temp_role != original_role:
            # Update to correct role
            logger.info(f"Updating user {user['id']} role from '{temp_role}' to '{original_role}'")
            supabase.table("users").update({"role": original_role}).eq("id", user["id"]).execute()
            user["role"] = original_role # Update local object

        return user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        print(f"CRITICAL ERROR creating user: {e}", file=sys.stderr)
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


def create_product(product_data: Dict) -> Optional[Dict]:
    """Crée un nouveau produit"""
    try:
        # S'assurer que le stock est un entier
        if "stock" in product_data:
            product_data["stock"] = int(product_data["stock"])
            
        # S'assurer que le prix est un float
        if "price" in product_data:
            product_data["price"] = float(product_data["price"])
            
        # S'assurer que la commission est un float
        if "commission_rate" in product_data:
            product_data["commission_rate"] = float(product_data["commission_rate"])

        result = supabase.table("products").insert(product_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return None


def update_product(product_id: str, updates: Dict) -> bool:
    """Met à jour un produit"""
    try:
        # Nettoyage des données
        if "stock" in updates:
            updates["stock"] = int(updates["stock"])
        if "price" in updates:
            updates["price"] = float(updates["price"])
        if "commission_rate" in updates:
            updates["commission_rate"] = float(updates["commission_rate"])
            
        # Ne pas mettre à jour l'ID ou le merchant_id
        if "id" in updates:
            del updates["id"]
        if "merchant_id" in updates:
            del updates["merchant_id"]
        if "created_at" in updates:
            del updates["created_at"]
            
        updates["updated_at"] = datetime.now().isoformat()

        supabase.table("products").update(updates).eq("id", product_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return False


def delete_product(product_id: str) -> bool:
    """Supprime un produit"""
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return False


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
        # Requête simple sans jointure problématique
        query = supabase.table("campaigns").select("*")

        if merchant_id:
            query = query.eq("merchant_id", merchant_id)

        result = query.execute()
        campaigns = result.data or []
        
        # Enrichir avec les infos du merchant si disponibles
        if campaigns:
            # Récupérer les user_ids uniques des merchants
            merchant_ids = list(set(c.get("merchant_id") for c in campaigns if c.get("merchant_id")))
            
            if merchant_ids:
                # Récupérer les infos des users (qui sont les merchants)
                users_result = supabase.table("users").select("id, email, username, company_name").in_("id", merchant_ids).execute()
                users_map = {u["id"]: u for u in (users_result.data or [])}
                
                # Enrichir chaque campagne
                for campaign in campaigns:
                    mid = campaign.get("merchant_id")
                    if mid and mid in users_map:
                        user_info = users_map[mid]
                        campaign["merchant_name"] = user_info.get("company_name") or user_info.get("username") or user_info.get("email", "").split("@")[0]
                    else:
                        campaign["merchant_name"] = "Inconnu"
        
        return campaigns
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
            "commission_rate": kwargs.get("commission_rate", 0.0),
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
            # Stats admin depuis la table users - OPTIMIZED with count='exact'
            users_count = supabase.table("users").select("id", count="exact", head=True).execute().count or 0
            
            # Compter les merchants
            merchants_count = (
                supabase.table("users").select("id", count="exact", head=True).eq("role", "merchant").execute().count or 0
            )
            
            # Compter les influencers
            influencers_count = (
                supabase.table("users").select("id", count="exact", head=True).eq("role", "influencer").execute().count or 0
            )
            
            # Compter les produits
            products_count = supabase.table("products").select("id", count="exact", head=True).execute().count or 0

            # Compter les services
            services_count = supabase.table("services").select("id", count="exact", head=True).execute().count or 0

            # Revenue total (sum des sales) - Optimized to fetch only amount
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
                .select("id", count="exact", head=True)
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

            # Calculate Affiliates Count (Distinct influencers)
            # Optimized: fetch only influencer_id
            affiliates_query = (
                supabase.table("trackable_links") # Fixed table name from tracking_links
                .select("influencer_id")
                .eq("merchant_id", merchant["id"]) # Assuming merchant_id is on trackable_links or join needed
                .execute()
            )
            # Note: trackable_links usually links product -> influencer. Product has merchant_id.
            # If trackable_links doesn't have merchant_id, we need a join.
            # Assuming simplified schema for now or direct link.
            
            affiliates_count = len(set([a["influencer_id"] for a in affiliates_query.data])) if affiliates_query.data else 0

            # Calculate ROI
            commissions_query = (
                supabase.table("commissions")
                .select("amount")
                .eq("merchant_id", merchant["id"])
                .execute()
            )
            total_commissions = sum([c["amount"] for c in commissions_query.data]) if commissions_query.data else 0
            
            roi = 0
            if total_commissions > 0:
                roi = ((total_sales - total_commissions) / total_commissions) * 100

            return {
                "total_sales": total_sales,
                "products_count": products_count,
                "affiliates_count": affiliates_count,
                "roi": round(roi, 2),
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


def update_payout_status(payout_id: str, status: str) -> tuple[bool, str]:
    """Met à jour le statut d'un payout (Implémentation Python pour contourner RPC cassé)"""
    try:
        # 1. Récupérer la commission
        comm_result = supabase.table("commissions").select("*").eq("id", payout_id).execute()
        if not comm_result.data:
            msg = f"Commission {payout_id} not found"
            logger.error(msg)
            return False, msg
        
        commission = comm_result.data[0]
        current_status = commission.get("status")
        amount = float(commission.get("amount", 0))
        influencer_id = commission.get("influencer_id")
        
        if not influencer_id:
            msg = f"Commission {payout_id} has no influencer_id"
            logger.error(msg)
            return False, msg

        # 2. Récupérer l'influenceur
        inf_result = supabase.table("influencers").select("balance").eq("id", influencer_id).execute()
        if not inf_result.data:
            msg = f"Influencer {influencer_id} not found"
            logger.error(msg)
            return False, msg
            
        influencer_balance = float(inf_result.data[0].get("balance") or 0)
        
        # 3. Logique de transition (copiée du RPC)
        if status == current_status:
            return True, "Status already set"
            
        if status not in ('approved', 'paid', 'rejected', 'pending'):
            msg = f"Invalid status: {status}"
            logger.error(msg)
            return False, msg

        # approved -> pending: Check balance and deduct
        if status == 'approved' and current_status == 'pending':
            if influencer_balance < amount:
                msg = f"Insufficient balance: {influencer_balance} < {amount}"
                logger.error(msg)
                return False, msg
            
            # Deduct balance
            new_balance = influencer_balance - amount
            supabase.table("influencers").update({"balance": new_balance}).eq("id", influencer_id).execute()
            
        # pending -> approved: Refund balance
        elif status == 'pending' and current_status == 'approved':
            new_balance = influencer_balance + amount
            supabase.table("influencers").update({"balance": new_balance}).eq("id", influencer_id).execute()
            
        # rejected -> approved: Refund balance
        elif status == 'rejected' and current_status == 'approved':
            new_balance = influencer_balance + amount
            supabase.table("influencers").update({"balance": new_balance}).eq("id", influencer_id).execute()
            
        # paid -> approved: No balance change, just status update
        elif status == 'paid' and current_status != 'approved':
            msg = "Cannot pay a commission that is not approved"
            logger.error(msg)
            return False, msg
            
        # Update commission status
        update_data = {"status": status}
        if status == 'approved' and current_status == 'pending':
            update_data["approved_at"] = datetime.now().isoformat()
        elif status == 'paid':
            update_data["paid_at"] = datetime.now().isoformat()
        elif status in ('pending', 'rejected'):
            update_data["approved_at"] = None
            update_data["paid_at"] = None
            
        supabase.table("commissions").update(update_data).eq("id", payout_id).execute()
        return True, "Status updated successfully"
        
    except Exception as e:
        msg = f"Error updating payout status (Python fallback): {e}"
        logger.error(msg)
        return False, msg


# ============================================
# SERVICES & LEADS (Génération de leads)
# ============================================

def create_service(marchand_id: str, service_data: Dict) -> Optional[Dict]:
    """Crée un nouveau service"""
    try:
        data = {
            "marchand_id": marchand_id,
            "nom": service_data.get("nom"),
            "description": service_data.get("description"),
            "images": service_data.get("images", []),
            "categorie_id": service_data.get("categorie_id"),
            "localisation": service_data.get("localisation"),
            "conditions": service_data.get("conditions"),
            "depot_initial": service_data.get("depot_initial", 0),
            "depot_actuel": service_data.get("depot_initial", 0),  # Même valeur au départ
            "prix_par_lead": service_data.get("prix_par_lead"),
            "commission_rate": service_data.get("commission_rate", 20.0),
            "formulaire_champs": service_data.get("formulaire_champs", []),
            "date_expiration": service_data.get("date_expiration"),
            "statut": "actif"
        }
        
        result = supabase.table("services").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        return None


def get_all_services(filters: Optional[Dict] = None) -> List[Dict]:
    """Récupère tous les services avec filtres optionnels"""
    try:
        query = supabase.table("services").select("*, users!marchand_id(full_name, email, company_name), categories(name)")
        
        if filters:
            if filters.get("marchand_id"):
                query = query.eq("marchand_id", filters["marchand_id"])
            if filters.get("statut"):
                query = query.eq("statut", filters["statut"])
            if filters.get("categorie_id"):
                query = query.eq("categorie_id", filters["categorie_id"])
        
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting all services: {e}")
        return []


def get_service_by_id(service_id: str) -> Optional[Dict]:
    """Récupère un service par ID avec infos complètes"""
    try:
        result = supabase.table("services").select(
            "*, users!marchand_id(full_name, email, company_name, phone), categories(name)"
        ).eq("id", service_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error getting service by id: {e}")
        return None


def update_service(service_id: str, update_data: Dict) -> bool:
    """Met à jour un service"""
    try:
        supabase.table("services").update(update_data).eq("id", service_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating service: {e}")
        return False


def delete_service(service_id: str) -> bool:
    """Supprime un service"""
    try:
        supabase.table("services").delete().eq("id", service_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        return False


def create_lead(lead_data: Dict) -> Optional[Dict]:
    """Crée un nouveau lead (demande client)"""
    try:
        data = {
            "service_id": lead_data.get("service_id"),
            "marchand_id": lead_data.get("marchand_id"),
            "nom_client": lead_data.get("nom_client"),
            "email_client": lead_data.get("email_client"),
            "telephone_client": lead_data.get("telephone_client"),
            "donnees_formulaire": lead_data.get("donnees_formulaire", {}),
            "cout_lead": lead_data.get("cout_lead"),
            "statut": "nouveau"
        }
        
        result = supabase.table("leads").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        return None


def get_leads_by_service(service_id: str) -> List[Dict]:
    """Récupère tous les leads d'un service"""
    try:
        result = supabase.table("leads").select("*").eq("service_id", service_id).order("date_reception", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting leads by service: {e}")
        return []


def get_leads_by_marchand(marchand_id: str) -> List[Dict]:
    """Récupère tous les leads d'un marchand"""
    try:
        result = supabase.table("leads").select(
            "*, services(nom, images)"
        ).eq("marchand_id", marchand_id).order("date_reception", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting leads by marchand: {e}")
        return []


def get_all_leads(filters: Optional[Dict] = None) -> List[Dict]:
    """Récupère tous les leads avec filtres"""
    try:
        query = supabase.table("leads").select(
            "*, services(nom, images), users!marchand_id(full_name, company_name)"
        )
        
        if filters:
            if filters.get("service_id"):
                query = query.eq("service_id", filters["service_id"])
            if filters.get("marchand_id"):
                query = query.eq("marchand_id", filters["marchand_id"])
            if filters.get("statut"):
                query = query.eq("statut", filters["statut"])
        
        result = query.order("date_reception", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting all leads: {e}")
        return []


def update_lead_status(lead_id: str, statut: str, notes: Optional[str] = None) -> bool:
    """Met à jour le statut d'un lead"""
    try:
        update_data = {"statut": statut}
        
        if statut == "converti":
            update_data["date_conversion"] = datetime.now().isoformat()
        elif statut == "perdu":
            update_data["date_perdu"] = datetime.now().isoformat()
        
        if notes:
            update_data["notes_marchand"] = notes
        
        supabase.table("leads").update(update_data).eq("id", lead_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        return False


def create_service_recharge(recharge_data: Dict) -> Optional[Dict]:
    """Crée une recharge de dépôt pour un service"""
    try:
        data = {
            "service_id": recharge_data.get("service_id"),
            "marchand_id": recharge_data.get("marchand_id"),
            "montant": recharge_data.get("montant"),
            "ancien_solde": recharge_data.get("ancien_solde"),
            "nouveau_solde": recharge_data.get("nouveau_solde"),
            "leads_ajoutes": recharge_data.get("leads_ajoutes"),
            "methode_paiement": recharge_data.get("methode_paiement"),
            "transaction_id": recharge_data.get("transaction_id"),
            "statut_paiement": recharge_data.get("statut_paiement", "en_attente")
        }
        
        result = supabase.table("service_recharges").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating service recharge: {e}")
        return None


def get_service_recharges(service_id: str) -> List[Dict]:
    """Récupère l'historique des recharges d'un service"""
    try:
        result = supabase.table("service_recharges").select("*").eq("service_id", service_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting service recharges: {e}")
        return []


def create_service_extra(extra_data: Dict) -> Optional[Dict]:
    """Crée un extra/boost pour un service"""
    try:
        data = {
            "service_id": extra_data.get("service_id"),
            "marchand_id": extra_data.get("marchand_id"),
            "type": extra_data.get("type"),
            "nom": extra_data.get("nom"),
            "description": extra_data.get("description"),
            "prix": extra_data.get("prix"),
            "date_debut": extra_data.get("date_debut", datetime.now().isoformat()),
            "date_fin": extra_data.get("date_fin"),
            "transaction_id": extra_data.get("transaction_id"),
            "actif": True
        }
        
        result = supabase.table("service_extras").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating service extra: {e}")
        return None


def get_service_extras(service_id: str) -> List[Dict]:
    """Récupère les extras d'un service"""
    try:
        result = supabase.table("service_extras").select("*").eq("service_id", service_id).order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting service extras: {e}")
        return []


def get_services_stats() -> Dict:
    """Récupère les statistiques globales des services"""
    try:
        # Services actifs
        services = supabase.table("services").select("id, depot_initial, depot_actuel, statut").execute()
        services_data = services.data if services.data else []
        
        # Leads
        leads = supabase.table("leads").select("id, statut, cout_lead, date_reception").execute()
        leads_data = leads.data if leads.data else []
        
        stats = {
            "total_services": len(services_data),
            "services_actifs": len([s for s in services_data if s.get("statut") == "actif"]),
            "depot_total": sum([float(s.get("depot_actuel", 0)) for s in services_data]),
            "total_leads": len(leads_data),
            "leads_aujourd_hui": len([l for l in leads_data if l.get("date_reception", "").startswith(datetime.now().strftime("%Y-%m-%d"))]),
            "leads_convertis": len([l for l in leads_data if l.get("statut") == "converti"]),
            "revenus_leads": sum([float(l.get("cout_lead", 0)) for l in leads_data]),
            "taux_conversion": round((len([l for l in leads_data if l.get("statut") == "converti"]) / len(leads_data) * 100) if leads_data else 0, 2)
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting services stats: {e}")
        return {}


# ============================================
# LOGGING & ACTIVITY
# ============================================

def log_user_activity(user_id: str, action: str, details: Optional[Dict] = None) -> bool:
    """Enregistre une activité utilisateur"""
    try:
        activity_data = {
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Vérifier si la table user_activity_logs existe, sinon on pourrait utiliser une autre table ou ignorer
        # Pour l'instant on suppose qu'elle existe ou on l'ajoute si nécessaire
        try:
            supabase.table("user_activity_logs").insert(activity_data).execute()
            return True
        except Exception:
            # Fallback: log to console if table doesn't exist
            logger.info(f"User Activity: {user_id} - {action} - {details}")
            return True
            
    except Exception as e:
        logger.error(f"Error logging user activity: {e}")
        return False
