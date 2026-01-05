import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

/**
 * ThemeToggle - Bouton de changement de thème
 *
 * Features:
 * - 3 modes: Light, Dark, System
 * - Animation fluide
 * - Icône dynamique
 * - Tooltip
 */
const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  const getIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun size={20} />;
      case 'dark':
        return <Moon size={20} />;
      case 'system':
        return <Monitor size={20} />;
      default:
        return <Sun size={20} />;
    }
  };

  const getLabel = () => {
    switch (theme) {
      case 'light':
        return 'Mode clair';
      case 'dark':
        return 'Mode sombre';
      case 'system':
        return 'Mode système';
      default:
        return 'Changer le thème';
    }
  };

  return (
    <button
      onClick={toggleTheme}
      className={`relative p-2 rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 ${className}`}
      title={getLabel()}
      aria-label={getLabel()}
    >
      <div className="flex items-center justify-center">
        {getIcon()}
      </div>
    </button>
  );
};

export default ThemeToggle;
