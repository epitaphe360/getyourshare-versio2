#!/usr/bin/env python3
"""
Script pour extraire toutes les tables Supabase utilisées dans l'application
"""
import re
import os
from pathlib import Path

def extract_tables_from_file(file_path):
    """Extrait tous les noms de tables d'un fichier Python"""
    tables = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Pattern pour extraire supabase.table("nom_table")
            pattern = r'supabase\.table\(["\']([a-zA-Z_]+)["\']'
            matches = re.findall(pattern, content)
            tables.update(matches)
            
            # Pattern alternatif: .table('nom_table')
            pattern2 = r'\.table\(["\']([a-zA-Z_]+)["\']'
            matches2 = re.findall(pattern2, content)
            tables.update(matches2)
            
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")
    
    return tables

def scan_backend_directory(backend_dir):
    """Scan tous les fichiers Python du backend"""
    all_tables = set()
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                tables = extract_tables_from_file(file_path)
                all_tables.update(tables)
                if tables:
                    print(f"📄 {file}: {len(tables)} tables")
    
    return all_tables

def main():
    backend_dir = r"c:\Users\samye\OneDrive\Desktop\v3\getyourshareversion2-\backend"
    
    print("🔍 SCAN DES FICHIERS BACKEND...")
    print("="*60)
    
    all_tables = scan_backend_directory(backend_dir)
    
    print("\n" + "="*60)
    print(f"📊 TOTAL: {len(all_tables)} TABLES UNIQUES TROUVÉES")
    print("="*60)
    
    # Trier par ordre alphabétique
    sorted_tables = sorted(list(all_tables))
    
    for i, table in enumerate(sorted_tables, 1):
        print(f"{i:3d}. {table}")
    
    # Sauvegarder dans un fichier
    output_file = r"c:\Users\samye\OneDrive\Desktop\v3\getyourshareversion2-\LISTE_TABLES_COMPLETE.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("LISTE COMPLÈTE DES TABLES SUPABASE UTILISÉES\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total: {len(all_tables)} tables\n\n")
        for i, table in enumerate(sorted_tables, 1):
            f.write(f"{i:3d}. {table}\n")
    
    print(f"\n✅ Liste sauvegardée dans: LISTE_TABLES_COMPLETE.txt")
    
    return sorted_tables

if __name__ == "__main__":
    tables = main()
