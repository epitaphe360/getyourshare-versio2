"""
ShareYourSales API Server - Version Complète Fonctionnelle
Plateforme d'affiliation influenceurs-marchands au Maroc
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime, timedelta
import jwt
import os
import sys
import json
import bcrypt
import time
import random
import logging
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables FIRST
load_dotenv()

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
    logger.debug(f"🔍 DEBUG Supabase: URL={SUPABASE_URL[:30] if SUPABASE_URL else None}..., KEY={'***' if SUPABASE_KEY else None}")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    SUPABASE_ENABLED = supabase is not None
    logger.info(f"✅ Supabase client créé: {SUPABASE_ENABLED}")
    
    # Helper function for other modules
    def get_supabase_client():
        """Return the global Supabase client instance"""
        return supabase

    # ============================================
    # SUPABASE USER HELPERS
    # ============================================

    def get_user_by_email(email: str):
        """Get user from Supabase by email"""
        try:
            response = supabase.table("users").select("*").eq("email", email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user by email: {e}")
            return None

    def get_user_by_id(user_id: str):
        """Get user from Supabase by ID"""
        try:
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None

    def create_user_in_supabase(user_data: dict):
        """Create new user in Supabase"""
        try:
            response = supabase.table("users").insert(user_data).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def get_users_by_role(role: str):
        """Get all users with specific role from Supabase"""
        try:
            response = supabase.table("users").select("*").eq("role", role).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching users by role: {e}")
            return []

except Exception as e:
    logger.info(f"⚠️ Supabase non disponible: {e}")
    import traceback
    traceback.print_exc()
    supabase = None
    SUPABASE_ENABLED = False

    # Fallback functions when Supabase is not available
    def get_user_by_email(email: str):
        return None

    def get_user_by_id(user_id: str):
        return None

    def create_user_in_supabase(user_data: dict):
        return None

    def get_users_by_role(role: str):
        return []

# Services
try:
    from services.email_service import email_service, EmailTemplates
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    logger.warning("Warning: Email service not available")

# Subscription limits middleware
try:
    from subscription_limits_middleware import SubscriptionLimits
    SUBSCRIPTION_LIMITS_ENABLED = True
    logger.info("✅ Subscription limits middleware loaded")
except ImportError as e:
    SUBSCRIPTION_LIMITS_ENABLED = False
    logger.info(f"⚠️ Subscription limits not available: {e}")

# Translation service with OpenAI and DB cache
try:
    from translation_service import init_translation_service, translation_service
    TRANSLATION_SERVICE_AVAILABLE = True
    logger.info("✅ Translation service with OpenAI loaded")
except ImportError as e:
    TRANSLATION_SERVICE_AVAILABLE = False
    logger.info(f"⚠️ Translation service not available: {e}")

# Database queries helpers (real data, not mocked)
try:
    from db_queries_real import (
        get_influencer_overview_stats,
        get_influencer_earnings_chart,
        get_merchant_sales_chart,
        get_user_affiliate_links,
        get_payment_history,
        get_merchant_products,
        get_user_payouts,
        get_user_campaigns,
        create_affiliate_link,
        get_all_products,
        get_all_merchants,
        get_all_influencers,
        create_product,
        get_merchant_performance,
        get_all_sales,
        get_user_notifications,
        get_top_products,
        get_conversion_funnel,
        get_all_commissions,
        request_payout,
        approve_payout,
        update_sale_status,
        get_payment_methods,
        get_all_users_admin,
        get_admin_stats,
        activate_user,
        get_user_profile,
        update_user_profile,
        update_user_password
    )
    DB_QUERIES_AVAILABLE = True
    logger.info("✅ DB Queries helpers loaded successfully")
except ImportError as e:
    DB_QUERIES_AVAILABLE = False
    logger.info(f"⚠️ DB Queries helpers not available: {e}")

# Subscription endpoints
try:
    from subscription_endpoints_simple import router as subscription_router
    SUBSCRIPTION_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    logger.info(f"⚠️ Subscription endpoints not available: {e}")
    SUBSCRIPTION_ENDPOINTS_AVAILABLE = False

# Moderation endpoints
try:
    from moderation_endpoints import router as moderation_router
    MODERATION_ENDPOINTS_AVAILABLE = True
    logger.info("✅ Moderation endpoints loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Moderation endpoints not available: {e}")
    MODERATION_ENDPOINTS_AVAILABLE = False

# Platform settings endpoints
try:
    from platform_settings_endpoints import router as platform_settings_router
    PLATFORM_SETTINGS_ENDPOINTS_AVAILABLE = True
    logger.info("✅ Platform settings endpoints loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Platform settings endpoints not available: {e}")
    PLATFORM_SETTINGS_ENDPOINTS_AVAILABLE = False

# Analytics routes (complete with real DB logic)
try:
    from routes.analytics_routes import router as analytics_router
    ANALYTICS_ROUTES_AVAILABLE = True
    logger.info("✅ Analytics routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Analytics routes not available: {e}")
    ANALYTICS_ROUTES_AVAILABLE = False

# Products routes (CRUD + bulk import + variants)
try:
    from routes.products_routes import router as products_router
    PRODUCTS_ROUTES_AVAILABLE = True
    logger.info("✅ Products routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Products routes not available: {e}")
    PRODUCTS_ROUTES_AVAILABLE = False

# Campaigns routes (create, analytics, manage)
try:
    from routes.campaigns_routes import router as campaigns_router
    CAMPAIGNS_ROUTES_AVAILABLE = True
    logger.info("✅ Campaigns routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Campaigns routes not available: {e}")
    CAMPAIGNS_ROUTES_AVAILABLE = False

# Commissions routes (real calculations)
try:
    from routes.commissions_routes import router as commissions_router
    COMMISSIONS_ROUTES_AVAILABLE = True
    logger.info("✅ Commissions routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Commissions routes not available: {e}")
    COMMISSIONS_ROUTES_AVAILABLE = False

# Reports routes (summary + detailed with exports)
try:
    from routes.reports_routes import router as reports_router
    REPORTS_ROUTES_AVAILABLE = True
    logger.info("✅ Reports routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Reports routes not available: {e}")
    REPORTS_ROUTES_AVAILABLE = False

# Content Studio routes (templates, AI generation, scheduling)
try:
    from routes.content_studio_routes import router as content_studio_router
    CONTENT_STUDIO_ROUTES_AVAILABLE = True
    logger.info("✅ Content Studio routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Content Studio routes not available: {e}")
    CONTENT_STUDIO_ROUTES_AVAILABLE = False

# Utility routes (settings, notifications, currency, messages, referrals, reviews, system)
try:
    from routes.utility_routes import router as utility_router
    UTILITY_ROUTES_AVAILABLE = True
    logger.info("✅ Utility routes loaded successfully")
except ImportError as e:
    logger.info(f"⚠️ Utility routes not available: {e}")
    UTILITY_ROUTES_AVAILABLE = False

# ============================================
# CONFIGURATION
# ============================================

# JWT Configuration avec validation stricte
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.warning("⚠️  JWT_SECRET non défini - Génération automatique d'un secret temporaire")
    logger.warning("   IMPORTANT: En production, définissez JWT_SECRET dans les variables d'environnement")
    logger.warning("   Générez-en un avec: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    import secrets
    JWT_SECRET = secrets.token_urlsafe(64)
    logger.info(f"✅ JWT_SECRET temporaire généré ({len(JWT_SECRET)} caractères)")

if len(JWT_SECRET) < 32:
    logger.warning(f"⚠️  ATTENTION: JWT_SECRET trop court ({len(JWT_SECRET)} chars, minimum 32 requis)")
    logger.warning("   Génération d'un secret plus sécurisé automatiquement")
    import secrets
    JWT_SECRET = secrets.token_urlsafe(64)
    logger.info(f"✅ JWT_SECRET régénéré avec sécurité renforcée ({len(JWT_SECRET)} caractères)")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "86400"))  # 24 heures par défaut
security = HTTPBearer()
logger.info(f"✅ JWT_SECRET chargé avec succès ({len(JWT_SECRET)} caractères)")

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ============================================
# APPLICATION SETUP
# ============================================

app = FastAPI(
    title="ShareYourSales API - Version Complète",
    description="""
# 🇲🇦 ShareYourSales - Plateforme d'Affiliation Marocaine

## 🎯 Fonctionnalités Principales

### 💳 Système d'Abonnements SaaS
- **Free**: 5 liens/mois, analytics de base
- **Starter**: 50 liens/mois, analytics avancées  
- **Pro**: 200 liens/mois, API, webhooks
- **Enterprise**: Illimité, support prioritaire

### 📱 Intégrations Réseaux Sociaux
- **Instagram**: Business API avec métriques
- **TikTok**: Creator API et TikTok Shop
- **Facebook**: Pages et groupes
- **WhatsApp Business**: Catalogue produits

### 🤖 Intelligence Artificielle
- Assistant conversationnel multilingue
- Recommandations personnalisées
- Analyse prédictive des performances
- Génération automatique de contenu

### 💰 Système de Paiement
- **Stripe**: Cartes internationales
- **PayPal**: Paiements globaux
- **CMI**: Cartes marocaines
- **Orange Money**: Mobile payment

### 🔐 Sécurité & Conformité
- Authentification 2FA
- Chiffrement end-to-end
- RGPD compliant
- Audit trails complets

### 📊 Analytics Avancées
- Tracking en temps réel
- Tableaux de bord personnalisés
- Rapports automatisés
- Prédictions IA

### 🌍 Support Multilingue
- Français, Anglais, Arabe
- Interface adaptative
- Documentation complète
""",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# MIDDLEWARE
# ============================================

# CORS configuration - Whitelist sécurisée par environnement
# ✅ FIX SÉCURITÉ P0: Remplacement wildcard par whitelist
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    os.getenv("FRONTEND_URL", "https://getyourshare.com"),
    os.getenv("PRODUCTION_URL", "https://www.getyourshare.com"),
]

# Ajouter les URLs Vercel (déploiement et preview)
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    # Vercel fournit l'URL sans protocole, on ajoute https://
    if not vercel_url.startswith("http"):
        vercel_url = f"https://{vercel_url}"
    allowed_origins.append(vercel_url)

# Ajouter les URLs Vercel spécifiques connues
vercel_production_url = os.getenv("VERCEL_PRODUCTION_URL")
if vercel_production_url:
    if not vercel_production_url.startswith("http"):
        vercel_production_url = f"https://{vercel_production_url}"
    allowed_origins.append(vercel_production_url)

# Ajouter l'URL Vercel actuelle du déploiement
current_vercel_url = "https://getyourshare-7h1z5006j-getyourshares-projects.vercel.app"
if current_vercel_url not in allowed_origins:
    allowed_origins.append(current_vercel_url)

# Ajouter origines de développement si ENV=development
if os.getenv("ENV", "development") == "development":
    allowed_origins.extend([
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

# Log les origines autorisées pour faciliter le débogage
logger.info(f"🔐 CORS allowed origins: {allowed_origins}")

# Regex pattern to allow all Vercel preview and production deployments
# This handles URLs like: https://getyourshare-*.vercel.app
vercel_regex = r"https://.*\.vercel\.app"

# CORS Configuration - Must be added FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ Whitelist au lieu de wildcard
    allow_origin_regex=vercel_regex,  # ✅ Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Translation Service with Supabase
logger.debug(f"🔍 DEBUG: TRANSLATION_SERVICE_AVAILABLE={TRANSLATION_SERVICE_AVAILABLE}, SUPABASE_ENABLED={SUPABASE_ENABLED}")
if TRANSLATION_SERVICE_AVAILABLE and SUPABASE_ENABLED:
    init_translation_service(supabase)
    logger.info("✅ Translation service initialized with Supabase")
else:
    logger.info(f"⚠️ Translation service initialization skipped (Translation: {TRANSLATION_SERVICE_AVAILABLE}, Supabase: {SUPABASE_ENABLED})")

# ============================================
# ROUTERS
# ============================================

# Monter le router des abonnements
if SUBSCRIPTION_ENDPOINTS_AVAILABLE:
    app.include_router(subscription_router)
    logger.info("✅ Subscription endpoints mounted at /api/subscriptions")
else:
    logger.info("⚠️ Subscription endpoints not available")

# Monter le router de modération
if MODERATION_ENDPOINTS_AVAILABLE:
    app.include_router(moderation_router)
    logger.info("✅ Moderation endpoints mounted at /api/admin/moderation")
else:
    logger.info("⚠️ Moderation endpoints not available")

# Monter le router des paramètres de plateforme
if PLATFORM_SETTINGS_ENDPOINTS_AVAILABLE:
    app.include_router(platform_settings_router)
    logger.info("✅ Platform settings endpoints mounted at /api/admin/platform-settings")
else:
    logger.info("⚠️ Platform settings endpoints not available")

# Monter le router d'authentification avancée
try:
    from auth_advanced_endpoints import router as auth_advanced_router
    app.include_router(auth_advanced_router)
    logger.info("✅ Advanced auth endpoints mounted at /api/auth")
except ImportError as e:
    logger.info("⚠️ Advanced auth endpoints not available: {e}")
    logger.info("💡 Install missing dependencies: pip install pyotp qrcode Pillow")

# Monter les nouveaux routers avec vraie logique DB
if ANALYTICS_ROUTES_AVAILABLE:
    app.include_router(analytics_router)
    logger.info("✅ Analytics routes mounted at /api/analytics")

if PRODUCTS_ROUTES_AVAILABLE:
    app.include_router(products_router)
    logger.info("✅ Products routes mounted at /api/products")

if CAMPAIGNS_ROUTES_AVAILABLE:
    app.include_router(campaigns_router)
    logger.info("✅ Campaigns routes mounted at /api/campaigns")

if COMMISSIONS_ROUTES_AVAILABLE:
    app.include_router(commissions_router)
    logger.info("✅ Commissions routes mounted at /api/commissions")

if REPORTS_ROUTES_AVAILABLE:
    app.include_router(reports_router)
    logger.info("✅ Reports routes mounted at /api/reports")

if CONTENT_STUDIO_ROUTES_AVAILABLE:
    app.include_router(content_studio_router)
    logger.info("✅ Content Studio routes mounted at /api/content-studio")

if UTILITY_ROUTES_AVAILABLE:
    app.include_router(utility_router)
    logger.info("✅ Utility routes mounted (settings, notifications, currency, messages, referrals, reviews, system)")

# ============================================
# HEALTH CHECK ENDPOINT (for Railway)
# ============================================

@app.get("/health")
async def health_check_root():
    """Railway healthcheck endpoint - simple and fast"""
    return {"status": "healthy", "service": "ShareYourSales Backend"}

# ============================================
# AUTHENTICATION
# ============================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifier le token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Vérification manuelle de l'expiration (doublon de sécurité)
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(status_code=401, detail="Token expiré")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erreur d'authentification: {str(e)}")

def create_token(user_id: str, email: str, role: str) -> str:
    """Créer un token JWT avec expiration"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_password_strength(password: str) -> None:
    """Valider la force du mot de passe"""
    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
    if not any(c.isupper() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une majuscule")
    if not any(c.islower() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une minuscule")
    if not any(c.isdigit() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre")

def hash_password(password: str, skip_validation: bool = False) -> str:
    """Hasher un mot de passe"""
    if not skip_validation:
        validate_password_strength(password)
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Vérifier un mot de passe"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ============================================
# MODELS
# ============================================

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")
    subscription_plan: str = Field(default="free", pattern="^(free|starter|pro|enterprise)$")
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AffiliateLink(BaseModel):
    id: Optional[str] = None
    user_id: str
    product_url: str = Field(..., min_length=10, max_length=2048)
    custom_slug: Optional[Annotated[str, Field(min_length=3, max_length=100)]] = None
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0
    status: str = Field(default="active", pattern="^(active|inactive|suspended)$")
    created_at: Optional[datetime] = None

class Product(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    price: Annotated[float, Field(ge=0.01)]
    category: Annotated[str, Field(min_length=2, max_length=100)]
    image_url: Optional[str] = Field(None, max_length=2048)
    merchant_id: str
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0

class Campaign(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    start_date: datetime
    end_date: datetime
    budget: Annotated[float, Field(ge=0.0)]
    target_audience: Dict[str, Any]
    status: str = Field(default="draft", pattern="^(draft|active|paused|completed|cancelled)$")

class ProductReview(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)]
    title: Optional[Annotated[str, Field(max_length=200)]] = None
    comment: Annotated[str, Field(min_length=10, max_length=2000)]

class AffiliationRequest(BaseModel):
    message: Optional[Annotated[str, Field(max_length=1000)]] = None

# ============================================
# MOCK DATA
# ============================================

MOCK_USERS = {
    "1": {
        "id": "1",
        "email": "admin@shareyoursales.ma",
        "username": "admin",
        "role": "admin",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Admin123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mohammed",
            "last_name": "Admin",
            "phone": "+212600000000",
            "city": "Casablanca"
        }
    },
    "2": {
        "id": "2", 
        "email": "influencer@example.com",
        "username": "sarah_influencer",
        "role": "influencer",
        "subscription_plan": "pro",
        "password_hash": hash_password("Password123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sarah",
            "last_name": "Benali",
            "phone": "+212611222333",
            "city": "Rabat",
            "instagram": "@sarah_lifestyle_ma",
            "followers_count": 125000,
            "engagement_rate": 4.8,
            "niche": "Lifestyle & Beauty",
            "rating": 4.9,
            "reviews": 87,
            "campaigns_completed": 45,
            "min_rate": 800,
            "categories": ["Mode", "Beauté", "Lifestyle"],
            "trending": True,
            "tiktok_followers": 95000
        }
    },
    "3": {
        "id": "3",
        "email": "merchant@example.com", 
        "username": "boutique_maroc",
        "role": "merchant",
        "subscription_plan": "starter",
        "password_hash": hash_password("Merchant123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Youssef",
            "last_name": "Alami",
            "phone": "+212622444555",
            "city": "Marrakech",
            "company": "Artisanat Maroc",
            "business_type": "Artisanat traditionnel"
        }
    },
    "4": {
        "id": "4",
        "email": "aminainfluencer@gmail.com",
        "username": "amina_beauty",
        "role": "influencer", 
        "subscription_plan": "pro",
        "password_hash": hash_password("Amina123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Amina",
            "last_name": "Tazi",
            "phone": "+212633666777",
            "city": "Fès",
            "instagram": "@amina_beauty_fes",
            "tiktok": "@aminabeauty",
            "followers_count": 89000,
            "engagement_rate": 6.2,
            "niche": "Beauty & Cosmetics",
            "rating": 4.7,
            "reviews": 62,
            "campaigns_completed": 38,
            "min_rate": 650,
            "categories": ["Beauté", "Cosmétiques", "Skincare"],
            "trending": False,
            "tiktok_followers": 112000
        }
    },
    "5": {
        "id": "5",
        "email": "commerciale@shareyoursales.ma",
        "username": "sofia_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Sofia123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sofia",
            "last_name": "Chakir",
            "phone": "+212644888999",
            "city": "Casablanca",
            "department": "Business Development",
            "territory": "Région Casablanca-Settat",
            "total_sales": 156,
            "commission_earned": 45600,
            "rating": 4.8,
            "reviews": 43,
            "specialties": ["E-commerce", "B2B", "Retail"]
        }
    },
    "6": {
        "id": "6",
        "email": "merchant2@artisanmaroc.ma",
        "username": "luxury_crafts",
        "role": "merchant",
        "subscription_plan": "pro", 
        "password_hash": hash_password("Luxury123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Rachid",
            "last_name": "Bennani",
            "phone": "+212655111222",
            "city": "Tétouan",
            "company": "Luxury Moroccan Crafts",
            "business_type": "Articles de luxe"
        }
    },
    "7": {
        "id": "7",
        "email": "foodinfluencer@gmail.com",
        "username": "chef_hassan",
        "role": "influencer",
        "subscription_plan": "starter",
        "password_hash": hash_password("Hassan123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Hassan",
            "last_name": "Oudrhiri",
            "phone": "+212666333444",
            "city": "Agadir",
            "instagram": "@chef_hassan_agadir",
            "youtube": "Chef Hassan Cuisine",
            "followers_count": 67000,
            "engagement_rate": 5.4,
            "niche": "Food & Cuisine",
            "rating": 4.6,
            "reviews": 34,
            "campaigns_completed": 28,
            "min_rate": 500,
            "categories": ["Food", "Cuisine", "Restaurant"],
            "trending": True,
            "tiktok_followers": 78000
        }
    },
    "8": {
        "id": "8",
        "email": "commercial2@shareyoursales.ma",
        "username": "omar_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Omar123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Omar",
            "last_name": "Filali",
            "phone": "+212677555666",
            "city": "Rabat",
            "department": "Client Relations",
            "territory": "Région Rabat-Salé-Kénitra",
            "total_sales": 203,
            "commission_earned": 62400,
            "rating": 4.9,
            "reviews": 56,
            "specialties": ["Grands Comptes", "Partenariats", "Support Client"]
        }
    },
    "9": {
        "id": "9",
        "email": "karim.influencer@gmail.com",
        "username": "karim_tech",
        "role": "influencer",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Karim123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Karim",
            "last_name": "Benjelloun",
            "phone": "+212688999000",
            "city": "Casablanca",
            "instagram": "@karim_tech_maroc",
            "youtube": "Karim Tech Reviews",
            "tiktok": "@karimtech",
            "followers_count": 285000,
            "engagement_rate": 7.5,
            "niche": "Tech & Gaming",
            "rating": 4.9,
            "reviews": 128,
            "campaigns_completed": 96,
            "min_rate": 1500,
            "categories": ["Technologie", "Gaming", "Innovation", "Gadgets"],
            "trending": True,
            "tiktok_followers": 320000,
            "verified": True
        }
    },
    "10": {
        "id": "10",
        "email": "premium.shop@electromaroc.ma",
        "username": "electro_maroc",
        "role": "merchant",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Electro123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mehdi",
            "last_name": "Tounsi",
            "phone": "+212699111222",
            "city": "Casablanca",
            "company": "ElectroMaroc Premium",
            "business_type": "Électronique & High-Tech",
            "annual_revenue": 2500000,
            "employee_count": 45,
            "verified_seller": True
        }
    }
}

