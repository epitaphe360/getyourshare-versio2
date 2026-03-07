import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
os.chdir(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv("backend/.env")

from utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

print("\n🔧 Ajout du rôle 'commercial' à la base de données...\n")
print("⚠️  Cette opération nécessite l'exécution d'un script SQL dans Supabase.\n")
print("📋 Copiez et exécutez ce script dans l'éditeur SQL de Supabase:\n")
print("-" * 60)
print("""
-- Supprimer l'ancienne contrainte
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Ajouter la nouvelle contrainte avec le rôle 'commercial'
ALTER TABLE users ADD CONSTRAINT users_role_check 
CHECK (role IN ('admin', 'merchant', 'influencer', 'commercial', 'affiliate'));

-- Vérifier que la contrainte est en place
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'users'::regclass AND conname = 'users_role_check';
""")
print("-" * 60)
print("\n✅ Après avoir exécuté ce script dans Supabase:")
print("   Relancez: python create_commercials.py\n")

# Alternative: Utiliser le rôle merchant pour les commerciaux
print("\n💡 ALTERNATIVE: Utiliser le rôle 'merchant' pour les commerciaux")
print("   Les commerciaux peuvent être considérés comme des marchands")
print("   qui vendent des services de vente plutôt que des produits.\n")

choice = input("Voulez-vous créer les commerciaux en tant que 'merchant' ? (o/n): ")

if choice.lower() == 'o':
    print("\n🚀 Création des commerciaux en tant que merchants...\n")
    exec(open('create_commercials_as_merchants.py').read())
else:
    print("\n👉 Exécutez le script SQL ci-dessus dans Supabase, puis relancez create_commercials.py")
