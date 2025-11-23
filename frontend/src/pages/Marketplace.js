import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';
import {
  Search, Filter, Star, TrendingUp, Package,
  Users, ShoppingBag, Sparkles, Eye, Target,
  Heart, ExternalLink, Loader2, ArrowRight, Zap
} from 'lucide-react';

const MarketplaceNew = memo(() => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popular');

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {};
      const response = await api.get('/api/marketplace/products', { params });
      // Gestion des deux formats de réponse possibles
      const productsData = Array.isArray(response.data) ? response.data : response.data.products || [];
      setProducts(productsData);
    } catch (error) {
      console.error('Error fetching products:', error);
      toast?.error('Erreur lors du chargement des produits');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, toast]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const categories = [
    { id: 'all', name: 'Tous', icon: '🌟' },
    { id: 'Mode', name: 'Mode', icon: '👕' },
    { id: 'Beauté', name: 'Beauté', icon: '💄' },
    { id: 'Technologie', name: 'Tech', icon: '📱' },
    { id: 'Sport', name: 'Sport', icon: '⚽' },
    { id: 'Alimentation', name: 'Food', icon: '🍔' },
    { id: 'Maison', name: 'Maison', icon: '🏠' }
  ];

  const handleGenerateLink = async (productId) => {
    if (user?.role !== 'influencer') {
      toast.warning('Vous devez être un influenceur pour générer des liens');
      return;
    }

    try {
      const response = await api.post('/api/affiliate-links/generate', { product_id: productId });
      if (response.data.link) {
        const linkUrl = response.data.link.short_url || response.data.link.full_url;
        
        // Copy to clipboard (with error handling)
        let copied = false;
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(linkUrl);
            copied = true;
          }
        } catch (err) {
          }
        
        toast.success(
          `Lien généré avec succès ! ${copied ? 'Copié dans le presse-papier.' : ''}`,
          { duration: 4000 }
        );
        
        // Redirect to tracking links page
        setTimeout(() => {
          navigate('/tracking-links');
        }, 1500);
      }
    } catch (error) {
      console.error('Error generating link:', error);
      console.error('Error details:', error.response?.data);
      toast.error(
        `Erreur lors de la génération du lien: ${error.response?.data?.detail || error.message}`
      );
    }
  };

  // Fonction utilitaire pour gérer les images (JSONB array)
  const getProductImages = (product) => {
    if (!product.images) return [];

    // Si c'est déjà un array
    if (Array.isArray(product.images)) return product.images;

    // Si c'est une string JSON, parser
    if (typeof product.images === 'string') {
      try {
        const parsed = JSON.parse(product.images);
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return [];
      }
    }

    return [];
  };

  // Filter and sort products with memoization
  const filteredProducts = useMemo(() => {
    let filtered = products.filter(product => {
      const matchesSearch = product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.description?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesSearch;
    });

    // Sort products
    const sorted = [...filtered];
    if (sortBy === 'popular') {
      sorted.sort((a, b) => (b.total_views || 0) - (a.total_views || 0));
    } else if (sortBy === 'commission') {
      sorted.sort((a, b) => (b.commission_rate || 0) - (a.commission_rate || 0));
    } else if (sortBy === 'sales') {
      sorted.sort((a, b) => (b.total_sales || 0) - (a.total_sales || 0));
    }

    return sorted;
  }, [products, searchTerm, sortBy]);

  // Skeleton loader component
  const ProductSkeleton = () => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-pulse">
      <div className="h-48 bg-gradient-to-br from-gray-200 to-gray-300"></div>
      <div className="p-5 space-y-3">
        <div className="h-6 bg-gray-200 rounded w-3/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="grid grid-cols-3 gap-2 mt-4">
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
        <div className="h-10 bg-gray-200 rounded mt-4"></div>
      </div>
    </div>
  );

  return (
    <>
      <SEOHead {...SEO_CONFIG.marketplace} />
      <div className="space-y-8">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white p-12 mb-12 shadow-2xl"
      >
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
          <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute top-[20%] left-[20%] w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="inline-flex items-center justify-center p-3 bg-white/10 backdrop-blur-md rounded-2xl mb-6 border border-white/20 shadow-xl"
          >
            <ShoppingBag className="text-pink-300 w-8 h-8" />
          </motion.div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-pink-100 to-purple-200 drop-shadow-sm">
            Marketplace Premium
          </h1>
          
          <p className="text-xl md:text-2xl text-purple-100 mb-8 font-light leading-relaxed">
            Découvrez des produits exclusifs, collaborez avec des marques d'élite et maximisez vos revenus.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <button className="px-8 py-4 bg-white text-purple-900 rounded-full font-bold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center">
              Explorer les Offres <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <button className="px-8 py-4 bg-purple-800/50 backdrop-blur-md text-white rounded-full font-bold text-lg border border-white/20 hover:bg-purple-800/70 transition-all duration-300">
              Comment ça marche ?
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { icon: Package, label: "Produits Disponibles", value: products.length, color: "text-purple-600", bg: "bg-purple-100" },
          { icon: TrendingUp, label: "Commission Moyenne", value: "15-25%", color: "text-green-600", bg: "bg-green-100" },
          { icon: Users, label: "Affiliés Actifs", value: "2.5K+", color: "text-indigo-600", bg: "bg-indigo-100" },
          { icon: Star, label: "Satisfaction Moyenne", value: "4.8/5", color: "text-orange-600", bg: "bg-orange-100" }
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
          >
            <div className="flex items-center space-x-4">
              <div className={`${stat.bg} p-4 rounded-xl`}>
                <stat.icon className={stat.color} size={28} />
              </div>
              <div>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm font-medium text-gray-500">{stat.label}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Filters & Search */}
      <div className="bg-white rounded-2xl shadow-xl p-6 mb-8 border border-gray-100">
        <div className="flex flex-col md:flex-row gap-6 items-center justify-between mb-8">
          {/* Search Bar */}
          <div className="relative w-full md:w-96 group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="Rechercher un produit, une marque..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-11 pr-4 py-4 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all duration-300 shadow-sm"
            />
          </div>

          {/* Sort Options */}
          <div className="flex items-center space-x-4 w-full md:w-auto">
            <div className="flex items-center space-x-2 bg-gray-50 px-4 py-3 rounded-xl border border-gray-200">
              <Filter className="text-gray-500" size={18} />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="bg-transparent border-none focus:ring-0 text-gray-700 font-medium cursor-pointer"
              >
                <option value="popular">🔥 Plus Populaires</option>
                <option value="commission">💰 Meilleure Commission</option>
                <option value="sales">📈 Meilleures Ventes</option>
              </select>
            </div>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-3 pb-2">
          {categories.map((category) => (
            <motion.button
              key={category.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-6 py-3 rounded-full font-semibold transition-all duration-300 flex items-center space-x-2 ${
                selectedCategory === category.id
                  ? 'bg-gray-900 text-white shadow-lg ring-2 ring-purple-500 ring-offset-2'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100 hover:text-gray-900 border border-gray-200'
              }`}
            >
              <span className="text-lg">{category.icon}</span>
              <span>{category.name}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[...Array(6)].map((_, i) => (
            <ProductSkeleton key={i} />
          ))}
        </div>
      ) : filteredProducts.length === 0 ? (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-20 bg-white rounded-3xl shadow-sm border border-gray-100"
        >
          <div className="bg-gray-50 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
            <Package className="w-12 h-12 text-gray-300" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Aucun produit trouvé</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Nous n'avons pas trouvé de produits correspondant à vos critères. Essayez de modifier vos filtres.
          </p>
        </motion.div>
      ) : (
        <motion.div 
          layout
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          <AnimatePresence>
            {filteredProducts.map((product) => (
              <motion.div
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
                key={product.id}
                onClick={() => navigate(`/marketplace/product/${product.id}`)}
                className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-2xl hover:border-purple-200 transition-all duration-500 group cursor-pointer relative"
              >
                {/* Product Image */}
                <div className={`relative h-64 flex items-center justify-center overflow-hidden ${
                  (() => {
                    const images = getProductImages(product);
                    if (images.length > 0) return 'bg-gray-100';
                    
                    const categoryGradients = {
                      'Mode': 'bg-gradient-to-br from-pink-100 via-purple-100 to-indigo-100',
                      'Beauté': 'bg-gradient-to-br from-rose-100 via-pink-100 to-fuchsia-100',
                      'Technologie': 'bg-gradient-to-br from-blue-100 via-cyan-100 to-teal-100',
                      'Sport': 'bg-gradient-to-br from-orange-100 via-amber-100 to-yellow-100',
                      'Alimentation': 'bg-gradient-to-br from-green-100 via-emerald-100 to-lime-100',
                      'Maison': 'bg-gradient-to-br from-indigo-100 via-violet-100 to-purple-100'
                    };
                    return categoryGradients[product.category] || 'bg-gradient-to-br from-gray-100 to-gray-200';
                  })()
                }`}>
                  {/* Overlay on Hover */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 z-10" />
                  
                  {(() => {
                    const images = getProductImages(product);
                    const hasImage = images.length > 0;

                    if (hasImage) {
                      return (
                        <img
                          src={images[0]}
                          alt={product.name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            const placeholder = e.target.nextElementSibling;
                            if (placeholder) placeholder.style.display = 'block';
                          }}
                        />
                      );
                    }
                    
                    const categoryIcons = {
                      'Mode': '👕', 'Beauté': '💄', 'Technologie': '📱',
                      'Sport': '⚽', 'Alimentation': '🍔', 'Maison': '🏠'
                    };
                    
                    const icon = categoryIcons[product.category] || '📦';
                    
                    return (
                      <div className="text-center transform group-hover:scale-110 transition-transform duration-500">
                        <div className="text-8xl mb-4 drop-shadow-sm">{icon}</div>
                        <div className="text-lg font-bold text-gray-400 uppercase tracking-widest">{product.category}</div>
                      </div>
                    );
                  })()}
                  
                  {/* Badges */}
                  <div className="absolute top-4 right-4 z-20">
                    <motion.button 
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="bg-white/90 backdrop-blur-md p-3 rounded-full shadow-lg hover:bg-pink-50 transition-colors"
                    >
                      <Heart className="w-5 h-5 text-gray-400 hover:text-pink-500 transition-colors" />
                    </motion.button>
                  </div>
                  
                  <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
                    <span className="bg-white/90 backdrop-blur-md px-4 py-1.5 rounded-full text-xs font-bold text-gray-900 shadow-sm border border-gray-100 uppercase tracking-wider">
                      {product.category}
                    </span>
                    {product.commission_rate >= 20 && (
                      <span className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-lg flex items-center gap-1">
                        <Zap size={12} fill="currentColor" /> {product.commission_rate}% Com.
                      </span>
                    )}
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-6">
                  <div className="mb-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-gray-900 line-clamp-1 group-hover:text-purple-600 transition-colors">
                        {product.name}
                      </h3>
                      <div className="text-xl font-bold text-purple-600 whitespace-nowrap ml-2">
                        {product.price?.toLocaleString()} {product.currency || '€'}
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 font-medium flex items-center">
                      <span className="w-2 h-2 rounded-full bg-gray-300 mr-2"></span>
                      {product.merchant_name}
                    </p>
                  </div>

                  <p className="text-sm text-gray-600 mb-6 line-clamp-2 leading-relaxed h-10">
                    {product.description}
                  </p>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-3 gap-4 mb-6 bg-gray-50 rounded-xl p-3 border border-gray-100">
                    <div className="text-center">
                      <div className="text-xs text-gray-400 uppercase font-bold mb-1">Vues</div>
                      <div className="font-bold text-gray-900">{product.total_views || 0}</div>
                    </div>
                    <div className="text-center border-l border-gray-200">
                      <div className="text-xs text-gray-400 uppercase font-bold mb-1">Clics</div>
                      <div className="font-bold text-gray-900">{product.total_clicks || 0}</div>
                    </div>
                    <div className="text-center border-l border-gray-200">
                      <div className="text-xs text-gray-400 uppercase font-bold mb-1">Ventes</div>
                      <div className="font-bold text-gray-900">{product.total_sales || 0}</div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3">
                    {user?.role === 'influencer' ? (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleGenerateLink(product.id);
                        }}
                        className="flex-1 bg-gray-900 text-white py-3.5 rounded-xl font-bold hover:bg-gray-800 shadow-lg hover:shadow-xl transition-all flex items-center justify-center group/btn"
                      >
                        <Sparkles className="w-4 h-4 mr-2 text-yellow-400 group-hover/btn:animate-spin" />
                        Promouvoir
                      </motion.button>
                    ) : (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={(e) => e.stopPropagation()}
                        className="flex-1 bg-white text-gray-900 border-2 border-gray-900 py-3.5 rounded-xl font-bold hover:bg-gray-50 transition-all"
                      >
                        Voir Détails
                      </motion.button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      {/* CTA Banner */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative overflow-hidden rounded-3xl bg-gray-900 text-white p-12 text-center shadow-2xl"
      >
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
          <div className="absolute top-[-50%] left-[-20%] w-[800px] h-[800px] bg-purple-600/30 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-[-50%] right-[-20%] w-[800px] h-[800px] bg-pink-600/30 rounded-full mix-blend-screen filter blur-3xl animate-blob animation-delay-2000"></div>
        </div>

        <div className="relative z-10 max-w-3xl mx-auto">
          <h3 className="text-4xl font-bold mb-6">Vous êtes une marque ambitieuse ?</h3>
          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            Rejoignez des milliers d'entreprises qui propulsent leur croissance grâce à notre réseau d'influenceurs d'élite.
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/register')}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-10 py-4 rounded-full font-bold text-lg shadow-lg hover:shadow-purple-500/50 transition-all duration-300"
          >
            Commencer Maintenant
          </motion.button>
        </div>
      </motion.div>
      </div>
    </>
  );
});

MarketplaceNew.displayName = 'MarketplaceNew';

export default MarketplaceNew;
