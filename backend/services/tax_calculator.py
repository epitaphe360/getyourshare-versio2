"""
Module de calcul fiscal pour Maroc, France et USA
Gère TVA, IR, retenues à la source et formulaires fiscaux
"""

from datetime import datetime, date
from typing import Dict, Optional, List
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass


class Country(Enum):
    MOROCCO = "MA"
    FRANCE = "FR"
    USA = "US"


class TaxStatus(Enum):
    AUTO_ENTREPRENEUR = "auto_entrepreneur"
    COMPANY = "company"
    INDIVIDUAL = "individual"
    MICRO_ENTERPRISE = "micro_enterprise"  # France
    SARL = "sarl"
    SAS = "sas"
    LLC = "llc"  # USA
    SOLE_PROPRIETOR = "sole_proprietor"


@dataclass
class TaxProfile:
    """Profil fiscal d'un utilisateur"""
    user_id: str
    country: Country
    status: TaxStatus
    tax_id: Optional[str] = None  # ICE (MA), SIRET (FR), EIN/SSN (US)
    vat_number: Optional[str] = None
    vat_exempt: bool = False
    withholding_exempt: bool = False
    created_at: datetime = None


@dataclass
class TaxCalculation:
    """Résultat d'un calcul fiscal"""
    gross_amount: Decimal
    net_amount: Decimal
    vat_amount: Decimal
    vat_rate: Decimal
    withholding_amount: Decimal
    withholding_rate: Decimal
    social_charges: Decimal
    social_rate: Decimal
    total_taxes: Decimal
    currency: str
    breakdown: Dict


