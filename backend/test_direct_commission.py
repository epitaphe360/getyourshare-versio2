"""
Test direct de la logique de calcul sans passer par l'API
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 80)
print("TEST CALCUL COMMISSION PLATEFORME")
print("=" * 80)

# Récupérer les ventes complétées
sales_result = supabase.table("sales").select("amount, platform_commission, commission_amount").eq("status", "completed").execute()
sales = sales_result.data or []

print(f"\n✅ Nombre de ventes complétées: {len(sales)}")

if not sales:
    print("❌ Aucune vente trouvée!")
    exit(1)

# Calculer les totaux
total_revenue = sum(float(s.get("amount", 0)) for s in sales)
platform_commission = sum(float(s.get("platform_commission", 0)) for s in sales)
influencer_commission = sum(float(s.get("commission_amount", 0)) for s in sales)
merchant_revenue = total_revenue - platform_commission - influencer_commission

print("\n💰 RÉSULTATS:")
print(f"  Total Revenue (ventes): {total_revenue:.2f} MAD")
print(f"  Platform Commission: {platform_commission:.2f} MAD")
print(f"  Influencer Commission: {influencer_commission:.2f} MAD")
print(f"  Merchant Revenue: {merchant_revenue:.2f} MAD")

# Vérifier cohérence
total_calculated = platform_commission + influencer_commission + merchant_revenue
print(f"\n🔍 VÉRIFICATION:")
print(f"  Total calculé (sum): {total_calculated:.2f} MAD")
print(f"  Différence: {abs(total_revenue - total_calculated):.2f} MAD")

# Calculer le pourcentage
if total_revenue > 0:
    platform_rate = (platform_commission / total_revenue) * 100
    print(f"  Taux commission plateforme: {platform_rate:.2f}%")

# Afficher quelques exemples
print("\n📋 EXEMPLES DE VENTES:")
for i, sale in enumerate(sales[:5], 1):
    amount = float(sale.get("amount", 0))
    plat_comm = float(sale.get("platform_commission", 0))
    rate = (plat_comm / amount * 100) if amount > 0 else 0
    print(f"{i}. {amount:.2f} MAD → Commission: {plat_comm:.2f} MAD ({rate:.1f}%)")

# Résultat final
print("\n" + "=" * 80)
if platform_commission > 0:
    print(f"✅ SUCCÈS: Commission plateforme = {platform_commission:.2f} MAD")
    print("   Le backend devrait afficher cette valeur dans le dashboard!")
else:
    print("❌ ERREUR: Commission plateforme = 0 MAD")
print("=" * 80)
