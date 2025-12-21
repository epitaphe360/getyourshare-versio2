import React from 'react';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import { TrendingUp } from 'lucide-react';

const StatCard = ({ title, value, icon, trend, trendValue, delay = 0, isCurrency = false, suffix = '' }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className="bg-white rounded-lg shadow-sm p-6"
  >
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <p className="text-sm text-gray-600 mb-1">{title}</p>
        <div className="text-2xl font-bold text-gray-800">
          {typeof value === 'number' ? (
            <CountUp
              end={value}
              duration={2.5}
              decimals={isCurrency ? 2 : 0}
              separator=" "
              suffix={suffix}
              prefix={isCurrency ? '' : ''}
            />
          ) : (
            value
          )}
          {isCurrency && ' €'}
        </div>
        {trend && (
          <div className={`flex items-center mt-2 text-sm ${trendValue >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            <TrendingUp size={16} className="mr-1" />
            <span>{trendValue >= 0 ? '+' : ''}{trendValue}%</span>
            <span className="text-gray-500 ml-2">vs mois dernier</span>
          </div>
        )}
      </div>
      <div className="ml-4">{icon}</div>
    </div>
  </motion.div>
);

export default StatCard;
