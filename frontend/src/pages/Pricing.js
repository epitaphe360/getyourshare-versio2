import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Check, X, Zap, TrendingUp, Users, Shield, Sparkles, ArrowRight, Globe } from 'lucide-react';
import axios from 'axios';
import Navigation from '../components/Navigation';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';
import { useCurrency } from '../context/CurrencyContext';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import { API_URL } from '../config/api.config';
import '../pages/MarketplaceAnimations.css';

// Plans par défaut si l'API échoue
const DEFAULT_PLANS = {
  merchants: [
    {
      id: 1,
      name: "Starter",
      price: 0,
      prices: { EUR: 0, MAD: 0, USD: 0 },
      commission_rate: 20,
      features: {
        user_accounts: 1,
        trackable_links_per_month: 50,
        reports: "basiques",
        ai_tools: false,
        dedicated_manager: false,
        support: "email"
      }
    },
    {
      id: 2,
      name: "Pro",
      price: 49,
      prices: { EUR: 49, MAD: 490, USD: 55 },
      commission_rate: 15,
      features: {
        user_accounts: 3,
        trackable_links_per_month: 500,
        reports: "avancés",
        ai_tools: true,
        dedicated_manager: false,
        support: "prioritaire"
      }
    },
    {
      id: 3,
      name: "Business",
      price: 149,
      prices: { EUR: 149, MAD: 1490, USD: 165 },
      commission_rate: 10,
      features: {
        user_accounts: 10,
        trackable_links_per_month: 2000,
        reports: "complets",
        ai_tools: true,
        dedicated_manager: false,
        support: "24/7"
      }
    },
    {
      id: 4,
      name: "Enterprise",
      price: null,
      prices: { EUR: null, MAD: null, USD: null },
      commission_rate: 5,
      features: {
        user_accounts: "Illimité",
        trackable_links_per_month: "Illimité",
        reports: "personnalisés",
        ai_tools: true,
        dedicated_manager: true,
        support: "dédié"
      }
    }
  ],
  influencers: [
    {
      id: 5,
      name: "Free",
      price: 0,
      prices: { EUR: 0, MAD: 0, USD: 0 },
      platform_fee_rate: 25,
      features: {
        ai_tools: "limités",
        campaigns_per_month: 5,
        payments: "mensuels",
        analytics: "basiques",
        priority_support: false
      }
    },
    {
      id: 6,
      name: "Creator Pro",
      price: 29,
      prices: { EUR: 29, MAD: 290, USD: 32 },
      platform_fee_rate: 15,
      features: {
        ai_tools: "complets",
        campaigns_per_month: "Illimité",
        payments: "instantanés",
        analytics: "avancés",
        priority_support: true
      }
    }
  ]
};

