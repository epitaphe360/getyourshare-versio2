import React, { useState, useEffect } from 'react';
import { Search, MapPin, Package, ArrowRight } from 'lucide-react';
import api from '../utils/api';
import { useNavigate } from 'react-router-dom';

const PublicServices = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadServices();
    loadCategories();
  }, [selectedCategory]);

  const loadServices = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('categorie_id', selectedCategory);
      if (searchTerm) params.append('search', searchTerm);

      const response = await api.get(`/api/public/services?${params}`);
      setServices(response.data.services || []);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await api.get('/api/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleSearch = () => {
    loadServices();
  };

  const filteredServices = services.filter(service =>
    searchTerm === '' ||
    service.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">Trouvez le service parfait</h1>
          <p className="text-xl mb-8">Découvrez des services de qualité près de chez vous</p>

          {/* Search Bar */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg p-2 flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher un service..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full pl-10 pr-4 py-3 rounded-lg focus:outline-none text-gray-800"
                />
              </div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-3 rounded-lg focus:outline-none text-gray-800"
              >
                <option value="">Toutes catégories</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
              <button
                onClick={handleSearch}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition font-medium"
              >
                Rechercher
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="container mx-auto px-4 py-12">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredServices.length === 0 ? (
          <div className="text-center py-20">
            <Package className="mx-auto text-gray-400 mb-4" size={64} />
            <h3 className="text-2xl font-semibold text-gray-700 mb-2">Aucun service trouvé</h3>
            <p className="text-gray-600">Essayez avec d'autres critères de recherche</p>
          </div>
        ) : (
          <>
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                {filteredServices.length} service{filteredServices.length > 1 ? 's' : ''} disponible{filteredServices.length > 1 ? 's' : ''}
              </h2>
              <p className="text-gray-600">Cliquez sur un service pour faire une demande gratuite</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredServices.map(service => (
                <div
                  key={service.id}
                  onClick={() => navigate(`/marketplace/services/${service.id}`)}
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition cursor-pointer group"
                >
                  {/* Image */}
                  <div className="relative h-48 bg-gray-200">
                    {service.images && service.images.length > 0 ? (
                      <img
                        src={service.images[0]}
                        alt={service.nom}
                        className="w-full h-full object-cover group-hover:scale-105 transition"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package size={48} className="text-gray-400" />
                      </div>
                    )}
                    {service.categories?.name && (
                      <div className="absolute top-3 left-3">
                        <span className="bg-white/90 backdrop-blur px-3 py-1 rounded-full text-sm font-medium text-gray-800">
                          {service.categories.name}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="p-5">
                    <h3 className="text-xl font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition">
                      {service.nom}
                    </h3>

                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {service.description || 'Aucune description disponible'}
                    </p>

                    <div className="flex items-center justify-between mb-4">
                      {service.localisation && (
                        <div className="flex items-center text-gray-600 text-sm">
                          <MapPin size={16} className="mr-1" />
                          {service.localisation}
                        </div>
                      )}
                      {service.users?.company_name && (
                        <div className="text-sm text-gray-500">
                          {service.users.company_name}
                        </div>
                      )}
                    </div>

                    <div className="pt-4 border-t">
                      <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition flex items-center justify-center gap-2 font-medium group">
                        Demander ce service
                        <ArrowRight size={18} className="group-hover:translate-x-1 transition" />
                      </button>
                      <p className="text-xs text-center text-gray-500 mt-2">
                        ✓ Gratuit • Sans engagement
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PublicServices;
