import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import { User, Mail, Phone, Globe, Download, Trash2, AlertTriangle } from 'lucide-react';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';

const PersonalSettings = () => {
  const { user, logout } = useAuth();
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    timezone: 'Europe/Paris',
    language: 'fr',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put(`/api/users/${user.id}`, formData);
      toast.success('Profil mis à jour avec succès');
      // Note: You may want to update the AuthContext with the new user data
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Erreur lors de la mise à jour du profil');
    } finally {
      setSaving(false);
    }
  };

  const handleExportData = async () => {
    setExporting(true);
    try {
      const response = await api.get('/api/user/export', {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `shareyoursales_data_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Vos données ont été exportées avec succès');
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Erreur lors de l\'exportation des données');
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    try {
      await api.delete('/api/user/delete');
      toast.success('Votre compte a été supprimé');
      logout(); // Log the user out
    } catch (error) {
      console.error('Error deleting account:', error);
      toast.error('Erreur lors de la suppression du compte');
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="personal-settings">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres Personnels</h1>
        <p className="text-gray-600 mt-2">Gérez vos informations personnelles</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card title="Informations Générales">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prénom
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nom
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Téléphone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fuseau Horaire
                </label>
                <select
                  value={formData.timezone}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Europe/Paris">Europe/Paris (GMT+1)</option>
                  <option value="America/New_York">America/New_York (GMT-5)</option>
                  <option value="Asia/Tokyo">Asia/Tokyo (GMT+9)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Langue
                </label>
                <select
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="fr">Français</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={saving}>
                {saving ? 'Sauvegarde...' : 'Enregistrer les modifications'}
              </Button>
            </div>
          </div>
        </Card>
      </form>

      {/* GDPR Section */}
      <Card title="Gestion des Données (RGPD)">
        <div className="space-y-6">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-5 w-5 text-blue-400" aria-hidden="true" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700">
                  Conformément au RGPD, vous avez le droit d'accéder à vos données personnelles ou de demander leur suppression.
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Exporter mes données</h3>
              <p className="text-sm text-gray-500 mb-4">
                Téléchargez une copie de toutes vos données personnelles stockées sur notre plateforme au format JSON.
              </p>
              <Button 
                variant="outline" 
                onClick={handleExportData} 
                disabled={exporting}
                className="w-full flex justify-center items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                {exporting ? 'Export en cours...' : 'Exporter mes données'}
              </Button>
            </div>

            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <h3 className="text-lg font-medium text-red-900 mb-2">Supprimer mon compte</h3>
              <p className="text-sm text-red-700 mb-4">
                Cette action est irréversible. Toutes vos données seront définitivement supprimées de nos serveurs.
              </p>
              {!showDeleteConfirm ? (
                <Button 
                  variant="danger" 
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full flex justify-center items-center bg-red-600 hover:bg-red-700 text-white"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Supprimer mon compte
                </Button>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm font-bold text-red-800 text-center">Êtes-vous sûr ?</p>
                  <div className="flex space-x-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowDeleteConfirm(false)}
                      className="w-1/2"
                    >
                      Annuler
                    </Button>
                    <Button 
                      variant="danger" 
                      onClick={handleDeleteAccount}
                      disabled={deleting}
                      className="w-1/2 bg-red-600 hover:bg-red-700 text-white"
                    >
                      {deleting ? '...' : 'Confirmer'}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default PersonalSettings;
