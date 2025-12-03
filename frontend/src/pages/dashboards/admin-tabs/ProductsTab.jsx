import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  Package, Eye, Edit, Copy, Trash2, Download, Search, Filter, Plus,
  TrendingUp, AlertTriangle, DollarSign, Box, ChevronDown, X, Check
} from 'lucide-react';
import {
  formatCurrency, formatDate, exportToCSV, formatNumber, getStatusColor
} from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';
import CountUp from 'react-countup';

/**
 * ProductsTab - Gestion complète des produits (Niveau SaaS)
 *
 * Features:
 * - KPI Cards (Total, Actifs, En rupture, Valeur inventaire)
 * - Filtres avancés (Recherche, Catégorie, Statut, Stock)
 * - Table avec images miniatures
 * - Actions inline (Voir, Éditer, Dupliquer, Supprimer)
 * - Modal détails produit complet
 * - Actions en masse (Approve, Archive, Delete)
 * - Export CSV
 * - Optimisé avec useCallback + AbortController
 */
const ProductsTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();

  // ========== STATES ==========
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [stockFilter, setStockFilter] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState([]);

  // Stats locales
  const [localStats, setLocalStats] = useState({
    total: 0,
    active: 0,
    outOfStock: 0,
    totalValue: 0
  });

  // ========== API CALLS ==========
  const fetchProducts = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};

      // Appel parallèle pour récupérer produits et catégories
      const [productsRes, categoriesRes] = await Promise.allSettled([
        api.get('/api/products', config),
        api.get('/api/categories', config)
      ]);

      if (productsRes.status === 'fulfilled') {
        const productsData = productsRes.value.data.products || productsRes.value.data || [];
        setProducts(productsData);

        // Calculer stats locales
        setLocalStats({
          total: productsData.length,
          active: productsData.filter(p => p.is_active).length,
          outOfStock: productsData.filter(p => p.stock === 0).length,
          totalValue: productsData.reduce((sum, p) => sum + (p.price * (p.stock || 0)), 0)
        });
      }

      if (categoriesRes.status === 'fulfilled') {
        setCategories(categoriesRes.value.data.categories || categoriesRes.value.data || []);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement produits:', error);
        toast.error('Impossible de charger les produits');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchProducts(controller.signal);
    return () => controller.abort();
  }, [fetchProducts, refreshKey]);

  // ========== HANDLERS ==========
  const handleViewDetails = useCallback(async (product) => {
    try {
      // Charger les détails complets du produit
      const response = await api.get(`/api/products/${product.id}`);
      setSelectedProduct(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Erreur chargement détails produit:', error);
      toast.error('Impossible de charger les détails');
    }
  }, [toast]);

  const handleToggleStatus = useCallback(async (productId, currentStatus) => {
    try {
      await api.patch(`/api/products/${productId}`, {
        is_active: !currentStatus
      });

      toast.success(!currentStatus ? 'Produit activé' : 'Produit désactivé');
      fetchProducts();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur toggle status:', error);
      toast.error('Impossible de modifier le statut');
    }
  }, [toast, fetchProducts, onRefresh]);

  const handleDuplicate = useCallback(async (product) => {
    try {
      const duplicateData = {
        ...product,
        name: `${product.name} (Copie)`,
        id: undefined,
        created_at: undefined,
        updated_at: undefined
      };

      await api.post('/api/products', duplicateData);
      toast.success('Produit dupliqué avec succès');
      fetchProducts();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur duplication:', error);
      toast.error('Impossible de dupliquer le produit');
    }
  }, [toast, fetchProducts, onRefresh]);

  const handleDelete = useCallback(async (productId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) return;

    try {
      await api.delete(`/api/products/${productId}`);
      toast.success('Produit supprimé');
      fetchProducts();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur suppression:', error);
      toast.error('Impossible de supprimer le produit');
    }
  }, [toast, fetchProducts, onRefresh]);

  const handleBulkAction = useCallback(async (action) => {
    if (selectedProducts.length === 0) {
      toast.warning('Aucun produit sélectionné');
      return;
    }

    try {
      switch (action) {
        case 'approve':
          await Promise.all(
            selectedProducts.map(id => api.patch(`/api/products/${id}`, { is_active: true }))
          );
          toast.success(`${selectedProducts.length} produits activés`);
          break;
        case 'archive':
          await Promise.all(
            selectedProducts.map(id => api.patch(`/api/products/${id}`, { is_active: false }))
          );
          toast.success(`${selectedProducts.length} produits désactivés`);
          break;
        case 'delete':
          if (!window.confirm(`Supprimer ${selectedProducts.length} produits ?`)) return;
          await Promise.all(
            selectedProducts.map(id => api.delete(`/api/products/${id}`))
          );
          toast.success(`${selectedProducts.length} produits supprimés`);
          break;
        default:
          break;
      }

      setSelectedProducts([]);
      fetchProducts();
      onRefresh?.();
    } catch (error) {
      console.error('Erreur action en masse:', error);
      toast.error('Impossible d\'effectuer l\'action');
    }
  }, [selectedProducts, toast, fetchProducts, onRefresh]);

  const handleExport = useCallback(() => {
    const exportData = filteredProducts.map(p => ({
      id: p.id,
      nom: p.name,
      categorie: categories.find(c => c.id === p.category_id)?.name || 'N/A',
      prix: p.price,
      stock: p.stock || 0,
      commission: p.commission_rate,
      statut: p.is_active ? 'Actif' : 'Inactif',
      merchant: p.merchant?.company_name || 'N/A',
      date_creation: formatDate(p.created_at)
    }));

    exportToCSV(exportData, 'produits_export');
    toast.success('Produits exportés avec succès');
  }, [categories, toast]);

  // ========== FILTRAGE ==========
  const filteredProducts = products.filter(product => {
    // Recherche
    if (searchTerm && !product.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Catégorie
    if (categoryFilter !== 'all' && product.category_id !== categoryFilter) {
      return false;
    }

    // Statut
    if (statusFilter === 'active' && !product.is_active) return false;
    if (statusFilter === 'inactive' && product.is_active) return false;

    // Stock
    if (stockFilter === 'in-stock' && (product.stock || 0) === 0) return false;
    if (stockFilter === 'low-stock' && (product.stock || 0) > 10) return false;
    if (stockFilter === 'out-of-stock' && (product.stock || 0) > 0) return false;

    return true;
  });

  // ========== RENDER ==========
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des produits...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Produits</p>
              <p className="text-3xl font-bold text-gray-900">
                <CountUp end={localStats.total} duration={1} />
              </p>
            </div>
            <div className="bg-blue-100 rounded-lg p-3">
              <Package className="text-blue-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Produits Actifs</p>
              <p className="text-3xl font-bold text-green-600">
                <CountUp end={localStats.active} duration={1} />
              </p>
            </div>
            <div className="bg-green-100 rounded-lg p-3">
              <TrendingUp className="text-green-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">En Rupture</p>
              <p className="text-3xl font-bold text-red-600">
                <CountUp end={localStats.outOfStock} duration={1} />
              </p>
            </div>
            <div className="bg-red-100 rounded-lg p-3">
              <AlertTriangle className="text-red-600" size={24} />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Valeur Inventaire</p>
              <p className="text-3xl font-bold text-purple-600">
                <CountUp
                  end={localStats.totalValue}
                  duration={1}
                  separator=" "
                  suffix=" €"
                  decimals={0}
                />
              </p>
            </div>
            <div className="bg-purple-100 rounded-lg p-3">
              <DollarSign className="text-purple-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Filtres et Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row gap-4 mb-4">
          {/* Recherche */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher un produit..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtre Catégorie */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Toutes catégories</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>

          {/* Filtre Statut */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>

          {/* Filtre Stock */}
          <select
            value={stockFilter}
            onChange={(e) => setStockFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
          >
            <option value="all">Tous stocks</option>
            <option value="in-stock">En stock</option>
            <option value="low-stock">Stock faible (&lt; 10)</option>
            <option value="out-of-stock">Rupture</option>
          </select>

          {/* Export */}
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2 transition-colors whitespace-nowrap"
          >
            <Download size={20} />
            Export CSV
          </button>
        </div>

        {/* Actions en masse */}
        {selectedProducts.length > 0 && (
          <div className="flex items-center gap-3 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
            <span className="text-sm font-medium text-indigo-900">
              {selectedProducts.length} produit(s) sélectionné(s)
            </span>
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => handleBulkAction('approve')}
                className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
              >
                <Check size={16} className="inline mr-1" />
                Activer
              </button>
              <button
                onClick={() => handleBulkAction('archive')}
                className="px-3 py-1.5 bg-orange-600 text-white text-sm rounded-lg hover:bg-orange-700 transition-colors"
              >
                <Box size={16} className="inline mr-1" />
                Désactiver
              </button>
              <button
                onClick={() => handleBulkAction('delete')}
                className="px-3 py-1.5 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
              >
                <Trash2 size={16} className="inline mr-1" />
                Supprimer
              </button>
              <button
                onClick={() => setSelectedProducts([])}
                className="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Table Produits */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedProducts.length === filteredProducts.length && filteredProducts.length > 0}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedProducts(filteredProducts.map(p => p.id));
                      } else {
                        setSelectedProducts([]);
                      }
                    }}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Produit
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Catégorie
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Prix
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Commission
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredProducts.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                    <Package className="mx-auto mb-3 text-gray-400" size={48} />
                    <p className="text-lg font-medium">Aucun produit trouvé</p>
                    <p className="text-sm mt-1">Essayez de modifier vos filtres</p>
                  </td>
                </tr>
              ) : (
                filteredProducts.map(product => (
                  <tr
                    key={product.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedProducts.includes(product.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedProducts([...selectedProducts, product.id]);
                          } else {
                            setSelectedProducts(selectedProducts.filter(id => id !== product.id));
                          }
                        }}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="w-12 h-12 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
                            <Package className="text-gray-400" size={24} />
                          </div>
                        )}
                        <div>
                          <p className="font-medium text-gray-900">{product.name}</p>
                          <p className="text-sm text-gray-500">
                            {product.merchant?.company_name || 'Merchant inconnu'}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                        {categories.find(c => c.id === product.category_id)?.name || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-semibold text-gray-900">
                        {formatCurrency(product.price)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className={`font-medium ${
                          (product.stock || 0) === 0 ? 'text-red-600' :
                          (product.stock || 0) < 10 ? 'text-orange-600' :
                          'text-green-600'
                        }`}>
                          {product.stock || 0}
                        </span>
                        {(product.stock || 0) === 0 && (
                          <AlertTriangle className="text-red-500" size={16} />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-900 font-medium">
                        {product.commission_rate}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        product.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {product.is_active ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleViewDetails(product)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Voir détails"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => navigate(`/admin/products/edit/${product.id}`)}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                          title="Éditer"
                        >
                          <Edit size={18} />
                        </button>
                        <button
                          onClick={() => handleDuplicate(product)}
                          className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                          title="Dupliquer"
                        >
                          <Copy size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Supprimer"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Détails Produit */}
      {showDetailModal && selectedProduct && (
        <BaseModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          title="Détails du Produit"
          size="large"
        >
          <div className="space-y-6">
            {/* Image et infos principales */}
            <div className="flex gap-6">
              {selectedProduct.image_url ? (
                <img
                  src={selectedProduct.image_url}
                  alt={selectedProduct.name}
                  className="w-48 h-48 rounded-lg object-cover"
                />
              ) : (
                <div className="w-48 h-48 rounded-lg bg-gray-200 flex items-center justify-center">
                  <Package className="text-gray-400" size={64} />
                </div>
              )}
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  {selectedProduct.name}
                </h3>
                <p className="text-gray-600 mb-4">{selectedProduct.description}</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Prix</p>
                    <p className="text-lg font-semibold">{formatCurrency(selectedProduct.price)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Stock</p>
                    <p className="text-lg font-semibold">{selectedProduct.stock || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Commission</p>
                    <p className="text-lg font-semibold">{selectedProduct.commission_rate}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Statut</p>
                    <p className="text-lg font-semibold">
                      {selectedProduct.is_active ? '✅ Actif' : '❌ Inactif'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Informations merchant */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Merchant</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="font-medium">{selectedProduct.merchant?.company_name || 'N/A'}</p>
                <p className="text-sm text-gray-600">{selectedProduct.merchant?.email || 'N/A'}</p>
              </div>
            </div>

            {/* Stats de performance */}
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-900 mb-3">Performance</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-blue-600">Vues</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {formatNumber(selectedProduct.views || 0)}
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-green-600">Clics</p>
                  <p className="text-2xl font-bold text-green-900">
                    {formatNumber(selectedProduct.clicks || 0)}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-600">Conversions</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {formatNumber(selectedProduct.conversions || 0)}
                  </p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="border-t pt-4 flex gap-3">
              <button
                onClick={() => {
                  setShowDetailModal(false);
                  navigate(`/admin/products/edit/${selectedProduct.id}`);
                }}
                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Éditer le produit
              </button>
              <button
                onClick={() => handleToggleStatus(selectedProduct.id, selectedProduct.is_active)}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  selectedProduct.is_active
                    ? 'bg-orange-600 text-white hover:bg-orange-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {selectedProduct.is_active ? 'Désactiver' : 'Activer'}
              </button>
            </div>
          </div>
        </BaseModal>
      )}
    </div>
  );
};

export default ProductsTab;