const Pricing = () => {
  const [subscriptionPlans, setSubscriptionPlans] = useState(DEFAULT_PLANS);
  const [selectedPlan, setSelectedPlan] = useState('merchants');
  const [loading, setLoading] = useState(true);
  const { currency, changeCurrency, formatPrice, CURRENCIES } = useCurrency();
  const location = useLocation();
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchSubscriptionPlans();
    
    const params = new URLSearchParams(location.search);
    const role = params.get('role');
    if (role === 'influencer') {
      setSelectedPlan('influencers');
    } else if (role === 'merchant') {
      setSelectedPlan('merchants');
    }
  }, [location]);

  const handlePlanSelect = async (plan) => {
    if (!user) {
      const role = selectedPlan === 'merchants' ? 'merchant' : 'influencer';
      navigate(`/register?role=${role}&plan=${plan.name.toLowerCase().replace(/\s+/g, '-')}`);
      return;
    }

    try {
      // Appel à l'API pour mettre à jour l'abonnement
      // On utilise /upgrade qui gère maintenant la création si inexistant
      await api.post('/api/subscriptions/upgrade', {
        new_plan_id: plan.id,
        immediate: true
      });

      toast.success(`Plan ${plan.name} activé avec succès ! Redirection...`);
      
      // Petit délai pour l'UX
      setTimeout(() => {
        if (user.role === 'influencer') {
          navigate('/dashboard/influencer');
        } else {
          navigate('/dashboard/merchant');
        }
      }, 1500);
      
    } catch (error) {
      console.error("Error selecting plan:", error);
      toast.error("Erreur lors de la mise à jour du plan. Veuillez réessayer.");
    }
  };

  const fetchSubscriptionPlans = async () => {
    try {
      const response = await axios.get(`${API_URL}/subscription-plans`);
      if (response.data && (response.data.merchants?.length > 0 || response.data.influencers?.length > 0)) {
        setSubscriptionPlans(response.data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Erreur lors du chargement des plans:', error);
      // Utiliser les plans par défaut si l'API échoue
      setSubscriptionPlans(DEFAULT_PLANS);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-500">
          <div className="text-2xl font-bold text-white animate-pulse">Chargement des plans...</div>
        </div>
      </>
    );
  }

  return (
    <>
      <SEOHead {...SEO_CONFIG.pricing} />
      <Navigation />
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        {/* Hero Section - Ultra Dynamique */}
        <div className="relative bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-500 text-white overflow-hidden">
        {/* Animations de fond */}
        <div className="absolute inset-0">
          {/* Particules */}
          <div className="absolute w-3 h-3 bg-white/60 rounded-full top-[15%] left-[10%] animate-float"></div>
          <div className="absolute w-2 h-2 bg-white/40 rounded-full top-[70%] left-[80%] animate-float-delayed"></div>
          <div className="absolute w-4 h-4 bg-white/50 rounded-full top-[80%] left-[25%] animate-float-slow"></div>
          <div className="absolute w-2 h-2 bg-white/60 rounded-full top-[30%] left-[70%] animate-float"></div>
          <div className="absolute w-3 h-3 bg-white/30 rounded-full top-[50%] left-[45%] animate-float-delayed"></div>
          
          {/* Blobs animés */}
          <div className="absolute w-[500px] h-[500px] bg-gradient-to-br from-cyan-400/30 to-blue-600/30 rounded-full blur-3xl -top-48 -left-48 animate-blob"></div>
          <div className="absolute w-[400px] h-[400px] bg-gradient-to-br from-teal-400/30 to-cyan-600/30 rounded-full blur-3xl -bottom-32 -right-32 animate-blob animation-delay-2000"></div>
          <div className="absolute w-[350px] h-[350px] bg-gradient-to-br from-blue-400/20 to-teal-600/20 rounded-full blur-2xl top-1/3 left-1/2 transform -translate-x-1/2 animate-blob animation-delay-4000"></div>
        </div>
        
        <div className="relative pt-20 pb-16 text-center">
          <div className="max-w-4xl mx-auto px-4">
            <div className="inline-block mb-6 px-5 py-2.5 bg-white/25 backdrop-blur-md rounded-full animate-pulse-glow border border-white/30">
              <span className="text-sm font-bold">🚀 Offre spéciale - 30 jours gratuits</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-black mb-6 leading-tight">
              Maximisez chaque clic,<br />
              <span className="inline-block bg-gradient-to-r from-yellow-300 via-orange-300 to-yellow-400 bg-clip-text text-transparent animate-gradient">
                générez des revenus automatiques
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-12 opacity-95 font-medium">
              Choisissez le plan qui correspond à vos ambitions 💰
            </p>
            
            {/* Currency Selector */}
            <div className="flex justify-center mb-8">
              <div className="bg-white/20 backdrop-blur-lg rounded-xl p-1 flex items-center space-x-1 border border-white/30">
                {Object.values(CURRENCIES).map((curr) => (
                  <button
                    key={curr.code}
                    onClick={() => changeCurrency(curr.code)}
                    className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                      currency === curr.code
                        ? 'bg-white text-cyan-600 shadow-lg'
                        : 'text-white hover:bg-white/10'
                    }`}
                  >
                    {curr.symbol} {curr.code}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Plan Toggle - Ultra Moderne */}
            <div className="inline-flex bg-white/20 backdrop-blur-lg rounded-2xl shadow-2xl p-2 mb-12 border border-white/30">
              <button
                onClick={() => setSelectedPlan('merchants')}
                className={`px-8 py-4 rounded-xl font-bold transition-all duration-300 ${
                  selectedPlan === 'merchants'
                    ? 'bg-white text-cyan-600 shadow-xl scale-105'
                    : 'text-white hover:bg-white/10'
                }`}
              >
                <Users className="inline-block w-5 h-5 mr-2" />
                Pour les Entreprises
              </button>
              <button
                onClick={() => setSelectedPlan('influencers')}
                className={`px-8 py-4 rounded-xl font-bold transition-all duration-300 ${
                  selectedPlan === 'influencers'
                    ? 'bg-white text-cyan-600 shadow-xl scale-105'
                    : 'text-white hover:bg-white/10'
                }`}
              >
                <Zap className="inline-block w-5 h-5 mr-2" />
                Pour les Influenceurs & Commerciaux
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Cards - Merchants */}
      {selectedPlan === 'merchants' && (
        <div className="max-w-7xl mx-auto px-4 py-16 -mt-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {subscriptionPlans.merchants && subscriptionPlans.merchants.length > 0 ? (
              subscriptionPlans.merchants.map((plan, index) => (
              <div
                key={plan.id}
                className={`bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-500 hover-lift ${
                  index === 2 ? 'ring-4 ring-cyan-600 scale-105' : ''
                }`}
              >
                {index === 2 && (
                  <div className="bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-center py-2.5 text-sm font-bold animate-gradient">
                    ⭐ POPULAIRE ⭐
                  </div>
                )}
                
                <div className="p-6">
                  <h3 className="text-2xl font-black mb-4 bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    {plan.name}
                  </h3>
                  <div className="mb-6">
                    {plan.price !== null ? (
                      <>
                        <span className="text-5xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                          {plan.prices ? formatPrice(plan.prices[currency], currency) : formatPrice(plan.price, currency)}
                        </span>
                        <span className="text-gray-600 font-semibold">/mois</span>
                      </>
                    ) : (
                      <span className="text-4xl font-black bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                        Sur devis
                      </span>
                    )}
                  </div>
                  
                  <div className="mb-6 p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border-2 border-blue-100">
                    <div className="text-sm text-gray-600 mb-2 font-semibold">Commission par vente</div>
                    <div className="text-3xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                      {plan.commission_rate}%
                    </div>
                  </div>

                  <div className="space-y-3 mb-8">
                    {/* Dynamic Features Rendering */}
                    {Object.entries(plan.features).map(([key, value]) => {
                       if (value === false) return null;
                       let label = "";
                       let icon = <Check className="w-4 h-4 text-white" />;
                       let bg = "bg-gradient-to-br from-green-400 to-emerald-500";

                       switch(key) {
                           case 'user_accounts': label = `${value} compte(s) utilisateur`; break;
                           case 'trackable_links_per_month': label = `${value} liens traçables/mois`; break;
                           case 'reports': label = `Rapports ${value}`; break;
                           case 'products': label = `${value === 'unlimited' ? 'Illimité' : value} produits`; break;
                           case 'campaigns': label = `${value === 'unlimited' ? 'Illimité' : value} campagnes`; break;
                           case 'analytics': label = `Analytics ${value}`; break;
                           case 'ai_tools': 
                               label = "Outils IA Marketing"; 
                               icon = <Sparkles className="w-4 h-4 text-white" />;
                               bg = "bg-gradient-to-br from-purple-400 to-pink-500 animate-pulse";
                               break;
                           case 'dedicated_manager':
                               label = "Manager dédié";
                               icon = <Users className="w-4 h-4 text-white" />;
                               bg = "bg-gradient-to-br from-orange-400 to-red-500";
                               break;
                           case 'support':
                               label = `Support ${value}`;
                               icon = <Shield className="w-4 h-4 text-white" />;
                               bg = "bg-gradient-to-br from-blue-400 to-cyan-500";
                               break;
                           case 'api_access':
                               label = "Accès API";
                               break;
                           default:
                               return null; 
                       }
                       
                       return (
                        <div key={key} className="flex items-start">
                          <div className={`w-6 h-6 rounded-full ${bg} flex items-center justify-center mr-3 mt-0.5 flex-shrink-0`}>
                            {icon}
                          </div>
                          <span className="text-sm font-medium text-gray-700">{label}</span>
                        </div>
                       );
                    })}
                  </div>

                  <button
                    onClick={() => handlePlanSelect(plan)}
                    className={`block w-full text-center py-4 rounded-xl font-bold transition-all duration-300 shadow-lg hover:shadow-2xl transform hover:scale-105 ${
                      index === 2
                        ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:from-cyan-700 hover:to-blue-700 animate-gradient'
                        : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 hover:from-gray-200 hover:to-gray-300'
                    }`}
                  >
                    {plan.price === 0 ? '🎉 Commencer gratuitement' : (user && user.role === 'merchant' ? '🚀 Choisir ce plan' : '🚀 Choisir ce plan')}
                  </button>
                </div>
              </div>
            ))
            ) : (
              <div className="col-span-full text-center py-12 bg-white rounded-2xl shadow-xl">
                <div className="text-6xl mb-4">📦</div>
                <p className="text-gray-600 text-lg font-medium">Aucun plan disponible pour le moment.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pricing Cards - Influencers */}
      {selectedPlan === 'influencers' && (
        <div className="max-w-5xl mx-auto px-4 py-16 -mt-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {subscriptionPlans.influencers && subscriptionPlans.influencers.length > 0 ? (
              subscriptionPlans.influencers.map((plan, index) => (
              <div
                key={plan.id}
                className={`bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-500 hover-lift ${
                  index === 1 ? 'ring-4 ring-cyan-600 scale-105' : ''
                }`}
              >
                {index === 1 && (
                  <div className="bg-gradient-to-r from-cyan-600 to-teal-600 text-white text-center py-2.5 text-sm font-bold animate-gradient">
                    ⭐ RECOMMANDÉ ⭐
                  </div>
                )}
                
                <div className="p-8">
                  <h3 className="text-2xl font-black mb-4 bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                    {plan.name}
                  </h3>
                  <div className="mb-6">
                    <span className="text-5xl font-black bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                      {plan.prices ? formatPrice(plan.prices[currency], currency) : formatPrice(plan.price, currency)}
                    </span>
                    <span className="text-gray-600 font-semibold">/mois</span>
                  </div>
                  
                  <div className="mb-6 p-4 bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl border-2 border-cyan-100">
                    <div className="text-sm text-gray-600 mb-2 font-semibold">Frais de plateforme</div>
                    <div className="text-3xl font-black bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                      {plan.platform_fee_rate}%
                    </div>
                  </div>

                  <div className="space-y-3 mb-8">
                    {Object.entries(plan.features).map(([key, value]) => {
                       if (value === false) return null;
                       let label = "";
                       let icon = <Check className="w-4 h-4 text-white" />;
                       let bg = "bg-gradient-to-br from-green-400 to-emerald-500";

                       switch(key) {
                           case 'ai_tools': 
                               label = `Outils IA: ${value}`; 
                               icon = <Sparkles className="w-4 h-4 text-white" />;
                               bg = "bg-gradient-to-br from-purple-400 to-pink-500 animate-pulse";
                               break;
                           case 'campaigns_per_month': label = `Campagnes: ${value}`; break;
                           case 'payments': label = `Paiements: ${value}`; break;
                           case 'analytics': label = `Analytics: ${value}`; break;
                           case 'priority_support': 
                               label = "Support prioritaire 24/7";
                               icon = <Shield className="w-4 h-4 text-white" />;
                               bg = "bg-gradient-to-br from-cyan-400 to-blue-500";
                               break;
                           case 'marketplace_access':
                               label = "Accès Marketplace";
                               break;
                           case 'support':
                               label = `Support ${value}`;
                               break;
                           default: return null;
                       }

                       return (
                        <div key={key} className="flex items-start">
                          <div className={`w-6 h-6 rounded-full ${bg} flex items-center justify-center mr-3 mt-0.5 flex-shrink-0`}>
                            {icon}
                          </div>
                          <span className="text-sm font-medium text-gray-700">{label}</span>
                        </div>
                       );
                    })}
                  </div>

                  <button
                    onClick={() => handlePlanSelect(plan)}
                    className={`block w-full text-center py-4 rounded-xl font-bold transition-all duration-300 shadow-lg hover:shadow-2xl transform hover:scale-105 ${
                      index === 1
                        ? 'bg-gradient-to-r from-cyan-600 to-teal-600 text-white hover:from-cyan-700 hover:to-teal-700 animate-gradient'
                        : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 hover:from-gray-200 hover:to-gray-300'
                    }`}
                  >
                    {plan.price === 0 ? '🎉 Commencer gratuitement' : (user && user.role === 'influencer' ? '🚀 Passer à ce plan' : '🚀 Choisir ce plan')}
                  </button>
                </div>
              </div>
            ))
            ) : (
              <div className="col-span-full text-center py-12 bg-white rounded-2xl shadow-xl">
                <div className="text-6xl mb-4">📦</div>
                <p className="text-gray-600 text-lg font-medium">Aucun plan disponible pour le moment.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Features Section */}
      <div className="bg-gradient-to-br from-white to-blue-50 py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-4xl font-black text-center mb-4 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
            Pourquoi choisir GetYourShare ?
          </h2>
          <p className="text-center text-gray-600 mb-16 text-lg">La plateforme d'affiliation la plus performante du Maroc 🇲🇦</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <div className="text-center hover-lift bg-white p-8 rounded-2xl shadow-lg">
              <div className="bg-gradient-to-br from-blue-400 to-cyan-500 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                <TrendingUp className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">ROI Garanti 📈</h3>
              <p className="text-gray-600 leading-relaxed">
                Optimisez vos investissements marketing avec des analyses en temps réel et des insights actionnables
              </p>
            </div>
            <div className="text-center hover-lift bg-white p-8 rounded-2xl shadow-lg">
              <div className="bg-gradient-to-br from-cyan-400 to-teal-500 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                <Shield className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">Transparence Totale 🔍</h3>
              <p className="text-gray-600 leading-relaxed">
                Rapports détaillés et tracking précis de toutes vos performances en temps réel
              </p>
            </div>
            <div className="text-center hover-lift bg-white p-8 rounded-2xl shadow-lg">
              <div className="bg-gradient-to-br from-teal-400 to-green-500 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
                <Zap className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4 text-gray-900">Paiements Rapides ⚡</h3>
              <p className="text-gray-600 leading-relaxed">
                Recevez vos commissions rapidement et en toute sécurité via plusieurs méthodes de paiement
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-500 py-20 overflow-hidden">
        {/* Animations de fond */}
        <div className="absolute inset-0">
          <div className="absolute w-96 h-96 bg-white/10 rounded-full blur-3xl top-0 left-0 animate-blob"></div>
          <div className="absolute w-96 h-96 bg-white/10 rounded-full blur-3xl bottom-0 right-0 animate-blob animation-delay-2000"></div>
        </div>
        
        <div className="relative max-w-4xl mx-auto text-center px-4">
          <div className="inline-block mb-6 px-5 py-2.5 bg-white/25 backdrop-blur-md rounded-full border border-white/30">
            <span className="text-sm font-bold text-white">🎁 Offre limitée</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
            Prêt à maximiser vos revenus ?
          </h2>
          <p className="text-xl md:text-2xl text-white/95 mb-10 font-medium">
            Rejoignez des milliers d'entreprises et d'influenceurs qui font confiance à GetYourShare 🚀
          </p>
          <Link
            to="/register"
            className="inline-flex items-center bg-white text-cyan-600 px-10 py-5 rounded-2xl font-black text-lg hover:bg-gray-100 transition-all shadow-2xl hover:shadow-3xl transform hover:scale-105"
          >
            Commencer maintenant
            <ArrowRight className="ml-3 w-6 h-6" />
          </Link>
          <p className="mt-6 text-white/80 text-sm">Aucune carte bancaire requise • Démarrage instantané</p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-400">
            © 2024 ShareYourSales. Tous droits réservés.
          </p>
        </div>
      </footer>
      </div>
    </>
  );
};

export default Pricing;
