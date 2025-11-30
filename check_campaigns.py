from supabase import create_client

url = 'https://iamezkmapbhlhhvvsits.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE0NDQxMywiZXhwIjoyMDc2NzIwNDEzfQ.Ov5kQX_bxt4-XsnhHkFFB-W-At-W3BrBzlRsgfrjf3g'

supabase = create_client(url, key)

# Vérifier les campagnes
print("=" * 60)
print("VÉRIFICATION DES CAMPAGNES")
print("=" * 60)

campaigns = supabase.table('campaigns').select('*').execute()
print(f'\nNombre total de campagnes: {len(campaigns.data)}')

for c in campaigns.data[:10]:
    print(f'\n  ID: {c.get("id")}')
    print(f'  Nom: {c.get("name")}')
    print(f'  merchant_id: {c.get("merchant_id")}')
    print(f'  Status: {c.get("status")}')

# Vérifier les merchants
print("\n" + "=" * 60)
print("VÉRIFICATION DES MERCHANTS")
print("=" * 60)

merchants = supabase.table('users').select('id, email, role, username').eq('role', 'merchant').execute()
print(f'\nNombre de merchants: {len(merchants.data)}')

for m in merchants.data[:5]:
    print(f'\n  ID: {m.get("id")}')
    print(f'  Email: {m.get("email")}')
    print(f'  Username: {m.get("username")}')

# Vérifier la correspondance
print("\n" + "=" * 60)
print("CORRESPONDANCE CAMPAIGNS <-> MERCHANTS")
print("=" * 60)

merchant_ids = {m.get('id') for m in merchants.data}
for c in campaigns.data:
    mid = c.get('merchant_id')
    match = "✅ MATCH" if mid in merchant_ids else "❌ NO MATCH"
    print(f'Campaign "{c.get("name")}" -> merchant_id={mid} -> {match}')
