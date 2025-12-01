import React from 'react';
import { useNavigate } from 'react-router-dom';
import MerchantManagement from '../../admin/MerchantManagement';

/**
 * Onglet Merchants - Réutilise le composant MerchantManagement existant
 * Évite la duplication de code
 */
const MerchantsTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();

  return (
    <div>
      <MerchantManagement />
    </div>
  );
};

export default MerchantsTab;
