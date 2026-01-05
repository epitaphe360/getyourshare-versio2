"""
Vérifier la structure réelle de tracking_links
"""
import os, sys, json
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from supabase_client import supabase

result = supabase.table('tracking_links').select('*').limit(1).execute()
if result.data:
    print("Colonnes tracking_links:")
    for col in result.data[0].keys():
        print(f"  - {col}")
else:
    print("Table vide")
