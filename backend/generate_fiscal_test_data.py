"""
Script de génération de données de test pour le système fiscal
Génère des factures, déclarations TVA, et données réalistes
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from supabase_client import supabase

# Données de test
COUNTRIES = ['MA', 'FR', 'US']
CURRENCIES = {'MA': 'MAD', 'FR': 'EUR', 'US': 'USD'}

COMPANY_NAMES = {
    'MA': ['Spa Serenity Marrakech', 'Salon Beauty Casa', 'Wellness Center Rabat', 'Coiffure Elite Tanger'],
    'FR': ['Institut Belle Vie Paris', 'Spa Luxe Lyon', 'Salon Chic Marseille', 'Beauté Premium Nice'],
    'US': ['Golden Spa New York', 'Beauty Palace LA', 'Wellness Center Miami', 'Elite Salon Chicago']
}

TAX_IDS = {
    'MA': ['002345678000012', '002345679000013', '002345680000014'],
    'FR': ['12345678900012', '12345678900013', '12345678900014'],
    'US': ['12-3456789', '12-3456790', '12-3456791']
}

CLIENT_NAMES = [
    'Marie Dubois', 'Sophie Martin', 'Julie Bernard', 'Emma Laurent',
    'Sarah Cohen', 'Léa Moreau', 'Camille Petit', 'Chloé Simon',
    'Laura Garcia', 'Jessica Martinez', 'Amanda Johnson', 'Emily Davis'
]

SERVICES = [
    'Massage relaxant 60min', 'Soin du visage complet', 'Coupe + Brushing',
    'Manucure + Pédicure', 'Épilation complète', 'Maquillage professionnel',
    'Soin du corps gommage', 'Hammam + Gommage', 'Extension de cils',
    'Coloration cheveux', 'Lissage brésilien', 'Spa privatif 2h'
]

def get_random_user():
    """Récupère un utilisateur aléatoire de la base"""
    try:
        result = supabase.table('users').select('id, email, role').limit(10).execute()
        if result.data:
            return random.choice(result.data)
    except Exception as e:
        print(f"⚠️  Erreur récupération users: {e}")
    return None

def create_fiscal_settings():
    """Crée des configurations fiscales pour 3 pays"""
    print("\n📋 Création des configurations fiscales...")
    
    settings_created = 0
    for country in COUNTRIES:
        user = get_random_user()
        if not user:
            print(f"  ⚠️  Aucun utilisateur trouvé pour {country}")
            continue
            
        try:
            # Vérifier si une config existe déjà
            existing = supabase.table('fiscal_settings').select('id').eq('user_id', user['id']).eq('country', country).execute()
            if existing.data:
                print(f"  ⏭️  Configuration {country} existe déjà pour {user['email']}")
                continue
            
            data = {
                'user_id': user['id'],
                'country': country,
                'company_name': random.choice(COMPANY_NAMES[country]),
                'tax_id': random.choice(TAX_IDS[country]),
                'vat_regime': 'normal',
                'accounting_start_date': '2024-01-01',
                'fiscal_year_end': '31/12',
                'currency': CURRENCIES[country],
                'invoice_prefix': 'FA',
                'next_invoice_number': 1
            }
            
            supabase.table('fiscal_settings').insert(data).execute()
            settings_created += 1
            print(f"  ✅ Config créée: {country} - {data['company_name']}")
        except Exception as e:
            print(f"  ❌ Erreur création config {country}: {e}")
    
    print(f"\n✅ {settings_created} configurations fiscales créées")

def create_invoices(count=30):
    """Crée des factures de test"""
    print(f"\n📄 Création de {count} factures...")
    
    # Récupérer des users
    users = supabase.table('users').select('id, email').limit(20).execute()
    if not users.data:
        print("  ❌ Aucun utilisateur trouvé")
        return
    
    # Récupérer les taux de TVA
    vat_rates = supabase.table('vat_rates').select('country, rate, category').execute()
    rates_by_country = {}
    for rate in vat_rates.data:
        if rate['country'] not in rates_by_country:
            rates_by_country[rate['country']] = []
        rates_by_country[rate['country']].append(rate['rate'])
    
    # Récupérer le dernier numéro de facture existant
    existing_invoices = supabase.table('fiscal_invoices').select('invoice_number').order('invoice_number', desc=True).limit(1).execute()
    last_num = 1000
    if existing_invoices.data:
        try:
            last_invoice_num = existing_invoices.data[0]['invoice_number']
            last_num = int(last_invoice_num.split('-')[-1])
        except Exception:
            pass
    
    invoices_created = 0
    for i in range(count):
        user = random.choice(users.data)
        country = random.choice(COUNTRIES)
        
        # Date aléatoire dans les 6 derniers mois
        days_ago = random.randint(0, 180)
        issue_date = datetime.now() - timedelta(days=days_ago)
        due_date = issue_date + timedelta(days=30)
        
        # Montants aléatoires
        amount_ht = round(random.uniform(50, 500), 2)
        vat_rate = random.choice(rates_by_country.get(country, [20.0]))
        vat_amount = round(amount_ht * vat_rate / 100, 2)
        amount_ttc = amount_ht + vat_amount
        
        # Statut aléatoire
        status = random.choices(
            ['paid', 'sent', 'draft', 'overdue'],
            weights=[60, 20, 10, 10]
        )[0]
        
        try:
            invoice_num = last_num + invoices_created + 1
            invoice_data = {
                'invoice_number': f'FA-2024-{invoice_num:04d}',
                'user_id': user['id'],
                'client_name': random.choice(CLIENT_NAMES),
                'client_email': f"{random.choice(CLIENT_NAMES).lower().replace(' ', '.')}@example.com",
                'country': country,
                'issue_date': issue_date.strftime('%Y-%m-%d'),
                'due_date': due_date.strftime('%Y-%m-%d'),
                'amount_ht': amount_ht,
                'vat_rate': vat_rate,
                'vat_amount': vat_amount,
                'amount_ttc': amount_ttc,
                'currency': CURRENCIES[country],
                'payment_method': random.choice(['bank_transfer', 'credit_card', 'cash']),
                'payment_date': issue_date.strftime('%Y-%m-%d') if status == 'paid' else None,
                'status': status,
                'notes': 'Facture générée automatiquement pour test'
            }
            
            result = supabase.table('fiscal_invoices').insert(invoice_data).execute()
            invoice_id = result.data[0]['id']
            
            # Créer 1-3 lignes de facture
            num_lines = random.randint(1, 3)
            for line_num in range(1, num_lines + 1):
                line_ht = round(amount_ht / num_lines, 2)
                line_vat = round(line_ht * vat_rate / 100, 2)
                
                line_data = {
                    'invoice_id': invoice_id,
                    'line_number': line_num,
                    'description': random.choice(SERVICES),
                    'quantity': 1,
                    'unit_price_ht': line_ht,
                    'vat_rate': vat_rate,
                    'total_ht': line_ht,
                    'total_vat': line_vat,
                    'total_ttc': line_ht + line_vat
                }
                supabase.table('fiscal_invoice_lines').insert(line_data).execute()
            
            invoices_created += 1
            if invoices_created % 10 == 0:
                print(f"  📄 {invoices_created}/{count} factures créées...")
                
        except Exception as e:
            print(f"  ❌ Erreur création facture {i+1}: {e}")
    
    print(f"\n✅ {invoices_created} factures créées avec succès")

def create_vat_declarations():
    """Crée des déclarations de TVA"""
    print("\n📊 Création des déclarations TVA...")
    
    users = supabase.table('users').select('id, email').limit(10).execute()
    if not users.data:
        print("  ❌ Aucun utilisateur trouvé")
        return
    
    declarations_created = 0
    
    # Créer des déclarations pour Q3 et Q4 2024
    quarters = [
        ('2024-07-01', '2024-09-30', 'quarterly'),
        ('2024-10-01', '2024-12-31', 'quarterly'),
    ]
    
    for user in users.data[:5]:  # 5 premiers users
        for period_start, period_end, decl_type in quarters:
            for country in COUNTRIES:
                try:
                    # Vérifier si existe déjà
                    existing = supabase.table('vat_declarations').select('id').eq('user_id', user['id']).eq('country', country).eq('period_start', period_start).execute()
                    if existing.data:
                        continue
                    
                    vat_collected = round(random.uniform(1000, 5000), 2)
                    vat_deductible = round(random.uniform(200, 1000), 2)
                    vat_to_pay = vat_collected - vat_deductible
                    
                    declaration_data = {
                        'user_id': user['id'],
                        'period_start': period_start,
                        'period_end': period_end,
                        'declaration_type': decl_type,
                        'country': country,
                        'vat_collected': vat_collected,
                        'vat_deductible': vat_deductible,
                        'vat_to_pay': vat_to_pay,
                        'status': random.choice(['paid', 'submitted', 'draft'])
                    }
                    
                    supabase.table('vat_declarations').insert(declaration_data).execute()
                    declarations_created += 1
                    
                except Exception as e:
                    print(f"  ❌ Erreur création déclaration: {e}")
    
    print(f"\n✅ {declarations_created} déclarations TVA créées")

def create_withholding_tax():
    """Crée des retenues à la source (influenceurs)"""
    print("\n💰 Création des retenues à la source...")
    
    users = supabase.table('users').select('id, email, role').eq('role', 'influencer').limit(10).execute()
    if not users.data:
        print("  ⚠️  Aucun influenceur trouvé, utilisation users standards")
        users = supabase.table('users').select('id, email, role').limit(5).execute()
    
    withholding_created = 0
    
    for user in users.data:
        # Créer 2 périodes de retenue
        periods = [
            ('2024-10-01', '2024-10-31'),
            ('2024-11-01', '2024-11-30')
        ]
        
        for period_start, period_end in periods:
            try:
                gross_amount = round(random.uniform(2000, 8000), 2)
                withholding_rate = 10.0  # 10% au Maroc
                withholding_amount = round(gross_amount * withholding_rate / 100, 2)
                net_amount = gross_amount - withholding_amount
                
                data = {
                    'user_id': user['id'],
                    'period_start': period_start,
                    'period_end': period_end,
                    'country': 'MA',
                    'gross_amount': gross_amount,
                    'withholding_rate': withholding_rate,
                    'withholding_amount': withholding_amount,
                    'net_amount': net_amount,
                    'status': random.choice(['paid', 'pending'])
                }
                
                supabase.table('withholding_tax').insert(data).execute()
                withholding_created += 1
                
            except Exception as e:
                print(f"  ❌ Erreur création retenue: {e}")
    
    print(f"\n✅ {withholding_created} retenues à la source créées")

def create_accounting_exports():
    """Crée des exports comptables"""
    print("\n📦 Création des exports comptables...")
    
    users = supabase.table('users').select('id, email').limit(5).execute()
    if not users.data:
        return
    
    exports_created = 0
    
    for user in users.data:
        export_types = ['csv', 'fec', 'sage']
        
        for export_type in export_types:
            try:
                data = {
                    'user_id': user['id'],
                    'export_type': export_type,
                    'country': random.choice(COUNTRIES),
                    'period_start': '2024-01-01',
                    'period_end': '2024-12-31',
                    'file_name': f'export_{export_type}_2024_{random.randint(1000, 9999)}.{export_type}'
                }
                
                supabase.table('accounting_exports').insert(data).execute()
                exports_created += 1
                
            except Exception as e:
                print(f"  ❌ Erreur création export: {e}")
    
    print(f"\n✅ {exports_created} exports comptables créés")

def show_stats():
    """Affiche les statistiques finales"""
    print("\n" + "="*60)
    print("📊 STATISTIQUES DES DONNÉES DE TEST")
    print("="*60)
    
    try:
        stats = {
            'fiscal_settings': supabase.table('fiscal_settings').select('id', count='exact').execute(),
            'vat_rates': supabase.table('vat_rates').select('id', count='exact').execute(),
            'fiscal_invoices': supabase.table('fiscal_invoices').select('id', count='exact').execute(),
            'fiscal_invoice_lines': supabase.table('fiscal_invoice_lines').select('id', count='exact').execute(),
            'vat_declarations': supabase.table('vat_declarations').select('id', count='exact').execute(),
            'withholding_tax': supabase.table('withholding_tax').select('id', count='exact').execute(),
            'accounting_exports': supabase.table('accounting_exports').select('id', count='exact').execute(),
        }
        
        print(f"\n📋 Configurations fiscales: {stats['fiscal_settings'].count}")
        print(f"💰 Taux de TVA: {stats['vat_rates'].count}")
        print(f"📄 Factures fiscales: {stats['fiscal_invoices'].count}")
        print(f"📝 Lignes de facture: {stats['fiscal_invoice_lines'].count}")
        print(f"📊 Déclarations TVA: {stats['vat_declarations'].count}")
        print(f"💸 Retenues à la source: {stats['withholding_tax'].count}")
        print(f"📦 Exports comptables: {stats['accounting_exports'].count}")
        
        # Montants totaux des factures
        invoices = supabase.table('fiscal_invoices').select('amount_ttc, status, country').execute()
        if invoices.data:
            total_ttc = sum(float(inv['amount_ttc'] or 0) for inv in invoices.data)
            paid = sum(float(inv['amount_ttc'] or 0) for inv in invoices.data if inv['status'] == 'paid')
            
            print(f"\n💵 Montant total factures: {total_ttc:,.2f}")
            print(f"✅ Montant payé: {paid:,.2f}")
            print(f"⏳ Montant en attente: {total_ttc - paid:,.2f}")
            
            # Par pays
            print("\n🌍 Répartition par pays:")
            for country in COUNTRIES:
                country_invoices = [inv for inv in invoices.data if inv['country'] == country]
                country_total = sum(float(inv['amount_ttc'] or 0) for inv in country_invoices)
                print(f"  {country}: {len(country_invoices)} factures - {country_total:,.2f} {CURRENCIES[country]}")
        
    except Exception as e:
        print(f"❌ Erreur récupération stats: {e}")
    
    print("\n" + "="*60)

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🚀 GÉNÉRATION DES DONNÉES DE TEST SYSTÈME FISCAL")
    print("="*60)
    
    try:
        # Vérifier la connexion Supabase
        print("\n🔗 Vérification connexion Supabase...")
        test = supabase.table('users').select('id').limit(1).execute()
        print("  ✅ Connexion Supabase OK")
        
        # Créer les données
        create_fiscal_settings()
        create_invoices(count=30)
        create_vat_declarations()
        create_withholding_tax()
        create_accounting_exports()
        
        # Afficher les stats
        show_stats()
        
        print("\n" + "="*60)
        print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
        print("="*60)
        print("\n💡 Le système fiscal est maintenant prêt avec des données de test réalistes")
        print("🌐 Vous pouvez démarrer le backend et tester les dashboards fiscaux\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
