/**
 * Helpers centralisés pour la gestion des abonnements
 * Utilisé par tous les dashboards pour éviter la duplication de code
 */

/**
 * Vérifie l'accès à une fonctionnalité selon le plan d'abonnement
 * @param {string} feature - Nom de la fonctionnalité
 * @param {object} subscription - Objet subscription avec plan_name ou plan_code
 * @param {string} role - Rôle de l'utilisateur (merchant, influencer, commercial, admin)
 * @returns {boolean}
 */
export const checkAccess = (feature, subscription, role = 'influencer') => {
  if (!subscription) return false;

  const plan = (subscription.plan_name || subscription.plan_code || 'free').toLowerCase();

  // Admin a accès à tout
  if (role === 'admin') return true;

  // Matrice d'accès par rôle et feature
  const accessMatrix = {
    // Influencer features
    influencer: {
      analytics_pro: ['pro', 'elite', 'premium'].includes(plan),
      matching: ['elite', 'premium'].includes(plan),
      ia_marketing: ['elite', 'premium'].includes(plan),
      live_shopping: !['free'].includes(plan),
      referral: true,
      mobile: true,
      marketplace: true,
      instant_payout: ['elite', 'premium'].includes(plan)
    },
    // Merchant features
    merchant: {
      advanced_analytics: ['premium', 'enterprise'].includes(plan),
      matching: ['enterprise'].includes(plan),
      live_shopping: ['enterprise'].includes(plan),
      unlimited_products: ['enterprise'].includes(plan),
      unlimited_affiliates: ['premium', 'enterprise'].includes(plan),
      referral: ['premium', 'enterprise'].includes(plan),
      api_access: ['enterprise'].includes(plan)
    },
    // Commercial features
    commercial: {
      advanced_analytics: ['pro', 'enterprise'].includes(plan),
      unlimited_links: ['enterprise'].includes(plan),
      ai_generator: ['enterprise'].includes(plan),
      unlimited_templates: ['pro', 'enterprise'].includes(plan),
      crm_integration: ['enterprise'].includes(plan),
      white_label: ['enterprise'].includes(plan)
    }
  };

  return accessMatrix[role]?.[feature] ?? true;
};

/**
 * Obtenir les limites du plan selon le rôle
 * @param {object} subscription - Objet subscription
 * @param {string} role - Rôle de l'utilisateur
 * @returns {object} Limites du plan
 */
export const getPlanLimits = (subscription, role = 'influencer') => {
  if (!subscription) {
    // Limites par défaut selon le rôle
    const defaults = {
      influencer: { campaigns: 3, lives: 0, commission: 5 },
      merchant: { campaigns: 1, products: 5, affiliates: 10, budget: 500 },
      commercial: { leads: 10, links: 3, templates: 3, commission: 10, analytics_days: 7 }
    };
    return defaults[role] || defaults.influencer;
  }

  const plan = (subscription.plan_name || subscription.plan_code || 'free').toLowerCase();

  // Limites par rôle
  const limits = {
    influencer: {
      free: { campaigns: 3, lives: 0, commission: 5 },
      basic: { campaigns: 10, lives: 1, commission: 7 },
      pro: { campaigns: 50, lives: 5, commission: 10 },
      elite: { campaigns: -1, lives: -1, commission: 15 },
      premium: { campaigns: -1, lives: -1, commission: 15 }
    },
    merchant: {
      freemium: { campaigns: 1, products: 5, affiliates: 10, budget: 500, analytics_days: 7 },
      standard: { campaigns: 5, products: 25, affiliates: 50, budget: 5000, analytics_days: 30 },
      premium: { campaigns: 20, products: 100, affiliates: 200, budget: 50000, analytics_days: 90 },
      enterprise: { campaigns: 999, products: 999, affiliates: 999, budget: 999999, analytics_days: 365 }
    },
    commercial: {
      starter: { leads: 10, links: 3, templates: 3, commission: 10, analytics_days: 7 },
      pro: { leads: 50, links: 15, templates: 999, commission: 15, analytics_days: 30 },
      enterprise: { leads: 999, links: 999, templates: 999, commission: 20, analytics_days: 365 }
    }
  };

  return limits[role]?.[plan] || limits[role]?.['free'] || limits.influencer.free;
};

