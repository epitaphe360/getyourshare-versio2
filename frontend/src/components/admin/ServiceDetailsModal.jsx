import React, { useState, useEffect } from 'react';
import { X, Users, TrendingUp, DollarSign, RefreshCw, Phone, Mail, Calendar } from 'lucide-react';
import api from '../../utils/api';
import { toast } from 'react-toastify';

const ServiceDetailsModal = ({ show, onClose, service, onReload }) => {
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState(null);
  const [activeTab, setActiveTab] = useState('leads'); // 'leads', 'recharges', 'extras'

  useEffect(() => {
    if (show && service) {
      loadDetails();
    }
  }, [show, service]);

  const loadDetails = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/admin/services/${service.id}`);
      setDetails(response.data);
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors du chargement des détails');
    } finally {
      setLoading(false);
    }
  };

  const handleRecharge = async () => {
    const montant = prompt('Montant de la recharge (€):');
    if (!montant || isNaN(montant) || parseFloat(montant) <= 0) return;

    try {
      await api.post(`/api/admin/services/${service.id}/recharge`, {
        montant: parseFloat(montant),
        methode_paiement: 'admin',
        statut_paiement: 'reussi'
      });
      toast.success('Recharge effectuée avec succès !');
      loadDetails();
      onReload();
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de la recharge');
    }
  };

  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      await api.put(`/api/admin/leads/${leadId}/status`, {
        statut: newStatus
      });
      toast.success('Statut mis à jour');
      loadDetails();
      onReload();
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de la mise à jour');
    }
  };

  if (!show || !service) return null;

  const getStatusBadge = (statut) => {
    const badges = {
      'nouveau': <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">🆕 Nouveau</span>,
      'en_cours': <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">⏳ En cours</span>,
      'converti': <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">✅ Converti</span>,
      'perdu': <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">❌ Perdu</span>,
      'spam': <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">🚫 Spam</span>
    };
    return badges[statut] || statut;
  };

  const depotPourcentage = details?.service 
    ? (parseFloat(details.service.depot_actuel || 0) / parseFloat(details.service.depot_initial || 1) * 100).toFixed(0)
    : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{service.nom}</h2>
            <p className="text-sm text-gray-600">{service.users?.company_name || service.users?.full_name}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : details ? (
          <div className="p-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <DollarSign size={24} />
                  <button
                    onClick={handleRecharge}
                    className="bg-white/20 hover:bg-white/30 px-3 py-1 rounded text-xs"
                  >
                    Recharger
                  </button>
                </div>
                <p className="text-sm opacity-90">Solde actuel</p>
                <p className="text-2xl font-bold">{parseFloat(details.service.depot_actuel || 0).toFixed(2)}€</p>
                <div className="w-full bg-white/20 rounded-full h-2 mt-2">
                  <div
                    className="bg-white h-2 rounded-full"
                    style={{ width: `${depotPourcentage}%` }}
                  ></div>
                </div>
                <p className="text-xs mt-1">{depotPourcentage}% du dépôt initial</p>
              </div>

              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 rounded-lg">
                <Users size={24} className="mb-2" />
                <p className="text-sm opacity-90">Leads reçus</p>
                <p className="text-2xl font-bold">{details.leads?.length || 0}</p>
                <p className="text-xs mt-1">{details.stats?.leads_restants || 0} restants possibles</p>
              </div>

              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white p-4 rounded-lg">
                <TrendingUp size={24} className="mb-2" />
                <p className="text-sm opacity-90">Taux conversion</p>
                <p className="text-2xl font-bold">{details.stats?.taux_conversion || 0}%</p>
                <p className="text-xs mt-1">{details.stats?.leads_convertis || 0} convertis</p>
              </div>

              <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-4 rounded-lg">
                <DollarSign size={24} className="mb-2" />
                <p className="text-sm opacity-90">Prix par lead</p>
                <p className="text-2xl font-bold">{parseFloat(details.service.prix_par_lead || 0).toFixed(2)}€</p>
                <p className="text-xs mt-1">Commission {details.service.commission_rate}%</p>
              </div>
            </div>

            {/* Tabs */}
            <div className="border-b mb-6">
              <div className="flex gap-4">
                <button
                  onClick={() => setActiveTab('leads')}
                  className={`pb-3 px-2 font-medium transition ${
                    activeTab === 'leads'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Leads ({details.leads?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('recharges')}
                  className={`pb-3 px-2 font-medium transition ${
                    activeTab === 'recharges'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Recharges ({details.recharges?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('extras')}
                  className={`pb-3 px-2 font-medium transition ${
                    activeTab === 'extras'
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  Extras ({details.extras?.length || 0})
                </button>
              </div>
            </div>

            {/* Content */}
            {activeTab === 'leads' && (
              <div className="space-y-3">
                {details.leads && details.leads.length > 0 ? (
                  details.leads.map(lead => (
                    <div key={lead.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-semibold text-gray-900">{lead.nom_client}</h4>
                            {getStatusBadge(lead.statut)}
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <p className="flex items-center gap-2">
                              <Mail size={14} /> {lead.email_client}
                            </p>
                            <p className="flex items-center gap-2">
                              <Phone size={14} /> {lead.telephone_client}
                            </p>
                            <p className="flex items-center gap-2">
                              <Calendar size={14} /> {new Date(lead.date_reception).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                          {lead.notes_marchand && (
                            <p className="text-sm text-gray-600 mt-2 italic">
                              Note: {lead.notes_marchand}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col gap-2">
                          {lead.statut === 'nouveau' && (
                            <>
                              <button
                                onClick={() => updateLeadStatus(lead.id, 'en_cours')}
                                className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200"
                              >
                                En cours
                              </button>
                              <button
                                onClick={() => updateLeadStatus(lead.id, 'converti')}
                                className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs hover:bg-green-200"
                              >
                                Converti
                              </button>
                            </>
                          )}
                          {lead.statut === 'en_cours' && (
                            <>
                              <button
                                onClick={() => updateLeadStatus(lead.id, 'converti')}
                                className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs hover:bg-green-200"
                              >
                                Converti
                              </button>
                              <button
                                onClick={() => updateLeadStatus(lead.id, 'perdu')}
                                className="px-3 py-1 bg-red-100 text-red-700 rounded text-xs hover:bg-red-200"
                              >
                                Perdu
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Aucun lead pour ce service
                  </div>
                )}
              </div>
            )}

            {activeTab === 'recharges' && (
              <div className="space-y-3">
                {details.recharges && details.recharges.length > 0 ? (
                  details.recharges.map(recharge => (
                    <div key={recharge.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-lg text-green-600">
                            +{parseFloat(recharge.montant).toFixed(2)}€
                          </p>
                          <p className="text-sm text-gray-600">
                            {new Date(recharge.created_at).toLocaleDateString('fr-FR')}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            +{recharge.leads_ajoutes} leads
                          </p>
                        </div>
                        <div className="text-right text-sm text-gray-600">
                          <p>Avant: {parseFloat(recharge.ancien_solde).toFixed(2)}€</p>
                          <p className="font-semibold">Après: {parseFloat(recharge.nouveau_solde).toFixed(2)}€</p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Aucune recharge
                  </div>
                )}
              </div>
            )}

            {activeTab === 'extras' && (
              <div className="space-y-3">
                {details.extras && details.extras.length > 0 ? (
                  details.extras.map(extra => (
                    <div key={extra.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{extra.nom}</p>
                          <p className="text-sm text-gray-600">{extra.description}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(extra.date_debut).toLocaleDateString('fr-FR')} - 
                            {extra.date_fin ? new Date(extra.date_fin).toLocaleDateString('fr-FR') : 'Indéfini'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-purple-600">{parseFloat(extra.prix).toFixed(2)}€</p>
                          {extra.actif ? (
                            <span className="text-xs text-green-600">✓ Actif</span>
                          ) : (
                            <span className="text-xs text-gray-500">Expiré</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Aucun extra acheté
                  </div>
                )}
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ServiceDetailsModal;
