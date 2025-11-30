import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, DollarSign, AlertTriangle, Check, CreditCard, Mail, Wallet } from 'lucide-react';
import api from '../../utils/api';

const RefundModal = ({ isOpen, onClose, subscription, onSuccess }) => {
  const [refundType, setRefundType] = useState('partial'); // 'full' or 'partial'
  const [amount, setAmount] = useState('');
  const [reason, setReason] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('stripe'); // 'stripe', 'credit', 'manual'
  const [loading, setLoading] = useState(false);

  const maxAmount = parseFloat(subscription?.monthly_fee || 0);

  const handleRefund = async () => {
    if (!reason.trim()) {
      alert('Veuillez indiquer la raison du remboursement');
      return;
    }

    const refundAmount = refundType === 'full' ? maxAmount : parseFloat(amount);
    
    if (refundType === 'partial' && (!refundAmount || refundAmount <= 0 || refundAmount > maxAmount)) {
      alert(`Le montant doit être entre 0 et ${maxAmount} MAD`);
      return;
    }

    setLoading(true);
    try {
      const response = await api.post(`/api/subscriptions/admin/${subscription.id}/refund`, {
        amount: refundType === 'full' ? null : refundAmount,
        reason: reason.trim(),
        type: paymentMethod
      });

      if (response.data.success) {
        onSuccess(response.data);
        onClose();
        // Reset form
        setRefundType('partial');
        setAmount('');
        setReason('');
        setPaymentMethod('stripe');
      }
    } catch (error) {
      console.error('Error processing refund:', error);
      alert('Erreur lors du remboursement: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setRefundType('partial');
    setAmount('');
    setReason('');
    setPaymentMethod('stripe');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-red-600 to-orange-600 p-6 rounded-t-2xl text-white">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-2xl font-bold">Remboursement</h2>
                  <p className="text-red-100 text-sm mt-1">
                    Abonnement: {subscription?.plan_name}
                  </p>
                </div>
                <button
                  onClick={() => {
                    resetForm();
                    onClose();
                  }}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Warning */}
              <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-lg p-4">
                <AlertTriangle className="text-amber-600 flex-shrink-0 mt-0.5" size={20} />
                <div className="text-sm text-amber-800">
                  <p className="font-semibold mb-1">Action Importante</p>
                  <p>Un remboursement complet annulera automatiquement l'abonnement. Cette action ne peut pas être annulée.</p>
                </div>
              </div>

              {/* User Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Utilisateur:</span>
                    <p className="font-semibold">{subscription?.users?.full_name || subscription?.users?.email}</p>
                  </div>
                  <div>
                    <span className="text-gray-600">Montant actuel:</span>
                    <p className="font-semibold text-blue-600">{maxAmount.toLocaleString('fr-MA')} MAD/mois</p>
                  </div>
                </div>
              </div>

              {/* Refund Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Type de remboursement
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setRefundType('partial')}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      refundType === 'partial'
                        ? 'border-blue-600 bg-blue-50 shadow-md'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">Partiel</span>
                      {refundType === 'partial' && (
                        <div className="bg-blue-600 text-white p-1 rounded-full">
                          <Check size={14} />
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-gray-600">Rembourser un montant personnalisé</p>
                  </motion.div>

                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setRefundType('full')}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      refundType === 'full'
                        ? 'border-red-600 bg-red-50 shadow-md'
                        : 'border-gray-200 hover:border-red-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">Complet</span>
                      {refundType === 'full' && (
                        <div className="bg-red-600 text-white p-1 rounded-full">
                          <Check size={14} />
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-gray-600">Rembourser la totalité et annuler</p>
                  </motion.div>
                </div>
              </div>

              {/* Amount (if partial) */}
              {refundType === 'partial' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Montant à rembourser
                  </label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      min="0"
                      max={maxAmount}
                      step="0.01"
                      placeholder="0.00"
                      className="w-full pl-10 pr-16 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg font-semibold"
                    />
                    <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">
                      MAD
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Maximum: {maxAmount.toLocaleString('fr-MA')} MAD
                  </p>
                </motion.div>
              )}

              {/* Payment Method */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Méthode de remboursement
                </label>
                <div className="space-y-3">
                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    onClick={() => setPaymentMethod('stripe')}
                    className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      paymentMethod === 'stripe'
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <CreditCard className={`mr-3 ${paymentMethod === 'stripe' ? 'text-blue-600' : 'text-gray-400'}`} size={20} />
                    <div className="flex-1">
                      <span className="font-medium">Stripe</span>
                      <p className="text-xs text-gray-600">Remboursement automatique sur la carte</p>
                    </div>
                    {paymentMethod === 'stripe' && (
                      <Check className="text-blue-600" size={20} />
                    )}
                  </motion.div>

                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    onClick={() => setPaymentMethod('credit')}
                    className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      paymentMethod === 'credit'
                        ? 'border-green-600 bg-green-50'
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                  >
                    <Wallet className={`mr-3 ${paymentMethod === 'credit' ? 'text-green-600' : 'text-gray-400'}`} size={20} />
                    <div className="flex-1">
                      <span className="font-medium">Crédit compte</span>
                      <p className="text-xs text-gray-600">Ajouter un crédit utilisable plus tard</p>
                    </div>
                    {paymentMethod === 'credit' && (
                      <Check className="text-green-600" size={20} />
                    )}
                  </motion.div>

                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    onClick={() => setPaymentMethod('manual')}
                    className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      paymentMethod === 'manual'
                        ? 'border-purple-600 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300'
                    }`}
                  >
                    <Mail className={`mr-3 ${paymentMethod === 'manual' ? 'text-purple-600' : 'text-gray-400'}`} size={20} />
                    <div className="flex-1">
                      <span className="font-medium">Manuel</span>
                      <p className="text-xs text-gray-600">Virement bancaire ou autre méthode</p>
                    </div>
                    {paymentMethod === 'manual' && (
                      <Check className="text-purple-600" size={20} />
                    )}
                  </motion.div>
                </div>
              </div>

              {/* Reason */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Raison du remboursement <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Décrivez la raison du remboursement (obligatoire pour l'audit)..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Cette information sera enregistrée dans l'historique
                </p>
              </div>

              {/* Summary */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-blue-200">
                <h3 className="font-semibold text-lg mb-4 text-gray-900">Résumé du remboursement</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-semibold">
                      {refundType === 'full' ? 'Remboursement complet' : 'Remboursement partiel'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Montant:</span>
                    <span className="font-semibold text-blue-600 text-lg">
                      {(refundType === 'full' ? maxAmount : parseFloat(amount) || 0).toLocaleString('fr-MA')} MAD
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Méthode:</span>
                    <span className="font-semibold capitalize">{paymentMethod}</span>
                  </div>
                  {refundType === 'full' && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Statut abonnement:</span>
                      <span className="font-semibold text-red-600">Sera annulé</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="bg-gray-50 p-6 rounded-b-2xl flex justify-end gap-3">
              <button
                onClick={() => {
                  resetForm();
                  onClose();
                }}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                onClick={handleRefund}
                disabled={loading || !reason.trim() || (refundType === 'partial' && (!amount || parseFloat(amount) <= 0))}
                className="px-6 py-2 bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-lg hover:from-red-700 hover:to-orange-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all font-medium flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Traitement...
                  </>
                ) : (
                  <>
                    <Check size={18} />
                    Confirmer le remboursement
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

export default RefundModal;
