import React from 'react';
import { Share2 } from 'lucide-react';

const PremiumLoader = ({ message = 'Chargement...' }) => (
  <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950">
    <div className="flex flex-col items-center gap-6">
      {/* Animated logo */}
      <div className="relative">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25 animate-pulse">
          <Share2 className="w-8 h-8 text-white" />
        </div>
        {/* Glow ring */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 opacity-20 animate-ping" />
      </div>

      {/* Loading bar */}
      <div className="w-48 h-1 bg-surface-200 dark:bg-surface-800 rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-primary-500 via-accent-500 to-primary-500 rounded-full animate-shimmer" style={{ width: '60%' }} />
      </div>

      <span className="text-sm font-medium text-surface-500 dark:text-surface-400">{message}</span>
    </div>
  </div>
);

export default PremiumLoader;
