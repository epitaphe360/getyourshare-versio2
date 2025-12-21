import React, { useState } from 'react';
import { Users, BarChart3, Settings, Eye, Lock, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';
import './SpecializedDashboards.css';

const SpecializedDashboards = ({ leads = [], user }) => {
  const [selectedRole, setSelectedRole] = useState(user?.role || 'vendor');

  const roles = {
    vendor: {
      title: 'Dashboard Vendeur',
      icon: <Users size={24} />,
      color: '#667eea',
      description: 'Votre pipeline de ventes personnel',
      metrics: [
        { label: 'Leads actifs', value: leads.filter(l => l.temperature !== 'cold').length, icon: '📊' },
        { label: 'Valeur pipeline', value: `${leads.reduce((sum, l) => sum + (l.estimatedValue || 0), 0) / 1000}k€`, icon: '💰' },
        { label: 'Taux de conversion', value: '35%', icon: '📈' },
        { label: 'Cycle moyen', value: '30 jours', icon: '⏱️' },
      ],
      sections: [
        {
          id: 'my-pipeline',
          title: 'Mon Pipeline',
          type: 'table',
          data: leads.slice(0, 5),
        },
        {
          id: 'activity',
          title: 'Mes Activités Récentes',
          type: 'activity',
          items: [
            { action: 'Appel avec Jean Dupont', time: 'Il y a 2h', status: 'completed' },
            { action: 'Email envoyé à Marie Bernard', time: 'Il y a 4h', status: 'completed' },
            { action: 'Rendez-vous prévu avec Acme Corp', time: 'Demain à 10h', status: 'scheduled' },
          ],
        },
      ],
    },

    manager: {
      title: 'Dashboard Manager',
      icon: <BarChart3 size={24} />,
      color: '#f093fb',
      description: 'Vue d\'ensemble de l\'équipe',
      metrics: [
        { label: 'Équipe', value: '12', icon: '👥' },
        { label: 'Pipeline total', value: '450k€', icon: '💼' },
        { label: 'Fermetures mensuelles', value: '150k€', icon: '✅' },
        { label: 'Performance', value: '105%', icon: '🎯' },
      ],
      sections: [
        {
          id: 'team-performance',
          title: 'Performance de l\'Équipe',
          type: 'chart',
          data: [
            { name: 'Jean D.', closed: 120, target: 100, percentage: 120 },
            { name: 'Marie B.', closed: 95, target: 100, percentage: 95 },
            { name: 'Pierre L.', closed: 110, target: 100, percentage: 110 },
            { name: 'Sophie M.', closed: 85, target: 100, percentage: 85 },
          ],
        },
        {
          id: 'team-leads',
          title: 'Leads par Vendeur',
          type: 'distribution',
          data: [
            { name: 'Jean D.', hot: 8, warm: 15, cold: 22 },
            { name: 'Marie B.', hot: 5, warm: 12, cold: 18 },
            { name: 'Pierre L.', hot: 6, warm: 14, cold: 20 },
            { name: 'Sophie M.', hot: 4, warm: 10, cold: 16 },
          ],
        },
      ],
    },

    admin: {
      title: 'Dashboard Admin',
      icon: <Settings size={24} />,
      color: '#fa709a',
      description: 'Gestion et analytics système',
      metrics: [
        { label: 'Utilisateurs actifs', value: '45', icon: '🔐' },
        { label: 'Leads total', value: '2.3k', icon: '📋' },
        { label: 'Taux d\'adoption', value: '92%', icon: '📊' },
        { label: 'Tickets support', value: '8', icon: '🎫' },
      ],
      sections: [
        {
          id: 'system-health',
          title: 'Santé du Système',
          type: 'status',
          items: [
            { service: 'API', status: 'online', uptime: '99.9%' },
            { service: 'Database', status: 'online', uptime: '99.8%' },
            { service: 'Email Service', status: 'online', uptime: '99.7%' },
            { service: 'File Storage', status: 'online', uptime: '99.9%' },
          ],
        },
        {
          id: 'user-management',
          title: 'Gestion Utilisateurs',
          type: 'users',
          stats: {
            totalUsers: 45,
            activeToday: 38,
            newThisMonth: 12,
            suspended: 2,
          },
        },
      ],
    },

    prospect: {
      title: 'Portal Client',
      icon: <Eye size={24} />,
      color: '#43e97b',
      description: 'Suivi de votre dossier',
      metrics: [
        { label: 'Votre demande', value: 'En cours', icon: '⏳' },
        { label: 'Dernière mise à jour', value: 'Il y a 2j', icon: '📅' },
        { label: 'Étape actuelle', value: '3/5', icon: '🎯' },
        { label: 'Temps moyen', value: '25 jours', icon: '⏱️' },
      ],
      sections: [
        {
          id: 'proposal-tracker',
          title: 'Suivi de Votre Proposition',
          type: 'timeline',
          steps: [
            { step: 1, title: 'Demande reçue', completed: true, date: 'Il y a 10 jours' },
            { step: 2, title: 'Analyse', completed: true, date: 'Il y a 5 jours' },
            { step: 3, title: 'Proposition envoyée', completed: true, date: 'Aujourd\'hui' },
            { step: 4, title: 'En attente signature', completed: false, date: 'À venir' },
            { step: 5, title: 'Finalisé', completed: false, date: 'À venir' },
          ],
        },
        {
          id: 'documents',
          title: 'Documents',
          type: 'documents',
          items: [
            { name: 'Proposition commerciale.pdf', date: 'Aujourd\'hui', size: '2.4 MB', icon: '📄' },
            { name: 'Conditions générales.pdf', date: 'Il y a 3j', size: '1.2 MB', icon: '📄' },
          ],
        },
      ],
    },
  };

  const dashboard = roles[selectedRole] || roles.vendor;

  const renderMetrics = () => (
    <div className="metrics-grid">
      {dashboard.metrics.map((metric, idx) => (
        <motion.div
          key={idx}
          className="metric-card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: idx * 0.1 }}
          style={{ borderLeftColor: dashboard.color }}
        >
          <span className="metric-icon">{metric.icon}</span>
          <div>
            <p className="metric-label">{metric.label}</p>
            <p className="metric-value">{metric.value}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );

  const renderSection = (section) => {
    switch (section.type) {
      case 'table':
        return (
          <div className="section-content">
            {section.data.map((item, idx) => (
              <div key={idx} className="table-row">
                <span className="col name">{item.name}</span>
                <span className="col company">{item.company}</span>
                <span className={`col status ${item.temperature}`}>{item.temperature}</span>
              </div>
            ))}
          </div>
        );

      case 'activity':
        return (
          <div className="section-content">
            {section.items.map((item, idx) => (
              <div key={idx} className={`activity-item ${item.status}`}>
                <div className="activity-dot"></div>
                <div>
                  <p className="activity-action">{item.action}</p>
                  <span className="activity-time">{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        );

      case 'chart':
        return (
          <div className="section-content">
            {section.data.map((item, idx) => (
              <div key={idx} className="chart-item">
                <span className="chart-label">{item.name}</span>
                <div className="chart-bar">
                  <div
                    className="bar-fill"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
                <span className="chart-value">{item.percentage}%</span>
              </div>
            ))}
          </div>
        );

      case 'status':
        return (
          <div className="section-content">
            {section.items.map((item, idx) => (
              <div key={idx} className="status-row">
                <span className="status-service">{item.service}</span>
                <span className={`status-badge ${item.status}`}>{item.status.toUpperCase()}</span>
                <span className="status-uptime">{item.uptime}</span>
              </div>
            ))}
          </div>
        );

      case 'timeline':
        return (
          <div className="section-content timeline">
            {section.steps.map((step, idx) => (
              <div key={idx} className={`timeline-item ${step.completed ? 'completed' : ''}`}>
                <div className="timeline-marker">
                  <span className="marker-step">{step.step}</span>
                </div>
                <div className="timeline-content">
                  <p className="timeline-title">{step.title}</p>
                  <p className="timeline-date">{step.date}</p>
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return <div className="section-content">Contenu non disponible</div>;
    }
  };

  return (
    <motion.div
      className="specialized-dashboards"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="dashboard-selector">
        {Object.entries(roles).map(([key, role]) => (
          <motion.button
            key={key}
            className={`role-btn ${selectedRole === key ? 'active' : ''}`}
            onClick={() => setSelectedRole(key)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              borderColor: selectedRole === key ? role.color : '#e9ecef',
              backgroundColor: selectedRole === key ? `${role.color}10` : 'white',
            }}
          >
            <span className="role-icon">{role.icon}</span>
            <span className="role-name">{role.title}</span>
          </motion.button>
        ))}
      </div>

      <motion.div
        className="dashboard-content"
        key={selectedRole}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="dashboard-header">
          <div>
            <h2>{dashboard.title}</h2>
            <p>{dashboard.description}</p>
          </div>
        </div>

        {renderMetrics()}

        <div className="dashboard-sections">
          {dashboard.sections.map((section, idx) => (
            <motion.div
              key={section.id}
              className="dashboard-section"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <h3>{section.title}</h3>
              {renderSection(section)}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default SpecializedDashboards;