/**
 * Obtenir le badge visuel du plan
 * @param {object} subscription - Objet subscription
 * @param {string} role - Rôle de l'utilisateur
 * @returns {object} Badge avec name, color, icon
 */
export const getPlanBadge = (subscription, role = 'influencer') => {
  if (!subscription) {
    return { name: 'Free', color: 'bg-gray-100 text-gray-700', icon: '🆓' };
  }

  const plan = (subscription.plan_name || subscription.plan_code || 'free').toLowerCase();

  // Badges par rôle
  const badges = {
    influencer: {
      free: { name: 'Free', color: 'bg-gray-100 text-gray-700', icon: '🆓' },
      basic: { name: 'Basic', color: 'bg-blue-100 text-blue-700', icon: '⭐' },
      pro: { name: 'Pro', color: 'bg-purple-100 text-purple-700', icon: '💎' },
      elite: { name: 'Elite', color: 'bg-yellow-100 text-yellow-700', icon: '👑' },
      premium: { name: 'Premium', color: 'bg-yellow-100 text-yellow-700', icon: '👑' }
    },
    merchant: {
      freemium: { name: 'Freemium', color: 'bg-gray-100 text-gray-700', icon: '🌱' },
      standard: { name: 'Standard', color: 'bg-blue-100 text-blue-700', icon: '⭐' },
      premium: { name: 'Premium', color: 'bg-purple-100 text-purple-700', icon: '💎' },
      enterprise: { name: 'Enterprise', color: 'bg-yellow-100 text-yellow-700', icon: '👑' }
    },
    commercial: {
      starter: { name: 'Starter', color: 'bg-orange-100 text-orange-800 border-orange-300', icon: '🌱' },
      pro: { name: 'Pro', color: 'bg-purple-100 text-purple-800 border-purple-300', icon: '⚡' },
      enterprise: { name: 'Enterprise', color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: '👑' }
    }
  };

  return badges[role]?.[plan] || badges[role]?.['free'] || badges.influencer.free;
};

/**
 * Formater l'affichage d'une limite (nombre ou illimité)
 * @param {number} limit - Limite numérique (-1 = illimité)
 * @returns {string}
 */
export const formatLimit = (limit) => {
  if (limit === -1 || limit >= 999) return 'Illimité';
  return limit.toString();
};

/**
 * Vérifier si un utilisateur a atteint sa limite
 * @param {number} current - Valeur actuelle
 * @param {number} limit - Limite max
 * @returns {object} { reached: boolean, percentage: number }
 */
export const checkLimitReached = (current, limit) => {
  if (limit === -1 || limit >= 999) {
    return { reached: false, percentage: 0 };
  }

  const percentage = (current / limit) * 100;
  return {
    reached: current >= limit,
    percentage: Math.min(percentage, 100)
  };
};

/**
 * Obtenir la couleur du badge de pourcentage d'utilisation
 * @param {number} percentage - Pourcentage d'utilisation
 * @returns {string} Classes Tailwind
 */
export const getUsageColor = (percentage) => {
  if (percentage >= 90) return 'bg-red-100 text-red-700';
  if (percentage >= 70) return 'bg-orange-100 text-orange-700';
  if (percentage >= 50) return 'bg-yellow-100 text-yellow-700';
  return 'bg-green-100 text-green-700';
};

/**
 * Obtenir le prochain plan recommandé
 * @param {object} subscription - Subscription actuelle
 * @param {string} role - Rôle de l'utilisateur
 * @returns {string|null} Nom du prochain plan ou null
 */
export const getUpgradePlan = (subscription, role = 'influencer') => {
  if (!subscription) return null;

  const plan = (subscription.plan_name || subscription.plan_code || 'free').toLowerCase();

  const upgradePaths = {
    influencer: {
      free: 'basic',
      basic: 'pro',
      pro: 'elite',
      elite: 'premium',
      premium: null
    },
    merchant: {
      freemium: 'standard',
      standard: 'premium',
      premium: 'enterprise',
      enterprise: null
    },
    commercial: {
      starter: 'pro',
      pro: 'enterprise',
      enterprise: null
    }
  };

  return upgradePaths[role]?.[plan] || null;
};
