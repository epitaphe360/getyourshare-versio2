import React from 'react';
import { Lock } from 'lucide-react';

const DashboardCard = ({ title, icon, children, className = '', locked = false, onUnlock, action }) => (
  <div className={`bg-white rounded-lg shadow-sm p-6 relative ${className}`}>
    {locked && (
      <div className="absolute inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
        <div className="text-center text-white">
          <Lock size={48} className="mx-auto mb-3" />
          <p className="font-bold text-lg">Fonctionnalité Premium</p>
          <button 
            onClick={onUnlock}
            className="mt-3 bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg font-semibold transition"
          >
            Débloquer
          </button>
        </div>
      </div>
    )}
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
      {action && <div>{action}</div>}
    </div>
    {children}
  </div>
);

export default DashboardCard;
