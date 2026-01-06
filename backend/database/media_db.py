"""
Connexion à la base de données pour le Module Media Automation
Utilise Supabase (PostgreSQL) et psycopg2 pour les requêtes SQL
"""

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from utils.logger import logger

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase/PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")  # Format: postgresql://user:pass@host:port/dbname

# Si DATABASE_URL n'existe pas, construire depuis les variables Supabase
if not DATABASE_URL:
    SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-0-eu-central-1.pooler.supabase.com")
    SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT", "5432")
    SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
    SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres")
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")

    if SUPABASE_DB_PASSWORD:
        DATABASE_URL = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"


class MediaDatabase:
    """
    Gestionnaire de connexion pour le module Media Automation
    Utilise un pool de connexions pour performance
    """

    def __init__(self):
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        """Initialise le pool de connexions"""
        if not DATABASE_URL:
            logger.warning("DATABASE_URL not configured. Media DB queries will not work.")
            print("⚠️ DATABASE_URL non configuré. Les requêtes DB ne fonctionneront pas.")
            return

        try:
            self.pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=DATABASE_URL
            )
            logger.info("Media DB connection pool initialized", extra={"minconn": 1, "maxconn": 10})
            print("✅ Pool de connexions Media DB initialisé")
        except Exception as e:
            logger.error(f"Failed to initialize Media DB pool: {str(e)}")
            print(f"❌ Erreur initialisation pool DB: {str(e)}")
            self.pool = None

    @contextmanager
    def get_connection(self):
        """Context manager pour obtenir une connexion du pool"""
        if not self.pool:
            raise Exception("Pool de connexions non initialisé")

        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)

    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Context manager pour obtenir un cursor"""
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Exécute une requête SELECT et retourne les résultats"""
        start_time = time.time()
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                duration_ms = (time.time() - start_time) * 1000

                # Log slow queries (> 100ms)
                if duration_ms > 100:
                    logger.warning("Slow query detected", extra={
                        "query": query[:100],
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(results)
                    })
                else:
                    logger.debug("Query executed", extra={
                        "duration_ms": round(duration_ms, 2),
                        "rows": len(results)
                    })

                return results
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}", extra={"query": query[:100]})
            raise

    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Exécute une requête SELECT et retourne un seul résultat"""
        start_time = time.time()
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                duration_ms = (time.time() - start_time) * 1000

                logger.debug("Query executed (one)", extra={"duration_ms": round(duration_ms, 2)})
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}", extra={"query": query[:100]})
            raise

    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Exécute un INSERT et retourne l'ID généré"""
        start_time = time.time()
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query + " RETURNING id", params or ())
                result = cursor.fetchone()
                duration_ms = (time.time() - start_time) * 1000

                logger.info("Insert executed", extra={
                    "duration_ms": round(duration_ms, 2),
                    "id": result['id'] if result else None
                })
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Insert failed: {str(e)}", extra={"query": query[:100]})
            raise

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Exécute un UPDATE et retourne le nombre de lignes affectées"""
        start_time = time.time()
        try:
            with self.get_cursor(dict_cursor=False) as cursor:
                cursor.execute(query, params or ())
                rowcount = cursor.rowcount
                duration_ms = (time.time() - start_time) * 1000

                logger.info("Update executed", extra={
                    "duration_ms": round(duration_ms, 2),
                    "rows_affected": rowcount
                })
                return rowcount
        except Exception as e:
            logger.error(f"Update failed: {str(e)}", extra={"query": query[:100]})
            raise

    def execute_delete(self, query: str, params: tuple = None) -> int:
        """Exécute un DELETE et retourne le nombre de lignes supprimées"""
        start_time = time.time()
        try:
            with self.get_cursor(dict_cursor=False) as cursor:
                cursor.execute(query, params or ())
                rowcount = cursor.rowcount
                duration_ms = (time.time() - start_time) * 1000

                logger.info("Delete executed", extra={
                    "duration_ms": round(duration_ms, 2),
                    "rows_deleted": rowcount
                })
                return rowcount
        except Exception as e:
            logger.error(f"Delete failed: {str(e)}", extra={"query": query[:100]})
            raise

    def close(self):
        """Ferme le pool de connexions"""
        if self.pool:
            self.pool.closeall()
            logger.info("Media DB connection pool closed")
            print("✅ Pool de connexions Media DB fermé")


# Instance globale
media_db = MediaDatabase()


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def dict_to_postgres_json(data: dict) -> Json:
    """Convertit un dict Python en Json PostgreSQL"""
    return Json(data)


def list_to_postgres_array(data: list) -> str:
    """Convertit une liste Python en array PostgreSQL"""
    if not data:
        return '{}'
    # Échapper les guillemets et formater
    escaped = [str(item).replace("'", "''") for item in data]
    return '{' + ','.join(f'"{item}"' for item in escaped) + '}'


# ============================================
# HELPER FUNCTIONS POUR LES QUERIES
# ============================================

def get_user_platforms(user_id: int) -> List[Dict[str, Any]]:
    """Récupère toutes les plateformes connectées d'un utilisateur"""
    query = """
        SELECT id, user_id, platform, account_name, account_id,
               is_active, connected_at, last_used_at, token_expires_at
        FROM media_platforms
        WHERE user_id = %s AND is_active = true
        ORDER BY connected_at DESC
    """
    return media_db.execute_query(query, (user_id,))


