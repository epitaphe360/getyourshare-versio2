"""
Calculs fiscaux avancés multi-pays
IR progressif Maroc, URSSAF France, State taxes USA
"""

from typing import Dict, List, Tuple
from decimal import Decimal


# ========================================
# MAROC - IR PROGRESSIF (Barème 2024)
# ========================================

MOROCCO_IR_BRACKETS_2024 = [
    {"min": 0, "max": 30000, "rate": 0.00, "deduction": 0},
    {"min": 30001, "max": 50000, "rate": 0.10, "deduction": 3000},
    {"min": 50001, "max": 60000, "rate": 0.20, "deduction": 8000},
    {"min": 60001, "max": 80000, "rate": 0.30, "deduction": 14000},
    {"min": 80001, "max": 180000, "rate": 0.34, "deduction": 17200},
    {"min": 180001, "max": float('inf'), "rate": 0.38, "deduction": 24400}
]


def calculate_morocco_ir(annual_income: float, dependents: int = 0, deductions: float = 0) -> Dict:
    """
    Calcule l'Impôt sur le Revenu Maroc (barème progressif)
    
    Args:
        annual_income: Revenu annuel net imposable (MAD)
        dependents: Nombre de personnes à charge
        deductions: Déductions fiscales (CNSS, CIMR, etc.)
    
    Returns:
        {
            "gross_income": float,
            "taxable_income": float,
            "ir_gross": float,
            "family_deduction": float,
            "ir_net": float,
            "effective_rate": float,
            "bracket_details": list
        }
    """
    
    # Déduction forfaitaire 20% (max 30 000 MAD)
    forfait_deduction = min(annual_income * 0.20, 30000)
    
    # Déductions personnelles (charges sociales, etc.)
    total_deductions = forfait_deduction + deductions
    
    # Revenu net imposable
    taxable_income = max(0, annual_income - total_deductions)
    
    # Calcul IR selon barème
    ir_gross = 0
    bracket_details = []
    
    for bracket in MOROCCO_IR_BRACKETS_2024:
        if taxable_income > bracket["min"]:
            income_in_bracket = min(taxable_income, bracket["max"]) - bracket["min"]
            tax_in_bracket = income_in_bracket * bracket["rate"]
            
            bracket_details.append({
                "bracket": f"{bracket['min']} - {bracket['max']}",
                "rate": f"{bracket['rate']*100}%",
                "income_in_bracket": income_in_bracket,
                "tax": tax_in_bracket
            })
            
            if taxable_income >= bracket["max"]:
                continue
            else:
                break
    
    # Méthode simplifiée avec déduction
    for bracket in MOROCCO_IR_BRACKETS_2024:
        if taxable_income >= bracket["min"] and taxable_income <= bracket["max"]:
            ir_gross = (taxable_income * bracket["rate"]) - bracket["deduction"]
            break
    
    # Déduction pour charges de famille (360 MAD par personne, max 2160 MAD pour 6 personnes)
    family_deduction = min(dependents * 360, 2160)
    
    # IR net à payer
    ir_net = max(0, ir_gross - family_deduction)
    
    # Taux effectif
    effective_rate = (ir_net / annual_income * 100) if annual_income > 0 else 0
    
    return {
        "gross_income": annual_income,
        "forfait_deduction": forfait_deduction,
        "other_deductions": deductions,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "ir_gross": ir_gross,
        "family_deduction": family_deduction,
        "dependents": dependents,
        "ir_net": ir_net,
        "effective_rate": round(effective_rate, 2),
        "bracket_details": bracket_details,
        "currency": "MAD"
    }


def calculate_morocco_professional_tax(annual_income: float, activity_class: str = "A") -> Dict:
    """
    Taxe professionnelle Maroc
    
    Args:
        annual_income: Chiffre d'affaires annuel
        activity_class: Classe d'activité (A, B, C, D selon nature activité)
    
    Returns:
        {
            "annual_tax": float,
            "monthly_tax": float,
            "activity_class": str
        }
    """
    
    # Barème simplifié par classe (montant annuel minimum)
    tax_by_class = {
        "A": 600,   # Activités de vente
        "B": 1200,  # Activités de services
        "C": 2400,  # Activités libérales
        "D": 6000   # Activités financières
    }
    
    base_tax = tax_by_class.get(activity_class, 1200)
    
    # Majoration selon CA (0.5% du CA excédentaire après 5M MAD)
    if annual_income > 5000000:
        additional_tax = (annual_income - 5000000) * 0.005
        total_tax = base_tax + additional_tax
    else:
        total_tax = base_tax
    
    return {
        "annual_tax": total_tax,
        "monthly_tax": total_tax / 12,
        "activity_class": activity_class,
        "currency": "MAD"
    }


