import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, AlertCircle, DollarSign, Calendar, TrendingUp, TrendingDown } from 'lucide-react';
import api from '../../utils/api';

const PlanChangeModal = ({ isOpen, onClose, subscription, onSuccess }) => {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [applyImmediately, setApplyImmediately] = useState(true);
  const [prorata, setProrata] = useState(true);
  const [prorataCalculation, setProrataCalculation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [note, setNote] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchPlans();
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedPlan && applyImmediately && prorata) {
      calculateProrata();
    } else {
      setProrataCalculation(null);
    }
  }, [selectedPlan, applyImmediately, prorata]);

  const fetchPlans = async () => {
    try {
      const response = await api.get('/api/subscriptions/plans');
      setPlans(response.data.plans || []);
    } catch (error) {
      console.error('Error fetching plans:', error);
    }
  };

  const calculateProrata = () => {
    if (!selectedPlan || !subscription) return;

    const currentPrice = parseFloat(subscription.monthly_fee || 0);
    const newPrice = parseFloat(selectedPlan.price_mad || selectedPlan.price || 0);

    // Calculer les jours restants dans la période
    const now = new Date();
    const periodEnd = new Date(subscription.current_period_end);
    const periodStart = new Date(subscription.current_period_start);
    
    const totalDays = Math.ceil((periodEnd - periodStart) / (1000 * 60 * 60 * 24));
    const daysRemaining = Math.ceil((periodEnd - now) / (1000 * 60 * 60 * 24));
    
    if (daysRemaining <= 0) {
      setProrataCalculation({
        credit: 0,
        charge: newPrice,
        netAmount: newPrice,
        daysRemaining: 0
      });
      return;
    }

    // Crédit pour jours non utilisés
    const unusedAmount = (currentPrice / totalDays) * daysRemaining;
    
    // Charge pour nouveau plan
    const newPeriodCost = (newPrice / totalDays) * daysRemaining;
    
    setProrataCalculation({
      credit: Math.round(unusedAmount * 100) / 100,
      charge: Math.round(newPeriodCost * 100) / 100,
      netAmount: Math.round((newPeriodCost - unusedAmount) * 100) / 100,
      daysRemaining,
      currentPrice,
      newPrice
    });
  };

  const handleChangePlan = async () => {
    if (!selectedPlan) return;

    setLoading(true);
    try {
      const response = await api.post(`/api/subscriptions/admin/${subscription.id}/change-plan`, {
        plan_code: selectedPlan.code,
        apply_immediately: applyImmediately,
        prorata: prorata,
        note: note || undefined
      });

      if (response.data.success) {
        onSuccess(response.data);
        onClose();
      }
    } catch (error) {
      console.error('Error changing plan:', error);
      alert('Erreur lors du changement de plan: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const currentPlanCode = subscription?.plan_code;
  const isUpgrade = selectedPlan && parseFloat(selectedPlan.price_mad || selectedPlan.price || 0) > parseFloat(subscription?.monthly_fee || 0);
  const isDowngrade = selectedPlan && parseFloat(selectedPlan.price_mad || selectedPlan.price || 0) < parseFloat(subscription?.monthly_fee || 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Changer de Plan</h2>
                <p className="text-gray-600 text-sm mt-1">
                  Abonnement actuel: <span className="font-semibold">{subscription?.plan_name}</span>
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Plans Grid */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-4">Sélectionnez un nouveau plan</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {plans.map((plan) => {
                    const isCurrentPlan = plan.code === currentPlanCode;
                    const isSelected = selectedPlan?.id === plan.id;
                    const planPrice = parseFloat(plan.price_mad || plan.price || 0);

                    return (
                      <motion.div
                        key={plan.id}
                        whileHover={{ scale: isCurrentPlan ? 1 : 1.02 }}
                        onClick={() => !isCurrentPlan && setSelectedPlan(plan)}
                        className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all ${
                          isCurrentPlan
                            ? 'border-gray-300 bg-gray-50 cursor-not-allowed opacity-60'
                            : isSelected
                            ? 'border-blue-600 bg-blue-50 shadow-lg'
                            : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                        }`}
                      >
                        {isCurrentPlan && (
                          <div className="absolute top-2 right-2 bg-gray-700 text-white text-xs px-2 py-1 rounded-full">
                            Actuel
                          </div>
                        )}
                        {isSelected && !isCurrentPlan && (
                          <div className="absolute top-2 right-2 bg-blue-600 text-white p-1 rounded-full">
                            <Check size={16} />
                          </div>
                        )}
                        
                        <h4 className="font-bold text-lg mb-2">{plan.name}</h4>
                        <div className="text-3xl font-bold text-blue-600 mb-2">
                          {planPrice.toLocaleString('fr-MA')}
                          <span className="text-lg text-gray-600"> MAD/mois</span>
                        </div>
                        
                        {plan.description && (
                          <p className="text-sm text-gray-600 mb-3">{plan.description}</p>
                        )}

                        {/* Indicateur upgrade/downgrade */}
                        {!isCurrentPlan && (
                          <div className="mt-3">
                            {planPrice > parseFloat(subscription?.monthly_fee || 0) ? (
                              <div className="flex items-center text-green-600 text-sm font-medium">
                                <TrendingUp size={16} className="mr-1" />
                                Upgrade (+{(planPrice - parseFloat(subscription?.monthly_fee || 0)).toFixed(0)} MAD)
                              </div>
                            ) : planPrice < parseFloat(subscription?.monthly_fee || 0) ? (
                              <div className="flex items-center text-orange-600 text-sm font-medium">
                                <TrendingDown size={16} className="mr-1" />
                                Downgrade (-{(parseFloat(subscription?.monthly_fee || 0) - planPrice).toFixed(0)} MAD)
                              </div>
                            ) : (
                              <div className="text-gray-500 text-sm">Même prix</div>
                            )}
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Options */}
              {selectedPlan && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4 mb-6"
                >
                  {/* Application immediate */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={applyImmediately}
                        onChange={(e) => setApplyImmediately(e.target.checked)}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <div className="ml-3">
                        <span className="font-medium text-gray-900">Appliquer immédiatement</span>
                        <p className="text-sm text-gray-600">
                          {applyImmediately 
                            ? "Le changement prendra effet maintenant" 
                            : "Le changement prendra effet à la fin de la période en cours"}
                        </p>
                      </div>
                    </label>
                  </div>

                  {/* Prorata */}
                  {applyImmediately && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={prorata}
                          onChange={(e) => setProrata(e.target.checked)}
                          className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <div className="ml-3">
                          <span className="font-medium text-gray-900">Calculer le prorata</span>
                          <p className="text-sm text-gray-600">
                            Ajuster le prix en fonction des jours restants
                          </p>
                        </div>
                      </label>
                    </div>
                  )}

                  {/* Note optionnelle */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Note (optionnelle)
                    </label>
                    <textarea
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="Raison du changement de plan..."
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={2}
                    />
                  </div>
                </motion.div>
              )}

              {/* Prorata Calculation */}
              {prorataCalculation && applyImmediately && prorata && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 mb-6"
                >
                  <h3 className="font-semibold text-lg mb-4 flex items-center text-blue-900">
                    <DollarSign className="mr-2" size={20} />
                    Calcul du Prorata
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-gray-700">
                      <span>Jours restants dans la période:</span>
                      <span className="font-semibold">{prorataCalculation.daysRemaining} jours</span>
                    </div>
                    
                    <div className="flex justify-between items-center text-gray-700">
                      <span>Crédit (ancien plan):</span>
                      <span className="font-semibold text-green-600">
                        -{prorataCalculation.credit.toLocaleString('fr-MA')} MAD
                      </span>
                    </div>
                    
                    <div className="flex justify-between items-center text-gray-700">
                      <span>Charge (nouveau plan):</span>
                      <span className="font-semibold text-orange-600">
                        +{prorataCalculation.charge.toLocaleString('fr-MA')} MAD
                      </span>
                    </div>
                    
                    <div className="border-t-2 border-blue-300 pt-3 mt-3">
                      <div className="flex justify-between items-center">
                        <span className="text-lg font-bold text-blue-900">Montant à facturer:</span>
                        <span className={`text-2xl font-bold ${
                          prorataCalculation.netAmount >= 0 ? 'text-blue-600' : 'text-green-600'
                        }`}>
                          {prorataCalculation.netAmount >= 0 ? '+' : ''}
                          {prorataCalculation.netAmount.toLocaleString('fr-MA')} MAD
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        {prorataCalculation.netAmount >= 0 
                          ? "Ce montant sera facturé immédiatement"
                          : "Ce montant sera crédité sur le compte"}
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Preview */}
              {selectedPlan && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="bg-gray-50 rounded-xl p-6 mb-6"
                >
                  <h3 className="font-semibold text-lg mb-4 flex items-center">
                    <Calendar className="mr-2 text-blue-600" size={20} />
                    Aperçu du changement
                  </h3>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Plan actuel:</span>
                      <span className="font-semibold">{subscription?.plan_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Nouveau plan:</span>
                      <span className="font-semibold text-blue-600">{selectedPlan.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Changement:</span>
                      <span className={`font-semibold ${isUpgrade ? 'text-green-600' : isDowngrade ? 'text-orange-600' : 'text-gray-600'}`}>
                        {isUpgrade ? 'Upgrade ⬆️' : isDowngrade ? 'Downgrade ⬇️' : 'Équivalent'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Application:</span>
                      <span className="font-semibold">
                        {applyImmediately ? 'Immédiate' : 'Fin de période'}
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Warning for downgrade */}
              {isDowngrade && (
                <div className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                  <AlertCircle className="text-orange-600 flex-shrink-0 mt-0.5" size={20} />
                  <div className="text-sm text-orange-800">
                    <p className="font-semibold mb-1">Attention - Downgrade</p>
                    <p>Ce plan a des limites inférieures. Vérifiez que l'utilisateur n'utilise pas de fonctionnalités qui seront restreintes.</p>
                  </div>
                </div>
              )}
            </div>

            {/* Footer Actions */}
            <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6 flex justify-end gap-3">
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                onClick={handleChangePlan}
                disabled={!selectedPlan || loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Traitement...
                  </>
                ) : (
                  <>
                    <Check size={18} />
                    Confirmer le changement
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default PlanChangeModal;
