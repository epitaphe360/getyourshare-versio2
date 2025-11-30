import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Calendar, CheckCircle, Package } from 'lucide-react';
import api from '../utils/api';
import { toast } from 'react-toastify';

const ServiceRequest = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    nom_client: '',
    email_client: '',
    telephone_client: '',
    message: ''
  });

  useEffect(() => {
    loadService();
  }, [id]);

  const loadService = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/public/services/${id}`);
      setService(response.data.service);
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Service introuvable');
      navigate('/services');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await api.post('/api/leads', {
        service_id: id,
        nom_client: formData.nom_client,
        email_client: formData.email_client,
        telephone_client: formData.telephone_client,
        donnees_formulaire: {
          message: formData.message
        }
      });
      
      setSuccess(true);
      toast.success('Votre demande a été envoyée avec succès !');
    } catch (error) {
      console.error('Erreur:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'envoi de la demande');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!service) {
    return null;
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle size={32} className="text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Demande envoyée !</h2>
          <p className="text-gray-600 mb-6">
            Le marchand va vous contacter sous 24h à l'adresse email ou numéro de téléphone fourni.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Vous recevrez également un email de confirmation.
          </p>
          <button
            onClick={() => navigate('/services')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition font-medium"
          >
            Retour aux services
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/services')}
            className="flex items-center text-gray-600 hover:text-gray-800 transition"
          >
            <ArrowLeft size={20} className="mr-2" />
            Retour aux services
          </button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
            {/* Service Info */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                {service.images && service.images.length > 0 ? (
                  <img
                    src={service.images[0]}
                    alt={service.nom}
                    className="w-full h-48 object-cover rounded-lg mb-4"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center mb-4">
                    <Package size={48} className="text-gray-400" />
                  </div>
                )}

                <h2 className="text-2xl font-bold text-gray-800 mb-2">{service.nom}</h2>
                
                {service.categories?.name && (
                  <span className="inline-block bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm mb-4">
                    {service.categories.name}
                  </span>
                )}

                <p className="text-gray-600 mb-4">{service.description}</p>

                {service.localisation && (
                  <div className="flex items-center text-gray-600 mb-2">
                    <MapPin size={18} className="mr-2" />
                    {service.localisation}
                  </div>
                )}

                {service.conditions && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs font-semibold text-gray-700 mb-1">Conditions:</p>
                    <p className="text-xs text-gray-600">{service.conditions}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Form */}
            <div className="lg:col-span-3">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                  Demander ce service
                </h3>
                <p className="text-gray-600 mb-6">
                  Remplissez le formulaire ci-dessous et le marchand vous contactera rapidement.
                </p>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nom complet *
                    </label>
                    <input
                      type="text"
                      required
                      value={formData.nom_client}
                      onChange={(e) => setFormData({ ...formData, nom_client: e.target.value })}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Jean Dupont"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email_client}
                      onChange={(e) => setFormData({ ...formData, email_client: e.target.value })}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="jean.dupont@email.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Téléphone *
                    </label>
                    <input
                      type="tel"
                      required
                      value={formData.telephone_client}
                      onChange={(e) => setFormData({ ...formData, telephone_client: e.target.value })}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="06 12 34 56 78"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Message (optionnel)
                    </label>
                    <textarea
                      rows={4}
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Des précisions sur votre demande..."
                    />
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">✓ Ce service est gratuit</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Aucun paiement requis</li>
                      <li>• Aucun engagement</li>
                      <li>• Réponse sous 24h</li>
                      <li>• Vos données sont sécurisées</li>
                    </ul>
                  </div>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-lg transition font-medium text-lg disabled:opacity-50"
                  >
                    {submitting ? 'Envoi en cours...' : 'Envoyer ma demande'}
                  </button>

                  <p className="text-xs text-center text-gray-500">
                    En envoyant ce formulaire, vous acceptez d'être contacté par le marchand concernant ce service.
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceRequest;
