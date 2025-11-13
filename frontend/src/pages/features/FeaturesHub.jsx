import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ReferralDashboard,
  ProductRecommendations,
  ContentStudio,
  LiveShoppingStudio
} from '../../components/features';
import { useAuth } from '../../context/AuthContext';
import { Users, Sparkles, Wand2, Video } from 'lucide-react';

const FeaturesHub = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('referral');

  const tabs = [
    {
      id: 'referral',
      name: 'Programme Parrainage',
      icon: Users,
      component: ReferralDashboard,
      color: 'purple',
      description: 'Gagne jusqu\'à 10% sur les ventes de tes filleuls'
    },
    {
      id: 'recommendations',
      name: 'Produits Recommandés',
      icon: Sparkles,
      component: ProductRecommendations,
      color: 'blue',
      description: 'Découvre les produits parfaits pour ton audience'
    },
    {
      id: 'content',
      name: 'Content Studio IA',
      icon: Wand2,
      component: ContentStudio,
      color: 'indigo',
      description: 'Génère du contenu optimisé en quelques secondes'
    },
    {
      id: 'live',
      name: 'Live Shopping',
      icon: Video,
      component: LiveShoppingStudio,
      color: 'red',
      description: 'Booste tes ventes en direct avec +5% de commission'
    }
  ];

  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component;

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-2">
            🚀 Features Hub
          </h1>
          <p className="text-gray-600">
            Accède à toutes les fonctionnalités pour booster tes ventes
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg p-2 mb-6 overflow-x-auto">
          <div className="flex gap-2 min-w-max">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 min-w-[200px] px-4 py-3 rounded-lg transition ${
                    activeTab === tab.id
                      ? `bg-${tab.color}-600 text-white shadow-md`
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.name}</span>
                  </div>
                  {activeTab === tab.id && (
                    <p className="text-xs opacity-90">{tab.description}</p>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {ActiveComponent && <ActiveComponent userId={user?.id} />}
        </motion.div>
      </div>
    </div>
  );
};

export default FeaturesHub;
