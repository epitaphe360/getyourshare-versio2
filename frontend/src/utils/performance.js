/**
 * Performance Optimization Utilities
 * Target: Lighthouse 98-100/100
 */

/**
 * 1. RESOURCE HINTS
 * Preload, prefetch, dns-prefetch for critical resources
 */
export const addResourceHints = () => {
  // DNS Prefetch for external domains
  const dnsPrefetchDomains = [
    'https://api.getyourshare.ma',
    'https://cdn.getyourshare.ma',
    'https://fonts.googleapis.com',
    'https://fonts.gstatic.com',
    'https://www.googletagmanager.com',
    'https://www.google-analytics.com'
  ];

  dnsPrefetchDomains.forEach(domain => {
    const link = document.createElement('link');
    link.rel = 'dns-prefetch';
    link.href = domain;
    document.head.appendChild(link);
  });

  // Preconnect for critical origins
  const preconnectOrigins = [
    'https://api.getyourshare.ma',
    'https://fonts.googleapis.com'
  ];

  preconnectOrigins.forEach(origin => {
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = origin;
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
};

/**
 * 2. IMAGE LAZY LOADING
 * Progressive image loading with blur-up effect
 */
export class LazyImageLoader {
  constructor() {
    this.observer = null;
    this.init();
  }

  init() {
    if ('IntersectionObserver' in window) {
      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              this.loadImage(entry.target);
              this.observer.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: '50px 0px', // Start loading 50px before viewport
          threshold: 0.01
        }
      );
    }
  }

  loadImage(img) {
    const src = img.dataset.src;
    const srcset = img.dataset.srcset;

    if (!src) return;

    // Create a new image to preload
    const tempImg = new Image();

    tempImg.onload = () => {
      // Remove blur placeholder
      img.classList.remove('blur-load');
      img.classList.add('blur-loaded');

      // Set actual image
      if (srcset) img.srcset = srcset;
      img.src = src;

      // Remove data attributes
      delete img.dataset.src;
      delete img.dataset.srcset;
    };

    tempImg.src = src;
  }

  observe(elements) {
    if (!this.observer) {
      // Fallback for browsers without IntersectionObserver
      elements.forEach(el => this.loadImage(el));
      return;
    }

    elements.forEach(el => this.observer.observe(el));
  }

  disconnect() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}

/**
 * 3. WEB VITALS MONITORING
 * Track Core Web Vitals (LCP, FID, CLS)
 * NOTE: Disabled to avoid import errors
 */
export const initWebVitals = async () => {
  if ('web-vital' in window) return;

  try {
    // Import web-vitals dynamically with better error handling
    const webVitalsModule = await import('web-vitals').catch(() => null);
    
    // If web-vitals is not available, skip silently
    if (!webVitalsModule) {
      window['web-vital'] = true; // Mark as attempted
      return;
    }

    const { getCLS, getFID, getFCP, getLCP, getTTFB } = webVitalsModule;
    
    // Verify all functions are available
    if (!getCLS || !getFID || !getFCP || !getLCP || !getTTFB) {
      window['web-vital'] = true;
      return;
    }

    const sendToAnalytics = (metric) => {
      // Send to analytics endpoint
      const body = JSON.stringify({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        delta: metric.delta,
        id: metric.id,
        navigationType: metric.navigationType
      });

      // Use sendBeacon for reliable delivery
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/analytics/web-vitals', body);
      } else {
        fetch('/api/analytics/web-vitals', {
          body,
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          keepalive: true
        }).catch(console.error);
      }
    };

    // Monitor all Core Web Vitals
    getCLS(sendToAnalytics);
    getFID(sendToAnalytics);
    getFCP(sendToAnalytics);
    getLCP(sendToAnalytics);
    getTTFB(sendToAnalytics);

    window['web-vital'] = true;
  } catch (error) {
    // Silently mark as attempted to avoid repeated errors
    window['web-vital'] = true;
  }
};

/**
 * 4. FONT LOADING OPTIMIZATION
 * FOIT/FOUT prevention with font-display
 */
export const optimizeFonts = () => {
  // Add font-display: swap to Google Fonts
  const fontLinks = document.querySelectorAll('link[href*="fonts.googleapis.com"]');

  fontLinks.forEach(link => {
    const url = new URL(link.href);
    if (!url.searchParams.has('display')) {
      url.searchParams.set('display', 'swap');
      link.href = url.toString();
    }
  });

  // Preload critical fonts
  // Note: Font preloading disabled - add fonts to /public/fonts/ directory to enable
  // const criticalFonts = [
  //   '/fonts/inter-var.woff2'
  // ];

  // criticalFonts.forEach(font => {
  //   const link = document.createElement('link');
  //   link.rel = 'preload';
  //   link.as = 'font';
  //   link.type = 'font/woff2';
  //   link.href = font;
  //   link.crossOrigin = 'anonymous';
  //   document.head.appendChild(link);
  // });
};

/**
 * 5. REDUCE JAVASCRIPT EXECUTION TIME
 * Code splitting and lazy loading utilities
 */
