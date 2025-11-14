#!/bin/bash
# Script de démarrage ULTRA-RAPIDE
# Saute tous les imports lents

PORT=${PORT:-8000}

echo "⚡ FAST START MODE - Serveur minimal Python"
echo "📍 Port: $PORT"

# Démarrer le serveur minimal (pas de FastAPI, pas d'imports)
exec python minimal_server.py
