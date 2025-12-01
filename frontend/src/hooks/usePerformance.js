/**
 * Performance Monitoring Hook
 * Surveille et supprime les avertissements de performance en développement
 */

import { useEffect } from 'react';

export const usePerformanceMonitor = () => {
  useEffect(() => {
    // Supprimer les warnings de performance si configuré
    if (process.env.REACT_APP_SUPPRESS_PERFORMANCE_WARNINGS === 'true') {
      const originalWarn = console.warn;
      const originalError = console.error;

      console.warn = function filterWarning(...args) {
        const msg = args[0];
        
        // Filtrer les warnings de performance
        if (typeof msg === 'string') {
          if (msg.includes('Performance budget exceeded') ||
              msg.includes('performance.js') ||
              msg.includes('Download the React DevTools')) {
            return; // Ignorer
          }
        }
        
        // Afficher les autres warnings
        originalWarn.apply(console, args);
      };

      console.error = function filterError(...args) {
        const msg = args[0];
        
        // Filtrer certaines erreurs non critiques
        if (typeof msg === 'string') {
          if (msg.includes('Performance budget') ||
              msg.includes('React DevTools')) {
            return; // Ignorer
          }
        }
        
        // Afficher les autres erreurs
        originalError.apply(console, args);
      };

      // Cleanup
      return () => {
        console.warn = originalWarn;
        console.error = originalError;
      };
    }
  }, []);
};

/**
 * Hook pour mesurer les performances d'un composant
 */
export const useComponentPerformance = (componentName) => {
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Log uniquement si le rendu prend plus de 100ms
      if (renderTime > 100 && process.env.NODE_ENV === 'development') {
        console.log(`⏱️ ${componentName} rendered in ${renderTime.toFixed(2)}ms`);
      }
    };
  });
};

/**
 * Hook pour détecter les slow renders
 */
export const useSlowRenderDetection = (threshold = 16.67) => {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'development') return;

    let lastTime = performance.now();

    const detectSlowRender = () => {
      const currentTime = performance.now();
      const frameTime = currentTime - lastTime;

      if (frameTime > threshold) {
        console.warn(`🐌 Slow render detected: ${frameTime.toFixed(2)}ms (threshold: ${threshold}ms)`);
      }

      lastTime = currentTime;
      requestAnimationFrame(detectSlowRender);
    };

    const rafId = requestAnimationFrame(detectSlowRender);

    return () => cancelAnimationFrame(rafId);
  }, [threshold]);
};

export default {
  usePerformanceMonitor,
  useComponentPerformance,
  useSlowRenderDetection
};
