import React, { useState, useEffect } from 'react';
import { advancedAnalyticsAPI } from '../../services/newEndpointsAPI';
import './AdvancedAnalytics.css';

const CustomerSegmentsPanel = () => {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [segmentCustomers, setSegmentCustomers] = useState([]);
  const [loadingCustomers, setLoadingCustomers] = useState(false);

  useEffect(() => {
    fetchSegments();
  }, []);

  const fetchSegments = async () => {
    setLoading(true);
    try {
      const response = await advancedAnalyticsAPI.getCustomerSegments();
      setSegments(response.data?.segments || []);
    } catch (error) {
      console.error('Error fetching customer segments:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSegmentCustomers = async (segmentId) => {
    setLoadingCustomers(true);
    try {
      const response = await advancedAnalyticsAPI.getSegmentCustomers(segmentId);
      setSegmentCustomers(response.data?.customers || []);
    } catch (error) {
      console.error('Error fetching segment customers:', error);
    } finally {
      setLoadingCustomers(false);
    }
  };

  const handleSegmentClick = (segment) => {
    if (selectedSegment?.id === segment.id) {
      setSelectedSegment(null);
      setSegmentCustomers([]);
    } else {
      setSelectedSegment(segment);
      fetchSegmentCustomers(segment.id);
    }
  };

  const getSegmentColor = (type) => {
    const colors = {
      'vip': '#ffd700',
      'high_value': '#4caf50',
      'active': '#2196f3',
      'promising': '#9c27b0',
      'dormant': '#ff9800',
      'at_risk': '#f44336',
      'lost': '#9e9e9e',
      'new': '#00bcd4',
    };
    return colors[type] || '#666';
  };

  const getSegmentIcon = (type) => {
    const icons = {
      'vip': '👑',
      'high_value': '💎',
      'active': '✅',
      'promising': '🌟',
      'dormant': '😴',
      'at_risk': '⚠️',
      'lost': '❌',
      'new': '🆕',
    };
    return icons[type] || '👥';
  };

  if (loading) {
    return (
      <div className="customer-segments-panel">
        <div className="panel-header">
          <h3>👥 Customer Segments</h3>
        </div>
        <div className="loading-state">Loading customer segments...</div>
      </div>
    );
  }

  return (
    <div className="customer-segments-panel">
      <div className="panel-header">
        <h3>👥 Customer Segments</h3>
        <button onClick={fetchSegments} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="segments-overview">
        <div className="overview-stats">
          <div className="stat-card">
            <div className="stat-label">Total Segments</div>
            <div className="stat-value">{segments.length}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Customers</div>
            <div className="stat-value">
              {segments.reduce((sum, seg) => sum + (seg.customer_count || 0), 0).toLocaleString()}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Revenue</div>
            <div className="stat-value">
              ${segments.reduce((sum, seg) => sum + (seg.total_revenue || 0), 0).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      <div className="segments-list">
        {segments.map((segment) => (
          <div key={segment.id} className="segment-item-panel">
            <div
              className="segment-summary"
              onClick={() => handleSegmentClick(segment)}
              style={{ cursor: 'pointer' }}
            >
              <div className="segment-info">
                <div className="segment-title">
                  <span className="segment-icon" style={{ fontSize: '24px' }}>
                    {getSegmentIcon(segment.type)}
                  </span>
                  <div>
                    <h4>{segment.name}</h4>
                    <p className="segment-subtitle">{segment.description}</p>
                  </div>
                </div>

                <div
                  className="segment-badge"
                  style={{ background: getSegmentColor(segment.type) }}
                >
                  {segment.type?.replace('_', ' ').toUpperCase()}
                </div>
              </div>

              <div className="segment-metrics">
                <div className="metric">
                  <div className="metric-label">Customers</div>
                  <div className="metric-value">{segment.customer_count?.toLocaleString()}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Avg Order Value</div>
                  <div className="metric-value">${segment.avg_order_value?.toFixed(2)}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Total Revenue</div>
                  <div className="metric-value">${segment.total_revenue?.toLocaleString()}</div>
                </div>
                <div className="metric">
                  <div className="metric-label">Lifetime Value</div>
                  <div className="metric-value">${segment.avg_lifetime_value?.toFixed(2)}</div>
                </div>
              </div>

              {segment.criteria && (
                <div className="segment-criteria">
                  <strong>Criteria:</strong>
                  <ul>
                    {Object.entries(segment.criteria).map(([key, value]) => (
                      <li key={key}>
                        <span className="criteria-key">{key.replace('_', ' ')}:</span>{' '}
                        <span className="criteria-value">{value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {selectedSegment?.id === segment.id && (
              <div className="segment-details-panel">
                <div className="details-header">
                  <h4>Segment Customers</h4>
                  {segment.customer_count && (
                    <span className="customer-count-badge">
                      {segment.customer_count} total
                    </span>
                  )}
                </div>

                {loadingCustomers ? (
                  <div className="loading-state">Loading customers...</div>
                ) : segmentCustomers.length === 0 ? (
                  <div className="empty-state">No customers in this segment</div>
                ) : (
                  <div className="customers-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Customer</th>
                          <th>Email</th>
                          <th>Orders</th>
                          <th>Total Spent</th>
                          <th>Last Order</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {segmentCustomers.slice(0, 10).map((customer) => (
                          <tr key={customer.id}>
                            <td>{customer.name || 'N/A'}</td>
                            <td>{customer.email}</td>
                            <td>{customer.order_count || 0}</td>
                            <td>${customer.total_spent?.toFixed(2) || '0.00'}</td>
                            <td>
                              {customer.last_order_date
                                ? new Date(customer.last_order_date).toLocaleDateString()
                                : 'Never'}
                            </td>
                            <td>
                              <span
                                className={`status-badge status-${customer.status?.toLowerCase()}`}
                              >
                                {customer.status || 'Active'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {segmentCustomers.length > 10 && (
                      <div className="table-footer">
                        Showing 10 of {segmentCustomers.length} customers
                      </div>
                    )}
                  </div>
                )}

                {segment.recommended_actions && segment.recommended_actions.length > 0 && (
                  <div className="recommended-actions">
                    <h4>💡 Recommended Actions</h4>
                    <ul>
                      {segment.recommended_actions.map((action, index) => (
                        <li key={index}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {segments.length === 0 && (
        <div className="empty-state">
          No customer segments available. Segments will be created automatically as customers make purchases.
        </div>
      )}
    </div>
  );
};

export default CustomerSegmentsPanel;
