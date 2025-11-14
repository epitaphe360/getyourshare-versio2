"""
Serveur minimal de test pour Railway
Ce serveur démarre TOUJOURS, sans aucune dépendance
Utilisez-le pour tester si Railway peut au moins démarrer Python
"""

from fastapi import FastAPI
import uvicorn
import os
import sys

# Créer une app FastAPI minimale
app = FastAPI(title="Health Check Server")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Server is running!",
        "status": "ok",
        "python_version": sys.version,
        "environment": {
            "PORT": os.getenv("PORT", "8000"),
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "not-set"),
            "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID", "not-set")[:10] + "..." if os.getenv("RAILWAY_PROJECT_ID") else "not-set"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Minimal Test Server"
    }

@app.get("/env-check")
async def env_check():
    """Check which environment variables are set"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET",
        "CORS_ORIGINS",
        "PORT"
    ]

    env_status = {}
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Montrer seulement les premiers caractères pour la sécurité
            env_status[var] = f"SET ({len(value)} chars)"
        else:
            env_status[var] = "❌ NOT SET"

    return {
        "environment_variables": env_status,
        "all_required_set": all(os.getenv(var) for var in required_vars)
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting minimal health server on port {port}...")
    print(f"📍 Health check available at: http://0.0.0.0:{port}/health")
    print(f"🔍 Environment check at: http://0.0.0.0:{port}/env-check")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
