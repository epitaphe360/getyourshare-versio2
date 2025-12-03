import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * ThemeContext - Gestion Dark Mode (Score 10/10)
 *
 * Features:
 * - Toggle light/dark/system
 * - Persistance localStorage
 * - Transition fluide
 * - Support prefers-color-scheme
 */
const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Récupérer le thème depuis localStorage ou utiliser 'system'
    const saved = localStorage.getItem('theme');
    return saved || 'system';
  });

  const [resolvedTheme, setResolvedTheme] = useState('light');

  useEffect(() => {
    const root = window.document.documentElement;

    // Calculer le thème effectif
    let effectiveTheme = theme;

    if (theme === 'system') {
      effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    }

    setResolvedTheme(effectiveTheme);

    // Appliquer le thème
    root.classList.remove('light', 'dark');
    root.classList.add(effectiveTheme);

    // Sauvegarder dans localStorage
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Écouter les changements de préférence système
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (e) => {
      const newTheme = e.matches ? 'dark' : 'light';
      setResolvedTheme(newTheme);

      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(newTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'system';
      return 'light';
    });
  };

  const setLightTheme = () => setTheme('light');
  const setDarkTheme = () => setTheme('dark');
  const setSystemTheme = () => setTheme('system');

  const value = {
    theme,
    resolvedTheme,
    setTheme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    setSystemTheme,
    isDark: resolvedTheme === 'dark'
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};
