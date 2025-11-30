import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Tag, TrendingUp, Users, DollarSign, Edit, Trash2, Copy, Check } from 'lucide-react';
import api from '../../utils/api';

const AdminCoupons = () => {
  const [coupons, setCoupons] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    code: '',
    type: 'percentage',
    value: '',
    duration_type: 'once',
    duration_months: 1,
    max_redemptions: '',
    max_redemptions_per_user: 1,
    valid_from: new Date().toISOString().slice(0, 16),
    valid_until: '',
    new_customers_only: false,
    description: ''
  });

  useEffect(() => {
    fetchCoupons();
    fetchStats();
  }, []);

  const fetchCoupons = async () => {
    try {
      const response = await api.get('/api/coupons/admin/all');
      if (response.data.success) {
        setCoupons(response.data.coupons);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching coupons:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/coupons/admin/stats');
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        code: formData.code.toUpperCase(),
        value: parseFloat(formData.value),
        max_redemptions: formData.max_redemptions ? parseInt(formData.max_redemptions) : null,
        valid_until: formData.valid_until || null
      };
      
      const response = await api.post('/api/coupons/admin/create', payload);
      if (response.data.success) {
        fetchCoupons();
        fetchStats();
        setShowCreateModal(false);
        // Reset form
        setFormData({
          code: '',
          type: 'percentage',
          value: '',
          duration_type: 'once',
          duration_months: 1,
          max_redemptions: '',
          max_redemptions_per_user: 1,
          valid_from: new Date().toISOString().slice(0, 16),
          valid_until: '',
          new_customers_only: false,
          description: ''
        });
      }
    } catch (error) {
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    }
  };

  const toggleActive = async (couponId, currentStatus) => {
    try {
      await api.patch(`/api/coupons/admin/${couponId}`, { is_active: !currentStatus });
      fetchCoupons();
    } catch (error) {
      alert('Erreur lors de la mise à jour');
    }
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    // TODO: Show toast
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Coupons</h1>
          <p className="text-gray-600 mt-2">Créez et gérez vos codes promotionnels</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-all shadow-lg"
        >
          <Plus size={20} />
          Nouveau Coupon
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Coupons Actifs</p>
                <h3 className="text-2xl font-bold text-blue-600">{stats.active_coupons}</h3>
              </div>
              <Tag className="text-blue-600" size={32} />
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Utilisations</p>
                <h3 className="text-2xl font-bold text-green-600">{stats.total_redemptions}</h3>
              </div>
              <TrendingUp className="text-green-600" size={32} />
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Utilisateurs Uniques</p>
                <h3 className="text-2xl font-bold text-purple-600">{stats.unique_users}</h3>
              </div>
              <Users className="text-purple-600" size={32} />
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Remises Totales</p>
                <h3 className="text-2xl font-bold text-orange-600">{stats.total_discount_given.toLocaleString()} MAD</h3>
              </div>
              <DollarSign className="text-orange-600" size={32} />
            </div>
          </motion.div>
        </div>
      )}

      {/* Coupons Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Valeur</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Utilisations</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Validité</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {coupons.map((coupon) => (
              <tr key={coupon.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-blue-600">{coupon.code}</span>
                    <button onClick={() => copyCode(coupon.code)} className="text-gray-400 hover:text-blue-600">
                      <Copy size={16} />
                    </button>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-700">
                    {coupon.type}
                  </span>
                </td>
                <td className="px-6 py-4 font-semibold">
                  {coupon.type === 'percentage' ? `${coupon.value}%` : `${coupon.value} MAD`}
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-semibold">{coupon.stats?.redemptions || 0} utilisations</div>
                    {coupon.max_redemptions && (
                      <div className="text-gray-500">/ {coupon.max_redemptions} max</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {coupon.valid_until ? new Date(coupon.valid_until).toLocaleDateString('fr-FR') : 'Illimitée'}
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => toggleActive(coupon.id, coupon.is_active)}
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      coupon.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {coupon.is_active ? 'Actif' : 'Inactif'}
                  </button>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Edit size={18} />
                    </button>
                    <button className="text-red-600 hover:text-red-800">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold">Créer un Coupon</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Code *</label>
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({...formData, code: e.target.value.toUpperCase()})}
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="PROMO2024"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Type *</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="percentage">Pourcentage</option>
                    <option value="fixed">Montant fixe</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Valeur *</label>
                <input
                  type="number"
                  value={formData.value}
                  onChange={(e) => setFormData({...formData, value: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  placeholder={formData.type === 'percentage' ? '20' : '100'}
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Durée</label>
                  <select
                    value={formData.duration_type}
                    onChange={(e) => setFormData({...formData, duration_type: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                  >
                    <option value="once">Une fois</option>
                    <option value="repeating">Récurrent</option>
                    <option value="forever">À vie</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Limite d'utilisations</label>
                  <input
                    type="number"
                    value={formData.max_redemptions}
                    onChange={(e) => setFormData({...formData, max_redemptions: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg"
                    placeholder="Illimité"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg"
                  rows={3}
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowCreateModal(false)} className="flex-1 px-4 py-2 border rounded-lg">
                  Annuler
                </button>
                <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Créer le Coupon
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AdminCoupons;
