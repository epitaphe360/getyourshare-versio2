import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import './ThemeToggle.css';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`theme-toggle ${className}`}
      aria-label={`Passer en mode ${isDark ? 'clair' : 'sombre'}`}
      title={`Mode ${isDark ? 'clair' : 'sombre'}`}
    >
      <div className="theme-toggle-icon">
        {isDark ? (
          <Sun size={20} className="theme-icon sun-icon" />
        ) : (
          <Moon size={20} className="theme-icon moon-icon" />
        )}
      </div>
      <span className="theme-toggle-label">
        {isDark ? 'Clair' : 'Sombre'}
      </span>
    </button>
  );
};

export default ThemeToggle;