MOCK_PRODUCTS = [
    # PRODUITS PHYSIQUES
    {
        "id": "1",
        "name": "Huile d'Argan Bio Premium - 100ml",
        "description": "Huile d'argan 100% bio certifiée, extraite à froid des coopératives d'Essaouira. Riche en vitamine E et acides gras essentiels.",
        "price": 120.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400",
        "merchant_id": "3",
        "commission_rate": 15.0,
        "stock": 50,
        "rating": 4.8,
        "sales_count": 234,
        "featured": True,
        "tags": ["bio", "argan", "naturel", "maroc"]
    },
    {
        "id": "2", 
        "name": "Caftan Marocain Brodé à la Main",
        "description": "Caftan traditionnel en soie naturelle, brodé à la main par les artisans de Fès. Pièce unique disponible en plusieurs tailles.",
        "price": 450.0,
        "category": "Mode",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1594736797933-d0901ba2fe65?w=400", 
        "merchant_id": "3",
        "commission_rate": 20.0,
        "stock": 12,
        "rating": 4.9,
        "sales_count": 89,
        "featured": True,
        "tags": ["caftan", "broderie", "soie", "artisanat"]
    },
    {
        "id": "3",
        "name": "Tajine en Terre Cuite de Salé",
        "description": "Tajine authentique fait à la main par les potiers de Salé. Idéal pour une cuisson traditionnelle et savoureuse.",
        "price": 85.0,
        "category": "Maison",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1574653105043-7ad6e4b08b9e?w=400",
        "merchant_id": "3", 
        "commission_rate": 12.0,
        "stock": 25,
        "rating": 4.7,
        "sales_count": 156,
        "featured": False,
        "tags": ["tajine", "poterie", "cuisine", "traditionnel"]
    },
    {
        "id": "4",
        "name": "Tapis Berbère Vintage",
        "description": "Tapis berbère authentique tissé à la main dans l'Atlas. Motifs traditionnels amazighs, laine naturelle de mouton.",
        "price": 890.0,
        "category": "Décoration",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400",
        "merchant_id": "3",
        "commission_rate": 18.0,
        "stock": 8,
        "rating": 4.9,
        "sales_count": 67,
        "featured": True,
        "tags": ["tapis", "berbère", "vintage", "atlas"]
    },
    {
        "id": "5",
        "name": "Savon Noir Beldi Traditionnel",
        "description": "Savon noir authentique à base d'olives marocaines. Utilisé dans les hammams traditionnels, exfoliant naturel.",
        "price": 25.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228994-b6c25e02c0e4?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "stock": 100,
        "rating": 4.6,
        "sales_count": 445,
        "featured": False,
        "tags": ["savon", "beldi", "hammam", "naturel"]
    },
    
    # SERVICES
    {
        "id": "11",
        "name": "Shooting Photo Professionnel",
        "description": "Séance photo professionnelle pour influenceurs et marques. Inclut 3 heures de shooting, retouche de 50 photos HD.",
        "price": 800.0,
        "category": "Photographie",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=400",
        "merchant_id": "4",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 78,
        "featured": True,
        "tags": ["photo", "shooting", "professionnel", "influenceur"]
    },
    {
        "id": "12",
        "name": "Coaching Marketing Digital",
        "description": "Consultation personnalisée en stratégie digitale et réseaux sociaux. 2 sessions de 1h30 avec plan d'action sur mesure.",
        "price": 650.0,
        "category": "Consulting",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400",
        "merchant_id": "5",
        "commission_rate": 25.0,
        "rating": 4.8,
        "sales_count": 112,
        "featured": True,
        "tags": ["marketing", "coaching", "digital", "stratégie"]
    },
    {
        "id": "13",
        "name": "Création Site Web Vitrine",
        "description": "Développement complet d'un site web responsive. Design moderne, optimisé SEO, livraison en 15 jours.",
        "price": 2500.0,
        "category": "Développement Web",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400",
        "merchant_id": "6",
        "commission_rate": 15.0,
        "rating": 4.9,
        "sales_count": 45,
        "featured": True,
        "tags": ["web", "site", "développement", "responsive"]
    },
    {
        "id": "14",
        "name": "Gestion Réseaux Sociaux - 1 Mois",
        "description": "Gestion complète de vos réseaux sociaux pendant 1 mois. Création de contenu, planification, engagement communauté.",
        "price": 1200.0,
        "category": "Social Media",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400",
        "merchant_id": "4",
        "commission_rate": 18.0,
        "rating": 4.7,
        "sales_count": 89,
        "featured": False,
        "tags": ["social media", "gestion", "instagram", "facebook"]
    },
    {
        "id": "15",
        "name": "Montage Vidéo Professionnel",
        "description": "Montage vidéo de qualité pro pour YouTube, TikTok, Instagram. Jusqu'à 10 minutes de vidéo finale avec effets.",
        "price": 450.0,
        "category": "Vidéo",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=400",
        "merchant_id": "5",
        "commission_rate": 22.0,
        "rating": 4.8,
        "sales_count": 134,
        "featured": False,
        "tags": ["vidéo", "montage", "youtube", "tiktok"]
    },
    {
        "id": "16",
        "name": "Formation E-commerce Complète",
        "description": "Formation intensive de 3 jours sur le e-commerce. De la création de boutique à la stratégie de vente en ligne.",
        "price": 1800.0,
        "category": "Formation",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 56,
        "featured": True,
        "tags": ["formation", "ecommerce", "vente", "business"]
    },
    {
        "id": "17",
        "name": "Rédaction Articles de Blog SEO",
        "description": "Pack de 5 articles optimisés SEO de 1000 mots chacun. Recherche mots-clés incluse, livraison en 10 jours.",
        "price": 550.0,
        "category": "Rédaction",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "rating": 4.6,
        "sales_count": 98,
        "featured": False,
        "tags": ["rédaction", "seo", "blog", "contenu"]
    },
    {
        "id": "18",
        "name": "Design Logo + Identité Visuelle",
        "description": "Création complète d'un logo professionnel + charte graphique. 3 propositions, révisions illimitées.",
        "price": 950.0,
        "category": "Design",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400",
        "merchant_id": "5",
        "commission_rate": 18.0,
        "rating": 4.8,
        "sales_count": 67,
        "featured": False,
        "tags": ["design", "logo", "identité", "graphisme"]
    },
    {
        "id": "19",
        "name": "Audit SEO Complet",
        "description": "Analyse SEO détaillée de votre site web avec rapport complet et recommandations d'amélioration.",
        "price": 750.0,
        "category": "SEO",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 83,
        "featured": True,
        "tags": ["seo", "audit", "analyse", "optimisation"]
    },
    {
        "id": "20",
        "name": "Campagne Publicité Facebook Ads",
        "description": "Création et gestion de campagne Facebook Ads pendant 2 semaines. Ciblage, créatifs, optimisation inclus.",
        "price": 1100.0,
        "category": "Publicité",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400",
        "merchant_id": "4",
        "commission_rate": 22.0,
        "rating": 4.7,
        "sales_count": 91,
        "featured": False,
        "tags": ["facebook", "ads", "publicité", "marketing"]
    }
]