# ========================================
# FRANCE - URSSAF & COTISATIONS SOCIALES
# ========================================

FRANCE_URSSAF_RATES_2024 = {
    "auto_entrepreneur_bnc": 0.222,  # Professions libérales
    "auto_entrepreneur_bic_services": 0.222,  # Services commerciaux
    "auto_entrepreneur_bic_commerce": 0.128,  # Achat-revente
    
    "micro_entreprise_bnc": 0.222,
    "micro_entreprise_bic_services": 0.222,
    "micro_entreprise_bic_commerce": 0.128,
    
    # Régime réel - Détail cotisations
    "maladie_maternite": 0.0685,  # 6.85% (déplafonnée)
    "allocations_familiales": 0.031,  # 3.1%
    "csg_crds": 0.097,  # 9.7%
    "retraite_base": 0.1775,  # 17.75% (plafonnée)
    "retraite_complementaire": 0.07,  # 7%
    "invalidite_deces": 0.013,  # 1.3%
    "formation_professionnelle": 0.0025  # 0.25%
}


def calculate_france_urssaf(revenue: float, status: str = "auto_entrepreneur_bnc") -> Dict:
    """
    Calcule cotisations URSSAF France
    
    Args:
        revenue: Chiffre d'affaires ou revenu
        status: auto_entrepreneur_bnc | micro_entreprise_bic_services | etc.
    
    Returns:
        {
            "revenue": float,
            "social_charges": float,
            "rate": float,
            "net_income": float,
            "breakdown": dict
        }
    """
    
    rate = FRANCE_URSSAF_RATES_2024.get(status, 0.222)
    social_charges = revenue * rate
    net_income = revenue - social_charges
    
    # Détail si régime réel
    breakdown = {}
    if "auto_entrepreneur" in status or "micro" in status:
        breakdown = {
            "cotisations_globales": social_charges,
            "rate": f"{rate*100}%"
        }
    else:
        # Régime réel - détail complet
        plafond_ss_2024 = 46368  # Plafond annuel sécurité sociale
        
        assiette_deplaconnee = revenue
        assiette_placonnee = min(revenue, plafond_ss_2024)
        
        breakdown = {
            "maladie_maternite": assiette_deplaconnee * FRANCE_URSSAF_RATES_2024["maladie_maternite"],
            "allocations_familiales": assiette_deplaconnee * FRANCE_URSSAF_RATES_2024["allocations_familiales"],
            "csg_crds": assiette_deplaconnee * FRANCE_URSSAF_RATES_2024["csg_crds"],
            "retraite_base": assiette_placonnee * FRANCE_URSSAF_RATES_2024["retraite_base"],
            "retraite_complementaire": assiette_placonnee * FRANCE_URSSAF_RATES_2024["retraite_complementaire"],
            "invalidite_deces": assiette_placonnee * FRANCE_URSSAF_RATES_2024["invalidite_deces"],
            "formation_pro": revenue * FRANCE_URSSAF_RATES_2024["formation_professionnelle"]
        }
        social_charges = sum(breakdown.values())
        net_income = revenue - social_charges
    
    return {
        "revenue": revenue,
        "social_charges": social_charges,
        "rate": rate,
        "net_income": net_income,
        "breakdown": breakdown,
        "currency": "EUR"
    }


