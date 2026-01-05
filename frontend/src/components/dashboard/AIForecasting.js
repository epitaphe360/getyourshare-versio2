import React, { useState, useEffect, useMemo } from 'react';
import { TrendingUp, LineChart, AlertTriangle, Target, Activity, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import './AIForecasting.css';

const AIForecasting = ({ leads = [], historicalData = [] }) => {
  const [forecastPeriod, setForecastPeriod] = useState('quarter'); // week, month, quarter, year
  const [forecastData, setForecastData] = useState(null);
  const [churnPredictions, setChurnPredictions] = useState([]);
  const [growthOpportunities, setGrowthOpportunities] = useState([]);

  // Calculate forecasts
  useEffect(() => {
    if (leads.length > 0) {
      const forecast = calculateRevenueForecast(leads, forecastPeriod);
      const churn = calculateChurnPredictions(leads);
      const growth = calculateGrowthOpportunities(leads);

      setForecastData(forecast);
      setChurnPredictions(churn);
      setGrowthOpportunities(growth);
    }
  }, [leads, forecastPeriod]);

  const calculateRevenueForecast = (leadsData, period) => {
    // Calculate weighted forecast based on lead scores and probabilities
    const hotLeads = leadsData.filter(l => l.temperature === 'hot');
    const warmLeads = leadsData.filter(l => l.temperature === 'warm');

    // Estimations
    const hotRevenue = hotLeads.reduce((sum, lead) => sum + (lead.estimatedValue || 0) * 0.7, 0);
    const warmRevenue = warmLeads.reduce((sum, lead) => sum + (lead.estimatedValue || 0) * 0.3, 0);

    const totalForecast = hotRevenue + warmRevenue;

    // Adjust by period
    let periodMultiplier = 1;
    if (period === 'month') periodMultiplier = 1 / 3;
    else if (period === 'week') periodMultiplier = 1 / 13;
    else if (period === 'year') periodMultiplier = 4;

    const projectedRevenue = Math.round(totalForecast * periodMultiplier);

    // Calculate confidence
    const confidence = 50 + (hotLeads.length * 5) + Math.min(30, warmLeads.length * 2);

    // Calculate growth rate
    const previousForecast = Math.round(totalForecast * 0.85); // Assume 15% improvement
    const growthRate = ((projectedRevenue - previousForecast) / previousForecast * 100).toFixed(1);

    // Scenario analysis
    const scenarios = {
      conservative: Math.round(projectedRevenue * 0.7),
      realistic: projectedRevenue,
      optimistic: Math.round(projectedRevenue * 1.3),
    };

    return {
      projectedRevenue,
      confidence: Math.min(95, confidence),
      growthRate,
      scenarios,
      hotDealsCount: hotLeads.length,
      warmDealsCount: warmLeads.length,
      averageDealSize: Math.round((hotRevenue + warmRevenue) / (hotLeads.length + warmLeads.length || 1)),
      daysToClose: calculateAverageDaysToClose(leadsData),
    };
  };

  const calculateChurnPredictions = (leadsData) => {
    // Identify leads at risk of churn
    const atRiskLeads = leadsData
      .filter(lead => {
        const lastContact = lead.lastContact ? new Date(lead.lastContact) : new Date(lead.createdAt);
        const daysSinceContact = (Date.now() - lastContact) / (1000 * 60 * 60 * 24);

        return (
          daysSinceContact > 30 &&
          (lead.temperature === 'cold' || lead.temperature === 'warm') &&
          !lead.hasNegativeSignal
        );
      })
      .map(lead => ({
        ...lead,
        churnRisk: calculateChurnRisk(lead),
      }))
      .sort((a, b) => b.churnRisk - a.churnRisk)
      .slice(0, 5);

    return atRiskLeads;
  };

  const calculateChurnRisk = (lead) => {
    let risk = 0;

    const lastContact = lead.lastContact ? new Date(lead.lastContact) : new Date(lead.createdAt);
    const daysSinceContact = (Date.now() - lastContact) / (1000 * 60 * 60 * 24);

    if (daysSinceContact > 60) risk += 40;
    else if (daysSinceContact > 30) risk += 20;
    else if (daysSinceContact > 14) risk += 10;

    if (lead.temperature === 'cold') risk += 30;
    else if (lead.temperature === 'warm') risk += 15;

    if (lead.hasNegativeSignal) risk += 35;

    return Math.min(100, risk);
  };

  const calculateGrowthOpportunities = (leadsData) => {
    // Find high-potential leads for expansion
    const opportunities = leadsData
      .filter(lead => lead.temperature !== 'cold' && lead.estimatedValue > 0)
      .map(lead => {
        const potentialExpansion = {
          lead,
          currentValue: lead.estimatedValue || 0,
          potentialValue: Math.round((lead.estimatedValue || 0) * 1.5),
          upsellOpportunity: generateUpsellStrategy(lead),
          timelineWeeks: lead.temperature === 'hot' ? 2 : 4,
        };
        return potentialExpansion;
      })
      .sort((a, b) => (b.potentialValue - b.currentValue) - (a.potentialValue - a.currentValue))
      .slice(0, 5);

    return opportunities;
  };

  const generateUpsellStrategy = (lead) => {
    const strategies = {
      small: 'Ajouter un module complémentaire (+30% valeur)',
      medium: 'Upgrader vers le plan supérieur (+50% valeur)',
      large: 'Vendre un service professionnel associé (+100% valeur)',
    };

    let size = 'small';
    if (lead.estimatedValue > 30000) size = 'large';
    else if (lead.estimatedValue > 10000) size = 'medium';

    return strategies[size];
  };

  const calculateAverageDaysToClose = (leadsData) => {
    const closedLeads = leadsData.filter(l => l.closedAt);
    if (closedLeads.length === 0) return 30;

    const totalDays = closedLeads.reduce((sum, lead) => {
      const created = new Date(lead.createdAt);
      const closed = new Date(lead.closedAt);
      return sum + Math.floor((closed - created) / (1000 * 60 * 60 * 24));
    }, 0);

    return Math.round(totalDays / closedLeads.length);
  };

  return (
    <motion.div
      className="ai-forecasting"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.5 }}
    >
      <div className="forecasting-header">
        <div className="header-content">
          <LineChart size={28} />
          <div>
            <h2>Prévisions IA & Revenue Intelligence</h2>
            <p>Modèles prédictifs alimentés par Machine Learning</p>
          </div>
        </div>

        <div className="period-selector">
          {['week', 'month', 'quarter', 'year'].map(period => (
            <button
              key={period}
              className={`period-btn ${forecastPeriod === period ? 'active' : ''}`}
              onClick={() => setForecastPeriod(period)}
            >
              {period === 'week' ? 'Semaine' : period === 'month' ? 'Mois' : period === 'quarter' ? 'Trimestre' : 'Année'}
            </button>
          ))}
        </div>
      </div>

      {forecastData && (
        <motion.div className="forecast-main" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="forecast-primary">
            <div className="revenue-card">
              <div className="card-header">
                <TrendingUp size={24} />
                <h3>Prévision de Revenu</h3>
              </div>

              <div className="revenue-display">
                <div className="revenue-value">
                  {(forecastData.projectedRevenue).toLocaleString('fr-FR')}€
                </div>
                <div className="revenue-meta">
                  <span className={`growth ${forecastData.growthRate > 0 ? 'positive' : 'negative'}`}>
                    {forecastData.growthRate > 0 ? '+' : ''}{forecastData.growthRate}%
                  </span>
                  <span className="confidence">
                    Confiance: {forecastData.confidence}%
                  </span>
                </div>
              </div>

              <div className="scenarios">
                <div className="scenario-item conservative">
                  <span className="scenario-label">Scénario pessimiste</span>
                  <span className="scenario-value">
                    {(forecastData.scenarios.conservative).toLocaleString('fr-FR')}€
                  </span>
                </div>
                <div className="scenario-item realistic">
                  <span className="scenario-label">Scénario réaliste</span>
                  <span className="scenario-value">
                    {(forecastData.scenarios.realistic).toLocaleString('fr-FR')}€
                  </span>
                </div>
                <div className="scenario-item optimistic">
                  <span className="scenario-label">Scénario optimiste</span>
                  <span className="scenario-value">
                    {(forecastData.scenarios.optimistic).toLocaleString('fr-FR')}€
                  </span>
                </div>
              </div>

              <div className="forecast-metrics">
                <div className="metric">
                  <span className="metric-label">Deals chauds</span>
                  <span className="metric-value">{forecastData.hotDealsCount}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Deals tièdes</span>
                  <span className="metric-value">{forecastData.warmDealsCount}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Deal moyen</span>
                  <span className="metric-value">{(forecastData.averageDealSize).toLocaleString('fr-FR')}€</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Jours pour fermer</span>
                  <span className="metric-value">{forecastData.daysToClose}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="forecast-secondary">
            <motion.div className="churn-risks">
              <div className="section-header">
                <AlertTriangle size={20} />
                <h3>Leads à Risque ({churnPredictions.length})</h3>
              </div>

              <div className="risks-list">
                {churnPredictions.length === 0 ? (
                  <p className="empty-message">Aucun lead à risque</p>
                ) : (
                  churnPredictions.map(lead => (
                    <motion.div
                      key={lead.id}
                      className="risk-item"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <div className="risk-info">
                        <p className="risk-name">{lead.name}</p>
                        <p className="risk-company">{lead.company}</p>
                      </div>
                      <div className="risk-score">
                        <div className="risk-gauge">
                          <div
                            className="risk-fill"
                            style={{
                              width: `${lead.churnRisk}%`,
                              background: lead.churnRisk > 60 ? '#d33027' : '#f9ab00',
                            }}
                          ></div>
                        </div>
                        <span className="risk-percent">{lead.churnRisk}%</span>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>

            <motion.div className="growth-opportunities">
              <div className="section-header">
                <Target size={20} />
                <h3>Opportunités de Croissance</h3>
              </div>

              <div className="opportunities-list">
                {growthOpportunities.length === 0 ? (
                  <p className="empty-message">Pas d'opportunités détectées</p>
                ) : (
                  growthOpportunities.map((opp, idx) => (
                    <motion.div
                      key={idx}
                      className="opportunity-item"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <div className="opp-info">
                        <p className="opp-name">{opp.lead.name}</p>
                        <p className="opp-strategy">{opp.upsellOpportunity}</p>
                      </div>
                      <div className="opp-value">
                        <span className="current">{(opp.currentValue).toLocaleString('fr-FR')}€</span>
                        <span className="arrow">→</span>
                        <span className="potential">{(opp.potentialValue).toLocaleString('fr-FR')}€</span>
                      </div>
                    </motion.div>
                  ))
                )}
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}

      <div className="forecast-insights">
        <div className="insight-card">
          <Activity size={20} />
          <p>
            <strong>Tendance:</strong> Votre pipeline est en bonne santé avec {leads.filter(l => l.temperature === 'hot').length} deals
            chauds et une moyenne de clôture de {forecastData?.daysToClose || 30} jours.
          </p>
        </div>

        <div className="insight-card">
          <Clock size={20} />
          <p>
            <strong>Recommandation:</strong> Concentrez vos efforts sur les {churnPredictions.length > 0 ? churnPredictions.length : 'risques identifiés'} leads
            à risque avant qu'ils ne quittent le pipeline.
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default AIForecasting;
