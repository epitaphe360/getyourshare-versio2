"""
Modèles Pydantic pour le Module d'Automation Média Multi-Plateformes
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# ENUMS
# ============================================

class PlatformType(str, Enum):
    """Types de plateformes sociales supportées"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"


class ContentStatus(str, Enum):
    """Statuts du contenu généré"""
    DRAFT = "draft"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


class PostStatus(str, Enum):
    """Statuts des publications planifiées"""
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToneVoice(str, Enum):
    """Tons de voix pour la génération de contenu"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    LUXURY = "luxury"
    PLAYFUL = "playful"
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    WITTY = "witty"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"


class ContentCategory(str, Enum):
    """Catégories de contenu"""
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    ENGAGEMENT = "engagement"
    STORY = "story"
    ANNOUNCEMENT = "announcement"
    BEHIND_SCENES = "behind_scenes"
    USER_GENERATED = "user_generated"
    TESTIMONIAL = "testimonial"


# ============================================
# PLATFORM CONNECTION MODELS
# ============================================

class PlatformConnectionBase(BaseModel):
    """Base pour les connexions de plateformes"""
    platform: PlatformType
    account_name: Optional[str] = None
    is_active: bool = True


class PlatformConnectionCreate(PlatformConnectionBase):
    """Création d'une connexion de plateforme"""
    access_token: str
    refresh_token: Optional[str] = None
    account_id: str
    token_expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class PlatformConnectionUpdate(BaseModel):
    """Mise à jour d'une connexion"""
    account_name: Optional[str] = None
    is_active: Optional[bool] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class PlatformConnection(PlatformConnectionBase):
    """Modèle complet de connexion"""
    id: int
    user_id: int
    account_id: str
    token_expires_at: Optional[datetime] = None
    connected_at: datetime
    last_used_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# TEMPLATE MODELS
# ============================================

class TemplateBase(BaseModel):
    """Base pour les templates"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    platform: PlatformType
    category: ContentCategory
    prompt_template: str = Field(..., min_length=10)
    tone: ToneVoice = ToneVoice.PROFESSIONAL
    max_length: Optional[int] = None
    include_hashtags: bool = True
    include_emojis: bool = True


class TemplateCreate(TemplateBase):
    """Création d'un template"""
    variables: Optional[List[str]] = []
    is_default: bool = False
    is_public: bool = False


