/**
 * Monitoring Frontend - Sentry
 * Initialiser dans index.js AVANT ReactDOM.render()
 *
 * Variables d'environnement (.env):
 *   REACT_APP_SENTRY_DSN=https://xxxx@sentry.io/yyyy
 *   REACT_APP_VERSION=1.0.0
 *   REACT_APP_ENV=production
 */

const initSentry = () => {
  const dsn = process.env.REACT_APP_SENTRY_DSN;
  if (!dsn) {
    console.info('[Sentry] DSN non configuré — monitoring désactivé');
    return;
  }

  import('@sentry/react').then(({ init, BrowserTracing, Replay, reactRouterV6BrowserTracingIntegration }) => {
    const { createRoutesFromChildren, matchRoutes, useLocation, useNavigationType } =
      require('react-router-dom');

    init({
      dsn,
      environment: process.env.REACT_APP_ENV || 'development',
      release: `getyourshare@${process.env.REACT_APP_VERSION || '1.0.0'}`,
      integrations: [
        reactRouterV6BrowserTracingIntegration({
          useEffect: require('react').useEffect,
          useLocation,
          useNavigationType,
          createRoutesFromChildren,
          matchRoutes,
        }),
        new Replay({
          maskAllText: true,
          blockAllMedia: true,
        }),
      ],
      tracesSampleRate: process.env.REACT_APP_ENV === 'production' ? 0.1 : 1.0,
      replaysSessionSampleRate: 0.05,
      replaysOnErrorSampleRate: 1.0,
      // Ne pas envoyer les informations personnelles
      beforeSend(event) {
        if (event.request) {
          delete event.request.cookies;
          delete event.request.headers?.Authorization;
        }
        return event;
      },
    });

    console.info('[Sentry] ✅ Initialisé');
  }).catch(err => {
    console.warn('[Sentry] Non disponible:', err.message);
  });
};

export default initSentry;
