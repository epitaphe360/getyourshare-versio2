/**
 * Page de gestion des connexions réseaux sociaux pour les influenceurs
 *
 * Permet de:
 * - Connecter des comptes sociaux (Instagram, TikTok, Facebook, etc.)
 * - Voir les statistiques automatiquement récupérées
 * - Synchroniser manuellement les données
 * - Déconnecter des comptes
 *
 * Workflow OAuth:
 * 1. Utilisateur clique sur "Connecter Instagram"
 * 2. Redirection vers Instagram OAuth
 * 3. Instagram redirige vers /oauth/callback avec code
 * 4. Callback envoie code au backend
 * 5. Backend sauvegarde connexion et récupère stats
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../utils/api';

const SocialMediaConnections = () => {
  const [connections, setConnections] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Configuration OAuth (à déplacer dans variables d'environnement)
  const OAUTH_CONFIG = {
    instagram: {
      clientId: process.env.REACT_APP_INSTAGRAM_CLIENT_ID || 'YOUR_INSTAGRAM_APP_ID',
      redirectUri: `${window.location.origin}/oauth/callback/instagram`,
      scope: 'instagram_basic,instagram_manage_insights',
      authUrl: 'https://api.instagram.com/oauth/authorize'
    },
    tiktok: {
      clientKey: process.env.REACT_APP_TIKTOK_CLIENT_KEY || 'YOUR_TIKTOK_CLIENT_KEY',
      redirectUri: `${window.location.origin}/oauth/callback/tiktok`,
      scope: 'user.info.basic,video.list',
      authUrl: 'https://www.tiktok.com/auth/authorize/'
    },
    facebook: {
      appId: process.env.REACT_APP_FACEBOOK_APP_ID || 'YOUR_FACEBOOK_APP_ID',
      redirectUri: `${window.location.origin}/oauth/callback/facebook`,
      scope: 'pages_read_engagement,pages_show_list',
      authUrl: 'https://www.facebook.com/v18.0/dialog/oauth'
    }
  };

  useEffect(() => {
    fetchConnections();
    fetchDashboardStats();
  }, []);

  const fetchConnections = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/social-media/connections');
      setConnections(response.data);
    } catch (err) {
      console.error('Error fetching connections:', err);
      setError('Erreur lors du chargement des connexions');
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get('/api/social-media/dashboard');
      setDashboardStats(response.data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  };

  // Connexion Instagram
  const handleConnectInstagram = () => {
    const { clientId, redirectUri, scope, authUrl } = OAUTH_CONFIG.instagram;

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scope,
      response_type: 'code'
    });

    const authorizationUrl = `${authUrl}?${params.toString()}`;

    // Sauvegarder l'état pour la redirection après OAuth
    localStorage.setItem('oauth_state', JSON.stringify({
      platform: 'instagram',
      returnUrl: window.location.pathname
    }));

    // Rediriger vers Instagram OAuth
    window.location.href = authorizationUrl;
  };

  // Connexion TikTok
  const handleConnectTikTok = () => {
    const { clientKey, redirectUri, scope, authUrl } = OAUTH_CONFIG.tiktok;

    const csrfState = Math.random().toString(36).substring(7);
    localStorage.setItem('tiktok_csrf_state', csrfState);

    const params = new URLSearchParams({
      client_key: clientKey,
      redirect_uri: redirectUri,
      scope: scope,
      response_type: 'code',
      state: csrfState
    });

    const authorizationUrl = `${authUrl}?${params.toString()}`;

    localStorage.setItem('oauth_state', JSON.stringify({
      platform: 'tiktok',
      returnUrl: window.location.pathname
    }));

    window.location.href = authorizationUrl;
  };

  // Connexion Facebook
  const handleConnectFacebook = () => {
    const { appId, redirectUri, scope, authUrl } = OAUTH_CONFIG.facebook;

    const params = new URLSearchParams({
      client_id: appId,
      redirect_uri: redirectUri,
      scope: scope,
      response_type: 'code'
    });

    const authorizationUrl = `${authUrl}?${params.toString()}`;

    localStorage.setItem('oauth_state', JSON.stringify({
      platform: 'facebook',
      returnUrl: window.location.pathname
    }));

    window.location.href = authorizationUrl;
  };

  // Déconnexion
  const handleDisconnect = async (connectionId, platform) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir déconnecter votre compte ${platform} ?`)) {
      return;
    }

    try {
      await api.delete(`/api/social-media/connections/${connectionId}`);
      setSuccessMessage(`Compte ${platform} déconnecté avec succès`);
      fetchConnections();
      fetchDashboardStats();
    } catch (err) {
      console.error('Error disconnecting:', err);
      setError(`Erreur lors de la déconnexion de ${platform}`);
    }
  };

  // Synchronisation manuelle
  const handleSyncAll = async () => {
    try {
      setSyncing(true);
      const response = await api.post('/api/social-media/sync');

      const successCount = response.data.filter(r => r.sync_status === 'success').length;
      const failedCount = response.data.filter(r => r.sync_status === 'failed').length;

      if (failedCount === 0) {
        setSuccessMessage(`✅ Synchronisation réussie pour ${successCount} compte(s)`);
      } else {
        setError(`⚠️ ${successCount} succès, ${failedCount} échec(s)`);
      }

      fetchConnections();
      fetchDashboardStats();
    } catch (err) {
      console.error('Error syncing:', err);
      setError('Erreur lors de la synchronisation');
    } finally {
      setSyncing(false);
    }
  };

  const handleSyncPlatform = async (platform) => {
    try {
      setSyncing(true);
      await api.post('/api/social-media/sync', {
        platforms: [platform]
      });
      setSuccessMessage(`✅ ${platform} synchronisé avec succès`);
      fetchConnections();
      fetchDashboardStats();
    } catch (err) {
      console.error('Error syncing platform:', err);
      setError(`Erreur lors de la synchronisation de ${platform}`);
    } finally {
      setSyncing(false);
    }
  };

  // Formater les nombres
  const formatNumber = (num) => {
    const n = Number(num);
    if (isNaN(n)) return '0';
    if (n >= 1000000) {
      return (n / 1000000).toFixed(1) + 'M';
    }
    if (n >= 1000) {
      return (n / 1000).toFixed(1) + 'K';
    }
    return n.toString();
  };

  // Statut de connexion avec badge coloré
  const getStatusBadge = (status) => {
    const badges = {
      active: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">✓ Actif</span>,
      expired: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">⚠ Expiré</span>,
      error: <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">⚠ Erreur</span>
    };
    return badges[status] || <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">{status}</span>;
  };

  // Icônes des plateformes
  const getPlatformIcon = (platform) => {
    const icons = {
      instagram: '📷',
      tiktok: '🎵',
      facebook: '👤',
      youtube: '📺',
      twitter: '🐦',
      linkedin: '💼'
    };
    return icons[platform] || '🌐';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Connexions Réseaux Sociaux
          </h1>
          <p className="text-gray-600">
            Connectez vos comptes sociaux pour récupérer automatiquement vos statistiques
          </p>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
            <button onClick={() => setError(null)} className="ml-4 underline">Fermer</button>
          </div>
        )}
        {successMessage && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {successMessage}
            <button onClick={() => setSuccessMessage(null)} className="ml-4 underline">Fermer</button>
          </div>
        )}

        {/* Statistiques globales */}
        {dashboardStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Followers</div>
              <div className="text-3xl font-bold text-primary-600">{formatNumber(dashboardStats.total_followers)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Plateformes</div>
              <div className="text-3xl font-bold text-primary-600">{dashboardStats.total_platforms}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Engagement Moyen</div>
              <div className="text-3xl font-bold text-primary-600">{dashboardStats.avg_engagement_rate.toFixed(1)}%</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Posts</div>
              <div className="text-3xl font-bold text-primary-600">{formatNumber(dashboardStats.total_posts)}</div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Mes Connexions</h2>
          <button
            onClick={handleSyncAll}
            disabled={syncing || connections.length === 0}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {syncing ? (
              <>
                <span className="animate-spin">⟳</span>
                Synchronisation...
              </>
            ) : (
              <>
                <span>↻</span>
                Synchroniser tout
              </>
            )}
          </button>
        </div>

        {/* Liste des connexions */}
        {connections.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {connections.map((connection) => {
              const stat = dashboardStats?.latest_stats?.find(s => s.platform === connection.platform);

              return (
                <div key={connection.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{getPlatformIcon(connection.platform)}</span>
                        <div>
                          <h3 className="font-semibold text-gray-900 capitalize">{connection.platform}</h3>
                          <p className="text-sm text-gray-600">@{connection.platform_username}</p>
                        </div>
                      </div>
                      {getStatusBadge(connection.connection_status)}
                    </div>

                    {/* Photo de profil */}
                    {connection.profile_picture_url && (
                      <img
                        src={connection.profile_picture_url}
                        alt="Profile"
                        className="w-16 h-16 rounded-full mb-4"
                      />
                    )}

                    {/* Statistiques */}
                    {stat && (
                      <div className="space-y-2 mb-4">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Followers:</span>
                          <span className="font-semibold">{formatNumber(stat.followers_count)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Engagement:</span>
                          <span className="font-semibold">{stat.engagement_rate.toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Posts:</span>
                          <span className="font-semibold">{stat.total_posts}</span>
                        </div>
                        {stat.followers_growth !== null && stat.followers_growth !== 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Croissance:</span>
                            <span className={`font-semibold ${stat.followers_growth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {stat.followers_growth > 0 ? '+' : ''}{stat.followers_growth}
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Info expiration */}
                    {connection.days_until_expiry !== null && connection.days_until_expiry < 14 && (
                      <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                        ⚠️ Token expire dans {connection.days_until_expiry} jour(s)
                      </div>
                    )}

                    {/* Dernière sync */}
                    {connection.last_synced_at && (
                      <p className="text-xs text-gray-500 mb-4">
                        Dernière sync: {new Date(connection.last_synced_at).toLocaleDateString('fr-FR')}
                      </p>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSyncPlatform(connection.platform)}
                        disabled={syncing}
                        className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm disabled:opacity-50"
                      >
                        ↻ Sync
                      </button>
                      <button
                        onClick={() => handleDisconnect(connection.id, connection.platform)}
                        className="flex-1 px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm"
                      >
                        Déconnecter
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center mb-8">
            <p className="text-gray-600 mb-4">Aucun compte connecté pour le moment</p>
            <p className="text-sm text-gray-500">Connectez vos réseaux sociaux pour commencer à suivre vos statistiques</p>
          </div>
        )}

        {/* Boutons de connexion */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Ajouter un compte</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            {/* Instagram */}
            {!connections.find(c => c.platform === 'instagram' && c.connection_status === 'active') && (
              <button
                onClick={handleConnectInstagram}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-pink-500 hover:bg-pink-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-3xl">📷</span>
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Instagram</div>
                    <div className="text-sm text-gray-600">Connecter votre compte</div>
                  </div>
                </div>
              </button>
            )}

            {/* TikTok */}
            {!connections.find(c => c.platform === 'tiktok' && c.connection_status === 'active') && (
              <button
                onClick={handleConnectTikTok}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-black hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-3xl">🎵</span>
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">TikTok</div>
                    <div className="text-sm text-gray-600">Connecter votre compte</div>
                  </div>
                </div>
              </button>
            )}

            {/* Facebook */}
            {!connections.find(c => c.platform === 'facebook' && c.connection_status === 'active') && (
              <button
                onClick={handleConnectFacebook}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-3xl">👤</span>
                  <div className="text-left">
                    <div className="font-semibold text-gray-900">Facebook</div>
                    <div className="text-sm text-gray-600">Bientôt disponible</div>
                  </div>
                </div>
              </button>
            )}
          </div>

          {/* Documentation */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">📖 Pourquoi connecter mes comptes ?</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ Récupération automatique de vos statistiques (followers, engagement)</li>
              <li>✓ Mise à jour quotidienne de vos données</li>
              <li>✓ Profil plus attractif pour les marchands</li>
              <li>✓ Suivi de votre croissance et performances</li>
            </ul>
          </div>
        </div>

        {/* Lien vers historique */}
        <div className="mt-6 text-center">
          <Link
            to="/influencer/social-media/history"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Voir l'historique complet de mes statistiques →
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SocialMediaConnections;