class TemplateUpdate(BaseModel):
    """Mise à jour d'un template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    prompt_template: Optional[str] = Field(None, min_length=10)
    variables: Optional[List[str]] = None
    tone: Optional[ToneVoice] = None
    max_length: Optional[int] = None
    include_hashtags: Optional[bool] = None
    include_emojis: Optional[bool] = None
    is_public: Optional[bool] = None


class Template(TemplateBase):
    """Modèle complet de template"""
    id: int
    user_id: int
    variables: List[str] = []
    is_default: bool = False
    is_public: bool = False
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# CONTENT GENERATION MODELS
# ============================================

class ContentGenerationRequest(BaseModel):
    """Requête de génération de contenu"""
    platform: PlatformType
    prompt: str = Field(..., min_length=10)
    template_id: Optional[int] = None
    variables: Optional[Dict[str, str]] = {}
    tone: ToneVoice = ToneVoice.PROFESSIONAL
    include_hashtags: bool = True
    include_emojis: bool = True
    max_length: Optional[int] = None
    num_variants: int = Field(default=1, ge=1, le=5)
    ai_model: str = "gpt-4-turbo"

    @validator('num_variants')
    def validate_variants(cls, v):
        if v < 1 or v > 5:
            raise ValueError('num_variants must be between 1 and 5')
        return v


class BatchContentGenerationRequest(BaseModel):
    """Requête de génération batch multi-plateformes"""
    platforms: List[PlatformType] = Field(..., min_items=1)
    base_prompt: str = Field(..., min_length=10)
    variables: Optional[Dict[str, str]] = {}
    tone: ToneVoice = ToneVoice.PROFESSIONAL
    include_hashtags: bool = True
    include_emojis: bool = True
    num_variants: int = Field(default=1, ge=1, le=3)


class GeneratedContentBase(BaseModel):
    """Base pour le contenu généré"""
    platform: PlatformType
    generated_text: str
    generated_hashtags: List[str] = []
    media_urls: List[str] = []
    tone: ToneVoice


class GeneratedContentCreate(GeneratedContentBase):
    """Création de contenu généré"""
    prompt: str
    template_id: Optional[int] = None
    ai_model: str = "gpt-4-turbo"
    variables_used: Optional[Dict[str, str]] = {}
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    engagement_prediction: Optional[int] = Field(None, ge=0, le=100)


class GeneratedContentUpdate(BaseModel):
    """Mise à jour du contenu"""
    generated_text: Optional[str] = None
    generated_hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    status: Optional[ContentStatus] = None


class GeneratedContent(GeneratedContentBase):
    """Modèle complet de contenu généré"""
    id: int
    user_id: int
    template_id: Optional[int] = None
    prompt: str
    ai_model: str
    variables_used: Dict[str, str] = {}
    quality_score: Optional[int] = None
    engagement_prediction: Optional[int] = None
    status: ContentStatus = ContentStatus.DRAFT
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# SCHEDULING MODELS
# ============================================

class SchedulePostRequest(BaseModel):
    """Requête de planification de publication"""
    content_id: int
    platform_id: int
    scheduled_time: datetime
    auto_optimize_time: bool = False
    custom_text: Optional[str] = None
    custom_hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = {}

    @validator('scheduled_time')
    def validate_future_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('scheduled_time must be in the future')
        return v


class RescheduleRequest(BaseModel):
    """Requête de reprogrammation"""
    new_scheduled_time: datetime

    @validator('new_scheduled_time')
    def validate_future_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('new_scheduled_time must be in the future')
        return v


class ScheduledPostBase(BaseModel):
    """Base pour les publications planifiées"""
    platform: PlatformType
    scheduled_time: datetime
    post_text: str
    hashtags: List[str] = []
    media_urls: List[str] = []


class ScheduledPostUpdate(BaseModel):
    """Mise à jour d'une publication planifiée"""
    scheduled_time: Optional[datetime] = None
    post_text: Optional[str] = None
    hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    status: Optional[PostStatus] = None


class ScheduledPost(ScheduledPostBase):
    """Modèle complet de publication planifiée"""
    id: int
    user_id: int
    content_id: Optional[int] = None
    platform_id: int
    optimal_time_suggested: bool = False
    status: PostStatus = PostStatus.SCHEDULED
    published_at: Optional[datetime] = None
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarQuery(BaseModel):
    """Requête pour le calendrier éditorial"""
    start_date: datetime
    end_date: datetime
    platforms: Optional[List[PlatformType]] = None
    status: Optional[List[PostStatus]] = None


# ============================================
# ANALYTICS MODELS
# ============================================

class AnalyticsBase(BaseModel):
    """Base pour les analytics"""
    platform: PlatformType
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0
    reach: int = 0
    impressions: int = 0


class AnalyticsCreate(AnalyticsBase):
    """Création d'analytics"""
    scheduled_post_id: int
    platform_post_id: Optional[str] = None
    saves: int = 0
    video_views: int = 0


class Analytics(AnalyticsBase):
    """Modèle complet d'analytics"""
    id: int
    scheduled_post_id: int
    user_id: int
    platform_post_id: Optional[str] = None
    engagement_rate: Optional[float] = None
    saves: int = 0
    video_views: int = 0
    fetch_count: int = 0
    last_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlatformAnalytics(BaseModel):
    """Analytics agrégées par plateforme"""
    platform: PlatformType
    total_posts: int
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_clicks: int
    avg_engagement_rate: float
    best_posting_time: Optional[str] = None
    top_content: List[Dict[str, Any]] = []


