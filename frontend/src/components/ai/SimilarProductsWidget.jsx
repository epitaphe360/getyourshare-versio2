import React, { useState, useEffect } from 'react';
import { aiAPI } from '../../services/newEndpointsAPI';
import './AIRecommendations.css';

const SimilarProductsWidget = ({ productId, productName }) => {
  const [similarProducts, setSimilarProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (productId) {
      fetchSimilarProducts();
    }
  }, [productId]);

  const fetchSimilarProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiAPI.getSimilarProducts(productId);
      setSimilarProducts(response.data?.similar_products || []);
    } catch (err) {
      console.error('Error fetching similar products:', err);
      setError('Failed to load similar products');
    } finally {
      setLoading(false);
    }
  };

  const handleProductClick = (product) => {
    // Navigate to product detail page
    window.location.href = `/products/${product.id}`;
  };

  if (!productId) {
    return null;
  }

  if (loading) {
    return (
      <div className="ai-recommendations-widget">
        <div className="widget-header">
          <h3>🔍 Similar Products</h3>
        </div>
        <div className="loading">Loading similar products...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ai-recommendations-widget">
        <div className="widget-header">
          <h3>🔍 Similar Products</h3>
        </div>
        <div className="empty-state">{error}</div>
      </div>
    );
  }

  if (similarProducts.length === 0) {
    return (
      <div className="ai-recommendations-widget">
        <div className="widget-header">
          <h3>🔍 Similar Products</h3>
        </div>
        <div className="empty-state">No similar products found</div>
      </div>
    );
  }

  return (
    <div className="ai-recommendations-widget">
      <div className="widget-header">
        <h3>🔍 Similar Products</h3>
        {productName && (
          <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
            Based on "{productName}"
          </p>
        )}
      </div>

      <div className="recommendations-list">
        {similarProducts.map((product) => (
          <div
            key={product.id}
            className="recommendation-card"
            onClick={() => handleProductClick(product)}
          >
            <div className="product-image">
              {product.image_url ? (
                <img src={product.image_url} alt={product.name} />
              ) : (
                <div className="placeholder-image">📦</div>
              )}
            </div>

            <div className="product-info">
              <h4>{product.name}</h4>

              {product.description && (
                <p style={{
                  fontSize: '13px',
                  color: '#666',
                  margin: '5px 0',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {product.description}
                </p>
              )}

              <div className="price">${product.price?.toFixed(2)}</div>

              {product.similarity_score && (
                <div className="score">
                  Match: {(product.similarity_score * 100).toFixed(0)}%
                </div>
              )}

              {product.match_reason && (
                <div className="reason">
                  {product.match_reason}
                </div>
              )}

              {product.category && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  color: '#999',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}>
                  <span>📂</span>
                  <span>{product.category}</span>
                </div>
              )}

              {product.rating && (
                <div style={{
                  marginTop: '5px',
                  fontSize: '12px',
                  color: '#ff9800',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}>
                  <span>⭐</span>
                  <span>{product.rating.toFixed(1)} ({product.reviews_count || 0} reviews)</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: '15px',
        textAlign: 'center',
        fontSize: '12px',
        color: '#999'
      }}>
        Powered by AI · {similarProducts.length} similar {similarProducts.length === 1 ? 'product' : 'products'} found
      </div>
    </div>
  );
};

export default SimilarProductsWidget;
