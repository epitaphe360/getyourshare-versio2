import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import {
  Calculator, Receipt, FileText, Globe, TrendingUp,
  DollarSign, Percent, AlertTriangle, CheckCircle,
  ChevronDown, RefreshCw, Download, Calendar,
  Building2, Wallet, PieChart, BarChart3, X, FileCheck, Clock
} from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const TaxDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState('FR');
  const [selectedStatus, setSelectedStatus] = useState('micro_enterprise');
  const [amount, setAmount] = useState(1000);
  const [taxResult, setTaxResult] = useState(null);
  const [countries, setCountries] = useState([]);
  const [taxRates, setTaxRates] = useState(null);
  const [annualRevenue, setAnnualRevenue] = useState(50000);
  const [activeModal, setActiveModal] = useState(null);

  const openModal = (modalName) => setActiveModal(modalName);
  const closeModal = () => setActiveModal(null);

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    if (selectedCountry) {
      fetchTaxRates();
    }
  }, [selectedCountry]);

  const fetchCountries = async () => {
    try {
      const response = await axios.get(`${API_URL}/fiscal/countries`);
      setCountries(response.data.countries);
    } catch (error) {
      console.error('Error fetching countries:', error);
    }
  };

  const fetchTaxRates = async () => {
    try {
      const response = await axios.get(`${API_URL}/fiscal/rates/${selectedCountry}`);
      setTaxRates(response.data);
    } catch (error) {
      console.error('Error fetching tax rates:', error);
    }
  };

  const calculateTax = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/fiscal/calculate`, {
        amount: amount,
        country: selectedCountry,
        status: selectedStatus,
        vat_exempt: false,
        withholding_exempt: false,
        options: {
          activity: 'services'
        }
      });
      setTaxResult(response.data);
    } catch (error) {
      console.error('Error calculating tax:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCountryFlag = (code) => {
    const flags = { MA: '🇲🇦', FR: '🇫🇷', US: '🇺🇸' };
    return flags[code] || '🌍';
  };

  const getStatusOptions = () => {
    switch (selectedCountry) {
      case 'MA':
        return [
          { value: 'auto_entrepreneur', label: 'Auto-Entrepreneur' },
          { value: 'company', label: 'Société (SARL/SA)' },
          { value: 'individual', label: 'Particulier' }
        ];
      case 'FR':
        return [
          { value: 'micro_enterprise', label: 'Micro-Entreprise' },
          { value: 'auto_entrepreneur', label: 'Auto-Entrepreneur' },
          { value: 'company', label: 'Société (SAS/SARL)' }
        ];
      case 'US':
        return [
          { value: 'sole_proprietor', label: 'Sole Proprietor' },
          { value: 'llc', label: 'LLC' },
          { value: 'company', label: 'Corporation' }
        ];
      default:
        return [];
    }
  };

  const getCurrencySymbol = () => {
    switch (selectedCountry) {
      case 'MA': return 'DH';
      case 'FR': return '€';
      case 'US': return '$';
      default: return '€';
    }
  };

  return (
    <div className="space-y-6 p-1">
      {/* Header */}
      <div className="relative overflow-hidden bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-600 rounded-2xl p-8 text-white">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                <Calculator size={28} />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Centre Fiscal</h1>
                <p className="text-white/80 mt-1">Calculs fiscaux et déclarations pour Maroc, France & USA</p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2.5 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl transition-all">
              <Download size={18} />
              <span className="hidden sm:inline">Exporter</span>
            </button>
            <button className="flex items-center gap-2 px-5 py-2.5 bg-white text-emerald-600 font-semibold rounded-xl hover:bg-white/90 transition-all shadow-lg shadow-black/20">
              <FileText size={20} />
              <span>Nouvelle Facture</span>
            </button>
          </div>
        </div>
      </div>

      {/* Country Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {countries.map((country) => (
          <button
            key={country.code}
            onClick={() => setSelectedCountry(country.code)}
            className={`p-5 rounded-xl border-2 transition-all ${
              selectedCountry === country.code
                ? 'border-emerald-500 bg-emerald-50 shadow-lg'
                : 'border-gray-200 bg-white hover:border-emerald-300'
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="text-4xl">{getCountryFlag(country.code)}</span>
              <div className="text-left">
                <h3 className="font-semibold text-gray-900">{country.name}</h3>
                <p className="text-sm text-gray-500">{country.currency}</p>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              {country.features.slice(0, 2).map((feature, idx) => (
                <span key={idx} className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                  {feature}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculator Card */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Calculator className="text-emerald-600" size={24} />
            Calculateur Fiscal
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Amount */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant Brut ({getCurrencySymbol()})
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Statut Fiscal
              </label>
              <div className="relative">
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full appearance-none pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer"
                >
                  {getStatusOptions().map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={18} />
              </div>
            </div>
          </div>

          <button
            onClick={calculateTax}
            disabled={loading}
            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 text-white py-4 rounded-xl font-semibold hover:from-emerald-700 hover:to-teal-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="animate-spin" size={20} />
                Calcul en cours...
              </>
            ) : (
              <>
                <Calculator size={20} />
                Calculer les Taxes
              </>
            )}
          </button>

          {/* Results */}
          {taxResult && (
            <div className="mt-6 space-y-4">
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-semibold text-emerald-900">Résultat du Calcul</h3>
                  <span className="text-sm text-emerald-600">{taxResult.currency}</span>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b border-emerald-200">
                    <span className="text-gray-600">Montant Brut</span>
                    <span className="font-semibold">{taxResult.gross_amount.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                  </div>

                  {taxResult.vat_amount > 0 && (
                    <div className="flex justify-between py-2 border-b border-emerald-200">
                      <span className="text-gray-600">TVA ({(taxResult.vat_rate * 100).toFixed(0)}%)</span>
                      <span className="text-red-600">-{taxResult.vat_amount.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                    </div>
                  )}

                  {taxResult.withholding_amount > 0 && (
                    <div className="flex justify-between py-2 border-b border-emerald-200">
                      <span className="text-gray-600">Retenue à la source ({(taxResult.withholding_rate * 100).toFixed(0)}%)</span>
                      <span className="text-red-600">-{taxResult.withholding_amount.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                    </div>
                  )}

                  {taxResult.social_charges > 0 && (
                    <div className="flex justify-between py-2 border-b border-emerald-200">
                      <span className="text-gray-600">Cotisations Sociales ({(taxResult.social_rate * 100).toFixed(1)}%)</span>
                      <span className="text-red-600">-{taxResult.social_charges.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                    </div>
                  )}

                  <div className="flex justify-between py-3 bg-emerald-100 rounded-lg px-4 mt-4">
                    <span className="font-bold text-emerald-900">Montant Net</span>
                    <span className="text-2xl font-bold text-emerald-700">{taxResult.net_amount.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                  </div>

                  <div className="flex justify-between py-2">
                    <span className="text-gray-600">Total des Taxes</span>
                    <span className="font-semibold text-red-600">{taxResult.total_taxes.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} {getCurrencySymbol()}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Tax Rates Reference */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Percent className="text-emerald-600" size={24} />
            Taux en Vigueur
          </h2>

          {taxRates && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">{getCountryFlag(selectedCountry)}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{taxRates.country}</h3>
                  <p className="text-sm text-gray-500">{taxRates.currency}</p>
                </div>
              </div>

              {/* VAT Rates */}
              {taxRates.vat && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase mb-3">TVA</h4>
                  <div className="space-y-2">
                    {Object.entries(taxRates.vat).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="font-semibold text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Auto-entrepreneur / Micro-enterprise */}
              {taxRates.auto_entrepreneur && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase mb-3">Auto-Entrepreneur</h4>
                  <div className="space-y-2">
                    {Object.entries(taxRates.auto_entrepreneur).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="font-semibold text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {taxRates.micro_enterprise && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase mb-3">Micro-Entreprise</h4>
                  <div className="space-y-2">
                    {Object.entries(taxRates.micro_enterprise).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                        <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="font-semibold text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* USA specific */}
              {taxRates.self_employment_tax && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase mb-3">Self-Employment</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Self-Employment Tax</span>
                      <span className="font-semibold text-gray-900">{taxRates.self_employment_tax}</span>
                    </div>
                    <div className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">Backup Withholding</span>
                      <span className="font-semibold text-gray-900">{taxRates.backup_withholding}</span>
                    </div>
                    <div className="flex justify-between py-2 px-3 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">1099 Threshold</span>
                      <span className="font-semibold text-gray-900">{taxRates.form_1099_threshold}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Withholding (Morocco) */}
              {taxRates.withholding && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase mb-3">Retenue à la Source</h4>
                  <div className="space-y-2">
                    {Object.entries(taxRates.withholding).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-2 px-3 bg-amber-50 rounded-lg">
                        <span className="text-gray-600 capitalize">{key}</span>
                        <span className="font-semibold text-amber-700">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <button 
          onClick={() => openModal('invoice')}
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-emerald-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-emerald-100 rounded-xl group-hover:bg-emerald-200 transition">
              <Receipt className="text-emerald-600" size={24} />
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Générer Facture</h3>
              <p className="text-sm text-gray-500">Créer une facture conforme</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => openModal('report')}
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-xl group-hover:bg-blue-200 transition">
              <BarChart3 className="text-blue-600" size={24} />
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Rapport Annuel</h3>
              <p className="text-sm text-gray-500">Résumé fiscal complet</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => openModal('calendar')}
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-100 rounded-xl group-hover:bg-purple-200 transition">
              <Calendar className="text-purple-600" size={24} />
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Échéances</h3>
              <p className="text-sm text-gray-500">Calendrier fiscal</p>
            </div>
          </div>
        </button>

        <button 
          onClick={() => openModal('documents')}
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all group"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-orange-100 rounded-xl group-hover:bg-orange-200 transition">
              <FileText className="text-orange-600" size={24} />
            </div>
            <div className="text-left">
              <h3 className="font-semibold text-gray-900">Documents</h3>
              <p className="text-sm text-gray-500">W-9, déclarations...</p>
            </div>
          </div>
        </button>
      </div>

      {/* Alerts & Tips */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {selectedCountry === 'MA' && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
            <div className="flex gap-3">
              <AlertTriangle className="text-amber-600 flex-shrink-0" size={24} />
              <div>
                <h4 className="font-semibold text-amber-900">Retenue à la Source</h4>
                <p className="text-sm text-amber-700 mt-1">
                  Au Maroc, une retenue de 10% s'applique sur les prestations de services. 
                  Assurez-vous d'avoir votre attestation de régularité fiscale.
                </p>
              </div>
            </div>
          </div>
        )}

        {selectedCountry === 'FR' && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <div className="flex gap-3">
              <CheckCircle className="text-blue-600 flex-shrink-0" size={24} />
              <div>
                <h4 className="font-semibold text-blue-900">Franchise de TVA</h4>
                <p className="text-sm text-blue-700 mt-1">
                  En dessous de 34 400€/an de CA (services), vous pouvez bénéficier de la franchise de TVA.
                  Mention obligatoire: "TVA non applicable, art. 293 B du CGI"
                </p>
              </div>
            </div>
          </div>
        )}

        {selectedCountry === 'US' && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <div className="flex gap-3">
              <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
              <div>
                <h4 className="font-semibold text-red-900">Formulaire W-9 Obligatoire</h4>
                <p className="text-sm text-red-700 mt-1">
                  Sans W-9 valide, une retenue de 24% (backup withholding) sera appliquée.
                  Un 1099-NEC est requis pour tout paiement supérieur à $600/an.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5">
          <div className="flex gap-3">
            <CheckCircle className="text-emerald-600 flex-shrink-0" size={24} />
            <div>
              <h4 className="font-semibold text-emerald-900">Conseil Fiscal</h4>
              <p className="text-sm text-emerald-700 mt-1">
                Conservez toutes vos factures pendant au moins 10 ans (France) ou 7 ans (USA).
                Utilisez notre générateur de factures pour être conforme.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {activeModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white z-10">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                {activeModal === 'invoice' && <><Receipt className="text-emerald-600" /> Générer une Facture</>}
                {activeModal === 'report' && <><BarChart3 className="text-blue-600" /> Rapport Fiscal Annuel</>}
                {activeModal === 'calendar' && <><Calendar className="text-purple-600" /> Calendrier Fiscal</>}
                {activeModal === 'documents' && <><FileText className="text-orange-600" /> Documents & Justificatifs</>}
              </h3>
              <button onClick={closeModal} className="p-2 hover:bg-gray-100 rounded-full transition">
                <X size={24} className="text-gray-500" />
              </button>
            </div>
            
            <div className="p-6">
              {activeModal === 'invoice' && renderInvoiceContent()}
              {activeModal === 'report' && renderReportContent()}
              {activeModal === 'calendar' && renderCalendarContent()}
              {activeModal === 'documents' && renderDocumentsContent()}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  function renderInvoiceContent() {
    return (
      <div className="space-y-4">
        <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-200 mb-4">
          <p className="text-emerald-800 text-sm">
            Générez une facture conforme aux normes de votre pays ({selectedCountry}).
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Client</label>
            <input type="text" className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="Nom du client" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input type="date" className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" defaultValue={new Date().toISOString().split('T')[0]} />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" rows="3" placeholder="Description des services..."></textarea>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Montant HT</label>
            <input type="number" className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" placeholder="0.00" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">TVA (%)</label>
            <input type="number" className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" defaultValue="20" />
          </div>
        </div>
        <button className="w-full bg-emerald-600 text-white py-3 rounded-lg font-semibold hover:bg-emerald-700 transition mt-4 flex items-center justify-center gap-2">
          <Download size={20} />
          Télécharger la Facture (PDF)
        </button>
      </div>
    );
  }

  function renderReportContent() {
    return (
      <div className="space-y-6">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-2">Résumé Annuel 2025</h4>
          <p className="text-blue-700 text-sm">
            Basé sur vos revenus déclarés et les taux en vigueur pour {selectedCountry}.
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-500">Chiffre d'Affaires</p>
            <p className="text-2xl font-bold text-gray-900">{annualRevenue.toLocaleString()} {getCurrencySymbol()}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-500">Taxes Estimées</p>
            <p className="text-2xl font-bold text-red-600">{(annualRevenue * 0.22).toLocaleString()} {getCurrencySymbol()}</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="font-semibold mb-3">Détail par Trimestre</h4>
          <div className="space-y-2">
            {[1, 2, 3, 4].map(q => (
              <div key={q} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded-lg transition">
                <span className="font-medium">Trimestre {q}</span>
                <span className="text-gray-600">{(annualRevenue / 4).toLocaleString()} {getCurrencySymbol()}</span>
              </div>
            ))}
          </div>
        </div>
        
        <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2">
          <Download size={20} />
          Télécharger le Rapport Complet
        </button>
      </div>
    );
  }

  function renderCalendarContent() {
    const events = {
      FR: [
        { date: '15 Janvier', title: 'Déclaration TVA Mensuelle', type: 'urgent' },
        { date: '31 Janvier', title: 'Paiement CFE (Solde)', type: 'normal' },
        { date: '15 Mai', title: 'Déclaration Impôt sur le Revenu', type: 'important' }
      ],
      US: [
        { date: 'Jan 15', title: 'Q4 Estimated Tax Payment', type: 'urgent' },
        { date: 'Apr 15', title: 'Federal Tax Return (1040)', type: 'important' },
        { date: 'Jun 15', title: 'Q2 Estimated Tax Payment', type: 'normal' }
      ],
      MA: [
        { date: '31 Janvier', title: 'Déclaration Trimestrielle T4', type: 'urgent' },
        { date: '28 Février', title: 'Déclaration Annuelle', type: 'important' },
        { date: '30 Avril', title: 'Déclaration Trimestrielle T1', type: 'normal' }
      ]
    };

    const countryEvents = events[selectedCountry] || events['FR'];

    return (
      <div className="space-y-4">
        {countryEvents.map((event, idx) => (
          <div key={idx} className="flex items-center gap-4 p-4 border border-gray-100 rounded-xl hover:shadow-sm transition">
            <div className={`p-3 rounded-lg ${
              event.type === 'urgent' ? 'bg-red-100 text-red-600' :
              event.type === 'important' ? 'bg-amber-100 text-amber-600' :
              'bg-blue-100 text-blue-600'
            }`}>
              <Clock size={20} />
            </div>
            <div>
              <p className="font-bold text-gray-900">{event.date}</p>
              <p className="text-gray-600">{event.title}</p>
            </div>
            <div className="ml-auto">
              <span className={`text-xs px-2 py-1 rounded-full ${
                event.type === 'urgent' ? 'bg-red-100 text-red-700' :
                event.type === 'important' ? 'bg-amber-100 text-amber-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {event.type === 'urgent' ? 'Urgent' : event.type === 'important' ? 'Important' : 'À venir'}
              </span>
            </div>
          </div>
        ))}
        <button className="w-full mt-4 border border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2">
          <Calendar size={20} />
          Synchroniser avec mon calendrier
        </button>
      </div>
    );
  }

  function renderDocumentsContent() {
    const docs = {
      FR: ['Attestation de Vigilance', 'Avis de Situation Sirene', 'Déclaration CFE', 'Justificatif de Domicile'],
      US: ['Form W-9', 'Form 1099-NEC', 'Schedule C (Form 1040)', 'EIN Confirmation'],
      MA: ['Attestation d\'Inscription Taxe Pro', 'Attestation de Régularité Fiscale', 'Registre de Commerce', 'Statuts de la Société']
    };

    return (
      <div className="space-y-3">
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 mb-4">
          <p className="text-orange-800 text-sm">
            Documents essentiels pour votre statut <strong>{selectedStatus}</strong> en {selectedCountry}.
          </p>
        </div>
        {(docs[selectedCountry] || docs['FR']).map((doc, idx) => (
          <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-white hover:shadow-sm border border-transparent hover:border-gray-200 transition">
            <div className="flex items-center gap-3">
              <FileCheck className="text-gray-400" size={20} />
              <span className="font-medium text-gray-700">{doc}</span>
            </div>
            <button className="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg transition">
              <Download size={18} />
            </button>
          </div>
        ))}
        <div className="mt-6 pt-4 border-t border-gray-100">
          <button className="w-full flex items-center justify-center gap-2 bg-gray-900 text-white py-3 rounded-lg hover:bg-gray-800 transition">
            <Download size={18} />
            Télécharger le Pack Complet (.zip)
          </button>
        </div>
      </div>
    );
  }
};

export default TaxDashboard;
