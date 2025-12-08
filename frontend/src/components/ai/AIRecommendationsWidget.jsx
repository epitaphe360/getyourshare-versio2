import React, { useState, useEffect } from 'react';
import { aiAPI } from '../../services/newEndpointsAPI';
import './AIRecommendations.css';

const AIRecommendationsWidget = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('for-you');

  useEffect(() => {
    fetchRecommendations(activeTab);
  }, [activeTab]);

  const fetchRecommendations = async (type) => {
    setLoading(true);
    try {
      let response;
      switch (type) {
        case 'for-you':
          response = await aiAPI.getRecommendationsForYou();
          break;
        case 'trending':
          response = await aiAPI.getTrendingProducts();
          break;
        case 'hybrid':
          response = await aiAPI.getHybridRecommendations();
          break;
        default:
          response = await aiAPI.getRecommendationsForYou();
      }

      setRecommendations(response.data?.recommendations || response.data?.products || []);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-recommendations-widget">
      <div className="widget-header">
        <h3>🤖 AI Recommendations</h3>
        <div className="tabs">
          <button
            className={activeTab === 'for-you' ? 'active' : ''}
            onClick={() => setActiveTab('for-you')}
          >
            For You
          </button>
          <button
            className={activeTab === 'trending' ? 'active' : ''}
            onClick={() => setActiveTab('trending')}
          >
            Trending
          </button>
          <button
            className={activeTab === 'hybrid' ? 'active' : ''}
            onClick={() => setActiveTab('hybrid')}
          >
            Hybrid
          </button>
        </div>
      </div>

      <div className="recommendations-list">
        {loading ? (
          <div className="loading">Loading recommendations...</div>
        ) : recommendations.length === 0 ? (
          <div className="empty-state">No recommendations available</div>
        ) : (
          recommendations.map((item, index) => (
            <div key={item.id || index} className="recommendation-card">
              <div className="product-image">
                {item.image_url || item.image ? (
                  <img src={item.image_url || item.image} alt={item.name || item.title} />
                ) : (
                  <div className="placeholder-image">📦</div>
                )}
              </div>
              <div className="product-info">
                <h4>{item.name || item.title}</h4>
                <p className="price">{item.price} MAD</p>
                {item.score && (
                  <div className="score">
                    Score: {(item.score * 100).toFixed(0)}%
                  </div>
                )}
                {item.reason && (
                  <p className="reason">{item.reason}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AIRecommendationsWidget;
