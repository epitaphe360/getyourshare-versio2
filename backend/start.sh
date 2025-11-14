#!/bin/bash
# Script de démarrage pour Railway
# Gère correctement la variable PORT

# Récupérer le port depuis la variable d'environnement, par défaut 8000
PORT=${PORT:-8000}

echo "🚀 Starting ShareYourSales Backend..."
echo "📍 Port: $PORT"
echo "🌐 Host: 0.0.0.0"

# Démarrer uvicorn avec le port correct
exec uvicorn server_complete:app --host 0.0.0.0 --port "$PORT"