class MoroccoTaxCalculator:
    """
    Calculateur fiscal pour le Maroc
    - TVA: 20% (standard), 14%, 10%, 7%, 0%
    - Retenue à la source: 10% sur prestations de services
    - IR Auto-entrepreneur: 0.5% à 2% selon CA
    - Seuil auto-entrepreneur: 500,000 MAD/an
    """
    
    VAT_RATES = {
        'standard': Decimal('0.20'),
        'reduced_14': Decimal('0.14'),
        'reduced_10': Decimal('0.10'),
        'reduced_7': Decimal('0.07'),
        'zero': Decimal('0.00'),
    }
    
    WITHHOLDING_RATE = Decimal('0.10')  # 10% sur prestations de services
    AUTO_ENTREPRENEUR_THRESHOLD = Decimal('500000')  # 500,000 MAD/an
    
    # Taux IR auto-entrepreneur selon activité
    IR_RATES = {
        'services': Decimal('0.02'),  # 2% pour services
        'commerce': Decimal('0.01'),  # 1% pour commerce
        'artisanat': Decimal('0.005'),  # 0.5% pour artisanat
    }
    
    def __init__(self):
        self.currency = "MAD"
    
    def calculate_vat(self, amount: Decimal, rate_type: str = 'standard') -> Dict:
        """Calcule la TVA marocaine"""
        rate = self.VAT_RATES.get(rate_type, self.VAT_RATES['standard'])
        vat_amount = (amount * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return {
            'base_amount': amount,
            'vat_rate': rate,
            'vat_amount': vat_amount,
            'total_ttc': amount + vat_amount
        }
    
    def calculate_withholding(self, amount: Decimal, is_exempt: bool = False) -> Dict:
        """Calcule la retenue à la source (10%)"""
        if is_exempt:
            return {
                'gross_amount': amount,
                'withholding_rate': Decimal('0'),
                'withholding_amount': Decimal('0'),
                'net_amount': amount
            }
        
        withholding = (amount * self.WITHHOLDING_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return {
            'gross_amount': amount,
            'withholding_rate': self.WITHHOLDING_RATE,
            'withholding_amount': withholding,
            'net_amount': amount - withholding
        }
    
    def calculate_auto_entrepreneur_tax(self, revenue: Decimal, activity_type: str = 'services') -> Dict:
        """Calcule l'IR pour auto-entrepreneur"""
        rate = self.IR_RATES.get(activity_type, self.IR_RATES['services'])
        tax = (revenue * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        exceeds_threshold = revenue > self.AUTO_ENTREPRENEUR_THRESHOLD
        
        return {
            'revenue': revenue,
            'activity_type': activity_type,
            'tax_rate': rate,
            'tax_amount': tax,
            'net_after_tax': revenue - tax,
            'exceeds_threshold': exceeds_threshold,
            'threshold': self.AUTO_ENTREPRENEUR_THRESHOLD,
            'warning': "Vous dépassez le seuil auto-entrepreneur. Consultez un comptable." if exceeds_threshold else None
        }
    
    def generate_invoice_requirements(self) -> Dict:
        """Retourne les mentions obligatoires pour une facture marocaine"""
        return {
            'required_fields': [
                'Raison sociale / Nom',
                'Adresse complète',
                'ICE (Identifiant Commun de l\'Entreprise)',
                'IF (Identifiant Fiscal)',
                'RC (Registre de Commerce)',
                'Numéro de facture',
                'Date de facture',
                'Désignation des services',
                'Montant HT',
                'Taux TVA',
                'Montant TVA',
                'Montant TTC',
                'Mode de paiement'
            ],
            'optional_fields': [
                'CNSS (si applicable)',
                'Patente',
                'Numéro de compte bancaire'
            ],
            'notes': [
                'La TVA doit être détaillée par taux si plusieurs taux appliqués',
                'Mention "Exonéré de TVA" si applicable avec référence légale'
            ]
        }


class FranceTaxCalculator:
    """
    Calculateur fiscal pour la France
    - TVA: 20% (standard), 10%, 5.5%, 2.1%
    - Micro-entreprise: Franchise TVA si CA < 34,400€ (services)
    - Cotisations sociales: ~22% pour micro-entreprise
    - Prélèvement libératoire: 2.2% (BNC) ou 1.7% (BIC)
    """
    
    VAT_RATES = {
        'standard': Decimal('0.20'),
        'intermediate': Decimal('0.10'),
        'reduced': Decimal('0.055'),
        'super_reduced': Decimal('0.021'),
    }
    
    # Seuils franchise TVA 2024
    VAT_THRESHOLDS = {
        'services': Decimal('34400'),
        'commerce': Decimal('85800'),
    }
    
    # Cotisations sociales micro-entreprise
    SOCIAL_CHARGES = {
        'bnc': Decimal('0.22'),  # Prestations de services BNC
        'bic_services': Decimal('0.22'),  # Prestations de services BIC
        'bic_commerce': Decimal('0.128'),  # Achat/revente
    }
    
    # Versement libératoire IR
    LIBERATORY_RATES = {
        'bnc': Decimal('0.022'),  # 2.2% pour BNC
        'bic_services': Decimal('0.017'),  # 1.7% pour BIC services
        'bic_commerce': Decimal('0.01'),  # 1% pour commerce
    }
    
    def __init__(self):
        self.currency = "EUR"
    
    def calculate_vat(self, amount: Decimal, rate_type: str = 'standard', 
                      is_franchise: bool = False) -> Dict:
        """Calcule la TVA française"""
        if is_franchise:
            return {
                'base_amount': amount,
                'vat_rate': Decimal('0'),
                'vat_amount': Decimal('0'),
                'total_ttc': amount,
                'mention': 'TVA non applicable, art. 293 B du CGI'
            }
        
        rate = self.VAT_RATES.get(rate_type, self.VAT_RATES['standard'])
        vat_amount = (amount * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return {
            'base_amount': amount,
            'vat_rate': rate,
            'vat_amount': vat_amount,
            'total_ttc': amount + vat_amount,
            'mention': None
        }
    
    def check_vat_franchise(self, annual_revenue: Decimal, activity_type: str = 'services') -> Dict:
        """Vérifie l'éligibilité à la franchise de TVA"""
        threshold = self.VAT_THRESHOLDS.get(activity_type, self.VAT_THRESHOLDS['services'])
        is_eligible = annual_revenue <= threshold
        
        return {
            'annual_revenue': annual_revenue,
            'threshold': threshold,
            'is_eligible': is_eligible,
            'message': 'Franchise de TVA applicable' if is_eligible else 'TVA obligatoire'
        }
    
    def calculate_micro_enterprise_charges(self, revenue: Decimal, 
                                           activity_type: str = 'bnc',
                                           liberatory_payment: bool = False) -> Dict:
        """Calcule les charges pour micro-entreprise"""
        social_rate = self.SOCIAL_CHARGES.get(activity_type, self.SOCIAL_CHARGES['bnc'])
        social_charges = (revenue * social_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        ir_amount = Decimal('0')
        if liberatory_payment:
            ir_rate = self.LIBERATORY_RATES.get(activity_type, self.LIBERATORY_RATES['bnc'])
            ir_amount = (revenue * ir_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        total_charges = social_charges + ir_amount
        net = revenue - total_charges
        
        return {
            'gross_revenue': revenue,
            'social_charges': social_charges,
            'social_rate': social_rate,
            'ir_amount': ir_amount,
            'ir_rate': self.LIBERATORY_RATES.get(activity_type, Decimal('0')) if liberatory_payment else Decimal('0'),
            'total_charges': total_charges,
            'net_income': net,
            'effective_rate': (total_charges / revenue * 100).quantize(Decimal('0.01')) if revenue > 0 else Decimal('0')
        }
    
    def calculate_urssaf_declaration(self, monthly_revenue: Decimal, 
                                     activity_type: str = 'bnc') -> Dict:
        """Prépare la déclaration URSSAF mensuelle/trimestrielle"""
        charges = self.calculate_micro_enterprise_charges(monthly_revenue, activity_type)
        
        return {
            'period': datetime.now().strftime('%B %Y'),
            'revenue_declared': monthly_revenue,
            'cotisations_due': charges['social_charges'],
            'payment_deadline': self._get_urssaf_deadline(),
            'declaration_url': 'https://www.autoentrepreneur.urssaf.fr'
        }
    
    def _get_urssaf_deadline(self) -> str:
        """Retourne la date limite de déclaration URSSAF"""
        today = date.today()
        # Fin du mois suivant généralement
        if today.month == 12:
            deadline = date(today.year + 1, 1, 31)
        else:
            deadline = date(today.year, today.month + 1, 28)
        return deadline.strftime('%d/%m/%Y')
    
    def generate_invoice_requirements(self) -> Dict:
        """Retourne les mentions obligatoires pour une facture française"""
        return {
            'required_fields': [
                'Numéro SIRET',
                'Numéro de TVA intracommunautaire (si assujetti)',
                'Raison sociale et forme juridique',
                'Adresse du siège social',
                'Numéro de facture (chronologique)',
                'Date d\'émission',
                'Date de prestation',
                'Désignation précise des services',
                'Quantité et prix unitaire HT',
                'Taux de TVA applicable',
                'Montant total HT, TVA et TTC',
                'Date d\'échéance de paiement',
                'Conditions de paiement',
                'Taux de pénalités de retard',
                'Indemnité forfaitaire de recouvrement (40€)'
            ],
            'micro_enterprise_mentions': [
                'TVA non applicable, art. 293 B du CGI',
                'Dispensé d\'immatriculation au RCS (si applicable)'
            ],
            'notes': [
                'Conservation obligatoire: 10 ans',
                'Numérotation chronologique sans rupture'
            ]
        }


class USATaxCalculator:
    """
    Calculateur fiscal pour les États-Unis
    - Pas de TVA fédérale (Sales Tax par État)
    - Formulaire W-9 obligatoire
    - 1099-NEC si revenus > $600
    - Backup Withholding: 24% si pas de W-9
    - Self-employment tax: 15.3%
    - Quarterly estimated taxes
    """
    
    SELF_EMPLOYMENT_TAX_RATE = Decimal('0.153')  # 15.3% (Social Security + Medicare)
    BACKUP_WITHHOLDING_RATE = Decimal('0.24')  # 24%
    FORM_1099_THRESHOLD = Decimal('600')  # $600
    
    # Sales Tax par État (exemples)
    STATE_SALES_TAX = {
        'CA': Decimal('0.0725'),
        'TX': Decimal('0.0625'),
        'NY': Decimal('0.04'),
        'FL': Decimal('0.06'),
        'WA': Decimal('0.065'),
        'OR': Decimal('0'),  # Pas de sales tax
        'MT': Decimal('0'),
        'NH': Decimal('0'),
        'DE': Decimal('0'),
        'AK': Decimal('0'),
    }
    
    # Tranches d'impôt fédéral 2024 (Single)
    FEDERAL_TAX_BRACKETS = [
        (Decimal('11600'), Decimal('0.10')),
        (Decimal('47150'), Decimal('0.12')),
        (Decimal('100525'), Decimal('0.22')),
        (Decimal('191950'), Decimal('0.24')),
        (Decimal('243725'), Decimal('0.32')),
        (Decimal('609350'), Decimal('0.35')),
        (Decimal('999999999'), Decimal('0.37')),
    ]
    
    def __init__(self):
        self.currency = "USD"
    
    def calculate_self_employment_tax(self, net_income: Decimal) -> Dict:
        """Calcule la self-employment tax (Social Security + Medicare)"""
        # 92.35% du net est soumis à SE tax
        taxable_income = net_income * Decimal('0.9235')
        se_tax = (taxable_income * self.SELF_EMPLOYMENT_TAX_RATE).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Déduction de 50% de la SE tax
        se_deduction = se_tax / 2
        
        return {
            'net_income': net_income,
            'taxable_se_income': taxable_income,
            'se_tax': se_tax,
            'se_deduction': se_deduction,
            'social_security_portion': (taxable_income * Decimal('0.124')).quantize(Decimal('0.01')),
            'medicare_portion': (taxable_income * Decimal('0.029')).quantize(Decimal('0.01'))
        }
    
    def calculate_backup_withholding(self, amount: Decimal, has_w9: bool = True) -> Dict:
        """Calcule le backup withholding si pas de W-9"""
        if has_w9:
            return {
                'gross_amount': amount,
                'withholding_rate': Decimal('0'),
                'withholding_amount': Decimal('0'),
                'net_amount': amount,
                'w9_status': 'Valid'
            }
        
        withholding = (amount * self.BACKUP_WITHHOLDING_RATE).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        return {
            'gross_amount': amount,
            'withholding_rate': self.BACKUP_WITHHOLDING_RATE,
            'withholding_amount': withholding,
            'net_amount': amount - withholding,
            'w9_status': 'Missing - Backup withholding applied'
        }
    
    def check_1099_requirement(self, annual_payments: Decimal) -> Dict:
        """Vérifie si un 1099-NEC est requis"""
        requires_1099 = annual_payments >= self.FORM_1099_THRESHOLD
        
        return {
            'annual_payments': annual_payments,
            'threshold': self.FORM_1099_THRESHOLD,
            'requires_1099': requires_1099,
            'form_type': '1099-NEC',
            'deadline': 'January 31st of following year',
            'message': 'Form 1099-NEC required' if requires_1099 else 'No 1099 required'
        }
    
    def calculate_quarterly_estimate(self, annual_income: Decimal, 
                                     filing_status: str = 'single') -> Dict:
        """Calcule les paiements trimestriels estimés"""
        se_calc = self.calculate_self_employment_tax(annual_income)
        
        # Calcul simplifié de l'impôt fédéral
        taxable_income = annual_income - se_calc['se_deduction']
        federal_tax = self._calculate_federal_tax(taxable_income)
        
        total_tax = se_calc['se_tax'] + federal_tax
        quarterly_payment = (total_tax / 4).quantize(Decimal('0.01'))
        
        return {
            'annual_income': annual_income,
            'se_tax': se_calc['se_tax'],
            'federal_tax': federal_tax,
            'total_estimated_tax': total_tax,
            'quarterly_payment': quarterly_payment,
            'due_dates': [
                'April 15',
                'June 15',
                'September 15',
                'January 15 (following year)'
            ]
        }
    
    def _calculate_federal_tax(self, taxable_income: Decimal) -> Decimal:
        """Calcule l'impôt fédéral selon les tranches"""
        tax = Decimal('0')
        remaining = taxable_income
        prev_bracket = Decimal('0')
        
        for bracket_limit, rate in self.FEDERAL_TAX_BRACKETS:
            if remaining <= 0:
                break
            
            bracket_income = min(remaining, bracket_limit - prev_bracket)
            tax += bracket_income * rate
            remaining -= bracket_income
            prev_bracket = bracket_limit
        
        return tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_state_sales_tax(self, state: str) -> Decimal:
        """Retourne le taux de sales tax pour un État"""
        return self.STATE_SALES_TAX.get(state.upper(), Decimal('0'))
    
    def generate_w9_requirements(self) -> Dict:
        """Retourne les informations requises pour le W-9"""
        return {
            'form': 'W-9',
            'full_name': 'Request for Taxpayer Identification Number and Certification',
            'required_fields': [
                'Legal name',
                'Business name (if different)',
                'Federal tax classification',
                'Exemptions (if any)',
                'Address',
                'TIN (SSN or EIN)',
                'Signature and date'
            ],
            'purpose': 'Required before any payment to avoid 24% backup withholding',
            'deadline': 'Before first payment',
            'retention': 'Keep on file for 4 years'
        }
    
    def generate_invoice_requirements(self) -> Dict:
        """Retourne les éléments recommandés pour une invoice US"""
        return {
            'required_fields': [
                'Your business name and address',
                'Client name and address',
                'Invoice number',
                'Invoice date',
                'Description of services',
                'Amount due',
                'Payment terms',
                'Payment methods accepted'
            ],
            'recommended_fields': [
                'Your EIN or SSN (for tax purposes)',
                'Due date',
                'Late payment terms',
                'Itemized breakdown'
            ],
            'notes': [
                'No VAT/GST in USA (only state sales tax if applicable)',
                'Keep records for 7 years (IRS recommendation)'
            ]
        }


class UnifiedTaxCalculator:
    """Calculateur fiscal unifié pour tous les pays"""
    
    def __init__(self):
        self.calculators = {
            Country.MOROCCO: MoroccoTaxCalculator(),
            Country.FRANCE: FranceTaxCalculator(),
            Country.USA: USATaxCalculator(),
        }
    
    def get_calculator(self, country: Country):
        """Retourne le calculateur pour un pays donné"""
        return self.calculators.get(country)
    
    def calculate_full_tax(self, profile: TaxProfile, gross_amount: Decimal, 
                           options: Dict = None) -> TaxCalculation:
        """Calcul fiscal complet selon le profil"""
        options = options or {}
        calculator = self.get_calculator(profile.country)
        
        if profile.country == Country.MOROCCO:
            return self._calculate_morocco_tax(calculator, profile, gross_amount, options)
        elif profile.country == Country.FRANCE:
            return self._calculate_france_tax(calculator, profile, gross_amount, options)
        elif profile.country == Country.USA:
            return self._calculate_usa_tax(calculator, profile, gross_amount, options)
        
        raise ValueError(f"Pays non supporté: {profile.country}")
    
    def _calculate_morocco_tax(self, calc: MoroccoTaxCalculator, profile: TaxProfile,
                                amount: Decimal, options: Dict) -> TaxCalculation:
        vat_result = calc.calculate_vat(amount, options.get('vat_type', 'standard'))
        withholding = calc.calculate_withholding(amount, profile.withholding_exempt)
        
        if profile.status == TaxStatus.AUTO_ENTREPRENEUR:
            ir_result = calc.calculate_auto_entrepreneur_tax(amount, options.get('activity', 'services'))
            social = ir_result['tax_amount']
        else:
            social = Decimal('0')
        
        total_taxes = vat_result['vat_amount'] + withholding['withholding_amount'] + social
        
        return TaxCalculation(
            gross_amount=amount,
            net_amount=amount - total_taxes,
            vat_amount=vat_result['vat_amount'],
            vat_rate=vat_result['vat_rate'],
            withholding_amount=withholding['withholding_amount'],
            withholding_rate=withholding['withholding_rate'],
            social_charges=social,
            social_rate=Decimal('0.02') if profile.status == TaxStatus.AUTO_ENTREPRENEUR else Decimal('0'),
            total_taxes=total_taxes,
            currency="MAD",
            breakdown={
                'vat': vat_result,
                'withholding': withholding,
                'ir': ir_result if profile.status == TaxStatus.AUTO_ENTREPRENEUR else None
            }
        )
    
    def _calculate_france_tax(self, calc: FranceTaxCalculator, profile: TaxProfile,
                               amount: Decimal, options: Dict) -> TaxCalculation:
        is_franchise = profile.vat_exempt or options.get('franchise_tva', False)
        vat_result = calc.calculate_vat(amount, options.get('vat_type', 'standard'), is_franchise)
        
        if profile.status == TaxStatus.MICRO_ENTERPRISE:
            charges = calc.calculate_micro_enterprise_charges(
                amount, 
                options.get('activity', 'bnc'),
                options.get('liberatory', False)
            )
            social = charges['social_charges']
            social_rate = charges['social_rate']
        else:
            social = Decimal('0')
            social_rate = Decimal('0')
        
        total_taxes = vat_result['vat_amount'] + social
        
        return TaxCalculation(
            gross_amount=amount,
            net_amount=amount - total_taxes,
            vat_amount=vat_result['vat_amount'],
            vat_rate=vat_result['vat_rate'],
            withholding_amount=Decimal('0'),
            withholding_rate=Decimal('0'),
            social_charges=social,
            social_rate=social_rate,
            total_taxes=total_taxes,
            currency="EUR",
            breakdown={
                'vat': vat_result,
                'social': charges if profile.status == TaxStatus.MICRO_ENTERPRISE else None
            }
        )
    
    def _calculate_usa_tax(self, calc: USATaxCalculator, profile: TaxProfile,
                            amount: Decimal, options: Dict) -> TaxCalculation:
        has_w9 = profile.tax_id is not None
        withholding = calc.calculate_backup_withholding(amount, has_w9)
        
        if profile.status in [TaxStatus.SOLE_PROPRIETOR, TaxStatus.LLC]:
            se_tax = calc.calculate_self_employment_tax(amount)
            social = se_tax['se_tax']
        else:
            social = Decimal('0')
        
        state = options.get('state', 'CA')
        sales_tax_rate = calc.get_state_sales_tax(state)
        
        total_taxes = withholding['withholding_amount'] + social
        
        return TaxCalculation(
            gross_amount=amount,
            net_amount=amount - total_taxes,
            vat_amount=Decimal('0'),  # Pas de VAT aux USA
            vat_rate=Decimal('0'),
            withholding_amount=withholding['withholding_amount'],
            withholding_rate=withholding['withholding_rate'],
            social_charges=social,
            social_rate=calc.SELF_EMPLOYMENT_TAX_RATE if social > 0 else Decimal('0'),
            total_taxes=total_taxes,
            currency="USD",
            breakdown={
                'backup_withholding': withholding,
                'self_employment': se_tax if profile.status in [TaxStatus.SOLE_PROPRIETOR, TaxStatus.LLC] else None,
                'state_sales_tax_rate': sales_tax_rate
            }
        )
    
    def get_annual_summary(self, profile: TaxProfile, transactions: List[Dict]) -> Dict:
        """Génère un résumé fiscal annuel"""
        total_gross = sum(Decimal(str(t.get('amount', 0))) for t in transactions)
        total_vat = sum(Decimal(str(t.get('vat', 0))) for t in transactions)
        total_withholding = sum(Decimal(str(t.get('withholding', 0))) for t in transactions)
        
        calculator = self.get_calculator(profile.country)
        
        summary = {
            'year': datetime.now().year,
            'country': profile.country.value,
            'total_gross_revenue': float(total_gross),
            'total_vat_collected': float(total_vat),
            'total_withholding': float(total_withholding),
            'transaction_count': len(transactions),
            'currency': calculator.currency,
        }
        
        # Ajout des spécificités par pays
        if profile.country == Country.MOROCCO:
            summary['ice'] = profile.tax_id
            summary['auto_entrepreneur_threshold'] = float(MoroccoTaxCalculator.AUTO_ENTREPRENEUR_THRESHOLD)
            summary['exceeds_threshold'] = total_gross > MoroccoTaxCalculator.AUTO_ENTREPRENEUR_THRESHOLD
            
        elif profile.country == Country.FRANCE:
            summary['siret'] = profile.tax_id
            franchise_check = calculator.check_vat_franchise(total_gross)
            summary['vat_franchise_eligible'] = franchise_check['is_eligible']
            
        elif profile.country == Country.USA:
            summary['ein_ssn'] = profile.tax_id
            form_1099_check = calculator.check_1099_requirement(total_gross)
            summary['requires_1099'] = form_1099_check['requires_1099']
            quarterly = calculator.calculate_quarterly_estimate(total_gross)
            summary['estimated_quarterly_tax'] = float(quarterly['quarterly_payment'])
        
        return summary