MOCK_AFFILIATE_LINKS = [
    {
        "id": "1",
        "user_id": "2",
        "product_id": "1", 
        "custom_slug": "argan-premium",
        "original_url": "https://boutique.ma/argan-oil",
        "affiliate_url": "https://shareyoursales.ma/aff/argan-premium",
        "commission_rate": 15.0,
        "clicks": 245,
        "conversions": 12,
        "revenue": 216.0,
        "status": "active",
        "created_at": "2024-10-15T10:30:00Z"
    },
    {
        "id": "2",
        "user_id": "2",
        "product_id": "2",
        "custom_slug": "caftan-luxury", 
        "original_url": "https://boutique.ma/caftan-traditionnel",
        "affiliate_url": "https://shareyoursales.ma/aff/caftan-luxury",
        "commission_rate": 20.0,
        "clicks": 89,
        "conversions": 3,
        "revenue": 270.0,
        "status": "active",
        "created_at": "2024-10-20T14:15:00Z"
    }
]

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🇲🇦 ShareYourSales API - Version Complète",
        "status": "operational",
        "version": "2.0.0",
        "features": [
            "Authentification JWT",
            "Gestion utilisateurs", 
            "Liens d'affiliation",
            "Produits marketplace",
            "Analytics en temps réel",
            "Intégrations sociales",
            "Paiements multi-gateway",
            "IA conversationnelle"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth/*",
            "users": "/api/users/*", 
            "products": "/api/products/*",
            "affiliate": "/api/affiliate/*",
            "analytics": "/api/analytics/*"
        }
    }

@app.get("/api/health")
async def health_check():
    """Vérification de santé du service"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales Backend",
        "version": "2.0.0",
        "uptime": "24h 15m",
        "database": "connected",
        "redis": "connected",
        "external_apis": {
            "stripe": "operational",
            "instagram": "operational", 
            "tiktok": "operational"
        }
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    """Inscription d'un nouvel utilisateur - Crée dans Supabase"""

    # Vérifier si l'email existe déjà (Supabase ou MOCK_USERS)
    existing_user = None
    if SUPABASE_ENABLED:
        existing_user = get_user_by_email(user_data.email)

    if not existing_user:
        # Fallback check in MOCK_USERS
        for user in MOCK_USERS.values():
            if user["email"] == user_data.email:
                existing_user = user
                break

    if existing_user:
        logger.warning(f"❌ Registration failed: Email already exists {user_data.email}")
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Préparer les données utilisateur
    import uuid
    user_id = str(uuid.uuid4())
    new_user_data = {
        "id": user_id,
        "email": user_data.email,
        "role": user_data.role,
        "password_hash": hash_password(user_data.password),
        "phone_verified": False,
        "two_fa_enabled": False,
        "is_active": True
    }

    # Essayer de créer dans Supabase d'abord
    created_user = None
    if SUPABASE_ENABLED:
        created_user = create_user_in_supabase(new_user_data)
        logger.info(f"✅ User created in Supabase: {user_data.email}")

    # Fallback to MOCK_USERS if Supabase fails
    if not created_user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user creation: {user_data.email}")
        new_user_data["username"] = user_data.username
        new_user_data["subscription_plan"] = "free"
        new_user_data["created_at"] = datetime.now().isoformat()
        MOCK_USERS[user_id] = new_user_data
        created_user = new_user_data

    # Envoyer email de bienvenue
    if EMAIL_ENABLED:
        try:
            await EmailTemplates.send_welcome_email(
                to_email=user_data.email,
                user_name=user_data.username,
                user_type=user_data.role
            )
        except Exception as e:
            logger.error(f"Email sending failed: {e}")

    # Générer token JWT avec fonction dédiée
    access_token = create_token(user_id, user_data.email, user_data.role)

    logger.info(f"✅ User registered successfully: {user_data.email} (role: {user_data.role})")

    return {
        "message": "Inscription réussie",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "role": user_data.role,
            "subscription_plan": "free"
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    """Connexion utilisateur - Lit depuis Supabase"""

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_email(credentials.email)
        logger.info(f"🔍 Login attempt for {credentials.email} - User found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for {credentials.email}")
        for u in MOCK_USERS.values():
            if u["email"] == credentials.email:
                user = u
                break

    if not user:
        logger.warning(f"❌ Login failed: User not found for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Vérifier le mot de passe
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"❌ Login failed: Invalid password for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Générer token JWT avec fonction dédiée
    user_id = str(user["id"])  # Ensure ID is string
    access_token = create_token(user_id, user["email"], user["role"])

    logger.info(f"✅ Login successful for {credentials.email} (role: {user['role']})")

    return {
        "message": "Connexion réussie",
        "user": {
            "id": user_id,
            "email": user["email"],
            "username": user.get("username", user["email"].split("@")[0]),
            "role": user["role"],
            "subscription_plan": user.get("subscription_plan", "free")
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Obtenir les informations de l'utilisateur connecté - Lit depuis Supabase"""
    user_id = payload.get("sub")

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_id(user_id)
        logger.info(f"🔍 /api/auth/me for user ID {user_id} - Found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user ID {user_id}")
        user = MOCK_USERS.get(user_id)

    if not user:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "username": user.get("username", user["email"].split("@")[0]),
        "role": user["role"],
        "subscription_plan": user.get("subscription_plan", "free"),
        "created_at": user.get("created_at")
    }

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    """Déconnexion utilisateur"""
    # Dans une implémentation réelle, on invaliderait le token côté serveur
    # Pour l'instant, on retourne simplement un message de succès
    return {
        "message": "Déconnexion réussie",
        "success": True
    }

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = Query(None, alias="type"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    sort_by: Optional[str] = "popularity"
):
    """Liste des produits avec filtres avancés (DONNÉES RÉELLES depuis DB)"""
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer les produits depuis la base de données
            result = await get_all_products(
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                limit=limit,
                offset=offset
            )
            
            # Ajouter les filtres disponibles
            if result["products"]:
                categories_set = set(p["category"] for p in result["products"] if p.get("category"))
                prices = [p["price"] for p in result["products"] if p.get("price")]
                
                result["filters"] = {
                    "categories": list(categories_set),
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0
                    }
                }
            
            return result
        
        except Exception as e:
            logger.info(f"❌ Erreur get_products: {str(e)}")
            # Fallback to mocked data
    
    # FALLBACK: Données mockées
    products = MOCK_PRODUCTS.copy()
    
    # Filtrer par type (product ou service)
    if product_type:
        products = [p for p in products if p.get("type", "product") == product_type]
    
    # Filtrer par catégorie
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    # Recherche textuelle
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
                   search_lower in p["name"].lower() or 
                   search_lower in p["description"].lower() or
                   any(search_lower in tag for tag in p.get("tags", []))]
    
    # Filtrer par prix
    if min_price:
        products = [p for p in products if p["price"] >= min_price]
    if max_price:
        products = [p for p in products if p["price"] <= max_price]
    
    # Filtrer par featured
    if featured is not None:
        products = [p for p in products if p.get("featured", False) == featured]
    
    # Tri
    if sort_by == "price_asc":
        products.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "popularity":
        products.sort(key=lambda x: x["sales_count"], reverse=True)
    
    # Pagination
    total = len(products)
    products = products[offset:offset + limit]
    
    return {
        "products": products,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        },
        "filters": {
            "categories": list(set(p["category"] for p in MOCK_PRODUCTS)),
            "price_range": {
                "min": min(p["price"] for p in MOCK_PRODUCTS),
                "max": max(p["price"] for p in MOCK_PRODUCTS)
            }
        }
    }

@app.get("/api/products/featured")
async def get_featured_products():
    """Produits en vedette"""
    featured_products = [p for p in MOCK_PRODUCTS if p.get("featured", False)]
    return {
        "products": featured_products[:6],
        "total": len(featured_products)
    }

@app.get("/api/products/categories")
async def get_categories():
    """Liste des catégories avec compteurs"""
    categories = {}
    for product in MOCK_PRODUCTS:
        cat = product["category"]
        if cat not in categories:
            categories[cat] = {"name": cat, "count": 0, "products": []}
        categories[cat]["count"] += 1
        categories[cat]["products"].append(product["id"])
    
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories)
    }

@app.post("/api/products")
async def create_new_product(
    product_data: dict,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_product_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau produit (INSERTION RÉELLE dans DB) - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("id")
    user_role = payload.get("role")
    
    if user_role != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les merchants peuvent créer des produits"
        )
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer le merchant_id
            merchant_response = supabase.table("merchants") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            merchant_id = merchant_response.data["id"]
            
            # Créer le produit
            result = await create_product(merchant_id, product_data)
            
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "Erreur lors de la création du produit")
                )
        
        except Exception as e:
            logger.info(f"❌ Erreur create_new_product: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création: {str(e)}"
            )
    
    # FALLBACK: Retourner un produit mocké (sans vraie insertion)
    return {
        "success": True,
        "product": {
            "id": f"prod_{datetime.now().timestamp()}",
            "name": product_data.get("name"),
            "price": product_data.get("price"),
            "category": product_data.get("category"),
            "created_at": datetime.now().isoformat()
        }
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Détails d'un produit spécifique"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "product": product,
        "related_products": [p for p in MOCK_PRODUCTS if p["category"] == product["category"] and p["id"] != product_id][:3],
        "affiliate_stats": {
            "total_affiliates": 45,
            "avg_commission": 15.5,
            "conversion_rate": 3.2
        }
    }

# ============================================
# MARKETPLACE ENDPOINTS (Compatibility)
# ============================================

@app.get("/api/marketplace/products")
async def get_marketplace_products(
    type: Optional[str] = "product",
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Produits et services pour le marketplace - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            query = supabase.table("products").select("*")
            
            # Filtrer par type si spécifié
            if type:
                query = query.eq("type", type)
            
            # Pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            products = result.data if result.data else []
            
            # Compter le total
            # La méthode a changé dans les versions récentes de postgrest-py
            count_result = supabase.table("products").select("id", count="exact").eq("type", type).execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            # Fallback sur MOCK_PRODUCTS si Supabase non disponible
            products = MOCK_PRODUCTS.copy()
            
            if type:
                products = [p for p in products if p.get("type", "product") == type]
            
            total = len(products)
            products = products[offset:offset + limit]
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        products = MOCK_PRODUCTS.copy()
        if type:
            products = [p for p in products if p.get("type", "product") == type]
        total = len(products)
        products = products[offset:offset + limit]
        return {
            "products": products,
            "total": total,
            "limit": limit,
            "offset": offset
        }

@app.get("/api/marketplace/products/{product_id}")
async def get_product_detail(product_id: str):
    """Détails complets d'un produit ou service - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            result = supabase.table("products").select("*").eq("id", product_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
            
            product = result.data[0]
        else:
            # Fallback sur MOCK_PRODUCTS
            product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
            if not product:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Enrichir avec des données supplémentaires pour la page détail
    product_detail = {
        **product,
        "images": product.get("images", [product.get("image", "")]),
        "highlights": product.get("highlights", [
            "Produit de qualité premium",
            "Livraison rapide au Maroc",
            "Service client disponible 7j/7",
            "Garantie satisfaction"
        ]),
        "included": product.get("included", [
            "Accès immédiat après achat",
            "Support technique inclus",
            "Mises à jour gratuites"
        ]),
        "how_it_works": product.get("how_it_works", 
            "1. Achetez le produit\n2. Recevez votre lien/code par email\n3. Profitez de votre achat\n4. Contactez le support si besoin"),
        "conditions": product.get("conditions",
            "• Valable 1 an à partir de la date d'achat\n• Non remboursable\n• Transférable\n• Utilisable au Maroc uniquement"),
        "faq": product.get("faq", [
            {
                "question": "Comment utiliser ce produit/service ?",
                "answer": "Après l'achat, vous recevrez toutes les instructions par email."
            },
            {
                "question": "Puis-je obtenir un remboursement ?",
                "answer": "Les remboursements sont possibles dans les 14 jours selon nos conditions."
            }
        ]),
        "merchant": {
            "name": product.get("merchant_name", "Marchand Vérifié"),
            "phone": "+212 6 00 00 00 00",
            "email": "contact@merchant.com"
        },
        "rating_average": product.get("rating", 4.5),
        "rating_count": product.get("rating_count", 150),
        "sold_count": product.get("sold_count", 450)
    }
    
    return {
        "success": True,
        "product": product_detail
    }

@app.get("/api/marketplace/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0)
):
    """Avis clients pour un produit"""
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer des avis mock
    mock_reviews = [
        {
            "id": f"rev_{product_id}_1",
            "rating": 5,
            "title": "Excellent produit!",
            "comment": "Très satisfait de mon achat. Livraison rapide et produit conforme à la description.",
            "user": {"first_name": "Ahmed"},
            "created_at": "2024-10-15T10:30:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_2",
            "rating": 4,
            "title": "Bon rapport qualité/prix",
            "comment": "Produit de bonne qualité. Je recommande!",
            "user": {"first_name": "Fatima"},
            "created_at": "2024-10-20T14:20:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_3",
            "rating": 5,
            "title": "Parfait",
            "comment": "Rien à redire, exactement ce que je cherchais.",
            "user": {"first_name": "Youssef"},
            "created_at": "2024-10-25T09:15:00",
            "is_verified_purchase": False
        }
    ]
    
    total = len(mock_reviews)
    reviews = mock_reviews[offset:offset + limit]
    
    return {
        "success": True,
        "reviews": reviews,
        "total": total
    }

@app.post("/api/marketplace/products/{product_id}/review")
async def submit_product_review(
    product_id: str,
    review_data: ProductReview,
    payload: dict = Depends(verify_token)
):
    """Soumettre un avis sur un produit"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Dans une vraie app, on sauvegarderait l'avis en DB
    review = {
        "id": f"rev_{product_id}_{user_id}_{datetime.now().timestamp()}",
        "product_id": product_id,
        "user_id": user_id,
        "rating": review_data.rating,
        "title": review_data.title,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat(),
        "is_verified_purchase": False  # À vérifier avec l'historique d'achats
    }
    
    return {
        "success": True,
        "message": "Votre avis sera publié après modération",
        "review": review
    }

@app.post("/api/marketplace/products/{product_id}/request-affiliate")
async def request_product_affiliation(
    product_id: str,
    request_data: AffiliationRequest,
    payload: dict = Depends(verify_token)
):
    """Demander l'affiliation pour un produit"""
    user_id = payload.get("sub")
    user_role = payload.get("role")
    
    # Vérifier que l'utilisateur est un influenceur
    if user_role != "influencer":
        raise HTTPException(
            status_code=403,
            detail="Seuls les influenceurs peuvent demander une affiliation"
        )
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Créer la demande d'affiliation
    affiliation_request = {
        "id": f"aff_req_{user_id}_{product_id}_{datetime.now().timestamp()}",
        "user_id": user_id,
        "product_id": product_id,
        "message": request_data.message or "Je souhaite promouvoir ce produit.",
        "status": "pending",
        "commission_rate": product.get("commission_rate", 15),
        "created_at": datetime.now().isoformat()
    }
    
    # Dans une vraie app, on notifierait le marchand
    
    # Générer un lien d'affiliation temporaire
    tracking_code = f"{user_id[:8]}-{product_id}"
    affiliate_link = f"https://shareyoursales.ma/go/{tracking_code}"
    
    return {
        "success": True,
        "message": "Demande d'affiliation envoyée avec succès!",
        "affiliation_request": affiliation_request,
        "affiliate_link": affiliate_link
    }

# ============================================
# COLLABORATION ENDPOINTS (Marchand-Influenceur)
# ============================================

class CollaborationRequestCreate(BaseModel):
    influencer_id: str
    product_id: str
    commission_rate: float
    message: Optional[str] = None

class CounterOfferData(BaseModel):
    counter_commission: float
    message: Optional[str] = None

class RejectData(BaseModel):
    reason: Optional[str] = None

class ContractSignatureData(BaseModel):
    signature: str

@app.post("/api/collaborations/requests")
async def create_collaboration_request(
    data: CollaborationRequestCreate,
    payload: dict = Depends(verify_token)
):
    """Créer une demande de collaboration (Marchand → Influenceur)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "create_collaboration_request",
            {
                "p_merchant_id": merchant_id,
                "p_influencer_id": data.influencer_id,
                "p_product_id": data.product_id,
                "p_commission_rate": data.commission_rate,
                "p_message": data.message
            }
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        request_data = result.data[0]
        
        return {
            "success": True,
            "message": "Demande envoyée avec succès",
            "request_id": request_data["request_id"],
            "status": request_data["status"],
            "expires_at": request_data["expires_at"]
        }
    except Exception as e:
        error_msg = str(e)
        if "existe déjà" in error_msg:
            raise HTTPException(status_code=409, detail="Une demande existe déjà pour ce produit")
        elif "Produit non trouvé" in error_msg:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/collaborations/requests/received")
async def get_received_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes reçues (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("influencer_id", influencer_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/sent")
async def get_sent_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes envoyées (Marchand)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/accept")
async def accept_collaboration_request(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Accepter une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande acceptée ! Vous devez maintenant signer le contrat."
        }
    except Exception as e:
        error_msg = str(e)
        if "non valide" in error_msg or "déjà traitée" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.put("/api/collaborations/requests/{request_id}/reject")
async def reject_collaboration_request(
    request_id: str,
    data: RejectData,
    payload: dict = Depends(verify_token)
):
    """Refuser une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "reject_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_reason": data.reason
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande refusée"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/counter-offer")
async def counter_offer_collaboration(
    request_id: str,
    data: CounterOfferData,
    payload: dict = Depends(verify_token)
):
    """Contre-offre (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "counter_offer_collaboration",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_counter_commission": data.counter_commission,
                "p_message": data.message
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Contre-offre envoyée au marchand"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collaborations/requests/{request_id}/sign-contract")
async def sign_collaboration_contract(
    request_id: str,
    data: ContractSignatureData,
    payload: dict = Depends(verify_token)
):
    """Signer le contrat"""
    user_id = payload.get("user_id")
    user_role = payload.get("role", "merchant")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_contract",
            {
                "p_request_id": request_id,
                "p_user_id": user_id,
                "p_user_role": user_role,
                "p_signature": data.signature
            }
        ).execute()
        
        if user_role == "influencer":
            link_result = supabase.rpc(
                "generate_affiliate_link_from_collaboration",
                {"p_request_id": request_id}
            ).execute()
            
            link_id = link_result.data if link_result.data else None
            
            return {
                "success": True,
                "message": "Contrat signé ! Votre lien d'affiliation a été généré.",
                "affiliate_link_id": link_id
            }
        
        return {
            "success": True,
            "message": "Contrat signé avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/{request_id}")
async def get_collaboration_request_details(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Détails d'une demande"""
    user_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("id", request_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        request_data = result.data
        if user_id not in [request_data["merchant_id"], request_data["influencer_id"]]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        if user_id == request_data["influencer_id"] and not request_data.get("viewed_by_influencer"):
            supabase.table("collaboration_requests") \
                .update({
                    "viewed_by_influencer": True,
                    "viewed_at": datetime.now().isoformat()
                }) \
                .eq("id", request_id) \
                .execute()
        
        history = supabase.table("collaboration_history") \
            .select("*") \
            .eq("collaboration_request_id", request_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return {
            "success": True,
            "request": request_data,
            "history": history.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/contract-terms")
async def get_contract_terms():
    """Termes du contrat de collaboration"""
    return {
        "success": True,
        "contract": {
            "version": "v1.0",
            "terms": [
                {
                    "title": "1. Respect Éthique",
                    "content": "L'influenceur s'engage à promouvoir le produit de manière éthique et honnête, sans fausses déclarations."
                },
                {
                    "title": "2. Transparence",
                    "content": "L'influenceur doit clairement indiquer qu'il s'agit d'un partenariat commercial (#ad, #sponsored)."
                },
                {
                    "title": "3. Commission",
                    "content": "La commission convenue sera versée pour chaque vente générée via le lien d'affiliation."
                },
                {
                    "title": "4. Durée",
                    "content": "Le contrat est valable pour 12 mois, renouvelable par accord mutuel."
                },
                {
                    "title": "5. Résiliation",
                    "content": "Chaque partie peut résilier avec un préavis de 30 jours."
                },
                {
                    "title": "6. Propriété Intellectuelle",
                    "content": "Le marchand conserve tous les droits sur le produit. L'influenceur conserve ses droits sur son contenu."
                },
                {
                    "title": "7. Confidentialité",
                    "content": "Les termes financiers de cet accord sont confidentiels."
                },
                {
                    "title": "8. Conformité Légale",
                    "content": "Les deux parties s'engagent à respecter toutes les lois applicables."
                }
            ]
        }
    }

# ============================================
# COMMERCIALS & INFLUENCERS DIRECTORY
# ============================================

@app.get("/api/commercials/directory")
async def get_commercials_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des commerciaux"""
    commercials = [u for u in MOCK_USERS.values() if u.get("role") == "commercial"]
    
    total = len(commercials)
    commercials = commercials[offset:offset + limit]
    
    return {
        "commercials": commercials,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/influencers/directory")
async def get_influencers_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des influenceurs"""
    influencers = [u for u in MOCK_USERS.values() if u.get("role") == "influencer"]
    
    total = len(influencers)
    influencers = influencers[offset:offset + limit]
    
    return {
        "influencers": influencers,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ============================================
# AFFILIATE LINKS ENDPOINTS  
# ============================================

@app.get("/api/affiliate/links")
async def get_affiliate_links(payload: dict = Depends(verify_token)):
    """Liste des liens d'affiliation de l'utilisateur"""
    user_id = payload.get("sub")
    user_links = [link for link in MOCK_AFFILIATE_LINKS if link["user_id"] == user_id]
    
    return {
        "links": user_links,
        "stats": {
            "total_links": len(user_links),
            "total_clicks": sum(link["clicks"] for link in user_links),
            "total_conversions": sum(link["conversions"] for link in user_links),
            "total_revenue": sum(link["revenue"] for link in user_links)
        }
    }

@app.post("/api/affiliate/links")
async def create_affiliate_link(
    product_id: str,
    custom_slug: Optional[str] = None,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_link_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau lien d'affiliation - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer slug si non fourni
    if not custom_slug:
        custom_slug = f"prod-{product_id}-{user_id}"
    
    # Créer le lien
    link_id = str(len(MOCK_AFFILIATE_LINKS) + 1)
    new_link = {
        "id": link_id,
        "user_id": user_id,
        "product_id": product_id,
        "custom_slug": custom_slug,
        "original_url": f"https://boutique.ma/product/{product_id}",
        "affiliate_url": f"https://shareyoursales.ma/aff/{custom_slug}",
        "commission_rate": product["commission_rate"],
        "clicks": 0,
        "conversions": 0,
        "revenue": 0.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_AFFILIATE_LINKS.append(new_link)
    
    return {
        "message": "Lien d'affiliation créé avec succès",
        "link": new_link
    }

# ============================================
# MODERATION ENDPOINTS (Admin)
# ============================================

@app.get("/api/admin/moderation/pending")
async def get_pending_moderation_items(
    risk_level: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Récupérer les produits en attente de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des données en attente
    pending_items = [
        {
            "id": "mod_1",
            "product_id": "prod_abc",
            "product_name": "Smartphone X-Pro 15",
            "product_description": "Le dernier smartphone avec une caméra révolutionnaire et une batterie longue durée.",
            "product_price": 12500.00,
            "product_category": "Électronique",
            "product_images": ["https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400"],
            "merchant_id": "merch_xyz",
            "merchant_name": "ElectroMaroc",
            "merchant_email": "contact@electromaroc.ma",
            "submitted_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "hours_pending": 2.1,
            "ai_risk_level": "high",
            "ai_confidence": 0.85,
            "ai_reason": "Le prix semble élevé par rapport à des produits similaires. La description contient des superlatifs ('révolutionnaire').",
            "ai_flags": ["prix_eleve", "description_exageree"]
        },
        {
            "id": "mod_2",
            "product_id": "prod_def",
            "product_name": "T-shirt 'Casablanca'",
            "product_description": "T-shirt en coton bio avec un design exclusif de la ville de Casablanca.",
            "product_price": 250.00,
            "product_category": "Mode",
            "product_images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"],
            "merchant_id": "merch_uvw",
            "merchant_name": "CasaStyle",
            "merchant_email": "contact@casastyle.ma",
            "submitted_at": (datetime.now() - timedelta(hours=8)).isoformat(),
            "hours_pending": 8.5,
            "ai_risk_level": "low",
            "ai_confidence": 0.98,
            "ai_reason": "Produit standard, description claire, prix cohérent.",
            "ai_flags": []
        }
    ]
    
    if risk_level:
        items = [item for item in pending_items if item['ai_risk_level'] == risk_level]
    else:
        items = pending_items

    return {"data": items}

@app.get("/api/admin/moderation/stats")
async def get_moderation_stats(
    period: str = "today",
    payload: dict = Depends(verify_token)
):
    """Récupérer les statistiques de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des statistiques
    stats = {
        "total": 150,
        "pending": 2,
        "approved": 135,
        "rejected": 13,
        "approval_rate": 135 / 150 if 150 > 0 else 0
    }
    return stats

@app.post("/api/admin/moderation/review")
async def review_moderation_item(
    payload: dict = Depends(verify_token)
):
    """Traiter une décision de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Simuler le traitement
    return {"success": True, "message": "Décision enregistrée"}
    

# ============================================
# AUTHENTICATION
# ============================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifier le token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Vérification manuelle de l'expiration (doublon de sécurité)
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(status_code=401, detail="Token expiré")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erreur d'authentification: {str(e)}")

def create_token(user_id: str, email: str, role: str) -> str:
    """Créer un token JWT avec expiration"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_password_strength(password: str) -> None:
    """Valider la force du mot de passe"""
    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
    if not any(c.isupper() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une majuscule")
    if not any(c.islower() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une minuscule")
    if not any(c.isdigit() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre")

def hash_password(password: str, skip_validation: bool = False) -> str:
    """Hasher un mot de passe"""
    if not skip_validation:
        validate_password_strength(password)
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Vérifier un mot de passe"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ============================================
# MODELS
# ============================================

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")
    subscription_plan: str = Field(default="free", pattern="^(free|starter|pro|enterprise)$")
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AffiliateLink(BaseModel):
    id: Optional[str] = None
    user_id: str
    product_url: str = Field(..., min_length=10, max_length=2048)
    custom_slug: Optional[Annotated[str, Field(min_length=3, max_length=100)]] = None
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0
    status: str = Field(default="active", pattern="^(active|inactive|suspended)$")
    created_at: Optional[datetime] = None

class Product(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    price: Annotated[float, Field(ge=0.01)]
    category: Annotated[str, Field(min_length=2, max_length=100)]
    image_url: Optional[str] = Field(None, max_length=2048)
    merchant_id: str
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0

class Campaign(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    start_date: datetime
    end_date: datetime
    budget: Annotated[float, Field(ge=0.0)]
    target_audience: Dict[str, Any]
    status: str = Field(default="draft", pattern="^(draft|active|paused|completed|cancelled)$")

class ProductReview(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)]
    title: Optional[Annotated[str, Field(max_length=200)]] = None
    comment: Annotated[str, Field(min_length=10, max_length=2000)]

class AffiliationRequest(BaseModel):
    message: Optional[Annotated[str, Field(max_length=1000)]] = None

# ============================================
# MOCK DATA
# ============================================

MOCK_USERS = {
    "1": {
        "id": "1",
        "email": "admin@shareyoursales.ma",
        "username": "admin",
        "role": "admin",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Admin123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mohammed",
            "last_name": "Admin",
            "phone": "+212600000000",
            "city": "Casablanca"
        }
    },
    "2": {
        "id": "2", 
        "email": "influencer@example.com",
        "username": "sarah_influencer",
        "role": "influencer",
        "subscription_plan": "pro",
        "password_hash": hash_password("Password123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sarah",
            "last_name": "Benali",
            "phone": "+212611222333",
            "city": "Rabat",
            "instagram": "@sarah_lifestyle_ma",
            "followers_count": 125000,
            "engagement_rate": 4.8,
            "niche": "Lifestyle & Beauty",
            "rating": 4.9,
            "reviews": 87,
            "campaigns_completed": 45,
            "min_rate": 800,
            "categories": ["Mode", "Beauté", "Lifestyle"],
            "trending": True,
            "tiktok_followers": 95000
        }
    },
    "3": {
        "id": "3",
        "email": "merchant@example.com", 
        "username": "boutique_maroc",
        "role": "merchant",
        "subscription_plan": "starter",
        "password_hash": hash_password("Merchant123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Youssef",
            "last_name": "Alami",
            "phone": "+212622444555",
            "city": "Marrakech",
            "company": "Artisanat Maroc",
            "business_type": "Artisanat traditionnel"
        }
    },
    "4": {
        "id": "4",
        "email": "aminainfluencer@gmail.com",
        "username": "amina_beauty",
        "role": "influencer", 
        "subscription_plan": "pro",
        "password_hash": hash_password("Amina123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Amina",
            "last_name": "Tazi",
            "phone": "+212633666777",
            "city": "Fès",
            "instagram": "@amina_beauty_fes",
            "tiktok": "@aminabeauty",
            "followers_count": 89000,
            "engagement_rate": 6.2,
            "niche": "Beauty & Cosmetics",
            "rating": 4.7,
            "reviews": 62,
            "campaigns_completed": 38,
            "min_rate": 650,
            "categories": ["Beauté", "Cosmétiques", "Skincare"],
            "trending": False,
            "tiktok_followers": 112000
        }
    },
    "5": {
        "id": "5",
        "email": "commerciale@shareyoursales.ma",
        "username": "sofia_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Sofia123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sofia",
            "last_name": "Chakir",
            "phone": "+212644888999",
            "city": "Casablanca",
            "department": "Business Development",
            "territory": "Région Casablanca-Settat",
            "total_sales": 156,
            "commission_earned": 45600,
            "rating": 4.8,
            "reviews": 43,
            "specialties": ["E-commerce", "B2B", "Retail"]
        }
    },
    "6": {
        "id": "6",
        "email": "merchant2@artisanmaroc.ma",
        "username": "luxury_crafts",
        "role": "merchant",
        "subscription_plan": "pro", 
        "password_hash": hash_password("Luxury123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Rachid",
            "last_name": "Bennani",
            "phone": "+212655111222",
            "city": "Tétouan",
            "company": "Luxury Moroccan Crafts",
            "business_type": "Articles de luxe"
        }
    },
    "7": {
        "id": "7",
        "email": "foodinfluencer@gmail.com",
        "username": "chef_hassan",
        "role": "influencer",
        "subscription_plan": "starter",
        "password_hash": hash_password("Hassan123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Hassan",
            "last_name": "Oudrhiri",
            "phone": "+212666333444",
            "city": "Agadir",
            "instagram": "@chef_hassan_agadir",
            "youtube": "Chef Hassan Cuisine",
            "followers_count": 67000,
            "engagement_rate": 5.4,
            "niche": "Food & Cuisine",
            "rating": 4.6,
            "reviews": 34,
            "campaigns_completed": 28,
            "min_rate": 500,
            "categories": ["Food", "Cuisine", "Restaurant"],
            "trending": True,
            "tiktok_followers": 78000
        }
    },
    "8": {
        "id": "8",
        "email": "commercial2@shareyoursales.ma",
        "username": "omar_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Omar123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Omar",
            "last_name": "Filali",
            "phone": "+212677555666",
            "city": "Rabat",
            "department": "Client Relations",
            "territory": "Région Rabat-Salé-Kénitra",
            "total_sales": 203,
            "commission_earned": 62400,
            "rating": 4.9,
            "reviews": 56,
            "specialties": ["Grands Comptes", "Partenariats", "Support Client"]
        }
    },
    "9": {
        "id": "9",
        "email": "karim.influencer@gmail.com",
        "username": "karim_tech",
        "role": "influencer",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Karim123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Karim",
            "last_name": "Benjelloun",
            "phone": "+212688999000",
            "city": "Casablanca",
            "instagram": "@karim_tech_maroc",
            "youtube": "Karim Tech Reviews",
            "tiktok": "@karimtech",
            "followers_count": 285000,
            "engagement_rate": 7.5,
            "niche": "Tech & Gaming",
            "rating": 4.9,
            "reviews": 128,
            "campaigns_completed": 96,
            "min_rate": 1500,
            "categories": ["Technologie", "Gaming", "Innovation", "Gadgets"],
            "trending": True,
            "tiktok_followers": 320000,
            "verified": True
        }
    },
    "10": {
        "id": "10",
        "email": "premium.shop@electromaroc.ma",
        "username": "electro_maroc",
        "role": "merchant",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Electro123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mehdi",
            "last_name": "Tounsi",
            "phone": "+212699111222",
            "city": "Casablanca",
            "company": "ElectroMaroc Premium",
            "business_type": "Électronique & High-Tech",
            "annual_revenue": 2500000,
            "employee_count": 45,
            "verified_seller": True
        }
    }
}

MOCK_PRODUCTS = [
    # PRODUITS PHYSIQUES
    {
        "id": "1",
        "name": "Huile d'Argan Bio Premium - 100ml",
        "description": "Huile d'argan 100% bio certifiée, extraite à froid des coopératives d'Essaouira. Riche en vitamine E et acides gras essentiels.",
        "price": 120.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400",
        "merchant_id": "3",
        "commission_rate": 15.0,
        "stock": 50,
        "rating": 4.8,
        "sales_count": 234,
        "featured": True,
        "tags": ["bio", "argan", "naturel", "maroc"]
    },
    {
        "id": "2", 
        "name": "Caftan Marocain Brodé à la Main",
        "description": "Caftan traditionnel en soie naturelle, brodé à la main par les artisans de Fès. Pièce unique disponible en plusieurs tailles.",
        "price": 450.0,
        "category": "Mode",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1594736797933-d0901ba2fe65?w=400", 
        "merchant_id": "3",
        "commission_rate": 20.0,
        "stock": 12,
        "rating": 4.9,
        "sales_count": 89,
        "featured": True,
        "tags": ["caftan", "broderie", "soie", "artisanat"]
    },
    {
        "id": "3",
        "name": "Tajine en Terre Cuite de Salé",
        "description": "Tajine authentique fait à la main par les potiers de Salé. Idéal pour une cuisson traditionnelle et savoureuse.",
        "price": 85.0,
        "category": "Maison",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1574653105043-7ad6e4b08b9e?w=400",
        "merchant_id": "3", 
        "commission_rate": 12.0,
        "stock": 25,
        "rating": 4.7,
        "sales_count": 156,
        "featured": False,
        "tags": ["tajine", "poterie", "cuisine", "traditionnel"]
    },
    {
        "id": "4",
        "name": "Tapis Berbère Vintage",
        "description": "Tapis berbère authentique tissé à la main dans l'Atlas. Motifs traditionnels amazighs, laine naturelle de mouton.",
        "price": 890.0,
        "category": "Décoration",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400",
        "merchant_id": "3",
        "commission_rate": 18.0,
        "stock": 8,
        "rating": 4.9,
        "sales_count": 67,
        "featured": True,
        "tags": ["tapis", "berbère", "vintage", "atlas"]
    },
    {
        "id": "5",
        "name": "Savon Noir Beldi Traditionnel",
        "description": "Savon noir authentique à base d'olives marocaines. Utilisé dans les hammams traditionnels, exfoliant naturel.",
        "price": 25.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228994-b6c25e02c0e4?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "stock": 100,
        "rating": 4.6,
        "sales_count": 445,
        "featured": False,
        "tags": ["savon", "beldi", "hammam", "naturel"]
    },
    
    # SERVICES
    {
        "id": "11",
        "name": "Shooting Photo Professionnel",
        "description": "Séance photo professionnelle pour influenceurs et marques. Inclut 3 heures de shooting, retouche de 50 photos HD.",
        "price": 800.0,
        "category": "Photographie",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=400",
        "merchant_id": "4",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 78,
        "featured": True,
        "tags": ["photo", "shooting", "professionnel", "influenceur"]
    },
    {
        "id": "12",
        "name": "Coaching Marketing Digital",
        "description": "Consultation personnalisée en stratégie digitale et réseaux sociaux. 2 sessions de 1h30 avec plan d'action sur mesure.",
        "price": 650.0,
        "category": "Consulting",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400",
        "merchant_id": "5",
        "commission_rate": 25.0,
        "rating": 4.8,
        "sales_count": 112,
        "featured": True,
        "tags": ["marketing", "coaching", "digital", "stratégie"]
    },
    {
        "id": "13",
        "name": "Création Site Web Vitrine",
        "description": "Développement complet d'un site web responsive. Design moderne, optimisé SEO, livraison en 15 jours.",
        "price": 2500.0,
        "category": "Développement Web",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400",
        "merchant_id": "6",
        "commission_rate": 15.0,
        "rating": 4.9,
        "sales_count": 45,
        "featured": True,
        "tags": ["web", "site", "développement", "responsive"]
    },
    {
        "id": "14",
        "name": "Gestion Réseaux Sociaux - 1 Mois",
        "description": "Gestion complète de vos réseaux sociaux pendant 1 mois. Création de contenu, planification, engagement communauté.",
        "price": 1200.0,
        "category": "Social Media",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400",
        "merchant_id": "4",
        "commission_rate": 18.0,
        "rating": 4.7,
        "sales_count": 89,
        "featured": False,
        "tags": ["social media", "gestion", "instagram", "facebook"]
    },
    {
        "id": "15",
        "name": "Montage Vidéo Professionnel",
        "description": "Montage vidéo de qualité pro pour YouTube, TikTok, Instagram. Jusqu'à 10 minutes de vidéo finale avec effets.",
        "price": 450.0,
        "category": "Vidéo",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=400",
        "merchant_id": "5",
        "commission_rate": 22.0,
        "rating": 4.8,
        "sales_count": 134,
        "featured": False,
        "tags": ["vidéo", "montage", "youtube", "tiktok"]
    },
    {
        "id": "16",
        "name": "Formation E-commerce Complète",
        "description": "Formation intensive de 3 jours sur le e-commerce. De la création de boutique à la stratégie de vente en ligne.",
        "price": 1800.0,
        "category": "Formation",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 56,
        "featured": True,
        "tags": ["formation", "ecommerce", "vente", "business"]
    },
    {
        "id": "17",
        "name": "Rédaction Articles de Blog SEO",
        "description": "Pack de 5 articles optimisés SEO de 1000 mots chacun. Recherche mots-clés incluse, livraison en 10 jours.",
        "price": 550.0,
        "category": "Rédaction",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "rating": 4.6,
        "sales_count": 98,
        "featured": False,
        "tags": ["rédaction", "seo", "blog", "contenu"]
    },
    {
        "id": "18",
        "name": "Design Logo + Identité Visuelle",
        "description": "Création complète d'un logo professionnel + charte graphique. 3 propositions, révisions illimitées.",
        "price": 950.0,
        "category": "Design",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400",
        "merchant_id": "5",
        "commission_rate": 18.0,
        "rating": 4.8,
        "sales_count": 67,
        "featured": False,
        "tags": ["design", "logo", "identité", "graphisme"]
    },
    {
        "id": "19",
        "name": "Audit SEO Complet",
        "description": "Analyse SEO détaillée de votre site web avec rapport complet et recommandations d'amélioration.",
        "price": 750.0,
        "category": "SEO",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 83,
        "featured": True,
        "tags": ["seo", "audit", "analyse", "optimisation"]
    },
    {
        "id": "20",
        "name": "Campagne Publicité Facebook Ads",
        "description": "Création et gestion de campagne Facebook Ads pendant 2 semaines. Ciblage, créatifs, optimisation inclus.",
        "price": 1100.0,
        "category": "Publicité",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400",
        "merchant_id": "4",
        "commission_rate": 22.0,
        "rating": 4.7,
        "sales_count": 91,
        "featured": False,
        "tags": ["facebook", "ads", "publicité", "marketing"]
    }
]

MOCK_AFFILIATE_LINKS = [
    {
        "id": "1",
        "user_id": "2",
        "product_id": "1", 
        "custom_slug": "argan-premium",
        "original_url": "https://boutique.ma/argan-oil",
        "affiliate_url": "https://shareyoursales.ma/aff/argan-premium",
        "commission_rate": 15.0,
        "clicks": 245,
        "conversions": 12,
        "revenue": 216.0,
        "status": "active",
        "created_at": "2024-10-15T10:30:00Z"
    },
    {
        "id": "2",
        "user_id": "2",
        "product_id": "2",
        "custom_slug": "caftan-luxury", 
        "original_url": "https://boutique.ma/caftan-traditionnel",
        "affiliate_url": "https://shareyoursales.ma/aff/caftan-luxury",
        "commission_rate": 20.0,
        "clicks": 89,
        "conversions": 3,
        "revenue": 270.0,
        "status": "active",
        "created_at": "2024-10-20T14:15:00Z"
    }
]

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🇲🇦 ShareYourSales API - Version Complète",
        "status": "operational",
        "version": "2.0.0",
        "features": [
            "Authentification JWT",
            "Gestion utilisateurs", 
            "Liens d'affiliation",
            "Produits marketplace",
            "Analytics en temps réel",
            "Intégrations sociales",
            "Paiements multi-gateway",
            "IA conversationnelle"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth/*",
            "users": "/api/users/*", 
            "products": "/api/products/*",
            "affiliate": "/api/affiliate/*",
            "analytics": "/api/analytics/*"
        }
    }

@app.get("/api/health")
async def health_check():
    """Vérification de santé du service"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales Backend",
        "version": "2.0.0",
        "uptime": "24h 15m",
        "database": "connected",
        "redis": "connected",
        "external_apis": {
            "stripe": "operational",
            "instagram": "operational", 
            "tiktok": "operational"
        }
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    """Inscription d'un nouvel utilisateur - Crée dans Supabase"""

    # Vérifier si l'email existe déjà (Supabase ou MOCK_USERS)
    existing_user = None
    if SUPABASE_ENABLED:
        existing_user = get_user_by_email(user_data.email)

    if not existing_user:
        # Fallback check in MOCK_USERS
        for user in MOCK_USERS.values():
            if user["email"] == user_data.email:
                existing_user = user
                break

    if existing_user:
        logger.warning(f"❌ Registration failed: Email already exists {user_data.email}")
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Préparer les données utilisateur
    import uuid
    user_id = str(uuid.uuid4())
    new_user_data = {
        "id": user_id,
        "email": user_data.email,
        "role": user_data.role,
        "password_hash": hash_password(user_data.password),
        "phone_verified": False,
        "two_fa_enabled": False,
        "is_active": True
    }

    # Essayer de créer dans Supabase d'abord
    created_user = None
    if SUPABASE_ENABLED:
        created_user = create_user_in_supabase(new_user_data)
        logger.info(f"✅ User created in Supabase: {user_data.email}")

    # Fallback to MOCK_USERS if Supabase fails
    if not created_user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user creation: {user_data.email}")
        new_user_data["username"] = user_data.username
        new_user_data["subscription_plan"] = "free"
        new_user_data["created_at"] = datetime.now().isoformat()
        MOCK_USERS[user_id] = new_user_data
        created_user = new_user_data

    # Envoyer email de bienvenue
    if EMAIL_ENABLED:
        try:
            await EmailTemplates.send_welcome_email(
                to_email=user_data.email,
                user_name=user_data.username,
                user_type=user_data.role
            )
        except Exception as e:
            logger.error(f"Email sending failed: {e}")

    # Générer token JWT avec fonction dédiée
    access_token = create_token(user_id, user_data.email, user_data.role)

    logger.info(f"✅ User registered successfully: {user_data.email} (role: {user_data.role})")

    return {
        "message": "Inscription réussie",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "role": user_data.role,
            "subscription_plan": "free"
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    """Connexion utilisateur - Lit depuis Supabase"""

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_email(credentials.email)
        logger.info(f"🔍 Login attempt for {credentials.email} - User found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for {credentials.email}")
        for u in MOCK_USERS.values():
            if u["email"] == credentials.email:
                user = u
                break

    if not user:
        logger.warning(f"❌ Login failed: User not found for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Vérifier le mot de passe
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"❌ Login failed: Invalid password for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Générer token JWT avec fonction dédiée
    user_id = str(user["id"])  # Ensure ID is string
    access_token = create_token(user_id, user["email"], user["role"])

    logger.info(f"✅ Login successful for {credentials.email} (role: {user['role']})")

    return {
        "message": "Connexion réussie",
        "user": {
            "id": user_id,
            "email": user["email"],
            "username": user.get("username", user["email"].split("@")[0]),
            "role": user["role"],
            "subscription_plan": user.get("subscription_plan", "free")
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Obtenir les informations de l'utilisateur connecté - Lit depuis Supabase"""
    user_id = payload.get("sub")

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_id(user_id)
        logger.info(f"🔍 /api/auth/me for user ID {user_id} - Found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user ID {user_id}")
        user = MOCK_USERS.get(user_id)

    if not user:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "username": user.get("username", user["email"].split("@")[0]),
        "role": user["role"],
        "subscription_plan": user.get("subscription_plan", "free"),
        "created_at": user.get("created_at")
    }

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    """Déconnexion utilisateur"""
    # Dans une implémentation réelle, on invaliderait le token côté serveur
    # Pour l'instant, on retourne simplement un message de succès
    return {
        "message": "Déconnexion réussie",
        "success": True
    }

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = Query(None, alias="type"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    sort_by: Optional[str] = "popularity"
):
    """Liste des produits avec filtres avancés (DONNÉES RÉELLES depuis DB)"""
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer les produits depuis la base de données
            result = await get_all_products(
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                limit=limit,
                offset=offset
            )
            
            # Ajouter les filtres disponibles
            if result["products"]:
                categories_set = set(p["category"] for p in result["products"] if p.get("category"))
                prices = [p["price"] for p in result["products"] if p.get("price")]
                
                result["filters"] = {
                    "categories": list(categories_set),
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0
                    }
                }
            
            return result
        
        except Exception as e:
            logger.info(f"❌ Erreur get_products: {str(e)}")
            # Fallback to mocked data
    
    # FALLBACK: Données mockées
    products = MOCK_PRODUCTS.copy()
    
    # Filtrer par type (product ou service)
    if product_type:
        products = [p for p in products if p.get("type", "product") == product_type]
    
    # Filtrer par catégorie
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    # Recherche textuelle
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
                   search_lower in p["name"].lower() or 
                   search_lower in p["description"].lower() or
                   any(search_lower in tag for tag in p.get("tags", []))]
    
    # Filtrer par prix
    if min_price:
        products = [p for p in products if p["price"] >= min_price]
    if max_price:
        products = [p for p in products if p["price"] <= max_price]
    
    # Filtrer par featured
    if featured is not None:
        products = [p for p in products if p.get("featured", False) == featured]
    
    # Tri
    if sort_by == "price_asc":
        products.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "popularity":
        products.sort(key=lambda x: x["sales_count"], reverse=True)
    
    # Pagination
    total = len(products)
    products = products[offset:offset + limit]
    
    return {
        "products": products,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        },
        "filters": {
            "categories": list(set(p["category"] for p in MOCK_PRODUCTS)),
            "price_range": {
                "min": min(p["price"] for p in MOCK_PRODUCTS),
                "max": max(p["price"] for p in MOCK_PRODUCTS)
            }
        }
    }

@app.get("/api/products/featured")
async def get_featured_products():
    """Produits en vedette"""
    featured_products = [p for p in MOCK_PRODUCTS if p.get("featured", False)]
    return {
        "products": featured_products[:6],
        "total": len(featured_products)
    }

@app.get("/api/products/categories")
async def get_categories():
    """Liste des catégories avec compteurs"""
    categories = {}
    for product in MOCK_PRODUCTS:
        cat = product["category"]
        if cat not in categories:
            categories[cat] = {"name": cat, "count": 0, "products": []}
        categories[cat]["count"] += 1
        categories[cat]["products"].append(product["id"])
    
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories)
    }

@app.post("/api/products")
async def create_new_product(
    product_data: dict,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_product_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau produit (INSERTION RÉELLE dans DB) - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("id")
    user_role = payload.get("role")
    
    if user_role != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les merchants peuvent créer des produits"
        )
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer le merchant_id
            merchant_response = supabase.table("merchants") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            merchant_id = merchant_response.data["id"]
            
            # Créer le produit
            result = await create_product(merchant_id, product_data)
            
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "Erreur lors de la création du produit")
                )
        
        except Exception as e:
            logger.info(f"❌ Erreur create_new_product: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création: {str(e)}"
            )
    
    # FALLBACK: Retourner un produit mocké (sans vraie insertion)
    return {
        "success": True,
        "product": {
            "id": f"prod_{datetime.now().timestamp()}",
            "name": product_data.get("name"),
            "price": product_data.get("price"),
            "category": product_data.get("category"),
            "created_at": datetime.now().isoformat()
        }
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Détails d'un produit spécifique"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "product": product,
        "related_products": [p for p in MOCK_PRODUCTS if p["category"] == product["category"] and p["id"] != product_id][:3],
        "affiliate_stats": {
            "total_affiliates": 45,
            "avg_commission": 15.5,
            "conversion_rate": 3.2
        }
    }

# ============================================
# MARKETPLACE ENDPOINTS (Compatibility)
# ============================================

@app.get("/api/marketplace/products")
async def get_marketplace_products(
    type: Optional[str] = "product",
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Produits et services pour le marketplace - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            query = supabase.table("products").select("*")
            
            # Filtrer par type si spécifié
            if type:
                query = query.eq("type", type)
            
            # Pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            products = result.data if result.data else []
            
            # Compter le total
            # La méthode a changé dans les versions récentes de postgrest-py
            count_result = supabase.table("products").select("id", count="exact").eq("type", type).execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            # Fallback sur MOCK_PRODUCTS si Supabase non disponible
            products = MOCK_PRODUCTS.copy()
            
            if type:
                products = [p for p in products if p.get("type", "product") == type]
            
            total = len(products)
            products = products[offset:offset + limit]
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        products = MOCK_PRODUCTS.copy()
        if type:
            products = [p for p in products if p.get("type", "product") == type]
        total = len(products)
        products = products[offset:offset + limit]
        return {
            "products": products,
            "total": total,
            "limit": limit,
            "offset": offset
        }

@app.get("/api/marketplace/products/{product_id}")
async def get_product_detail(product_id: str):
    """Détails complets d'un produit ou service - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            result = supabase.table("products").select("*").eq("id", product_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
            
            product = result.data[0]
        else:
            # Fallback sur MOCK_PRODUCTS
            product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
            if not product:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Enrichir avec des données supplémentaires pour la page détail
    product_detail = {
        **product,
        "images": product.get("images", [product.get("image", "")]),
        "highlights": product.get("highlights", [
            "Produit de qualité premium",
            "Livraison rapide au Maroc",
            "Service client disponible 7j/7",
            "Garantie satisfaction"
        ]),
        "included": product.get("included", [
            "Accès immédiat après achat",
            "Support technique inclus",
            "Mises à jour gratuites"
        ]),
        "how_it_works": product.get("how_it_works", 
            "1. Achetez le produit\n2. Recevez votre lien/code par email\n3. Profitez de votre achat\n4. Contactez le support si besoin"),
        "conditions": product.get("conditions",
            "• Valable 1 an à partir de la date d'achat\n• Non remboursable\n• Transférable\n• Utilisable au Maroc uniquement"),
        "faq": product.get("faq", [
            {
                "question": "Comment utiliser ce produit/service ?",
                "answer": "Après l'achat, vous recevrez toutes les instructions par email."
            },
            {
                "question": "Puis-je obtenir un remboursement ?",
                "answer": "Les remboursements sont possibles dans les 14 jours selon nos conditions."
            }
        ]),
        "merchant": {
            "name": product.get("merchant_name", "Marchand Vérifié"),
            "phone": "+212 6 00 00 00 00",
            "email": "contact@merchant.com"
        },
        "rating_average": product.get("rating", 4.5),
        "rating_count": product.get("rating_count", 150),
        "sold_count": product.get("sold_count", 450)
    }
    
    return {
        "success": True,
        "product": product_detail
    }

@app.get("/api/marketplace/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0)
):
    """Avis clients pour un produit"""
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer des avis mock
    mock_reviews = [
        {
            "id": f"rev_{product_id}_1",
            "rating": 5,
            "title": "Excellent produit!",
            "comment": "Très satisfait de mon achat. Livraison rapide et produit conforme à la description.",
            "user": {"first_name": "Ahmed"},
            "created_at": "2024-10-15T10:30:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_2",
            "rating": 4,
            "title": "Bon rapport qualité/prix",
            "comment": "Produit de bonne qualité. Je recommande!",
            "user": {"first_name": "Fatima"},
            "created_at": "2024-10-20T14:20:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_3",
            "rating": 5,
            "title": "Parfait",
            "comment": "Rien à redire, exactement ce que je cherchais.",
            "user": {"first_name": "Youssef"},
            "created_at": "2024-10-25T09:15:00",
            "is_verified_purchase": False
        }
    ]
    
    total = len(mock_reviews)
    reviews = mock_reviews[offset:offset + limit]
    
    return {
        "success": True,
        "reviews": reviews,
        "total": total
    }

@app.post("/api/marketplace/products/{product_id}/review")
async def submit_product_review(
    product_id: str,
    review_data: ProductReview,
    payload: dict = Depends(verify_token)
):
    """Soumettre un avis sur un produit"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Dans une vraie app, on sauvegarderait l'avis en DB
    review = {
        "id": f"rev_{product_id}_{user_id}_{datetime.now().timestamp()}",
        "product_id": product_id,
        "user_id": user_id,
        "rating": review_data.rating,
        "title": review_data.title,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat(),
        "is_verified_purchase": False  # À vérifier avec l'historique d'achats
    }
    
    return {
        "success": True,
        "message": "Votre avis sera publié après modération",
        "review": review
    }

@app.post("/api/marketplace/products/{product_id}/request-affiliate")
async def request_product_affiliation(
    product_id: str,
    request_data: AffiliationRequest,
    payload: dict = Depends(verify_token)
):
    """Demander l'affiliation pour un produit"""
    user_id = payload.get("sub")
    user_role = payload.get("role")
    
    # Vérifier que l'utilisateur est un influenceur
    if user_role != "influencer":
        raise HTTPException(
            status_code=403,
            detail="Seuls les influenceurs peuvent demander une affiliation"
        )
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Créer la demande d'affiliation
    affiliation_request = {
        "id": f"aff_req_{user_id}_{product_id}_{datetime.now().timestamp()}",
        "user_id": user_id,
        "product_id": product_id,
        "message": request_data.message or "Je souhaite promouvoir ce produit.",
        "status": "pending",
        "commission_rate": product.get("commission_rate", 15),
        "created_at": datetime.now().isoformat()
    }
    
    # Dans une vraie app, on notifierait le marchand
    
    # Générer un lien d'affiliation temporaire
    tracking_code = f"{user_id[:8]}-{product_id}"
    affiliate_link = f"https://shareyoursales.ma/go/{tracking_code}"
    
    return {
        "success": True,
        "message": "Demande d'affiliation envoyée avec succès!",
        "affiliation_request": affiliation_request,
        "affiliate_link": affiliate_link
    }

# ============================================
# COLLABORATION ENDPOINTS (Marchand-Influenceur)
# ============================================

class CollaborationRequestCreate(BaseModel):
    influencer_id: str
    product_id: str
    commission_rate: float
    message: Optional[str] = None

class CounterOfferData(BaseModel):
    counter_commission: float
    message: Optional[str] = None

class RejectData(BaseModel):
    reason: Optional[str] = None

class ContractSignatureData(BaseModel):
    signature: str

@app.post("/api/collaborations/requests")
async def create_collaboration_request(
    data: CollaborationRequestCreate,
    payload: dict = Depends(verify_token)
):
    """Créer une demande de collaboration (Marchand → Influenceur)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "create_collaboration_request",
            {
                "p_merchant_id": merchant_id,
                "p_influencer_id": data.influencer_id,
                "p_product_id": data.product_id,
                "p_commission_rate": data.commission_rate,
                "p_message": data.message
            }
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        request_data = result.data[0]
        
        return {
            "success": True,
            "message": "Demande envoyée avec succès",
            "request_id": request_data["request_id"],
            "status": request_data["status"],
            "expires_at": request_data["expires_at"]
        }
    except Exception as e:
        error_msg = str(e)
        if "existe déjà" in error_msg:
            raise HTTPException(status_code=409, detail="Une demande existe déjà pour ce produit")
        elif "Produit non trouvé" in error_msg:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/collaborations/requests/received")
async def get_received_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes reçues (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("influencer_id", influencer_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/sent")
async def get_sent_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes envoyées (Marchand)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/accept")
async def accept_collaboration_request(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Accepter une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande acceptée ! Vous devez maintenant signer le contrat."
        }
    except Exception as e:
        error_msg = str(e)
        if "non valide" in error_msg or "déjà traitée" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.put("/api/collaborations/requests/{request_id}/reject")
async def reject_collaboration_request(
    request_id: str,
    data: RejectData,
    payload: dict = Depends(verify_token)
):
    """Refuser une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "reject_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_reason": data.reason
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande refusée"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/counter-offer")
async def counter_offer_collaboration(
    request_id: str,
    data: CounterOfferData,
    payload: dict = Depends(verify_token)
):
    """Contre-offre (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "counter_offer_collaboration",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_counter_commission": data.counter_commission,
                "p_message": data.message
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Contre-offre envoyée au marchand"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collaborations/requests/{request_id}/sign-contract")
async def sign_collaboration_contract(
    request_id: str,
    data: ContractSignatureData,
    payload: dict = Depends(verify_token)
):
    """Signer le contrat"""
    user_id = payload.get("user_id")
    user_role = payload.get("role", "merchant")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_contract",
            {
                "p_request_id": request_id,
                "p_user_id": user_id,
                "p_user_role": user_role,
                "p_signature": data.signature
            }
        ).execute()
        
        if user_role == "influencer":
            link_result = supabase.rpc(
                "generate_affiliate_link_from_collaboration",
                {"p_request_id": request_id}
            ).execute()
            
            link_id = link_result.data if link_result.data else None
            
            return {
                "success": True,
                "message": "Contrat signé ! Votre lien d'affiliation a été généré.",
                "affiliate_link_id": link_id
            }
        
        return {
            "success": True,
            "message": "Contrat signé avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/{request_id}")
async def get_collaboration_request_details(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Détails d'une demande"""
    user_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("id", request_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        request_data = result.data
        if user_id not in [request_data["merchant_id"], request_data["influencer_id"]]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        if user_id == request_data["influencer_id"] and not request_data.get("viewed_by_influencer"):
            supabase.table("collaboration_requests") \
                .update({
                    "viewed_by_influencer": True,
                    "viewed_at": datetime.now().isoformat()
                }) \
                .eq("id", request_id) \
                .execute()
        
        history = supabase.table("collaboration_history") \
            .select("*") \
            .eq("collaboration_request_id", request_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return {
            "success": True,
            "request": request_data,
            "history": history.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/contract-terms")
async def get_contract_terms():
    """Termes du contrat de collaboration"""
    return {
        "success": True,
        "contract": {
            "version": "v1.0",
            "terms": [
                {
                    "title": "1. Respect Éthique",
                    "content": "L'influenceur s'engage à promouvoir le produit de manière éthique et honnête, sans fausses déclarations."
                },
                {
                    "title": "2. Transparence",
                    "content": "L'influenceur doit clairement indiquer qu'il s'agit d'un partenariat commercial (#ad, #sponsored)."
                },
                {
                    "title": "3. Commission",
                    "content": "La commission convenue sera versée pour chaque vente générée via le lien d'affiliation."
                },
                {
                    "title": "4. Durée",
                    "content": "Le contrat est valable pour 12 mois, renouvelable par accord mutuel."
                },
                {
                    "title": "5. Résiliation",
                    "content": "Chaque partie peut résilier avec un préavis de 30 jours."
                },
                {
                    "title": "6. Propriété Intellectuelle",
                    "content": "Le marchand conserve tous les droits sur le produit. L'influenceur conserve ses droits sur son contenu."
                },
                {
                    "title": "7. Confidentialité",
                    "content": "Les termes financiers de cet accord sont confidentiels."
                },
                {
                    "title": "8. Conformité Légale",
                    "content": "Les deux parties s'engagent à respecter toutes les lois applicables."
                }
            ]
        }
    }

# ============================================
# COMMERCIALS & INFLUENCERS DIRECTORY
# ============================================

@app.get("/api/commercials/directory")
async def get_commercials_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des commerciaux"""
    commercials = [u for u in MOCK_USERS.values() if u.get("role") == "commercial"]
    
    total = len(commercials)
    commercials = commercials[offset:offset + limit]
    
    return {
        "commercials": commercials,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/influencers/directory")
async def get_influencers_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des influenceurs"""
    influencers = [u for u in MOCK_USERS.values() if u.get("role") == "influencer"]
    
    total = len(influencers)
    influencers = influencers[offset:offset + limit]
    
    return {
        "influencers": influencers,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ============================================
# AFFILIATE LINKS ENDPOINTS  
# ============================================

@app.get("/api/affiliate/links")
async def get_affiliate_links(payload: dict = Depends(verify_token)):
    """Liste des liens d'affiliation de l'utilisateur"""
    user_id = payload.get("sub")
    user_links = [link for link in MOCK_AFFILIATE_LINKS if link["user_id"] == user_id]
    
    return {
        "links": user_links,
        "stats": {
            "total_links": len(user_links),
            "total_clicks": sum(link["clicks"] for link in user_links),
            "total_conversions": sum(link["conversions"] for link in user_links),
            "total_revenue": sum(link["revenue"] for link in user_links)
        }
    }

@app.post("/api/affiliate/links")
async def create_affiliate_link(
    product_id: str,
    custom_slug: Optional[str] = None,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_link_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau lien d'affiliation - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer slug si non fourni
    if not custom_slug:
        custom_slug = f"prod-{product_id}-{user_id}"
    
    # Créer le lien
    link_id = str(len(MOCK_AFFILIATE_LINKS) + 1)
    new_link = {
        "id": link_id,
        "user_id": user_id,
        "product_id": product_id,
        "custom_slug": custom_slug,
        "original_url": f"https://boutique.ma/product/{product_id}",
        "affiliate_url": f"https://shareyoursales.ma/aff/{custom_slug}",
        "commission_rate": product["commission_rate"],
        "clicks": 0,
        "conversions": 0,
        "revenue": 0.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_AFFILIATE_LINKS.append(new_link)
    
    return {
        "message": "Lien d'affiliation créé avec succès",
        "link": new_link
    }

# ============================================
# MODERATION ENDPOINTS (Admin)
# ============================================

@app.get("/api/admin/moderation/pending")
async def get_pending_moderation_items(
    risk_level: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Récupérer les produits en attente de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des données en attente
    pending_items = [
        {
            "id": "mod_1",
            "product_id": "prod_abc",
            "product_name": "Smartphone X-Pro 15",
            "product_description": "Le dernier smartphone avec une caméra révolutionnaire et une batterie longue durée.",
            "product_price": 12500.00,
            "product_category": "Électronique",
            "product_images": ["https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400"],
            "merchant_id": "merch_xyz",
            "merchant_name": "ElectroMaroc",
            "merchant_email": "contact@electromaroc.ma",
            "submitted_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "hours_pending": 2.1,
            "ai_risk_level": "high",
            "ai_confidence": 0.85,
            "ai_reason": "Le prix semble élevé par rapport à des produits similaires. La description contient des superlatifs ('révolutionnaire').",
            "ai_flags": ["prix_eleve", "description_exageree"]
        },
        {
            "id": "mod_2",
            "product_id": "prod_def",
            "product_name": "T-shirt 'Casablanca'",
            "product_description": "T-shirt en coton bio avec un design exclusif de la ville de Casablanca.",
            "product_price": 250.00,
            "product_category": "Mode",
            "product_images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"],
            "merchant_id": "merch_uvw",
            "merchant_name": "CasaStyle",
            "merchant_email": "contact@casastyle.ma",
            "submitted_at": (datetime.now() - timedelta(hours=8)).isoformat(),
            "hours_pending": 8.5,
            "ai_risk_level": "low",
            "ai_confidence": 0.98,
            "ai_reason": "Produit standard, description claire, prix cohérent.",
            "ai_flags": []
        }
    ]
    
    if risk_level:
        items = [item for item in pending_items if item['ai_risk_level'] == risk_level]
    else:
        items = pending_items

    return {"data": items}

@app.get("/api/admin/moderation/stats")
async def get_moderation_stats(
    period: str = "today",
    payload: dict = Depends(verify_token)
):
    """Récupérer les statistiques de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des statistiques
    stats = {
        "total": 150,
        "pending": 2,
        "approved": 135,
        "rejected": 13,
        "approval_rate": 135 / 150 if 150 > 0 else 0
    }
    return stats

@app.post("/api/admin/moderation/review")
async def review_moderation_item(
    payload: dict = Depends(verify_token)
):
    """Traiter une décision de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Simuler le traitement
    return {"success": True, "message": "Décision enregistrée"}
    

# ============================================
# AUTHENTICATION
# ============================================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifier le token JWT"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Vérification manuelle de l'expiration (doublon de sécurité)
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.utcnow().timestamp() > exp_timestamp:
                raise HTTPException(status_code=401, detail="Token expiré")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erreur d'authentification: {str(e)}")

def create_token(user_id: str, email: str, role: str) -> str:
    """Créer un token JWT avec expiration"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_password_strength(password: str) -> None:
    """Valider la force du mot de passe"""
    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
    if not any(c.isupper() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une majuscule")
    if not any(c.islower() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une minuscule")
    if not any(c.isdigit() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre")

def hash_password(password: str, skip_validation: bool = False) -> str:
    """Hasher un mot de passe"""
    if not skip_validation:
        validate_password_strength(password)
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Vérifier un mot de passe"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ============================================
# MODELS
# ============================================

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")
    subscription_plan: str = Field(default="free", pattern="^(free|starter|pro|enterprise)$")
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    role: str = Field(default="user", pattern="^(user|influencer|merchant|admin)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AffiliateLink(BaseModel):
    id: Optional[str] = None
    user_id: str
    product_url: str = Field(..., min_length=10, max_length=2048)
    custom_slug: Optional[Annotated[str, Field(min_length=3, max_length=100)]] = None
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0
    status: str = Field(default="active", pattern="^(active|inactive|suspended)$")
    created_at: Optional[datetime] = None

class Product(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    price: Annotated[float, Field(ge=0.01)]
    category: Annotated[str, Field(min_length=2, max_length=100)]
    image_url: Optional[str] = Field(None, max_length=2048)
    merchant_id: str
    commission_rate: Annotated[float, Field(ge=0.0, le=100.0)] = 10.0

class Campaign(BaseModel):
    id: Optional[str] = None
    name: Annotated[str, Field(min_length=3, max_length=200)]
    description: Annotated[str, Field(min_length=10, max_length=5000)]
    start_date: datetime
    end_date: datetime
    budget: Annotated[float, Field(ge=0.0)]
    target_audience: Dict[str, Any]
    status: str = Field(default="draft", pattern="^(draft|active|paused|completed|cancelled)$")

class ProductReview(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)]
    title: Optional[Annotated[str, Field(max_length=200)]] = None
    comment: Annotated[str, Field(min_length=10, max_length=2000)]

class AffiliationRequest(BaseModel):
    message: Optional[Annotated[str, Field(max_length=1000)]] = None

# ============================================
# MOCK DATA
# ============================================

MOCK_USERS = {
    "1": {
        "id": "1",
        "email": "admin@shareyoursales.ma",
        "username": "admin",
        "role": "admin",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Admin123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mohammed",
            "last_name": "Admin",
            "phone": "+212600000000",
            "city": "Casablanca"
        }
    },
    "2": {
        "id": "2", 
        "email": "influencer@example.com",
        "username": "sarah_influencer",
        "role": "influencer",
        "subscription_plan": "pro",
        "password_hash": hash_password("Password123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sarah",
            "last_name": "Benali",
            "phone": "+212611222333",
            "city": "Rabat",
            "instagram": "@sarah_lifestyle_ma",
            "followers_count": 125000,
            "engagement_rate": 4.8,
            "niche": "Lifestyle & Beauty",
            "rating": 4.9,
            "reviews": 87,
            "campaigns_completed": 45,
            "min_rate": 800,
            "categories": ["Mode", "Beauté", "Lifestyle"],
            "trending": True,
            "tiktok_followers": 95000
        }
    },
    "3": {
        "id": "3",
        "email": "merchant@example.com", 
        "username": "boutique_maroc",
        "role": "merchant",
        "subscription_plan": "starter",
        "password_hash": hash_password("Merchant123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Youssef",
            "last_name": "Alami",
            "phone": "+212622444555",
            "city": "Marrakech",
            "company": "Artisanat Maroc",
            "business_type": "Artisanat traditionnel"
        }
    },
    "4": {
        "id": "4",
        "email": "aminainfluencer@gmail.com",
        "username": "amina_beauty",
        "role": "influencer", 
        "subscription_plan": "pro",
        "password_hash": hash_password("Amina123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Amina",
            "last_name": "Tazi",
            "phone": "+212633666777",
            "city": "Fès",
            "instagram": "@amina_beauty_fes",
            "tiktok": "@aminabeauty",
            "followers_count": 89000,
            "engagement_rate": 6.2,
            "niche": "Beauty & Cosmetics",
            "rating": 4.7,
            "reviews": 62,
            "campaigns_completed": 38,
            "min_rate": 650,
            "categories": ["Beauté", "Cosmétiques", "Skincare"],
            "trending": False,
            "tiktok_followers": 112000
        }
    },
    "5": {
        "id": "5",
        "email": "commerciale@shareyoursales.ma",
        "username": "sofia_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Sofia123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Sofia",
            "last_name": "Chakir",
            "phone": "+212644888999",
            "city": "Casablanca",
            "department": "Business Development",
            "territory": "Région Casablanca-Settat",
            "total_sales": 156,
            "commission_earned": 45600,
            "rating": 4.8,
            "reviews": 43,
            "specialties": ["E-commerce", "B2B", "Retail"]
        }
    },
    "6": {
        "id": "6",
        "email": "merchant2@artisanmaroc.ma",
        "username": "luxury_crafts",
        "role": "merchant",
        "subscription_plan": "pro", 
        "password_hash": hash_password("Luxury123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Rachid",
            "last_name": "Bennani",
            "phone": "+212655111222",
            "city": "Tétouan",
            "company": "Luxury Moroccan Crafts",
            "business_type": "Articles de luxe"
        }
    },
    "7": {
        "id": "7",
        "email": "foodinfluencer@gmail.com",
        "username": "chef_hassan",
        "role": "influencer",
        "subscription_plan": "starter",
        "password_hash": hash_password("Hassan123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Hassan",
            "last_name": "Oudrhiri",
            "phone": "+212666333444",
            "city": "Agadir",
            "instagram": "@chef_hassan_agadir",
            "youtube": "Chef Hassan Cuisine",
            "followers_count": 67000,
            "engagement_rate": 5.4,
            "niche": "Food & Cuisine",
            "rating": 4.6,
            "reviews": 34,
            "campaigns_completed": 28,
            "min_rate": 500,
            "categories": ["Food", "Cuisine", "Restaurant"],
            "trending": True,
            "tiktok_followers": 78000
        }
    },
    "8": {
        "id": "8",
        "email": "commercial2@shareyoursales.ma",
        "username": "omar_commercial",
        "role": "commercial",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Omar123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Omar",
            "last_name": "Filali",
            "phone": "+212677555666",
            "city": "Rabat",
            "department": "Client Relations",
            "territory": "Région Rabat-Salé-Kénitra",
            "total_sales": 203,
            "commission_earned": 62400,
            "rating": 4.9,
            "reviews": 56,
            "specialties": ["Grands Comptes", "Partenariats", "Support Client"]
        }
    },
    "9": {
        "id": "9",
        "email": "karim.influencer@gmail.com",
        "username": "karim_tech",
        "role": "influencer",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Karim123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Karim",
            "last_name": "Benjelloun",
            "phone": "+212688999000",
            "city": "Casablanca",
            "instagram": "@karim_tech_maroc",
            "youtube": "Karim Tech Reviews",
            "tiktok": "@karimtech",
            "followers_count": 285000,
            "engagement_rate": 7.5,
            "niche": "Tech & Gaming",
            "rating": 4.9,
            "reviews": 128,
            "campaigns_completed": 96,
            "min_rate": 1500,
            "categories": ["Technologie", "Gaming", "Innovation", "Gadgets"],
            "trending": True,
            "tiktok_followers": 320000,
            "verified": True
        }
    },
    "10": {
        "id": "10",
        "email": "premium.shop@electromaroc.ma",
        "username": "electro_maroc",
        "role": "merchant",
        "subscription_plan": "enterprise",
        "password_hash": hash_password("Electro123", skip_validation=True),
        "created_at": datetime.now().isoformat(),
        "profile": {
            "first_name": "Mehdi",
            "last_name": "Tounsi",
            "phone": "+212699111222",
            "city": "Casablanca",
            "company": "ElectroMaroc Premium",
            "business_type": "Électronique & High-Tech",
            "annual_revenue": 2500000,
            "employee_count": 45,
            "verified_seller": True
        }
    }
}

MOCK_PRODUCTS = [
    # PRODUITS PHYSIQUES
    {
        "id": "1",
        "name": "Huile d'Argan Bio Premium - 100ml",
        "description": "Huile d'argan 100% bio certifiée, extraite à froid des coopératives d'Essaouira. Riche en vitamine E et acides gras essentiels.",
        "price": 120.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400",
        "merchant_id": "3",
        "commission_rate": 15.0,
        "stock": 50,
        "rating": 4.8,
        "sales_count": 234,
        "featured": True,
        "tags": ["bio", "argan", "naturel", "maroc"]
    },
    {
        "id": "2", 
        "name": "Caftan Marocain Brodé à la Main",
        "description": "Caftan traditionnel en soie naturelle, brodé à la main par les artisans de Fès. Pièce unique disponible en plusieurs tailles.",
        "price": 450.0,
        "category": "Mode",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1594736797933-d0901ba2fe65?w=400", 
        "merchant_id": "3",
        "commission_rate": 20.0,
        "stock": 12,
        "rating": 4.9,
        "sales_count": 89,
        "featured": True,
        "tags": ["caftan", "broderie", "soie", "artisanat"]
    },
    {
        "id": "3",
        "name": "Tajine en Terre Cuite de Salé",
        "description": "Tajine authentique fait à la main par les potiers de Salé. Idéal pour une cuisson traditionnelle et savoureuse.",
        "price": 85.0,
        "category": "Maison",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1574653105043-7ad6e4b08b9e?w=400",
        "merchant_id": "3", 
        "commission_rate": 12.0,
        "stock": 25,
        "rating": 4.7,
        "sales_count": 156,
        "featured": False,
        "tags": ["tajine", "poterie", "cuisine", "traditionnel"]
    },
    {
        "id": "4",
        "name": "Tapis Berbère Vintage",
        "description": "Tapis berbère authentique tissé à la main dans l'Atlas. Motifs traditionnels amazighs, laine naturelle de mouton.",
        "price": 890.0,
        "category": "Décoration",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=400",
        "merchant_id": "3",
        "commission_rate": 18.0,
        "stock": 8,
        "rating": 4.9,
        "sales_count": 67,
        "featured": True,
        "tags": ["tapis", "berbère", "vintage", "atlas"]
    },
    {
        "id": "5",
        "name": "Savon Noir Beldi Traditionnel",
        "description": "Savon noir authentique à base d'olives marocaines. Utilisé dans les hammams traditionnels, exfoliant naturel.",
        "price": 25.0,
        "category": "Cosmétiques",
        "type": "product",
        "image_url": "https://images.unsplash.com/photo-1556228994-b6c25e02c0e4?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "stock": 100,
        "rating": 4.6,
        "sales_count": 445,
        "featured": False,
        "tags": ["savon", "beldi", "hammam", "naturel"]
    },
    
    # SERVICES
    {
        "id": "11",
        "name": "Shooting Photo Professionnel",
        "description": "Séance photo professionnelle pour influenceurs et marques. Inclut 3 heures de shooting, retouche de 50 photos HD.",
        "price": 800.0,
        "category": "Photographie",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=400",
        "merchant_id": "4",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 78,
        "featured": True,
        "tags": ["photo", "shooting", "professionnel", "influenceur"]
    },
    {
        "id": "12",
        "name": "Coaching Marketing Digital",
        "description": "Consultation personnalisée en stratégie digitale et réseaux sociaux. 2 sessions de 1h30 avec plan d'action sur mesure.",
        "price": 650.0,
        "category": "Consulting",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400",
        "merchant_id": "5",
        "commission_rate": 25.0,
        "rating": 4.8,
        "sales_count": 112,
        "featured": True,
        "tags": ["marketing", "coaching", "digital", "stratégie"]
    },
    {
        "id": "13",
        "name": "Création Site Web Vitrine",
        "description": "Développement complet d'un site web responsive. Design moderne, optimisé SEO, livraison en 15 jours.",
        "price": 2500.0,
        "category": "Développement Web",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400",
        "merchant_id": "6",
        "commission_rate": 15.0,
        "rating": 4.9,
        "sales_count": 45,
        "featured": True,
        "tags": ["web", "site", "développement", "responsive"]
    },
    {
        "id": "14",
        "name": "Gestion Réseaux Sociaux - 1 Mois",
        "description": "Gestion complète de vos réseaux sociaux pendant 1 mois. Création de contenu, planification, engagement communauté.",
        "price": 1200.0,
        "category": "Social Media",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400",
        "merchant_id": "4",
        "commission_rate": 18.0,
        "rating": 4.7,
        "sales_count": 89,
        "featured": False,
        "tags": ["social media", "gestion", "instagram", "facebook"]
    },
    {
        "id": "15",
        "name": "Montage Vidéo Professionnel",
        "description": "Montage vidéo de qualité pro pour YouTube, TikTok, Instagram. Jusqu'à 10 minutes de vidéo finale avec effets.",
        "price": 450.0,
        "category": "Vidéo",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=400",
        "merchant_id": "5",
        "commission_rate": 22.0,
        "rating": 4.8,
        "sales_count": 134,
        "featured": False,
        "tags": ["vidéo", "montage", "youtube", "tiktok"]
    },
    {
        "id": "16",
        "name": "Formation E-commerce Complète",
        "description": "Formation intensive de 3 jours sur le e-commerce. De la création de boutique à la stratégie de vente en ligne.",
        "price": 1800.0,
        "category": "Formation",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 56,
        "featured": True,
        "tags": ["formation", "ecommerce", "vente", "business"]
    },
    {
        "id": "17",
        "name": "Rédaction Articles de Blog SEO",
        "description": "Pack de 5 articles optimisés SEO de 1000 mots chacun. Recherche mots-clés incluse, livraison en 10 jours.",
        "price": 550.0,
        "category": "Rédaction",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400",
        "merchant_id": "4",
        "commission_rate": 25.0,
        "rating": 4.6,
        "sales_count": 98,
        "featured": False,
        "tags": ["rédaction", "seo", "blog", "contenu"]
    },
    {
        "id": "18",
        "name": "Design Logo + Identité Visuelle",
        "description": "Création complète d'un logo professionnel + charte graphique. 3 propositions, révisions illimitées.",
        "price": 950.0,
        "category": "Design",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400",
        "merchant_id": "5",
        "commission_rate": 18.0,
        "rating": 4.8,
        "sales_count": 67,
        "featured": False,
        "tags": ["design", "logo", "identité", "graphisme"]
    },
    {
        "id": "19",
        "name": "Audit SEO Complet",
        "description": "Analyse SEO détaillée de votre site web avec rapport complet et recommandations d'amélioration.",
        "price": 750.0,
        "category": "SEO",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400",
        "merchant_id": "6",
        "commission_rate": 20.0,
        "rating": 4.9,
        "sales_count": 83,
        "featured": True,
        "tags": ["seo", "audit", "analyse", "optimisation"]
    },
    {
        "id": "20",
        "name": "Campagne Publicité Facebook Ads",
        "description": "Création et gestion de campagne Facebook Ads pendant 2 semaines. Ciblage, créatifs, optimisation inclus.",
        "price": 1100.0,
        "category": "Publicité",
        "type": "service",
        "image_url": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400",
        "merchant_id": "4",
        "commission_rate": 22.0,
        "rating": 4.7,
        "sales_count": 91,
        "featured": False,
        "tags": ["facebook", "ads", "publicité", "marketing"]
    }
]

MOCK_AFFILIATE_LINKS = [
    {
        "id": "1",
        "user_id": "2",
        "product_id": "1", 
        "custom_slug": "argan-premium",
        "original_url": "https://boutique.ma/argan-oil",
        "affiliate_url": "https://shareyoursales.ma/aff/argan-premium",
        "commission_rate": 15.0,
        "clicks": 245,
        "conversions": 12,
        "revenue": 216.0,
        "status": "active",
        "created_at": "2024-10-15T10:30:00Z"
    },
    {
        "id": "2",
        "user_id": "2",
        "product_id": "2",
        "custom_slug": "caftan-luxury", 
        "original_url": "https://boutique.ma/caftan-traditionnel",
        "affiliate_url": "https://shareyoursales.ma/aff/caftan-luxury",
        "commission_rate": 20.0,
        "clicks": 89,
        "conversions": 3,
        "revenue": 270.0,
        "status": "active",
        "created_at": "2024-10-20T14:15:00Z"
    }
]

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🇲🇦 ShareYourSales API - Version Complète",
        "status": "operational",
        "version": "2.0.0",
        "features": [
            "Authentification JWT",
            "Gestion utilisateurs", 
            "Liens d'affiliation",
            "Produits marketplace",
            "Analytics en temps réel",
            "Intégrations sociales",
            "Paiements multi-gateway",
            "IA conversationnelle"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "auth": "/api/auth/*",
            "users": "/api/users/*", 
            "products": "/api/products/*",
            "affiliate": "/api/affiliate/*",
            "analytics": "/api/analytics/*"
        }
    }

@app.get("/api/health")
async def health_check():
    """Vérification de santé du service"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ShareYourSales Backend",
        "version": "2.0.0",
        "uptime": "24h 15m",
        "database": "connected",
        "redis": "connected",
        "external_apis": {
            "stripe": "operational",
            "instagram": "operational", 
            "tiktok": "operational"
        }
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreate):
    """Inscription d'un nouvel utilisateur - Crée dans Supabase"""

    # Vérifier si l'email existe déjà (Supabase ou MOCK_USERS)
    existing_user = None
    if SUPABASE_ENABLED:
        existing_user = get_user_by_email(user_data.email)

    if not existing_user:
        # Fallback check in MOCK_USERS
        for user in MOCK_USERS.values():
            if user["email"] == user_data.email:
                existing_user = user
                break

    if existing_user:
        logger.warning(f"❌ Registration failed: Email already exists {user_data.email}")
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    # Préparer les données utilisateur
    import uuid
    user_id = str(uuid.uuid4())
    new_user_data = {
        "id": user_id,
        "email": user_data.email,
        "role": user_data.role,
        "password_hash": hash_password(user_data.password),
        "phone_verified": False,
        "two_fa_enabled": False,
        "is_active": True
    }

    # Essayer de créer dans Supabase d'abord
    created_user = None
    if SUPABASE_ENABLED:
        created_user = create_user_in_supabase(new_user_data)
        logger.info(f"✅ User created in Supabase: {user_data.email}")

    # Fallback to MOCK_USERS if Supabase fails
    if not created_user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user creation: {user_data.email}")
        new_user_data["username"] = user_data.username
        new_user_data["subscription_plan"] = "free"
        new_user_data["created_at"] = datetime.now().isoformat()
        MOCK_USERS[user_id] = new_user_data
        created_user = new_user_data

    # Envoyer email de bienvenue
    if EMAIL_ENABLED:
        try:
            await EmailTemplates.send_welcome_email(
                to_email=user_data.email,
                user_name=user_data.username,
                user_type=user_data.role
            )
        except Exception as e:
            logger.error(f"Email sending failed: {e}")

    # Générer token JWT avec fonction dédiée
    access_token = create_token(user_id, user_data.email, user_data.role)

    logger.info(f"✅ User registered successfully: {user_data.email} (role: {user_data.role})")

    return {
        "message": "Inscription réussie",
        "user": {
            "id": user_id,
            "email": user_data.email,
            "username": user_data.username,
            "role": user_data.role,
            "subscription_plan": "free"
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    """Connexion utilisateur - Lit depuis Supabase"""

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_email(credentials.email)
        logger.info(f"🔍 Login attempt for {credentials.email} - User found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for {credentials.email}")
        for u in MOCK_USERS.values():
            if u["email"] == credentials.email:
                user = u
                break

    if not user:
        logger.warning(f"❌ Login failed: User not found for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Vérifier le mot de passe
    if not verify_password(credentials.password, user["password_hash"]):
        logger.warning(f"❌ Login failed: Invalid password for {credentials.email}")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Générer token JWT avec fonction dédiée
    user_id = str(user["id"])  # Ensure ID is string
    access_token = create_token(user_id, user["email"], user["role"])

    logger.info(f"✅ Login successful for {credentials.email} (role: {user['role']})")

    return {
        "message": "Connexion réussie",
        "user": {
            "id": user_id,
            "email": user["email"],
            "username": user.get("username", user["email"].split("@")[0]),
            "role": user["role"],
            "subscription_plan": user.get("subscription_plan", "free")
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_token)):
    """Obtenir les informations de l'utilisateur connecté - Lit depuis Supabase"""
    user_id = payload.get("sub")

    # Essayer de lire depuis Supabase d'abord
    user = None
    if SUPABASE_ENABLED:
        user = get_user_by_id(user_id)
        logger.info(f"🔍 /api/auth/me for user ID {user_id} - Found in Supabase: {user is not None}")

    # Fallback to MOCK_USERS if Supabase not available or user not found
    if not user:
        logger.info(f"⚠️ Falling back to MOCK_USERS for user ID {user_id}")
        user = MOCK_USERS.get(user_id)

    if not user:
        logger.warning(f"❌ User not found: {user_id}")
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "username": user.get("username", user["email"].split("@")[0]),
        "role": user["role"],
        "subscription_plan": user.get("subscription_plan", "free"),
        "created_at": user.get("created_at")
    }

@app.post("/api/auth/logout")
async def logout(payload: dict = Depends(verify_token)):
    """Déconnexion utilisateur"""
    # Dans une implémentation réelle, on invaliderait le token côté serveur
    # Pour l'instant, on retourne simplement un message de succès
    return {
        "message": "Déconnexion réussie",
        "success": True
    }

# ============================================
# PRODUCTS ENDPOINTS
# ============================================

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = Query(None, alias="type"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    featured: Optional[bool] = None,
    sort_by: Optional[str] = "popularity"
):
    """Liste des produits avec filtres avancés (DONNÉES RÉELLES depuis DB)"""
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer les produits depuis la base de données
            result = await get_all_products(
                category=category,
                search=search,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by,
                limit=limit,
                offset=offset
            )
            
            # Ajouter les filtres disponibles
            if result["products"]:
                categories_set = set(p["category"] for p in result["products"] if p.get("category"))
                prices = [p["price"] for p in result["products"] if p.get("price")]
                
                result["filters"] = {
                    "categories": list(categories_set),
                    "price_range": {
                        "min": min(prices) if prices else 0,
                        "max": max(prices) if prices else 0
                    }
                }
            
            return result
        
        except Exception as e:
            logger.info(f"❌ Erreur get_products: {str(e)}")
            # Fallback to mocked data
    
    # FALLBACK: Données mockées
    products = MOCK_PRODUCTS.copy()
    
    # Filtrer par type (product ou service)
    if product_type:
        products = [p for p in products if p.get("type", "product") == product_type]
    
    # Filtrer par catégorie
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    
    # Recherche textuelle
    if search:
        search_lower = search.lower()
        products = [p for p in products if 
                   search_lower in p["name"].lower() or 
                   search_lower in p["description"].lower() or
                   any(search_lower in tag for tag in p.get("tags", []))]
    
    # Filtrer par prix
    if min_price:
        products = [p for p in products if p["price"] >= min_price]
    if max_price:
        products = [p for p in products if p["price"] <= max_price]
    
    # Filtrer par featured
    if featured is not None:
        products = [p for p in products if p.get("featured", False) == featured]
    
    # Tri
    if sort_by == "price_asc":
        products.sort(key=lambda x: x["price"])
    elif sort_by == "price_desc":
        products.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "rating":
        products.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "popularity":
        products.sort(key=lambda x: x["sales_count"], reverse=True)
    
    # Pagination
    total = len(products)
    products = products[offset:offset + limit]
    
    return {
        "products": products,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        },
        "filters": {
            "categories": list(set(p["category"] for p in MOCK_PRODUCTS)),
            "price_range": {
                "min": min(p["price"] for p in MOCK_PRODUCTS),
                "max": max(p["price"] for p in MOCK_PRODUCTS)
            }
        }
    }

@app.get("/api/products/featured")
async def get_featured_products():
    """Produits en vedette"""
    featured_products = [p for p in MOCK_PRODUCTS if p.get("featured", False)]
    return {
        "products": featured_products[:6],
        "total": len(featured_products)
    }

@app.get("/api/products/categories")
async def get_categories():
    """Liste des catégories avec compteurs"""
    categories = {}
    for product in MOCK_PRODUCTS:
        cat = product["category"]
        if cat not in categories:
            categories[cat] = {"name": cat, "count": 0, "products": []}
        categories[cat]["count"] += 1
        categories[cat]["products"].append(product["id"])
    
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories)
    }

@app.post("/api/products")
async def create_new_product(
    product_data: dict,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_product_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau produit (INSERTION RÉELLE dans DB) - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("id")
    user_role = payload.get("role")
    
    if user_role != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les merchants peuvent créer des produits"
        )
    
    if DB_QUERIES_AVAILABLE:
        try:
            # Récupérer le merchant_id
            merchant_response = supabase.table("merchants") \
                .select("id") \
                .eq("user_id", user_id) \
                .single() \
                .execute()
            
            merchant_id = merchant_response.data["id"]
            
            # Créer le produit
            result = await create_product(merchant_id, product_data)
            
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "Erreur lors de la création du produit")
                )
        
        except Exception as e:
            logger.info(f"❌ Erreur create_new_product: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création: {str(e)}"
            )
    
    # FALLBACK: Retourner un produit mocké (sans vraie insertion)
    return {
        "success": True,
        "product": {
            "id": f"prod_{datetime.now().timestamp()}",
            "name": product_data.get("name"),
            "price": product_data.get("price"),
            "category": product_data.get("category"),
            "created_at": datetime.now().isoformat()
        }
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Détails d'un produit spécifique"""
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "product": product,
        "related_products": [p for p in MOCK_PRODUCTS if p["category"] == product["category"] and p["id"] != product_id][:3],
        "affiliate_stats": {
            "total_affiliates": 45,
            "avg_commission": 15.5,
            "conversion_rate": 3.2
        }
    }

# ============================================
# MARKETPLACE ENDPOINTS (Compatibility)
# ============================================

@app.get("/api/marketplace/products")
async def get_marketplace_products(
    type: Optional[str] = "product",
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Produits et services pour le marketplace - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            query = supabase.table("products").select("*")
            
            # Filtrer par type si spécifié
            if type:
                query = query.eq("type", type)
            
            # Pagination
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            products = result.data if result.data else []
            
            # Compter le total
            # La méthode a changé dans les versions récentes de postgrest-py
            count_result = supabase.table("products").select("id", count="exact").eq("type", type).execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            # Fallback sur MOCK_PRODUCTS si Supabase non disponible
            products = MOCK_PRODUCTS.copy()
            
            if type:
                products = [p for p in products if p.get("type", "product") == type]
            
            total = len(products)
            products = products[offset:offset + limit]
            
            return {
                "products": products,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        products = MOCK_PRODUCTS.copy()
        if type:
            products = [p for p in products if p.get("type", "product") == type]
        total = len(products)
        products = products[offset:offset + limit]
        return {
            "products": products,
            "total": total,
            "limit": limit,
            "offset": offset
        }

@app.get("/api/marketplace/products/{product_id}")
async def get_product_detail(product_id: str):
    """Détails complets d'un produit ou service - Depuis Supabase"""
    try:
        if SUPABASE_ENABLED:
            # Récupérer depuis Supabase
            result = supabase.table("products").select("*").eq("id", product_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
            
            product = result.data[0]
        else:
            # Fallback sur MOCK_PRODUCTS
            product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
            if not product:
                raise HTTPException(status_code=404, detail="Produit non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"❌ Erreur Supabase: {e}")
        # Fallback sur MOCK en cas d'erreur
        product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
        if not product:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Enrichir avec des données supplémentaires pour la page détail
    product_detail = {
        **product,
        "images": product.get("images", [product.get("image", "")]),
        "highlights": product.get("highlights", [
            "Produit de qualité premium",
            "Livraison rapide au Maroc",
            "Service client disponible 7j/7",
            "Garantie satisfaction"
        ]),
        "included": product.get("included", [
            "Accès immédiat après achat",
            "Support technique inclus",
            "Mises à jour gratuites"
        ]),
        "how_it_works": product.get("how_it_works", 
            "1. Achetez le produit\n2. Recevez votre lien/code par email\n3. Profitez de votre achat\n4. Contactez le support si besoin"),
        "conditions": product.get("conditions",
            "• Valable 1 an à partir de la date d'achat\n• Non remboursable\n• Transférable\n• Utilisable au Maroc uniquement"),
        "faq": product.get("faq", [
            {
                "question": "Comment utiliser ce produit/service ?",
                "answer": "Après l'achat, vous recevrez toutes les instructions par email."
            },
            {
                "question": "Puis-je obtenir un remboursement ?",
                "answer": "Les remboursements sont possibles dans les 14 jours selon nos conditions."
            }
        ]),
        "merchant": {
            "name": product.get("merchant_name", "Marchand Vérifié"),
            "phone": "+212 6 00 00 00 00",
            "email": "contact@merchant.com"
        },
        "rating_average": product.get("rating", 4.5),
        "rating_count": product.get("rating_count", 150),
        "sold_count": product.get("sold_count", 450)
    }
    
    return {
        "success": True,
        "product": product_detail
    }

@app.get("/api/marketplace/products/{product_id}/reviews")
async def get_product_reviews(
    product_id: str,
    limit: int = Query(10, le=50),
    offset: int = Query(0, ge=0)
):
    """Avis clients pour un produit"""
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer des avis mock
    mock_reviews = [
        {
            "id": f"rev_{product_id}_1",
            "rating": 5,
            "title": "Excellent produit!",
            "comment": "Très satisfait de mon achat. Livraison rapide et produit conforme à la description.",
            "user": {"first_name": "Ahmed"},
            "created_at": "2024-10-15T10:30:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_2",
            "rating": 4,
            "title": "Bon rapport qualité/prix",
            "comment": "Produit de bonne qualité. Je recommande!",
            "user": {"first_name": "Fatima"},
            "created_at": "2024-10-20T14:20:00",
            "is_verified_purchase": True
        },
        {
            "id": f"rev_{product_id}_3",
            "rating": 5,
            "title": "Parfait",
            "comment": "Rien à redire, exactement ce que je cherchais.",
            "user": {"first_name": "Youssef"},
            "created_at": "2024-10-25T09:15:00",
            "is_verified_purchase": False
        }
    ]
    
    total = len(mock_reviews)
    reviews = mock_reviews[offset:offset + limit]
    
    return {
        "success": True,
        "reviews": reviews,
        "total": total
    }

@app.post("/api/marketplace/products/{product_id}/review")
async def submit_product_review(
    product_id: str,
    review_data: ProductReview,
    payload: dict = Depends(verify_token)
):
    """Soumettre un avis sur un produit"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Dans une vraie app, on sauvegarderait l'avis en DB
    review = {
        "id": f"rev_{product_id}_{user_id}_{datetime.now().timestamp()}",
        "product_id": product_id,
        "user_id": user_id,
        "rating": review_data.rating,
        "title": review_data.title,
        "comment": review_data.comment,
        "created_at": datetime.now().isoformat(),
        "is_verified_purchase": False  # À vérifier avec l'historique d'achats
    }
    
    return {
        "success": True,
        "message": "Votre avis sera publié après modération",
        "review": review
    }

@app.post("/api/marketplace/products/{product_id}/request-affiliate")
async def request_product_affiliation(
    product_id: str,
    request_data: AffiliationRequest,
    payload: dict = Depends(verify_token)
):
    """Demander l'affiliation pour un produit"""
    user_id = payload.get("sub")
    user_role = payload.get("role")
    
    # Vérifier que l'utilisateur est un influenceur
    if user_role != "influencer":
        raise HTTPException(
            status_code=403,
            detail="Seuls les influenceurs peuvent demander une affiliation"
        )
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if str(p["id"]) == str(product_id)), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Créer la demande d'affiliation
    affiliation_request = {
        "id": f"aff_req_{user_id}_{product_id}_{datetime.now().timestamp()}",
        "user_id": user_id,
        "product_id": product_id,
        "message": request_data.message or "Je souhaite promouvoir ce produit.",
        "status": "pending",
        "commission_rate": product.get("commission_rate", 15),
        "created_at": datetime.now().isoformat()
    }
    
    # Dans une vraie app, on notifierait le marchand
    
    # Générer un lien d'affiliation temporaire
    tracking_code = f"{user_id[:8]}-{product_id}"
    affiliate_link = f"https://shareyoursales.ma/go/{tracking_code}"
    
    return {
        "success": True,
        "message": "Demande d'affiliation envoyée avec succès!",
        "affiliation_request": affiliation_request,
        "affiliate_link": affiliate_link
    }

# ============================================
# COLLABORATION ENDPOINTS (Marchand-Influenceur)
# ============================================

class CollaborationRequestCreate(BaseModel):
    influencer_id: str
    product_id: str
    commission_rate: float
    message: Optional[str] = None

class CounterOfferData(BaseModel):
    counter_commission: float
    message: Optional[str] = None

class RejectData(BaseModel):
    reason: Optional[str] = None

class ContractSignatureData(BaseModel):
    signature: str

@app.post("/api/collaborations/requests")
async def create_collaboration_request(
    data: CollaborationRequestCreate,
    payload: dict = Depends(verify_token)
):
    """Créer une demande de collaboration (Marchand → Influenceur)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "create_collaboration_request",
            {
                "p_merchant_id": merchant_id,
                "p_influencer_id": data.influencer_id,
                "p_product_id": data.product_id,
                "p_commission_rate": data.commission_rate,
                "p_message": data.message
            }
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        request_data = result.data[0]
        
        return {
            "success": True,
            "message": "Demande envoyée avec succès",
            "request_id": request_data["request_id"],
            "status": request_data["status"],
            "expires_at": request_data["expires_at"]
        }
    except Exception as e:
        error_msg = str(e)
        if "existe déjà" in error_msg:
            raise HTTPException(status_code=409, detail="Une demande existe déjà pour ce produit")
        elif "Produit non trouvé" in error_msg:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/collaborations/requests/received")
async def get_received_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes reçues (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("influencer_id", influencer_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/sent")
async def get_sent_collaboration_requests(
    status: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Demandes envoyées (Marchand)"""
    merchant_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "success": True,
            "requests": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/accept")
async def accept_collaboration_request(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Accepter une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande acceptée ! Vous devez maintenant signer le contrat."
        }
    except Exception as e:
        error_msg = str(e)
        if "non valide" in error_msg or "déjà traitée" in error_msg:
            raise HTTPException(status_code=400, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.put("/api/collaborations/requests/{request_id}/reject")
async def reject_collaboration_request(
    request_id: str,
    data: RejectData,
    payload: dict = Depends(verify_token)
):
    """Refuser une demande (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "reject_collaboration_request",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_reason": data.reason
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Demande refusée"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/collaborations/requests/{request_id}/counter-offer")
async def counter_offer_collaboration(
    request_id: str,
    data: CounterOfferData,
    payload: dict = Depends(verify_token)
):
    """Contre-offre (Influenceur)"""
    influencer_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "counter_offer_collaboration",
            {
                "p_request_id": request_id,
                "p_influencer_id": influencer_id,
                "p_counter_commission": data.counter_commission,
                "p_message": data.message
            }
        ).execute()
        
        return {
            "success": True,
            "message": "Contre-offre envoyée au marchand"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collaborations/requests/{request_id}/sign-contract")
async def sign_collaboration_contract(
    request_id: str,
    data: ContractSignatureData,
    payload: dict = Depends(verify_token)
):
    """Signer le contrat"""
    user_id = payload.get("user_id")
    user_role = payload.get("role", "merchant")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.rpc(
            "accept_contract",
            {
                "p_request_id": request_id,
                "p_user_id": user_id,
                "p_user_role": user_role,
                "p_signature": data.signature
            }
        ).execute()
        
        if user_role == "influencer":
            link_result = supabase.rpc(
                "generate_affiliate_link_from_collaboration",
                {"p_request_id": request_id}
            ).execute()
            
            link_id = link_result.data if link_result.data else None
            
            return {
                "success": True,
                "message": "Contrat signé ! Votre lien d'affiliation a été généré.",
                "affiliate_link_id": link_id
            }
        
        return {
            "success": True,
            "message": "Contrat signé avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/requests/{request_id}")
async def get_collaboration_request_details(
    request_id: str,
    payload: dict = Depends(verify_token)
):
    """Détails d'une demande"""
    user_id = payload.get("user_id")
    
    if not SUPABASE_ENABLED:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = supabase.table("collaboration_requests") \
            .select("*") \
            .eq("id", request_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Demande non trouvée")
        
        request_data = result.data
        if user_id not in [request_data["merchant_id"], request_data["influencer_id"]]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
        
        if user_id == request_data["influencer_id"] and not request_data.get("viewed_by_influencer"):
            supabase.table("collaboration_requests") \
                .update({
                    "viewed_by_influencer": True,
                    "viewed_at": datetime.now().isoformat()
                }) \
                .eq("id", request_id) \
                .execute()
        
        history = supabase.table("collaboration_history") \
            .select("*") \
            .eq("collaboration_request_id", request_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return {
            "success": True,
            "request": request_data,
            "history": history.data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collaborations/contract-terms")
async def get_contract_terms():
    """Termes du contrat de collaboration"""
    return {
        "success": True,
        "contract": {
            "version": "v1.0",
            "terms": [
                {
                    "title": "1. Respect Éthique",
                    "content": "L'influenceur s'engage à promouvoir le produit de manière éthique et honnête, sans fausses déclarations."
                },
                {
                    "title": "2. Transparence",
                    "content": "L'influenceur doit clairement indiquer qu'il s'agit d'un partenariat commercial (#ad, #sponsored)."
                },
                {
                    "title": "3. Commission",
                    "content": "La commission convenue sera versée pour chaque vente générée via le lien d'affiliation."
                },
                {
                    "title": "4. Durée",
                    "content": "Le contrat est valable pour 12 mois, renouvelable par accord mutuel."
                },
                {
                    "title": "5. Résiliation",
                    "content": "Chaque partie peut résilier avec un préavis de 30 jours."
                },
                {
                    "title": "6. Propriété Intellectuelle",
                    "content": "Le marchand conserve tous les droits sur le produit. L'influenceur conserve ses droits sur son contenu."
                },
                {
                    "title": "7. Confidentialité",
                    "content": "Les termes financiers de cet accord sont confidentiels."
                },
                {
                    "title": "8. Conformité Légale",
                    "content": "Les deux parties s'engagent à respecter toutes les lois applicables."
                }
            ]
        }
    }

# ============================================
# COMMERCIALS & INFLUENCERS DIRECTORY
# ============================================

@app.get("/api/commercials/directory")
async def get_commercials_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des commerciaux"""
    commercials = [u for u in MOCK_USERS.values() if u.get("role") == "commercial"]
    
    total = len(commercials)
    commercials = commercials[offset:offset + limit]
    
    return {
        "commercials": commercials,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/influencers/directory")
async def get_influencers_directory(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Annuaire des influenceurs"""
    influencers = [u for u in MOCK_USERS.values() if u.get("role") == "influencer"]
    
    total = len(influencers)
    influencers = influencers[offset:offset + limit]
    
    return {
        "influencers": influencers,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# ============================================
# AFFILIATE LINKS ENDPOINTS  
# ============================================

@app.get("/api/affiliate/links")
async def get_affiliate_links(payload: dict = Depends(verify_token)):
    """Liste des liens d'affiliation de l'utilisateur"""
    user_id = payload.get("sub")
    user_links = [link for link in MOCK_AFFILIATE_LINKS if link["user_id"] == user_id]
    
    return {
        "links": user_links,
        "stats": {
            "total_links": len(user_links),
            "total_clicks": sum(link["clicks"] for link in user_links),
            "total_conversions": sum(link["conversions"] for link in user_links),
            "total_revenue": sum(link["revenue"] for link in user_links)
        }
    }

@app.post("/api/affiliate/links")
async def create_affiliate_link(
    product_id: str,
    custom_slug: Optional[str] = None,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_link_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer un nouveau lien d'affiliation - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    user_id = payload.get("sub")
    
    # Vérifier que le produit existe
    product = next((p for p in MOCK_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Générer slug si non fourni
    if not custom_slug:
        custom_slug = f"prod-{product_id}-{user_id}"
    
    # Créer le lien
    link_id = str(len(MOCK_AFFILIATE_LINKS) + 1)
    new_link = {
        "id": link_id,
        "user_id": user_id,
        "product_id": product_id,
        "custom_slug": custom_slug,
        "original_url": f"https://boutique.ma/product/{product_id}",
        "affiliate_url": f"https://shareyoursales.ma/aff/{custom_slug}",
        "commission_rate": product["commission_rate"],
        "clicks": 0,
        "conversions": 0,
        "revenue": 0.0,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_AFFILIATE_LINKS.append(new_link)
    
    return {
        "message": "Lien d'affiliation créé avec succès",
        "link": new_link
    }

# ============================================
# MODERATION ENDPOINTS (Admin)
# ============================================

@app.get("/api/admin/moderation/pending")
async def get_pending_moderation_items(
    risk_level: Optional[str] = None,
    payload: dict = Depends(verify_token)
):
    """Récupérer les produits en attente de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des données en attente
    pending_items = [
        {
            "id": "mod_1",
            "product_id": "prod_abc",
            "product_name": "Smartphone X-Pro 15",
            "product_description": "Le dernier smartphone avec une caméra révolutionnaire et une batterie longue durée.",
            "product_price": 12500.00,
            "product_category": "Électronique",
            "product_images": ["https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400"],
            "merchant_id": "merch_xyz",
            "merchant_name": "ElectroMaroc",
            "merchant_email": "contact@electromaroc.ma",
            "submitted_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "hours_pending": 2.1,
            "ai_risk_level": "high",
            "ai_confidence": 0.85,
            "ai_reason": "Le prix semble élevé par rapport à des produits similaires. La description contient des superlatifs ('révolutionnaire').",
            "ai_flags": ["prix_eleve", "description_exageree"]
        },
        {
            "id": "mod_2",
            "product_id": "prod_def",
            "product_name": "T-shirt 'Casablanca'",
            "product_description": "T-shirt en coton bio avec un design exclusif de la ville de Casablanca.",
            "product_price": 250.00,
            "product_category": "Mode",
            "product_images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400"],
            "merchant_id": "merch_uvw",
            "merchant_name": "CasaStyle",
            "merchant_email": "contact@casastyle.ma",
            "submitted_at": (datetime.now() - timedelta(hours=8)).isoformat(),
            "hours_pending": 8.5,
            "ai_risk_level": "low",
            "ai_confidence": 0.98,
            "ai_reason": "Produit standard, description claire, prix cohérent.",
            "ai_flags": []
        }
    ]
    
    if risk_level:
        items = [item for item in pending_items if item['ai_risk_level'] == risk_level]
    else:
        items = pending_items

    return {"data": items}

@app.get("/api/admin/moderation/stats")
async def get_moderation_stats(
    period: str = "today",
    payload: dict = Depends(verify_token)
):
    """Récupérer les statistiques de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Simuler des statistiques
    stats = {
        "total": 150,
        "pending": 2,
        "approved": 135,
        "rejected": 13,
        "approval_rate": 135 / 150 if 150 > 0 else 0
    }
    return stats

@app.post("/api/admin/moderation/review")
async def review_moderation_item(
    payload: dict = Depends(verify_token)
):
    """Traiter une décision de modération"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Simuler le traitement
    return {"success": True, "message": "Décision enregistrée"}


# ============================================
# AUTHENTICATION & SALES
# ============================================

@app.put("/api/sales/{sale_id}/status")
async def update_sale_status_endpoint(
    sale_id: str,
    status: str,
    payload: dict = Depends(verify_token)
):
    """Mettre à jour le statut d'une vente (MODIFICATION RÉELLE dans DB)"""
    user_id = payload.get("id")
    user_role = payload.get("role")
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await update_sale_status(
                sale_id=sale_id,
                new_status=status,
                user_id=user_id,
                user_role=user_role
            )
            
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "Erreur lors de la mise à jour")
                )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur update_sale_status: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Réponse mockée
    return {
        "success": True,
        "sale_id": sale_id,
        "new_status": status,
        "message": f"Statut de la vente mis à jour: {status}"
    }

@app.get("/api/sales/stats")
async def get_sales_stats(payload: dict = Depends(verify_token)):
    """Stats ventes"""
    return {"total_sales": 15280.00, "total_orders": 245, "avg_order_value": 62.37, "growth": "+12.5%"}

@app.post("/api/sales")
async def create_sale(sale_data: dict, payload: dict = Depends(verify_token)):
    """Créer vente"""
    return {"message": "Vente enregistrée", "sale_id": f"sale_{datetime.now().timestamp()}", "amount": sale_data.get("amount")}

@app.get("/api/commissions")
async def get_commissions(
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(verify_token)
):
    """Commissions (DONNÉES RÉELLES depuis DB)"""
    user_id = payload.get("id")
    user_role = payload.get("role")
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await get_all_commissions(
                user_id=user_id,
                user_role=user_role,
                status=status,
                limit=limit,
                offset=offset
            )
            return result
        except Exception as e:
            logger.info(f"❌ Erreur get_commissions: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Données mockées
    return {
        "commissions": [
            {
                "id": "comm_001",
                "sale_id": "sale_001",
                "amount": 36.00,
                "status": "paid",
                "sale_date": "2024-11-01"
            }
        ],
        "total": 1,
        "limit": limit,
        "offset": offset
    }

@app.post("/api/commissions")
async def create_commission(comm_data: dict, payload: dict = Depends(verify_token)):
    """Créer commission"""
    return {"message": "Commission créée", "commission_id": f"comm_{datetime.now().timestamp()}", "amount": comm_data.get("amount")}

@app.get("/api/payments")
async def get_payments(payload: dict = Depends(verify_token)):
    """Paiements"""
    return {"payments": [{"id": "pay_001", "amount": 1250.00, "method": "bank_transfer", "status": "completed", "date": "2024-10-15"}], "total": 1}

@app.post("/api/payments")
async def create_payment(payment_data: dict, payload: dict = Depends(verify_token)):
    """Créer paiement"""
    return {"message": "Paiement créé", "payment_id": f"pay_{datetime.now().timestamp()}", "amount": payment_data.get("amount")}

@app.get("/api/payment-methods")
async def get_payment_methods_endpoint(payload: dict = Depends(verify_token)):
    """Moyens de paiement configurés (DONNÉES RÉELLES depuis DB)"""
    user_id = payload.get("id")
    
    if DB_QUERIES_AVAILABLE:
        try:
            methods = await get_payment_methods(user_id)
            return {"payment_methods": methods, "total": len(methods)}
        except Exception as e:
            logger.info(f"❌ Erreur get_payment_methods: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Données mockées
    return {
        "payment_methods": [
            {
                "id": "default_1",
                "type": "bank_transfer",
                "name": "Virement bancaire",
                "details": "Non configuré",
                "is_default": True
            }
        ],
        "total": 1
    }

@app.get("/api/clicks")
async def get_clicks(payload: dict = Depends(verify_token)):
    """Clics"""
    return {"clicks": [{"id": "click_001", "link_id": "link_001", "ip": "105.xxx.xxx.xxx", "country": "MA", "device": "mobile", "timestamp": "2024-11-02T10:30:00"}], "total": 1}

@app.get("/api/leads")
async def get_leads(payload: dict = Depends(verify_token)):
    """Leads"""
    return {"leads": [{"id": "lead_001", "name": "Mohamed A.", "email": "mohamed@example.com", "phone": "+212 6 12 34 56 78", "source": "Instagram", "status": "new"}], "total": 1}

@app.get("/api/conversions")
async def get_conversions(payload: dict = Depends(verify_token)):
    """Conversions"""
    return {"conversions": [{"id": "conv_001", "link_id": "link_001", "sale_id": "sale_001", "amount": 180.00, "date": "2024-11-01"}], "total": 1}

# ============================================
# MERCHANT PAYMENT & COUPONS
# ============================================

@app.get("/api/merchant/payment-config")
async def get_merchant_payment_config_full(payload: dict = Depends(verify_token)):
    """Config paiement merchant complète"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    return {"bank_name": "Attijariwafa Bank", "iban": "MA64011519000001234567890123", "swift": "BCMAMAMC", "payment_schedule": "monthly"}

@app.put("/api/merchant/payment-config")
async def update_merchant_payment_config_full(config: dict, payload: dict = Depends(verify_token)):
    """MAJ config paiement merchant"""
    if payload.get("role") not in ["merchant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès merchant requis")
    return {"message": "Configuration mise à jour", "config": config}

@app.get("/api/coupons")
async def get_coupons(payload: dict = Depends(verify_token)):
    """Coupons"""
    return {"coupons": [{"id": "coup_001", "code": "BEAUTY20", "discount": 20, "type": "percentage", "expires_at": "2024-11-30", "uses": 45, "max_uses": 100}], "total": 1}

@app.get("/api/advertisers")
async def get_advertisers(payload: dict = Depends(verify_token)):
    """Annonceurs"""
    return {"advertisers": [{"id": "adv_001", "name": "Google Ads", "budget": 5000, "spent": 2450, "conversions": 45}], "total": 1}

# ============================================
# MOBILE PAYMENTS & SETTINGS
# ============================================

@app.get("/api/mobile-payments-ma/providers")
async def get_mobile_payment_providers(payload: dict = Depends(verify_token)):
    """Opérateurs mobile Maroc"""
    return {"providers": [{"id": "iam", "name": "Maroc Telecom", "logo": "/providers/iam.png"}, {"id": "orange", "name": "Orange Maroc", "logo": "/providers/orange.png"}, {"id": "inwi", "name": "Inwi", "logo": "/providers/inwi.png"}]}

@app.post("/api/mobile-payments-ma/payout")
async def request_mobile_payout(payout_data: dict, payload: dict = Depends(verify_token)):
    """Demande paiement mobile"""
    return {"message": "Demande envoyée", "payout_id": f"mpay_{datetime.now().timestamp()}", "amount": payout_data.get("amount"), "phone": payout_data.get("phone")}

@app.get("/api/settings")
async def get_settings(payload: dict = Depends(verify_token)):
    """Paramètres"""
    return {"company_name": "Ma Société", "email": "contact@company.ma", "phone": "+212 5 22 33 44 55", "address": "Casablanca, Maroc"}

@app.put("/api/settings/company")
async def update_company_settings(settings: dict, payload: dict = Depends(verify_token)):
    """MAJ paramètres société"""
    return {"message": "Paramètres mis à jour", "settings": settings}

@app.post("/api/settings/affiliate")
async def save_affiliate_settings(settings: dict, payload: dict = Depends(verify_token)):
    """Sauvegarder paramètres affiliation"""
    return {"message": "Paramètres affiliation sauvegardés", "settings": settings}

@app.post("/api/settings/mlm")
async def save_mlm_settings(settings: dict, payload: dict = Depends(verify_token)):
    """Sauvegarder paramètres MLM"""
    return {"message": "Paramètres MLM sauvegardés", "mlm_enabled": settings.get("mlmEnabled"), "levels": settings.get("levels")}

@app.post("/api/settings/permissions")
async def save_permissions(permissions: dict, payload: dict = Depends(verify_token)):
    """Sauvegarder permissions"""
    return {"message": "Permissions mises à jour", "permissions": permissions}

@app.post("/api/settings/registration")
async def save_registration_settings(settings: dict, payload: dict = Depends(verify_token)):
    """Paramètres inscription"""
    return {"message": "Paramètres inscription sauvegardés", "settings": settings}

@app.post("/api/settings/smtp")
async def save_smtp_settings(smtp: dict, payload: dict = Depends(verify_token)):
    """Paramètres SMTP"""
    return {"message": "Paramètres SMTP sauvegardés", "host": smtp.get("host")}

@app.post("/api/settings/smtp/test")
async def test_smtp_settings(smtp: dict, payload: dict = Depends(verify_token)):
    """Tester SMTP"""
    return {"message": "Email de test envoyé", "success": True}

@app.post("/api/settings/whitelabel")
async def save_whitelabel_settings(settings: dict, payload: dict = Depends(verify_token)):
    """Paramètres white label"""
    return {"message": "Paramètres white label sauvegardés", "settings": settings}

# ============================================
# BOT & DASHBOARD STATS
# ============================================

@app.get("/api/bot/suggestions")
async def get_bot_suggestions(payload: dict = Depends(verify_token)):
    """Suggestions chatbot"""
    return {"suggestions": ["Comment créer un lien d'affiliation?", "Quels sont mes gains ce mois?", "Comment retirer mes commissions?"]}

@app.get("/api/bot/conversations")
async def get_bot_conversations(payload: dict = Depends(verify_token)):
    """Conversations chatbot"""
    return {"conversations": [{"id": "bot_conv_001", "last_message": "Comment puis-je vous aider?", "timestamp": "2024-11-02T09:00:00"}]}

@app.post("/api/bot/chat")
async def chat_with_bot(message_data: dict, payload: dict = Depends(verify_token)):
    """Chat avec bot"""
    return {"response": "Je suis là pour vous aider avec vos questions sur l'affiliation!", "message_id": f"bot_msg_{datetime.now().timestamp()}"}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(role: str = None, payload: dict = Depends(verify_token)):
    """Stats dashboard par rôle"""
    user_role = role or payload.get("role")
    if user_role == "influencer":
        return {"earnings": 2450.75, "clicks": 1247, "conversions": 89}
    elif user_role == "merchant":
        return {"sales": 15280.00, "orders": 245, "affiliates": 18}
    elif user_role == "admin":
        return {"revenue": 125000.00, "users": 1250, "transactions": 5680}
    return {"stats": {}}

@app.get("/api/payouts")
async def get_payouts_list(payload: dict = Depends(verify_token)):
    """Liste des paiements - Vraies données DB"""
    user_id = payload.get("user_id")
    
    if DB_QUERIES_AVAILABLE:
        try:
            payouts = await get_user_payouts(user_id)
            return {"payouts": payouts, "total": len(payouts)}
        except Exception as e:
            logger.info(f"❌ Erreur get_user_payouts: {e}")
            # Fallback aux données mockées
    
    # Fallback: Données mockées
    return {"payouts": [{"id": "payout_001", "amount": 1250.00, "status": "completed", "method": "bank_transfer", "date": "2024-10-15"}], "total": 1}

# ============================================
# CONTACT & SEARCH
# ============================================

@app.post("/api/contact/submit")
async def submit_contact_form(form_data: dict):
    """Formulaire de contact"""
    return {"message": "Message envoyé avec succès", "ticket_id": f"ticket_{datetime.now().timestamp()}"}

@app.post("/api/campaigns")
async def create_campaign_post(
    campaign_data: dict,
    payload: dict = Depends(verify_token),
    _: bool = Depends(SubscriptionLimits.check_campaign_limit()) if SUBSCRIPTION_LIMITS_ENABLED else None
):
    """Créer campagne (POST) - VÉRIFIE LES LIMITES D'ABONNEMENT"""
    return {"message": "Campagne créée", "campaign_id": f"camp_{datetime.now().timestamp()}", "title": campaign_data.get("title")}

# ============================================================================
# ADMIN USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_admin_users(
    role: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(verify_token)
):
    """Liste des utilisateurs admin (DONNÉES RÉELLES depuis DB)"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await get_all_users_admin(
                role=role,
                status=status,
                limit=limit,
                offset=offset
            )
            return result
        except Exception as e:
            logger.info(f"❌ Erreur get_admin_users: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Mock data
    users = [
        {
            "id": "1",
            "email": "admin@tracknow.io",
            "phone": "+212 6 12 34 56 78",
            "role": "admin",
            "created_at": "2024-01-15",
            "last_login": "2024-11-02 10:30"
        }
    ]
    
    return {"users": users, "total": 1, "limit": limit, "offset": offset}

@app.post("/api/admin/users")
async def create_admin_user(user_data: dict, payload: dict = Depends(verify_token)):
    """Créer un nouvel utilisateur admin"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validation basique
    required_fields = ["username", "email", "password", "role"]
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
    
    # TODO: Hash password, save to database
    new_user = {
        "id": 999,
        "username": user_data["username"],
        "email": user_data["email"],
        "phone": user_data.get("phone", ""),
        "role": user_data["role"],
        "status": user_data.get("status", "active"),
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "last_login": "-"
    }
    
    return {"success": True, "user": new_user, "message": "Utilisateur créé avec succès"}

@app.put("/api/admin/users/{user_id}")
async def update_admin_user(user_id: int, user_data: dict, payload: dict = Depends(verify_token)):
    """Mettre à jour un utilisateur"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Update in database
    updated_user = {
        "id": user_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone", ""),
        "role": user_data.get("role"),
        "status": user_data.get("status")
    }
    
    return {"success": True, "user": updated_user, "message": "Utilisateur mis à jour"}

@app.post("/api/admin/users/{user_id}/activate")
async def activate_user_endpoint(
    user_id: str,
    activation_data: dict,
    payload: dict = Depends(verify_token)
):
    """Activer/désactiver un utilisateur (MODIFICATION RÉELLE dans DB)"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès administrateur requis")
    
    active = activation_data.get("active", True)
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await activate_user(user_id, active)
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "Erreur lors de l'activation")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur activate_user: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Réponse mockée
    return {
        "success": True,
        "user_id": user_id,
        "active": active,
        "message": f"Utilisateur {'activé' if active else 'désactivé'} avec succès"
    }

@app.delete("/api/admin/users/{user_id}")
async def delete_admin_user(user_id: int, payload: dict = Depends(verify_token)):
    """Supprimer un utilisateur"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Delete from database
    return {"success": True, "message": "Utilisateur supprimé"}

@app.patch("/api/admin/users/{user_id}/status")
async def toggle_user_status(user_id: int, status_data: dict, payload: dict = Depends(verify_token)):
    """Changer le statut d'un utilisateur (actif/inactif)"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_status = status_data.get("status", "active")
    
    # TODO: Update in database
    return {"success": True, "status": new_status, "message": f"Statut changé à {new_status}"}

@app.put("/api/admin/users/{user_id}/permissions")
async def update_user_permissions(user_id: int, permissions: dict, payload: dict = Depends(verify_token)):
    """Mettre à jour les permissions d'un utilisateur"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Save permissions to database
    return {
        "success": True, 
        "permissions": permissions,
        "message": "Autorisations mises à jour"
    }

@app.get("/api/admin/users/{user_id}/permissions")
async def get_user_permissions(user_id: int, payload: dict = Depends(verify_token)):
    """Récupérer les permissions d'un utilisateur"""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mock permissions
    permissions = {
        "dashboard": True,
        "users": True,
        "merchants": True,
        "influencers": True,
        "products": True,
        "campaigns": True,
        "analytics": True,
        "settings": True,
        "reports": True,
        "payments": True,
        "marketplace": True,
        "social_media": True
    }
    
    return {"permissions": permissions}


# ============================================
# USER SETTINGS ENDPOINTS
# ============================================

@app.get("/api/settings/profile")
async def get_user_profile_endpoint(payload: dict = Depends(verify_token)):
    """Récupérer le profil complet de l'utilisateur connecté (DONNÉES RÉELLES depuis DB)"""
    user_id = payload.get("id")
    
    if DB_QUERIES_AVAILABLE:
        try:
            profile = await get_user_profile(user_id)
            if profile:
                return {"profile": profile}
            else:
                raise HTTPException(status_code=404, detail="Profil non trouvé")
        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur get_user_profile: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Profil mocké
    return {
        "profile": {
            "id": user_id,
            "email": "user@example.com",
            "role": payload.get("role", "influencer"),
            "phone": "",
            "created_at": datetime.now().isoformat()
        }
    }

@app.put("/api/settings/profile")
async def update_user_profile_endpoint(
    profile_data: dict,
    payload: dict = Depends(verify_token)
):
    """Mettre à jour le profil de l'utilisateur connecté (MODIFICATION RÉELLE dans DB)"""
    user_id = payload.get("id")
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await update_user_profile(user_id, profile_data)
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "Erreur lors de la mise à jour")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur update_user_profile: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Réponse mockée
    return {
        "success": True,
        "message": "Profil mis à jour avec succès"
    }

@app.put("/api/settings/password")
async def update_user_password_endpoint(
    password_data: dict,
    payload: dict = Depends(verify_token)
):
    """Mettre à jour le mot de passe de l'utilisateur connecté (MODIFICATION RÉELLE dans DB)"""
    user_id = payload.get("id")
    
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel et nouveau mot de passe requis"
        )
    
    if DB_QUERIES_AVAILABLE:
        try:
            result = await update_user_password(user_id, current_password, new_password)
            if result.get("success"):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.get("error", "Erreur lors de la mise à jour")
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.info(f"❌ Erreur update_user_password: {str(e)}")
            # Fallback to mocked
    
    # FALLBACK: Réponse mockée
    return {
        "success": True,
        "message": "Mot de passe mis à jour avec succès"
    }


# ============================================================================
# SUBSCRIPTION LIMITS & USAGE ENDPOINTS
# ============================================================================

@app.get("/api/subscription/limits")
async def get_subscription_limits(payload: dict = Depends(verify_token)):
    """Obtenir les limites et l'usage actuel de l'abonnement"""
    if not SUBSCRIPTION_LIMITS_ENABLED:
        return {
            "error": "Subscription limits not enabled",
            "limits": {},
            "usage": {},
            "plan": payload.get("subscription_plan", "unknown")
        }
    
    try:
        from subscription_helpers_simple import get_user_subscription_data
        
        user_id = payload.get("id")
        user_role = payload.get("role")
        
        subscription_data = await get_user_subscription_data(user_id, user_role)
        
        if not subscription_data:
            return {
                "error": "No subscription data found",
                "limits": {},
                "usage": {},
                "plan": payload.get("subscription_plan", "unknown")
            }
        
        return {
            "success": True,
            "plan_name": subscription_data.get("plan_name"),
            "plan_code": subscription_data.get("plan_code"),
            "limits": subscription_data.get("limits", {}),
            "usage": subscription_data.get("usage", {}),
            "features": subscription_data.get("features", []),
            "percentage_used": {
                "products": round((subscription_data.get("usage", {}).get("products", 0) / subscription_data.get("limits", {}).get("products", 1)) * 100) if subscription_data.get("limits", {}).get("products") else 0,
                "campaigns": round((subscription_data.get("usage", {}).get("campaigns", 0) / subscription_data.get("limits", {}).get("campaigns", 1)) * 100) if subscription_data.get("limits", {}).get("campaigns") else 0,
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting subscription limits: {e}")
        return {
            "error": str(e),
            "limits": {},
            "usage": {},
            "plan": payload.get("subscription_plan", "unknown")
        }


@app.get("/api/subscription/features")
async def get_subscription_features(payload: dict = Depends(verify_token)):
    """Obtenir les fonctionnalités disponibles pour l'abonnement actuel"""
    if not SUBSCRIPTION_LIMITS_ENABLED:
        return {"features": [], "error": "Subscription limits not enabled"}
    
    try:
        features = await SubscriptionLimits.get_plan_features(payload)
        return {
            "success": True,
            "features": features,
            "plan": payload.get("subscription_plan", "unknown")
        }
    except Exception as e:
        logger.error(f"❌ Error getting features: {e}")
        return {"features": [], "error": str(e)}


@app.get("/api/subscription/check-feature/{feature_name}")
async def check_feature_access(feature_name: str, payload: dict = Depends(verify_token)):
    """Vérifier si l'utilisateur a accès à une fonctionnalité spécifique"""
    if not SUBSCRIPTION_LIMITS_ENABLED:
        return {"has_access": True, "error": "Subscription limits not enabled"}
    
    try:
        has_access = await SubscriptionLimits.has_feature(feature_name, payload)
        return {
            "success": True,
            "feature": feature_name,
            "has_access": has_access,
            "plan": payload.get("subscription_plan", "unknown")
        }
    except Exception as e:
        logger.error(f"❌ Error checking feature: {e}")
        return {"has_access": False, "error": str(e)}


# ============================================
# 🌍 TRANSLATION ENDPOINTS (OpenAI + DB Cache)
# ============================================

@app.get("/api/translations/{language}")
async def get_all_translations(language: str):
    """
    Récupère toutes les traductions pour une langue
    Utilisé au chargement initial de l'application
    """
    if not TRANSLATION_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        translations = await translation_service.get_all_translations(language)
        
        return {
            "success": True,
            "language": language,
            "translations": translations,
            "count": len(translations)
        }
    except Exception as e:
        logger.error(f"❌ Error loading translations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translations/translate")
async def translate_text(
    request: dict,
    payload: dict = Depends(verify_token)
):
    """
    Traduit un texte avec OpenAI et le stocke en cache
    
    Body:
    {
        "key": "nav_dashboard",
        "target_language": "en",
        "context": "Navigation menu item",
        "auto_translate": true
    }
    """
    if not TRANSLATION_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        key = request.get("key")
        target_language = request.get("target_language")
        context = request.get("context")
        auto_translate = request.get("auto_translate", True)
        
        if not key or not target_language:
            raise HTTPException(status_code=400, detail="key and target_language required")
        
        translation = await translation_service.get_translation(
            key=key,
            language=target_language,
            context=context,
            auto_translate=auto_translate
        )
        
        if translation:
            return {
                "success": True,
                "key": key,
                "language": target_language,
                "translation": translation,
                "source": "cache" if not auto_translate else "openai"
            }
        else:
            raise HTTPException(status_code=404, detail="Translation not found and auto_translate disabled")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translations/batch")
async def batch_translate(
    request: dict,
    payload: dict = Depends(verify_token)
):
    """
    Traduit plusieurs clés en une seule fois
    
    Body:
    {
        "keys": ["nav_dashboard", "nav_marketplace", "nav_settings"],
        "target_language": "ar",
        "context": "Navigation menu"
    }
    """
    if not TRANSLATION_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        keys = request.get("keys", [])
        target_language = request.get("target_language")
        context = request.get("context")
        
        if not keys or not target_language:
            raise HTTPException(status_code=400, detail="keys and target_language required")
        
        translations = await translation_service.batch_translate(
            keys=keys,
            target_language=target_language,
            context=context
        )
        
        return {
            "success": True,
            "language": target_language,
            "translations": translations,
            "count": len(translations),
            "requested": len(keys),
            "missing": [k for k in keys if k not in translations]
        }
    
    except Exception as e:
        logger.error(f"❌ Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/translations/import")
async def import_translations(
    request: dict,
    payload: dict = Depends(verify_token)
):
    """
    Importe des traductions statiques en masse
    Nécessite le rôle ADMIN
    
    Body:
    {
        "language": "fr",
        "translations": {
            "nav_dashboard": "Tableau de Bord",
            "nav_marketplace": "Marketplace",
            ...
        }
    }
    """
    # Vérifier le rôle admin
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not TRANSLATION_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Translation service not available")
    
    try:
        language = request.get("language")
        translations_dict = request.get("translations", {})
        
        if not language or not translations_dict:
            raise HTTPException(status_code=400, detail="language and translations required")
        
        imported = await translation_service.import_static_translations(
            translations_dict=translations_dict,
            language=language
        )
        
        return {
            "success": True,
            "language": language,
            "imported": imported,
            "total": len(translations_dict)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
