import React, { useState } from 'react';
import {
  Phone, Mail, MessageCircle, PlusCircle, Heart, Search,
  TrendingUp, Target, Zap, Award, BarChart2, Users
} from 'lucide-react';

/**
 * Quick action buttons for mobile - context-aware based on user type
 * Supports offline mode with IndexedDB sync
 */
const QuickActions = ({ userType, userId }) => {
  const [showAddModal, setShowAddModal] = useState(false);

  const getActions = () => {
    if (userType === 'merchant') {
      return [
        {
          icon: PlusCircle,
          label: 'Nouveau Produit',
          color: 'from-blue-500 to-blue-600',
          action: () => window.location.href = '/products/new'
        },
        {
          icon: Search,
          label: 'Trouver Influenceur',
          color: 'from-purple-500 to-purple-600',
          action: () => window.location.href = '/influencer-matching'
        },
        {
          icon: BarChart2,
          label: 'Analytics',
          color: 'from-green-500 to-green-600',
          action: () => window.location.href = '/analytics-pro'
        },
        {
          icon: Award,
          label: 'Gamification',
          color: 'from-yellow-500 to-yellow-600',
          action: () => window.location.href = '/gamification'
        }
      ];
    } else if (userType === 'influencer') {
      return [
        {
          icon: Zap,
          label: 'Créer Contenu',
          color: 'from-pink-500 to-pink-600',
          action: () => window.location.href = '/content/new'
        },
        {
          icon: Heart,
          label: 'Mes Marques',
          color: 'from-red-500 to-red-600',
          action: () => window.location.href = '/brands'
        },
        {
          icon: TrendingUp,
          label: 'Performance',
          color: 'from-green-500 to-green-600',
          action: () => window.location.href = '/analytics-pro'
        },
        {
          icon: Award,
          label: 'Niveaux',
          color: 'from-yellow-500 to-yellow-600',
          action: () => window.location.href = '/gamification'
        }
      ];
    } else {
      // Sales Rep
      return [
        {
          icon: Phone,
          label: 'Appeler Lead',
          color: 'from-green-500 to-green-600',
          action: () => handleCallLead()
        },
        {
          icon: PlusCircle,
          label: 'Nouveau Lead',
          color: 'from-blue-500 to-blue-600',
          action: () => setShowAddModal(true)
        },
        {
          icon: Target,
          label: 'Pipeline',
          color: 'from-purple-500 to-purple-600',
          action: () => window.location.href = '/sales/pipeline'
        },
        {
          icon: Mail,
          label: 'Envoyer Email',
          color: 'from-orange-500 to-orange-600',
          action: () => handleSendEmail()
        }
      ];
    }
  };

  const handleCallLead = async () => {
    // Get hot lead
    try {
      const response = await fetch(`/api/sales/leads/hot?sales_rep_id=${userId}&limit=1`);
      const data = await response.json();

      if (data.leads && data.leads.length > 0) {
        const hotLead = data.leads[0];
        if (hotLead.contact_phone) {
          window.location.href = `tel:${hotLead.contact_phone}`;

          // Log activity (offline-capable)
          await logActivity({
            type: 'call',
            lead_id: hotLead.id,
            notes: 'Appel depuis quick action mobile'
          });
        } else {
          alert('Ce lead n\'a pas de numéro de téléphone');
        }
      } else {
        alert('Aucun lead HOT disponible');
      }
    } catch (error) {
      console.error('Error calling lead:', error);
      alert('Erreur lors de l\'appel');
    }
  };

  const handleSendEmail = async () => {
    try {
      const response = await fetch(`/api/sales/leads/hot?sales_rep_id=${userId}&limit=1`);
      const data = await response.json();

      if (data.leads && data.leads.length > 0) {
        const hotLead = data.leads[0];
        if (hotLead.contact_email) {
          const subject = encodeURIComponent('Proposition GetYourShare');
          const body = encodeURIComponent(`Bonjour ${hotLead.contact_name},\n\n`);
          window.location.href = `mailto:${hotLead.contact_email}?subject=${subject}&body=${body}`;

          // Log activity
          await logActivity({
            type: 'email',
            lead_id: hotLead.id,
            notes: 'Email envoyé depuis quick action mobile'
          });
        } else {
          alert('Ce lead n\'a pas d\'email');
        }
      } else {
        alert('Aucun lead HOT disponible');
      }
    } catch (error) {
      console.error('Error sending email:', error);
      alert('Erreur lors de l\'envoi d\'email');
    }
  };

  const logActivity = async (activityData) => {
    try {
      await fetch('/api/sales/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sales_rep_id: userId,
          ...activityData,
          created_at: new Date().toISOString()
        })
      });
    } catch (error) {
      // If offline, save to IndexedDB for later sync

      await saveToIndexedDB('pendingActivities', {
        data: {
          sales_rep_id: userId,
          ...activityData
        },
        token: localStorage.getItem('auth_token')
      });

      // Trigger background sync
      if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('sync-activities');
      }
    }
  };

  const actions = getActions();

  return (
    <>
      <div className="bg-white rounded-2xl shadow-md p-4">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Actions Rapides</h2>
        <div className="grid grid-cols-4 gap-3">
          {actions.map((action, index) => (
            <QuickActionButton key={index} {...action} />
          ))}
        </div>
      </div>

      {/* Add Lead Modal (for sales reps) */}
      {showAddModal && userType === 'sales_rep' && (
        <AddLeadModal
          userId={userId}
          onClose={() => setShowAddModal(false)}
        />
      )}
    </>
  );
};

