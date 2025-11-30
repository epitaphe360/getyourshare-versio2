import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import Card from '../../components/common/Card';
import { 
  Search, Filter, Building, TrendingUp, 
  DollarSign, Package, Users, Eye, MoreVertical 
} from 'lucide-react';

const MerchantsList = () => {
  const navigate = useNavigate();
  const [merchants, setMerchants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');

  useEffect(() => {
    fetchMerchants();
  }, []);

  const fetchMerchants = async () => {
    try {
      const response = await api.get('/api/merchants');
      setMerchants(response.data.merchants || []);
    } catch (error) {
      console.error('Error fetching merchants:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredMerchants = merchants.filter(merchant => {
    const companyName = merchant.company_name || '';
    const category = merchant.category || '';
    const matchesSearch = companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || merchant.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', 'Mode et lifestyle', 'Beauté et bien-être', 'Technologie', 'Sport et fitness'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gérez vos annonceurs</h1>
          <p className="text-gray-600 mt-2">Suivez et gérez les comptes annonceurs</p>
        </div>
        <button 
          onClick={() => navigate('/advertisers/registrations')}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition font-semibold flex items-center gap-2"
        >
          <Users size={20} />
          Nouvel Annonceur
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-100 p-3 rounded-lg">
              <Building className="text-indigo-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{merchants.length}</div>
              <div className="text-sm text-gray-600">Annonceurs Actifs</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-green-100 p-3 rounded-lg">
              <DollarSign className="text-green-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {merchants.reduce((sum, m) => sum + (m.total_spent || 0), 0).toLocaleString()}€
              </div>
              <div className="text-sm text-gray-600">Total Dépensé</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-purple-100 p-3 rounded-lg">
              <Package className="text-purple-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {merchants.reduce((sum, m) => sum + (m.campaigns_count || 0), 0)}
              </div>
              <div className="text-sm text-gray-600">Campagnes Actives</div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center space-x-3">
            <div className="bg-orange-100 p-3 rounded-lg">
              <TrendingUp className="text-orange-600" size={24} />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                 {merchants.reduce((sum, m) => sum + (m.balance || 0), 0).toLocaleString()}€
              </div>
              <div className="text-sm text-gray-600">Solde Total</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher un annonceur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </Card>

      {/* Merchants Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Entreprise
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pays
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campagnes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Solde
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Dépensé
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Créé le
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMerchants.map((merchant) => (
                <tr key={merchant.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        {merchant.logo_url ? (
                          <img className="h-10 w-10 rounded-full object-cover border border-gray-200" src={merchant.logo_url} alt="" />
                        ) : (
                          <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold border border-indigo-200">
                            {merchant.company_name ? merchant.company_name.charAt(0).toUpperCase() : <Building size={18} />}
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="font-medium text-gray-900">{merchant.company_name || 'Entreprise Inconnue'}</div>
                        <div className="text-sm text-gray-500">{merchant.email || 'email@example.com'}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700">{merchant.country || 'FR'}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${
                      (merchant.status || 'active') === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {merchant.status === 'active' ? 'Actif' : 'En attente'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 font-medium text-center w-8">
                      {merchant.campaigns_count || 0}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {(merchant.balance || 0).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {(merchant.total_spent || 0).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {merchant.created_at ? new Date(merchant.created_at).toLocaleDateString('fr-FR', {
                      day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                    }) : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => navigate(`/merchants/${merchant.id}`)}
                      className="text-indigo-600 hover:text-indigo-900 p-2 hover:bg-indigo-50 rounded-full transition-colors"
                      title="Voir les détails"
                    >
                      <Eye size={18} />
                    </button>
                    <button 
                      className="text-gray-400 hover:text-gray-600 p-2 hover:bg-gray-100 rounded-full transition-colors ml-1"
                      title="Plus d'options"
                    >
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default MerchantsList;