class PerformanceReport(BaseModel):
    """Rapport de performance global"""
    start_date: datetime
    end_date: datetime
    total_posts: int
    total_engagement: int
    avg_engagement_rate: float
    platform_breakdown: List[PlatformAnalytics]
    best_performing_posts: List[Dict[str, Any]]
    recommendations: List[str] = []


class ContentRecommendations(BaseModel):
    """Recommandations de contenu basées sur l'IA"""
    user_id: int
    best_posting_times: Dict[str, List[str]]  # platform -> list of times
    trending_topics: List[str]
    suggested_hashtags: Dict[str, List[str]]  # platform -> hashtags
    content_ideas: List[str]
    tone_recommendations: Dict[str, str]  # platform -> recommended tone


# ============================================
# OAUTH MODELS
# ============================================

class OAuthInitRequest(BaseModel):
    """Requête d'initialisation OAuth"""
    platform: PlatformType
    redirect_uri: str


class OAuthInitResponse(BaseModel):
    """Réponse d'initialisation OAuth"""
    authorization_url: str
    state: str
    platform: PlatformType


class OAuthCallbackRequest(BaseModel):
    """Requête de callback OAuth"""
    platform: PlatformType
    code: str
    state: str


class OAuthCallbackResponse(BaseModel):
    """Réponse de callback OAuth"""
    success: bool
    platform_connection: Optional[PlatformConnection] = None
    error: Optional[str] = None


# ============================================
# PUBLISHING MODELS
# ============================================

class PublishRequest(BaseModel):
    """Requête de publication immédiate"""
    content_id: int
    platform_id: int
    custom_text: Optional[str] = None
    custom_hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None


class PublishResult(BaseModel):
    """Résultat d'une publication"""
    success: bool
    platform: PlatformType
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[str] = None
    error_message: Optional[str] = None
    published_at: Optional[datetime] = None


class PublishStatus(BaseModel):
    """Statut d'une publication"""
    scheduled_post_id: int
    status: PostStatus
    published_at: Optional[datetime] = None
    platform_post_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int


# ============================================
# UTILITY MODELS
# ============================================

class OptimalTimesQuery(BaseModel):
    """Requête pour obtenir les heures optimales"""
    platform: PlatformType
    start_date: datetime
    end_date: datetime
    timezone: str = "UTC"


class OptimalTimesResponse(BaseModel):
    """Réponse avec les heures optimales"""
    platform: PlatformType
    optimal_times: List[Dict[str, Any]]  # [{"time": "14:00", "score": 85, "day": "Monday"}]
    based_on_posts: int
    confidence_level: str  # "high", "medium", "low"


class HashtagSuggestions(BaseModel):
    """Suggestions de hashtags"""
    platform: PlatformType
    content: str
    suggested_hashtags: List[Dict[str, Any]]  # [{"tag": "#marketing", "relevance": 95, "volume": "high"}]
    trending_hashtags: List[str]


class MediaUploadRequest(BaseModel):
    """Requête d'upload de média"""
    file_url: Optional[str] = None
    file_base64: Optional[str] = None
    file_type: str  # "image", "video"
    platform: PlatformType


class MediaUploadResponse(BaseModel):
    """Réponse d'upload de média"""
    success: bool
    media_url: str
    media_id: Optional[str] = None
    platform: PlatformType
    error: Optional[str] = None


# ============================================
# ERROR MODELS
# ============================================

class MediaAutomationError(BaseModel):
    """Modèle d'erreur standardisé"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Erreur de validation"""
    field: str
    message: str
    value: Any


# ============================================
# STATISTICS MODELS
# ============================================

class UserStatistics(BaseModel):
    """Statistiques utilisateur"""
    user_id: int
    total_content_generated: int
    total_posts_published: int
    total_posts_scheduled: int
    connected_platforms: List[PlatformType]
    total_engagement: int
    avg_engagement_rate: float
    most_used_platform: Optional[PlatformType] = None
    most_successful_content_type: Optional[ContentCategory] = None
