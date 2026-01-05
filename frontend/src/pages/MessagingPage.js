import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import {
  MessageSquare, Send, ArrowLeft, User, Search,
  CheckCheck, Check, Circle
} from 'lucide-react';
import { formatDate } from '../utils/helpers';

const MessagingPage = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (conversationId && conversations.length > 0) {
      const conv = conversations.find(c => c.id === conversationId);
      if (conv) {
        setActiveConversation(conv);
        fetchMessages(conversationId);
      }
    }
  }, [conversationId, conversations]);

  useEffect(() => {
    // Auto-scroll vers le bas quand nouveaux messages
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/messages/conversations');
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (convId) => {
    try {
      const response = await api.get(`/api/messages/${convId}`);
      setMessages(response.data.messages || []);
      // Ne pas écraser activeConversation avec les données de l'API messages
      // car elle contient déjà les infos merchant/influencer de l'API conversations
      // setActiveConversation(response.data.conversation);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeConversation) return;

    setSending(true);
    try {
      // Déterminer le destinataire
      const isUser1 = activeConversation.user1_id === user.id;
      const recipientId = isUser1 ? activeConversation.user2_id : activeConversation.user1_id;
      const recipientType = isUser1 ? activeConversation.user2_type : activeConversation.user1_type;

      await api.post('/api/messages/send', {
        recipient_id: recipientId,
        recipient_type: recipientType,
        content: newMessage,
        campaign_id: activeConversation.campaign_id
      });

      setNewMessage('');
      await fetchMessages(activeConversation.id);
      await fetchConversations(); // Rafraîchir la liste
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Erreur lors de l\'envoi du message');
    } finally {
      setSending(false);
    }
  };

  const getOtherUserInfo = (conversation) => {
    if (!conversation) return { name: 'Utilisateur', role: '', badge: '' };
    
    // Pour les admins, afficher les deux parties de la conversation
    if (user?.role === 'admin' && conversation.merchant && conversation.influencer) {
      return {
        name: `${conversation.merchant.name} ↔ ${conversation.influencer.name}`,
        role: 'Conversation',
        badge: 'bg-purple-100 text-purple-800'
      };
    }
    
    // Pour merchant/influencer, utiliser other_user
    if (conversation.other_user) {
      const roleLabels = {
        influencer: { name: 'Influenceur', badge: 'bg-green-100 text-green-800' },
        merchant: { name: 'Marchand', badge: 'bg-blue-100 text-blue-800' },
        admin: { name: 'Admin', badge: 'bg-purple-100 text-purple-800' }
      };
      
      const roleInfo = roleLabels[conversation.other_user.role] || { name: 'Utilisateur', badge: 'bg-gray-100 text-gray-800' };
      
      return {
        name: conversation.other_user.name || 'Utilisateur',
        role: roleInfo.name,
        badge: roleInfo.badge
      };
    }
    
    // Fallback pour l'ancien format
    const isUser1 = conversation.user1_id === user?.id;
    const otherType = isUser1 ? conversation.user2_type : conversation.user1_type;
    const otherId = isUser1 ? conversation.user2_id : conversation.user1_id;
    
    const roleLabels = {
      influencer: { name: 'Influenceur', badge: 'bg-green-100 text-green-800' },
      merchant: { name: 'Marchand', badge: 'bg-blue-100 text-blue-800' },
      admin: { name: 'Admin', badge: 'bg-purple-100 text-purple-800' }
    };
    
    const roleInfo = roleLabels[otherType] || { name: otherType || 'Utilisateur', badge: 'bg-gray-100 text-gray-800' };
    
    let defaultName = roleInfo.name;
    if (otherId) {
      const idStr = String(otherId);
      defaultName = `${roleInfo.name} #${idStr.substring(0, 8)}`;
    }
    
    return {
      name: conversation.other_user_name || defaultName,
      role: roleInfo.name,
      badge: roleInfo.badge
    };
  };

  const getOtherUserName = (conversation) => {
    return getOtherUserInfo(conversation).name;
  };

  const filteredConversations = conversations.filter(conv =>
    getOtherUserName(conv).toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.subject?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl">Chargement des messages...</div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-120px)]">
      <div className="flex h-full gap-6">
        {/* Liste des conversations - Sidebar */}
        <div className="w-80 flex-shrink-0">
          <Card className="h-full flex flex-col">
            <div className="p-4 border-b">
              <h2 className="text-xl font-bold mb-4">Modération & Support</h2>
              
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* Conversations list */}
            <div className="flex-1 overflow-y-auto">
              {filteredConversations.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  <MessageSquare size={48} className="mx-auto mb-3 text-gray-300" />
                  <p>Aucune conversation</p>
                  {user?.role === 'merchant' && (
                    <p className="text-sm mt-1">Les influenceurs vous contacteront pour vos campagnes</p>
                  )}
                  {user?.role === 'influencer' && (
                    <p className="text-sm mt-1">Contactez les marchands depuis leurs campagnes</p>
                  )}
                  {user?.role === 'admin' && (
                    <p className="text-sm mt-1">Gérez les conversations entre marchands et influenceurs</p>
                  )}
                </div>
              ) : (
                filteredConversations.map((conv) => {
                  const otherUser = getOtherUserInfo(conv);
                  return (
                    <div
                      key={conv.id}
                      onClick={() => navigate(`/messages/${conv.id}`)}
                      className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition ${
                        activeConversation?.id === conv.id ? 'bg-indigo-50 border-l-4 border-indigo-600' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2 flex-1">
                          <User size={20} className="text-gray-600" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-sm truncate">{otherUser.name}</span>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${otherUser.badge}`}>
                                {otherUser.role}
                              </span>
                            </div>
                          </div>
                        </div>
                        {conv.unread_count > 0 && (
                          <span className="bg-indigo-600 text-white text-xs rounded-full px-2 py-0.5 flex-shrink-0">
                            {conv.unread_count}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 font-medium mb-1 truncate">{conv.subject}</p>
                      {conv.last_message && (
                        <p className="text-xs text-gray-500 truncate">
                          {conv.last_message.content}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDate(conv.last_message_at)}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </div>

        {/* Zone de conversation */}
        <div className="flex-1">
          {activeConversation ? (
            <Card className="h-full flex flex-col">
              {/* Header conversation */}
              <div className="p-4 border-b flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => navigate('/messages')}
                    className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <ArrowLeft size={20} />
                  </button>
                  <div className="bg-indigo-100 w-10 h-10 rounded-full flex items-center justify-center">
                    <User size={20} className="text-indigo-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{getOtherUserInfo(activeConversation).name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getOtherUserInfo(activeConversation).badge}`}>
                        {getOtherUserInfo(activeConversation).role}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{activeConversation.subject}</p>
                  </div>
                </div>
                <Circle size={12} className="text-green-500 fill-green-500" />
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-12">
                    <MessageSquare size={48} className="mx-auto mb-3 text-gray-300" />
                    <p>Aucun message encore</p>
                    <p className="text-sm mt-1">Commencez la conversation !</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => {
                    const isOwn = msg.sender_id === user?.id || msg.is_mine;
                    const showSenderName = user?.role === 'admin' || !isOwn;
                    
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-md px-4 py-2 rounded-lg ${
                            isOwn
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          {user?.role === 'admin' && msg.sender_name && (
                            <div className={`text-xs font-semibold mb-1 ${isOwn ? 'text-indigo-200' : 'text-gray-600'}`}>
                              {msg.sender_name}
                              {msg.sender_role && (
                                <span className={`ml-2 px-2 py-0.5 rounded ${
                                  msg.sender_role === 'merchant' ? 'bg-blue-200 text-blue-800' :
                                  msg.sender_role === 'influencer' ? 'bg-green-200 text-green-800' :
                                  'bg-gray-200 text-gray-800'
                                }`}>
                                  {msg.sender_role === 'merchant' ? 'Marchand' : 
                                   msg.sender_role === 'influencer' ? 'Influenceur' : 
                                   msg.sender_role}
                                </span>
                              )}
                            </div>
                          )}
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          <div className={`flex items-center gap-1 mt-1 text-xs ${isOwn ? 'text-indigo-200' : 'text-gray-500'}`}>
                            <span>{new Date(msg.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>
                            {isOwn && (
                              msg.is_read ? <CheckCheck size={14} /> : <Check size={14} />
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input message */}
              <div className="p-4 border-t">
                {/* Messages prédéfinis pour admin */}
                {user?.role === 'admin' && (
                  <div className="mb-3 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setNewMessage("Bonjour, je suis l'administrateur de la plateforme. Comment puis-je vous aider à résoudre ce différend ?")}
                      className="text-xs px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition"
                    >
                      👋 Intervention admin
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewMessage("Merci de rester courtois et professionnel dans vos échanges. Je suis là pour faciliter la communication entre les deux parties.")}
                      className="text-xs px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition"
                    >
                      ⚖️ Rappel courtoisie
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewMessage("Pouvez-vous me fournir plus de détails sur le problème rencontré ? Je vais examiner la situation et revenir vers vous rapidement.")}
                      className="text-xs px-3 py-1.5 bg-yellow-100 text-yellow-700 rounded-full hover:bg-yellow-200 transition"
                    >
                      🔍 Demande détails
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewMessage("J'ai examiné votre cas. Voici ma recommandation pour résoudre cette situation de manière équitable pour les deux parties...")}
                      className="text-xs px-3 py-1.5 bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition"
                    >
                      ✅ Résolution
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewMessage("Pour toute question concernant les paiements, veuillez contacter notre service financier à finance@getyourshare.com")}
                      className="text-xs px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded-full hover:bg-indigo-200 transition"
                    >
                      💰 Paiements
                    </button>
                    <button
                      type="button"
                      onClick={() => setNewMessage("Si le problème persiste, je vais suspendre temporairement cette collaboration jusqu'à clarification. Merci de votre compréhension.")}
                      className="text-xs px-3 py-1.5 bg-red-100 text-red-700 rounded-full hover:bg-red-200 transition"
                    >
                      ⛔ Suspension
                    </button>
                  </div>
                )}
                
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Écrivez votre message..."
                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    disabled={sending}
                  />
                  <Button type="submit" disabled={sending || !newMessage.trim()}>
                    <Send size={20} />
                  </Button>
                </form>
              </div>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500 max-w-md mx-auto">
                <MessageSquare size={64} className="mx-auto mb-4 text-gray-300" />
                <p className="text-xl font-semibold mb-2">Messagerie Professionnelle</p>
                
                {user?.role === 'merchant' && (
                  <div className="space-y-2 text-sm">
                    <p className="font-medium text-gray-700">💼 En tant que Marchand :</p>
                    <p>• Les influenceurs vous contacteront via vos campagnes</p>
                    <p>• Vous recevrez des messages pour des collaborations</p>
                    <p>• Gérez les questions sur vos produits et commissions</p>
                  </div>
                )}
                
                {user?.role === 'influencer' && (
                  <div className="space-y-2 text-sm">
                    <p className="font-medium text-gray-700">🌟 En tant qu'Influenceur :</p>
                    <p>• Contactez les marchands depuis le Marketplace</p>
                    <p>• Posez vos questions sur les campagnes</p>
                    <p>• Négociez vos conditions de collaboration</p>
                    <div className="mt-4">
                      <Button disabled={loading} onClick={() => navigate('/dashboard/marketplace', { state: { fromDashboard: true } })}>
                        Découvrir les Campagnes
                      </Button>
                    </div>
                  </div>
                )}
                
                {user?.role === 'admin' && (
                  <div className="space-y-2 text-sm">
                    <p className="font-medium text-gray-700">👑 En tant qu'Admin :</p>
                    <p>• Supervisez toutes les conversations</p>
                    <p>• Résolvez les litiges entre parties</p>
                    <p>• Assistez marchands et influenceurs</p>
                  </div>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessagingPage;