def calculate_france_ir(taxable_income: float, family_quotient: float = 1.0) -> Dict:
    """
    Calcule l'Impôt sur le Revenu France (barème progressif 2024)
    
    Args:
        taxable_income: Revenu net imposable annuel
        family_quotient: Nombre de parts fiscales (1 célibataire, 2 couple, +0.5 par enfant)
    
    Returns:
        {
            "taxable_income": float,
            "family_quotient": float,
            "income_per_part": float,
            "ir_gross": float,
            "ir_net": float,
            "effective_rate": float
        }
    """
    
    # Barème IR France 2024
    brackets = [
        {"max": 11294, "rate": 0.00},
        {"max": 28797, "rate": 0.11},
        {"max": 82341, "rate": 0.30},
        {"max": 177106, "rate": 0.41},
        {"max": float('inf'), "rate": 0.45}
    ]
    
    # Revenu par part
    income_per_part = taxable_income / family_quotient
    
    # Calcul IR par part
    ir_per_part = 0
    previous_max = 0
    
    for bracket in brackets:
        if income_per_part > previous_max:
            taxable_in_bracket = min(income_per_part, bracket["max"]) - previous_max
            ir_per_part += taxable_in_bracket * bracket["rate"]
            previous_max = bracket["max"]
            
            if income_per_part <= bracket["max"]:
                break
    
    # IR total (reconstitué)
    ir_gross = ir_per_part * family_quotient
    
    # Décote (si applicable, couple < 3209€ IR, célibataire < 1929€)
    decote_threshold = 1929 if family_quotient < 2 else 3209
    if ir_gross < decote_threshold:
        decote = (decote_threshold - ir_gross) * 0.75
        ir_net = max(0, ir_gross - decote)
    else:
        ir_net = ir_gross
    
    effective_rate = (ir_net / taxable_income * 100) if taxable_income > 0 else 0
    
    return {
        "taxable_income": taxable_income,
        "family_quotient": family_quotient,
        "income_per_part": income_per_part,
        "ir_gross": ir_gross,
        "ir_net": ir_net,
        "effective_rate": round(effective_rate, 2),
        "currency": "EUR"
    }


# ========================================
# USA - STATE TAXES (50 États)
# ========================================

USA_STATE_TAX_RATES_2024 = {
    # États sans impôt sur le revenu
    "AK": 0.00, "FL": 0.00, "NV": 0.00, "SD": 0.00, "TN": 0.00, "TX": 0.00, "WA": 0.00, "WY": 0.00,
    
    # États avec taux fixe
    "CO": 0.044, "IL": 0.0495, "IN": 0.0305, "KY": 0.045, "MI": 0.0425, "NC": 0.0475, "PA": 0.0307, "UT": 0.0485,
    
    # États avec barème progressif (taux maximum)
    "AL": 0.05, "AR": 0.055, "AZ": 0.045, "CA": 0.133, "CT": 0.0699, "DE": 0.066, "GA": 0.0575,
    "HI": 0.11, "IA": 0.0853, "ID": 0.058, "KS": 0.057, "LA": 0.0425, "MA": 0.05, "MD": 0.0575,
    "ME": 0.0715, "MN": 0.0985, "MO": 0.054, "MS": 0.05, "MT": 0.0675, "NE": 0.0684, "NH": 0.05,
    "NJ": 0.1075, "NM": 0.059, "NY": 0.109, "ND": 0.029, "OH": 0.0399, "OK": 0.05, "OR": 0.099,
    "RI": 0.0599, "SC": 0.07, "VT": 0.0875, "VA": 0.0575, "WI": 0.0765, "WV": 0.065,
    
    # Washington DC
    "DC": 0.1075
}


def calculate_usa_state_tax(federal_taxable_income: float, state: str = "CA") -> Dict:
    """
    Calcule l'impôt d'État USA
    
    Args:
        federal_taxable_income: Revenu imposable fédéral
        state: Code État (CA, NY, TX, etc.)
    
    Returns:
        {
            "state": str,
            "taxable_income": float,
            "state_tax": float,
            "rate": float
        }
    """
    
    rate = USA_STATE_TAX_RATES_2024.get(state.upper(), 0.05)
    state_tax = federal_taxable_income * rate
    
    return {
        "state": state.upper(),
        "taxable_income": federal_taxable_income,
        "state_tax": state_tax,
        "rate": rate,
        "rate_percent": f"{rate*100}%",
        "currency": "USD"
    }


