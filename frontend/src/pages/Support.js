import React, { useState, useRef, useEffect } from 'react';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import LiveChatWidget from '../components/chat/LiveChatWidget';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { MessageCircle, Mail, Phone, Clock, Send, HelpCircle, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../utils/api';
import { formatDateShort } from '../utils/helpers';

const Support = () => {
  const toast = useToast();
  const { user } = useAuth();
  const chatWidgetRef = useRef(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    subject: '',
    category: 'general',
    priority: 'medium',
    message: ''
  });

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await api.get('/api/support/tickets');
      setTickets(response.data);
    } catch (error) {
      console.error('Erreur chargement tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/support/tickets', formData);
      toast.success('Votre demande a été envoyée avec succès! Notre équipe vous répondra dans les plus brefs délais.');
      setFormData({ subject: '', category: 'general', priority: 'medium', message: '' });
      fetchTickets(); // Refresh list
    } catch (error) {
      console.error('Erreur création ticket:', error);
      toast.error('Erreur lors de la création du ticket. Veuillez réessayer.');
    }
  };

  const contactMethods = [
    {
      icon: <MessageCircle className="text-blue-500" size={32} />,
      title: 'Chat en Direct',
      description: 'Obtenez une réponse instantanée',
      action: 'Démarrer le chat',
      available: 'Disponible maintenant',
      color: 'bg-blue-50 hover:bg-blue-100'
    },
    {
      icon: <Mail className="text-green-500" size={32} />,
      title: 'Email Support',
      description: 'support@shareyoursales.com',
      action: 'Envoyer un email',
      available: 'Réponse sous 24h',
      color: 'bg-green-50 hover:bg-green-100'
    },
    {
      icon: <Phone className="text-purple-500" size={32} />,
      title: 'Support Téléphonique',
      description: '+212 600-000-000',
      action: 'Appeler maintenant',
      available: 'Lun-Ven: 9h-18h',
      color: 'bg-purple-50 hover:bg-purple-100'
    }
  ];

  const faqCategories = [
    {
      title: 'Compte & Profil',
      icon: '👤',
      questions: [
        { q: 'Comment modifier mon profil ?', a: 'Allez dans Paramètres > Personnel pour modifier vos informations.' },
        { q: 'Comment réinitialiser mon mot de passe ?', a: 'Cliquez sur "Mot de passe oublié" sur la page de connexion.' },
        { q: 'Comment supprimer mon compte ?', a: 'Contactez le support pour demander la suppression de votre compte.' }
      ]
    },
    {
      title: 'Paiements & Commissions',
      icon: '💰',
      questions: [
        { q: 'Quand reçois-je mes paiements ?', a: 'Les paiements sont traités le 15 de chaque mois pour le mois précédent.' },
        { q: 'Quels sont les modes de paiement ?', a: 'Nous supportons virements bancaires, PayPal et Stripe.' },
        { q: 'Quel est le seuil minimum de retrait ?', a: 'Le montant minimum est de 100 MAD.' }
      ]
    },
    {
      title: 'Campagnes & Liens',
      icon: '🎯',
      questions: [
        { q: 'Comment créer un lien de tracking ?', a: 'Allez dans Mes Liens et cliquez sur "Nouveau Lien".' },
        { q: 'Combien de campagnes puis-je rejoindre ?', a: 'Vous pouvez rejoindre un nombre illimité de campagnes.' },
        { q: 'Comment suivre mes performances ?', a: 'Consultez votre Dashboard pour voir toutes vos statistiques en temps réel.' }
      ]
    },
    {
      title: 'Technique & Intégration',
      icon: '⚙️',
      questions: [
        { q: 'Comment intégrer l\'API ?', a: 'Consultez notre documentation API dans la section Documentation.' },
        { q: 'Les webhooks sont-ils disponibles ?', a: 'Oui, configurez-les dans Paramètres > Webhooks.' },
        { q: 'Quels CMS sont supportés ?', a: 'WooCommerce, Shopify, PrestaShop et intégrations personnalisées.' }
      ]
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'text-blue-600 bg-blue-50';
      case 'in_progress': return 'text-yellow-600 bg-yellow-50';
      case 'resolved': return 'text-green-600 bg-green-50';
      case 'closed': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'open': return 'Ouvert';
      case 'in_progress': return 'En cours';
      case 'resolved': return 'Résolu';
      case 'closed': return 'Fermé';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Centre de Support</h1>
        <p className="text-blue-100">Notre équipe est là pour vous aider 24/7</p>
      </div>

      {/* Contact Methods */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {contactMethods.map((method, index) => (
          <Card key={index} className={method.color}>
            <div className="text-center space-y-4">
              <div className="flex justify-center">{method.icon}</div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">{method.title}</h3>
                <p className="text-sm text-gray-600 mb-2">{method.description}</p>
                <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
                  <Clock size={14} />
                  <span>{method.available}</span>
                </div>
              </div>
              <Button 
                size="sm" 
                className="w-full"
                onClick={() => {
                  if (method.title === 'Chat en Direct') {
                    if (user) {
                      if (chatWidgetRef.current) {
                        chatWidgetRef.current.open();
                      } else {
                        toast.info('Le chat est en cours de chargement...');
                      }
                    } else {
                      toast.info('Veuillez vous connecter pour accéder au chat en direct.');
                    }
                  } else if (method.title === 'Email Support') {
                    window.location.href = 'mailto:support@shareyoursales.com';
                  } else if (method.title === 'Support Téléphonique') {
                    toast.info('Appelez-nous au +212 600-000-000');
                  }
                }}
              >
                {method.action}
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Ticket Status */}
      {tickets.length > 0 && (
        <Card title="📋 Mes Tickets de Support">
          <div className="space-y-3">
            {tickets.map((ticket) => (
              <div key={ticket.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <span className="font-mono text-sm text-gray-600">{ticket.ticket_number}</span>
                  <div>
                    <h4 className="font-semibold text-gray-900">{ticket.subject}</h4>
                    <p className="text-sm text-gray-600">{formatDateShort(ticket.created_at)}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ticket.status)}`}>
                  {getStatusLabel(ticket.status)}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Contact Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="✉️ Créer un Ticket de Support">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Sujet</label>
                <input
                  type="text"
                  required
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Décrivez brièvement votre problème"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="general">Question Générale</option>
                    <option value="technical">Problème Technique</option>
                    <option value="payment">Paiement</option>
                    <option value="account">Compte</option>
                    <option value="campaign">Campagnes</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Priorité</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Basse</option>
                    <option value="medium">Moyenne</option>
                    <option value="high">Haute</option>
                    <option value="urgent">Urgente</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                <textarea
                  required
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  rows="6"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Décrivez votre problème en détail..."
                />
              </div>

              <Button type="submit" className="w-full">
                <Send size={16} className="mr-2" />
                Envoyer le Ticket
              </Button>
            </form>
          </Card>
        </div>

        {/* Support Info */}
        <div className="space-y-6">
          <Card title="⏰ Temps de Réponse">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="text-green-500" size={20} />
                  <span className="text-sm font-medium">Chat</span>
                </div>
                <span className="text-sm text-green-600">~2 min</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="text-blue-500" size={20} />
                  <span className="text-sm font-medium">Email</span>
                </div>
                <span className="text-sm text-blue-600">~24h</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <HelpCircle className="text-purple-500" size={20} />
                  <span className="text-sm font-medium">Ticket</span>
                </div>
                <span className="text-sm text-purple-600">~48h</span>
              </div>
            </div>
          </Card>

          <Card title="📚 Ressources Utiles">
            <div className="space-y-2">
              <a href="/documentation" className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all text-sm text-gray-700">
                📖 Documentation Complète
              </a>
              <a href="/video-tutorials" className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all text-sm text-gray-700">
                🎥 Vidéos Tutoriels
              </a>
              <a href="/getting-started" className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all text-sm text-gray-700">
                🚀 Guide de Démarrage
              </a>
            </div>
          </Card>
        </div>
      </div>

      {/* FAQ Section */}
      <Card title="❓ Questions Fréquentes">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {faqCategories.map((category, index) => (
            <div key={index}>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <span>{category.icon}</span>
                <span>{category.title}</span>
              </h3>
              <div className="space-y-3">
                {category.questions.map((item, qIndex) => (
                  <details key={qIndex} className="bg-gray-50 rounded-lg p-3 cursor-pointer">
                    <summary className="font-medium text-gray-900">{item.q}</summary>
                    <p className="mt-2 text-sm text-gray-600">{item.a}</p>
                  </details>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {user && <LiveChatWidget ref={chatWidgetRef} userId={user.id} userRole={user.role || 'customer'} />}
    </div>
  );
};

export default Support;
