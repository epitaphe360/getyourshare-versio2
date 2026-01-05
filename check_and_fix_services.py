"""
Script pour ajouter la colonne commission_rate à services via Supabase client
"""
import os
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

def add_commission_rate_column():
    print("🔄 Ajout de commission_rate à la table services...")
    print("-" * 60)
    
    # Méthode 1: Essayer via une fonction PostgreSQL existante
    try:
        # Vérifier d'abord si la colonne existe déjà
        result = supabase.table('services').select('*').limit(1).execute()
        
        if result.data and 'commission_rate' in result.data[0]:
            print("✅ La colonne commission_rate existe déjà!")
            return True
        else:
            print("⚠️  La colonne commission_rate n'existe pas")
            print("\n📋 INSTRUCTIONS MANUELLES:")
            print("=" * 60)
            print("Allez sur https://supabase.com/dashboard")
            print("1. Ouvrez votre projet")
            print("2. Allez dans SQL Editor")
            print("3. Exécutez cette requête:")
            print("-" * 60)
            print("""
ALTER TABLE services 
ADD COLUMN commission_rate DECIMAL(5,2) DEFAULT 10.0 
CHECK (commission_rate >= 0 AND commission_rate <= 100);

UPDATE services 
SET commission_rate = 10.0 
WHERE commission_rate IS NULL;

COMMENT ON COLUMN services.commission_rate IS 
'Taux de commission en pourcentage pour ce service (0-100)';
            """)
            print("-" * 60)
            print("\n4. Après exécution, relancez le script d'automation")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_commission_rate_column()
    if not success:
        print("\n⚠️  Migration manuelle requise. Suivez les instructions ci-dessus.")
        sys.exit(1)
    else:
        print("\n✅ Migration vérifiée - vous pouvez lancer le script d'automation!")
        sys.exit(0)
