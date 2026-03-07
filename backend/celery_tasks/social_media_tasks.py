"""
Tâches Celery pour la synchronisation automatique des réseaux sociaux

Tâches principales:
1. sync_all_active_connections - Synchronise tous les comptes actifs (quotidien)
2. sync_user_connections - Synchronise les comptes d'un utilisateur spécifique
3. sync_single_connection - Synchronise une seule connexion
4. refresh_expiring_tokens - Rafraîchit les tokens expirant bientôt
5. check_and_repair_connections - Répare les connexions en erreur
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict

from services.social_media_service import SocialMediaService
from database import get_db_connection

logger = get_task_logger(__name__)

# ============================================
# TÂCHES DE SYNCHRONISATION
# ============================================

@shared_task(
    name='celery_tasks.social_media_tasks.sync_all_active_connections',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def sync_all_active_connections(self):
    """
    Synchroniser tous les comptes sociaux actifs

    Exécuté quotidiennement à 8h00 par Celery Beat
    """
    try:
        logger.info("🚀 Starting daily sync of all active social media connections")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer toutes les connexions actives avec auto_refresh activé
        cursor.execute("""
            SELECT id, user_id, platform, platform_user_id
            FROM social_media_connections
            WHERE connection_status = 'active'
            AND auto_refresh_enabled = TRUE
            ORDER BY last_synced_at ASC NULLS FIRST
        """)

        connections = cursor.fetchall()
        total_connections = len(connections)

        logger.info(f"Found {total_connections} active connections to sync")

        success_count = 0
        error_count = 0
        results = []

        # Synchroniser chaque connexion
        for conn_data in connections:
            connection_id, user_id, platform, platform_user_id = conn_data

            try:
                # Lancer la tâche de synchronisation individuelle
                result = sync_single_connection.delay(
                    connection_id=str(connection_id),
                    user_id=str(user_id),
                    platform=platform
                )

                results.append({
                    'connection_id': str(connection_id),
                    'platform': platform,
                    'task_id': result.id,
                    'status': 'queued'
                })

                success_count += 1

            except Exception as e:
                logger.error(f"Error queuing sync for connection {connection_id}: {str(e)}")
                error_count += 1

        cursor.close()
        conn.close()

        summary = {
            'total_connections': total_connections,
            'queued': success_count,
            'errors': error_count,
            'timestamp': datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Daily sync completed: {success_count} queued, {error_count} errors")

        return summary

    except Exception as exc:
        logger.error(f"❌ Daily sync failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='celery_tasks.social_media_tasks.sync_user_connections',
    bind=True,
    max_retries=2
)
def sync_user_connections(self, user_id: str, platforms: List[str] = None):
    """
    Synchroniser tous les comptes sociaux d'un utilisateur spécifique

    Args:
        user_id: ID de l'utilisateur
        platforms: Liste des plateformes à synchroniser (toutes si None)
    """
    try:
        logger.info(f"Syncing connections for user {user_id}, platforms: {platforms}")

        # Utiliser asyncio pour exécuter la fonction async
        service = SocialMediaService()
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            service.sync_all_user_stats(user_id=user_id, platforms=platforms)
        )

        logger.info(f"✅ User {user_id} sync completed: {len(results)} connections processed")

        return {
            'user_id': user_id,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ User sync failed for {user_id}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='celery_tasks.social_media_tasks.sync_single_connection',
    bind=True,
    max_retries=3,
    default_retry_delay=60  # 1 minute
)
def sync_single_connection(self, connection_id: str, user_id: str, platform: str):
    """
    Synchroniser une seule connexion

    Args:
        connection_id: ID de la connexion
        user_id: ID de l'utilisateur
        platform: Plateforme (instagram, tiktok, etc.)
    """
    try:
        logger.info(f"Syncing {platform} connection {connection_id} for user {user_id}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les détails de la connexion
        cursor.execute("""
            SELECT platform_user_id, access_token_encrypted, connection_status
            FROM social_media_connections
            WHERE id = %s AND user_id = %s
        """, (connection_id, user_id))

        result = cursor.fetchone()
        if not result:
            logger.warning(f"Connection {connection_id} not found")
            return {'status': 'not_found'}

        platform_user_id, access_token_encrypted, connection_status = result

        if connection_status != 'active':
            logger.warning(f"Connection {connection_id} is not active (status: {connection_status})")
            return {'status': 'inactive'}

        # Déchiffrer le token (TODO: implémenter le déchiffrement avec pgcrypto)
        # Pour l'instant, supposons que le token est stocké en clair (À CHANGER EN PRODUCTION!)
        access_token = access_token_encrypted

        # Synchroniser selon la plateforme
        service = SocialMediaService()
        loop = asyncio.get_event_loop()

        if platform == 'instagram':
            stats = loop.run_until_complete(
                service.fetch_instagram_stats(platform_user_id, access_token)
            )
        elif platform == 'tiktok':
            stats = loop.run_until_complete(
                service.fetch_tiktok_stats(platform_user_id, access_token)
            )
        else:
            logger.error(f"Unsupported platform: {platform}")
            return {'status': 'unsupported_platform'}

        # Sauvegarder les stats
        loop.run_until_complete(
            service._save_social_stats(user_id, stats)
        )

        # Mettre à jour last_synced_at
        cursor.execute("""
            UPDATE social_media_connections
            SET last_synced_at = CURRENT_TIMESTAMP,
                connection_status = 'active',
                connection_error = NULL
            WHERE id = %s
        """, (connection_id,))
        conn.commit()

        cursor.close()
        conn.close()

        logger.info(f"✅ Connection {connection_id} synced successfully")

        return {
            'connection_id': connection_id,
            'platform': platform,
            'stats': {
                'followers': stats.followers_count,
                'engagement_rate': stats.engagement_rate
            },
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Sync failed for connection {connection_id}: {str(exc)}")

        # Marquer la connexion comme erreur
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE social_media_connections
                SET connection_status = 'error',
                    connection_error = %s
                WHERE id = %s
            """, (str(exc)[:500], connection_id))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass

        raise self.retry(exc=exc)


