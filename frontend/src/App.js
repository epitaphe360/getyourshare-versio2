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
const LandingPageNew = lazy(() => import('./pages/LandingPageNew'));
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

// ---------- Services & Leads (Lead Generation System) ----------
const PublicServices = lazy(() => import('./pages/PublicServices'));
const ServiceRequest = lazy(() => import('./pages/ServiceRequest'));

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
const AnalyticsDashboard = lazy(() => import('./pages/admin/AnalyticsDashboard'));
const LeadManagement = lazy(() => import('./pages/admin/LeadManagement'));
const ModerationDashboard = lazy(() => import('./pages/admin/ModerationDashboard'));
const AdminProductsManager = lazy(() => import('./pages/admin/AdminProductsManager'));
const ServiceManagement = lazy(() => import('./pages/admin/ServiceManagement'));

// ---------- TOP 5 FEATURES ----------
const AdvancedAnalyticsDashboard = lazy(() => import('./pages/AdvancedAnalyticsDashboard'));
const InfluencerMatchingPage = lazy(() => import('./pages/InfluencerMatchingPage'));
const MobileDashboard = lazy(() => import('./components/mobile/MobileDashboard'));

// ---------- Commercial & Influencer Dashboards ----------
const CommercialDashboard = lazy(() => import('./pages/commercial/CommercialDashboard'));
const InfluencerDashboard = lazy(() => import('./pages/influencer/InfluencerDashboard'));
const LeadsPage = lazy(() => import('./pages/commercial/LeadsPage'));
const LeadDetailPage = lazy(() => import('./pages/commercial/LeadDetailPage'));
const CommercialTrackingPage = lazy(() => import('./pages/commercial/TrackingPage'));

// ---------- Billing & Invoices ----------
const InvoiceManagement = lazy(() => import('./pages/billing/InvoiceManagement'));

// ---------- Advanced Marketplace ----------
const AdvancedMarketplace = lazy(() => import('./pages/marketplace/AdvancedMarketplace'));

// ---------- Phase 3 - Advanced Features ----------
const ReportsAdvanced = lazy(() => import('./pages/reports/ReportsAdvanced'));
const IntegrationsHub = lazy(() => import('./pages/integrations/IntegrationsHub'));
const AdvancedPlatformSettings = lazy(() => import('./pages/settings/AdvancedPlatformSettings'));
const EmailCampaigns = lazy(() => import('./pages/email/EmailCampaigns'));
const APIDocs = lazy(() => import('./pages/api/APIDocs'));

// ---------- Company & Subscription ----------
const SubscriptionDashboard = lazy(() => import('./pages/company/SubscriptionDashboard'));
const SubscriptionManagement = lazy(() => import('./pages/subscription/SubscriptionManagement'));
const AdminSubscriptionsManager = lazy(() => import('./pages/admin/AdminSubscriptionsManager'));
const AdminSubscriptionsAnalytics = lazy(() => import('./pages/admin/AdminSubscriptionsAnalytics'));
const AdminCoupons = lazy(() => import('./pages/admin/AdminCoupons'));
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

// ---------- Fiscal Module (MA/FR/US) - COMPLETE SYSTEM ----------
const TaxDashboard = lazy(() => import('./pages/fiscal/TaxDashboard'));
const InvoiceGenerator = lazy(() => import('./pages/fiscal/InvoiceGenerator'));
const TaxSettings = lazy(() => import('./pages/fiscal/TaxSettings'));

// Fiscal Dashboards (Role-specific)
const FiscalDashboardAdmin = lazy(() => import('./components/fiscal/FiscalDashboardAdmin'));
const FiscalDashboardMerchant = lazy(() => import('./components/fiscal/FiscalDashboardMerchant'));
const FiscalDashboardInfluencer = lazy(() => import('./components/fiscal/FiscalDashboardInfluencer'));
const FiscalDashboardCommercial = lazy(() => import('./components/fiscal/FiscalDashboardCommercial'));

// Fiscal Utilities
const InvoiceGeneratorNew = lazy(() => import('./components/fiscal/InvoiceGenerator'));
const VATCalculator = lazy(() => import('./components/fiscal/VATCalculator'));
const TaxDeclarationForm = lazy(() => import('./components/fiscal/TaxDeclarationForm'));
const AccountingExport = lazy(() => import('./components/fiscal/AccountingExport'));

