import React, { useState } from 'react';
import api from '../../services/api';
import { motion } from 'framer-motion';

const ROICalculatorForm = () => {
  const [formData, setFormData] = useState({
    industry: 'fashion',
    average_order_value: 50,
    monthly_traffic: 10000,
    conversion_rate: 2.0
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const industries = [
    { value: 'fashion', label: 'Mode & Accessoires' },
    { value: 'beauty', label: 'Beauté & Cosmétiques' },
    { value: 'tech', label: 'High-Tech & Gadgets' },
    { value: 'home', label: 'Maison & Déco' },
    { value: 'services', label: 'Services en ligne' },
    { value: 'other', label: 'Autre' }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'industry' ? value : parseFloat(value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/roi/calculate', formData);
      setResults(response.data);
    } catch (err) {
      console.error('ROI Calculation Error:', err);
      setError('Une erreur est survenue lors du calcul. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800">Calculateur de ROI</h2>
        <p className="text-gray-600 mt-2">Découvrez combien vous pouvez gagner avec ShareYourSales</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form Section */}
        <div className="space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Secteur d'activité</label>
              <select
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {industries.map(ind => (
                  <option key={ind.value} value={ind.value}>{ind.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Panier Moyen (€)</label>
              <input
                type="number"
                name="average_order_value"
                value={formData.average_order_value}
                onChange={handleChange}
                min="1"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trafic Mensuel (visiteurs)</label>
              <input
                type="number"
                name="monthly_traffic"
                value={formData.monthly_traffic}
                onChange={handleChange}
                min="100"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Taux de Conversion Actuel (%)</label>
              <input
                type="number"
                name="conversion_rate"
                value={formData.conversion_rate}
                onChange={handleChange}
                step="0.1"
                min="0.1"
                max="100"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-6 text-white font-semibold rounded-lg shadow-md transition duration-300 ${
                loading ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
            >
              {loading ? 'Calcul en cours...' : 'Calculer mon Potentiel'}
            </button>
          </form>
          
          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg border border-red-200">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 flex flex-col justify-center">
          {!results ? (
            <div className="text-center text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p>Remplissez le formulaire pour voir vos projections de revenus.</p>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="space-y-6"
            >
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-600">Revenu Mensuel Potentiel</h3>
                <p className="text-4xl font-bold text-green-600 mt-2">
                  {new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(results.potential_revenue)}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-center">
                  <p className="text-sm text-gray-500">ROI Multiplier</p>
                  <p className="text-2xl font-bold text-indigo-600">x{results.roi_multiplier}</p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-center">
                  <p className="text-sm text-gray-500">Plan Recommandé</p>
                  <p className="text-xl font-bold text-indigo-600 capitalize">{results.recommended_tier}</p>
                </div>
              </div>

              <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100">
                <h4 className="font-semibold text-indigo-800 mb-2">Pourquoi ce résultat ?</h4>
                <p className="text-sm text-indigo-700">
                  Basé sur les performances moyennes de nos marchands dans le secteur <strong>{industries.find(i => i.value === formData.industry)?.label}</strong>.
                </p>
              </div>
              
              <div className="text-center mt-4">
                <a href="/register" className="inline-block text-indigo-600 font-medium hover:text-indigo-800 underline">
                  Commencer maintenant &rarr;
                </a>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ROICalculatorForm;