def get_platform_by_id(platform_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Récupère une plateforme par ID"""
    query = """
        SELECT *
        FROM media_platforms
        WHERE id = %s AND user_id = %s
    """
    return media_db.execute_one(query, (platform_id, user_id))


def get_generated_content(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Récupère le contenu généré d'un utilisateur"""
    query = """
        SELECT id, platform, prompt, generated_text, generated_hashtags,
               ai_model, tone, quality_score, engagement_prediction, status, created_at
        FROM media_generated_content
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    return media_db.execute_query(query, (user_id, limit, offset))


def get_scheduled_posts(user_id: int, platform: Optional[str] = None,
                       status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Récupère les posts planifiés"""
    conditions = ["user_id = %s"]
    params = [user_id]

    if platform:
        conditions.append("platform = %s")
        params.append(platform)

    if status:
        conditions.append("status = %s")
        params.append(status)

    query = f"""
        SELECT id, platform, scheduled_time, post_text, hashtags,
               status, published_at, platform_post_url, error_message
        FROM media_scheduled_posts
        WHERE {' AND '.join(conditions)}
        ORDER BY scheduled_time DESC
        LIMIT 100
    """
    return media_db.execute_query(query, tuple(params))


def get_posts_due_for_publication() -> List[Dict[str, Any]]:
    """Récupère les posts qui doivent être publiés maintenant"""
    query = """
        SELECT sp.*, mp.access_token, mp.refresh_token, mp.account_id, mp.metadata
        FROM media_scheduled_posts sp
        JOIN media_platforms mp ON sp.platform_id = mp.id
        WHERE sp.status = 'scheduled'
        AND sp.scheduled_time <= CURRENT_TIMESTAMP
        AND sp.retry_count < sp.max_retries
        ORDER BY sp.scheduled_time ASC
        LIMIT 50
    """
    return media_db.execute_query(query)


def get_analytics_by_post(post_id: int) -> Optional[Dict[str, Any]]:
    """Récupère les analytics d'un post"""
    query = """
        SELECT *
        FROM media_analytics
        WHERE scheduled_post_id = %s
    """
    return media_db.execute_one(query, (post_id,))


def save_oauth_state(user_id: int, platform: str, state_token: str,
                     code_verifier: Optional[str], redirect_uri: str) -> int:
    """Sauvegarde un état OAuth"""
    query = """
        INSERT INTO media_oauth_states
        (user_id, platform, state_token, code_verifier, redirect_uri, expires_at)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '10 minutes')
    """
    return media_db.execute_insert(query, (user_id, platform, state_token, code_verifier, redirect_uri))


def verify_oauth_state(state_token: str) -> Optional[Dict[str, Any]]:
    """Vérifie et marque un état OAuth comme utilisé"""
    # D'abord récupérer l'état
    query_select = """
        SELECT *
        FROM media_oauth_states
        WHERE state_token = %s
        AND used = false
        AND expires_at > CURRENT_TIMESTAMP
    """
    state = media_db.execute_one(query_select, (state_token,))

    if state:
        # Marquer comme utilisé
        query_update = """
            UPDATE media_oauth_states
            SET used = true
            WHERE state_token = %s
        """
        media_db.execute_update(query_update, (state_token,))

    return state


# ============================================
# CLEANUP
# ============================================

def cleanup_expired_oauth_states():
    """Nettoie les états OAuth expirés (à exécuter périodiquement)"""
    query = """
        DELETE FROM media_oauth_states
        WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '1 day'
    """
    return media_db.execute_delete(query)