// ---------- Invoices - Influencer & Commercial Invoices for Tax ----------
const InfluencerInvoicesPage = lazy(() => import('./pages/invoices/InfluencerInvoicesPage'));
const CommercialInvoicesPage = lazy(() => import('./pages/invoices/CommercialInvoicesPage'));

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
                <Route path="/landing-new" element={<LandingPageNew />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/pricing-v3" element={<PricingV3 />} />
                <Route path="/marketplace-4tabs" element={<MarketplaceFourTabs />} />
                <Route path="/marketplace" element={<PublicLayout><MarketplaceGroupon /></PublicLayout>} />
                <Route path="/marketplace/product/:productId" element={<PublicLayout><ProductDetail /></PublicLayout>} />
                <Route path="/contact" element={<PublicLayout><Contact /></PublicLayout>} />
                <Route path="/roi-calculator" element={<ROICalculator />} />

                {/* Services & Lead Generation (Public Access) */}
                <Route path="/services" element={<PublicLayout><PublicServices /></PublicLayout>} />
                <Route path="/services/:id" element={<PublicLayout><ServiceRequest /></PublicLayout>} />

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

                {/* ========================================
                    COMMERCIAL - CRM LEADS
                ======================================== */}
                <Route
                  path="/commercial/leads"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <LeadsPage />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/commercial/leads/:leadId"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <LeadDetailPage />
                    </RoleProtectedRoute>
                  }
                />
                
                <Route
                  path="/commercial/tracking"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <CommercialTrackingPage />
                    </RoleProtectedRoute>
                  }
                />
                
                <Route
                  path="/news"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <News />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    ADVERTISERS (Admin uniquement)
                ======================================== */}
          <Route
            path="/advertisers"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdvertisersList />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/advertisers/registrations"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdvertiserRegistrations />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/advertisers/billing"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdvertiserBilling />
              </RoleProtectedRoute>
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
              <RoleProtectedRoute allowedRoles={['admin']}>
                <MerchantsList />
              </RoleProtectedRoute>
            }
          />

          {/* Influencers Routes (Merchant et Admin) */}
          <Route
            path="/influencers"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <InfluencersList />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/influencers/search"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <InfluencerSearchPage />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/influencers/:influencerId"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <InfluencerProfilePage />
              </RoleProtectedRoute>
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
                    PRODUCTS (Merchant et Admin uniquement)
                ======================================== */}
          <Route
            path="/products"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <ProductsListPage />
              </RoleProtectedRoute>
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
                    SERVICES (Merchant et Admin uniquement)
                ======================================== */}
          <Route
            path="/services"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <ServicesListPage />
              </RoleProtectedRoute>
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
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <ServiceDetailPage />
              </RoleProtectedRoute>
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
                    AFFILIATES (Merchant et Admin uniquement)
                ======================================== */}
          <Route
            path="/affiliates"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <AffiliatesList />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/affiliates/applications"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <AffiliateApplications />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/affiliates/payouts"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <AffiliatePayouts />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/affiliates/coupons"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <AffiliateCoupons />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/affiliates/lost-orders"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <LostOrders />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/affiliates/balance-report"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <BalanceReport />
              </RoleProtectedRoute>
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
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <MLMCommissions />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/performance/leads"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <Leads />
                    </RoleProtectedRoute>
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
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <Clicks />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/logs/postback"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <Postback />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/logs/audit"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <Audit />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/logs/webhooks"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <Webhooks />
              </RoleProtectedRoute>
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
                    ADMIN (Admin uniquement)
                ======================================== */}
          <Route
            path="/admin/social-dashboard"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdminSocialDashboard />
              </RoleProtectedRoute>
            }
          <Route
            path="/admin/users"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <UserManagement />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/analytics"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AnalyticsDashboard />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/leads"
            element={
              <RoleProtectedRoute allowedRoles={['admin', 'merchant']}>
                <LeadManagement />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/moderation"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <ModerationDashboard />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/billing/invoices"
            element={
              <RoleProtectedRoute allowedRoles={['admin', 'merchant', 'commercial']}>
                <InvoiceManagement />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/marketplace/advanced"
            element={
              <ProtectedRoute>
                <AdvancedMarketplace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/advanced"
            element={
              <RoleProtectedRoute allowedRoles={['admin', 'merchant', 'commercial']}>
                <ReportsAdvanced />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/integrations"
            element={
              <RoleProtectedRoute allowedRoles={['admin', 'merchant']}>
                <IntegrationsHub />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/advanced"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdvancedPlatformSettings />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/email/campaigns"
            element={
              <RoleProtectedRoute allowedRoles={['admin', 'merchant', 'commercial']}>
                <EmailCampaigns />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/api/docs"
            element={
              <ProtectedRoute>
                <APIDocs />
              </ProtectedRoute>
            }
          />}
          />
          <Route
            path="/admin/products"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <AdminProductsManager />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/admin/services"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <ServiceManagement />
              </RoleProtectedRoute>
            }
          />

                {/* ========================================
                    COMPANY & TEAM (Merchant et Admin uniquement)
                ======================================== */}
                {/* Admin: Gestion de TOUS les abonnements */}
                <Route
                  path="/admin/subscriptions"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <AdminSubscriptionsManager />
                    </RoleProtectedRoute>
                  }
                />
                {/* Admin: Analytics Avancés */}
                <Route
                  path="/admin/subscriptions/analytics"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <AdminSubscriptionsAnalytics />
                    </RoleProtectedRoute>
                  }
                />
                {/* Admin: Gestion Coupons */}
                <Route
                  path="/admin/coupons"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <AdminCoupons />
                    </RoleProtectedRoute>
                  }
                />
                {/* Users: Mon abonnement */}
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
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <TeamManagement />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/company-links"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <CompanyLinksDashboard />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    COMMERCIAL & INFLUENCER DASHBOARDS
                ======================================== */}
                <Route
                  path="/commercial/dashboard"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <CommercialDashboard />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/influencer/dashboard"
                  element={
                    <RoleProtectedRoute allowedRoles={['influencer', 'admin']}>
                      <InfluencerDashboard />
                    </RoleProtectedRoute>
                  }
                />

                {/* ========================================
                    TOOLS & INTEGRATIONS
                ======================================== */}
                <Route
                  path="/ai-marketing"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <AIMarketing />
                    </RoleProtectedRoute>
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
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <Integrations />
                    </RoleProtectedRoute>
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

                {/* ========================================
                    FISCAL MODULE - COMPLETE SYSTEM (Maroc, France, USA)
                    Support multi-pays avec dashboards role-specific
                ======================================== */}
                
                {/* Admin - Dashboard fiscal global */}
                <Route
                  path="/fiscal/admin"
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <FiscalDashboardAdmin />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* Merchant - Dashboard fiscal marchand */}
                <Route
                  path="/fiscal/merchant"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <FiscalDashboardMerchant />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* Influencer - Dashboard fiscal influenceur (auto-entrepreneur) */}
                <Route
                  path="/fiscal/influencer"
                  element={
                    <RoleProtectedRoute allowedRoles={['influencer', 'admin']}>
                      <FiscalDashboardInfluencer />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* Commercial - Dashboard fiscal salarié */}
                <Route
                  path="/fiscal/commercial"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'admin']}>
                      <FiscalDashboardCommercial />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* Outils fiscaux - Accessibles selon rôle */}
                <Route
                  path="/fiscal/invoice/new"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <InvoiceGeneratorNew />
                    </RoleProtectedRoute>
                  }
                />
                
                <Route
                  path="/fiscal/vat/calculator"
                  element={
                    <ProtectedRoute>
                      <VATCalculator />
                    </ProtectedRoute>
                  }
                />
                
                <Route
                  path="/fiscal/vat/declare"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <TaxDeclarationForm />
                    </RoleProtectedRoute>
                  }
                />
                
                <Route
                  path="/fiscal/accounting/export"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <AccountingExport />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* Routes legacy - Redirection vers nouvelles routes */}
                <Route
                  path="/fiscal"
                  element={
                    <ProtectedRoute>
                      <TaxDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/fiscal/dashboard"
                  element={
                    <ProtectedRoute>
                      <TaxDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/fiscal/invoices"
                  element={
                    <ProtectedRoute>
                      <InvoiceGenerator />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/fiscal/settings"
                  element={
                    <ProtectedRoute>
                      <TaxSettings />
                    </ProtectedRoute>
                  }
                />

                {/* ========================================
                    INVOICES - Factures Influenceurs pour Impôts
                ======================================== */}
                <Route
                  path="/invoices/influencers"
                  element={
                    <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                      <InfluencerInvoicesPage />
                    </RoleProtectedRoute>
                  }
                />
                
                {/* ========================================
                    INVOICES - Factures Commerciaux pour Impôts
                ======================================== */}
                <Route
                  path="/invoices/commercials"
                  element={
                    <RoleProtectedRoute allowedRoles={['commercial', 'sales_rep', 'admin']}>
                      <CommercialInvoicesPage />
                    </RoleProtectedRoute>
                  }
                />
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
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <CompanySettings />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/affiliates"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <AffiliateSettings />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/registration"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <RegistrationSettings />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/mlm"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <MLMSettings />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/traffic-sources"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <TrafficSources />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/permissions"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <Permissions />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/users"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <Users />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/smtp"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <SMTP />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/emails"
            element={
              <RoleProtectedRoute allowedRoles={['merchant', 'admin']}>
                <Emails />
              </RoleProtectedRoute>
            }
          />
          <Route
            path="/settings/white-label"
            element={
              <RoleProtectedRoute allowedRoles={['admin']}>
                <WhiteLabel />
              </RoleProtectedRoute>
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
