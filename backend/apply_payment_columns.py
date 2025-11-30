"""
Script SIMPLIFIÉ pour ajouter colonnes manquantes via Supabase SQL Editor
Instructions: Copier-coller ce SQL dans Supabase Dashboard > SQL Editor
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     MIGRATION 013: COLONNES PAIEMENT                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  CETTE MIGRATION DOIT ÊTRE EXÉCUTÉE MANUELLEMENT via Supabase Dashboard

📍 Instructions:
   1. Ouvrir https://supabase.com/dashboard/project/YOUR_PROJECT/sql
   2. Copier-coller le SQL ci-dessous
   3. Cliquer "Run"

═══════════════════════════════════════════════════════════════════════════════

-- ÉTAPE 1: Ajouter colonnes paiement à invoices
ALTER TABLE invoices 
ADD COLUMN IF NOT EXISTS payment_id TEXT,
ADD COLUMN IF NOT EXISTS payment_provider TEXT,
ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'unpaid',
ADD COLUMN IF NOT EXISTS stripe_payment_intent_id TEXT,
ADD COLUMN IF NOT EXISTS paypal_order_id TEXT,
ADD COLUMN IF NOT EXISTS payment_link TEXT,
ADD COLUMN IF NOT EXISTS webhook_received_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(12,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS refund_reason TEXT,
ADD COLUMN IF NOT EXISTS bank_reconciliation_id UUID,
ADD COLUMN IF NOT EXISTS reminder_sent_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reminder_sent_at TIMESTAMP;

-- ÉTAPE 2: Index pour performance
CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON invoices(payment_id);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);

-- ÉTAPE 3: Créer vue fiscal_invoices (alias)
CREATE OR REPLACE VIEW fiscal_invoices AS SELECT * FROM invoices;

-- ÉTAPE 4: Tables rapprochement bancaire
CREATE TABLE IF NOT EXISTS bank_reconciliations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bank_name TEXT NOT NULL,
  statement_date DATE NOT NULL,
  total_amount DECIMAL(12,2) DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
  payment_provider TEXT NOT NULL,
  payment_link TEXT NOT NULL,
  payment_id TEXT UNIQUE NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  currency TEXT DEFAULT 'MAD',
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

═══════════════════════════════════════════════════════════════════════════════

✅ Après exécution, toutes les colonnes manquantes seront créées!

═══════════════════════════════════════════════════════════════════════════════
""")

# Test de connexion pour vérifier
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        
        # Test si colonnes existent déjà
        print("\n🔍 TEST: Vérification colonnes existantes...")
        try:
            result = supabase.table('invoices').select('payment_id, payment_status').limit(1).execute()
            print("✅ Les colonnes existent déjà! Migration non nécessaire.")
        except Exception as e:
            if 'does not exist' in str(e).lower():
                print("⚠️  Les colonnes n'existent PAS encore - migration nécessaire!")
            else:
                print(f"❓ Erreur test: {e}")
    else:
        print("\n⚠️  Variables Supabase non trouvées dans .env")
        
except ImportError:
    print("\n⚠️  Module supabase non installé")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
