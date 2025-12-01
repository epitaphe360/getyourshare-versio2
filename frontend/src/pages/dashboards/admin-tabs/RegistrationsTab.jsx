import React from 'react';
import RegistrationManagement from '../../admin/RegistrationManagement';

/**
 * Onglet Registrations - Réutilise le composant RegistrationManagement existant
 */
const RegistrationsTab = ({ refreshKey, onRefresh }) => {
  return (
    <div>
      <RegistrationManagement />
    </div>
  );
};

export default RegistrationsTab;
