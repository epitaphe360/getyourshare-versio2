import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft, Mail, Phone, Calendar, DollarSign, Edit, Save,
  X, MessageSquare, Clock, User, FileText, Activity, 
  CheckCircle, AlertCircle, TrendingUp, Target, Briefcase
} from 'lucide-react';
import api from '../../utils/api';
import { toast } from 'react-toastify';

const LeadDetailPage = () => {
  const { leadId } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [newActivity, setNewActivity] = useState({
    type: 'note',
    subject: '',
    description: ''
  });
  const [showActivityForm, setShowActivityForm] = useState(false);

  useEffect(() => {
    fetchLeadDetails();
    fetchActivities();
  }, [leadId]);

  const fetchLeadDetails = async () => {
    try {
      const response = await api.get(`/api/commercial/leads/${leadId}`);
      setLead(response.data);
      setEditData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement lead:', error);
      toast.error('Lead introuvable');
      navigate('/commercial/leads');
    }
  };

  const fetchActivities = async () => {
    try {
      const response = await api.get(`/api/commercial/leads/${leadId}/activities`);
      setActivities(Array.isArray(response.data) ? response.data : response.data?.activities || []);
    } catch (error) {
      console.error('Erreur chargement activités:', error);
      setActivities([]);
    }
  };

  const handleUpdateLead = async () => {
    try {
      await api.patch(`/api/commercial/leads/${leadId}`, editData);
      toast.success('Lead mis à jour avec succès');
      setLead(editData);
      setIsEditing(false);
      fetchActivities(); // Recharger pour voir l'activité de mise à jour
    } catch (error) {
      console.error('Erreur mise à jour:', error);
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleAddActivity = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/api/commercial/leads/${leadId}/activities`, newActivity);
      toast.success('Activité ajoutée');
      setShowActivityForm(false);
      setNewActivity({ type: 'note', subject: '', description: '' });
      fetchActivities();
    } catch (error) {
      console.error('Erreur ajout activité:', error);
      toast.error('Erreur lors de l\'ajout de l\'activité');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      nouveau: 'bg-blue-100 text-blue-800 border-blue-200',
      contacté: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      qualifié: 'bg-purple-100 text-purple-800 border-purple-200',
      proposition: 'bg-pink-100 text-pink-800 border-pink-200',
      négociation: 'bg-orange-100 text-orange-800 border-orange-200',
      conclu: 'bg-green-100 text-green-800 border-green-200',
      perdu: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getTemperatureEmoji = (temp) => {
    const emojis = {
      chaud: '🔥',
      tiède: '☀️',
      froid: '❄️'
    };
    return emojis[temp] || '❄️';
  };

  const getActivityIcon = (type) => {
    const icons = {
      call: <Phone size={16} className="text-blue-600" />,
      email: <Mail size={16} className="text-green-600" />,
      meeting: <Calendar size={16} className="text-purple-600" />,
      note: <MessageSquare size={16} className="text-gray-600" />,
      update: <Edit size={16} className="text-orange-600" />
    };
    return icons[type] || <Activity size={16} className="text-gray-600" />;
  };

  const getActivityColor = (type) => {
    const colors = {
      call: 'bg-blue-50 border-blue-200',
      email: 'bg-green-50 border-green-200',
      meeting: 'bg-purple-50 border-purple-200',
      note: 'bg-gray-50 border-gray-200',
      update: 'bg-orange-50 border-orange-200'
    };
    return colors[type] || 'bg-gray-50 border-gray-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du lead...</p>
        </div>
      </div>
    );
  }

  if (!lead) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => navigate('/commercial/leads')}
            className="flex items-center gap-2 text-white/80 hover:text-white transition mb-4"
          >
            <ArrowLeft size={20} />
            Retour aux leads
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{lead.company_name}</h1>
              <p className="text-xl text-purple-100">{lead.contact_name}</p>
              <div className="flex items-center gap-4 mt-4">
                <span className="px-4 py-1 bg-white/20 rounded-full text-sm font-medium">
                  {lead.status}
                </span>
                <span className="text-2xl">{getTemperatureEmoji(lead.temperature)}</span>
                <span className="text-xl font-bold">
                  {lead.estimated_value?.toLocaleString() || 0} €
                </span>
              </div>
            </div>

            <button
              onClick={() => setIsEditing(!isEditing)}
              className="px-6 py-3 bg-white text-purple-600 rounded-lg hover:bg-purple-50 transition font-medium flex items-center gap-2"
            >
              {isEditing ? (
                <>
                  <X size={20} />
                  Annuler
                </>
              ) : (
                <>
                  <Edit size={20} />
                  Modifier
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-3 gap-6">
          {/* Colonne principale - Informations */}
          <div className="col-span-2 space-y-6">
            {/* Informations de contact */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Briefcase size={24} className="text-purple-600" />
                Informations de contact
              </h2>

              {isEditing ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Entreprise
                      </label>
                      <input
                        type="text"
                        value={editData.company_name}
                        onChange={(e) => setEditData({ ...editData, company_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contact
                      </label>
                      <input
                        type="text"
                        value={editData.contact_name}
                        onChange={(e) => setEditData({ ...editData, contact_name: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={editData.contact_email}
                        onChange={(e) => setEditData({ ...editData, contact_email: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Téléphone
                      </label>
                      <input
                        type="tel"
                        value={editData.contact_phone || ''}
                        onChange={(e) => setEditData({ ...editData, contact_phone: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Statut
                      </label>
                      <select
                        value={editData.status}
                        onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="nouveau">Nouveau</option>
                        <option value="contacté">Contacté</option>
                        <option value="qualifié">Qualifié</option>
                        <option value="proposition">Proposition</option>
                        <option value="négociation">Négociation</option>
                        <option value="conclu">Conclu</option>
                        <option value="perdu">Perdu</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Température
                      </label>
                      <select
                        value={editData.temperature}
                        onChange={(e) => setEditData({ ...editData, temperature: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="froid">❄️ Froid</option>
                        <option value="tiède">☀️ Tiède</option>
                        <option value="chaud">🔥 Chaud</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Valeur estimée (€)
                      </label>
                      <input
                        type="number"
                        value={editData.estimated_value || ''}
                        onChange={(e) => setEditData({ ...editData, estimated_value: parseFloat(e.target.value) })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Type de service
                      </label>
                      <input
                        type="text"
                        value={editData.service_type || ''}
                        onChange={(e) => setEditData({ ...editData, service_type: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes
                    </label>
                    <textarea
                      value={editData.notes || ''}
                      onChange={(e) => setEditData({ ...editData, notes: e.target.value })}
                      rows="4"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <button
                    onClick={handleUpdateLead}
                    className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center justify-center gap-2"
                  >
                    <Save size={20} />
                    Enregistrer les modifications
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Email</p>
                    <div className="flex items-center gap-2">
                      <Mail size={18} className="text-gray-400" />
                      <a href={`mailto:${lead.contact_email}`} className="text-purple-600 hover:underline">
                        {lead.contact_email}
                      </a>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Téléphone</p>
                    <div className="flex items-center gap-2">
                      <Phone size={18} className="text-gray-400" />
                      <a href={`tel:${lead.contact_phone}`} className="text-purple-600 hover:underline">
                        {lead.contact_phone || 'Non renseigné'}
                      </a>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Service</p>
                    <p className="text-gray-900 font-medium">{lead.service_type || 'Non renseigné'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Date de création</p>
                    <div className="flex items-center gap-2">
                      <Calendar size={18} className="text-gray-400" />
                      <p className="text-gray-900 font-medium">
                        {new Date(lead.created_at).toLocaleDateString('fr-FR', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {!isEditing && lead.notes && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <p className="text-sm text-gray-600 mb-2">Notes</p>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{lead.notes}</p>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Timeline d'activités */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <Activity size={24} className="text-purple-600" />
                  Historique d'activités
                </h2>
                <button
                  onClick={() => setShowActivityForm(!showActivityForm)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm flex items-center gap-2"
                >
                  {showActivityForm ? <X size={16} /> : <MessageSquare size={16} />}
                  {showActivityForm ? 'Annuler' : 'Nouvelle activité'}
                </button>
              </div>

              {showActivityForm && (
                <form onSubmit={handleAddActivity} className="mb-6 bg-gray-50 rounded-lg p-4">
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Type d'activité
                        </label>
                        <select
                          value={newActivity.type}
                          onChange={(e) => setNewActivity({ ...newActivity, type: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="note">📝 Note</option>
                          <option value="call">📞 Appel</option>
                          <option value="email">✉️ Email</option>
                          <option value="meeting">🤝 Réunion</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Sujet
                        </label>
                        <input
                          type="text"
                          required
                          value={newActivity.subject}
                          onChange={(e) => setNewActivity({ ...newActivity, subject: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Ex: Premier contact"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        value={newActivity.description}
                        onChange={(e) => setNewActivity({ ...newActivity, description: e.target.value })}
                        rows="3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        placeholder="Détails de l'activité..."
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition flex items-center justify-center gap-2"
                    >
                      <CheckCircle size={18} />
                      Ajouter l'activité
                    </button>
                  </div>
                </form>
              )}

              <div className="space-y-4">
                {activities.length === 0 ? (
                  <div className="text-center py-12">
                    <Activity size={48} className="mx-auto text-gray-300 mb-3" />
                    <p className="text-gray-600">Aucune activité pour ce lead</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Ajoutez des notes, appels ou réunions pour suivre votre progression
                    </p>
                  </div>
                ) : (
                  <div className="relative border-l-2 border-gray-200 pl-6 ml-3">
                    {activities.map((activity, index) => (
                      <motion.div
                        key={activity.id || index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="relative mb-6 last:mb-0"
                      >
                        <div className={`absolute -left-9 p-2 rounded-full border-2 ${getActivityColor(activity.type)}`}>
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className={`border rounded-lg p-4 ${getActivityColor(activity.type)}`}>
                          <div className="flex items-start justify-between mb-2">
                            <h3 className="font-semibold text-gray-900">{activity.subject}</h3>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <Clock size={14} />
                              {new Date(activity.created_at).toLocaleDateString('fr-FR', {
                                day: 'numeric',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                          {activity.description && (
                            <p className="text-sm text-gray-700">{activity.description}</p>
                          )}
                          {activity.user_name && (
                            <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                              <User size={14} />
                              {activity.user_name}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Colonne droite - Actions rapides */}
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Target size={24} className="text-purple-600" />
                Actions rapides
              </h2>

              <div className="space-y-3">
                <button
                  onClick={() => handleUpdateLead(leadId, { status: 'contacté' })}
                  className="w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition flex items-center gap-2"
                >
                  <Phone size={18} />
                  Marquer comme contacté
                </button>
                <button
                  onClick={() => handleUpdateLead(leadId, { status: 'qualifié' })}
                  className="w-full px-4 py-3 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition flex items-center gap-2"
                >
                  <CheckCircle size={18} />
                  Marquer comme qualifié
                </button>
                <button
                  onClick={() => window.location.href = `mailto:${lead.contact_email}`}
                  className="w-full px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition flex items-center gap-2"
                >
                  <Mail size={18} />
                  Envoyer un email
                </button>
                <button
                  onClick={() => handleUpdateLead(leadId, { status: 'proposition' })}
                  className="w-full px-4 py-3 bg-pink-50 text-pink-700 rounded-lg hover:bg-pink-100 transition flex items-center gap-2"
                >
                  <FileText size={18} />
                  Envoyer une proposition
                </button>
                <button
                  onClick={() => handleUpdateLead(leadId, { status: 'conclu' })}
                  className="w-full px-4 py-3 bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition flex items-center gap-2"
                >
                  <DollarSign size={18} />
                  Marquer comme conclu
                </button>
              </div>
            </motion.div>

            {/* Stats du lead */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp size={24} className="text-purple-600" />
                Statistiques
              </h2>

              <div className="space-y-4">
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Valeur estimée</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {lead.estimated_value?.toLocaleString() || 0} €
                  </p>
                </div>

                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Température</p>
                  <p className="text-2xl">
                    {getTemperatureEmoji(lead.temperature)} {lead.temperature}
                  </p>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Activités totales</p>
                  <p className="text-2xl font-bold text-green-600">
                    {activities.length}
                  </p>
                </div>

                <div className="bg-orange-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Jours depuis création</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {Math.floor((new Date() - new Date(lead.created_at)) / (1000 * 60 * 60 * 24))}
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadDetailPage;
