import React, { useState, useEffect } from 'react';
import { advancedAnalyticsAPI } from '../../services/newEndpointsAPI';
import './AdvancedAnalytics.css';

const ABTestingManager = () => {
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [testResults, setTestResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_type: 'conversion',
    control_variant: '',
    test_variants: [''],
    traffic_split: {},
    start_date: '',
    end_date: '',
    goal_metric: 'conversion_rate',
  });

  useEffect(() => {
    fetchTests();
  }, []);

  const fetchTests = async () => {
    setLoading(true);
    try {
      const response = await advancedAnalyticsAPI.getABTests();
      setTests(response.data?.ab_tests || []);
    } catch (error) {
      console.error('Error fetching A/B tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTestResults = async (testId) => {
    try {
      const response = await advancedAnalyticsAPI.getABTestResults(testId);
      setTestResults(response.data);
    } catch (error) {
      console.error('Error fetching test results:', error);
    }
  };

  const handleCreateTest = async (e) => {
    e.preventDefault();

    try {
      // Calculate traffic split automatically if not set
      const variants = [formData.control_variant, ...formData.test_variants];
      const splitPercentage = 100 / variants.length;
      const trafficSplit = {};
      variants.forEach((variant) => {
        if (variant) trafficSplit[variant] = splitPercentage;
      });

      const testData = {
        ...formData,
        traffic_split: trafficSplit,
        test_variants: formData.test_variants.filter(v => v),
      };

      await advancedAnalyticsAPI.createABTest(testData);
      alert('A/B test created successfully!');
      setShowCreateForm(false);
      setFormData({
        name: '',
        description: '',
        test_type: 'conversion',
        control_variant: '',
        test_variants: [''],
        traffic_split: {},
        start_date: '',
        end_date: '',
        goal_metric: 'conversion_rate',
      });
      fetchTests();
    } catch (error) {
      console.error('Error creating A/B test:', error);
      alert('Failed to create A/B test. Please try again.');
    }
  };

  const handleUpdateTest = async (testId, status) => {
    try {
      await advancedAnalyticsAPI.updateABTestStatus(testId, status);
      alert(`Test ${status} successfully!`);
      fetchTests();
    } catch (error) {
      console.error('Error updating test:', error);
      alert('Failed to update test status.');
    }
  };

  const handleDeleteTest = async (testId) => {
    if (!window.confirm('Are you sure you want to delete this test?')) return;

    try {
      await advancedAnalyticsAPI.deleteABTest(testId);
      alert('Test deleted successfully!');
      fetchTests();
    } catch (error) {
      console.error('Error deleting test:', error);
      alert('Failed to delete test.');
    }
  };

  const addVariant = () => {
    setFormData({
      ...formData,
      test_variants: [...formData.test_variants, ''],
    });
  };

  const updateVariant = (index, value) => {
    const newVariants = [...formData.test_variants];
    newVariants[index] = value;
    setFormData({ ...formData, test_variants: newVariants });
  };

  const removeVariant = (index) => {
    const newVariants = formData.test_variants.filter((_, i) => i !== index);
    setFormData({ ...formData, test_variants: newVariants });
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: '#9e9e9e',
      running: '#4caf50',
      paused: '#ff9800',
      completed: '#2196f3',
      stopped: '#f44336',
    };
    return colors[status] || '#666';
  };

  const getStatusIcon = (status) => {
    const icons = {
      draft: '📝',
      running: '▶️',
      paused: '⏸️',
      completed: '✅',
      stopped: '⏹️',
    };
    return icons[status] || '❓';
  };

  if (loading) {
    return (
      <div className="ab-testing-manager">
        <div className="manager-header">
          <h3>🧪 A/B Testing Manager</h3>
        </div>
        <div className="loading-state">Loading A/B tests...</div>
      </div>
    );
  }

  return (
    <div className="ab-testing-manager">
      <div className="manager-header">
        <h3>🧪 A/B Testing Manager</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="create-test-btn"
        >
          {showCreateForm ? '✖ Cancel' : '+ Create New Test'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-test-form">
          <h4>Create New A/B Test</h4>
          <form onSubmit={handleCreateTest}>
            <div className="form-row">
              <div className="form-group">
                <label>Test Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="e.g., Homepage CTA Button Test"
                />
              </div>

              <div className="form-group">
                <label>Test Type *</label>
                <select
                  value={formData.test_type}
                  onChange={(e) => setFormData({ ...formData, test_type: e.target.value })}
                  required
                >
                  <option value="conversion">Conversion</option>
                  <option value="engagement">Engagement</option>
                  <option value="revenue">Revenue</option>
                  <option value="retention">Retention</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what you're testing and why..."
                rows="3"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Goal Metric *</label>
                <select
                  value={formData.goal_metric}
                  onChange={(e) => setFormData({ ...formData, goal_metric: e.target.value })}
                  required
                >
                  <option value="conversion_rate">Conversion Rate</option>
                  <option value="click_through_rate">Click-Through Rate</option>
                  <option value="revenue_per_user">Revenue per User</option>
                  <option value="engagement_time">Engagement Time</option>
                  <option value="retention_rate">Retention Rate</option>
                </select>
              </div>

              <div className="form-group">
                <label>Control Variant Name *</label>
                <input
                  type="text"
                  value={formData.control_variant}
                  onChange={(e) => setFormData({ ...formData, control_variant: e.target.value })}
                  required
                  placeholder="e.g., Original Blue Button"
                />
              </div>
            </div>

            <div className="variants-section">
              <label>Test Variants *</label>
              {formData.test_variants.map((variant, index) => (
                <div key={index} className="variant-input-row">
                  <input
                    type="text"
                    value={variant}
                    onChange={(e) => updateVariant(index, e.target.value)}
                    placeholder={`Variant ${index + 1} (e.g., Red Button)`}
                    required
                  />
                  {formData.test_variants.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeVariant(index)}
                      className="remove-variant-btn"
                    >
                      ✖
                    </button>
                  )}
                </div>
              ))}
              <button type="button" onClick={addVariant} className="add-variant-btn">
                + Add Variant
              </button>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>End Date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="submit-btn">
                Create Test
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="tests-list">
        {tests.length === 0 ? (
          <div className="empty-state">
            No A/B tests yet. Create your first test to start optimizing!
          </div>
        ) : (
          tests.map((test) => (
            <div key={test.id} className="test-card">
              <div className="test-header">
                <div className="test-title-section">
                  <h4>{test.name}</h4>
                  <span
                    className="status-badge"
                    style={{ background: getStatusColor(test.status) }}
                  >
                    {getStatusIcon(test.status)} {test.status}
                  </span>
                </div>
                <div className="test-actions">
                  {test.status === 'draft' && (
                    <button
                      onClick={() => handleUpdateTest(test.id, 'running')}
                      className="action-btn start-btn"
                    >
                      ▶️ Start
                    </button>
                  )}
                  {test.status === 'running' && (
                    <>
                      <button
                        onClick={() => handleUpdateTest(test.id, 'paused')}
                        className="action-btn pause-btn"
                      >
                        ⏸️ Pause
                      </button>
                      <button
                        onClick={() => handleUpdateTest(test.id, 'completed')}
                        className="action-btn complete-btn"
                      >
                        ✅ Complete
                      </button>
                    </>
                  )}
                  {test.status === 'paused' && (
                    <button
                      onClick={() => handleUpdateTest(test.id, 'running')}
                      className="action-btn start-btn"
                    >
                      ▶️ Resume
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setSelectedTest(selectedTest === test.id ? null : test.id);
                      if (selectedTest !== test.id) fetchTestResults(test.id);
                    }}
                    className="action-btn results-btn"
                  >
                    📊 Results
                  </button>
                  <button
                    onClick={() => handleDeleteTest(test.id)}
                    className="action-btn delete-btn"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              {test.description && <p className="test-description">{test.description}</p>}

              <div className="test-metadata">
                <div className="metadata-item">
                  <strong>Type:</strong> {test.test_type}
                </div>
                <div className="metadata-item">
                  <strong>Goal:</strong> {test.goal_metric?.replace('_', ' ')}
                </div>
                <div className="metadata-item">
                  <strong>Variants:</strong> {test.variants?.length || 0}
                </div>
                {test.start_date && (
                  <div className="metadata-item">
                    <strong>Started:</strong> {new Date(test.start_date).toLocaleDateString()}
                  </div>
                )}
              </div>

              {selectedTest === test.id && testResults && (
                <div className="test-results">
                  <h4>📊 Test Results</h4>

                  <div className="results-summary">
                    <div className="summary-stat">
                      <div className="stat-label">Total Participants</div>
                      <div className="stat-value">{testResults.total_participants?.toLocaleString()}</div>
                    </div>
                    <div className="summary-stat">
                      <div className="stat-label">Confidence Level</div>
                      <div className="stat-value">
                        {testResults.confidence_level ? `${(testResults.confidence_level * 100).toFixed(1)}%` : 'N/A'}
                      </div>
                    </div>
                    <div className="summary-stat">
                      <div className="stat-label">Winner</div>
                      <div className="stat-value" style={{ color: '#4caf50' }}>
                        {testResults.winner || 'TBD'}
                      </div>
                    </div>
                  </div>

                  <div className="variants-results">
                    {testResults.variant_results?.map((variant, index) => (
                      <div
                        key={index}
                        className="variant-result"
                        style={{
                          borderLeft: variant.is_winner ? '4px solid #4caf50' : '4px solid #e0e0e0',
                        }}
                      >
                        <div className="variant-name">
                          {variant.variant_name}
                          {variant.is_winner && <span className="winner-badge">🏆 Winner</span>}
                        </div>
                        <div className="variant-stats">
                          <div className="stat">
                            <span>Participants:</span> {variant.participants}
                          </div>
                          <div className="stat">
                            <span>Conversions:</span> {variant.conversions}
                          </div>
                          <div className="stat">
                            <span>Rate:</span> {(variant.conversion_rate * 100).toFixed(2)}%
                          </div>
                          {variant.improvement !== undefined && variant.improvement !== 0 && (
                            <div className="stat">
                              <span>vs Control:</span>
                              <span style={{ color: variant.improvement > 0 ? '#4caf50' : '#f44336' }}>
                                {variant.improvement > 0 ? '+' : ''}{(variant.improvement * 100).toFixed(2)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {testResults.recommendation && (
                    <div className="test-recommendation">
                      <strong>💡 Recommendation:</strong> {testResults.recommendation}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ABTestingManager;
