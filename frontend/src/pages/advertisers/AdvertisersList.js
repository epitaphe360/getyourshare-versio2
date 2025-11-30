import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import { formatCurrency, formatDate } from '../../utils/helpers';
import { 
  Plus, Search, Building2, TrendingUp, Wallet, 
  Users, Filter, MoreVertical, Eye, Edit, Trash2,
  ChevronDown, Globe, Mail, Calendar, ShoppingBag,
  ArrowUpRight, ArrowDownRight, RefreshCw
} from 'lucide-react';

const AdvertisersList = () => {
  const navigate = useNavigate();
  const [advertisers, setAdvertisers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [openMenuId, setOpenMenuId] = useState(null);

  useEffect(() => {
    fetchAdvertisers();
  }, []);

  const fetchAdvertisers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/advertisers');
      const data = response.data?.data || response.data || [];
      setAdvertisers(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching advertisers:', error);
      setAdvertisers([]);
    } finally {
      setLoading(false);
    }
  };

  // Calculate stats
  const stats = {
    total: advertisers.length,
    active: advertisers.filter(a => a.status === 'active').length,
    totalBalance: advertisers.reduce((sum, a) => sum + (parseFloat(a.balance) || 0), 0),
    totalSpent: advertisers.reduce((sum, a) => sum + (parseFloat(a.total_spent) || 0), 0),
    totalCampaigns: advertisers.reduce((sum, a) => sum + (parseInt(a.campaigns_count) || 0), 0),
  };

  const filteredAdvertisers = (advertisers || [])
    .filter(adv => {
      const companyName = adv?.company_name || '';
      const email = adv?.email || '';
      const matchesSearch = companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           email.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || adv.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      if (sortBy === 'balance' || sortBy === 'total_spent') {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      }
      if (sortOrder === 'asc') return aVal > bVal ? 1 : -1;
      return aVal < bVal ? 1 : -1;
    });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'pending': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'suspended': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active': return 'Actif';
      case 'pending': return 'En attente';
      case 'suspended': return 'Suspendu';
      default: return status;
    }
  };

  const getInitials = (name) => {
    if (!name || name === 'Inconnu') return '?';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  };

  const getAvatarColor = (name) => {
    const colors = [
      'from-violet-500 to-purple-600',
      'from-blue-500 to-cyan-600',
      'from-emerald-500 to-teal-600',
      'from-orange-500 to-amber-600',
      'from-pink-500 to-rose-600',
      'from-indigo-500 to-blue-600',
    ];
    const index = (name || '').charCodeAt(0) % colors.length;
    return colors[index];
  };

  return (
    <div className="space-y-6 p-1" data-testid="advertisers-list">
      {/* Header Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 rounded-2xl p-8 text-white">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                <Building2 size={28} />
              </div>
              <div>
                <h1 className="text-3xl font-bold">Annonceurs</h1>
                <p className="text-white/80 mt-1">Gérez et suivez vos partenaires commerciaux</p>
              </div>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button 
              onClick={fetchAdvertisers}
              className="flex items-center gap-2 px-4 py-2.5 bg-white/20 backdrop-blur-sm hover:bg-white/30 rounded-xl transition-all"
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              <span className="hidden sm:inline">Actualiser</span>
            </button>
            <button 
              onClick={() => navigate('/advertisers/registrations')}
              className="flex items-center gap-2 px-5 py-2.5 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-white/90 transition-all shadow-lg shadow-black/20"
            >
              <Plus size={20} />
              <span>Nouvel Annonceur</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="p-2.5 bg-indigo-100 rounded-lg">
              <Users className="text-indigo-600" size={22} />
            </div>
            <span className="flex items-center text-sm text-emerald-600 font-medium">
              <ArrowUpRight size={16} />
              +12%
            </span>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            <p className="text-sm text-gray-500 mt-1">Total Annonceurs</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="p-2.5 bg-emerald-100 rounded-lg">
              <TrendingUp className="text-emerald-600" size={22} />
            </div>
            <span className="text-sm text-gray-500 font-medium">{Math.round(stats.active / stats.total * 100) || 0}%</span>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-bold text-gray-900">{stats.active}</p>
            <p className="text-sm text-gray-500 mt-1">Annonceurs Actifs</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="p-2.5 bg-purple-100 rounded-lg">
              <Wallet className="text-purple-600" size={22} />
            </div>
            <span className="flex items-center text-sm text-emerald-600 font-medium">
              <ArrowUpRight size={16} />
              +8%
            </span>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalBalance)}</p>
            <p className="text-sm text-gray-500 mt-1">Solde Total</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div className="p-2.5 bg-orange-100 rounded-lg">
              <ShoppingBag className="text-orange-600" size={22} />
            </div>
            <span className="text-sm text-gray-500 font-medium">{stats.totalCampaigns} campagnes</span>
          </div>
          <div className="mt-4">
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(stats.totalSpent)}</p>
            <p className="text-sm text-gray-500 mt-1">Total Dépensé</p>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Rechercher par nom ou email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              data-testid="search-input"
            />
          </div>
          
          <div className="flex gap-3">
            <div className="relative">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="appearance-none pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
              >
                <option value="all">Tous les statuts</option>
                <option value="active">Actifs</option>
                <option value="pending">En attente</option>
                <option value="suspended">Suspendus</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={18} />
            </div>

            <div className="relative">
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field);
                  setSortOrder(order);
                }}
                className="appearance-none pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer"
              >
                <option value="created_at-desc">Plus récent</option>
                <option value="created_at-asc">Plus ancien</option>
                <option value="balance-desc">Solde (décroissant)</option>
                <option value="balance-asc">Solde (croissant)</option>
                <option value="total_spent-desc">Dépenses (décroissant)</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={18} />
            </div>
          </div>
        </div>
      </div>

      {/* Advertisers List */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-500">Chargement des annonceurs...</p>
          </div>
        ) : filteredAdvertisers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="p-4 bg-gray-100 rounded-full mb-4">
              <Users className="text-gray-400" size={32} />
            </div>
            <h3 className="text-lg font-semibold text-gray-700 mb-1">Aucun annonceur trouvé</h3>
            <p className="text-gray-500 mb-4">Modifiez vos filtres ou ajoutez un nouvel annonceur</p>
            <button 
              onClick={() => navigate('/advertisers/registrations')}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
            >
              <Plus size={18} />
              Ajouter un annonceur
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {/* Table Header */}
            <div className="hidden md:grid md:grid-cols-12 gap-4 px-6 py-4 bg-gray-50 text-sm font-medium text-gray-500 uppercase tracking-wider">
              <div className="col-span-4">Annonceur</div>
              <div className="col-span-2 text-center">Statut</div>
              <div className="col-span-1 text-center">Campagnes</div>
              <div className="col-span-2 text-right">Solde</div>
              <div className="col-span-2 text-right">Dépensé</div>
              <div className="col-span-1"></div>
            </div>

            {/* Table Rows */}
            {filteredAdvertisers.map((advertiser) => (
              <div 
                key={advertiser.id}
                className="group grid grid-cols-1 md:grid-cols-12 gap-4 px-6 py-5 hover:bg-gray-50 transition-colors items-center"
              >
                {/* Advertiser Info */}
                <div className="col-span-4 flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getAvatarColor(advertiser.company_name)} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                    {getInitials(advertiser.company_name)}
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {advertiser.company_name || 'Inconnu'}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500 mt-0.5">
                      <Mail size={14} />
                      <span className="truncate">{advertiser.email}</span>
                    </div>
                    {advertiser.country && (
                      <div className="flex items-center gap-2 text-sm text-gray-400 mt-0.5">
                        <Globe size={14} />
                        <span>{advertiser.country}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Status */}
                <div className="col-span-2 flex justify-center">
                  <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border ${getStatusColor(advertiser.status)}`}>
                    <span className={`w-1.5 h-1.5 rounded-full mr-2 ${advertiser.status === 'active' ? 'bg-emerald-500' : advertiser.status === 'pending' ? 'bg-amber-500' : 'bg-red-500'}`}></span>
                    {getStatusLabel(advertiser.status)}
                  </span>
                </div>

                {/* Campaigns */}
                <div className="col-span-1 text-center">
                  <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 font-semibold">
                    {advertiser.campaigns_count || 0}
                  </span>
                </div>

                {/* Balance */}
                <div className="col-span-2 text-right">
                  <p className="font-semibold text-gray-900">{formatCurrency(advertiser.balance)}</p>
                  <p className="text-xs text-gray-500 mt-0.5">Disponible</p>
                </div>

                {/* Total Spent */}
                <div className="col-span-2 text-right">
                  <p className="font-semibold text-gray-900">{formatCurrency(advertiser.total_spent)}</p>
                  <p className="text-xs text-gray-500 mt-0.5 flex items-center justify-end gap-1">
                    <Calendar size={12} />
                    {formatDate(advertiser.created_at)}
                  </p>
                </div>

                {/* Actions */}
                <div className="col-span-1 flex justify-end relative">
                  <button 
                    onClick={() => setOpenMenuId(openMenuId === advertiser.id ? null : advertiser.id)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <MoreVertical size={20} className="text-gray-400" />
                  </button>

                  {openMenuId === advertiser.id && (
                    <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-10">
                      <button 
                        onClick={() => {
                          navigate(`/advertisers/${advertiser.id}`);
                          setOpenMenuId(null);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <Eye size={16} />
                        Voir le profil
                      </button>
                      <button 
                        onClick={() => {
                          navigate(`/advertisers/${advertiser.id}/edit`);
                          setOpenMenuId(null);
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <Edit size={16} />
                        Modifier
                      </button>
                      <hr className="my-2 border-gray-100" />
                      <button 
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                        Supprimer
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Footer */}
        {!loading && filteredAdvertisers.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Affichage de <span className="font-medium text-gray-700">{filteredAdvertisers.length}</span> annonceur{filteredAdvertisers.length > 1 ? 's' : ''}
              {searchTerm && ` pour "${searchTerm}"`}
            </p>
            <div className="flex gap-2">
              <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition">
                Précédent
              </button>
              <button className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                1
              </button>
              <button className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition">
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvertisersList;
