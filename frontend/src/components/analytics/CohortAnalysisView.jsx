import React, { useState, useEffect } from 'react';
import { advancedAnalyticsAPI } from '../../services/newEndpointsAPI';
import './AdvancedAnalytics.css';

const CohortAnalysisView = () => {
  const [cohorts, setCohorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [metric, setMetric] = useState('retention');
  const [period, setPeriod] = useState('monthly');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    // Set default dates (last 6 months)
    const end = new Date();
    const start = new Date();
    start.setMonth(start.getMonth() - 6);

    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchCohortAnalysis();
    }
  }, [metric, period, startDate, endDate]);

  const fetchCohortAnalysis = async () => {
    setLoading(true);
    try {
      const response = await advancedAnalyticsAPI.getCohortAnalysis({
        start_date: startDate,
        end_date: endDate,
        metric: metric,
        period: period,
      });
      setCohorts(response.data?.cohorts || []);
    } catch (error) {
      console.error('Error fetching cohort analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const getColorForValue = (value, maxValue) => {
    if (!value || value === 0) return '#f5f5f5';
    const intensity = (value / maxValue) * 100;
    if (intensity >= 80) return '#4caf50';
    if (intensity >= 60) return '#8bc34a';
    if (intensity >= 40) return '#ffc107';
    if (intensity >= 20) return '#ff9800';
    return '#f44336';
  };

  const formatValue = (value, metricType) => {
    if (value === null || value === undefined) return '-';

    switch (metricType) {
      case 'retention':
        return `${value.toFixed(1)}%`;
      case 'revenue':
        return `$${value.toLocaleString()}`;
      case 'engagement':
        return value.toFixed(1);
      default:
        return value;
    }
  };

  const calculateMaxValue = () => {
    if (cohorts.length === 0) return 100;
    let max = 0;
    cohorts.forEach(cohort => {
      cohort.periods.forEach(period => {
        if (period.value > max) max = period.value;
      });
    });
    return max;
  };

  if (loading && cohorts.length === 0) {
    return (
      <div className="cohort-analysis-view">
        <div className="view-header">
          <h3>📊 Cohort Analysis</h3>
        </div>
        <div className="loading-state">Loading cohort data...</div>
      </div>
    );
  }

  const maxValue = calculateMaxValue();

  return (
    <div className="cohort-analysis-view">
      <div className="view-header">
        <h3>📊 Cohort Analysis</h3>
        <div className="header-actions">
          <button onClick={fetchCohortAnalysis} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label>Metric</label>
          <select value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="retention">Retention Rate</option>
            <option value="revenue">Revenue per Cohort</option>
            <option value="engagement">Engagement Score</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Period</label>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>

      {cohorts.length === 0 ? (
        <div className="empty-state">
          No cohort data available for the selected period
        </div>
      ) : (
        <>
          <div className="cohort-table-container">
            <table className="cohort-table">
              <thead>
                <tr>
                  <th>Cohort</th>
                  <th>Size</th>
                  {cohorts[0]?.periods.map((_, index) => (
                    <th key={index}>Period {index}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {cohorts.map((cohort, cohortIndex) => (
                  <tr key={cohortIndex}>
                    <td className="cohort-name">{cohort.cohort_name}</td>
                    <td className="cohort-size">{cohort.cohort_size}</td>
                    {cohort.periods.map((period, periodIndex) => (
                      <td
                        key={periodIndex}
                        className="cohort-cell"
                        style={{
                          background: getColorForValue(period.value, maxValue),
                          color: period.value > maxValue * 0.5 ? 'white' : '#333',
                          fontWeight: period.value > maxValue * 0.7 ? 'bold' : 'normal',
                        }}
                      >
                        {formatValue(period.value, metric)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="cohort-legend">
            <h4>Color Legend</h4>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#4caf50' }}></span>
                <span>Excellent (80-100%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#8bc34a' }}></span>
                <span>Good (60-80%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#ffc107' }}></span>
                <span>Average (40-60%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#ff9800' }}></span>
                <span>Below Average (20-40%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#f44336' }}></span>
                <span>Poor (&lt;20%)</span>
              </div>
            </div>
          </div>

          <div className="cohort-insights">
            <h4>📈 Key Insights</h4>
            <div className="insights-grid">
              <div className="insight-card">
                <div className="insight-label">Best Performing Cohort</div>
                <div className="insight-value">
                  {cohorts.reduce((best, cohort) => {
                    const avgValue = cohort.periods.reduce((sum, p) => sum + p.value, 0) / cohort.periods.length;
                    return avgValue > (best.avgValue || 0) ? { name: cohort.cohort_name, avgValue } : best;
                  }, {}).name || 'N/A'}
                </div>
              </div>

              <div className="insight-card">
                <div className="insight-label">Total Cohorts</div>
                <div className="insight-value">{cohorts.length}</div>
              </div>

              <div className="insight-card">
                <div className="insight-label">Total Users</div>
                <div className="insight-value">
                  {cohorts.reduce((sum, cohort) => sum + cohort.cohort_size, 0).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CohortAnalysisView;