export const deferNonCriticalJS = () => {
  // Defer non-critical scripts
  const scripts = document.querySelectorAll('script[data-defer]');

  scripts.forEach(script => {
    if (script.src) {
      script.defer = true;
    }
  });

  // Load analytics after page load
  if (document.readyState === 'complete') {
    loadAnalytics();
  } else {
    window.addEventListener('load', loadAnalytics);
  }
};

const loadAnalytics = () => {
  // Defer Google Analytics
  setTimeout(() => {
    if (window.gtag) return;

    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function() { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'GA_MEASUREMENT_ID');
  }, 3000); // Load after 3 seconds
};

/**
 * 6. CUMULATIVE LAYOUT SHIFT (CLS) PREVENTION
 * Reserve space for dynamic content
 */
export const preventCLS = () => {
  // Add aspect ratio boxes for images
  const images = document.querySelectorAll('img:not([width]):not([height])');

  images.forEach(img => {
    if (img.naturalWidth && img.naturalHeight) {
      const aspectRatio = (img.naturalHeight / img.naturalWidth) * 100;
      img.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`;
    }
  });

  // Reserve space for ads/embeds
  const dynamicContainers = document.querySelectorAll('[data-dynamic-height]');

  dynamicContainers.forEach(container => {
    const height = container.dataset.dynamicHeight;
    container.style.minHeight = height;
  });
};

/**
 * 7. THIRD-PARTY SCRIPT OPTIMIZATION
 * Load third-party scripts efficiently
 */
export const optimizeThirdPartyScripts = () => {
  // Use facade pattern for heavy embeds
  const embedContainers = document.querySelectorAll('[data-embed-src]');

  embedContainers.forEach(container => {
    const embedSrc = container.dataset.embedSrc;
    const embedType = container.dataset.embedType;

    // Show placeholder with "Click to load" button
    const placeholder = document.createElement('div');
    placeholder.className = 'embed-placeholder';

    // Create button safely without innerHTML to prevent XSS
    const button = document.createElement('button');
    button.textContent = `Load ${embedType || 'content'}`;

    button.addEventListener('click', () => {
      const iframe = document.createElement('iframe');
      iframe.src = embedSrc;
      iframe.loading = 'lazy';
      container.appendChild(iframe);
      placeholder.remove();
    });

    placeholder.appendChild(button);
    container.appendChild(placeholder);
  });
};

/**
 * 8. PERFORMANCE BUDGET MONITOR
 * Track bundle size and warn if exceeded
 */
export const checkPerformanceBudget = () => {
  if (!performance.getEntriesByType) return;

  const resources = performance.getEntriesByType('resource');

  const budgets = {
    'script': 500 * 1024,      // 500 KB max for JS
    'stylesheet': 100 * 1024,  // 100 KB max for CSS
    'image': 2 * 1024 * 1024   // 2 MB max for images
  };

  const usage = {
    script: 0,
    stylesheet: 0,
    image: 0
  };

  resources.forEach(resource => {
    const type = resource.initiatorType;
    const size = resource.transferSize || 0;

    if (type in usage) {
      usage[type] += size;
    }
  });

  // Check budgets
  Object.keys(budgets).forEach(type => {
    if (usage[type] > budgets[type]) {
      console.warn(
        `⚠️ Performance budget exceeded for ${type}: ` +
        `${(usage[type] / 1024).toFixed(2)} KB / ${(budgets[type] / 1024).toFixed(2)} KB`
      );
    }
  });

  return usage;
};

/**
 * 9. INITIALIZE ALL OPTIMIZATIONS
 * Main entry point
 */
export const initPerformanceOptimizations = () => {
  // Run immediately
  addResourceHints();
  optimizeFonts();

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      preventCLS();
      deferNonCriticalJS();
      optimizeThirdPartyScripts();
    });
  } else {
    preventCLS();
    deferNonCriticalJS();
    optimizeThirdPartyScripts();
  }

  // Run after page load
  window.addEventListener('load', () => {
    initWebVitals();
    checkPerformanceBudget();

    // Initialize lazy image loader
    const lazyLoader = new LazyImageLoader();
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyLoader.observe(lazyImages);
  });
};

/**
 * 10. PRELOAD CRITICAL RESOURCES
 * Preload above-the-fold resources
 */
export const preloadCriticalResources = () => {
  const criticalResources = [
    // Preload the actual logo file that exists
    { href: '/logo.png', as: 'image', type: 'image/png' }
    // Note: Additional resources can be added here when they become available:
    // - Add fonts to /public/fonts/ directory
    // - Add API endpoints only if they exist and are used immediately on page load
  ];

  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    Object.keys(resource).forEach(key => {
      link[key] = resource[key];
    });
    document.head.appendChild(link);
  });
};

// Export singleton instance
export default {
  init: initPerformanceOptimizations,
  preload: preloadCriticalResources,
  LazyImageLoader,
  checkBudget: checkPerformanceBudget
};
