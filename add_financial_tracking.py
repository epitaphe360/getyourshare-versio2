#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les appels track_financial_operation
à toutes les opérations de balance dans run_automation_scenario.py
"""

import re
from pathlib import Path

def add_financial_tracking():
    script_path = Path(__file__).parent / "backend" / "run_automation_scenario.py"
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modifications = 0
    
    # Pattern pour détecter les updates de balance
    pattern = r'(supabase\.table\([\'"]users[\'"]\)\.update\(\{[\'"]balance[\'"]: ([^}]+)\}\)\.eq\([\'"]id[\'"], ([^)]+)\)\.execute\(\))'
    
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Détecter update de balance
        if 'supabase.table(\'users\').update({"balance":' in line or 'supabase.table("users").update({"balance":' in line:
            # Analyser le contexte pour déterminer le type d'opération
            context_before = '\n'.join(lines[max(0, i-10):i]).lower()
            context_after = '\n'.join(lines[i:min(len(lines), i+5)]).lower()
            
            # Déjà tracké ?
            if 'track_financial_operation' in context_after:
                continue
            
            # Déterminer le type et catégorie
            op_type = "entrée"
            category = "ventes"
            description = "Opération financière"
            
            if 'abonnement' in context_before or 'subscription' in context_before:
                category = "abonnements"
                description = "Paiement abonnement"
                op_type = "entrée"
            elif 'commercial' in context_before and 'commission' in context_before:
                category = "commissions_commerciales"
                description = "Commission commerciale"
                op_type = "entrée"
            elif 'commission' in context_before and 'influenc' in context_before:
                if '-' in line or 'rembours' in context_before:
                    op_type = "sortie"
                    category = "remboursements"
                    description = "Remboursement commission"
                else:
                    category = "ventes"
                    description = "Commission influenceur"
            elif 'payout' in context_before or 'retrait' in context_before:
                op_type = "sortie"
                category = "retraits"
                description = "Retrait"
            elif 'refund' in context_before or 'rembours' in context_before:
                op_type = "sortie"
                category = "remboursements"
                description = "Remboursement"
            elif 'referral' in context_before or 'parrain' in context_before:
                category = "ventes"
                description = "Bonus parrainage"
            elif 'lead' in context_before:
                category = "ventes"
                description = "Commission lead"
            
            # Extraire le montant et user_id
            match = re.search(r'balance[\'"]:\s*([^}]+)\}', line)
            if match:
                balance_expr = match.group(1).strip()
                
                # Extraire user_id
                user_match = re.search(r"eq\(['\"]id['\"],\s*([^)]+)\)", line)
                if user_match:
                    user_id = user_match.group(1).strip()
                    
                    # Calculer le montant (simplification)
                    if '+' in balance_expr:
                        amount_match = re.search(r'\+\s*([\d.]+)', balance_expr)
                        if amount_match:
                            amount = amount_match.group(1)
                            tracking_line = f'    track_financial_operation("{op_type}", "{category}", {amount}, {user_id}, "{description}")'
                            new_lines.append(tracking_line)
                            modifications += 1
                    elif '-' in balance_expr and op_type == "sortie":
                        amount_match = re.search(r'-\s*([\d.]+)', balance_expr)
                        if amount_match:
                            amount = amount_match.group(1)
                            tracking_line = f'    track_financial_operation("{op_type}", "{category}", {amount}, {user_id}, "{description}")'
                            new_lines.append(tracking_line)
                            modifications += 1
    
    new_content = '\n'.join(new_lines)
    
    if modifications > 0:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {modifications} appels track_financial_operation ajoutés")
        return True
    else:
        print("ℹ️  Aucune modification nécessaire")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🔧 AJOUT AUTOMATIQUE DU TRACKING FINANCIER")
    print("="*60 + "\n")
    
    success = add_financial_tracking()
    
    if success:
        print("\n✅ Modifications appliquées avec succès!")
        print("\n💡 Relancer maintenant:")
        print("   python backend/run_automation_scenario.py")
    else:
        print("\n⚠️  Vérifier manuellement le code")
