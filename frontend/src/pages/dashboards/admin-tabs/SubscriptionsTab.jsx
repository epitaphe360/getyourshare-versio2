import React from 'react';
import AdminSubscriptionsManager from '../../admin/AdminSubscriptionsManager';

/**
 * Onglet Subscriptions - Réutilise le composant AdminSubscriptionsManager existant
 */
const SubscriptionsTab = ({ stats, refreshKey, onRefresh }) => {
  return (
    <div>
      <AdminSubscriptionsManager />
    </div>
  );
};

export default SubscriptionsTab;
