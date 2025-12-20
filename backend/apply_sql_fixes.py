
import os
import re
from supabase_client import supabase

def apply_sql():
    print("=" * 80)
    print(" APPLICATION DES CORRECTIFS SQL")
    print("=" * 80)

    # Lire le fichier SQL
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'ADD_MISSING_TABLES_AND_COLUMNS.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Séparer par sections basées sur les commentaires de niveau 1 ou 2
    # On cherche les lignes qui commencent par -- suivi d'un chiffre ou d'un titre majeur
    sections = re.split(r'\n(?=-- [0-9])', sql_content)
    
    success_count = 0
    error_count = 0
    
    for section in sections:
        if not section.strip():
            continue
            
        # Extraire le titre de la section pour l'affichage
        title_match = re.search(r'-- (.*)', section)
        title = title_match.group(1) if title_match else "Section sans titre"
        
        print(f"\n▶ Exécution: {title}")
        
        try:
            # Nettoyer le SQL pour éviter les problèmes de caractères spéciaux
            query = section.strip()
            if not query:
                continue
                
            # Exécuter via RPC
            # Note: exec_sql doit exister dans Supabase
            supabase.rpc('exec_sql', {'query': query}).execute()
            print(f"  ✅ Succès")
            success_count += 1
        except Exception as e:
            error_msg = str(e)
            # Ignorer les erreurs "already exists" qui sont normales avec CREATE TABLE IF NOT EXISTS
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                print(f"  ℹ️  Déjà existant / Doublon (ignoré)")
                success_count += 1
            else:
                print(f"  ❌ Erreur: {error_msg[:200]}")
                error_count += 1

    print("\n" + "=" * 80)
    print(f" RÉSUMÉ: {success_count} sections traitées, {error_count} erreurs réelles")
    print("=" * 80)

if __name__ == "__main__":
    apply_sql()
