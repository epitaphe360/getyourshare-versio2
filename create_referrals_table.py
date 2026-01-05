"""
Script pour créer la table referrals manquante
"""
import os
from supabase import create_client

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gwgvnusegnnhiciprvyc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3Z3ZudXNlZ25uaGljaXBydnljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MjE3NjgsImV4cCI6MjA0NjM5Nzc2OH0.gftLI_u0AxQUVIUi3hWjfJQ-m6Y56b5H5lDwbMEDGbU")

SQL = """
CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    referral_url TEXT,
    total_referrals INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_referrals_user ON referrals(user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);

ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all for referrals" ON referrals;
CREATE POLICY "Enable all for referrals" ON referrals FOR ALL USING (true);
"""

print("🔧 Création de la table referrals...")
print("\n⚠️  IMPORTANT: Ce SQL doit être exécuté dans Supabase SQL Editor")
print("="*80)
print("\n📋 Copiez et collez ce code dans Supabase SQL Editor:\n")
print("="*80)
print(SQL)
print("="*80)
print(f"\n💡 URL: https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new")
print("\nOu exécutez via API REST si vous avez les permissions suffisantes.")

# Tentative via l'API (peut ne pas fonctionner avec les permissions anon)
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Test si la table existe
    result = supabase.table('referrals').select('id').limit(1).execute()
    print("\n✅ La table 'referrals' existe déjà!")
except Exception as e:
    if "relation" in str(e).lower() and "does not exist" in str(e).lower():
        print("\n❌ La table 'referrals' n'existe pas encore")
        print("👉 Veuillez exécuter le SQL ci-dessus dans Supabase SQL Editor")
    else:
        print(f"\n⚠️  Erreur: {str(e)[:100]}")
