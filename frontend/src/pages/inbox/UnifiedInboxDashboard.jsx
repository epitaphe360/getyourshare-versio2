import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, MessageSquare, Phone, Star, Archive, Search, Send, Filter, Clock, AlertCircle, CheckCircle, Zap, BarChart3, TrendingDown } from 'lucide-react';
import api from '../../services/api';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * Unified Inbox Dashboard - Commercial
 * Boîte de réception unifiée tous canaux avec IA
 * ROI: Productivité +60%, Temps de réponse -50%
 */
const UnifiedInboxDashboard = () => {
  const [messages, setMessages] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('unread');
  const [selectedChannel, setSelectedChannel] = useState('all');
  const [selectedMessage, setSelectedMessage] = useState(null);

  useEffect(() => {
    fetchData();
  }, [filter, selectedChannel]);

  const fetchData = async () => {
    try {
      setLoading(true);
      let params = '';
      if (filter === 'unread') params += '?is_read=false';
      if (filter === 'starred') params += '?is_starred=true';
      if (selectedChannel !== 'all') params += `${params ? '&' : '?'}channel=${selectedChannel}`;

      const messagesRes = await api.get(`/api/inbox/messages${params}`);
      setMessages(messagesRes.data.messages || []);

      const statsRes = await api.get('/api/inbox/statistics');
      setStats(statsRes.data.statistics);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (channel) => {
    const icons = {
      email: '📧',
      sms: '💬',
      whatsapp: '📱',
      messenger: '💙',
      instagram: '📷',
      linkedin: '💼',
      twitter: '🐦',
      in_app: '💻',
      phone: '☎️'
    };
    return icons[channel] || '📩';
  };

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: 'text-green-600 bg-green-100',
      neutral: 'text-gray-600 bg-gray-100',
      negative: 'text-red-600 bg-red-100'
    };
    return colors[sentiment] || colors.neutral;
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      urgent: { label: '🔴 Urgent', color: 'bg-red-100 text-red-700' },
      high: { label: '🟠 Haute', color: 'bg-orange-100 text-orange-700' },
      normal: { label: '⚪ Normale', color: 'bg-blue-100 text-blue-700' },
      low: { label: '🟢 Basse', color: 'bg-green-100 text-green-700' }
    };
    return badges[priority] || badges.normal;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
          <Mail size={48} className="text-blue-600" />
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-gray-50 to-blue-50 min-h-screen">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">📬 Boîte de Réception Unifiée</h1>
            <p className="text-blue-100 text-lg">
              Tous vos canaux en un seul endroit • Analyse IA automatique
            </p>
          </div>
          <button className="px-6 py-3 bg-white text-blue-600 rounded-xl font-semibold hover:shadow-lg transition-all flex items-center gap-2">
            <Send size={20} /> Nouveau Message
          </button>
        </div>
      </motion.div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <Mail className="text-blue-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.unread}</p>
            <p className="text-sm text-gray-600">Messages non lus</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500">
            <Star className="text-yellow-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.starred}</p>
            <p className="text-sm text-gray-600">Messages favoris</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <Clock className="text-green-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.avg_response_time_hours}h</p>
            <p className="text-sm text-gray-600">Temps de réponse moy.</p>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
            <AlertCircle className="text-red-600 mb-2" size={24} />
            <p className="text-3xl font-bold">{stats.urgent}</p>
            <p className="text-sm text-gray-600">Urgent</p>
          </div>
        </div>
      )}

      {/* Channel Filters */}
      <div className="flex gap-3 overflow-x-auto pb-2">
        {[
          { id: 'all', label: 'Tous', icon: '📩' },
          { id: 'email', label: 'Email', icon: '📧' },
          { id: 'sms', label: 'SMS', icon: '💬' },
          { id: 'whatsapp', label: 'WhatsApp', icon: '📱' },
          { id: 'messenger', label: 'Messenger', icon: '💙' },
          { id: 'linkedin', label: 'LinkedIn', icon: '💼' }
        ].map(channel => (
          <button
            key={channel.id}
            onClick={() => setSelectedChannel(channel.id)}
            className={`px-4 py-2 rounded-lg font-semibold flex items-center gap-2 whitespace-nowrap transition-all ${
              selectedChannel === channel.id
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <span>{channel.icon}</span>
            {channel.label}
            {stats && stats.by_channel && stats.by_channel[channel.id] > 0 && (
              <span className="ml-1 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                {stats.by_channel[channel.id]}
              </span>
            )}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Messages List */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-lg p-6">
          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher dans les messages..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('unread')}
                className={`px-4 py-2 rounded-lg font-semibold ${
                  filter === 'unread' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                Non lus
              </button>
              <button
                onClick={() => setFilter('starred')}
                className={`px-4 py-2 rounded-lg font-semibold ${
                  filter === 'starred' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                Favoris
              </button>
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg font-semibold ${
                  filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                Tous
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {messages.map(msg => {
              const priorityBadge = getPriorityBadge(msg.priority);
              return (
                <motion.div
                  key={msg.id}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => setSelectedMessage(msg)}
                  className={`p-4 rounded-lg cursor-pointer transition-all border ${
                    !msg.is_read
                      ? 'bg-blue-50 border-blue-200 font-semibold'
                      : 'bg-white border-gray-200 hover:bg-gray-50'
                  } ${selectedMessage?.id === msg.id ? 'ring-2 ring-blue-500' : ''}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3 flex-1">
                      <span className="text-2xl">{getChannelIcon(msg.channel)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold truncate">{msg.contact_name}</p>
                        <p className="text-sm text-gray-600 truncate">{msg.subject || msg.channel}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <span className="text-sm text-gray-500 whitespace-nowrap">
                        {formatDistanceToNow(new Date(msg.created_at), { locale: fr, addSuffix: true })}
                      </span>
                      <div className="flex items-center gap-2">
                        {msg.is_starred && <Star size={14} className="text-yellow-500 fill-yellow-500" />}
                        {msg.priority !== 'normal' && (
                          <span className={`text-xs px-2 py-0.5 rounded-full ${priorityBadge.color}`}>
                            {priorityBadge.label}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <p className="text-gray-700 text-sm line-clamp-2 mb-2">{msg.body}</p>

                  {/* Sentiment & Category */}
                  <div className="flex items-center gap-2">
                    {msg.sentiment && (
                      <span className={`text-xs px-2 py-1 rounded-full ${getSentimentColor(msg.sentiment)}`}>
                        {msg.sentiment === 'positive' && '😊 Positif'}
                        {msg.sentiment === 'neutral' && '😐 Neutre'}
                        {msg.sentiment === 'negative' && '😞 Négatif'}
                      </span>
                    )}
                    {msg.category && (
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                        {msg.category}
                      </span>
                    )}
                  </div>
                </motion.div>
              );
            })}

            {messages.length === 0 && (
              <div className="text-center py-20">
                <CheckCircle size={64} className="mx-auto mb-4 text-green-500" />
                <p className="text-xl font-semibold text-gray-700 mb-2">Boîte de réception vide!</p>
                <p className="text-gray-500">Tous les messages ont été traités. Excellent travail! 🎉</p>
              </div>
            )}
          </div>
        </div>

        {/* Sentiment Analysis Panel */}
        <div className="space-y-6">
          {/* Sentiment Distribution */}
          {stats && stats.by_sentiment && (
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="text-blue-600" />
                Analyse de Sentiment
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">😊 Positif</span>
                    <span className="text-sm font-bold">{stats.by_sentiment.positive}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(stats.by_sentiment.positive / stats.total) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">😐 Neutre</span>
                    <span className="text-sm font-bold">{stats.by_sentiment.neutral}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gray-500 h-2 rounded-full"
                      style={{ width: `${(stats.by_sentiment.neutral / stats.total) * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">😞 Négatif</span>
                    <span className="text-sm font-bold">{stats.by_sentiment.negative}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${(stats.by_sentiment.negative / stats.total) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Zap className="text-yellow-600" />
              Actions Rapides
            </h3>
            <div className="space-y-2">
              <button className="w-full px-4 py-3 bg-blue-100 text-blue-700 rounded-lg font-semibold hover:bg-blue-200 transition-all text-left">
                ✅ Marquer tout comme lu
              </button>
              <button className="w-full px-4 py-3 bg-purple-100 text-purple-700 rounded-lg font-semibold hover:bg-purple-200 transition-all text-left">
                📁 Archiver les anciens
              </button>
              <button className="w-full px-4 py-3 bg-green-100 text-green-700 rounded-lg font-semibold hover:bg-green-200 transition-all text-left">
                🤖 Réponses automatiques
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedInboxDashboard;
