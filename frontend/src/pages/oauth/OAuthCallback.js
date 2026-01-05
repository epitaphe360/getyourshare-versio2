/**
 * Gestionnaire de callback OAuth universel
 *
 * Gère les redirections depuis:
 * - Instagram OAuth
 * - TikTok OAuth
 * - Facebook OAuth
 * - Autres plateformes sociales
 *
 * Routes:
 * /oauth/callback/instagram
 * /oauth/callback/tiktok
 * /oauth/callback/facebook
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import api from '../../utils/api';

const OAuthCallback = () => {
  const { platform } = useParams(); // instagram, tiktok, facebook
  const navigate = useNavigate();
  const location = useLocation();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Connexion en cours...');
  const [error, setError] = useState(null);

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      // Extraire les paramètres de l'URL
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const error = params.get('error');
      const errorDescription = params.get('error_description');

      // Vérifier si l'utilisateur a refusé l'autorisation
      if (error) {
        setStatus('error');
        setError(errorDescription || 'Autorisation refusée par l\'utilisateur');
        setMessage('Connexion annulée');
        return;
      }

      // Vérifier que le code est présent
      if (!code) {
        setStatus('error');
        setError('Code d\'autorisation manquant');
        setMessage('Erreur de connexion');
        return;
      }

      // Récupérer l'état OAuth sauvegardé
      const oauthState = JSON.parse(localStorage.getItem('oauth_state') || '{}');

      // Appeler le backend selon la plateforme
      let response;
      switch (platform) {
        case 'instagram':
          response = await handleInstagramCallback(code);
          break;
        case 'tiktok':
          response = await handleTikTokCallback(code);
          break;
        case 'facebook':
          response = await handleFacebookCallback(code);
          break;
        default:
          throw new Error(`Plateforme non supportée: ${platform}`);
      }

      // Succès
      setStatus('success');
      setMessage(`✅ Compte ${platform} connecté avec succès !`);

      // Nettoyer le localStorage
      localStorage.removeItem('oauth_state');
      if (platform === 'tiktok') {
        localStorage.removeItem('tiktok_csrf_state');
      }

      // Rediriger vers la page des connexions après 2 secondes
      setTimeout(() => {
        navigate(oauthState.returnUrl || '/influencer/social-media');
      }, 2000);

    } catch (err) {
      console.error('OAuth callback error:', err);
      setStatus('error');
      setError(err.response?.data?.detail || err.message || 'Erreur inconnue');
      setMessage('❌ Erreur lors de la connexion');
    }
  };

  // Callback Instagram
  const handleInstagramCallback = async (code) => {
    setMessage('Échange du code Instagram...');

    // Étape 1: Échanger le code contre un short-lived token
    const tokenResponse = await fetch('https://api.instagram.com/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        client_id: process.env.REACT_APP_INSTAGRAM_CLIENT_ID,
        client_secret: process.env.REACT_APP_INSTAGRAM_CLIENT_SECRET,
        grant_type: 'authorization_code',
        redirect_uri: `${window.location.origin}/oauth/callback/instagram`,
        code: code,
      }),
    });

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.json();
      throw new Error(errorData.error_message || 'Erreur lors de l\'échange du code Instagram');
    }

    const tokenData = await tokenResponse.json();
    const { access_token, user_id } = tokenData;

    // Étape 2: Envoyer au backend (qui va échanger contre long-lived token)
    setMessage('Connexion à votre compte Instagram...');
    const response = await api.post('/api/social-media/connect/instagram', {
      instagram_user_id: user_id.toString(),
      access_token: access_token,
    });

    return response.data;
  };

  // Callback TikTok
  const handleTikTokCallback = async (code) => {
    setMessage('Connexion à TikTok...');

    // Vérifier le CSRF state
    const params = new URLSearchParams(location.search);
    const state = params.get('state');
    const savedState = localStorage.getItem('tiktok_csrf_state');

    if (state !== savedState) {
      throw new Error('État CSRF invalide - possible attaque CSRF');
    }

    // Envoyer le code au backend
    const response = await api.post('/api/social-media/connect/tiktok', {
      authorization_code: code,
      redirect_uri: `${window.location.origin}/oauth/callback/tiktok`,
    });

    return response.data;
  };

  // Callback Facebook
  const handleFacebookCallback = async (code) => {
    setMessage('Connexion à Facebook...');

    // Échanger le code contre un access_token
    const params = new URLSearchParams({
      client_id: process.env.REACT_APP_FACEBOOK_APP_ID,
      client_secret: process.env.REACT_APP_FACEBOOK_APP_SECRET,
      redirect_uri: `${window.location.origin}/oauth/callback/facebook`,
      code: code,
    });

    const tokenResponse = await fetch(
      `https://graph.facebook.com/v18.0/oauth/access_token?${params.toString()}`
    );

    if (!tokenResponse.ok) {
      const errorData = await tokenResponse.json();
      throw new Error(errorData.error?.message || 'Erreur lors de l\'échange du code Facebook');
    }

    const tokenData = await tokenResponse.json();
    const { access_token } = tokenData;

    // Récupérer l'ID utilisateur
    const userResponse = await fetch(
      `https://graph.facebook.com/me?access_token=${access_token}`
    );
    const userData = await userResponse.json();

    // Envoyer au backend
    const response = await api.post('/api/social-media/connect/facebook', {
      facebook_user_id: userData.id,
      access_token: access_token,
    });

    return response.data;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">

        {/* Processing */}
        {status === 'processing' && (
          <div className="text-center">
            <div className="mb-4">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Connexion en cours
            </h2>
            <p className="text-gray-600 mb-4">{message}</p>
            <p className="text-sm text-gray-500">
              Veuillez patienter, cela peut prendre quelques secondes...
            </p>
          </div>
        )}

        {/* Success */}
        {status === 'success' && (
          <div className="text-center">
            <div className="mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Connexion réussie !
            </h2>
            <p className="text-gray-600 mb-4">{message}</p>
            <p className="text-sm text-gray-500">
              Redirection en cours...
            </p>
          </div>
        )}

        {/* Error */}
        {status === 'error' && (
          <div className="text-center">
            <div className="mb-4">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Erreur de connexion
            </h2>
            <p className="text-gray-600 mb-4">{message}</p>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                {error}
              </div>
            )}
            <button
              onClick={() => navigate('/influencer/social-media')}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Retour aux connexions
            </button>
          </div>
        )}

        {/* Informations de sécurité */}
        <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800">
          🔒 Vos données sont sécurisées. Nous ne stockons jamais vos mots de passe.
        </div>
      </div>
    </div>
  );
};

export default OAuthCallback;
