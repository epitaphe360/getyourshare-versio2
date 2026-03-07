"""
Health Check Endpoint - Production Grade
GET /health    → vérification rapide (load balancer)
GET /health/details → vérification complète avec DB, Redis, services
"""

import os
import time
import logging
from typing import Dict, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


def _check_supabase() -> Dict[str, Any]:
    """Vérifie la connexion Supabase"""
    start = time.monotonic()
    try:
        from supabase_client import supabase
        result = supabase.table("users").select("id").limit(1).execute()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "ok", "latency_ms": latency_ms}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}


def _check_redis() -> Dict[str, Any]:
    """Vérifie la connexion Redis"""
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return {"status": "not_configured"}
    start = time.monotonic()
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {"status": "ok", "latency_ms": latency_ms}
    except ImportError:
        return {"status": "not_installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}


def _check_resend() -> Dict[str, Any]:
    """Vérifie que la clé Resend est configurée"""
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key:
        return {"status": "not_configured"}
    return {"status": "ok", "key_prefix": api_key[:8] + "..."}


def _check_celery() -> Dict[str, Any]:
    """Vérifie que Celery est accessible"""
    try:
        from celery_app import celery_app
        i = celery_app.control.inspect(timeout=1.0)
        active = i.active()
        if active is not None:
            worker_count = len(active)
            return {"status": "ok", "workers": worker_count}
        return {"status": "degraded", "message": "no_workers_responding"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}


@router.get("/health")
async def health_quick():
    """
    Health check rapide pour load balancer / Railway
    Répond toujours 200 sauf si la DB est HS
    """
    try:
        from supabase_client import supabase
        supabase.table("users").select("id").limit(1).execute()
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "timestamp": time.time()}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "error": str(e)[:100]}
        )


@router.get("/health/details")
async def health_details():
    """
    Health check complet avec tous les services
    Utilisé pour monitoring Grafana / alertes
    """
    start = time.monotonic()

    db = _check_supabase()
    redis_status = _check_redis()
    email = _check_resend()
    celery_status = _check_celery()

    total_ms = round((time.monotonic() - start) * 1000, 1)

    # Statut global
    critical_ok = db["status"] == "ok"
    overall = "ok" if critical_ok else "degraded"

    status_code = 200 if critical_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall,
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "total_check_ms": total_ms,
            "services": {
                "database": db,
                "redis": redis_status,
                "email": email,
                "celery": celery_status,
            }
        }
    )
