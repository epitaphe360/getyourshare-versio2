import sys
import os

# Add current directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

def execute_sql(sql: str, description: str):
    """Exécute une requête SQL via RPC et gère les erreurs."""
    try:
        print(f"⏳ {description}...")
        response = supabase.rpc('execute_sql', {'sql': sql}).execute()
        print(f"✅ {description} - Succès.")
        return True
    except Exception as e:
        print(f"❌ {description} - Erreur: {e}")
        # Fallback: try to print the error details if available
        if hasattr(e, 'details'):
             print(f"Details: {e.details}")
        return False

def main():
    print("\n🔧 Application du correctif pour social_media_stats...\n")
    
    sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'FIX_SOCIAL_STATS.sql')
    
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        execute_sql(sql_content, "Ajout de la colonne captured_at")
        
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {sql_file_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")

    print("\n🏁 Opération terminée.")

if __name__ == "__main__":
    main()
