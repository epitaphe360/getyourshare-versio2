import React, { useState, useEffect } from 'react';
import { advancedAnalyticsAPI } from '../../services/newEndpointsAPI';
import './AdvancedAnalytics.css';

const RFMSegmentationView = () => {
  const [rfmData, setRfmData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSegment, setSelectedSegment] = useState(null);

  useEffect(() => {
    fetchRFMAnalysis();
  }, []);

  const fetchRFMAnalysis = async () => {
    setLoading(true);
    try {
      const response = await advancedAnalyticsAPI.getRFMAnalysis();
      setRfmData(response.data);
    } catch (error) {
      console.error('Error fetching RFM analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSegmentColor = (segmentName) => {
    const colors = {
      'Champions': '#4caf50',
      'Loyal Customers': '#8bc34a',
      'Potential Loyalists': '#03a9f4',
      'Recent Customers': '#00bcd4',
      'Promising': '#9c27b0',
      'Need Attention': '#ffc107',
      'About to Sleep': '#ff9800',
      'At Risk': '#ff5722',
      'Cannot Lose Them': '#f44336',
      'Hibernating': '#9e9e9e',
      'Lost': '#607d8b',
    };
    return colors[segmentName] || '#999';
  };

  const getSegmentIcon = (segmentName) => {
    const icons = {
      'Champions': '👑',
      'Loyal Customers': '⭐',
      'Potential Loyalists': '🌟',
      'Recent Customers': '🆕',
      'Promising': '💎',
      'Need Attention': '⚠️',
      'About to Sleep': '😴',
      'At Risk': '🚨',
      'Cannot Lose Them': '🔴',
      'Hibernating': '💤',
      'Lost': '❌',
    };
    return icons[segmentName] || '📊';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <div className="rfm-segmentation-view">
        <div className="view-header">
          <h3>🎯 RFM Segmentation</h3>
        </div>
        <div className="loading-state">Analyzing customer segments...</div>
      </div>
    );
  }

  if (!rfmData || !rfmData.segments) {
    return (
      <div className="rfm-segmentation-view">
        <div className="view-header">
          <h3>🎯 RFM Segmentation</h3>
        </div>
        <div className="empty-state">No RFM data available</div>
      </div>
    );
  }

  return (
    <div className="rfm-segmentation-view">
      <div className="view-header">
        <h3>🎯 RFM Segmentation</h3>
        <button onClick={fetchRFMAnalysis} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="rfm-info-box">
        <h4>What is RFM Analysis?</h4>
        <p>
          RFM (Recency, Frequency, Monetary) analysis segments customers based on:
        </p>
        <ul>
          <li><strong>Recency:</strong> How recently they made a purchase</li>
          <li><strong>Frequency:</strong> How often they make purchases</li>
          <li><strong>Monetary:</strong> How much money they spend</li>
        </ul>
      </div>

      {/* Summary Stats */}
      <div className="rfm-summary">
        <div className="summary-card">
          <div className="summary-label">Total Customers</div>
          <div className="summary-value">
            {rfmData.total_customers?.toLocaleString() || 0}
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Total Revenue</div>
          <div className="summary-value">
            {formatCurrency(rfmData.total_revenue || 0)}
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-label">Avg Customer Value</div>
          <div className="summary-value">
            {formatCurrency(rfmData.avg_customer_value || 0)}
          </div>
        </div>
      </div>

      {/* Segments Grid */}
      <div className="segments-grid">
        {rfmData.segments.map((segment, index) => (
          <div
            key={index}
            className="segment-card"
            style={{ borderLeft: `4px solid ${getSegmentColor(segment.segment_name)}` }}
            onClick={() => setSelectedSegment(selectedSegment === segment.segment_name ? null : segment.segment_name)}
          >
            <div className="segment-header">
              <span className="segment-icon">{getSegmentIcon(segment.segment_name)}</span>
              <h4>{segment.segment_name}</h4>
            </div>

            <div className="segment-stats">
              <div className="stat-row">
                <span className="stat-label">Customers:</span>
                <span className="stat-value">{segment.customer_count?.toLocaleString()}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">% of Total:</span>
                <span className="stat-value">{segment.percentage?.toFixed(1)}%</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Avg Revenue:</span>
                <span className="stat-value">{formatCurrency(segment.avg_revenue || 0)}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Total Revenue:</span>
                <span className="stat-value" style={{ fontWeight: 'bold', color: '#1976d2' }}>
                  {formatCurrency(segment.total_revenue || 0)}
                </span>
              </div>
            </div>

            {segment.description && (
              <div className="segment-description">
                <p>{segment.description}</p>
              </div>
            )}

            {segment.recommended_actions && segment.recommended_actions.length > 0 && (
              <div className="segment-actions">
                <strong>Recommended Actions:</strong>
                <ul>
                  {segment.recommended_actions.map((action, idx) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedSegment === segment.segment_name && segment.rfm_scores && (
              <div className="segment-details">
                <div className="rfm-scores">
                  <div className="score-item">
                    <span className="score-label">R Score:</span>
                    <span className="score-value">{segment.rfm_scores.recency}/5</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">F Score:</span>
                    <span className="score-value">{segment.rfm_scores.frequency}/5</span>
                  </div>
                  <div className="score-item">
                    <span className="score-label">M Score:</span>
                    <span className="score-value">{segment.rfm_scores.monetary}/5</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* RFM Matrix Visualization */}
      {rfmData.matrix && (
        <div className="rfm-matrix-section">
          <h4>📊 RFM Matrix</h4>
          <div className="matrix-container">
            <div className="matrix-grid">
              {rfmData.matrix.map((row, rowIndex) => (
                <div key={rowIndex} className="matrix-row">
                  {row.map((cell, colIndex) => (
                    <div
                      key={colIndex}
                      className="matrix-cell"
                      style={{
                        background: getSegmentColor(cell.segment),
                        opacity: cell.count > 0 ? 1 : 0.3,
                      }}
                      title={`${cell.segment}: ${cell.count} customers`}
                    >
                      <div className="cell-count">{cell.count}</div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
            <div className="matrix-labels">
              <div className="x-label">Frequency →</div>
              <div className="y-label">← Recency</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RFMSegmentationView;
