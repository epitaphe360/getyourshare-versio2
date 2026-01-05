import React, { useState, useEffect } from 'react';
import { X, Upload, Plus, Trash2 } from 'lucide-react';
import api from '../../utils/api';
import { toast } from 'react-toastify';

const ServiceFormModal = ({ show, onClose, onSuccess, service, mode }) => {
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  
  const [formData, setFormData] = useState({
    nom: '',
    description: '',
    images: [],
    categorie_id: '',
    localisation: '',
    conditions: '',
    depot_initial: '',
    prix_par_lead: '',
    commission_rate: 20,
    formulaire_champs: [],
    date_expiration: ''
  });

  useEffect(() => {
    if (show) {
      loadCategories();
      if (mode === 'edit' && service) {
        setFormData({
          nom: service.nom || '',
          description: service.description || '',
          images: service.images || [],
          categorie_id: service.categorie_id || '',
          localisation: service.localisation || '',
          conditions: service.conditions || '',
          depot_initial: service.depot_initial || '',
          prix_par_lead: service.prix_par_lead || '',
          commission_rate: service.commission_rate || 20,
          formulaire_champs: service.formulaire_champs || [],
          date_expiration: service.date_expiration ? service.date_expiration.split('T')[0] : ''
        });
      }
    }
  }, [show, service, mode]);

  const loadCategories = async () => {
    try {
      const response = await api.get('/api/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Erreur chargement catégories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (mode === 'create') {
        await api.post('/api/admin/services', formData);
        toast.success('Service créé avec succès !');
      } else {
        await api.put(`/api/admin/services/${service.id}`, formData);
        toast.success('Service mis à jour avec succès !');
      }
      onSuccess();
    } catch (error) {
      console.error('Erreur:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally {
      setLoading(false);
    }
  };

  const addImage = () => {
    const url = prompt('URL de l\'image:');
    if (url) {
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, url]
      }));
    }
  };

  const removeImage = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  if (!show) return null;

  const leadsEstimes = formData.depot_initial && formData.prix_par_lead
    ? Math.floor(parseFloat(formData.depot_initial) / parseFloat(formData.prix_par_lead))
    : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">
            {mode === 'create' ? '➕ Créer un Service' : '✏️ Modifier le Service'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Info de base */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-700">📝 Informations du Service</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom du service *
              </label>
              <input
                type="text"
                required
                value={formData.nom}
                onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Massage relaxant 1h"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Décrivez le service en détail..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Catégorie
                </label>
                <select
                  value={formData.categorie_id}
                  onChange={(e) => setFormData({ ...formData, categorie_id: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Sélectionner...</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Localisation
                </label>
                <input
                  type="text"
                  value={formData.localisation}
                  onChange={(e) => setFormData({ ...formData, localisation: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Paris 15ème"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Images
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.images.map((img, index) => (
                  <div key={index} className="relative group">
                    <img src={img} alt="" className="w-20 h-20 object-cover rounded" />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addImage}
                  className="w-20 h-20 border-2 border-dashed rounded flex items-center justify-center hover:bg-gray-50"
                >
                  <Plus size={24} className="text-gray-400" />
                </button>
              </div>
            </div>
          </div>

          {/* Tarification */}
          <div className="space-y-4 bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-700">💰 Système de Paiement par Lead</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Dépôt de garantie (€) *
                </label>
                <input
                  type="number"
                  required
                  step="0.01"
                  min="0"
                  value={formData.depot_initial}
                  onChange={(e) => setFormData({ ...formData, depot_initial: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="1000"
                />
                <p className="text-xs text-gray-500 mt-1">Montant que le marchand verse</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prix par lead (€) *
                </label>
                <input
                  type="number"
                  required
                  step="0.01"
                  min="0"
                  value={formData.prix_par_lead}
                  onChange={(e) => setFormData({ ...formData, prix_par_lead: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="50"
                />
                <p className="text-xs text-gray-500 mt-1">Prix par demande client</p>
              </div>
            </div>

            {leadsEstimes > 0 && (
              <div className="bg-white p-3 rounded border border-blue-200">
                <p className="text-sm text-gray-700">
                  📊 <strong>{leadsEstimes} leads</strong> pourront être générés avec ce dépôt
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Commission GetYourShare ({formData.commission_rate}%): {(parseFloat(formData.depot_initial || 0) * parseFloat(formData.commission_rate) / 100).toFixed(2)}€
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Commission (%) 
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={formData.commission_rate}
                onChange={(e) => setFormData({ ...formData, commission_rate: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Autres */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date d'expiration
              </label>
              <input
                type="date"
                value={formData.date_expiration}
                onChange={(e) => setFormData({ ...formData, date_expiration: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conditions d'utilisation
              </label>
              <textarea
                value={formData.conditions}
                onChange={(e) => setFormData({ ...formData, conditions: e.target.value })}
                rows={3}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Conditions et restrictions..."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Enregistrement...' : mode === 'create' ? 'Créer le Service' : 'Mettre à jour'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ServiceFormModal;
