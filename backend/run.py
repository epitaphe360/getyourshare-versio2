#!/usr/bin/env python3
"""
Script de démarrage Python pour Railway
Gère le PORT directement en Python pour éviter les problèmes de shell
"""
import os
import sys

if __name__ == "__main__":
    # Récupérer le port depuis l'environnement
    port_str = os.environ.get("PORT", "8000")

    # DEBUG: Afficher la valeur brute de PORT
    print(f"🔍 DEBUG: PORT environment variable = '{port_str}'")

    # Si PORT contient littéralement "$PORT" (variable Railway mal configurée), utiliser 8000
    if port_str == "$PORT" or port_str == "${PORT}":
        print("⚠️  WARNING: PORT variable contains literal '$PORT', using default 8000")
        port = 8000
    else:
        try:
            port = int(port_str)
        except ValueError:
            print(f"⚠️  WARNING: Invalid PORT value '{port_str}', using default 8000")
            port = 8000

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
