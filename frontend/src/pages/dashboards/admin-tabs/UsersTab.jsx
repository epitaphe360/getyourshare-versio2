import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../../context/ToastContext';
import api from '../../../utils/api';
import {
  Users, ShoppingBag, Eye, Edit, Lock, Unlock, Mail, Download, Search, Filter, Plus
} from 'lucide-react';
import { formatCurrency, formatDate, exportToCSV, getInitials, generateColorFromString } from '../../../utils/helpers';
import BaseModal from '../../../components/modals/BaseModal';

const UsersTab = ({ stats, refreshKey, onRefresh }) => {
  const navigate = useNavigate();
  const toast = useToast();
  const [merchants, setMerchants] = useState([]);
  const [influencers, setInfluencers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const fetchUsers = useCallback(async (signal = null) => {
    try {
      setLoading(true);
      const config = signal ? { signal } : {};
      const [merchantsRes, influencersRes] = await Promise.allSettled([
        api.get('/api/admin/users?role=merchant', config),
        api.get('/api/admin/users?role=influencer', config)
      ]);

      if (merchantsRes.status === 'fulfilled') {
        setMerchants(merchantsRes.value.data.users || merchantsRes.value.data || []);
      }
      if (influencersRes.status === 'fulfilled') {
        setInfluencers(influencersRes.value.data.users || influencersRes.value.data || []);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur chargement utilisateurs:', error);
        toast.error('Impossible de charger les utilisateurs');
      }
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    const controller = new AbortController();
    fetchUsers(controller.signal);
    return () => controller.abort();
  }, [fetchUsers, refreshKey]);

  const handleToggleStatus = async (user) => {
    try {
      const newStatus = user.status === 'active' ? 'suspended' : 'active';
      await api.patch(`/api/admin/users/${user.id}/status`, { status: newStatus });
      toast.success(`Utilisateur ${newStatus === 'active' ? 'activé' : 'suspendu'} avec succès`);
      fetchUsers();
    } catch (error) {
      toast.error('Impossible de modifier le statut');
    }
  };

  const handleViewDetails = (user) => {
    setSelectedUser(user);
    setShowDetailModal(true);
  };

  const filteredMerchants = merchants.filter(m => {
    const matchesSearch = !searchTerm ||
      m.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'active' && m.status === 'active') ||
      (statusFilter === 'inactive' && m.status !== 'active');
    return matchesSearch && matchesStatus;
  });

  const filteredInfluencers = influencers.filter(i => {
    const matchesSearch = !searchTerm ||
      i.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'active' && i.status === 'active') ||
      (statusFilter === 'inactive' && i.status !== 'active');
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Filters Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher par nom, email, entreprise..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">Tous les statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>
          <button
            onClick={() => navigate('/admin/users')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 transition-colors"
          >
            <Plus size={20} />
            Gérer les utilisateurs
          </button>
        </div>
      </div>

      {/* Merchants Table */}
      <UserTable
        title="Annonceurs"
        icon={<ShoppingBag size={20} className="text-indigo-600" />}
        users={filteredMerchants}
        loading={loading}
        onToggleStatus={handleToggleStatus}
        onViewDetails={handleViewDetails}
        onExport={() => exportToCSV(filteredMerchants, 'annonceurs')}
        roleType="merchant"
      />

      {/* Influencers Table */}
      <UserTable
        title="Influenceurs"
        icon={<Users size={20} className="text-pink-600" />}
        users={filteredInfluencers}
        loading={loading}
        onToggleStatus={handleToggleStatus}
        onViewDetails={handleViewDetails}
        onExport={() => exportToCSV(filteredInfluencers, 'influenceurs')}
        roleType="influencer"
      />

      {/* User Detail Modal */}
      <BaseModal
        isOpen={showDetailModal}
        onClose={() => {
          setShowDetailModal(false);
          setSelectedUser(null);
        }}
        title="Détails Utilisateur"
        size="2xl"
      >
        {selectedUser && <UserDetails user={selectedUser} />}
      </BaseModal>
    </div>
  );
};

// Composant Table réutilisable
const UserTable = ({ title, icon, users, loading, onToggleStatus, onViewDetails, onExport, roleType }) => (
  <div className="bg-white rounded-lg shadow">
    <div className="p-6 border-b border-gray-200">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          {icon}
          {title} ({users.length})
        </h3>
        <button
          onClick={onExport}
          className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
        >
          <Download size={16} />
          Exporter
        </button>
      </div>
    </div>
    <div className="overflow-x-auto">
      {loading ? (
        <div className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : users.length === 0 ? (
        <div className="p-12 text-center text-gray-500">
          Aucun utilisateur trouvé
        </div>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {roleType === 'merchant' ? 'Entreprise' : 'Influenceur'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {roleType === 'merchant' ? 'Solde' : 'Gains'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {roleType === 'merchant' ? 'Campagnes' : 'Conversions'}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div
                      className="h-10 w-10 rounded-full flex items-center justify-center text-white font-semibold"
                      style={{ backgroundColor: generateColorFromString(user.email) }}
                    >
                      {getInitials(user.company_name || user.full_name || user.email)}
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {user.company_name || user.full_name || 'Sans nom'}
                      </div>
                      {user.username && (
                        <div className="text-sm text-gray-500">@{user.username}</div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {formatCurrency(user.balance || user.total_earnings || 0)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.campaigns_count || user.total_conversions || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    user.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.status === 'active' ? 'Actif' : 'Suspendu'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onViewDetails(user)}
                      className="text-blue-600 hover:text-blue-700"
                      title="Voir détails"
                    >
                      <Eye size={18} />
                    </button>
                    <button
                      onClick={() => onToggleStatus(user)}
                      className={user.status === 'active' ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'}
                      title={user.status === 'active' ? 'Suspendre' : 'Activer'}
                    >
                      {user.status === 'active' ? <Lock size={18} /> : <Unlock size={18} />}
                    </button>
                    <a
                      href={`mailto:${user.email}`}
                      className="text-gray-600 hover:text-gray-700"
                      title="Envoyer email"
                    >
                      <Mail size={18} />
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  </div>
);

// Composant de détails utilisateur
const UserDetails = ({ user }) => (
  <div className="space-y-6">
    <div>
      <h4 className="font-semibold mb-3">Informations Générales</h4>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-600">Nom</p>
          <p className="font-medium">{user.full_name || user.company_name || 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Email</p>
          <p className="font-medium">{user.email}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Téléphone</p>
          <p className="font-medium">{user.phone || 'N/A'}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Date d'inscription</p>
          <p className="font-medium">{formatDate(user.created_at)}</p>
        </div>
      </div>
    </div>

    <div>
      <h4 className="font-semibold mb-3">Finances</h4>
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600">Solde actuel</p>
        <p className="text-2xl font-bold text-gray-900">
          {formatCurrency(user.balance || user.total_earnings || 0)}
        </p>
      </div>
    </div>
  </div>
);

export default UsersTab;
