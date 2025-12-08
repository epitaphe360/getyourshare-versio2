import React, { useState, useEffect } from 'react';
import { ecommerceAPI } from '../../services/newEndpointsAPI';
import './Integrations.css';

const EcommerceIntegrationsPanel = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [syncing, setSyncing] = useState(false);

  // Form states for different platforms
  const [shopifyData, setShopifyData] = useState({ shop_url: '', access_token: '' });
  const [woocommerceData, setWoocommerceData] = useState({ shop_url: '', consumer_key: '', consumer_secret: '' });
  const [prestashopData, setPrestashopData] = useState({ shop_url: '', api_key: '' });

  const platforms = [
    {
      id: 'shopify',
      name: 'Shopify',
      icon: '🛍️',
      description: 'Connect your Shopify store to sync products and orders',
      color: '#96bf48',
    },
    {
      id: 'woocommerce',
      name: 'WooCommerce',
      icon: '🛒',
      description: 'Integrate with your WooCommerce powered WordPress site',
      color: '#96588a',
    },
    {
      id: 'prestashop',
      name: 'PrestaShop',
      icon: '🏪',
      description: 'Sync with your PrestaShop online store',
      color: '#df0067',
    },
  ];

  useEffect(() => {
    fetchConnectedPlatforms();
  }, []);

  const fetchConnectedPlatforms = async () => {
    setLoading(true);
    try {
      const response = await ecommerceAPI.getConnectedPlatforms();
      setConnectedPlatforms(response.data?.platforms || []);
    } catch (error) {
      console.error('Error fetching connected platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectPlatform = (platform) => {
    setSelectedPlatform(platform);
    setShowConnectModal(true);
  };

  const handleSubmitConnection = async (e) => {
    e.preventDefault();

    try {
      let response;

      switch (selectedPlatform.id) {
        case 'shopify':
          response = await ecommerceAPI.connectShopify(shopifyData.shop_url, shopifyData.access_token);
          break;
        case 'woocommerce':
          response = await ecommerceAPI.connectWooCommerce(
            woocommerceData.shop_url,
            woocommerceData.consumer_key,
            woocommerceData.consumer_secret
          );
          break;
        case 'prestashop':
          response = await ecommerceAPI.connectPrestaShop(prestashopData.shop_url, prestashopData.api_key);
          break;
        default:
          throw new Error('Unknown platform');
      }

      alert(`Successfully connected to ${selectedPlatform.name}!`);
      setShowConnectModal(false);
      fetchConnectedPlatforms();

      // Reset forms
      setShopifyData({ shop_url: '', access_token: '' });
      setWoocommerceData({ shop_url: '', consumer_key: '', consumer_secret: '' });
      setPrestashopData({ shop_url: '', api_key: '' });
    } catch (error) {
      console.error('Error connecting platform:', error);
      alert(`Failed to connect to ${selectedPlatform.name}. Please check your credentials and try again.`);
    }
  };

  const handleSyncProducts = async (platformId) => {
    setSyncing(true);
    try {
      switch (platformId) {
        case 'shopify':
          await ecommerceAPI.syncShopifyProducts();
          break;
        case 'woocommerce':
          await ecommerceAPI.syncWooCommerceProducts();
          break;
        case 'prestashop':
          await ecommerceAPI.syncPrestaShopProducts();
          break;
        default:
          throw new Error('Unknown platform');
      }

      alert('Product sync started successfully! This may take a few minutes.');
      fetchConnectedPlatforms();
    } catch (error) {
      console.error('Error syncing products:', error);
      alert('Failed to sync products. Please try again.');
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = async (platformId) => {
    if (!window.confirm(`Are you sure you want to disconnect ${platformId}?`)) return;

    try {
      await ecommerceAPI.disconnectPlatform(platformId);
      alert(`Successfully disconnected from ${platformId}`);
      fetchConnectedPlatforms();
    } catch (error) {
      console.error('Error disconnecting platform:', error);
      alert('Failed to disconnect platform.');
    }
  };

  const isConnected = (platformId) => {
    return connectedPlatforms.some(p => p.platform_id === platformId);
  };

  const getConnectedPlatform = (platformId) => {
    return connectedPlatforms.find(p => p.platform_id === platformId);
  };

  if (loading) {
    return (
      <div className="ecommerce-integrations-panel">
        <div className="panel-header">
          <h3>E-commerce Integrations</h3>
        </div>
        <div className="loading-state">Loading integrations...</div>
      </div>
    );
  }

  return (
    <div className="ecommerce-integrations-panel">
      <div className="panel-header">
        <h3>🏬 E-commerce Integrations</h3>
        <button onClick={fetchConnectedPlatforms} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="integrations-info-box">
        <h4>Connect Your Store</h4>
        <p>
          Integrate your e-commerce platform to automatically sync products, manage inventory,
          and track sales all in one place.
        </p>
      </div>

      <div className="platforms-grid">
        {platforms.map((platform) => {
          const connected = isConnected(platform.id);
          const connectedData = getConnectedPlatform(platform.id);

          return (
            <div
              key={platform.id}
              className={`platform-card ${connected ? 'connected' : ''}`}
              style={{ borderTopColor: platform.color }}
            >
              <div className="platform-header">
                <div className="platform-icon" style={{ background: platform.color }}>
                  {platform.icon}
                </div>
                <div className="platform-info">
                  <h4>{platform.name}</h4>
                  <p>{platform.description}</p>
                </div>
              </div>

              {connected ? (
                <div className="platform-connected">
                  <div className="connection-status">
                    <span className="status-indicator">✅</span>
                    <span>Connected</span>
                  </div>

                  {connectedData && (
                    <div className="connection-details">
                      <div className="detail-row">
                        <span className="detail-label">Store URL:</span>
                        <span className="detail-value">{connectedData.shop_url}</span>
                      </div>
                      {connectedData.last_sync_at && (
                        <div className="detail-row">
                          <span className="detail-label">Last Sync:</span>
                          <span className="detail-value">
                            {new Date(connectedData.last_sync_at).toLocaleString()}
                          </span>
                        </div>
                      )}
                      {connectedData.products_synced !== undefined && (
                        <div className="detail-row">
                          <span className="detail-label">Products Synced:</span>
                          <span className="detail-value">{connectedData.products_synced}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="platform-actions">
                    <button
                      onClick={() => handleSyncProducts(platform.id)}
                      className="action-btn sync-btn"
                      disabled={syncing}
                    >
                      {syncing ? '⏳ Syncing...' : '🔄 Sync Products'}
                    </button>
                    <button
                      onClick={() => handleDisconnect(platform.id)}
                      className="action-btn disconnect-btn"
                    >
                      🔌 Disconnect
                    </button>
                  </div>
                </div>
              ) : (
                <div className="platform-not-connected">
                  <button
                    onClick={() => handleConnectPlatform(platform)}
                    className="connect-btn"
                    style={{ background: platform.color }}
                  >
                    Connect {platform.name}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Connection Modal */}
      {showConnectModal && selectedPlatform && (
        <div className="modal-overlay" onClick={() => setShowConnectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Connect to {selectedPlatform.name}</h3>
              <button onClick={() => setShowConnectModal(false)} className="modal-close">
                ✖
              </button>
            </div>

            <form onSubmit={handleSubmitConnection} className="connection-form">
              {selectedPlatform.id === 'shopify' && (
                <>
                  <div className="form-group">
                    <label>Store URL *</label>
                    <input
                      type="text"
                      value={shopifyData.shop_url}
                      onChange={(e) => setShopifyData({ ...shopifyData, shop_url: e.target.value })}
                      placeholder="your-store.myshopify.com"
                      required
                    />
                    <small>Enter your Shopify store URL</small>
                  </div>

                  <div className="form-group">
                    <label>Access Token *</label>
                    <input
                      type="password"
                      value={shopifyData.access_token}
                      onChange={(e) => setShopifyData({ ...shopifyData, access_token: e.target.value })}
                      placeholder="shpat_xxxxxxxxxxxxx"
                      required
                    />
                    <small>Get this from your Shopify admin → Apps → Private apps</small>
                  </div>
                </>
              )}

              {selectedPlatform.id === 'woocommerce' && (
                <>
                  <div className="form-group">
                    <label>Store URL *</label>
                    <input
                      type="text"
                      value={woocommerceData.shop_url}
                      onChange={(e) => setWoocommerceData({ ...woocommerceData, shop_url: e.target.value })}
                      placeholder="https://your-store.com"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Consumer Key *</label>
                    <input
                      type="text"
                      value={woocommerceData.consumer_key}
                      onChange={(e) => setWoocommerceData({ ...woocommerceData, consumer_key: e.target.value })}
                      placeholder="ck_xxxxxxxxxxxxx"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Consumer Secret *</label>
                    <input
                      type="password"
                      value={woocommerceData.consumer_secret}
                      onChange={(e) => setWoocommerceData({ ...woocommerceData, consumer_secret: e.target.value })}
                      placeholder="cs_xxxxxxxxxxxxx"
                      required
                    />
                    <small>Find these in WooCommerce → Settings → Advanced → REST API</small>
                  </div>
                </>
              )}

              {selectedPlatform.id === 'prestashop' && (
                <>
                  <div className="form-group">
                    <label>Store URL *</label>
                    <input
                      type="text"
                      value={prestashopData.shop_url}
                      onChange={(e) => setPrestashopData({ ...prestashopData, shop_url: e.target.value })}
                      placeholder="https://your-store.com"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>API Key *</label>
                    <input
                      type="password"
                      value={prestashopData.api_key}
                      onChange={(e) => setPrestashopData({ ...prestashopData, api_key: e.target.value })}
                      placeholder="XXXXXXXXXXXXXXXXXXXXX"
                      required
                    />
                    <small>Generate from PrestaShop → Advanced Parameters → Webservice</small>
                  </div>
                </>
              )}

              <div className="modal-actions">
                <button type="submit" className="submit-btn">
                  Connect
                </button>
                <button
                  type="button"
                  onClick={() => setShowConnectModal(false)}
                  className="cancel-btn"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {connectedPlatforms.length > 0 && (
        <div className="sync-summary">
          <h4>📊 Sync Summary</h4>
          <div className="summary-stats">
            <div className="summary-stat">
              <div className="stat-value">
                {connectedPlatforms.reduce((sum, p) => sum + (p.products_synced || 0), 0)}
              </div>
              <div className="stat-label">Total Products Synced</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{connectedPlatforms.length}</div>
              <div className="stat-label">Connected Platforms</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">
                {connectedPlatforms.filter(p => p.status === 'active').length}
              </div>
              <div className="stat-label">Active Connections</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EcommerceIntegrationsPanel;
