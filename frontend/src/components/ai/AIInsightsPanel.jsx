import React, { useState, useEffect } from 'react';
import { aiAPI } from '../../services/newEndpointsAPI';
import './AIInsights.css';

const AIInsightsPanel = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.getInsights();
      setInsights(response.data);
    } catch (err) {
      console.error('Error fetching AI insights:', err);
      setError('Failed to load insights. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    const icons = {
      success: '✅',
      warning: '⚠️',
      info: 'ℹ️',
      trend_up: '📈',
      trend_down: '📉',
      recommendation: '💡',
      alert: '🔔',
    };
    return icons[type] || '📊';
  };

  const getInsightColor = (type) => {
    const colors = {
      success: '#4caf50',
      warning: '#ff9800',
      info: '#2196f3',
      trend_up: '#4caf50',
      trend_down: '#f44336',
      recommendation: '#9c27b0',
      alert: '#f44336',
    };
    return colors[type] || '#666';
  };

  if (loading) {
    return (
      <div className="ai-insights-panel">
        <div className="insights-header">
          <h3>🧠 AI Insights</h3>
        </div>
        <div className="loading-insights">
          <div className="spinner"></div>
          <p>Analyzing your data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-insights-panel">
        <div className="insights-header">
          <h3>🧠 AI Insights</h3>
          <button onClick={fetchInsights} className="refresh-btn">
            🔄 Retry
          </button>
        </div>
        <div className="error-state">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-insights-panel">
      <div className="insights-header">
        <h3>🧠 AI Insights</h3>
        <button onClick={fetchInsights} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      {/* Performance Overview */}
      {insights?.performance_summary && (
        <div className="insights-section">
          <h4>Performance Overview</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Overall Score</div>
              <div className="metric-value" style={{ color: '#1976d2' }}>
                {insights.performance_summary.overall_score}/100
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Trend</div>
              <div className="metric-value" style={{ color: insights.performance_summary.trend === 'up' ? '#4caf50' : '#f44336' }}>
                {insights.performance_summary.trend === 'up' ? '📈' : '📉'} {insights.performance_summary.trend_percentage}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Insights */}
      {insights?.insights && insights.insights.length > 0 && (
        <div className="insights-section">
          <h4>Key Insights</h4>
          <div className="insights-list">
            {insights.insights.map((insight, index) => (
              <div
                key={index}
                className="insight-card"
                style={{ borderLeft: `4px solid ${getInsightColor(insight.type)}` }}
              >
                <div className="insight-header">
                  <span className="insight-icon">{getInsightIcon(insight.type)}</span>
                  <span className="insight-title">{insight.title}</span>
                </div>
                <p className="insight-description">{insight.description}</p>
                {insight.action && (
                  <div className="insight-action">
                    <strong>Recommended Action:</strong> {insight.action}
                  </div>
                )}
                {insight.impact && (
                  <div className="insight-impact">
                    <span>Potential Impact: </span>
                    <span style={{ color: '#1976d2', fontWeight: 'bold' }}>{insight.impact}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {insights?.recommendations && insights.recommendations.length > 0 && (
        <div className="insights-section">
          <h4>💡 AI Recommendations</h4>
          <div className="recommendations-list">
            {insights.recommendations.map((rec, index) => (
              <div key={index} className="recommendation-item">
                <div className="recommendation-priority" data-priority={rec.priority}>
                  {rec.priority}
                </div>
                <div className="recommendation-content">
                  <div className="recommendation-title">{rec.title}</div>
                  <div className="recommendation-description">{rec.description}</div>
                  {rec.estimated_impact && (
                    <div className="recommendation-impact">
                      Expected impact: <strong>{rec.estimated_impact}</strong>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Products */}
      {insights?.top_products && insights.top_products.length > 0 && (
        <div className="insights-section">
          <h4>🏆 Top Performing Products</h4>
          <div className="top-products-list">
            {insights.top_products.map((product, index) => (
              <div key={index} className="top-product-item">
                <div className="product-rank">#{index + 1}</div>
                <div className="product-info">
                  <div className="product-name">{product.name}</div>
                  <div className="product-stats">
                    <span>Revenue: ${product.revenue?.toLocaleString()}</span>
                    <span>Sales: {product.sales}</span>
                    <span>Growth: {product.growth > 0 ? '📈' : '📉'} {product.growth}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alerts */}
      {insights?.alerts && insights.alerts.length > 0 && (
        <div className="insights-section">
          <h4>🔔 Alerts</h4>
          <div className="alerts-list">
            {insights.alerts.map((alert, index) => (
              <div key={index} className={`alert-item alert-${alert.severity}`}>
                <div className="alert-header">
                  <span className="alert-icon">
                    {alert.severity === 'high' ? '🔴' : alert.severity === 'medium' ? '🟡' : '🟢'}
                  </span>
                  <span className="alert-title">{alert.title}</span>
                </div>
                <p className="alert-message">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Updated */}
      <div className="insights-footer">
        <small>
          Last updated: {insights?.generated_at ? new Date(insights.generated_at).toLocaleString() : 'Just now'}
        </small>
      </div>
    </div>
  );
};

export default AIInsightsPanel;
