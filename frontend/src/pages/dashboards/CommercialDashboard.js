import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import {
  DollarSign, Users, Target, TrendingUp, Link as LinkIcon,
  Mail, Phone, Calendar, FileText, Lock, Crown, Zap,
  Copy, ExternalLink, Download, Eye, Edit, Trash2,
  Plus, Filter, Search, MessageCircle, Sparkles
} from 'lucide-react';
import api from '../../services/api';
import { toast } from 'react-toastify';

// =====================================================
// COMPOSANTS UTILITAIRES
// =====================================================

const Card = ({ title, icon, children, className = '', locked = false }) => (
  <div className={`bg-white rounded-lg shadow-sm p-6 relative ${className}`}>
    {locked && (
      <div className="absolute inset-0 bg-gray-900 bg-opacity-50 backdrop-blur-sm rounded-lg flex items-center justify-center z-10">
        <div className="text-center text-white">
          <Lock size={48} className="mx-auto mb-3" />
          <p className="font-bold text-lg">Fonctionnalité Premium</p>
          <button className="mt-3 bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg font-semibold transition">
            Débloquer
          </button>
        </div>
      </div>
    )}
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      {icon && <div className="text-gray-400">{icon}</div>}
    </div>
    {children}
  </div>
);

const StatCard = ({ title, value, icon, trend, trendValue, delay = 0, isCurrency = false, suffix = '' }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    className="bg-white rounded-lg shadow-sm p-6"
  >
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <p className="text-sm text-gray-600 mb-1">{title}</p>
        <div className="text-2xl font-bold text-gray-800">
          {typeof value === 'number' ? (
            <CountUp
              end={value}
              duration={2.5}
              decimals={isCurrency ? 2 : 0}
              separator=" "
              suffix={suffix}
              prefix={isCurrency ? '' : ''}
            />
          ) : (
            value
          )}
          {isCurrency && ' €'}
        </div>
        {trend && (
          <div className={`flex items-center mt-2 text-sm ${trendValue >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            <TrendingUp size={16} className="mr-1" />
            <span>{trendValue >= 0 ? '+' : ''}{trendValue}%</span>
            <span className="text-gray-500 ml-2">vs mois dernier</span>
          </div>
        )}
      </div>
      <div className="ml-4">{icon}</div>
    </div>
  </motion.div>
);

// =====================================================
// BANDEAU ABONNEMENT
// =====================================================

const SubscriptionBanner = ({ tier, stats }) => {
  const config = {
    starter: {
      color: 'from-orange-500 to-pink-500',
      icon: '🌱',
      title: 'STARTER',
      message: `Vous avez utilisé ${stats?.leads_generated_month || 0}/10 leads ce mois`,
      cta: '🚀 Passer à PRO - 29€/mois',
      benefits: ['10 leads/mois', '3 liens trackés', '3 templates']
    },
    pro: {
      color: 'from-purple-600 to-blue-600',
      icon: '⚡',
      title: 'PRO',
      message: 'Tous les outils professionnels débloqués',
      benefits: ['Leads illimités', 'CRM avancé', '15 templates', 'Kit marketing']
    },
    enterprise: {
      color: 'from-yellow-500 to-amber-600',
      icon: '👑',
      title: 'ENTERPRISE',
      message: 'Accès Total + IA + Automation',
      benefits: ['Tout illimité', 'IA suggestions', 'Automation complète', 'Support dédié']
    }
  };

  const currentConfig = config[tier] || config.starter;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className={`bg-gradient-to-r ${currentConfig.color} rounded-xl p-6 mb-6 shadow-lg`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <span className="text-3xl mr-3">{currentConfig.icon}</span>
            <h2 className="text-2xl font-bold text-white">Abonnement {currentConfig.title}</h2>
          </div>
          <p className="text-white text-lg mb-3">{currentConfig.message}</p>
          <div className="flex flex-wrap gap-2">
            {currentConfig.benefits.map((benefit, idx) => (
              <span key={idx} className="bg-white bg-opacity-20 text-white px-3 py-1 rounded-full text-sm">
                ✓ {benefit}
              </span>
            ))}
          </div>
        </div>
        {tier === 'starter' && (
          <button className="bg-white text-orange-600 hover:bg-gray-100 px-8 py-3 rounded-lg font-bold text-lg transition transform hover:scale-105 shadow-lg">
            {currentConfig.cta}
          </button>
        )}
      </div>
    </motion.div>
  );
};

// =====================================================
// COMPOSANT PRINCIPAL
// =====================================================

const CommercialDashboard = () => {
  // États
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [trackingLinks, setTrackingLinks] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [funnelData, setFunnelData] = useState([]);
  const [subscriptionTier, setSubscriptionTier] = useState('starter');
  
  // Modals
  const [showCreateLead, setShowCreateLead] = useState(false);
  const [showCreateLink, setShowCreateLink] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  // =====================================================
  // CHARGEMENT DES DONNÉES
  // =====================================================

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Récupérer le profil utilisateur pour le tier
      const userProfile = JSON.parse(localStorage.getItem('user') || '{}');
      setSubscriptionTier(userProfile.subscription_tier || 'starter');

      // Récupérer les stats
      const statsRes = await api.get('/api/commercial/stats');
      setStats(statsRes.data);

      // Récupérer les leads
      const leadsRes = await api.get('/api/commercial/leads?limit=20');
      setLeads(leadsRes.data);

      // Récupérer les liens trackés
      const linksRes = await api.get('/api/commercial/tracking-links');
      setTrackingLinks(linksRes.data);

      // Récupérer les templates
      const templatesRes = await api.get('/api/commercial/templates');
      setTemplates(templatesRes.data);

      // Récupérer les données de performance
      const perfRes = await api.get('/api/commercial/analytics/performance?period=30');
      setPerformanceData(perfRes.data.data || []);

      // Récupérer le funnel
      const funnelRes = await api.get('/api/commercial/analytics/funnel');
      setFunnelData([
        { name: 'Nouveaux', value: funnelRes.data.nouveau.count, amount: funnelRes.data.nouveau.value },
        { name: 'Qualifiés', value: funnelRes.data.qualifie.count, amount: funnelRes.data.qualifie.value },
        { name: 'En Négociation', value: funnelRes.data.en_negociation.count, amount: funnelRes.data.en_negociation.value },
        { name: 'Conclus', value: funnelRes.data.conclu.count, amount: funnelRes.data.conclu.value }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement données:', error);
      toast.error('Erreur lors du chargement des données');
      setLoading(false);
    }
  };

  // =====================================================
  // HANDLERS
  // =====================================================

  const handleCreateLead = async (leadData) => {
    try {
      await api.post('/api/commercial/leads', leadData);
      toast.success('Lead créé avec succès !');
      fetchAllData();
      setShowCreateLead(false);
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error('Limite atteinte ! Passez à PRO pour leads illimités.');
      } else {
        toast.error('Erreur lors de la création du lead');
      }
    }
  };

  const handleCreateLink = async (linkData) => {
    try {
      const response = await api.post('/api/commercial/tracking-links', linkData);
      toast.success('Lien tracké créé !');
      toast.info(`Code: ${response.data.link_code}`);
      fetchAllData();
      setShowCreateLink(false);
    } catch (error) {
      if (error.response?.status === 403) {
        toast.error('Limite de 3 liens atteinte ! Passez à PRO.');
      } else {
        toast.error('Erreur lors de la création du lien');
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copié dans le presse-papier !');
  };

  // =====================================================
  // LOADING STATE
  // =====================================================

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du dashboard...</p>
        </div>
      </div>
    );
  }

  // =====================================================
  // RENDER
  // =====================================================

  const isStarter = subscriptionTier === 'starter';
  const isPro = subscriptionTier === 'pro';
  const isEnterprise = subscriptionTier === 'enterprise';

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Bandeau Abonnement */}
      <SubscriptionBanner tier={subscriptionTier} stats={stats} />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Leads Total"
          value={stats?.total_leads || 0}
          icon={<Users className="text-blue-600" size={32} />}
          delay={0}
        />
        <StatCard
          title="Commission Gagnée"
          value={stats?.total_commission || 0}
          icon={<DollarSign className="text-green-600" size={32} />}
          isCurrency
          delay={0.1}
        />
        <StatCard
          title="Pipeline Valeur"
          value={stats?.pipeline_value || 0}
          icon={<Target className="text-purple-600" size={32} />}
          isCurrency
          delay={0.2}
        />
        <StatCard
          title="Taux de Conversion"
          value={stats?.conversion_rate || 0}
          icon={<TrendingUp className="text-orange-600" size={32} />}
          suffix="%"
          delay={0.3}
        />
      </div>

      {/* Actions Rapides */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-white rounded-lg shadow-sm p-6 mb-6"
      >
        <h3 className="text-lg font-semibold text-gray-800 mb-4">🚀 Actions Rapides</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => setShowCreateLead(true)}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition"
          >
            <Plus className="text-purple-600 mb-2" size={24} />
            <span className="text-sm font-medium">Ajouter Lead</span>
          </button>
          
          <button
            onClick={() => setShowCreateLink(true)}
            disabled={isStarter && trackingLinks.length >= 3}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <LinkIcon className="text-blue-600 mb-2" size={24} />
            <span className="text-sm font-medium">Créer Lien Tracké</span>
            {isStarter && <span className="text-xs text-red-600 mt-1">{trackingLinks.length}/3</span>}
          </button>
          
          <button
            onClick={() => setShowTemplates(true)}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition"
          >
            <FileText className="text-green-600 mb-2" size={24} />
            <span className="text-sm font-medium">Templates</span>
            <span className="text-xs text-gray-500 mt-1">{templates.length} disponibles</span>
          </button>
          
          <button
            disabled={!isEnterprise}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition disabled:opacity-50 disabled:cursor-not-allowed relative"
          >
            {!isEnterprise && <Lock className="absolute top-2 right-2 text-gray-400" size={16} />}
            <Sparkles className="text-yellow-600 mb-2" size={24} />
            <span className="text-sm font-medium">Générateur Devis</span>
            {!isEnterprise && <span className="text-xs text-orange-600 mt-1">ENTERPRISE</span>}
          </button>
        </div>
      </motion.div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <Card 
            title={`Performance ${isStarter ? '(7 derniers jours)' : '(30 derniers jours)'}`}
            icon={<TrendingUp size={20} />}
          >
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData.slice(isStarter ? -7 : -30)}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" stroke="#9ca3af" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#8b5cf6"
                  strokeWidth={3}
                  dot={{ fill: '#8b5cf6', r: 4 }}
                  activeDot={{ r: 6 }}
                  fill="url(#colorRevenue)"
                  name="Revenue (€)"
                />
                <Line
                  type="monotone"
                  dataKey="leads"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={{ fill: '#3b82f6', r: 4 }}
                  activeDot={{ r: 6 }}
                  fill="url(#colorLeads)"
                  name="Leads"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>

        {/* Funnel Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Card title="Pipeline de Conversion" icon={<Target size={20} />} locked={isStarter && !isPro && !isEnterprise}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={funnelData} layout="vertical">
                <defs>
                  <linearGradient id="colorFunnel" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.9}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.6}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" stroke="#9ca3af" />
                <YAxis type="category" dataKey="name" stroke="#9ca3af" width={120} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                  formatter={(value, name, props) => [
                    `${value} leads (${props.payload.amount?.toLocaleString()}€)`,
                    'Leads'
                  ]}
                />
                <Bar dataKey="value" fill="url(#colorFunnel)" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </motion.div>
      </div>

      {/* Liens Trackés */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.7 }}
        className="mb-6"
      >
        <Card title="🔗 Mes Liens Trackés" icon={<LinkIcon size={20} />}>
          {trackingLinks.length === 0 ? (
            <div className="text-center py-8">
              <LinkIcon size={48} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">Aucun lien tracké pour le moment</p>
              <button
                onClick={() => setShowCreateLink(true)}
                className="mt-4 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition"
              >
                Créer mon premier lien
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Produit</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Canal</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Clics</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversions</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trackingLinks.map((link) => (
                    <tr key={link.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-800">{link.product_name}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                          {link.channel}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-800">{link.total_clicks}</td>
                      <td className="px-4 py-3 text-sm text-gray-800">{link.total_conversions}</td>
                      <td className="px-4 py-3 text-sm font-semibold text-green-600">
                        {link.total_revenue?.toLocaleString()} €
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <button
                          onClick={() => copyToClipboard(link.full_url)}
                          className="text-purple-600 hover:text-purple-800 mr-2"
                          title="Copier le lien"
                        >
                          <Copy size={16} />
                        </button>
                        <a
                          href={link.full_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800"
                          title="Ouvrir"
                        >
                          <ExternalLink size={16} />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </motion.div>

      {/* CRM Leads - Visible pour PRO et ENTERPRISE */}
      {(isPro || isEnterprise) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <Card title="👥 Mes Leads CRM" icon={<Users size={20} />}>
            {leads.length === 0 ? (
              <div className="text-center py-8">
                <Users size={48} className="mx-auto text-gray-300 mb-3" />
                <p className="text-gray-500">Aucun lead pour le moment</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entreprise</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Température</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valeur</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leads.slice(0, 10).map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-sm font-medium text-gray-800">
                              {lead.first_name} {lead.last_name}
                            </p>
                            <p className="text-xs text-gray-500">{lead.email}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-800">{lead.company || '-'}</td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            lead.status === 'conclu' ? 'bg-green-100 text-green-800' :
                            lead.status === 'en_negociation' ? 'bg-yellow-100 text-yellow-800' :
                            lead.status === 'qualifie' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {lead.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            lead.temperature === 'chaud' ? 'bg-red-100 text-red-800' :
                            lead.temperature === 'tiede' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {lead.temperature === 'chaud' ? '🔥' : lead.temperature === 'tiede' ? '☀️' : '❄️'}
                            {' '}{lead.temperature}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm font-semibold text-gray-800">
                          {lead.estimated_value?.toLocaleString() || 0} €
                        </td>
                        <td className="px-4 py-3">
                          <button className="text-blue-600 hover:text-blue-800 mr-2" title="Voir">
                            <Eye size={16} />
                          </button>
                          <button className="text-green-600 hover:text-green-800 mr-2" title="Éditer">
                            <Edit size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </motion.div>
      )}

      {/* CRM Verrouillé pour STARTER */}
      {isStarter && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <Card title="👥 CRM Leads Avancé" locked={true}>
            <div className="h-64"></div>
          </Card>
        </motion.div>
      )}

      {/* Modal Templates */}
      {showTemplates && (
        <TemplatesModal
          templates={templates}
          onClose={() => setShowTemplates(false)}
          tier={subscriptionTier}
        />
      )}

      {/* Modal Create Lead */}
      {showCreateLead && (
        <CreateLeadModal
          onClose={() => setShowCreateLead(false)}
          onSubmit={handleCreateLead}
        />
      )}

      {/* Modal Create Link */}
      {showCreateLink && (
        <CreateLinkModal
          onClose={() => setShowCreateLink(false)}
          onSubmit={handleCreateLink}
        />
      )}
    </div>
  );
}

// =====================================================
// MODALS
// =====================================================

const TemplatesModal = ({ templates, onClose, tier }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
    >
      <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">📝 Templates Marketing</h2>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-800">
          ✕
        </button>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((template) => (
            <div key={template.id} className="border rounded-lg p-4 hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-800">{template.title}</h3>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                  {template.category}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3 whitespace-pre-wrap">{template.content.substring(0, 150)}...</p>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(template.content);
                  toast.success('Template copié !');
                }}
                className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition"
              >
                <Copy size={16} className="inline mr-2" />
                Copier le template
              </button>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  </div>
);

const CreateLeadModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company: '',
    status: 'nouveau',
    temperature: 'froid',
    source: 'linkedin',
    estimated_value: 0,
    notes: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">➕ Nouveau Lead</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Prénom *</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom *</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Téléphone</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Entreprise</label>
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({...formData, company: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Source</label>
              <select
                value={formData.source}
                onChange={(e) => setFormData({...formData, source: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              >
                <option value="linkedin">LinkedIn</option>
                <option value="email">Email</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="referral">Référence</option>
                <option value="event">Événement</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Température</label>
              <select
                value={formData.temperature}
                onChange={(e) => setFormData({...formData, temperature: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              >
                <option value="froid">❄️ Froid</option>
                <option value="tiede">☀️ Tiède</option>
                <option value="chaud">🔥 Chaud</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Valeur Estimée (€)</label>
              <input
                type="number"
                value={formData.estimated_value}
                onChange={(e) => setFormData({...formData, estimated_value: parseFloat(e.target.value)})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Annuler
            </button>
            <button type="submit" className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              Créer Lead
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

const CreateLinkModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    product_id: '',
    channel: 'whatsapp',
    campaign_name: ''
  });

  const [products, setProducts] = useState([]);

  useEffect(() => {
    // Charger les produits
    api.get('/api/marketplace/products?limit=50').then(res => {
      setProducts(res.data.products || []);
    });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-md w-full"
      >
        <div className="bg-white border-b p-6 flex justify-between items-center rounded-t-xl">
          <h2 className="text-2xl font-bold text-gray-800">🔗 Créer Lien Tracké</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Produit *</label>
              <select
                required
                value={formData.product_id}
                onChange={(e) => setFormData({...formData, product_id: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Sélectionner un produit</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Canal *</label>
              <select
                value={formData.channel}
                onChange={(e) => setFormData({...formData, channel: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              >
                <option value="whatsapp">WhatsApp</option>
                <option value="linkedin">LinkedIn</option>
                <option value="facebook">Facebook</option>
                <option value="email">Email</option>
                <option value="sms">SMS</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom de Campagne</label>
              <input
                type="text"
                value={formData.campaign_name}
                onChange={(e) => setFormData({...formData, campaign_name: e.target.value})}
                placeholder="Ex: Promo Black Friday"
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              Annuler
            </button>
            <button type="submit" className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              Créer Lien
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default CommercialDashboard;
