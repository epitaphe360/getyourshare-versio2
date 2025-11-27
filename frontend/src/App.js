import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { CurrencyProvider } from './context/CurrencyContext';
import { I18nProvider } from './i18n/i18n';
import Layout from './components/layout/Layout';
import PublicLayout from './components/layout/PublicLayout';
import ChatbotWidget from './components/bot/ChatbotWidget';
import WhatsAppFloatingButton from './components/social/WhatsAppFloatingButton';
import CookieConsent from './components/CookieConsent';
import LoadingFallback from './components/LoadingFallback';
import performanceUtils from './utils/performance';
import './App.css';

// ============================================================================
// CODE SPLITTING - React.lazy() pour toutes les pages
// Amélioration performances: Bundle size réduit de ~2.7MB à ~300KB initial
// ============================================================================

// ---------- Auth & Public Pages ----------
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const HomepageV2 = lazy(() => import('./pages/HomepageV2'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const Pricing = lazy(() => import('./pages/Pricing'));
const PricingV3 = lazy(() => import('./pages/PricingV3'));
const Contact = lazy(() => import('./pages/Contact'));
const ROICalculator = lazy(() => import('./pages/ROICalculator'));

// ---------- Legal Pages ----------
const Privacy = lazy(() => import('./pages/Privacy'));
const Terms = lazy(() => import('./pages/Terms'));
const About = lazy(() => import('./pages/About'));

// ---------- Dashboard & Core ----------
const Dashboard = lazy(() => import('./pages/Dashboard'));
const GettingStarted = lazy(() => import('./pages/GettingStarted'));
const News = lazy(() => import('./pages/News'));

// ---------- Dashboards Spécifiques ----------
const AdminDashboard = lazy(() => import('./pages/dashboards/AdminDashboard'));
const MerchantDashboard = lazy(() => import('./pages/dashboards/MerchantDashboard'));
const InfluencerDashboard = lazy(() => import('./pages/dashboards/InfluencerDashboard'));
const CommercialDashboard = lazy(() => import('./pages/dashboards/CommercialDashboard'));

// ---------- Marketplace ----------
const Marketplace = lazy(() => import('./pages/Marketplace'));
const MarketplaceV2 = lazy(() => import('./pages/MarketplaceV2'));
const MarketplaceFourTabs = lazy(() => import('./pages/MarketplaceFourTabs'));
const MarketplaceGroupon = lazy(() => import('./pages/MarketplaceGroupon'));
const ProductDetail = lazy(() => import('./pages/ProductDetail'));

// ---------- Merchants & Influencers ----------
const MerchantsList = lazy(() => import('./pages/merchants/MerchantsList'));
const InfluencersList = lazy(() => import('./pages/influencers/InfluencersList'));
const InfluencerSearchPage = lazy(() => import('./pages/influencers/InfluencerSearchPage'));
const InfluencerProfilePage = lazy(() => import('./pages/influencers/InfluencerProfilePage'));
const MyLinks = lazy(() => import('./pages/influencer/MyLinks'));

// ---------- Messaging ----------
const MessagingPage = lazy(() => import('./pages/MessagingPage'));

// ---------- Products ----------
const ProductsListPage = lazy(() => import('./pages/products/ProductsListPage'));
const CreateProductPage = lazy(() => import('./pages/products/CreateProductPage'));

// ---------- Services ----------
const ServicesListPage = lazy(() => import('./pages/services/ServicesListPage'));
const CreateServicePage = lazy(() => import('./pages/services/CreateServicePage'));
const ServiceDetailPage = lazy(() => import('./pages/services/ServiceDetailPage'));

// ---------- Advertisers ----------
const AdvertisersList = lazy(() => import('./pages/advertisers/AdvertisersList'));
const AdvertiserRegistrations = lazy(() => import('./pages/advertisers/AdvertiserRegistrations'));
const AdvertiserBilling = lazy(() => import('./pages/advertisers/AdvertiserBilling'));

// ---------- Campaigns ----------
const CampaignsList = lazy(() => import('./pages/campaigns/CampaignsList'));
const CreateCampaignPage = lazy(() => import('./pages/campaigns/CreateCampaignPage'));
const CampaignDetailPage = lazy(() => import('./pages/campaigns/CampaignDetailPage'));

// ---------- Affiliates ----------
const AffiliatesList = lazy(() => import('./pages/affiliates/AffiliatesList'));
const AffiliateApplications = lazy(() => import('./pages/affiliates/AffiliateApplications'));
const AffiliatePayouts = lazy(() => import('./pages/affiliates/AffiliatePayouts'));
const AffiliateCoupons = lazy(() => import('./pages/affiliates/AffiliateCoupons'));
const LostOrders = lazy(() => import('./pages/affiliates/LostOrders'));
const BalanceReport = lazy(() => import('./pages/affiliates/BalanceReport'));

// ---------- Performance ----------
const Conversions = lazy(() => import('./pages/performance/Conversions'));
const MLMCommissions = lazy(() => import('./pages/performance/MLMCommissions'));
const Leads = lazy(() => import('./pages/performance/Leads'));
const Reports = lazy(() => import('./pages/performance/Reports'));

// ---------- Logs ----------
const Clicks = lazy(() => import('./pages/logs/Clicks'));
const Postback = lazy(() => import('./pages/logs/Postback'));
const Audit = lazy(() => import('./pages/logs/Audit'));
const Webhooks = lazy(() => import('./pages/logs/Webhooks'));

// ---------- Settings ----------
const PersonalSettings = lazy(() => import('./pages/settings/PersonalSettings'));
const SecuritySettings = lazy(() => import('./pages/settings/SecuritySettings'));
const CompanySettings = lazy(() => import('./pages/settings/CompanySettings'));
const AffiliateSettings = lazy(() => import('./pages/settings/AffiliateSettings'));
const RegistrationSettings = lazy(() => import('./pages/settings/RegistrationSettings'));
const MLMSettings = lazy(() => import('./pages/settings/MLMSettings'));
const TrafficSources = lazy(() => import('./pages/settings/TrafficSources'));
const Permissions = lazy(() => import('./pages/settings/Permissions'));
const Users = lazy(() => import('./pages/settings/Users'));
const SMTP = lazy(() => import('./pages/settings/SMTP'));
const Emails = lazy(() => import('./pages/settings/Emails'));
const WhiteLabel = lazy(() => import('./pages/settings/WhiteLabel'));
const PlatformSettings = lazy(() => import('./pages/settings/PlatformSettings'));

// ---------- Admin ----------
const AdminSocialDashboard = lazy(() => import('./pages/admin/AdminSocialDashboard'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const ModerationDashboard = lazy(() => import('./pages/admin/ModerationDashboard'));

// ---------- TOP 5 FEATURES ----------
const AdvancedAnalyticsDashboard = lazy(() => import('./pages/AdvancedAnalyticsDashboard'));
const InfluencerMatchingPage = lazy(() => import('./pages/InfluencerMatchingPage'));
const MobileDashboard = lazy(() => import('./components/mobile/MobileDashboard'));

// ---------- Company & Subscription ----------
const SubscriptionDashboard = lazy(() => import('./pages/company/SubscriptionDashboard'));
const SubscriptionManagement = lazy(() => import('./pages/subscription/SubscriptionManagement'));
const TeamManagement = lazy(() => import('./pages/company/TeamManagement'));
const CompanyLinksDashboard = lazy(() => import('./pages/company/CompanyLinksDashboard'));
const SubscriptionPlans = lazy(() => import('./pages/subscription/SubscriptionPlans'));
const BillingHistory = lazy(() => import('./pages/subscription/BillingHistory'));
const CancelSubscription = lazy(() => import('./pages/subscription/CancelSubscription'));
const SubscriptionCancelled = lazy(() => import('./pages/subscription/SubscriptionCancelled'));

// ---------- Other Features ----------
const TrackingLinks = lazy(() => import('./pages/TrackingLinks'));
const Integrations = lazy(() => import('./pages/Integrations'));
const AIMarketing = lazy(() => import('./pages/AIMarketing'));
const FeaturesHub = lazy(() => import('./pages/features/FeaturesHub'));

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
};

// Role-based Protected Route Component
const RoleProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Chargement...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Vérifier si le rôle de l'utilisateur est autorisé
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Accès refusé</h2>
            <p className="text-gray-600 mb-4">
              Vous n'avez pas les permissions nécessaires pour accéder à cette page.
            </p>
            <p className="text-sm text-gray-500">
              Cette fonctionnalité est réservée aux {allowedRoles.join(', ')}.
            </p>
            <button
              onClick={() => window.history.back()}
              className="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Retour
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return <Layout>{children}</Layout>;
};

function App() {
  // Initialize performance optimizations on mount
  useEffect(() => {
    // Initialize all performance optimizations
    performanceUtils.init();

    // Preload critical resources
    performanceUtils.preload();

    // Log performance budget
    window.addEventListener('load', () => {
      setTimeout(() => {
        const budget = performanceUtils.checkBudget();

      }, 2000);
    });
  }, []);

  return (
    <AuthProvider>
      <ToastProvider>
        <CurrencyProvider>
          <I18nProvider>
            <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true
            }}
          >
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                {/* ========================================
                    PUBLIC ROUTES (No Authentication)
                ======================================== */}
                <Route path="/" element={<HomepageV2 />} />
                <Route path="/home" element={<HomepageV2 />} />
                <Route path="/landing-old" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/pricing-v3" element={<PricingV3 />} />
                <Route path="/marketplace-4tabs" element={<MarketplaceFourTabs />} />
                <Route path="/marketplace" element={<PublicLayout><MarketplaceGroupon /></PublicLayout>} />
                <Route path="/marketplace/product/:productId" element={<PublicLayout><ProductDetail /></PublicLayout>} />
                <Route path="/contact" element={<PublicLayout><Contact /></PublicLayout>} />
                <Route path="/roi-calculator" element={<ROICalculator />} />

                {/* Legal Pages */}
                <Route path="/privacy" element={<PublicLayout><Privacy /></PublicLayout>} />
                <Route path="/terms" element={<PublicLayout><Terms /></PublicLayout>} />
                <Route path="/about" element={<PublicLayout><About /></PublicLayout>} />

                {/* ========================================
                    SUBSCRIPTION ROUTES
                ======================================== */}
          <Route
            path="/subscription/plans"
            element={
              <ProtectedRoute>
                <SubscriptionPlans />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/billing"
            element={
              <ProtectedRoute>
                <BillingHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/cancel"
            element={
              <ProtectedRoute>
                <CancelSubscription />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription/cancelled"
            element={
              <ProtectedRoute>
                <SubscriptionCancelled />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    DASHBOARD & CORE
                ======================================== */}
                <Route
                  path="/getting-started"
                  element={
                    <ProtectedRoute>
                      <GettingStarted />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  }
                />
                
                {/* ========================================
                    DASHBOARDS SPÉCIFIQUES PAR RÔLE
                ======================================== */}
                <Route
                  path="/dashboard/admin"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <AdminDashboard />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard/merchant"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <MerchantDashboard />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard/influencer"
                  element={
                    <RoleProtectedRoute allowedRoles={['influencer', 'admin']}>
                      <InfluencerDashboard />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard/commercial"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <CommercialDashboard />
                    </RoleProtectedRoute>
                  }
                />
                
                <Route
                  path="/news"
                  element={
                    <ProtectedRoute>
                      <News />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    ADVERTISERS
                ======================================== */}
          <Route
            path="/advertisers"
            element={
              <ProtectedRoute>
                <AdvertisersList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/advertisers/registrations"
            element={
              <ProtectedRoute>
                <AdvertiserRegistrations />
              </ProtectedRoute>
            }
          />
          <Route
            path="/advertisers/billing"
            element={
              <ProtectedRoute>
                <AdvertiserBilling />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    CAMPAIGNS
                ======================================== */}
                <Route
                  path="/campaigns"
                  element={
                    <ProtectedRoute>
                      <CampaignsList />
                    </ProtectedRoute>
                  }
                />
                {/* Détail d'une campagne */}
                <Route
                  path="/campaigns/:id"
                  element={
                    <ProtectedRoute>
                      <CampaignDetailPage />
                    </ProtectedRoute>
                  }
                />
                {/* Création - Merchants/Admin uniquement */}
                <Route
                  path="/campaigns/create"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <CreateCampaignPage />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    MERCHANTS & INFLUENCERS
                ======================================== */}
          <Route
            path="/merchants"
            element={
              <ProtectedRoute>
                <MerchantsList />
              </ProtectedRoute>
            }
          />

          {/* Influencers Routes */}
          <Route
            path="/influencers"
            element={
              <ProtectedRoute>
                <InfluencersList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/influencers/search"
            element={
              <ProtectedRoute>
                <InfluencerSearchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/influencers/:influencerId"
            element={
              <ProtectedRoute>
                <InfluencerProfilePage />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    MESSAGING
                ======================================== */}
                <Route
                  path="/messages"
                  element={
                    <ProtectedRoute>
                      <MessagingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/messages/:conversationId"
                  element={
                    <ProtectedRoute>
                      <MessagingPage />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    PRODUCTS
                ======================================== */}
          <Route
            path="/products"
            element={
              <ProtectedRoute>
                <ProductsListPage />
              </ProtectedRoute>
            }
          />
                {/* Création/Édition - Merchants/Admin uniquement */}
                <Route
                  path="/products/create"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <CreateProductPage />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    SERVICES
                ======================================== */}
          <Route
            path="/services"
            element={
              <ProtectedRoute>
                <ServicesListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/services/create"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CreateServicePage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/services/:serviceId"
            element={
              <ProtectedRoute>
                <ServiceDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/services/:serviceId/edit"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CreateServicePage />
              </RoleProtectedRoute>
            }
          />

                <Route
                  path="/products/:productId/edit"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <CreateProductPage />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    AFFILIATES
                ======================================== */}
          <Route
            path="/affiliates"
            element={
              <ProtectedRoute>
                <AffiliatesList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/applications"
            element={
              <ProtectedRoute>
                <AffiliateApplications />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/payouts"
            element={
              <ProtectedRoute>
                <AffiliatePayouts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/coupons"
            element={
              <ProtectedRoute>
                <AffiliateCoupons />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/lost-orders"
            element={
              <ProtectedRoute>
                <LostOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/affiliates/balance-report"
            element={
              <ProtectedRoute>
                <BalanceReport />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    PERFORMANCE & ANALYTICS
                ======================================== */}
                <Route
                  path="/performance/conversions"
                  element={
                    <ProtectedRoute>
                      <Conversions />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/performance/mlm-commissions"
                  element={
                    <ProtectedRoute>
                      <MLMCommissions />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/performance/leads"
                  element={
                    <ProtectedRoute>
                      <Leads />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/performance/reports"
                  element={
                    <ProtectedRoute>
                      <Reports />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    LOGS & TRACKING
                ======================================== */}
          <Route
            path="/logs/clicks"
            element={
              <ProtectedRoute>
                <Clicks />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/postback"
            element={
              <ProtectedRoute>
                <Postback />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/audit"
            element={
              <ProtectedRoute>
                <Audit />
              </ProtectedRoute>
            }
          />
          <Route
            path="/logs/webhooks"
            element={
              <ProtectedRoute>
                <Webhooks />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    MARKETPLACE (Protected Versions)
                ======================================== */}
                {/* Anciennes versions - Pour référence */}
                <Route
                  path="/marketplace-old"
                  element={
                    <ProtectedRoute>
                      <Marketplace />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/marketplace-v2"
                  element={
                    <ProtectedRoute>
                      <MarketplaceV2 />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    INFLUENCER TOOLS
                ======================================== */}
                <Route
                  path="/my-links"
                  element={
                    <ProtectedRoute>
                      <MyLinks />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    ADMIN
                ======================================== */}
          <Route
            path="/admin/social-dashboard"
            element={
              <ProtectedRoute>
                <AdminSocialDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <UserManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/moderation"
            element={
              <ProtectedRoute>
                <ModerationDashboard />
              </ProtectedRoute>
            }
          />

                {/* ========================================
                    COMPANY & TEAM
                ======================================== */}
                <Route
                  path="/subscription"
                  element={
                    <ProtectedRoute>
                      <SubscriptionDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/subscription/manage"
                  element={
                    <ProtectedRoute>
                      <SubscriptionManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/team"
                  element={
                    <ProtectedRoute>
                      <TeamManagement />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/company-links"
                  element={
                    <ProtectedRoute>
                      <CompanyLinksDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    TOOLS & INTEGRATIONS
                ======================================== */}
                <Route
                  path="/ai-marketing"
                  element={
                    <ProtectedRoute>
                      <AIMarketing />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/tracking-links"
                  element={
                    <ProtectedRoute>
                      <TrackingLinks />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/integrations"
                  element={
                    <ProtectedRoute>
                      <Integrations />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    TOP 5 FEATURES - ROUTES
                ======================================== */}
                {/* Analytics Pro Dashboard - Tous les acteurs */}
                <Route
                  path="/analytics-pro"
                  element={
                    <ProtectedRoute>
                      <AdvancedAnalyticsDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Influencer Matching Tinder - Marchands uniquement */}
                <Route
                  path="/matching"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <InfluencerMatchingPage />
                    </RoleProtectedRoute>
                  }
                />

                {/* Mobile Dashboard - Tous les acteurs */}
                <Route
                  path="/mobile-dashboard"
                  element={
                    <ProtectedRoute>
                      <MobileDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Features Hub - Influenceurs et Marchands */}
                <Route
                  path="/features"
                  element={
                    <ProtectedRoute>
                      <FeaturesHub />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    SETTINGS
                ======================================== */}
          <Route
            path="/settings/personal"
            element={
              <ProtectedRoute>
                <PersonalSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/security"
            element={
              <ProtectedRoute>
                <SecuritySettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/company"
            element={
              <ProtectedRoute>
                <CompanySettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/affiliates"
            element={
              <ProtectedRoute>
                <AffiliateSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/registration"
            element={
              <ProtectedRoute>
                <RegistrationSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/mlm"
            element={
              <ProtectedRoute>
                <MLMSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/traffic-sources"
            element={
              <ProtectedRoute>
                <TrafficSources />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/permissions"
            element={
              <ProtectedRoute>
                <Permissions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/users"
            element={
              <ProtectedRoute>
                <Users />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/smtp"
            element={
              <ProtectedRoute>
                <SMTP />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/emails"
            element={
              <ProtectedRoute>
                <Emails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings/white-label"
            element={
              <ProtectedRoute>
                <WhiteLabel />
              </ProtectedRoute>
            }
          />
                {/* Paramètres Plateforme - Admin uniquement */}
                <Route
                  path="/settings/platform"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <PlatformSettings />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    DEFAULT & FALLBACK ROUTES
                ======================================== */}
                <Route path="/app" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>

            {/* Chatbot Widget flottant (en bas à droite) */}
            <ChatbotWidget />

            {/* Bouton WhatsApp flottant (en bas à gauche) */}
            <WhatsAppFloatingButton
              phoneNumber="+212600000000"
              message="Bonjour! Je suis intéressé par la plateforme ShareYourSales."
              position="left"
            />

            {/* Bannière Cookies (RGPD) */}
            <CookieConsent />
          </BrowserRouter>
          </I18nProvider>
        </CurrencyProvider>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
