import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { motion } from 'framer-motion';

const ReferralDashboard = () => {
  const [referralData, setReferralData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchReferralData();
  }, []);

  const fetchReferralData = async () => {
    try {
      // Try to get stats, which might include the code if it exists
      // If the backend requires a code to exist for stats, we might need to handle 404
      const response = await api.get('/api/referrals/stats');
      
      // Map backend response to frontend expected structure
      const data = response.data;
      const formattedData = {
        ...data,
        referral_code: data.code,
        referral_url: data.code ? `https://getyourshare.com/register?ref=${data.code}` : null,
        total_earned: data.total_earnings,
        conversion_rate: data.total_referrals > 0 ? ((data.active_referrals / data.total_referrals) * 100).toFixed(1) : 0
      };
      
      setReferralData(formattedData);
    } catch (err) {
      // If 404, it might mean no code exists yet. 
      // But usually stats endpoint should return empty stats if no referrals.
      // Let's assume if it fails, we might need to generate a code or just show error.
      console.error('Error fetching referral data:', err);
      // If the error is that no code exists, we can set data to null to show "Generate" button
      if (err.response && err.response.status === 404) {
        setReferralData(null);
      } else {
        setError('Impossible de charger les données de parrainage.');
      }
    } finally {
      setLoading(false);
    }
  };

  const generateCode = async () => {
    setGenerating(true);
    setError(null);
    try {
      const response = await api.post('/api/referrals/generate-code');
      // After generating, fetch stats again or use response if it returns the code
      // The backend returns { "code": ..., "share_link": ... }
      setReferralData({
        ...referralData,
        referral_code: response.data.code,
        referral_url: response.data.share_link,
        total_referrals: 0,
        total_earned: 0,
        conversion_rate: 0
      });
    } catch (err) {
      console.error('Error generating code:', err);
      setError('Erreur lors de la génération du code.');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (referralData?.referral_url) {
      navigator.clipboard.writeText(referralData.referral_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return <div className="p-4 text-center">Chargement du programme de parrainage...</div>;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800">Programme de Parrainage</h3>
        <p className="text-sm text-gray-500">Invitez des amis et gagnez des commissions.</p>
      </div>

      <div className="p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {!referralData?.referral_code ? (
          <div className="text-center py-8">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-indigo-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">Commencez à parrainer</h4>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Générez votre lien unique et partagez-le pour gagner des récompenses sur chaque nouvel inscrit.
            </p>
            <button
              onClick={generateCode}
              disabled={generating}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {generating ? 'Génération...' : 'Générer mon lien de parrainage'}
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Link Section */}
            <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-100">
              <label className="block text-sm font-medium text-indigo-900 mb-2">Votre lien de parrainage</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  readOnly
                  value={referralData.referral_url}
                  className="flex-1 px-4 py-2 border border-indigo-200 rounded-lg bg-white text-gray-600 focus:outline-none"
                />
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      Copié
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                      </svg>
                      Copier
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm"
              >
                <p className="text-sm text-gray-500">Total Parrainages</p>
                <p className="text-2xl font-bold text-gray-900">{referralData.total_referrals}</p>
              </motion.div>
              
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm"
              >
                <p className="text-sm text-gray-500">Gains Totaux</p>
                <p className="text-2xl font-bold text-green-600">
                  {new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(referralData.total_earned)}
                </p>
              </motion.div>

              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm"
              >
                <p className="text-sm text-gray-500">Taux de Conversion</p>
                <p className="text-2xl font-bold text-indigo-600">{referralData.conversion_rate}%</p>
              </motion.div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReferralDashboard;
