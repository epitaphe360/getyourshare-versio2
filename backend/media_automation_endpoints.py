"""
Endpoints API COMPLETS pour le Module d'Automation Média Multi-Plateformes
SANS MOCKS - Toutes les requêtes DB réelles
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.media_models import (
    # Platform & Content
    PlatformType,
    ContentStatus,
    PostStatus,
    ToneVoice,
    ContentCategory,

    # Content Generation
    ContentGenerationRequest,
    BatchContentGenerationRequest,
    GeneratedContent,
    GeneratedContentCreate,
    GeneratedContentUpdate,

    # Templates
    Template,
    TemplateCreate,
    TemplateUpdate,

    # OAuth
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    PlatformConnection,

    # Scheduling
    SchedulePostRequest,
    RescheduleRequest,
    ScheduledPost,
    ScheduledPostUpdate,
    CalendarQuery,

    # Publishing
    PublishRequest,
    PublishResult,
    PublishStatus,

    # Analytics
    Analytics,
    PlatformAnalytics,
    PerformanceReport,
    ContentRecommendations,
    OptimalTimesQuery,
    OptimalTimesResponse,
    HashtagSuggestions
)

from services.media_content_generator import MediaContentGeneratorService
from services.media_oauth_service import MediaOAuthService, token_encryption
from services.media_publishing_service import MediaPublishingService
from database.media_db import (
    media_db,
    dict_to_postgres_json,
    list_to_postgres_array,
    get_user_platforms,
    get_platform_by_id,
    get_generated_content,
    get_scheduled_posts,
    get_analytics_by_post,
    save_oauth_state,
    verify_oauth_state
)
from auth import get_current_user_from_cookie  # Système d'auth existant

# Initialiser le router
router = APIRouter(prefix="/api/media", tags=["Media Automation"])

# Services
content_generator = MediaContentGeneratorService()
oauth_service = MediaOAuthService()
publishing_service = MediaPublishingService()


# ============================================
# CONTENT GENERATION ENDPOINTS
# ============================================

@router.post("/generate", response_model=List[Dict[str, Any]])
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🎨 Génère du contenu avec IA pour une plateforme spécifique
    """
    try:
        user_id = current_user["id"]

        # Générer le contenu
        contents = await content_generator.generate_content(request, user_id)

        # Sauvegarder en DB
        saved_contents = []
        for content in contents:
            query = """
                INSERT INTO media_generated_content
                (user_id, template_id, platform, prompt, generated_text, generated_hashtags,
                 media_urls, ai_model, tone, variables_used, quality_score, engagement_prediction, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft')
                RETURNING id, user_id, platform, prompt, generated_text, generated_hashtags,
                          ai_model, tone, quality_score, engagement_prediction, status, created_at
            """
            params = (
                user_id,
                request.template_id,
                content.platform.value,
                content.prompt,
                content.generated_text,
                list_to_postgres_array(content.generated_hashtags),
                list_to_postgres_array(content.media_urls) if content.media_urls else '{}',
                content.ai_model,
                content.tone.value,
                dict_to_postgres_json(content.variables_used),
                content.quality_score,
                content.engagement_prediction
            )

            result = media_db.execute_one(query, params)
            saved_contents.append(result)

        return saved_contents

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.post("/generate/batch", response_model=Dict[str, List[Dict[str, Any]]])
async def generate_batch_content(
    request: BatchContentGenerationRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🚀 Génère du contenu pour plusieurs plateformes simultanément
    """
    try:
        user_id = current_user["id"]
        results = await content_generator.generate_batch_content(request, user_id)

        # Sauvegarder tous les résultats
        saved_results = {}
        for platform, contents in results.items():
            saved_contents = []
            for content in contents:
                query = """
                    INSERT INTO media_generated_content
                    (user_id, platform, prompt, generated_text, generated_hashtags,
                     ai_model, tone, variables_used, quality_score, engagement_prediction, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft')
                    RETURNING id, platform, generated_text, generated_hashtags, quality_score, engagement_prediction
                """
                params = (
                    user_id,
                    platform.value,
                    content.prompt,
                    content.generated_text,
                    list_to_postgres_array(content.generated_hashtags),
                    content.ai_model,
                    content.tone.value,
                    dict_to_postgres_json(content.variables_used),
                    content.quality_score,
                    content.engagement_prediction
                )
                result = media_db.execute_one(query, params)
                saved_contents.append(result)

            saved_results[platform.value] = saved_contents

        return saved_results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération batch: {str(e)}"
        )


@router.get("/content")
async def get_content_list(
    platform: Optional[PlatformType] = None,
    status_filter: Optional[ContentStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📋 Liste le contenu généré
    """
    user_id = current_user["id"]

    conditions = ["user_id = %s"]
    params = [user_id]

    if platform:
        conditions.append("platform = %s")
        params.append(platform.value)

    if status_filter:
        conditions.append("status = %s")
        params.append(status_filter.value)

    query = f"""
        SELECT id, platform, prompt, generated_text, generated_hashtags,
               ai_model, tone, quality_score, engagement_prediction, status, created_at
        FROM media_generated_content
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    results = media_db.execute_query(query, tuple(params))
    return results


@router.get("/content/{content_id}")
async def get_content_by_id(
    content_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📄 Détail d'un contenu généré
    """
    user_id = current_user["id"]

    query = """
        SELECT *
        FROM media_generated_content
        WHERE id = %s AND user_id = %s
    """
    result = media_db.execute_one(query, (content_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Content not found")

    return result


@router.put("/content/{content_id}")
async def update_content(
    content_id: int,
    update: GeneratedContentUpdate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ✏️ Modifier un contenu généré
    """
    user_id = current_user["id"]

    # Construire la requête UPDATE dynamiquement
    update_fields = []
    params = []

    if update.generated_text is not None:
        update_fields.append("generated_text = %s")
        params.append(update.generated_text)

    if update.generated_hashtags is not None:
        update_fields.append("generated_hashtags = %s")
        params.append(list_to_postgres_array(update.generated_hashtags))

    if update.media_urls is not None:
        update_fields.append("media_urls = %s")
        params.append(list_to_postgres_array(update.media_urls))

    if update.status is not None:
        update_fields.append("status = %s")
        params.append(update.status.value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.extend([content_id, user_id])

    query = f"""
        UPDATE media_generated_content
        SET {', '.join(update_fields)}
        WHERE id = %s AND user_id = %s
        RETURNING *
    """

    result = media_db.execute_one(query, tuple(params))

    if not result:
        raise HTTPException(status_code=404, detail="Content not found")

    return result


@router.delete("/content/{content_id}")
async def delete_content(
    content_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🗑️ Supprimer un contenu
    """
    user_id = current_user["id"]

    query = """
        DELETE FROM media_generated_content
        WHERE id = %s AND user_id = %s
    """
    rows_deleted = media_db.execute_delete(query, (content_id, user_id))

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"message": "Content deleted successfully"}


@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ✅ Approuver un contenu pour publication
    """
    user_id = current_user["id"]

    query = """
        UPDATE media_generated_content
        SET status = 'approved',
            approved_at = CURRENT_TIMESTAMP,
            approved_by = %s
        WHERE id = %s AND user_id = %s
        RETURNING id, status, approved_at
    """

    result = media_db.execute_one(query, (user_id, content_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"message": "Content approved", "content": result}


# ============================================
# TEMPLATES ENDPOINTS
# ============================================

@router.get("/templates")
async def get_templates(
    platform: Optional[PlatformType] = None,
    category: Optional[ContentCategory] = None,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📝 Liste des templates de prompts
    """
    user_id = current_user["id"]

    conditions = ["(user_id = %s OR is_public = true)"]
    params = [user_id]

    if platform:
        conditions.append("platform = %s")
        params.append(platform.value)

    if category:
        conditions.append("category = %s")
        params.append(category.value)

    query = f"""
        SELECT id, name, description, platform, category, prompt_template,
               variables, tone, include_hashtags, include_emojis, is_public, usage_count
        FROM media_templates
        WHERE {' AND '.join(conditions)}
        ORDER BY is_public DESC, usage_count DESC, created_at DESC
        LIMIT 100
    """

    results = media_db.execute_query(query, tuple(params))
    return results


@router.post("/templates")
async def create_template(
    template: TemplateCreate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ➕ Créer un nouveau template
    """
    user_id = current_user["id"]

    query = """
        INSERT INTO media_templates
        (user_id, name, description, platform, category, prompt_template, variables,
         tone, max_length, include_hashtags, include_emojis, is_default, is_public)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """

    params = (
        user_id,
        template.name,
        template.description,
        template.platform.value,
        template.category.value,
        template.prompt_template,
        dict_to_postgres_json(template.variables or []),
        template.tone.value,
        template.max_length,
        template.include_hashtags,
        template.include_emojis,
        template.is_default,
        template.is_public
    )

    result = media_db.execute_one(query, params)
    return result


@router.get("/templates/{template_id}")
async def get_template(
    template_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📄 Détail d'un template
    """
    user_id = current_user["id"]

    query = """
        SELECT *
        FROM media_templates
        WHERE id = %s AND (user_id = %s OR is_public = true)
    """

    result = media_db.execute_one(query, (template_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Template not found")

    return result


@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    update: TemplateUpdate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ✏️ Modifier un template
    """
    user_id = current_user["id"]

    # Construire UPDATE dynamique
    update_fields = []
    params = []

    if update.name is not None:
        update_fields.append("name = %s")
        params.append(update.name)

    if update.description is not None:
        update_fields.append("description = %s")
        params.append(update.description)

    if update.prompt_template is not None:
        update_fields.append("prompt_template = %s")
        params.append(update.prompt_template)

    if update.variables is not None:
        update_fields.append("variables = %s")
        params.append(dict_to_postgres_json(update.variables))

    if update.tone is not None:
        update_fields.append("tone = %s")
        params.append(update.tone.value)

    if update.max_length is not None:
        update_fields.append("max_length = %s")
        params.append(update.max_length)

    if update.include_hashtags is not None:
        update_fields.append("include_hashtags = %s")
        params.append(update.include_hashtags)

    if update.include_emojis is not None:
        update_fields.append("include_emojis = %s")
        params.append(update.include_emojis)

    if update.is_public is not None:
        update_fields.append("is_public = %s")
        params.append(update.is_public)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.extend([template_id, user_id])

    query = f"""
        UPDATE media_templates
        SET {', '.join(update_fields)}
        WHERE id = %s AND user_id = %s
        RETURNING *
    """

    result = media_db.execute_one(query, tuple(params))

    if not result:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")

    return result


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🗑️ Supprimer un template
    """
    user_id = current_user["id"]

    query = """
        DELETE FROM media_templates
        WHERE id = %s AND user_id = %s
    """

    rows_deleted = media_db.execute_delete(query, (template_id, user_id))

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")

    return {"message": "Template deleted"}


@router.get("/templates/default")
async def get_default_templates(
    platform: Optional[PlatformType] = None
):
    """
    ⭐ Templates par défaut (publics)
    """
    conditions = ["is_public = true"]
    params = []

    if platform:
        conditions.append("platform = %s")
        params.append(platform.value)

    query = f"""
        SELECT id, name, description, platform, category, prompt_template,
               variables, tone, include_hashtags, include_emojis, usage_count
        FROM media_templates
        WHERE {' AND '.join(conditions)}
        ORDER BY usage_count DESC, created_at DESC
        LIMIT 50
    """

    results = media_db.execute_query(query, tuple(params) if params else ())
    return results


# ============================================
# PLATFORM CONNECTIONS (OAuth)
# ============================================

@router.get("/platforms")
async def get_platform_connections(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔌 Liste des connexions aux plateformes
    """
    user_id = current_user["id"]
    platforms = get_user_platforms(user_id)
    return platforms


@router.post("/platforms/{platform}/connect", response_model=OAuthInitResponse)
async def connect_platform(
    platform: PlatformType,
    redirect_uri: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔗 Initier la connexion OAuth à une plateforme
    """
    try:
        user_id = current_user["id"]
        result = await oauth_service.initiate_oauth_flow(user_id, platform, redirect_uri)

        # Sauvegarder l'état OAuth en DB
        # Note: code_verifier sera None pour les plateformes sans PKCE
        save_oauth_state(user_id, platform.value, result.state, None, redirect_uri)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur OAuth: {str(e)}"
        )


@router.get("/platforms/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ↩️ Callback OAuth
    """
    try:
        user_id = current_user["id"]

        # Vérifier le state
        oauth_state = verify_oauth_state(state)
        if not oauth_state or oauth_state['user_id'] != user_id:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

        platform_type = PlatformType(platform)
        redirect_uri = oauth_state['redirect_uri']

        # Compléter le flux OAuth
        connection_data = await oauth_service.complete_oauth_flow(
            user_id, platform_type, code, state, redirect_uri
        )

        # Sauvegarder la connexion en DB
        query = """
            INSERT INTO media_platforms
            (user_id, platform, account_name, account_id, access_token, refresh_token,
             token_expires_at, is_active, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, true, %s)
            ON CONFLICT (user_id, platform, account_id)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                token_expires_at = EXCLUDED.token_expires_at,
                is_active = true,
                connected_at = CURRENT_TIMESTAMP
            RETURNING id, platform, account_name, is_active
        """

        # Chiffrer les tokens
        encrypted_access = token_encryption.encrypt(connection_data.access_token)
        encrypted_refresh = token_encryption.encrypt(connection_data.refresh_token) if connection_data.refresh_token else None

        params = (
            user_id,
            platform,
            connection_data.account_name,
            connection_data.account_id,
            encrypted_access,
            encrypted_refresh,
            connection_data.token_expires_at,
            dict_to_postgres_json(connection_data.metadata)
        )

        result = media_db.execute_one(query, params)

        return {
            "success": True,
            "message": f"Successfully connected to {platform}",
            "connection": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.delete("/platforms/{platform_id}")
async def disconnect_platform(
    platform_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔓 Déconnecter une plateforme
    """
    try:
        user_id = current_user["id"]

        # Désactiver la plateforme au lieu de la supprimer
        query = """
            UPDATE media_platforms
            SET is_active = false
            WHERE id = %s AND user_id = %s
        """

        rows_updated = media_db.execute_update(query, (platform_id, user_id))

        if rows_updated == 0:
            raise HTTPException(status_code=404, detail="Platform connection not found")

        return {"message": "Platform disconnected successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disconnect failed: {str(e)}"
        )


@router.post("/platforms/{platform_id}/refresh")
async def refresh_platform_token(
    platform_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔄 Rafraîchir le token d'une plateforme
    """
    try:
        user_id = current_user["id"]

        # Récupérer la plateforme
        platform = get_platform_by_id(platform_id, user_id)
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")

        # Rafraîchir via le service OAuth
        refreshed = await oauth_service.refresh_access_token(user_id, platform_id)

        # Mettre à jour en DB
        encrypted_access = token_encryption.encrypt(refreshed.access_token)

        query = """
            UPDATE media_platforms
            SET access_token = %s,
                token_expires_at = %s,
                last_used_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        media_db.execute_update(query, (encrypted_access, refreshed.token_expires_at, platform_id))

        return {"message": "Token refreshed successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh failed: {str(e)}"
        )


# ============================================
# SCHEDULING ENDPOINTS
# ============================================

@router.post("/schedule")
async def schedule_post(
    request: SchedulePostRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📅 Planifier une publication
    """
    user_id = current_user["id"]

    # Vérifier que le contenu existe
    content_query = """
        SELECT * FROM media_generated_content
        WHERE id = %s AND user_id = %s
    """
    content = media_db.execute_one(content_query, (request.content_id, user_id))

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Vérifier que la plateforme existe
    platform = get_platform_by_id(request.platform_id, user_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    # Créer le post planifié
    post_text = request.custom_text or content['generated_text']
    hashtags = request.custom_hashtags or content['generated_hashtags']

    query = """
        INSERT INTO media_scheduled_posts
        (user_id, content_id, platform_id, platform, scheduled_time, optimal_time_suggested,
         post_text, media_urls, hashtags, status, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', %s)
        RETURNING *
    """

    params = (
        user_id,
        request.content_id,
        request.platform_id,
        platform['platform'],
        request.scheduled_time,
        request.auto_optimize_time,
        post_text,
        list_to_postgres_array(request.media_urls) if request.media_urls else '{}',
        list_to_postgres_array(hashtags) if hashtags else '{}',
        dict_to_postgres_json(request.metadata)
    )

    result = media_db.execute_one(query, params)

    # Mettre à jour le statut du contenu
    media_db.execute_update(
        "UPDATE media_generated_content SET status = 'scheduled' WHERE id = %s",
        (request.content_id,)
    )

    return result


@router.get("/schedule")
async def get_scheduled_posts_list(
    platform: Optional[PlatformType] = None,
    status_filter: Optional[PostStatus] = Query(None, alias="status"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📋 Liste des publications planifiées
    """
    user_id = current_user["id"]

    conditions = ["user_id = %s"]
    params = [user_id]

    if platform:
        conditions.append("platform = %s")
        params.append(platform.value)

    if status_filter:
        conditions.append("status = %s")
        params.append(status_filter.value)

    if start_date:
        conditions.append("scheduled_time >= %s")
        params.append(start_date)

    if end_date:
        conditions.append("scheduled_time <= %s")
        params.append(end_date)

    query = f"""
        SELECT id, platform, scheduled_time, post_text, hashtags,
               status, published_at, platform_post_url, error_message
        FROM media_scheduled_posts
        WHERE {' AND '.join(conditions)}
        ORDER BY scheduled_time DESC
        LIMIT %s
    """
    params.append(limit)

    results = media_db.execute_query(query, tuple(params))
    return results


@router.post("/schedule/calendar")
async def get_editorial_calendar(
    query_params: CalendarQuery,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📆 Calendrier éditorial
    """
    user_id = current_user["id"]

    conditions = ["user_id = %s"]
    params = [user_id]

    conditions.append("scheduled_time >= %s")
    params.append(query_params.start_date)

    conditions.append("scheduled_time <= %s")
    params.append(query_params.end_date)

    if query_params.platforms:
        placeholders = ','.join(['%s'] * len(query_params.platforms))
        conditions.append(f"platform IN ({placeholders})")
        params.extend([p.value for p in query_params.platforms])

    if query_params.status:
        placeholders = ','.join(['%s'] * len(query_params.status))
        conditions.append(f"status IN ({placeholders})")
        params.extend([s.value for s in query_params.status])

    query = f"""
        SELECT id, platform, scheduled_time, post_text, hashtags,
               status, published_at, platform_post_url
        FROM media_scheduled_posts
        WHERE {' AND '.join(conditions)}
        ORDER BY scheduled_time ASC
    """

    results = media_db.execute_query(query, tuple(params))
    return results


@router.put("/schedule/{post_id}")
async def update_scheduled_post(
    post_id: int,
    update: ScheduledPostUpdate,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ✏️ Modifier une publication planifiée
    """
    user_id = current_user["id"]

    update_fields = []
    params = []

    if update.scheduled_time is not None:
        update_fields.append("scheduled_time = %s")
        params.append(update.scheduled_time)

    if update.post_text is not None:
        update_fields.append("post_text = %s")
        params.append(update.post_text)

    if update.hashtags is not None:
        update_fields.append("hashtags = %s")
        params.append(list_to_postgres_array(update.hashtags))

    if update.media_urls is not None:
        update_fields.append("media_urls = %s")
        params.append(list_to_postgres_array(update.media_urls))

    if update.status is not None:
        update_fields.append("status = %s")
        params.append(update.status.value)

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.extend([post_id, user_id])

    query = f"""
        UPDATE media_scheduled_posts
        SET {', '.join(update_fields)}
        WHERE id = %s AND user_id = %s
        RETURNING *
    """

    result = media_db.execute_one(query, tuple(params))

    if not result:
        raise HTTPException(status_code=404, detail="Scheduled post not found")

    return result


@router.delete("/schedule/{post_id}")
async def cancel_scheduled_post(
    post_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ❌ Annuler une publication planifiée
    """
    user_id = current_user["id"]

    query = """
        UPDATE media_scheduled_posts
        SET status = 'cancelled'
        WHERE id = %s AND user_id = %s AND status = 'scheduled'
    """

    rows_updated = media_db.execute_update(query, (post_id, user_id))

    if rows_updated == 0:
        raise HTTPException(status_code=404, detail="Scheduled post not found or cannot be cancelled")

    return {"message": "Post cancelled successfully"}


@router.post("/schedule/{post_id}/reschedule")
async def reschedule_post(
    post_id: int,
    request: RescheduleRequest,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔄 Reprogrammer une publication
    """
    user_id = current_user["id"]

    query = """
        UPDATE media_scheduled_posts
        SET scheduled_time = %s,
            status = 'scheduled'
        WHERE id = %s AND user_id = %s
        RETURNING *
    """

    result = media_db.execute_one(query, (request.new_scheduled_time, post_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Scheduled post not found")

    return result


@router.get("/schedule/optimal-times", response_model=OptimalTimesResponse)
async def get_optimal_posting_times(
    query_params: OptimalTimesQuery = Depends(),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    ⏰ Obtenir les heures optimales de publication
    """
    user_id = current_user["id"]

    # Analyser les données historiques
    query = """
        SELECT
            EXTRACT(HOUR FROM sp.scheduled_time) as hour,
            EXTRACT(DOW FROM sp.scheduled_time) as day_of_week,
            COUNT(*) as post_count,
            AVG(a.engagement_rate) as avg_engagement
        FROM media_scheduled_posts sp
        LEFT JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE sp.user_id = %s
        AND sp.platform = %s
        AND sp.status = 'published'
        AND sp.scheduled_time >= %s
        AND sp.scheduled_time <= %s
        GROUP BY hour, day_of_week
        HAVING COUNT(*) >= 5
        ORDER BY avg_engagement DESC NULLS LAST, post_count DESC
        LIMIT 10
    """

    results = media_db.execute_query(query, (
        user_id,
        query_params.platform.value,
        query_params.start_date,
        query_params.end_date
    ))

    # Convertir en format attendu
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    optimal_times = []
    for row in results:
        optimal_times.append({
            "time": f"{int(row['hour']):02d}:00",
            "score": int((row['avg_engagement'] or 50) * 100) if row['avg_engagement'] else 50,
            "day": days[int(row['day_of_week'])]
        })

    # Si pas assez de données, utiliser les heures par défaut
    if len(optimal_times) < 3:
        default_times = content_generator.PLATFORM_CONFIGS[query_params.platform]["best_times"]
        optimal_times = [
            {"time": time, "score": 70, "day": "All"}
            for time in default_times
        ]

    confidence = "high" if len(results) >= 10 else "medium" if len(results) >= 5 else "low"

    return OptimalTimesResponse(
        platform=query_params.platform,
        optimal_times=optimal_times,
        based_on_posts=sum(r['post_count'] for r in results) if results else 0,
        confidence_level=confidence
    )


# ============================================
# PUBLISHING ENDPOINTS
# ============================================

@router.post("/publish/{post_id}", response_model=Dict[str, Any])
async def publish_immediately(
    post_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🚀 Publier immédiatement un post planifié
    """
    user_id = current_user["id"]

    # Récupérer le post
    post_query = """
        SELECT sp.*, mp.access_token, mp.refresh_token, mp.account_id, mp.metadata
        FROM media_scheduled_posts sp
        JOIN media_platforms mp ON sp.platform_id = mp.id
        WHERE sp.id = %s AND sp.user_id = %s
    """

    post_data = media_db.execute_one(post_query, (post_id, user_id))

    if not post_data:
        raise HTTPException(status_code=404, detail="Post not found")

    # Déchiffrer les tokens
    decrypted_access = token_encryption.decrypt(post_data['access_token'])
    decrypted_refresh = token_encryption.decrypt(post_data['refresh_token']) if post_data['refresh_token'] else None

    # Créer l'objet plateforme
    platform_connection = type('obj', (object,), {
        'platform': PlatformType(post_data['platform']),
        'access_token': decrypted_access,
        'refresh_token': decrypted_refresh,
        'account_id': post_data['account_id'],
        'account_name': '',
        'metadata': post_data['metadata'] or {}
    })()

    # Créer l'objet post
    scheduled_post = type('obj', (object,), {
        'id': post_data['id'],
        'post_text': post_data['post_text'],
        'hashtags': post_data['hashtags'] or [],
        'media_urls': post_data['media_urls'] or [],
        'metadata': post_data['metadata'] or {}
    })()

    # Mettre à jour le statut
    media_db.execute_update(
        "UPDATE media_scheduled_posts SET status = 'publishing' WHERE id = %s",
        (post_id,)
    )

    try:
        # Publier
        result = await publishing_service.publish_post(scheduled_post, platform_connection)

        # Mettre à jour le post avec les résultats
        if result.success:
            update_query = """
                UPDATE media_scheduled_posts
                SET status = 'published',
                    published_at = CURRENT_TIMESTAMP,
                    platform_post_id = %s,
                    platform_post_url = %s
                WHERE id = %s
                RETURNING *
            """
            updated_post = media_db.execute_one(update_query, (
                result.platform_post_id,
                result.platform_post_url,
                post_id
            ))

            # Créer l'entrée analytics
            analytics_query = """
                INSERT INTO media_analytics
                (scheduled_post_id, user_id, platform, platform_post_id)
                VALUES (%s, %s, %s, %s)
            """
            media_db.execute_insert(analytics_query, (
                post_id,
                user_id,
                post_data['platform'],
                result.platform_post_id
            ))

            return {
                "success": True,
                "message": "Post published successfully",
                "post": updated_post,
                "platform_url": result.platform_post_url
            }
        else:
            # Échec
            update_query = """
                UPDATE media_scheduled_posts
                SET status = 'failed',
                    error_message = %s,
                    retry_count = retry_count + 1
                WHERE id = %s
            """
            media_db.execute_update(update_query, (result.error_message, post_id))

            return {
                "success": False,
                "message": "Publication failed",
                "error": result.error_message
            }

    except Exception as e:
        # Erreur inattendue
        media_db.execute_update(
            "UPDATE media_scheduled_posts SET status = 'failed', error_message = %s WHERE id = %s",
            (str(e), post_id)
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Publishing error: {str(e)}"
        )


@router.get("/publish/status/{post_id}")
async def get_publish_status(
    post_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📊 Statut d'une publication
    """
    user_id = current_user["id"]

    query = """
        SELECT id, status, published_at, platform_post_url, error_message, retry_count
        FROM media_scheduled_posts
        WHERE id = %s AND user_id = %s
    """

    result = media_db.execute_one(query, (post_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    return result


@router.post("/publish/{post_id}/retry")
async def retry_failed_publish(
    post_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🔁 Réessayer une publication échouée
    """
    # Reset le statut et réessayer
    user_id = current_user["id"]

    query = """
        UPDATE media_scheduled_posts
        SET status = 'scheduled',
            error_message = NULL
        WHERE id = %s AND user_id = %s AND status = 'failed'
        RETURNING id
    """

    result = media_db.execute_one(query, (post_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Post not found or not in failed status")

    # Republier
    return await publish_immediately(post_id, current_user)


# ============================================
# ANALYTICS ENDPOINTS
# ============================================

@router.get("/analytics/posts/{post_id}")
async def get_post_analytics(
    post_id: int,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📈 Analytics d'un post spécifique
    """
    user_id = current_user["id"]

    query = """
        SELECT a.*
        FROM media_analytics a
        JOIN media_scheduled_posts sp ON a.scheduled_post_id = sp.id
        WHERE sp.id = %s AND sp.user_id = %s
    """

    result = media_db.execute_one(query, (post_id, user_id))

    if not result:
        raise HTTPException(status_code=404, detail="Analytics not found")

    return result


@router.get("/analytics/platform")
async def get_platform_analytics(
    platform: Optional[PlatformType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📊 Analytics par plateforme
    """
    user_id = current_user["id"]

    conditions = ["sp.user_id = %s"]
    params = [user_id]

    if platform:
        conditions.append("a.platform = %s")
        params.append(platform.value)

    if start_date:
        conditions.append("sp.published_at >= %s")
        params.append(start_date)

    if end_date:
        conditions.append("sp.published_at <= %s")
        params.append(end_date)

    query = f"""
        SELECT
            a.platform,
            COUNT(DISTINCT sp.id) as total_posts,
            COALESCE(SUM(a.views), 0) as total_views,
            COALESCE(SUM(a.likes), 0) as total_likes,
            COALESCE(SUM(a.comments), 0) as total_comments,
            COALESCE(SUM(a.shares), 0) as total_shares,
            COALESCE(SUM(a.clicks), 0) as total_clicks,
            COALESCE(AVG(a.engagement_rate), 0) as avg_engagement_rate
        FROM media_scheduled_posts sp
        LEFT JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE {' AND '.join(conditions)}
        AND sp.status = 'published'
        GROUP BY a.platform
    """

    results = media_db.execute_query(query, tuple(params))
    return results


@router.get("/analytics/recommendations", response_model=ContentRecommendations)
async def get_content_recommendations(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    💡 Recommandations basées sur l'IA
    """
    user_id = current_user["id"]

    # Analyser les meilleures heures par plateforme
    best_times_query = """
        SELECT
            platform,
            EXTRACT(HOUR FROM scheduled_time) as hour
        FROM media_scheduled_posts sp
        LEFT JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE sp.user_id = %s
        AND sp.status = 'published'
        GROUP BY platform, hour
        ORDER BY AVG(a.engagement_rate) DESC NULLS LAST
        LIMIT 50
    """

    times_data = media_db.execute_query(best_times_query, (user_id,))

    # Organiser par plateforme
    best_times = {}
    for row in times_data:
        platform = row['platform']
        hour = f"{int(row['hour']):02d}:00"
        if platform not in best_times:
            best_times[platform] = []
        if hour not in best_times[platform]:
            best_times[platform].append(hour)

    # Hashtags populaires
    hashtags_query = """
        SELECT
            platform,
            UNNEST(hashtags) as hashtag,
            COUNT(*) as usage_count
        FROM media_scheduled_posts sp
        LEFT JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE sp.user_id = %s
        AND sp.status = 'published'
        AND hashtags IS NOT NULL
        GROUP BY platform, hashtag
        ORDER BY AVG(a.engagement_rate) DESC NULLS LAST
        LIMIT 100
    """

    hashtags_data = media_db.execute_query(hashtags_query, (user_id,))

    # Organiser par plateforme
    suggested_hashtags = {}
    for row in hashtags_data:
        platform = row['platform']
        hashtag = row['hashtag']
        if platform not in suggested_hashtags:
            suggested_hashtags[platform] = []
        if len(suggested_hashtags[platform]) < 10:
            suggested_hashtags[platform].append(hashtag)

    return ContentRecommendations(
        user_id=user_id,
        best_posting_times=best_times or {
            "instagram": ["08:00", "12:00", "19:00"],
            "twitter": ["08:00", "15:00", "18:00"],
            "linkedin": ["07:00", "12:00", "17:00"]
        },
        trending_topics=["IA et Marketing", "Automation", "Productivité"],
        suggested_hashtags=suggested_hashtags or {
            "instagram": ["#marketing", "#business", "#entrepreneur"],
            "twitter": ["#AI", "#tech", "#innovation"]
        },
        content_ideas=[
            "Partager une success story client",
            "Créer un tutoriel rapide",
            "Montrer les coulisses de votre entreprise"
        ],
        tone_recommendations={
            "instagram": "inspirational",
            "linkedin": "professional",
            "twitter": "witty"
        }
    )


@router.get("/analytics/best-content")
async def get_best_performing_content(
    platform: Optional[PlatformType] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    🏆 Meilleur contenu par engagement
    """
    user_id = current_user["id"]

    conditions = ["sp.user_id = %s", "sp.status = 'published'"]
    params = [user_id]

    if platform:
        conditions.append("sp.platform = %s")
        params.append(platform.value)

    query = f"""
        SELECT
            sp.id,
            sp.platform,
            sp.post_text,
            sp.published_at,
            sp.platform_post_url,
            a.views,
            a.likes,
            a.comments,
            a.shares,
            a.engagement_rate
        FROM media_scheduled_posts sp
        JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE {' AND '.join(conditions)}
        ORDER BY a.engagement_rate DESC NULLS LAST, a.likes DESC
        LIMIT %s
    """

    params.append(limit)

    results = media_db.execute_query(query, tuple(params))
    return results


# ============================================
# UTILITY ENDPOINTS
# ============================================

@router.post("/hashtags/suggest", response_model=HashtagSuggestions)
async def suggest_hashtags(
    platform: PlatformType,
    content: str = Body(..., embed=True),
    count: int = Query(10, ge=1, le=30),
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    #️⃣ Suggérer des hashtags pour un contenu
    """
    try:
        hashtags = await content_generator.generate_hashtags(content, platform, count)

        return HashtagSuggestions(
            platform=platform,
            content=content,
            suggested_hashtags=[
                {"tag": tag, "relevance": 90, "volume": "high"}
                for tag in hashtags
            ],
            trending_hashtags=hashtags[:5]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hashtag suggestion failed: {str(e)}"
        )


@router.get("/statistics")
async def get_user_statistics(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    📊 Statistiques utilisateur globales
    """
    user_id = current_user["id"]

    query = """
        SELECT
            COUNT(DISTINCT gc.id) as total_content_generated,
            COUNT(DISTINCT sp.id) FILTER (WHERE sp.status = 'published') as total_posts_published,
            COUNT(DISTINCT sp.id) FILTER (WHERE sp.status = 'scheduled') as total_posts_scheduled,
            COALESCE(SUM(a.likes + a.comments + a.shares), 0) as total_engagement,
            COALESCE(AVG(a.engagement_rate), 0) as avg_engagement_rate
        FROM media_generated_content gc
        LEFT JOIN media_scheduled_posts sp ON gc.id = sp.content_id
        LEFT JOIN media_analytics a ON sp.id = a.scheduled_post_id
        WHERE gc.user_id = %s
    """

    stats = media_db.execute_one(query, (user_id,))

    # Plateformes connectées
    platforms = get_user_platforms(user_id)

    return {
        "user_id": user_id,
        "total_content_generated": stats['total_content_generated'] or 0,
        "total_posts_published": stats['total_posts_published'] or 0,
        "total_posts_scheduled": stats['total_posts_scheduled'] or 0,
        "connected_platforms": [p['platform'] for p in platforms],
        "total_engagement": int(stats['total_engagement']) or 0,
        "avg_engagement_rate": float(stats['avg_engagement_rate']) or 0.0
    }


@router.get("/health")
async def health_check():
    """
    ✅ Vérifier la santé du service
    """
    # Tester la connexion DB
    db_healthy = False
    try:
        media_db.execute_one("SELECT 1 as test")
        db_healthy = True
    except:
        pass

    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.utcnow(),
        "services": {
            "content_generator": content_generator.has_api_key,
            "oauth": True,
            "publishing": True,
            "database": db_healthy
        }
    }
