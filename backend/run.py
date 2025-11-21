#!/usr/bin/env python3
"""
Script de démarrage Python pour Railway - VERSION DEBUG
Gère le PORT directement en Python pour éviter les problèmes de shell
"""
import os
import sys

if __name__ == "__main__":
    # DEBUG: Confirmer que ce script s'exécute
    print("="*70)
    print("🔍 DEBUG: run.py is EXECUTING (version: syntax-fixes-final)")
    print("="*70)

    # DEBUG: Afficher toutes les variables d'environnement
    print(f"🔍 All environment variables:")
    for key in sorted(os.environ.keys()):
        if "PORT" in key or "SECRET" in key or "SUPABASE" in key:
            value = os.environ[key]
            if "SECRET" in key or "KEY" in key:
                print(f"   {key} = {value[:20]}... (masked)")
            else:
                print(f"   {key} = {value}")

    # Récupérer le port depuis l'environnement
    port_str = os.environ.get("PORT")
    print(f"\n🔍 DEBUG: os.environ.get('PORT') = {repr(port_str)}")

    # Si PORT n'est pas défini, utiliser le défaut
    if port_str is None:
        print("⚠️  WARNING: PORT not defined in environment, using 8003")
        port = 8003
    # Si PORT contient littéralement "$PORT" (variable Railway mal configurée), utiliser 8003
    elif port_str in ["$PORT", "${PORT}", ""]:
        print(f"⚠️  WARNING: PORT variable contains '{port_str}', using default 8003")
        port = 8003
    else:
        try:
            port = int(port_str)
            print(f"✅ PORT successfully parsed: {port}")
        except ValueError as e:
            print(f"⚠️  WARNING: Invalid PORT value '{port_str}' (error: {e}), using default 8003")
            port = 8003

    print(f"\n🚀 Starting ShareYourSales Backend...")
    print(f"📍 Port: {port}")
    print(f"🌐 Host: 0.0.0.0")
    print("="*70)

    # Démarrer uvicorn via Python (pas via subprocess)
    import uvicorn

    uvicorn.run(
        "server:app",  # Changed from server_complete to server (has httpOnly cookie auth)
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
