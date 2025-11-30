import React, { useState, useEffect } from 'react';
import { 
  Package, Plus, Search, Filter, Edit2, Trash2, Eye, 
  ChevronLeft, ChevronRight, AlertCircle, Check, X,
  TrendingUp, TrendingDown, DollarSign, Box
} from 'lucide-react';
import api from '../../utils/api';
import ProductFormModal from '../../components/admin/ProductFormModal';

const AdminProductsManager = () => {
  // État principal
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState([]);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [totalProducts, setTotalProducts] = useState(0);
  
  // Recherche et filtres
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [stockFilter, setStockFilter] = useState('all');
  
  // Modal
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  
  // Statistiques rapides
  const [stats, setStats] = useState({
    total: 0,
    inStock: 0,
    outOfStock: 0,
    lowStock: 0,
    totalValue: 0
  });

  // Chargement initial
  useEffect(() => {
    loadProducts();
    loadStats();
  }, [currentPage, itemsPerPage, searchTerm, categoryFilter, statusFilter, stockFilter]);

  // Charger les produits
  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: currentPage,
        limit: itemsPerPage,
        ...(searchTerm && { search: searchTerm }),
        ...(categoryFilter !== 'all' && { category: categoryFilter }),
        ...(statusFilter !== 'all' && { status: statusFilter }),
        ...(stockFilter !== 'all' && { stock: stockFilter })
      });

      const response = await api.get(`/api/products?${params}`);
      setProducts(response.data.products || []);
      setTotalProducts(response.data.total || 0);
    } catch (error) {
      console.error('Erreur lors du chargement des produits:', error);
    } finally {
      setLoading(false);
    }
  };

  // Charger les statistiques
  const loadStats = async () => {
    try {
      const response = await api.get('/api/products/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des stats:', error);
    }
  };

  // Créer un nouveau produit
  const handleCreate = () => {
    setModalMode('create');
    setEditingProduct(null);
    setShowModal(true);
  };

  // Éditer un produit
  const handleEdit = (product) => {
    setModalMode('edit');
    setEditingProduct(product);
    setShowModal(true);
  };

  // Supprimer un produit
  const handleDelete = async (productId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
      return;
    }

    try {
      await api.delete(`/api/products/${productId}`);
      loadProducts();
      loadStats();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      alert('Erreur lors de la suppression du produit');
    }
  };

  // Actions en masse
  const handleBulkDelete = async () => {
    if (!window.confirm(`Supprimer ${selectedProducts.length} produit(s) sélectionné(s) ?`)) {
      return;
    }

    try {
      await Promise.all(
        selectedProducts.map(id => api.delete(`/api/products/${id}`))
      );
      setSelectedProducts([]);
      loadProducts();
      loadStats();
    } catch (error) {
      console.error('Erreur lors de la suppression en masse:', error);
      alert('Erreur lors de la suppression');
    }
  };

  const handleBulkStatusChange = async (status) => {
    try {
      await Promise.all(
        selectedProducts.map(id => 
          api.put(`/api/products/${id}`, { status })
        )
      );
      setSelectedProducts([]);
      loadProducts();
    } catch (error) {
      console.error('Erreur lors du changement de statut:', error);
      alert('Erreur lors du changement de statut');
    }
  };

  // Sélection
  const toggleSelectAll = () => {
    if (selectedProducts.length === products.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(products.map(p => p.id));
    }
  };

  const toggleSelect = (productId) => {
    if (selectedProducts.includes(productId)) {
      setSelectedProducts(selectedProducts.filter(id => id !== productId));
    } else {
      setSelectedProducts([...selectedProducts, productId]);
    }
  };

  // Pagination
  const totalPages = Math.ceil(totalProducts / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage + 1;
  const endIndex = Math.min(currentPage * itemsPerPage, totalProducts);

  // Indicateur de stock
  const getStockBadge = (stock) => {
    if (stock === 0) {
      return <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-700">Rupture</span>;
    } else if (stock < 10) {
      return <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-700">Stock faible</span>;
    }
    return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">En stock</span>;
  };

  // Indicateur de statut
  const getStatusBadge = (status) => {
    const badges = {
      active: <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700 flex items-center gap-1"><Check size={12} /> Actif</span>,
      inactive: <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700 flex items-center gap-1"><X size={12} /> Inactif</span>,
      draft: <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-700">Brouillon</span>
    };
    return badges[status] || badges.draft;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <Package className="text-blue-600" size={36} />
          Gestion des Produits
        </h1>
        <p className="text-gray-600 mt-2">
          Gérez l'ensemble du catalogue de produits de la plateforme
        </p>
      </div>

      {/* Statistiques Rapides */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Produits</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <Box className="text-blue-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">En stock</p>
              <p className="text-2xl font-bold text-green-600">{stats.inStock}</p>
            </div>
            <TrendingUp className="text-green-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Rupture</p>
              <p className="text-2xl font-bold text-red-600">{stats.outOfStock}</p>
            </div>
            <TrendingDown className="text-red-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Stock faible</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.lowStock}</p>
            </div>
            <AlertCircle className="text-yellow-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Valeur totale</p>
              <p className="text-2xl font-bold text-blue-600">{stats.totalValue}€</p>
            </div>
            <DollarSign className="text-blue-600" size={32} />
          </div>
        </div>
      </div>

      {/* Barre d'outils */}
      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          {/* Recherche */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un produit..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filtres */}
          <div className="flex gap-3 flex-wrap">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Toutes catégories</option>
              <option value="electronics">Électronique</option>
              <option value="fashion">Mode</option>
              <option value="home">Maison</option>
              <option value="beauty">Beauté</option>
              <option value="sports">Sport</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tous statuts</option>
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
              <option value="draft">Brouillon</option>
            </select>

            <select
              value={stockFilter}
              onChange={(e) => setStockFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Tous les stocks</option>
              <option value="in-stock">En stock</option>
              <option value="low-stock">Stock faible</option>
              <option value="out-of-stock">Rupture</option>
            </select>

            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2 font-medium"
            >
              <Plus size={20} />
              Ajouter un produit
            </button>
          </div>
        </div>

        {/* Actions en masse */}
        {selectedProducts.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 flex items-center gap-3">
            <span className="text-sm text-gray-600">
              {selectedProducts.length} produit(s) sélectionné(s)
            </span>
            <button
              onClick={() => handleBulkStatusChange('active')}
              className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
            >
              Activer
            </button>
            <button
              onClick={() => handleBulkStatusChange('inactive')}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
            >
              Désactiver
            </button>
            <button
              onClick={handleBulkDelete}
              className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm"
            >
              Supprimer
            </button>
          </div>
        )}
      </div>

      {/* Tableau des produits */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedProducts.length === products.length && products.length > 0}
                    onChange={toggleSelectAll}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Image
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nom
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Catégorie
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Prix
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                    <div className="flex justify-center items-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                  </td>
                </tr>
              ) : products.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                    Aucun produit trouvé
                  </td>
                </tr>
              ) : (
                products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedProducts.includes(product.id)}
                        onChange={() => toggleSelect(product.id)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <img
                        src={product.image || '/placeholder-product.png'}
                        alt={product.name}
                        className="w-12 h-12 object-cover rounded"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      <div className="text-xs text-gray-500">{product.sku}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-700">{product.category || 'Non catégorisé'}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-medium text-gray-900">{product.price}€</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1">
                        <span className="text-sm text-gray-900">{product.stock || 0}</span>
                        {getStockBadge(product.stock || 0)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(product.status || 'draft')}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEdit(product)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition"
                          title="Modifier"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => window.open(`/marketplace/product/${product.id}`, '_blank')}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                          title="Voir"
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
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

        {/* Pagination */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-700">
              Affichage de {startIndex} à {endIndex} sur {totalProducts} produits
            </span>
            <select
              value={itemsPerPage}
              onChange={(e) => setItemsPerPage(Number(e.target.value))}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value={10}>10 par page</option>
              <option value={25}>25 par page</option>
              <option value={50}>50 par page</option>
              <option value={100}>100 par page</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              <ChevronLeft size={20} />
            </button>
            
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-1 rounded-lg ${
                      currentPage === pageNum
                        ? 'bg-blue-600 text-white'
                        : 'border border-gray-300 hover:bg-gray-100'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <ProductFormModal
          mode={modalMode}
          product={editingProduct}
          onClose={() => {
            setShowModal(false);
            setEditingProduct(null);
          }}
          onSuccess={() => {
            setShowModal(false);
            setEditingProduct(null);
            loadProducts();
            loadStats();
          }}
        />
      )}
    </div>
  );
};

export default AdminProductsManager;