# ============================================
# TÂCHES DE MAINTENANCE DES TOKENS
# ============================================

@shared_task(
    name='celery_tasks.social_media_tasks.refresh_expiring_tokens',
    bind=True
)
def refresh_expiring_tokens(self, days_before: int = 7):
    """
    Rafraîchir les tokens OAuth expirant bientôt

    Args:
        days_before: Nombre de jours avant expiration pour rafraîchir
    """
    try:
        logger.info(f"🔄 Refreshing tokens expiring in {days_before} days")

        service = SocialMediaService()
        loop = asyncio.get_event_loop()

        results = loop.run_until_complete(
            service.refresh_expiring_tokens(days_before=days_before)
        )

        success_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])

        logger.info(f"✅ Token refresh completed: {success_count} success, {failed_count} failed")

        return {
            'total': len(results),
            'success': success_count,
            'failed': failed_count,
            'details': results,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Token refresh failed: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='celery_tasks.social_media_tasks.check_and_repair_connections'
)
def check_and_repair_connections():
    """
    Vérifier et réparer les connexions en erreur

    Tente de réactiver les connexions marquées comme 'error'
    """
    try:
        logger.info("🔧 Checking and repairing failed connections")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Récupérer les connexions en erreur
        cursor.execute("""
            SELECT id, user_id, platform
            FROM social_media_connections
            WHERE connection_status = 'error'
            AND updated_at < NOW() - INTERVAL '1 hour'
            ORDER BY updated_at DESC
            LIMIT 50
        """)

        connections = cursor.fetchall()

        logger.info(f"Found {len(connections)} connections in error state")

        repaired_count = 0
        for conn_data in connections:
            connection_id, user_id, platform = conn_data

            try:
                # Tenter de synchroniser à nouveau
                result = sync_single_connection.delay(
                    connection_id=str(connection_id),
                    user_id=str(user_id),
                    platform=platform
                )
                repaired_count += 1

            except Exception as e:
                logger.error(f"Failed to queue repair for connection {connection_id}: {str(e)}")

        cursor.close()
        conn.close()

        logger.info(f"✅ Queued {repaired_count} connections for repair")

        return {
            'total_errors': len(connections),
            'queued_for_repair': repaired_count,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Connection repair failed: {str(exc)}")
        raise


# ============================================
# TÂCHES DE MAINTENANCE
# ============================================

@shared_task(
    name='celery_tasks.social_media_tasks.refresh_materialized_views'
)
def refresh_materialized_views():
    """
    Rafraîchir les vues matérialisées pour les dashboards

    Exécuté toutes les 6 heures
    """
    try:
        logger.info("🔄 Refreshing materialized views")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Rafraîchir la vue des dernières stats
        cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_latest_social_stats")

        # Rafraîchir la vue des top influenceurs
        cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_influencers_by_engagement")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("✅ Materialized views refreshed successfully")

        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Materialized view refresh failed: {str(exc)}")
        raise


@shared_task(
    name='celery_tasks.social_media_tasks.cleanup_old_logs'
)
def cleanup_old_logs(days_to_keep: int = 90):
    """
    Nettoyer les anciens logs de synchronisation

    Args:
        days_to_keep: Nombre de jours de logs à conserver
    """
    try:
        logger.info(f"🧹 Cleaning up sync logs older than {days_to_keep} days")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Supprimer les anciens logs
        cursor.execute("""
            DELETE FROM social_media_sync_logs
            WHERE created_at < NOW() - INTERVAL '%s days'
        """, (days_to_keep,))

        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ Deleted {deleted_count} old sync logs")

        return {
            'deleted_count': deleted_count,
            'days_to_keep': days_to_keep,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as exc:
        logger.error(f"❌ Log cleanup failed: {str(exc)}")
        raise


# ============================================
# TÂCHES SPÉCIFIQUES PAR PLATEFORME
# ============================================

@shared_task(
    name='celery_tasks.social_media_tasks.sync_instagram_account',
    rate_limit='200/h'  # Limite Instagram API
)
def sync_instagram_account(connection_id: str, user_id: str, platform_user_id: str, access_token: str):
    """
    Synchroniser un compte Instagram spécifique
    """
    return sync_single_connection(
        connection_id=connection_id,
        user_id=user_id,
        platform='instagram'
    )


@shared_task(
    name='celery_tasks.social_media_tasks.sync_tiktok_account',
    rate_limit='100/h'  # Limite TikTok API
)
def sync_tiktok_account(connection_id: str, user_id: str, platform_user_id: str, access_token: str):
    """
    Synchroniser un compte TikTok spécifique
    """
    return sync_single_connection(
        connection_id=connection_id,
        user_id=user_id,
        platform='tiktok'
    )


# ============================================
# CALLBACKS ET MONITORING
# ============================================

@shared_task
def task_success_callback(result):
    """Callback appelé quand une tâche réussit"""
    logger.info(f"✅ Task completed successfully: {result}")


@shared_task
def task_failure_callback(task_id, exc, traceback):
    """Callback appelé quand une tâche échoue"""
    logger.error(f"❌ Task {task_id} failed: {exc}\n{traceback}")
    # Envoyer notification aux admins
    try:
        import os, resend
        resend_key = os.getenv("RESEND_API_KEY", "")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@getyourshare.ma")
        if resend_key and admin_email:
            resend.api_key = resend_key
            resend.Emails.send({
                "from": "noreply@getyourshare.ma",
                "to": admin_email,
                "subject": f"[GetYourShare] Tâche Celery échouée : {task_id}",
                "html": f"<p><strong>Tâche :</strong> {task_id}</p><p><strong>Erreur :</strong> {exc}</p><pre>{traceback}</pre>"
            })
    except Exception:
        pass
