// =====================================================
// FONCTIONS HELPER ABONNEMENT
// =====================================================

// Fonction centralisée pour vérifier l'accès aux fonctionnalités
export const checkAccess = (feature, subscriptionTier) => {
  const tierLower = (subscriptionTier || 'starter').toLowerCase();
  
  switch(feature) {
    case 'advanced_analytics':
      return ['pro', 'enterprise'].includes(tierLower);
    case 'unlimited_links':
      return ['enterprise'].includes(tierLower);
    case 'ai_generator':
      return ['enterprise'].includes(tierLower);
    case 'unlimited_templates':
      return ['pro', 'enterprise'].includes(tierLower);
    case 'crm_integration':
      return ['enterprise'].includes(tierLower);
    case 'white_label':
      return ['enterprise'].includes(tierLower);
    default:
      return true;
  }
};

// Obtenir les limites du plan
export const getPlanLimits = (subscriptionTier) => {
  const tierLower = (subscriptionTier || 'starter').toLowerCase();
  
  switch(tierLower) {
    case 'starter':
      return {
        leads: 10,
        links: 3,
        templates: 3,
        commission: 10,
        analytics_days: 7
      };
    case 'pro':
      return {
        leads: 50,
        links: 15,
        templates: 999,
        commission: 15,
        analytics_days: 30
      };
    case 'enterprise':
      return {
        leads: 999,
        links: 999,
        templates: 999,
        commission: 20,
        analytics_days: 365
      };
    default:
      return getPlanLimits('starter');
  }
};

// Obtenir le badge du plan
export const getPlanBadge = (subscriptionTier) => {
  const tierLower = (subscriptionTier || 'starter').toLowerCase();
  
  switch(tierLower) {
    case 'starter':
      return {
        name: 'Starter',
        color: 'bg-orange-100 text-orange-800 border-orange-300',
        icon: '🌱'
      };
    case 'pro':
      return {
        name: 'Pro',
        color: 'bg-purple-100 text-purple-800 border-purple-300',
        icon: '⚡'
      };
    case 'enterprise':
      return {
        name: 'Enterprise',
        color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: '👑'
      };
    default:
      return getPlanBadge('starter');
  }
};
