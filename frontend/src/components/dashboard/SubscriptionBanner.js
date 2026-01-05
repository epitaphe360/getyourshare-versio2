import React from 'react';
import { motion } from 'framer-motion';

const SubscriptionBanner = ({ tier, stats }) => {
  const config = {
    starter: {
      color: 'from-orange-500 to-pink-500',
      icon: '🌱',
      title: 'STARTER',
      message: `Vous avez utilisé ${stats?.leads_generated_month || 0}/10 leads ce mois`,
      cta: '🚀 Passer à PRO - 29€/mois',
      benefits: ['10 leads/mois', '3 liens trackés', '3 templates']
    },
    pro: {
      color: 'from-purple-600 to-blue-600',
      icon: '⚡',
      title: 'PRO',
      message: 'Tous les outils professionnels débloqués',
      benefits: ['Leads illimités', 'CRM avancé', '15 templates', 'Kit marketing']
    },
    enterprise: {
      color: 'from-yellow-500 to-amber-600',
      icon: '👑',
      title: 'ENTERPRISE',
      message: 'Accès Total + IA + Automation',
      benefits: ['Tout illimité', 'IA suggestions', 'Automation complète', 'Support dédié']
    }
  };

  const currentConfig = config[tier] || config.starter;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`bg-gradient-to-r ${currentConfig.color} rounded-xl p-6 mb-6 shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <span className="text-3xl mr-3">{currentConfig.icon}</span>
            <h2 className="text-2xl font-bold text-white">Abonnement {currentConfig.title}</h2>
          </div>
          <p className="text-white text-lg mb-3">{currentConfig.message}</p>
          <div className="flex flex-wrap gap-2">
            {currentConfig.benefits.map((benefit, idx) => (
              <span key={idx} className="bg-white bg-opacity-20 text-white px-3 py-1 rounded-full text-sm">
                ✓ {benefit}
              </span>
            ))}
          </div>
        </div>
        {tier === 'starter' && (
          <button 
            onClick={() => window.location.href = '/subscription/plans'}
            className="bg-white text-orange-600 hover:bg-gray-100 px-8 py-3 rounded-lg font-bold text-lg transition transform hover:scale-105 shadow-lg"
          >
            {currentConfig.cta}
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default SubscriptionBanner;
