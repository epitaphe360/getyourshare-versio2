"""
Script pour vérifier si la table leads existe et contient des données
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils.supabase_client import get_supabase_client
supabase = get_supabase_client()

try:
    print("🔍 Vérification de la table 'leads'...")
    result = supabase.table('leads').select('*').limit(5).execute()
    print(f"✅ Table 'leads' existe: {len(result.data) if result.data else 0} enregistrements trouvés")
    if result.data:
        print(f"📊 Exemple de données: {result.data[0]}")
except Exception as e:
    print(f"❌ Erreur avec table 'leads': {e}")

try:
    print("\n🔍 Vérification de la table 'sales'...")
    result = supabase.table('sales').select('*').eq('status', 'pending').limit(5).execute()
    print(f"✅ Table 'sales' existe: {len(result.data) if result.data else 0} ventes en 'pending'")
    if result.data:
        print(f"📊 Exemple de données: {result.data[0]}")
except Exception as e:
    print(f"❌ Erreur avec table 'sales': {e}")

try:
    print("\n🔍 Vérification de la table 'conversions'...")
    result = supabase.table('conversions').select('*').limit(5).execute()
    print(f"✅ Table 'conversions' existe: {len(result.data) if result.data else 0} enregistrements")
    if result.data:
        print(f"📊 Exemple de données: {result.data[0]}")
except Exception as e:
    print(f"❌ Erreur avec table 'conversions': {e}")

print("\n" + "="*50)
print("📝 DIAGNOSTIC:")
print("="*50)
print("L'endpoint /api/leads cherche dans la table 'sales' avec status='pending'")
print("Mais votre système de leads utilise la table 'leads'")
print("Solutions possibles:")
print("1. Créer la table 'leads' si elle n'existe pas (leads_system.sql)")
print("2. Modifier l'endpoint pour utiliser la bonne table")
print("3. Ajouter des données de test dans la table appropriée")
