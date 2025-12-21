import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { TrendingUp, Zap, Target, Brain, BarChart3, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import './LeadScoring.css';

const LeadScoring = ({ leads = [] }) => {
  const [scoredLeads, setScoredLeads] = useState([]);
  const [sortBy, setSortBy] = useState('score'); // score, engagement, buyProbability
  const [filterCategory, setFilterCategory] = useState('all'); // all, hot, warm, cold
  const [showScoreBreakdown, setShowScoreBreakdown] = useState(null);

  // Calculate lead score using sophisticated algorithm
  const calculateLeadScore = useCallback((lead) => {
    let score = 0;
    const breakdown = {
      engagement: 0,
      buyProbability: 0,
      urgency: 0,
      rot: 0, // Return on Time
    };

    // 1. ENGAGEMENT SCORE (30%)
    const engagementFactors = {
      emailOpens: (lead.emailOpens || 0) * 10,
      emailClicks: (lead.emailClicks || 0) * 20,
      pageVisits: (lead.pageVisits || 0) * 5,
      contentDownloads: (lead.contentDownloads || 0) * 15,
      demoRequests: (lead.demoRequests || 0) * 25,
      proposalViewed: (lead.proposalViewed || false) ? 30 : 0,
      formSubmissions: (lead.formSubmissions || 0) * 20,
    };

    const engagementScore = Math.min(
      100,
      Object.values(engagementFactors).reduce((a, b) => a + b, 0)
    );
    breakdown.engagement = engagementScore;
    score += engagementScore * 0.3;

    // 2. BUY PROBABILITY (35%)
    const buyFactors = {
      budgetConfirmed: (lead.budgetConfirmed || false) ? 30 : 0,
      decisionMakerIdentified: (lead.decisionMakerIdentified || false) ? 25 : 0,
      needsAlignment: (lead.needsAlignment || 0) * 10,
      competitorMentioned: (lead.competitorMentioned || false) ? 15 : 0,
      talkingToCompetitors: (lead.talkingToCompetitors || false) ? -20 : 0,
      signalNegative: (lead.signalNegative || false) ? -30 : 0,
      implementationTimeline: (lead.implementationTimeline ? 20 : 0),
    };

    const buyScore = Math.max(
      0,
      Math.min(
        100,
        Object.values(buyFactors).reduce((a, b) => a + b, 0)
      )
    );
    breakdown.buyProbability = buyScore;
    score += buyScore * 0.35;

    // 3. URGENCY SCORE (20%)
    const now = new Date();
    const lastContact = lead.lastContact ? new Date(lead.lastContact) : new Date(lead.createdAt);
    const daysSinceContact = Math.floor((now - lastContact) / (1000 * 60 * 60 * 24));

    let urgencyScore = 0;
    if (daysSinceContact < 3) urgencyScore = 90;
    else if (daysSinceContact < 7) urgencyScore = 70;
    else if (daysSinceContact < 14) urgencyScore = 50;
    else if (daysSinceContact < 30) urgencyScore = 30;
    else urgencyScore = 10;

    breakdown.urgency = urgencyScore;
    score += urgencyScore * 0.2;

    // 4. ROT SCORE - Return on Time (15%)
    // Score based on estimated time to close vs potential deal value
    const estimatedValue = lead.estimatedValue || 10000;
    const estimatedDaysToClose = lead.estimatedDaysToClose || 30;
    const rotScore = Math.min(
      100,
      (estimatedValue / estimatedDaysToClose) * 0.1
    );
    breakdown.rot = rotScore;
    score += rotScore * 0.15;

    return {
      score: Math.round(score),
      breakdown,
      category: score >= 70 ? 'hot' : score >= 40 ? 'warm' : 'cold',
    };
  }, []);

  // Score all leads
  useEffect(() => {
    const scored = leads.map(lead => ({
      ...lead,
      scoring: calculateLeadScore(lead),
    }));
    setScoredLeads(scored);
  }, [leads, calculateLeadScore]);

  // Filter and sort leads
  const filteredAndSortedLeads = useMemo(() => {
    let filtered = scoredLeads;

    // Filter by category
    if (filterCategory !== 'all') {
      filtered = filtered.filter(lead => lead.scoring.category === filterCategory);
    }

    // Sort
    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.scoring.score - a.scoring.score;
        case 'engagement':
          return b.scoring.breakdown.engagement - a.scoring.breakdown.engagement;
        case 'buyProbability':
          return b.scoring.breakdown.buyProbability - a.scoring.breakdown.buyProbability;
        default:
          return 0;
      }
    });
  }, [scoredLeads, sortBy, filterCategory]);

  // Get score color
  const getScoreColor = (score) => {
    if (score >= 70) return '#0f9d58';
    if (score >= 40) return '#f9ab00';
    return '#d33027';
  };

  // Get score label
  const getScoreLabel = (score) => {
    if (score >= 70) return 'HOT';
    if (score >= 40) return 'WARM';
    return 'COLD';
  };

  // Render score gauge
  const renderScoreGauge = (score) => {
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;
    const color = getScoreColor(score);

    return (
      <svg width="120" height="120" className="score-gauge">
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="#e9ecef"
          strokeWidth="8"
        />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
        />
        <text
          x="60"
          y="70"
          textAnchor="middle"
          className="gauge-text"
          fill={color}
        >
          {score}
        </text>
      </svg>
    );
  };

  return (
    <motion.div
      className="lead-scoring"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 }}
    >
      <div className="scoring-header">
        <div className="header-title">
          <Brain size={28} />
          <div>
            <h2>Scoring IA des Leads</h2>
            <p>Algorithme intelligent de qualification automatique</p>
          </div>
        </div>
      </div>

      <div className="scoring-controls">
        <div className="control-group">
          <label>Trier par:</label>
          <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
            <option value="score">Score global</option>
            <option value="engagement">Engagement</option>
            <option value="buyProbability">Probabilité d'achat</option>
          </select>
        </div>

        <div className="control-group">
          <label>Filtrer:</label>
          <div className="filter-buttons">
            <button
              className={`filter-btn ${filterCategory === 'all' ? 'active' : ''}`}
              onClick={() => setFilterCategory('all')}
            >
              Tous ({scoredLeads.length})
            </button>
            <button
              className={`filter-btn hot ${filterCategory === 'hot' ? 'active' : ''}`}
              onClick={() => setFilterCategory('hot')}
            >
              🔥 Hot ({scoredLeads.filter(l => l.scoring.category === 'hot').length})
            </button>
            <button
              className={`filter-btn warm ${filterCategory === 'warm' ? 'active' : ''}`}
              onClick={() => setFilterCategory('warm')}
            >
              🌡️ Warm ({scoredLeads.filter(l => l.scoring.category === 'warm').length})
            </button>
            <button
              className={`filter-btn cold ${filterCategory === 'cold' ? 'active' : ''}`}
              onClick={() => setFilterCategory('cold')}
            >
              ❄️ Cold ({scoredLeads.filter(l => l.scoring.category === 'cold').length})
            </button>
          </div>
        </div>
      </div>

      <div className="scoring-stats">
        <motion.div className="stat-card">
          <TrendingUp size={24} />
          <div>
            <p className="stat-label">Score moyen</p>
            <p className="stat-value">
              {scoredLeads.length > 0
                ? Math.round(scoredLeads.reduce((a, b) => a + b.scoring.score, 0) / scoredLeads.length)
                : 0}
            </p>
          </div>
        </motion.div>

        <motion.div className="stat-card">
          <Zap size={24} />
          <div>
            <p className="stat-label">Leads prêts à vendre</p>
            <p className="stat-value">
              {scoredLeads.filter(l => l.scoring.score >= 70).length}
            </p>
          </div>
        </motion.div>

        <motion.div className="stat-card">
          <Target size={24} />
          <div>
            <p className="stat-label">Conversion probable</p>
            <p className="stat-value">
              {scoredLeads.length > 0
                ? Math.round(
                    scoredLeads.reduce((a, b) => a + b.scoring.breakdown.buyProbability, 0) /
                      scoredLeads.length
                  )
                : 0}
              %
            </p>
          </div>
        </motion.div>

        <motion.div className="stat-card">
          <AlertCircle size={24} />
          <div>
            <p className="stat-label">Urgents à traiter</p>
            <p className="stat-value">
              {scoredLeads.filter(l => l.scoring.breakdown.urgency >= 80).length}
            </p>
          </div>
        </motion.div>
      </div>

      <div className="leads-grid">
        {filteredAndSortedLeads.length === 0 ? (
          <div className="empty-state">
            <AlertCircle size={48} />
            <p>Aucun lead dans cette catégorie</p>
          </div>
        ) : (
          filteredAndSortedLeads.map(lead => (
            <motion.div
              key={lead.id}
              className={`lead-score-card ${lead.scoring.category}`}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileHover={{ y: -4 }}
            >
              <div className="card-header">
                <div className="lead-basic">
                  <h3>{lead.name}</h3>
                  <p className="lead-company">{lead.company}</p>
                </div>
                <div className="score-display">
                  {renderScoreGauge(lead.scoring.score)}
                  <span className={`score-label ${lead.scoring.category}`}>
                    {getScoreLabel(lead.scoring.score)}
                  </span>
                </div>
              </div>

              <div className="breakdown-bars">
                <div className="bar-item">
                  <div className="bar-label">
                    <span>Engagement</span>
                    <span className="bar-value">{Math.round(lead.scoring.breakdown.engagement)}</span>
                  </div>
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${lead.scoring.breakdown.engagement}%`,
                        background: '#667eea',
                      }}
                    ></div>
                  </div>
                </div>

                <div className="bar-item">
                  <div className="bar-label">
                    <span>Achat probable</span>
                    <span className="bar-value">{Math.round(lead.scoring.breakdown.buyProbability)}</span>
                  </div>
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${lead.scoring.breakdown.buyProbability}%`,
                        background: '#43e97b',
                      }}
                    ></div>
                  </div>
                </div>

                <div className="bar-item">
                  <div className="bar-label">
                    <span>Urgence</span>
                    <span className="bar-value">{Math.round(lead.scoring.breakdown.urgency)}</span>
                  </div>
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${lead.scoring.breakdown.urgency}%`,
                        background: '#f5576c',
                      }}
                    ></div>
                  </div>
                </div>
              </div>

              <button
                className="details-btn"
                onClick={() =>
                  setShowScoreBreakdown(
                    showScoreBreakdown === lead.id ? null : lead.id
                  )
                }
              >
                {showScoreBreakdown === lead.id ? 'Masquer' : 'Voir'} les détails
              </button>

              {showScoreBreakdown === lead.id && (
                <motion.div
                  className="score-breakdown"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <div className="breakdown-detail">
                    <p className="breakdown-title">Analyse détaillée du score</p>
                    <div className="breakdown-metrics">
                      <div className="metric">
                        <span className="metric-name">Engagement (30%)</span>
                        <span className="metric-calc">
                          {Math.round(lead.scoring.breakdown.engagement)} × 0.30 = {Math.round(lead.scoring.breakdown.engagement * 0.3)}
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-name">Probabilité d'achat (35%)</span>
                        <span className="metric-calc">
                          {Math.round(lead.scoring.breakdown.buyProbability)} × 0.35 = {Math.round(lead.scoring.breakdown.buyProbability * 0.35)}
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-name">Urgence (20%)</span>
                        <span className="metric-calc">
                          {Math.round(lead.scoring.breakdown.urgency)} × 0.20 = {Math.round(lead.scoring.breakdown.urgency * 0.2)}
                        </span>
                      </div>
                      <div className="metric">
                        <span className="metric-name">ROT (15%)</span>
                        <span className="metric-calc">
                          {Math.round(lead.scoring.breakdown.rot)} × 0.15 = {Math.round(lead.scoring.breakdown.rot * 0.15)}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default LeadScoring;
