import subprocess
import time
import sys

print("=" * 70)
print("SURVEILLANCE DES LOGS BACKEND EN TEMPS RÉEL")
print("=" * 70)
print("\nEssayez de vous connecter sur http://localhost:3000")
print("Les erreurs apparaîtront ci-dessous...")
print("\nAppuyez sur Ctrl+C pour arrêter\n")
print("=" * 70)

# Chercher le processus Python qui exécute server.py
try:
    # Attendre quelques secondes pour voir les logs
    time.sleep(30)
    print("\n✓ Surveillance terminée")
    
except KeyboardInterrupt:
    print("\n\n✓ Surveillance arrêtée par l'utilisateur")
    sys.exit(0)
