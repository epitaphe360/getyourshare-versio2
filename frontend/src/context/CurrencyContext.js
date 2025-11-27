import React, { createContext, useState, useContext, useEffect } from 'react';

const CurrencyContext = createContext();

export const CURRENCIES = {
  MAD: { code: 'MAD', symbol: 'DH', name: 'Dirham Marocain', locale: 'fr-MA' },
  EUR: { code: 'EUR', symbol: '€', name: 'Euro', locale: 'fr-FR' },
  USD: { code: 'USD', symbol: '$', name: 'Dollar Américain', locale: 'en-US' }
};

export const CurrencyProvider = ({ children }) => {
  // Default to MAD as per request "destined to Morocco"
  const [currency, setCurrency] = useState('MAD');

  // Persist selection
  useEffect(() => {
    const saved = localStorage.getItem('currency');
    if (saved && CURRENCIES[saved]) {
      setCurrency(saved);
    }
  }, []);

  const changeCurrency = (code) => {
    if (CURRENCIES[code]) {
      setCurrency(code);
      localStorage.setItem('currency', code);
    }
  };

  const formatPrice = (amount, currencyCode = currency) => {
    const curr = CURRENCIES[currencyCode];
    if (!curr) return `${amount}`;
    
    return new Intl.NumberFormat(curr.locale, {
      style: 'currency',
      currency: curr.code,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  };

  return (
    <CurrencyContext.Provider value={{ currency, changeCurrency, formatPrice, CURRENCIES }}>
      {children}
    </CurrencyContext.Provider>
  );
};

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};