def calculate_usa_federal_tax_2024(taxable_income: float, filing_status: str = "single") -> Dict:
    """
    Calcule l'impôt fédéral USA (barème 2024)
    
    Args:
        taxable_income: Revenu imposable
        filing_status: 'single', 'married_joint', 'married_separate', 'head_of_household'
    
    Returns:
        {
            "taxable_income": float,
            "filing_status": str,
            "federal_tax": float,
            "effective_rate": float,
            "bracket_details": list
        }
    """
    
    # Barèmes 2024
    brackets = {
        "single": [
            {"max": 11600, "rate": 0.10},
            {"max": 47150, "rate": 0.12},
            {"max": 100525, "rate": 0.22},
            {"max": 191950, "rate": 0.24},
            {"max": 243725, "rate": 0.32},
            {"max": 609350, "rate": 0.35},
            {"max": float('inf'), "rate": 0.37}
        ],
        "married_joint": [
            {"max": 23200, "rate": 0.10},
            {"max": 94300, "rate": 0.12},
            {"max": 201050, "rate": 0.22},
            {"max": 383900, "rate": 0.24},
            {"max": 487450, "rate": 0.32},
            {"max": 731200, "rate": 0.35},
            {"max": float('inf'), "rate": 0.37}
        ]
    }
    
    applicable_brackets = brackets.get(filing_status, brackets["single"])
    
    federal_tax = 0
    previous_max = 0
    bracket_details = []
    
    for bracket in applicable_brackets:
        if taxable_income > previous_max:
            taxable_in_bracket = min(taxable_income, bracket["max"]) - previous_max
            tax_in_bracket = taxable_in_bracket * bracket["rate"]
            federal_tax += tax_in_bracket
            
            bracket_details.append({
                "bracket": f"${previous_max:,.0f} - ${bracket['max']:,.0f}",
                "rate": f"{bracket['rate']*100}%",
                "taxable_in_bracket": taxable_in_bracket,
                "tax": tax_in_bracket
            })
            
            previous_max = bracket["max"]
            
            if taxable_income <= bracket["max"]:
                break
    
    effective_rate = (federal_tax / taxable_income * 100) if taxable_income > 0 else 0
    
    return {
        "taxable_income": taxable_income,
        "filing_status": filing_status,
        "federal_tax": federal_tax,
        "effective_rate": round(effective_rate, 2),
        "bracket_details": bracket_details,
        "currency": "USD"
    }


def calculate_usa_self_employment_tax(net_profit: float) -> Dict:
    """
    Calcule Self-Employment Tax USA (Social Security + Medicare)
    
    Args:
        net_profit: Bénéfice net de l'activité
    
    Returns:
        {
            "net_profit": float,
            "se_tax": float,
            "social_security": float,
            "medicare": float
        }
    """
    
    # Plafond Social Security 2024
    ss_wage_base = 160200
    
    # Calcul Social Security (12.4% jusqu'au plafond)
    social_security = min(net_profit, ss_wage_base) * 0.124
    
    # Calcul Medicare (2.9% déplafonné + 0.9% additionnel si > $200k)
    medicare_base = net_profit * 0.029
    medicare_additional = max(0, net_profit - 200000) * 0.009
    medicare = medicare_base + medicare_additional
    
    se_tax = social_security + medicare
    
    # Déduction 50% SE tax pour calcul revenu imposable
    deductible_se_tax = se_tax * 0.50
    
    return {
        "net_profit": net_profit,
        "se_tax": se_tax,
        "social_security": social_security,
        "medicare": medicare,
        "deductible_se_tax": deductible_se_tax,
        "effective_rate": round((se_tax / net_profit * 100), 2) if net_profit > 0 else 0,
        "currency": "USD"
    }


# === EXEMPLE D'UTILISATION ===
if __name__ == "__main__":
    # Test Maroc IR
    morocco_result = calculate_morocco_ir(annual_income=250000, dependents=2, deductions=5000)
    print("=== MAROC IR ===")
    print(f"Revenu brut: {morocco_result['gross_income']} MAD")
    print(f"IR net: {morocco_result['ir_net']} MAD")
    print(f"Taux effectif: {morocco_result['effective_rate']}%\n")
    
    # Test France URSSAF
    france_result = calculate_france_urssaf(revenue=50000, status="auto_entrepreneur_bnc")
    print("=== FRANCE URSSAF ===")
    print(f"CA: {france_result['revenue']} EUR")
    print(f"Cotisations: {france_result['social_charges']} EUR")
    print(f"Net: {france_result['net_income']} EUR\n")
    
    # Test USA State Tax
    usa_state = calculate_usa_state_tax(federal_taxable_income=100000, state="CA")
    print("=== USA STATE TAX (California) ===")
    print(f"Income: ${usa_state['taxable_income']:,.2f}")
    print(f"State Tax: ${usa_state['state_tax']:,.2f}")
    print(f"Rate: {usa_state['rate_percent']}\n")
    
    # Test USA Self-Employment Tax
    usa_se = calculate_usa_self_employment_tax(net_profit=80000)
    print("=== USA SELF-EMPLOYMENT TAX ===")
    print(f"Net Profit: ${usa_se['net_profit']:,.2f}")
    print(f"SE Tax: ${usa_se['se_tax']:,.2f}")
    print(f"Effective Rate: {usa_se['effective_rate']}%")
