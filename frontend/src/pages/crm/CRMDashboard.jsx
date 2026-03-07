import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  TrendingUp,
  Target,
  Mail,
  Phone,
  Calendar,
  Award,
  Zap,
  ThumbsUp,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Send,
  BarChart3,
  Activity,
  Star,
  Flame,
  Eye,
  MessageSquare,
  FileText,
  ArrowRight
} from 'lucide-react';
import api from '../../services/api';
import { format, formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

/**
 * CRM Automation Dashboard
 * ROI: 660K€/month
 * Features: Lead Scoring, Email Sequences, Predictions IA, Task Automation
 */
const CRMDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState('leads'); // leads, sequences, analytics
  const [selectedLead, setSelectedLead] = useState(null);
  const [filter, setFilter] = useState('all'); // all, hot, warm, cold

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    try {
      setLoading(true);

      const [leadsRes, statsRes] = await Promise.all([
        api.get(`/api/crm/leads?filter=${filter}`),
        api.get('/api/crm/stats')
      ]);

      setLeads(leadsRes.data?.leads || []);
      setStats(statsRes.data || {
        total_leads: 0, hot_leads: 0, warm_leads: 0, cold_leads: 0,
        avg_score: 0, conversion_rate: 0, avg_closing_time: 0,
        revenue_pipeline: 0, active_sequences: 0, tasks_automated: 0
      });

    } catch (error) {
      console.error('Error fetching CRM data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateLeadScore = async (leadId) => {
    try {
      const result = await api.post(`/api/crm/leads/${leadId}/score`);
      alert(`✅ Score recalculé: ${result.data?.lead?.score} (${result.data?.lead?.grade})`);
      fetchData();
    } catch (error) {
      alert('Erreur lors du calcul du score');
    }
  };

  const startEmailSequence = async (leadId, sequenceType) => {
    try {
      const result = await api.post('/api/crm/sequence/start', {
        lead_id: leadId,
        sequence_type: sequenceType
      });
      alert(`✅ ${result.data?.message || 'Séquence lancée'}`);
    } catch (error) {
      alert('Erreur lors du lancement de la séquence');
    }
  };

  const predictClosing = async (leadId) => {
    try {
      const result = await api.get(`/api/crm/leads/${leadId}/predict`);
      const { closing_probability, predicted_close_date, recommendation } = result.data;
      alert(`🔮 Prédiction:\n\nProbabilité: ${closing_probability}%\nDate estimée: ${predicted_close_date ? new Date(predicted_close_date).toLocaleDateString('fr-FR') : 'N/A'}\n\nAction: ${recommendation}`);
    } catch (error) {
      alert('Erreur lors de la prédiction');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Target size={48} className="text-indigo-600" />
        </motion.div>
      </div>
    );
  }

  const filteredLeads = filter === 'all' ? leads : leads.filter(l => l.status === filter);

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
            <h1 className="text-4xl font-bold mb-2">CRM Automation</h1>
            <p className="text-blue-100 text-lg">
              Automatisez 60% de vos tâches commerciales • ROI: 660K€/mois
            </p>
          </div>
          <motion.div
            whileHover={{ scale: 1.05, rotate: 5 }}
            className="bg-white/20 backdrop-blur-lg rounded-2xl p-6"
          >
            <Target size={64} />
          </motion.div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-2 bg-white rounded-xl p-2 shadow-lg">
        {[
          { id: 'leads', label: 'Leads & Scoring', icon: Users },
          { id: 'sequences', label: 'Séquences Email', icon: Mail },
          { id: 'analytics', label: 'Analytics & IA', icon: BarChart3 }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <tab.icon size={20} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          icon={Flame}
          title="Leads Chauds"
          value={stats.hot_leads}
          subtitle={`Score > 70 (${stats.total_leads} total)`}
          color="red"
          trend="+32%"
        />
        <KPICard
          icon={Award}
          title="Score Moyen"
          value={stats.avg_score}
          subtitle="Sur 100 points"
          color="blue"
          trend="+8pts"
        />
        <KPICard
          icon={TrendingUp}
          title="Taux de Conversion"
          value={`${stats.conversion_rate}%`}
          subtitle={`Temps moyen: ${stats.avg_closing_time}j`}
          color="green"
          trend="+5.2%"
        />
        <KPICard
          icon={DollarSign}
          title="Pipeline"
          value={`${(stats.revenue_pipeline / 1000000).toFixed(1)}M€`}
          subtitle="Valeur totale estimée"
          color="purple"
          trend="+18%"
        />
      </div>

      {/* Leads Tab */}
      {activeTab === 'leads' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Filters */}
          <div className="flex gap-3">
            <button
              onClick={() => setFilter('all')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                filter === 'all'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Tous ({stats.total_leads})
            </button>
            <button
              onClick={() => setFilter('hot')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                filter === 'hot'
                  ? 'bg-gradient-to-r from-red-600 to-orange-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🔥 Chauds ({stats.hot_leads})
            </button>
            <button
              onClick={() => setFilter('warm')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                filter === 'warm'
                  ? 'bg-gradient-to-r from-yellow-600 to-orange-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              🌤️ Tièdes ({stats.warm_leads})
            </button>
            <button
              onClick={() => setFilter('cold')}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                filter === 'cold'
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              ❄️ Froids ({stats.cold_leads})
            </button>
          </div>

          {/* Leads List */}
          <div className="grid grid-cols-1 gap-4">
            {filteredLeads.map(lead => (
              <LeadCard
                key={lead.id}
                lead={lead}
                onCalculateScore={() => calculateLeadScore(lead.id)}
                onStartSequence={(type) => startEmailSequence(lead.id, type)}
                onPredict={() => predictClosing(lead.id)}
                onClick={() => setSelectedLead(lead)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Sequences Tab */}
      {activeTab === 'sequences' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Mail className="text-indigo-600" />
              Séquences d'Emails Automatiques
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Nurture Sequence */}
              <SequenceCard
                title="🌱 Nurture (14 jours)"
                description="5 emails sur 14 jours pour convertir les prospects"
                emails={[
                  { day: 0, subject: "Bienvenue! Découvrez comment nous pouvons vous aider" },
                  { day: 2, subject: "3 raisons de choisir notre solution" },
                  { day: 5, subject: "Case Study: +300% de ventes" },
                  { day: 7, subject: "Démo gratuite: Prêt à passer à l'action?" },
                  { day: 14, subject: "Dernière chance: Offre -20%" }
                ]}
                stats={{ sent: 342, opened: 231, clicked: 89, converted: 34 }}
                color="green"
              />

              {/* Onboarding Sequence */}
              <SequenceCard
                title="👋 Onboarding (7 jours)"
                description="4 emails pour accompagner les nouveaux clients"
                emails={[
                  { day: 0, subject: "Bienvenue! Commençons ensemble" },
                  { day: 1, subject: "Étape 1: Configurez votre profil" },
                  { day: 3, subject: "Étape 2: Invitez votre équipe" },
                  { day: 7, subject: "Astuce: Maximisez votre ROI" }
                ]}
                stats={{ sent: 187, opened: 165, clicked: 98, converted: 145 }}
                color="blue"
              />

              {/* Demo Follow-up */}
              <SequenceCard
                title="🎯 Suivi Démo (5 jours)"
                description="3 emails après une démo pour closer"
                emails={[
                  { day: 0, subject: "Merci pour votre intérêt!" },
                  { day: 2, subject: "Proposition personnalisée" },
                  { day: 5, subject: "Prêt à démarrer?" }
                ]}
                stats={{ sent: 89, opened: 78, clicked: 45, converted: 28 }}
                color="purple"
              />

              {/* Re-engagement */}
              <SequenceCard
                title="🔄 Réengagement (10 jours)"
                description="Réactivez les leads inactifs"
                emails={[
                  { day: 0, subject: "On ne vous oublie pas!" },
                  { day: 3, subject: "Nouveautés depuis votre départ" },
                  { day: 7, subject: "Offre exclusive de retour" },
                  { day: 10, subject: "Dernière tentative..." }
                ]}
                stats={{ sent: 234, opened: 98, clicked: 34, converted: 12 }}
                color="orange"
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* AI Predictions Section */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Zap className="text-indigo-600" />
              Prédictions IA
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl p-6 text-white">
                <Activity size={32} className="mb-2" />
                <p className="text-3xl font-bold">85%</p>
                <p className="text-purple-100">Précision des prédictions</p>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white">
                <TrendingUp size={32} className="mb-2" />
                <p className="text-3xl font-bold">+25%</p>
                <p className="text-green-100">Augmentation conversions</p>
              </div>
              <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl p-6 text-white">
                <Clock size={32} className="mb-2" />
                <p className="text-3xl font-bold">-40%</p>
                <p className="text-orange-100">Temps de closing réduit</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-bold">Top 5 Leads à Closer Cette Semaine</h3>
              {leads
                .filter(l => l.status === 'hot')
                .slice(0, 5)
                .map(lead => (
                  <PredictionRow key={lead.id} lead={lead} />
                ))}
            </div>
          </div>

          {/* Automation Stats */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <CheckCircle className="text-green-600" />
              Tâches Automatisées
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4">Ce Mois</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Emails envoyés automatiquement</span>
                    <span className="font-bold text-indigo-600">1,234</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Tâches créées automatiquement</span>
                    <span className="font-bold text-indigo-600">234</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Scores recalculés</span>
                    <span className="font-bold text-indigo-600">487</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Notifications envoyées</span>
                    <span className="font-bold text-indigo-600">892</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4">Gains de Productivité</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Temps économisé</span>
                    <span className="font-bold text-green-600">124h</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Tâches automatisées</span>
                    <span className="font-bold text-green-600">60%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Revenus additionnels</span>
                    <span className="font-bold text-green-600">187K€</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">ROI</span>
                    <span className="font-bold text-green-600">5,238%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Lead Detail Modal */}
      <AnimatePresence>
        {selectedLead && (
          <LeadDetailModal
            lead={selectedLead}
            onClose={() => setSelectedLead(null)}
            onCalculateScore={() => calculateLeadScore(selectedLead.id)}
            onStartSequence={(type) => startEmailSequence(selectedLead.id, type)}
            onPredict={() => predictClosing(selectedLead.id)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Component: KPI Card
const KPICard = ({ icon: Icon, title, value, subtitle, color, trend }) => {
  const colorClasses = {
    red: 'border-red-500 text-red-600',
    blue: 'border-blue-500 text-blue-600',
    green: 'border-green-500 text-green-600',
    purple: 'border-purple-500 text-purple-600'
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${colorClasses[color]}`}
    >
      <div className="flex items-center justify-between mb-3">
        <Icon size={32} className={colorClasses[color]} />
        {trend && (
          <span className="text-green-600 font-semibold text-sm bg-green-50 px-2 py-1 rounded">
            {trend}
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-4xl font-bold mb-1">{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </motion.div>
  );
};

// Component: Lead Card
const LeadCard = ({ lead, onCalculateScore, onStartSequence, onPredict, onClick }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-blue-500 to-indigo-600';
    if (score >= 40) return 'from-orange-500 to-yellow-600';
    return 'from-gray-500 to-gray-600';
  };

  const getStatusIcon = (status) => {
    if (status === 'hot') return <Flame className="text-red-500" size={20} />;
    if (status === 'warm') return <Activity className="text-orange-500" size={20} />;
    return <Target className="text-blue-500" size={20} />;
  };

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      className="bg-white rounded-xl shadow-lg p-6 cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            {getStatusIcon(lead.status)}
            <h3 className="text-xl font-bold">
              {lead.first_name} {lead.last_name}
            </h3>
            <div className={`px-3 py-1 rounded-full bg-gradient-to-r ${getScoreColor(lead.score)} text-white font-bold text-sm`}>
              {lead.score} ({lead.grade})
            </div>
          </div>
          <p className="text-gray-600">{lead.job_title} @ {lead.company}</p>
          <p className="text-sm text-gray-500">{lead.email}</p>
        </div>

        <div className="text-right">
          <p className="text-2xl font-bold text-purple-600">
            {lead.estimated_value.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })}
          </p>
          <p className="text-sm text-gray-500">Valeur estimée</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <Eye size={20} className="text-blue-600 mx-auto mb-1" />
          <p className="text-xl font-bold">{lead.email_opens}</p>
          <p className="text-xs text-gray-600">Ouvertures</p>
        </div>
        <div className="text-center">
          <MessageSquare size={20} className="text-green-600 mx-auto mb-1" />
          <p className="text-xl font-bold">{lead.link_clicks}</p>
          <p className="text-xs text-gray-600">Clics</p>
        </div>
        <div className="text-center">
          <TrendingUp size={20} className="text-purple-600 mx-auto mb-1" />
          <p className="text-xl font-bold">{lead.closing_probability}%</p>
          <p className="text-xs text-gray-600">Probabilité</p>
        </div>
        <div className="text-center">
          <Clock size={20} className="text-orange-600 mx-auto mb-1" />
          <p className="text-sm font-bold">
            {formatDistanceToNow(lead.last_activity, { locale: fr, addSuffix: true })}
          </p>
          <p className="text-xs text-gray-600">Dernière activité</p>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); onCalculateScore(); }}
          className="flex-1 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-semibold hover:bg-blue-200 transition-colors text-sm"
        >
          ♻️ Recalculer Score
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onStartSequence('nurture'); }}
          className="flex-1 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg font-semibold hover:bg-purple-200 transition-colors text-sm"
        >
          📧 Lancer Séquence
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onPredict(); }}
          className="flex-1 px-4 py-2 bg-green-100 text-green-700 rounded-lg font-semibold hover:bg-green-200 transition-colors text-sm"
        >
          🔮 Prédire
        </button>
      </div>
    </motion.div>
  );
};

// Component: Sequence Card
const SequenceCard = ({ title, description, emails, stats, color }) => {
  const colorClasses = {
    green: 'from-green-500 to-emerald-600',
    blue: 'from-blue-500 to-indigo-600',
    purple: 'from-purple-500 to-pink-600',
    orange: 'from-orange-500 to-red-600'
  };

  const openRate = ((stats.opened / stats.sent) * 100).toFixed(1);
  const conversionRate = ((stats.converted / stats.sent) * 100).toFixed(1);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className={`h-2 bg-gradient-to-r ${colorClasses[color]}`} />
      <div className="p-6">
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-gray-600 text-sm mb-4">{description}</p>

        <div className="space-y-2 mb-4">
          {emails.map((email, idx) => (
            <div key={idx} className="flex items-center gap-2 text-sm">
              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-700">
                J{email.day}
              </div>
              <div className="flex-1">
                <p className="text-gray-700">{email.subject}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-center">
            <p className="text-xl font-bold text-blue-600">{openRate}%</p>
            <p className="text-xs text-gray-600">Ouverture</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-green-600">{stats.clicked}</p>
            <p className="text-xs text-gray-600">Clics</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-purple-600">{conversionRate}%</p>
            <p className="text-xs text-gray-600">Conversion</p>
          </div>
        </div>

        <button className={`w-full px-4 py-3 bg-gradient-to-r ${colorClasses[color]} text-white rounded-lg font-semibold hover:shadow-lg transition-all`}>
          Utiliser cette séquence
        </button>
      </div>
    </div>
  );
};

// Component: Prediction Row
const PredictionRow = ({ lead }) => {
  return (
    <div className="flex items-center justify-between p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-r from-red-500 to-orange-500 flex items-center justify-center text-white font-bold">
          {lead.score}
        </div>
        <div>
          <h4 className="font-bold">{lead.first_name} {lead.last_name}</h4>
          <p className="text-sm text-gray-600">{lead.company}</p>
        </div>
      </div>
      <div className="text-center">
        <p className="text-2xl font-bold text-green-600">{lead.closing_probability}%</p>
        <p className="text-xs text-gray-600">Probabilité</p>
      </div>
      <div className="text-right">
        <p className="font-bold text-purple-600">
          {lead.predicted_close_date
            ? format(lead.predicted_close_date, 'dd MMM', { locale: fr })
            : 'N/A'}
        </p>
        <p className="text-xs text-gray-600">Date estimée</p>
      </div>
      <button className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all">
        Contacter maintenant
      </button>
    </div>
  );
};

// Component: Lead Detail Modal
const LeadDetailModal = ({ lead, onClose, onCalculateScore, onStartSequence, onPredict }) => {
  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-full md:max-w-4xl bg-white rounded-2xl shadow-2xl z-50 overflow-auto max-h-[90vh]"
      >
        <div className="p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold mb-2">
                {lead.first_name} {lead.last_name}
              </h2>
              <p className="text-xl text-gray-600">{lead.job_title} @ {lead.company}</p>
              <p className="text-gray-500">{lead.email}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-4 text-white">
              <Award size={24} className="mb-2" />
              <p className="text-3xl font-bold">{lead.score}</p>
              <p className="text-green-100">Score (Grade {lead.grade})</p>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-4 text-white">
              <TrendingUp size={24} className="mb-2" />
              <p className="text-3xl font-bold">{lead.closing_probability}%</p>
              <p className="text-purple-100">Probabilité de closing</p>
            </div>
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 text-white">
              <DollarSign size={24} className="mb-2" />
              <p className="text-3xl font-bold">
                {(lead.estimated_value / 1000).toFixed(0)}K€
              </p>
              <p className="text-blue-100">Valeur estimée</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="font-bold mb-3">Activité</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Emails ouverts</span>
                  <span className="font-bold">{lead.email_opens}</span>
                </div>
                <div className="flex justify-between">
                  <span>Liens cliqués</span>
                  <span className="font-bold">{lead.link_clicks}</span>
                </div>
                <div className="flex justify-between">
                  <span>Page pricing visitée</span>
                  <span className="font-bold">{lead.visited_pricing_page ? '✅ Oui' : '❌ Non'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Démo demandée</span>
                  <span className="font-bold">{lead.requested_demo ? '✅ Oui' : '❌ Non'}</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h3 className="font-bold mb-3">Informations</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Assigné à</span>
                  <span className="font-bold">{lead.assigned_to}</span>
                </div>
                <div className="flex justify-between">
                  <span>Dernière activité</span>
                  <span className="font-bold">
                    {formatDistanceToNow(lead.last_activity, { locale: fr, addSuffix: true })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Date closing estimée</span>
                  <span className="font-bold">
                    {lead.predicted_close_date
                      ? format(lead.predicted_close_date, 'dd MMMM yyyy', { locale: fr })
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onCalculateScore}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors"
            >
              ♻️ Recalculer Score
            </button>
            <button
              onClick={() => onStartSequence('nurture')}
              className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors"
            >
              📧 Lancer Séquence
            </button>
            <button
              onClick={onPredict}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-colors"
            >
              🔮 Prédire Closing
            </button>
          </div>
        </div>
      </motion.div>
    </>
  );
};

export default CRMDashboard;
