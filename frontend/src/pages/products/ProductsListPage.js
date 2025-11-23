import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Table from '../../components/common/Table';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import EmptyState from '../../components/common/EmptyState';
import {
  Package, Plus, Edit, Trash2, Search, Eye, TrendingUp,
  DollarSign, Archive, Star, Zap
} from 'lucide-react';

const ProductsListPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, product: null });
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/marketplace/products');
      const productsData = response.data.products || [];
      setProducts(productsData);
      
      // Calculer statistiques
      const total = productsData.length;
      const active = productsData.filter(p => p.status === 'active').length;
      const totalValue = productsData.reduce((sum, p) => sum + (parseFloat(p.price) || 0), 0);
      
      setStats({ total, active, totalValue });
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId) => {
    try {
      await api.delete(`/api/products/${productId}`);
      setDeleteModal({ isOpen: false, product: null });
      await fetchProducts();
      toast.success('Produit supprimé avec succès');
    } catch (error) {
      console.error('Error deleting product:', error);
      toast.error('Erreur lors de la suppression du produit');
    }
  };

  const filteredProducts = products.filter(product =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Fonction utilitaire pour gérer les images (JSONB array)
  const getFirstImage = (product) => {
    if (!product.images) return null;

    // Si c'est déjà un array
    if (Array.isArray(product.images) && product.images.length > 0) {
      return product.images[0];
    }

    // Si c'est une string JSON, parser
    if (typeof product.images === 'string') {
      try {
        const parsed = JSON.parse(product.images);
        return Array.isArray(parsed) && parsed.length > 0 ? parsed[0] : null;
      } catch {
        return null;
      }
    }

    return null;
  };

  const columns = useMemo(() => [
    {
      key: 'name',
      label: 'Produit',
      render: (product) => {
        const imageUrl = getFirstImage(product);

        return (
          <div className="flex items-center gap-3">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={product.name}
                className="w-12 h-12 rounded object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            ) : (
              <div className="w-12 h-12 bg-gray-200 rounded flex items-center justify-center">
                <Package size={24} className="text-gray-400" />
              </div>
            )}
            <div>
              <div className="font-semibold">{product.name}</div>
              <div className="text-sm text-gray-500">{product.category || 'Non catégorisé'}</div>
            </div>
          </div>
        );
      }
    },
    {
      key: 'description',
      label: 'Description',
      render: (product) => (
        <div className="max-w-md">
          <p className="text-sm text-gray-600 truncate">{product.description}</p>
        </div>
      )
    },
    {
      key: 'price',
      label: 'Prix',
      render: (product) => (
        <div className="font-semibold text-lg">
          {parseFloat(product.price).toFixed(2)} €
        </div>
      )
    },
    {
      key: 'commission_rate',
      label: 'Commission',
      render: (product) => (
        <Badge variant="success">
          {product.commission_rate}%
        </Badge>
      )
    },
    {
      key: 'status',
      label: 'Statut',
      render: (product) => (
        <Badge variant={product.status === 'active' ? 'success' : 'secondary'}>
          {product.status === 'active' ? 'Actif' : 'Inactif'}
        </Badge>
      )
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (product) => (
        <div className="flex gap-2">
          <button
            onClick={() => navigate(`/marketplace/product/${product.id}`)}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Voir détails"
          >
            <Eye size={18} className="text-gray-600" />
          </button>
          <button
            onClick={() => navigate(`/products/${product.id}/edit`)}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Modifier"
          >
            <Edit size={18} className="text-blue-600" />
          </button>
          <button
            onClick={() => setDeleteModal({ isOpen: true, product })}
            className="p-2 hover:bg-gray-100 rounded transition"
            title="Supprimer"
          >
            <Trash2 size={18} className="text-red-600" />
          </button>
        </div>
      )
    }
  ], [navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement des produits...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Produits</h1>
          <p className="text-gray-600 mt-2 text-lg">Gérez votre catalogue de produits premium</p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button disabled={loading} onClick={() => navigate('/products/create')}>
            <Plus size={20} className="mr-2" />
            Ajouter un produit
          </Button>
        </motion.div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { icon: Package, label: "Total Produits", value: stats.total, color: "indigo", gradient: "from-indigo-500 to-purple-600" },
          { icon: TrendingUp, label: "Produits Actifs", value: stats.active, color: "green", gradient: "from-green-500 to-emerald-600" },
          { icon: DollarSign, label: "Valeur Catalogue", value: `${stats.totalValue.toFixed(2)} €`, color: "blue", gradient: "from-blue-500 to-cyan-600" }
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5, shadow: "2xl" }}
          >
            <Card className="relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br opacity-10 rounded-full -mr-8 -mt-8" style={{ background: `linear-gradient(135deg, var(--tw-gradient-stops))` }}></div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-4xl font-black text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`bg-gradient-to-br ${stat.gradient} p-4 rounded-xl shadow-lg`}>
                  <stat.icon size={32} className="text-white" />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Search and Filters */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        <Card className="bg-white/80 backdrop-blur-sm">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative group">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-600 transition-colors" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom, description, catégorie..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all shadow-sm"
              />
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Products Grid */}
      <AnimatePresence mode="wait">
        {filteredProducts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card className="py-16">
              <EmptyState
                icon={Package}
                title={searchTerm ? "Aucun produit trouvé" : "Aucun produit pour le moment"}
                description={searchTerm 
                  ? "Essayez avec d'autres mots-clés ou filtres" 
                  : "Créez votre premier produit pour commencer à vendre et travailler avec des influenceurs"}
                actionLabel={!searchTerm ? "Créer un produit" : null}
                onAction={() => navigate('/products/create')}
              />
            </Card>
          </motion.div>
        ) : (
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {filteredProducts.map((product, index) => {
              const imageUrl = getFirstImage(product);
              return (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ y: -8 }}
                  className="group"
                >
                  <Card className="overflow-hidden h-full hover:shadow-2xl transition-all duration-300 border border-gray-100">
                    {/* Image */}
                    <div className="relative h-56 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden">
                      {imageUrl ? (
                        <img
                          src={imageUrl}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Package size={64} className="text-gray-300" />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      
                      {/* Badges */}
                      <div className="absolute top-4 left-4 flex gap-2">
                        <span className="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-gray-900 border border-gray-200">
                          {product.category || 'Non catégorisé'}
                        </span>
                        {product.commission_rate >= 20 && (
                          <span className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1">
                            <Zap size={12} fill="currentColor" /> {product.commission_rate}%
                          </span>
                        )}
                      </div>
                      
                      {/* Status Badge */}
                      <div className="absolute top-4 right-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${product.status === 'active' ? 'bg-green-500 text-white' : 'bg-gray-500 text-white'}`}>
                          {product.status === 'active' ? 'Actif' : 'Inactif'}
                        </span>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                      <div className="mb-4">
                        <h3 className="text-xl font-bold text-gray-900 mb-1 group-hover:text-indigo-600 transition-colors line-clamp-1">
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-500 line-clamp-2 h-10">
                          {product.description}
                        </p>
                      </div>

                      {/* Price & Commission */}
                      <div className="flex items-center justify-between mb-6 bg-gray-50 rounded-xl p-4">
                        <div>
                          <div className="text-xs text-gray-500 mb-1">Prix</div>
                          <div className="text-2xl font-black text-gray-900">
                            {parseFloat(product.price).toFixed(2)} €
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500 mb-1">Commission</div>
                          <div className="text-2xl font-black text-green-600">
                            {product.commission_rate}%
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => navigate(`/marketplace/product/${product.id}`)}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
                        >
                          <Eye size={18} />
                          Voir
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => navigate(`/products/${product.id}/edit`)}
                          className="px-4 py-3 bg-white border-2 border-gray-200 text-gray-700 rounded-lg hover:border-indigo-600 hover:text-indigo-600 transition-all"
                        >
                          <Edit size={18} />
                        </motion.button>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setDeleteModal({ isOpen: true, product })}
                          className="px-4 py-3 bg-white border-2 border-gray-200 text-red-600 rounded-lg hover:border-red-600 hover:bg-red-50 transition-all"
                        >
                          <Trash2 size={18} />
                        </motion.button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, product: null })}
        title="Supprimer le produit"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Êtes-vous sûr de vouloir supprimer le produit{' '}
            <span className="font-semibold">{deleteModal.product?.name}</span> ?
          </p>
          <p className="text-sm text-red-600">
            Cette action est irréversible et supprimera également toutes les données associées.
          </p>
          <div className="flex gap-3 justify-end mt-6">
            <Button
              variant="secondary"
              onClick={() => setDeleteModal({ isOpen: false, product: null })}
            >
              Annuler
            </Button>
            <Button
              variant="danger"
              onClick={() => handleDelete(deleteModal.product?.id)}
            >
              <Trash2 size={18} className="mr-2" />
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ProductsListPage;
