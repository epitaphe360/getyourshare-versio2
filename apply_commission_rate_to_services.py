"""
Script Python pour appliquer la migration ADD_COMMISSION_RATE_TO_SERVICES
"""
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from supabase_client import supabase

def apply_migration():
    print("🔄 Application de la migration: ADD_COMMISSION_RATE_TO_SERVICES")
    print("-" * 60)
    
    sql_statements = [
        """
        ALTER TABLE services 
        ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,2) DEFAULT 10.0 
        CHECK (commission_rate >= 0 AND commission_rate <= 100);
        """,
        """
        UPDATE services 
        SET commission_rate = 10.0 
        WHERE commission_rate IS NULL;
        """,
        """
        COMMENT ON COLUMN services.commission_rate IS 
        'Taux de commission en pourcentage pour ce service (0-100)';
        """
    ]
    
    try:
        for i, sql in enumerate(sql_statements, 1):
            print(f"\n[{i}/{len(sql_statements)}] Exécution de la requête...")
            result = supabase.rpc('exec_sql', {'query': sql.strip()}).execute()
            print(f"✅ Succès")
        
        print("\n" + "=" * 60)
        print("✅ Migration appliquée avec succès!")
        print("=" * 60)
        
        # Vérifier la structure
        print("\n🔍 Vérification de la colonne...")
        result = supabase.table('services').select('*').limit(1).execute()
        if result.data:
            print(f"✅ Structure vérifiée. Colonnes disponibles: {list(result.data[0].keys())}")
        else:
            print("⚠️  Aucun service trouvé pour vérifier la structure")
            
    except Exception as e:
        print(f"\n❌ Erreur lors de l'application: {str(e)}")
        print("\n💡 Tentative d'application directe via SQL...")
        
        # Méthode alternative: direct SQL execution
        try:
            # Essayer d'ajouter la colonne directement
            supabase.postgrest.schema('public').rpc('exec_sql', {
                'query': """
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'services' 
                        AND column_name = 'commission_rate'
                    ) THEN
                        ALTER TABLE services 
                        ADD COLUMN commission_rate DECIMAL(5,2) DEFAULT 10.0 
                        CHECK (commission_rate >= 0 AND commission_rate <= 100);
                        
                        UPDATE services 
                        SET commission_rate = 10.0 
                        WHERE commission_rate IS NULL;
                    END IF;
                END $$;
                """
            }).execute()
            print("✅ Migration appliquée via méthode alternative!")
        except Exception as e2:
            print(f"❌ Échec méthode alternative: {str(e2)}")
            print("\n⚠️  SOLUTION MANUELLE REQUISE:")
            print("Exécutez cette requête directement dans Supabase SQL Editor:")
            print("-" * 60)
            print("""
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,2) DEFAULT 10.0 
CHECK (commission_rate >= 0 AND commission_rate <= 100);

UPDATE services 
SET commission_rate = 10.0 
WHERE commission_rate IS NULL;
            """)
            print("-" * 60)
            sys.exit(1)

if __name__ == "__main__":
    apply_migration()
