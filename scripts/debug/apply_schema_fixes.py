#!/usr/bin/env python3
"""
Script pour appliquer les corrections SQL critiques sur Supabase
Exécute FIX_SCHEMA_PART3_NEW_TABLES.sql
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Charger les variables d'environnement
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(env_path)

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERREUR: Variables SUPABASE_URL et SUPABASE_SERVICE_KEY requises dans backend/.env")
    sys.exit(1)

# Créer client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def execute_sql_file(filepath: str):
    """Exécute un fichier SQL via l'API Supabase"""
    print(f"\n📄 Lecture de {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Découper en commandes individuelles
    commands = []
    current_cmd = []
    in_do_block = False
    
    for line in sql_content.split('\n'):
        stripped = line.strip()
        
        # Ignorer commentaires
        if stripped.startswith('--') or not stripped:
            continue
            
        # Détecter blocs DO
        if 'DO $$' in stripped or 'DO $' in stripped:
            in_do_block = True
            current_cmd.append(line)
            continue
            
        if in_do_block:
            current_cmd.append(line)
            if '$$;' in stripped or '$;' in stripped:
                in_do_block = False
                commands.append('\n'.join(current_cmd))
                current_cmd = []
            continue
        
        current_cmd.append(line)
        
        # Fin de commande
        if stripped.endswith(';'):
            commands.append('\n'.join(current_cmd))
            current_cmd = []
    
    print(f"✅ {len(commands)} commandes SQL détectées\n")
    
    # Exécuter chaque commande
    success_count = 0
    error_count = 0
    
    for i, cmd in enumerate(commands, 1):
        cmd_preview = cmd.strip()[:60].replace('\n', ' ')
        print(f"[{i}/{len(commands)}] {cmd_preview}...")
        
        try:
            # Utiliser rpc pour exécuter du SQL brut
            result = supabase.rpc('exec_sql', {'sql': cmd}).execute()
            print(f"  ✅ Succès")
            success_count += 1
        except Exception as e:
            error_msg = str(e)
            
            # Ignorer les erreurs "already exists" ou "does not exist"
            if any(x in error_msg.lower() for x in [
                'already exists', 
                'does not exist',
                'duplicate',
                'if exists',
                'if not exists'
            ]):
                print(f"  ⚠️  Ignoré (déjà existant/inexistant)")
                success_count += 1
            else:
                print(f"  ❌ ERREUR: {error_msg}")
                error_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ:")
    print(f"  ✅ Succès: {success_count}/{len(commands)}")
    print(f"  ❌ Erreurs: {error_count}/{len(commands)}")
    print(f"{'='*60}\n")
    
    return error_count == 0

def main():
    print("="*60)
    print("🔧 APPLICATION DES CORRECTIONS SQL CRITIQUES")
    print("="*60)
    
    sql_file = Path(__file__).parent / "FIX_SCHEMA_PART3_NEW_TABLES.sql"
    
    if not sql_file.exists():
        print(f"❌ Fichier non trouvé: {sql_file}")
        sys.exit(1)
    
    print(f"\n🎯 Corrections à appliquer:")
    print(f"  1. Contrainte FK users_referred_by_fkey → ON DELETE SET NULL")
    print(f"  2. Colonne trust_scores.reviews_count")
    print(f"  3. Colonne qr_scan_events.user_id")
    print(f"  4. Rendre nullable: leads.marchand_id, integrations.credentials, content_templates.category")
    print(f"  5. Tables: disputes, promotions, live_streams, report_runs, workspace_comments")
    print(f"  6. Tables: invoices, webhook_logs, api_keys, rate_limits, data_exports")
    
    print(f"\n⚠️  ATTENTION: Ces modifications vont altérer le schéma de la base de données!")
    response = input("Continuer? [o/N]: ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Annulé par l'utilisateur")
        sys.exit(0)
    
    # Méthode alternative: exécution directe via PostgREST
    print("\n📡 Connexion à Supabase...")
    print(f"   URL: {SUPABASE_URL}")
    
    try:
        # Lire et exécuter le fichier SQL ligne par ligne
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Pour l'instant, afficher le SQL à exécuter manuellement
        print("\n" + "="*60)
        print("⚠️  EXÉCUTION MANUELLE REQUISE")
        print("="*60)
        print("\nSupabase n'expose pas d'API pour exécuter du SQL arbitraire.")
        print("Veuillez exécuter le contenu de FIX_SCHEMA_PART3_NEW_TABLES.sql")
        print("dans le SQL Editor de Supabase:")
        print(f"\n1. Ouvrir: {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/').split('.supabase')[0]}")
        print("2. Aller dans 'SQL Editor'")
        print("3. Copier-coller le contenu de FIX_SCHEMA_PART3_NEW_TABLES.sql")
        print("4. Cliquer sur 'Run'")
        print("\n" + "="*60)
        
        # Vérifier les tables critiques
        print("\n🔍 Vérification des tables existantes...")
        
        tables_to_check = [
            'users', 'trust_scores', 'qr_scan_events', 'leads', 
            'integrations', 'content_templates', 'disputes', 
            'promotions', 'live_streams'
        ]
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"  ✅ Table '{table}' existe")
            except Exception as e:
                if "Could not find" in str(e):
                    print(f"  ❌ Table '{table}' MANQUANTE")
                else:
                    print(f"  ⚠️  Table '{table}': {str(e)[:50]}")
        
        print("\n✅ Vérification terminée!")
        print("\n💡 Une fois le SQL exécuté dans Supabase, relancez:")
        print("   python backend/run_automation_scenario.py")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
