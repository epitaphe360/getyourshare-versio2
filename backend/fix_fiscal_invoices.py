"""
Script pour diagnostiquer et corriger le problème fiscal_invoices
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def fix_fiscal_invoices():
    print("\n🔍 DIAGNOSTIC: fiscal_invoices vs invoices")
    print("=" * 70)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Variables Supabase manquantes dans .env")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Test 1: Vérifier table invoices
    print("\n1️⃣  Test table 'invoices'...")
    try:
        result = supabase.table('invoices').select('id, invoice_number, payment_id').limit(1).execute()
        print(f"   ✅ Table 'invoices' existe")
        print(f"   📊 Colonnes: id, invoice_number, payment_id")
        if result.data:
            print(f"   💾 Données: {len(result.data)} ligne(s)")
    except Exception as e:
        error = str(e).lower()
        if 'payment_id' in error and 'does not exist' in error:
            print(f"   ⚠️  Table existe MAIS colonne 'payment_id' manquante!")
            print(f"   🔧 Solution: Exécuter ALTER TABLE invoices ADD COLUMN payment_id TEXT;")
        else:
            print(f"   ❌ Erreur: {e}")
    
    # Test 2: Vérifier fiscal_invoices
    print("\n2️⃣  Test table/vue 'fiscal_invoices'...")
    try:
        result = supabase.table('fiscal_invoices').select('id').limit(1).execute()
        print(f"   ✅ 'fiscal_invoices' existe (table ou vue)")
        if result.data:
            print(f"   💾 Données: {len(result.data)} ligne(s)")
    except Exception as e:
        print(f"   ❌ 'fiscal_invoices' n'existe pas: {e}")
    
    # Solution proposée
    print("\n" + "=" * 70)
    print("🔧 SOLUTION RECOMMANDÉE")
    print("=" * 70)
    print("""
Scénario A: fiscal_invoices est une TABLE (pas une vue)
----------------------------------------
Si fiscal_invoices existe déjà comme table, on doit:
1. Supprimer la table fiscal_invoices (si vide ou migrer données)
2. Créer une vue fiscal_invoices pointant vers invoices

SQL à exécuter dans Supabase Dashboard:
```sql
-- Option 1: Si fiscal_invoices est vide
DROP TABLE IF EXISTS fiscal_invoices CASCADE;
CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;

-- Option 2: Si fiscal_invoices contient des données
-- Migrer d'abord les données vers invoices
-- INSERT INTO invoices SELECT * FROM fiscal_invoices;
-- DROP TABLE fiscal_invoices CASCADE;
-- CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;
```

Scénario B: Colonnes payment_id manquantes dans invoices
---------------------------------------------------------
Si invoices n'a pas les colonnes payment_id, etc:

```sql
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS payment_id TEXT,
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid',
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT,
ADD COLUMN IF NOT EXISTS paypal_order_id TEXT,
ADD COLUMN IF NOT EXISTS payment_link TEXT,
ADD COLUMN IF NOT EXISTS webhook_received_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS refund_reason TEXT;
```

Scénario C: fiscal_invoices n'existe pas du tout
-------------------------------------------------
```sql
CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;
```
    """)
    
    # Test colonnes invoices
    print("\n3️⃣  Test colonnes table 'invoices'...")
    try:
        # Essayer de sélectionner toutes les colonnes potentielles
        columns_to_test = [
            'id', 'invoice_number', 'user_id', 'client_name', 'amount_ttc',
            'payment_id', 'payment_status', 'stripe_payment_intent_id', 
            'paypal_order_id', 'payment_link'
        ]
        
        existing_columns = []
        missing_columns = []
        
        for col in columns_to_test:
            try:
                supabase.table('invoices').select(col).limit(1).execute()
                existing_columns.append(col)
            except Exception:
                missing_columns.append(col)
        
        print(f"   ✅ Colonnes existantes ({len(existing_columns)}): {', '.join(existing_columns[:5])}...")
        if missing_columns:
            print(f"   ⚠️  Colonnes manquantes ({len(missing_columns)}): {', '.join(missing_columns)}")
        else:
            print(f"   ✅ Toutes les colonnes testées existent!")
            
    except Exception as e:
        print(f"   ❌ Erreur test colonnes: {e}")

if __name__ == "__main__":
    fix_fiscal_invoices()