const QuickActionButton = ({ icon: Icon, label, color, action }) => {
  return (
    <button
      onClick={action}
      className="flex flex-col items-center space-y-2 active:scale-95 transition"
    >
      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${color} flex items-center justify-center shadow-lg`}>
        <Icon className="h-7 w-7 text-white" />
      </div>
      <span className="text-xs font-medium text-gray-700 text-center leading-tight">
        {label}
      </span>
    </button>
  );
};

// ==================== ADD LEAD MODAL ====================
const AddLeadModal = ({ userId, onClose }) => {
  const [formData, setFormData] = useState({
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    company_name: '',
    estimated_value: '',
    source: 'mobile_app'
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await fetch('/api/sales/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sales_rep_id: userId,
          ...formData,
          estimated_value: parseFloat(formData.estimated_value) || 0
        })
      });

      if (response.ok) {
        alert('Lead créé avec succès! ✅');
        onClose();
        window.location.reload();
      } else {
        throw new Error('Failed to create lead');
      }
    } catch (error) {
      console.error('Error creating lead:', error);

      // Save offline
      await saveToIndexedDB('pendingLeads', {
        data: {
          sales_rep_id: userId,
          ...formData
        },
        token: localStorage.getItem('auth_token')
      });

      // Trigger background sync
      if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('sync-leads');
      }

      alert('Lead sauvegardé hors ligne. Sera synchronisé à la reconnexion. 📱');
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center">
      <div className="bg-white rounded-t-3xl sm:rounded-3xl w-full sm:max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Nouveau Lead</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nom du contact *
            </label>
            <input
              type="text"
              required
              value={formData.contact_name}
              onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Jean Dupont"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.contact_email}
              onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="jean@exemple.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Téléphone
            </label>
            <input
              type="tel"
              value={formData.contact_phone}
              onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="+212 6 XX XX XX XX"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entreprise
            </label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nom de l'entreprise"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Valeur estimée (MAD)
            </label>
            <input
              type="number"
              value={formData.estimated_value}
              onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="10000"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-xl font-medium text-gray-700 hover:bg-gray-50 transition"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg transition disabled:opacity-50"
            >
              {saving ? 'Enregistrement...' : 'Créer Lead'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ==================== INDEXEDDB HELPER ====================
async function saveToIndexedDB(storeName, data) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('GetYourShareDB', 2);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction(storeName, 'readwrite');
      const store = transaction.objectStore(storeName);
      const addRequest = store.add(data);

      addRequest.onsuccess = () => resolve();
      addRequest.onerror = () => reject(addRequest.error);
    };
  });
}

export default QuickActions;
