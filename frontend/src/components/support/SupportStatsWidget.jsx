import React, { useState, useEffect } from 'react';
import { supportAPI } from '../../services/newEndpointsAPI';
import './Support.css';

const SupportStatsWidget = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('week'); // week, month, all

  useEffect(() => {
    fetchStats();
  }, [timeframe]);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await supportAPI.getStats({ timeframe });
      setStats(response.data?.stats || null);
    } catch (error) {
      console.error('Error fetching support stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getResponseTimeColor = (hours) => {
    if (hours < 1) return '#4caf50';
    if (hours < 4) return '#8bc34a';
    if (hours < 12) return '#ff9800';
    return '#f44336';
  };

  const getSatisfactionColor = (percentage) => {
    if (percentage >= 90) return '#4caf50';
    if (percentage >= 75) return '#8bc34a';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <div className="support-stats-widget">
        <div className="widget-header">
          <h3>Support Statistics</h3>
        </div>
        <div className="loading-state">Loading statistics...</div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="support-stats-widget">
        <div className="widget-header">
          <h3>Support Statistics</h3>
        </div>
        <div className="empty-state">No statistics available</div>
      </div>
    );
  }

  return (
    <div className="support-stats-widget">
      <div className="widget-header">
        <h3>📊 Support Statistics</h3>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          className="timeframe-select"
        >
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="all">All Time</option>
        </select>
      </div>

      {/* Overview Stats */}
      <div className="stats-grid">
        <div className="stat-card total-tickets">
          <div className="stat-icon">🎫</div>
          <div className="stat-content">
            <div className="stat-value">{stats.total_tickets || 0}</div>
            <div className="stat-label">Total Tickets</div>
          </div>
        </div>

        <div className="stat-card open-tickets">
          <div className="stat-icon">📬</div>
          <div className="stat-content">
            <div className="stat-value">{stats.open_tickets || 0}</div>
            <div className="stat-label">Open Tickets</div>
          </div>
        </div>

        <div className="stat-card resolved-tickets">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.resolved_tickets || 0}</div>
            <div className="stat-label">Resolved</div>
          </div>
        </div>

        <div className="stat-card resolution-rate">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-value">
              {stats.resolution_rate !== undefined
                ? `${stats.resolution_rate.toFixed(1)}%`
                : 'N/A'}
            </div>
            <div className="stat-label">Resolution Rate</div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="performance-section">
        <h4>Performance Metrics</h4>

        <div className="metric-row">
          <span className="metric-label">Avg Response Time</span>
          <span
            className="metric-value"
            style={{
              color: getResponseTimeColor(stats.avg_response_time_hours || 0),
            }}
          >
            {stats.avg_response_time_hours !== undefined
              ? `${stats.avg_response_time_hours.toFixed(1)}h`
              : 'N/A'}
          </span>
        </div>

        <div className="metric-row">
          <span className="metric-label">Avg Resolution Time</span>
          <span className="metric-value">
            {stats.avg_resolution_time_hours !== undefined
              ? `${stats.avg_resolution_time_hours.toFixed(1)}h`
              : 'N/A'}
          </span>
        </div>

        <div className="metric-row">
          <span className="metric-label">Customer Satisfaction</span>
          <span
            className="metric-value"
            style={{
              color: getSatisfactionColor(stats.customer_satisfaction_percentage || 0),
            }}
          >
            {stats.customer_satisfaction_percentage !== undefined
              ? `${stats.customer_satisfaction_percentage.toFixed(1)}%`
              : 'N/A'}
          </span>
        </div>

        <div className="metric-row">
          <span className="metric-label">First Contact Resolution</span>
          <span className="metric-value">
            {stats.first_contact_resolution_percentage !== undefined
              ? `${stats.first_contact_resolution_percentage.toFixed(1)}%`
              : 'N/A'}
          </span>
        </div>
      </div>

      {/* Status Breakdown */}
      {stats.status_breakdown && (
        <div className="status-breakdown">
          <h4>Status Breakdown</h4>
          <div className="breakdown-chart">
            {Object.entries(stats.status_breakdown).map(([status, count]) => (
              <div key={status} className="breakdown-item">
                <div className="breakdown-label">
                  {status.replace('_', ' ')}
                </div>
                <div className="breakdown-bar">
                  <div
                    className="breakdown-fill"
                    style={{
                      width: `${(count / stats.total_tickets) * 100}%`,
                      background: getStatusColor(status),
                    }}
                  ></div>
                </div>
                <div className="breakdown-count">{count}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Priority Breakdown */}
      {stats.priority_breakdown && (
        <div className="priority-breakdown">
          <h4>Priority Breakdown</h4>
          <div className="priority-grid">
            {Object.entries(stats.priority_breakdown).map(([priority, count]) => (
              <div key={priority} className="priority-item">
                <div className="priority-count">{count}</div>
                <div className="priority-label">{priority}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Categories */}
      {stats.top_categories && stats.top_categories.length > 0 && (
        <div className="top-categories">
          <h4>Top Categories</h4>
          <div className="categories-list">
            {stats.top_categories.map((category, index) => (
              <div key={index} className="category-item">
                <span className="category-rank">#{index + 1}</span>
                <span className="category-name">{category.category}</span>
                <span className="category-count">{category.count} tickets</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Performance (if applicable) */}
      {stats.agent_performance && stats.agent_performance.length > 0 && (
        <div className="agent-performance">
          <h4>👨‍💼 Agent Performance</h4>
          <div className="agents-list">
            {stats.agent_performance.map((agent, index) => (
              <div key={index} className="agent-item">
                <div className="agent-info">
                  <div className="agent-avatar">
                    {agent.name?.charAt(0).toUpperCase() || '?'}
                  </div>
                  <div>
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-stats-row">
                      <span>{agent.tickets_handled} tickets</span>
                      <span>·</span>
                      <span>{agent.avg_rating?.toFixed(1)} ⭐</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="stats-footer">
        <button onClick={fetchStats} className="refresh-stats-btn">
          🔄 Refresh
        </button>
        <small>
          Last updated: {new Date().toLocaleTimeString()}
        </small>
      </div>
    </div>
  );
};

const getStatusColor = (status) => {
  const colors = {
    open: '#2196f3',
    in_progress: '#ff9800',
    resolved: '#4caf50',
    closed: '#9e9e9e',
  };
  return colors[status] || '#666';
};

export default SupportStatsWidget;
