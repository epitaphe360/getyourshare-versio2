import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Gift, Sparkles, Wand2, Video, Calculator } from 'lucide-react';
import Layout from '../../components/layout/Layout';
import { useAuth } from '../../context/AuthContext';
import ReferralDashboard from '../../components/referral/ReferralDashboard';
import AIContentGenerator from '../../components/features/AIContentGenerator';
import ProductRecommendations from '../../components/features/ProductRecommendations';
import LiveShoppingStudio from '../../components/features/LiveShoppingStudio';
import ROICalculatorForm from '../../components/roi/ROICalculatorForm';

const FeaturesHub = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('referral');

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    if (tab) {
      setActiveTab(tab);
    }
  }, [location]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    navigate(`/features?tab=${tab}`);
  };

  const tabs = [
    { id: 'referral', label: 'Parrainage', icon: Gift, color: 'text-purple-600' },
    { id: 'recommendations', label: 'Recommandations IA', icon: Sparkles, color: 'text-indigo-600' },
    { id: 'content', label: 'Content Studio', icon: Wand2, color: 'text-pink-600' },
    { id: 'live', label: 'Live Shopping', icon: Video, color: 'text-red-600' },
    { id: 'roi', label: 'Calculateur ROI', icon: Calculator, color: 'text-green-600' }
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Hub Fonctionnalités</h1>
          <p className="mt-2 text-gray-600">
            Accédez à tous vos outils de croissance et d'intelligence artificielle.
          </p>
        </div>

        {/* Tabs Navigation */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8 overflow-hidden">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors whitespace-nowrap border-b-2 ${
                    isActive
                      ? `border-${tab.color.split('-')[1]}-600 bg-${tab.color.split('-')[1]}-50 ${tab.color}`
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={20} className={isActive ? tab.color : 'text-gray-400'} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Area */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'referral' && <ReferralDashboard />}
          
          {activeTab === 'recommendations' && <ProductRecommendations />}
          
          {activeTab === 'content' && <AIContentGenerator />}
          
          {activeTab === 'live' && <LiveShoppingStudio userId={user?.id} />}

          {activeTab === 'roi' && <ROICalculatorForm />}
        </motion.div>
      </div>
    </Layout>
  );
};

export default FeaturesHub;
