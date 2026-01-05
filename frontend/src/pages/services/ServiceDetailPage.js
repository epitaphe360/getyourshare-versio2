import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useToast } from '../../context/ToastContext';
import api from '../../utils/api';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import { 
  ArrowLeft, 
  Edit, 
  Clock, 
  DollarSign, 
  Tag, 
  Briefcase, 
  Mail,
  Calendar,
  TrendingUp,
  Users,
  Eye,
  Package
} from 'lucide-react';

const ServiceDetailPage = () => {
  const navigate = useNavigate();
  const { serviceId } = useParams();
  const toast = useToast();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchService();
  }, [serviceId]);

  const fetchService = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/services/${serviceId}`);
      setService(response.data);
    } catch (error) {
      console.error('Error fetching service:', error);
      toast.error('Erreur lors du chargement du service');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="text-center py-12">
        <Package size={48} className="mx-auto text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Service non trouvé</h3>
        <p className="text-gray-600 mb-6">Ce service n'existe pas ou a été supprimé.</p>
        <Button onClick={() => navigate('/services')}>Retour aux services</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate('/services')}
              icon={<ArrowLeft size={18} />}
            >
              Retour
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Détails du service</h1>
              <p className="text-sm text-gray-500 mt-1">
                Créé le {new Date(service.created_at || Date.now()).toLocaleDateString('fr-FR')}
              </p>
            </div>
          </div>
          <Button
            onClick={() => navigate(`/services/${serviceId}/edit`)}
            icon={<Edit size={18} />}
          >
            Modifier
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Service Overview Card */}
          <Card>
            <div className="p-6">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <h2 className="text-3xl font-bold text-gray-900">{service.name}</h2>
                    <Badge
                      variant={service.is_active ? 'success' : 'secondary'}
                    >
                      {service.is_active ? 'Actif' : 'Inactif'}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 font-medium">
                      <Tag size={14} className="mr-1" />
                      {service.category || 'Non catégorisé'}
                    </span>
                  </div>
                </div>
                {service.image_url && (
                  <div className="ml-4">
                    <img
                      src={service.image_url}
                      alt={service.name}
                      className="w-32 h-32 rounded-xl object-cover shadow-md border-2 border-gray-100"
                    />
                  </div>
                )}
              </div>

              <div className="border-t border-gray-100 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Eye size={20} className="mr-2 text-gray-400" />
                  Description
                </h3>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {service.description || 'Aucune description disponible pour ce service.'}
                </p>
              </div>
            </div>
          </Card>

          {/* Merchant Info Card */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Briefcase size={20} className="mr-2 text-gray-400" />
                Informations du marchand
              </h3>
              {service.merchant ? (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900 text-lg mb-2">
                        {service.merchant.company_name || 'Sans nom'}
                      </h4>
                      <div className="space-y-2">
                        <div className="flex items-center text-gray-600">
                          <Mail size={16} className="mr-2 text-gray-400" />
                          <a 
                            href={`mailto:${service.merchant.email}`} 
                            className="text-blue-600 hover:text-blue-700 hover:underline"
                          >
                            {service.merchant.email}
                          </a>
                        </div>
                        {service.merchant.phone && (
                          <div className="flex items-center text-gray-600">
                            <Users size={16} className="mr-2 text-gray-400" />
                            <span>{service.merchant.phone}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => navigate(`/merchants/${service.merchant.id}`)}
                    >
                      Voir profil
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 bg-gray-50 rounded-lg">
                  <Users size={32} className="mx-auto text-gray-300 mb-2" />
                  <p className="text-gray-500 italic">Aucun marchand assigné</p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Pricing Card */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Tarification</h3>
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="flex items-center text-gray-600 mb-2">
                    <DollarSign size={18} className="mr-2 text-blue-600" />
                    <span className="text-sm font-medium">Prix du service</span>
                  </div>
                  <div className="text-3xl font-bold text-blue-900">{service.price} €</div>
                </div>

                <div className="pt-4 border-t border-gray-100 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-gray-600">
                      <Clock size={18} className="mr-2 text-gray-400" />
                      <span className="text-sm">Durée</span>
                    </div>
                    <span className="font-semibold text-gray-900">{service.duration} min</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center text-gray-600">
                      <TrendingUp size={18} className="mr-2 text-gray-400" />
                      <span className="text-sm">Commission</span>
                    </div>
                    <span className="font-semibold text-gray-900">{service.commission_rate}%</span>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <span className="text-sm text-gray-600">Revenu marchand</span>
                    <span className="font-bold text-green-600">
                      {(service.price * (1 - service.commission_rate / 100)).toFixed(2)} €
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Status Card */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statut</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-600">Disponibilité</span>
                  <Badge variant={service.is_active ? 'success' : 'secondary'}>
                    {service.is_active ? 'Actif' : 'Inactif'}
                  </Badge>
                </div>
                
                {service.created_at && (
                  <div className="flex items-center justify-between py-2 border-t border-gray-100">
                    <div className="flex items-center text-gray-600">
                      <Calendar size={16} className="mr-2 text-gray-400" />
                      <span className="text-sm">Création</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(service.created_at).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                )}

                {service.updated_at && (
                  <div className="flex items-center justify-between py-2 border-t border-gray-100">
                    <div className="flex items-center text-gray-600">
                      <Calendar size={16} className="mr-2 text-gray-400" />
                      <span className="text-sm">Dernière MAJ</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(service.updated_at).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetailPage;
