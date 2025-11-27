/**
 * Service d'Internationalisation (i18n)
 * Support: Français, Arabe, Darija Marocaine, Anglais
 * Avec RTL (Right-to-Left) pour arabe
 */

import { logger } from '../utils/logger';
import { createContext, useContext, useState, useEffect } from 'react';

// ============================================
// LANGUES SUPPORTÉES
// ============================================

export const LANGUAGES = {
  FR: 'fr',
  AR: 'ar',
  DARIJA: 'darija',
  EN: 'en',
};

export const LANGUAGE_NAMES = {
  [LANGUAGES.FR]: 'Français',
  [LANGUAGES.AR]: 'العربية',
  [LANGUAGES.DARIJA]: 'Darija',
  [LANGUAGES.EN]: 'English',
};

export const LANGUAGE_FLAGS = {
  [LANGUAGES.FR]: '🇫🇷',
  [LANGUAGES.AR]: '🇸🇦',
  [LANGUAGES.DARIJA]: '🇲🇦',
  [LANGUAGES.EN]: '🇬🇧',
};

// Langues RTL (Right-to-Left)
export const RTL_LANGUAGES = [LANGUAGES.AR, LANGUAGES.DARIJA];

// ============================================
// SERVICE I18N
// ============================================

class I18nService {
  constructor() {
    this.currentLanguage = this.getDefaultLanguage();
    this.translations = {};
    this.fallbackLanguage = LANGUAGES.FR;
  }

  /**
   * Récupère la langue par défaut (depuis localStorage ou navigateur)
   */
  getDefaultLanguage() {
    // 1. Vérifier localStorage
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage && Object.values(LANGUAGES).includes(savedLanguage)) {
      return savedLanguage;
    }

    // 2. Détecter la langue du navigateur
    const browserLang = navigator.language.split('-')[0];
    if (browserLang === 'ar') return LANGUAGES.AR;
    if (browserLang === 'fr') return LANGUAGES.FR;
    if (browserLang === 'en') return LANGUAGES.EN;

    // 3. Par défaut : Français
    return LANGUAGES.FR;
  }

  /**
   * Change la langue active
   */
  setLanguage(lang) {
    if (!Object.values(LANGUAGES).includes(lang)) {
      console.error(`Langue non supportée: ${lang}`);
      return;
    }

    this.currentLanguage = lang;
    localStorage.setItem('language', lang);

    // Appliquer direction RTL si nécessaire
    const isRTL = RTL_LANGUAGES.includes(lang);
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;

    // Event pour notifier le changement
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  }

  /**
   * Récupère la langue active
   */
  getLanguage() {
    return this.currentLanguage;
  }

  /**
   * Vérifie si la langue est RTL
   */
  isRTL() {
    return RTL_LANGUAGES.includes(this.currentLanguage);
  }

  /**
   * Charge les traductions pour une langue
   */
  async loadTranslations(lang) {
    if (this.translations[lang]) {
      return true;
    }
    
    try {
      const module = await import(`./translations/${lang}.js`);
      this.translations[lang] = module.default;
      // Notifier que les traductions sont chargées
      window.dispatchEvent(new CustomEvent('translationsLoaded', { detail: { language: lang } }));
      return true;
    } catch (error) {
      console.error(`Erreur chargement traductions ${lang}:`, error);
      return false;
    }
  }

  /**
   * Traduit une clé
   */
  t(key, params = {}) {
    const lang = this.currentLanguage;

    // Récupérer la traduction
    let translation = this.translations[lang]?.[key];

    // Fallback sur la langue par défaut
    if (!translation) {
      translation = this.translations[this.fallbackLanguage]?.[key];
    }

    // Si toujours pas trouvé, retourner la clé
    if (!translation) {
      logger.warning(`Traduction manquante: ${key} (${lang})`);
      return key;
    }

    // Remplacer les paramètres {{param}}
    return translation.replace(/\{\{(\w+)\}\}/g, (match, param) => {
      return params[param] !== undefined ? params[param] : match;
    });
  }
}

// Instance singleton
export const i18nService = new I18nService();

// ============================================
// REACT CONTEXT & HOOK
// ============================================

const I18nContext = createContext();

export const I18nProvider = ({ children }) => {
  const [language, setLanguage] = useState(i18nService.getLanguage());
  const [isRTL, setIsRTL] = useState(i18nService.isRTL());
  const [, setTick] = useState(0); // Force update state

  useEffect(() => {
    // Charger les traductions quand la langue change
    i18nService.loadTranslations(language);

    // Appliquer la direction RTL
    const rtl = i18nService.isRTL();
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
    setIsRTL(rtl);
  }, [language]);

  useEffect(() => {
    // Écouter les changements de langue
    const handleLanguageChange = (e) => {
      const newLang = e.detail.language;
      setLanguage(newLang);
    };

    // Écouter le chargement des traductions
    const handleTranslationsLoaded = () => {
      setTick(t => t + 1);
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    window.addEventListener('translationsLoaded', handleTranslationsLoaded);

    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange);
      window.removeEventListener('translationsLoaded', handleTranslationsLoaded);
    };
  }, []);

  const changeLanguage = (newLang) => {
    i18nService.setLanguage(newLang);
  };

  const t = (key, params) => i18nService.t(key, params);

  const value = {
    language,
    isRTL,
    changeLanguage,
    t,
    languages: LANGUAGES,
    languageNames: LANGUAGE_NAMES,
    languageFlags: LANGUAGE_FLAGS,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

/**
 * Hook pour utiliser i18n dans les composants
 */
export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
};

export default i18nService;
