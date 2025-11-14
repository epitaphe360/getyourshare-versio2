#!/usr/bin/env python3
"""
Script de démarrage Python pour Railway
Gère le PORT directement en Python pour éviter les problèmes de shell
"""
import os
import sys

if __name__ == "__main__":
    # Récupérer le port depuis l'environnement
    port = int(os.environ.get("PORT", "8000"))

    print(f"🚀 Starting ShareYourSales Backend...")
    print(f"📍 Port: {port}")
    print(f"🌐 Host: 0.0.0.0")

    # Démarrer uvicorn via Python (pas via subprocess)
    import uvicorn

    uvicorn.run(
        "server_complete:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
