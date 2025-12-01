import React from 'react';
import AdminProductsManager from '../../admin/AdminProductsManager';

/**
 * Onglet Products - Réutilise le composant AdminProductsManager existant
 */
const ProductsTab = ({ stats, refreshKey, onRefresh }) => {
  return (
    <div>
      <AdminProductsManager />
    </div>
  );
};

export default ProductsTab;
