import React from 'react';
import ServiceManagement from '../../admin/ServiceManagement';

/**
 * Onglet Services - Réutilise le composant ServiceManagement existant
 */
const ServicesTab = ({ stats, refreshKey, onRefresh }) => {
  return (
    <div>
      <ServiceManagement />
    </div>
  );
};

export default ServicesTab;
