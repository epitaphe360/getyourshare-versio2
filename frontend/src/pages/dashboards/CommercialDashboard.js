import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  DollarSign, Users, Target, TrendingUp, Link as LinkIcon,
  Mail, Phone, Calendar, FileText, Lock, Crown,
  Copy, ExternalLink, Eye, Edit,
  Plus, ShoppingCart, Sparkles
} from 'lucide-react';
import api from '../../utils/api';
import { toast } from 'react-toastify';

// Import des utilitaires
import { checkAccess, getPlanLimits, getPlanBadge } from '../../utils/subscriptionUtils';
import { exportToCSV, exportToPDF } from '../../utils/exportUtils';

// Import des composants
import DashboardCard from '../../components/dashboard/DashboardCard';
import StatCard from '../../components/dashboard/StatCard';
import SubscriptionBanner from '../../components/dashboard/SubscriptionBanner';
import DashboardSkeleton from '../../components/dashboard/DashboardSkeleton';
import AdvancedFilters from '../../components/dashboard/AdvancedFilters';
import PeriodComparison from '../../components/dashboard/PeriodComparison';
import TemplatesModal from '../../components/dashboard/modals/TemplatesModal';
import CreateLeadModal from '../../components/dashboard/modals/CreateLeadModal';
import CreateLinkModal from '../../components/dashboard/modals/CreateLinkModal';
import NotificationCenter from '../../components/NotificationCenter';

// PHASE 2: Outils de Communication
import CalendarIntegration from '../../components/dashboard/CalendarIntegration';
import EmailTracker from '../../components/dashboard/EmailTracker';
import ClickToCall from '../../components/dashboard/ClickToCall';

// PHASE 3: Intelligence IA
import LeadScoring from '../../components/dashboard/LeadScoring';
import AISuggestions from '../../components/dashboard/AISuggestions';
import AIForecasting from '../../components/dashboard/AIForecasting';

// PHASE 4: Dashboards Spécialisés
import SpecializedDashboards from '../../components/dashboard/SpecializedDashboards';

const CommercialDashboard = () => {
  const navigate = useNavigate();
  
  // États
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [leads, setLeads] = useState([]);
  const [trackingLinks, setTrackingLinks] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [funnelData, setFunnelData] = useState([]);
  const [subscriptionTier, setSubscriptionTier] = useState('starter');
  
  // Nouveaux états pour fonctionnalités critiques
  const [pipeline, setPipeline] = useState(null);
  const [quota, setQuota] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [hotLead, setHotLead] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  
  // Modals
  const [showCreateLead, setShowCreateLead] = useState(false);
  const [showCreateLink, setShowCreateLink] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);

  // Nouvelles fonctionnalités
  const [showComparison, setShowComparison] = useState(false);
  const [filteredLeads, setFilteredLeads] = useState([]);
  const [userId, setUserId] = useState(null);
  
  // PHASE 3: Lead sélectionné pour suggestions IA
  const [selectedLeadForAI, setSelectedLeadForAI] = useState(null);

  // =====================================================
  // CHARGEMENT DES DONNÉES
  // =====================================================

  useEffect(() => {
    fetchAllData();
    // Récupérer l'ID utilisateur depuis localStorage ou API
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setUserId(user.id || 'unknown');
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Utiliser Promise.allSettled pour robustesse
      const results = await Promise.allSettled([
        api.get('/api/subscriptions/current'),
        api.get('/api/commercial/stats'),
        api.get('/api/commercial/leads?limit=20'),
        api.get('/api/commercial/tracking-links'),
        api.get('/api/commercial/templates'),
        api.get('/api/commercial/analytics/performance?period=30'),
        api.get('/api/commercial/analytics/funnel'),
        api.get('/api/commercial/pipeline'),
        api.get('/api/commercial/quota'),
        api.get('/api/commercial/tasks'),
        api.get('/api/commercial/hot-lead'),
        api.get('/api/commercial/leaderboard')
      ]);

      const [subscriptionRes, statsRes, leadsRes, linksRes, templatesRes, perfRes, funnelRes, pipelineRes, quotaRes, tasksRes, hotLeadRes, leaderboardRes] = results;

      // Récupérer le tier depuis l'API (plus fiable que localStorage)
      if (subscriptionRes.status === 'fulfilled') {
        const planName = subscriptionRes.value.data?.plan_name?.toLowerCase() || 'starter';
        setSubscriptionTier(planName);
      } else {
        // Fallback sur localStorage
        const userProfile = JSON.parse(localStorage.getItem('user') || '{}');
        setSubscriptionTier(userProfile.subscription_tier || 'starter');
      }

      // Stats
      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      } else {
        setStats({ total_leads: 0, total_commission: 0, pipeline_value: 0, conversion_rate: 0, leads_generated_month: 0 });
      }

      // Leads
      if (leadsRes.status === 'fulfilled') {
        setLeads(Array.isArray(leadsRes.value.data) ? leadsRes.value.data : leadsRes.value.data?.leads || []);
      } else {
        setLeads([]);
      }

      // Tracking Links
      if (linksRes.status === 'fulfilled') {
        setTrackingLinks(Array.isArray(linksRes.value.data) ? linksRes.value.data : linksRes.value.data?.links || []);
      } else {
        setTrackingLinks([]);
      }

      // Templates
      if (templatesRes.status === 'fulfilled') {
        setTemplates(Array.isArray(templatesRes.value.data) ? templatesRes.value.data : templatesRes.value.data?.templates || []);
      } else {
        setTemplates([]);
      }

      // Performance Data
      if (perfRes.status === 'fulfilled') {
        setPerformanceData(perfRes.value.data?.data || []);
      } else {
        setPerformanceData([]);
      }

      // Funnel Data
      if (funnelRes.status === 'fulfilled' && funnelRes.value.data) {
        const funnel = funnelRes.value.data;
        setFunnelData([
          { name: 'Nouveaux', value: funnel.nouveau?.count || 0, amount: funnel.nouveau?.value || 0 },
          { name: 'Qualifiés', value: funnel.qualifie?.count || 0, amount: funnel.qualifie?.value || 0 },
          { name: 'En Négociation', value: funnel.en_negociation?.count || 0, amount: funnel.en_negociation?.value || 0 },
          { name: 'Conclus', value: funnel.conclu?.count || 0, amount: funnel.conclu?.value || 0 }
        ]);
      } else {
        setFunnelData([
          { name: 'Nouveaux', value: 0, amount: 0 },
          { name: 'Qualifiés', value: 0, amount: 0 },
          { name: 'En Négociation', value: 0, amount: 0 },
          { name: 'Conclus', value: 0, amount: 0 }
        ]);
      }

      // Pipeline
      if (pipelineRes.status === 'fulfilled') {
        setPipeline(pipelineRes.value.data);
      } else {
        setPipeline({ new: 0, contacted: 0, qualified: 0, proposal: 0, negotiation: 0, won: 0, conversion_rate: 0 });
      }

      // Quota
      if (quotaRes.status === 'fulfilled') {
        setQuota(quotaRes.value.data);
      } else {
        const today = new Date();
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        const daysRemaining = Math.ceil((lastDay - today) / (1000 * 60 * 60 * 24));
        setQuota({ 
          current: 0, 
          target: 10000, 
          progress: 0, 
          remaining: 10000, 
          days_remaining: daysRemaining,
          on_track: false 
        });
      }

      // Tasks
      if (tasksRes.status === 'fulfilled') {
        setTasks(tasksRes.value.data?.tasks || []);
      } else {
        setTasks([]);
      }

      // Hot Lead
      if (hotLeadRes.status === 'fulfilled') {
        setHotLead(hotLeadRes.value.data?.lead || null);
      }

      // Leaderboard
      if (leaderboardRes.status === 'fulfilled') {
        setLeaderboard(leaderboardRes.value.data?.rankings || []);
      } else {
        setLeaderboard([]);
      }

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

  const handleCompleteTask = async (taskId) => {
    try {
      await api.patch(`/api/commercial/tasks/${taskId}/complete`);
      toast.success('Tâche marquée comme complétée !');
      // Rafraîchir les tâches
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors de la mise à jour de la tâche');
    }
  };

  // =====================================================
  // MEMOIZED VALUES
  // =====================================================

  const planBadge = useMemo(() => getPlanBadge(subscriptionTier), [subscriptionTier]);
  const planLimits = useMemo(() => getPlanLimits(subscriptionTier), [subscriptionTier]);
  const isStarter = subscriptionTier === 'starter';
  const isPro = subscriptionTier === 'pro';
  const isEnterprise = subscriptionTier === 'enterprise';

  // Fonction pour gérer les fonctionnalités verrouillées
  const handleLockedFeature = (featureName) => {
    toast.info(`🔒 ${featureName} nécessite un abonnement supérieur`);
    navigate('/pricing');
  };

  // =====================================================
  // RENDER
  // =====================================================

  if (loading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header avec Badge Plan */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 mb-6 text-white"
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard Commercial</h1>
            <p className="text-purple-100">Gérez vos leads et maximisez vos commissions</p>
          </div>
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg border-2 ${planBadge.color} font-bold text-lg`}>
              {planBadge.icon} {planBadge.name}
            </div>
            <div className="text-right">
              <div className="text-sm text-purple-100">Commission</div>
              <div className="text-2xl font-bold">{planLimits.commission}%</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Navigation Bar */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex flex-wrap gap-3 items-center justify-between">
          <div className="flex flex-wrap gap-3 items-center">
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition flex items-center gap-2 font-medium"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Accueil
            </button>
            <button
              onClick={() => setShowCreateLead(true)}
              className="px-4 py-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition flex items-center gap-2 font-medium"
            >
              <Plus size={18} />
              Nouveau Lead
            </button>
            <button
              onClick={() => navigate('/dashboard/marketplace')}
              className="px-4 py-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition flex items-center gap-2 font-medium"
            >
              <ShoppingCart size={18} />
              Marketplace
            </button>
            <button
              onClick={() => navigate('/features')}
              className="px-4 py-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition flex items-center gap-2 font-medium"
            >
              <Sparkles size={18} />
              Features
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="px-4 py-2 text-gray-700 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition flex items-center gap-2 font-medium"
            >
              <Users size={18} />
              Profil
            </button>
          </div>
          
          {/* Notifications et Actions Rapides */}
          <div className="flex items-center gap-2">
            {userId && <NotificationCenter userId={userId} />}
            <button
              onClick={() => setShowComparison(!showComparison)}
              className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition flex items-center gap-2 font-medium"
              title="Comparer les périodes"
            >
              📊 Comparer
            </button>
          </div>
        </div>
      </div>

      {/* Bandeau Abonnement */}
      <SubscriptionBanner tier={subscriptionTier} stats={stats} />

      {/* Filtres Avancés & Recherche */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.15 }}
      >
        <AdvancedFilters 
          data={leads} 
          onFilter={setFilteredLeads}
          onExport={(data) => {
            const format = window.confirm('PDF? OK = PDF, Cancel = CSV');
            if (format) {
              exportToPDF(data, `leads_${new Date().toLocaleDateString()}.pdf`);
            } else {
              exportToCSV(data, `leads_${new Date().toLocaleDateString()}.csv`);
            }
          }}
          filterableFields={{
            search: ['first_name', 'last_name', 'email', 'company'],
            status: ['nouveau', 'qualifie', 'en_negociation', 'conclu'],
            temperature: ['froid', 'tiede', 'chaud'],
            minValue: 0,
            maxValue: 1000000
          }}
        />
      </motion.div>

      {/* Comparaison Périodes */}
      {showComparison && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-lg shadow-sm p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">📊 Analyse Comparative</h2>
            <button
              onClick={() => setShowComparison(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          <PeriodComparison 
            data={performanceData.length > 0 ? performanceData : []} 
            currentPeriod="month"
          />
        </motion.div>
      )}

      {/* Quota Tracker - NOUVEAU */}
      {quota && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-500 rounded-lg">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  🎯 Objectif du Mois
                </h3>
                <p className="text-sm text-gray-600">
                  {quota.days_remaining} jours restants
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(quota.progress || 0)}%
              </p>
              <p className="text-sm text-gray-600">
                {quota.current?.toLocaleString() || 0}€ / {quota.target?.toLocaleString() || 10000}€
              </p>
            </div>
          </div>
          
          <div className="relative pt-1">
            <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-green-100">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(quota.progress || 0, 100)}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${
                  (quota.progress || 0) >= 100 ? 'bg-green-500' :
                  (quota.progress || 0) >= 75 ? 'bg-blue-500' :
                  (quota.progress || 0) >= 50 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
              />
            </div>
          </div>
          
          {(quota.progress || 0) >= 100 ? (
            <p className="text-sm text-green-700 font-medium">
              ✨ Félicitations! Vous avez dépassé votre objectif de {Math.round((quota.progress || 0) - 100)}%!
            </p>
          ) : (
            <p className="text-sm text-gray-700">
              Il vous reste <span className="font-semibold">{quota.remaining?.toLocaleString() || 0}€</span> à générer
              {quota.on_track ? (
                <span className="text-green-600 ml-2">✓ Vous êtes en avance!</span>
              ) : (
                <span className="text-orange-600 ml-2">⚠️ Accélérez le rythme</span>
              )}
            </p>
          )}
        </motion.div>
      )}

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
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">🚀 Actions Rapides</h3>
          <div className="text-sm text-gray-500">
            Leads: {stats?.total_leads || 0}/{planLimits.leads} • 
            Liens: {trackingLinks.length}/{planLimits.links}
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => setShowCreateLead(true)}
            disabled={stats?.total_leads >= planLimits.leads}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="text-purple-600 mb-2" size={24} />
            <span className="text-sm font-medium">Ajouter Lead</span>
            {stats?.total_leads >= planLimits.leads && (
              <span className="text-xs text-red-600 mt-1">Limite atteinte</span>
            )}
          </button>
          
          <button
            onClick={() => {
              if (trackingLinks.length >= planLimits.links && !checkAccess('unlimited_links', subscriptionTier)) {
                handleLockedFeature('Liens illimités');
              } else {
                setShowCreateLink(true);
              }
            }}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition relative"
          >
            {trackingLinks.length >= planLimits.links && !checkAccess('unlimited_links', subscriptionTier) && (
              <Lock className="absolute top-2 right-2 text-gray-400" size={16} />
            )}
            <LinkIcon className="text-blue-600 mb-2" size={24} />
            <span className="text-sm font-medium">Créer Lien Tracké</span>
            <span className="text-xs text-gray-500 mt-1">{trackingLinks.length}/{planLimits.links}</span>
          </button>
          
          <button
            onClick={() => {
              if (templates.length >= planLimits.templates && !checkAccess('unlimited_templates', subscriptionTier)) {
                handleLockedFeature('Templates illimités');
              } else {
                setShowTemplates(true);
              }
            }}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition relative"
          >
            {!checkAccess('unlimited_templates', subscriptionTier) && templates.length >= planLimits.templates && (
              <Lock className="absolute top-2 right-2 text-gray-400" size={16} />
            )}
            <FileText className="text-green-600 mb-2" size={24} />
            <span className="text-sm font-medium">Templates</span>
            <span className="text-xs text-gray-500 mt-1">{templates.length} disponibles</span>
          </button>
          
          <button
            onClick={() => {
              if (!checkAccess('ai_generator', subscriptionTier)) {
                handleLockedFeature('Générateur IA');
              } else {
                // Logique du générateur
              }
            }}
            className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition relative"
          >
            {!checkAccess('ai_generator', subscriptionTier) && (
              <Lock className="absolute top-2 right-2 text-gray-400" size={16} />
            )}
            <Sparkles className="text-yellow-600 mb-2" size={24} />
            <span className="text-sm font-medium">Générateur Devis IA</span>
            {!checkAccess('ai_generator', subscriptionTier) && (
              <span className="text-xs text-orange-600 mt-1">ENTERPRISE</span>
            )}
          </button>
        </div>
      </motion.div>

      {/* Tâches & Rappels - NOUVEAU */}
      {tasks && tasks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              📋 Mes Prochaines Tâches
            </h3>
            <button 
              onClick={() => navigate('/tasks')}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Voir tout →
            </button>
          </div>
          
          <div className="space-y-3">
            {tasks.slice(0, 5).map((task, index) => (
              <motion.div
                key={task.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center justify-between p-4 rounded-lg border ${
                  task.priority === 'high' 
                    ? 'border-red-200 bg-red-50' 
                    : task.priority === 'medium'
                    ? 'border-yellow-200 bg-yellow-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3 flex-1">
                  {task.type === 'call' && <Phone className="w-4 h-4 text-gray-600" />}
                  {task.type === 'email' && <Mail className="w-4 h-4 text-gray-600" />}
                  {task.type === 'meeting' && <Calendar className="w-4 h-4 text-gray-600" />}
                  
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{task.title}</p>
                    {task.description && <p className="text-xs text-gray-600">{task.description}</p>}
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    task.priority === 'high' 
                      ? 'bg-red-100 text-red-700' 
                      : task.priority === 'medium'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {task.due_date}
                  </span>
                  
                  <button
                    onClick={() => handleCompleteTask(task.id)}
                    className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                    title="Marquer comme terminé"
                  >
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Lead Chaud de la Semaine - NOUVEAU */}
      {hotLead && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl shadow-sm border border-orange-200 p-6 mb-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            🔥 Lead Chaud de la Semaine
          </h3>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-red-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {hotLead.company?.charAt(0) || 'L'}
              </div>
              
              <div>
                <h4 className="text-xl font-bold text-gray-900">{hotLead.company}</h4>
                <p className="text-sm text-gray-600">{hotLead.contact_name}</p>
                <p className="text-sm text-gray-500">{hotLead.contact_email}</p>
                
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                    💰 Budget: {hotLead.estimated_value?.toLocaleString() || 0}€
                  </span>
                  <span className="px-3 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                    🔥 Très intéressé
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col gap-2">
              <button
                onClick={() => navigate(`/leads/${hotLead.id}`)}
                className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg font-medium hover:from-orange-600 hover:to-red-600 transition-all"
              >
                📞 Contacter Maintenant
              </button>
              <p className="text-xs text-center text-gray-600">
                Dernière interaction: {hotLead.last_contact || 'Jamais'}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Pipeline de Vente - NOUVEAU */}
      {pipeline && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-600" />
            🎯 Pipeline de Vente
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            {[
              { stage: 'Nouveau', count: pipeline.new || 0, amount: pipeline.new_amount || 0, color: 'blue' },
              { stage: 'Contacté', count: pipeline.contacted || 0, amount: pipeline.contacted_amount || 0, color: 'indigo' },
              { stage: 'Qualifié', count: pipeline.qualified || 0, amount: pipeline.qualified_amount || 0, color: 'purple' },
              { stage: 'Proposition', count: pipeline.proposal || 0, amount: pipeline.proposal_amount || 0, color: 'pink' },
              { stage: 'Négociation', count: pipeline.negotiation || 0, amount: pipeline.negotiation_amount || 0, color: 'orange' },
              { stage: 'Gagné', count: pipeline.won || 0, amount: pipeline.won_amount || 0, color: 'green' }
            ].map((stage, index) => (
              <motion.div
                key={stage.stage}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`bg-${stage.color}-50 border border-${stage.color}-200 rounded-lg p-4 hover:shadow-md transition-all cursor-pointer`}
                onClick={() => navigate(`/leads?stage=${stage.stage.toLowerCase()}`)}
              >
                <div className="text-center">
                  <p className="text-xs font-medium text-gray-600 mb-2">{stage.stage}</p>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{stage.count}</p>
                  <p className="text-sm text-gray-600">{stage.amount.toLocaleString()}€</p>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Taux de Conversion Global</span>
              <span className="text-lg font-bold text-green-600">
                {pipeline.conversion_rate || 0}%
              </span>
            </div>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-green-600"
                style={{ width: `${pipeline.conversion_rate || 0}%` }}
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Leaderboard - NOUVEAU */}
      {leaderboard && leaderboard.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Crown className="w-5 h-5 text-yellow-500" />
              🏆 Top Commerciaux ce Mois
            </h3>
          </div>
          
          <div className="space-y-3">
            {leaderboard.slice(0, 5).map((rank, index) => (
              <motion.div
                key={rank.id || index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-center justify-between p-4 rounded-lg ${
                  rank.is_current_user 
                    ? 'bg-indigo-50 border-2 border-indigo-500' 
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-orange-600' :
                    'bg-gray-300'
                  }`}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                  </div>
                  
                  <div>
                    <p className="font-semibold text-gray-900">
                      {rank.name}
                      {rank.is_current_user && (
                        <span className="ml-2 text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                          Vous
                        </span>
                      )}
                    </p>
                    <p className="text-sm text-gray-600">{rank.leads_count || 0} leads générés</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">
                    {rank.revenue?.toLocaleString() || 0}€
                  </p>
                  {rank.position_change && rank.position_change !== 0 && (
                    <p className={`text-sm flex items-center gap-1 justify-end ${
                      rank.position_change > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {rank.position_change > 0 ? (
                        <><TrendingUp className="w-4 h-4" /> +{rank.position_change}</>
                      ) : (
                        <><TrendingUp className="w-4 h-4 rotate-180" /> {rank.position_change}</>
                      )}
                    </p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Performance Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <DashboardCard 
            title={`Performance (${planLimits.analytics_days} derniers jours)`}
            icon={<TrendingUp size={20} />}
            locked={!checkAccess('advanced_analytics', subscriptionTier) && performanceData.length > 7}
            onUnlock={() => handleLockedFeature('Analytics Avancées')}
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
          </DashboardCard>
        </motion.div>

        {/* Funnel Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <DashboardCard title="Pipeline de Conversion" icon={<Target size={20} />} locked={isStarter && !isPro && !isEnterprise}>
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
          </DashboardCard>
        </motion.div>
      </div>

      {/* Liens Trackés */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.7 }}
        className="mb-6"
      >
        <DashboardCard title="🔗 Mes Liens Trackés" icon={<LinkIcon size={20} />}>
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
        </DashboardCard>
      </motion.div>

      {/* CRM Leads - Visible pour PRO et ENTERPRISE */}
      {(isPro || isEnterprise) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <DashboardCard 
            title="👥 Mes Leads CRM" 
            icon={<Users size={20} />}
            action={
              <button
                onClick={() => navigate('/commercial/leads')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium flex items-center gap-2"
              >
                <Users size={16} />
                Voir tous les leads
              </button>
            }
          >
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
                          <button 
                            onClick={() => {
                              toast.info(`Affichage du lead: ${lead.name}`);
                            }}
                            className="text-blue-600 hover:text-blue-800 mr-2" 
                            title="Voir"
                          >
                            <Eye size={16} />
                          </button>
                          <button 
                            onClick={() => {
                              toast.info(`Édition du lead: ${lead.name}`);
                            }}
                            className="text-green-600 hover:text-green-800 mr-2" 
                            title="Éditer"
                          >
                            <Edit size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </DashboardCard>
        </motion.div>
      )}

      {/* CRM Verrouillé pour STARTER */}
      {isStarter && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <DashboardCard title="👥 CRM Leads Avancé" locked={true}>
            <div className="h-64"></div>
          </DashboardCard>
        </motion.div>
      )}

      {/* ========== PHASE 2: OUTILS DE COMMUNICATION ========== */}
      
      {/* CALENDRIER INTÉGRÉ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.45 }}
      >
        <CalendarIntegration userId={userId} />
      </motion.div>

      {/* EMAIL TRACKER */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <EmailTracker userId={userId} leads={leads} />
      </motion.div>

      {/* CLICK-TO-CALL */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.55 }}
      >
        <ClickToCall userId={userId} leads={leads} />
      </motion.div>

      {/* ========== PHASE 3: INTELLIGENCE ARTIFICIELLE ========== */}

      {/* SCORING INTELLIGENT DES LEADS */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <LeadScoring 
          leads={leads} 
          onSelectLead={setSelectedLeadForAI}
        />
      </motion.div>

      {/* SUGGESTIONS IA */}
      {selectedLeadForAI && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.65 }}
        >
          <AISuggestions 
            lead={selectedLeadForAI} 
            leadHistory={leads}
          />
        </motion.div>
      )}

      {/* FORECASTING IA */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.7 }}
      >
        <AIForecasting 
          leads={leads} 
          historicalData={performanceData}
        />
      </motion.div>

      {/* ========== PHASE 4: DASHBOARDS SPÉCIALISÉS ========== */}

      {/* DASHBOARDS PAR RÔLE */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.75 }}
      >
        <SpecializedDashboards 
          leads={leads} 
          user={{id: userId, role: 'commercial'}}
        />
      </motion.div>

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

export default CommercialDashboard;
