import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, useInView } from 'framer-motion';
import { Check, X, Zap, TrendingUp, Users, Shield, Sparkles, ArrowRight, Globe } from 'lucide-react';
import axios from 'axios';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';
import { useCurrency } from '../context/CurrencyContext';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

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
      <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25 animate-pulse">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="text-lg font-display font-semibold text-surface-600 dark:text-surface-400">Chargement des plans...</div>
        </div>
      </div>
    );
  }

  const FadeIn = ({ children, delay = 0, className = '' }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-60px' });
    return (
      <motion.div ref={ref} initial={{ opacity: 0, y: 30, filter: 'blur(6px)' }}
        animate={isInView ? { opacity: 1, y: 0, filter: 'blur(0px)' } : {}}
        transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }} className={className}>
        {children}
      </motion.div>
    );
  };

  const renderFeature = (key, value, type = 'merchant') => {
    if (value === false) return null;
    let label = '', icon = <Check className="w-3.5 h-3.5 text-white" />, gradient = 'from-emerald-500 to-teal-500';
    if (type === 'merchant') {
      switch(key) {
        case 'user_accounts': label = `${value} compte(s) utilisateur`; break;
        case 'trackable_links_per_month': label = `${value} liens traçables/mois`; break;
        case 'reports': label = `Rapports ${value}`; break;
        case 'products': label = `${value === 'unlimited' ? 'Illimité' : value} produits`; break;
        case 'campaigns': label = `${value === 'unlimited' ? 'Illimité' : value} campagnes`; break;
        case 'analytics': label = `Analytics ${value}`; break;
        case 'ai_tools': label = 'Outils IA Marketing'; gradient = 'from-violet-500 to-purple-500'; break;
        case 'dedicated_manager': label = 'Manager dédié'; gradient = 'from-orange-500 to-rose-500'; break;
        case 'support': label = `Support ${value}`; gradient = 'from-blue-500 to-cyan-500'; break;
        case 'api_access': label = 'Accès API'; break;
        default: return null;
      }
    } else {
      switch(key) {
        case 'ai_tools': label = `Outils IA: ${value}`; gradient = 'from-violet-500 to-purple-500'; break;
        case 'campaigns_per_month': label = `Campagnes: ${value}`; break;
        case 'payments': label = `Paiements: ${value}`; break;
        case 'analytics': label = `Analytics: ${value}`; break;
        case 'priority_support': label = 'Support prioritaire 24/7'; gradient = 'from-blue-500 to-cyan-500'; break;
        case 'marketplace_access': label = 'Accès Marketplace'; break;
        case 'support': label = `Support ${value}`; break;
        default: return null;
      }
    }
    return (
      <div key={key} className="flex items-center gap-3">
        <div className={`w-5 h-5 rounded-full bg-gradient-to-br ${gradient} flex items-center justify-center flex-shrink-0`}>{icon}</div>
        <span className="text-sm text-surface-600 dark:text-surface-300">{label}</span>
      </div>
    );
  };

  return (
    <>
      <SEOHead {...SEO_CONFIG.pricing} />
      <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
        {/* ═══ Hero ═══ */}
        <div className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800 text-white">
          <div className="absolute inset-0 aurora-bg opacity-50" />
          <div className="absolute inset-0 noise-overlay" />
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-accent-400/15 rounded-full blur-3xl animate-morph" />

          <div className="relative pt-24 pb-20 text-center max-w-4xl mx-auto px-4">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-sm font-medium mb-8">
                <Sparkles className="w-4 h-4" /> Offre spéciale — 30 jours gratuits
              </div>

              <h1 className="text-4xl md:text-5xl lg:text-display-lg font-display font-extrabold mb-6 leading-tight">
                Maximisez chaque clic,{' '}
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-white to-purple-300">
                  générez des revenus
                </span>
              </h1>
              <p className="text-lg md:text-xl text-white/80 mb-10 font-light">
                Choisissez le plan qui correspond à vos ambitions
              </p>

              {/* Currency selector */}
              <div className="flex justify-center mb-8">
                <div className="inline-flex bg-white/10 backdrop-blur-md rounded-xl p-1 border border-white/20">
                  {Object.values(CURRENCIES).map((curr) => (
                    <button key={curr.code} onClick={() => changeCurrency(curr.code)}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${currency === curr.code ? 'bg-white text-primary-600 shadow-lg' : 'text-white/80 hover:bg-white/10'}`}>
                      {curr.symbol} {curr.code}
                    </button>
                  ))}
                </div>
              </div>

              {/* Plan Toggle */}
              <div className="inline-flex bg-white/10 backdrop-blur-md rounded-2xl p-1.5 border border-white/20">
                <button onClick={() => setSelectedPlan('merchants')}
                  className={`px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center gap-2 ${selectedPlan === 'merchants' ? 'bg-white text-primary-600 shadow-lg' : 'text-white/80 hover:bg-white/10'}`}>
                  <Users className="w-4 h-4" /> Entreprises
                </button>
                <button onClick={() => setSelectedPlan('influencers')}
                  className={`px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300 flex items-center gap-2 ${selectedPlan === 'influencers' ? 'bg-white text-primary-600 shadow-lg' : 'text-white/80 hover:bg-white/10'}`}>
                  <Zap className="w-4 h-4" /> Influenceurs & Commerciaux
                </button>
              </div>
            </motion.div>
          </div>

          {/* Wave */}
          <div className="absolute bottom-0 left-0 right-0">
            <svg viewBox="0 0 1440 80" fill="none" className="w-full">
              <path d="M0 80L60 72C120 64 240 48 360 42C480 36 600 40 720 44C840 48 960 52 1080 50C1200 48 1320 40 1380 36L1440 32V80H0Z" className="fill-surface-50 dark:fill-surface-950"/>
            </svg>
          </div>
        </div>

        {/* ═══ Pricing Cards — Merchants ═══ */}
        {selectedPlan === 'merchants' && (
          <div className="max-w-7xl mx-auto px-4 py-16 -mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {subscriptionPlans.merchants?.length > 0 ? subscriptionPlans.merchants.map((plan, i) => (
                <FadeIn key={plan.id} delay={i * 0.1}>
                  <div className={`glass-card p-6 h-full relative overflow-hidden group transition-all duration-500 ${i === 2 ? 'ring-2 ring-primary-500 dark:ring-primary-400 shadow-neon-indigo' : 'hover:shadow-neon-indigo dark:hover:shadow-neon-indigo'}`}>
                    {i === 2 && (
                      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 via-accent-500 to-primary-500 animate-gradient-x" />
                    )}
                    {i === 2 && (
                      <span className="badge-premium text-[10px] absolute top-3 right-3">POPULAIRE</span>
                    )}

                    <h3 className="text-xl font-display font-bold text-surface-900 dark:text-white mb-2">{plan.name}</h3>
                    <div className="mb-4">
                      {plan.price !== null ? (
                        <div className="flex items-baseline gap-1">
                          <span className="text-3xl font-display font-extrabold text-gradient">{plan.prices ? formatPrice(plan.prices[currency], currency) : formatPrice(plan.price, currency)}</span>
                          <span className="text-sm text-surface-500">/mois</span>
                        </div>
                      ) : (
                        <span className="text-2xl font-display font-bold text-gradient">Sur devis</span>
                      )}
                    </div>

                    <div className="mb-5 p-3 rounded-xl bg-surface-100 dark:bg-surface-800/50">
                      <div className="text-xs text-surface-500 dark:text-surface-400 mb-1">Commission par vente</div>
                      <div className="text-2xl font-display font-bold text-gradient">{plan.commission_rate}%</div>
                    </div>

                    <div className="space-y-2.5 mb-6">
                      {Object.entries(plan.features).map(([k, v]) => renderFeature(k, v, 'merchant'))}
                    </div>

                    <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} onClick={() => handlePlanSelect(plan)}
                      className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${i === 2 ? 'btn-premium' : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 hover:bg-primary-50 dark:hover:bg-primary-950 hover:text-primary-600 dark:hover:text-primary-400'}`}>
                      {plan.price === 0 ? 'Commencer gratuitement' : 'Choisir ce plan →'}
                    </motion.button>
                  </div>
                </FadeIn>
              )) : (
                <div className="col-span-full text-center py-12 glass-card">
                  <p className="text-surface-500 text-lg">Aucun plan disponible.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══ Pricing Cards — Influencers ═══ */}
        {selectedPlan === 'influencers' && (
          <div className="max-w-5xl mx-auto px-4 py-16 -mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {subscriptionPlans.influencers?.length > 0 ? subscriptionPlans.influencers.map((plan, i) => (
                <FadeIn key={plan.id} delay={i * 0.15}>
                  <div className={`glass-card p-8 h-full relative overflow-hidden group transition-all duration-500 ${i === 1 ? 'ring-2 ring-accent-500 dark:ring-accent-400 shadow-neon-purple' : 'hover:shadow-neon-purple dark:hover:shadow-neon-purple'}`}>
                    {i === 1 && <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-accent-500 via-primary-500 to-accent-500 animate-gradient-x" />}
                    {i === 1 && <span className="badge-premium text-[10px] absolute top-4 right-4">RECOMMANDÉ</span>}

                    <h3 className="text-2xl font-display font-bold text-surface-900 dark:text-white mb-2">{plan.name}</h3>
                    <div className="mb-5">
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-display font-extrabold text-gradient">{plan.prices ? formatPrice(plan.prices[currency], currency) : formatPrice(plan.price, currency)}</span>
                        <span className="text-sm text-surface-500">/mois</span>
                      </div>
                    </div>

                    <div className="mb-5 p-3 rounded-xl bg-surface-100 dark:bg-surface-800/50">
                      <div className="text-xs text-surface-500 dark:text-surface-400 mb-1">Frais de plateforme</div>
                      <div className="text-2xl font-display font-bold text-gradient">{plan.platform_fee_rate}%</div>
                    </div>

                    <div className="space-y-2.5 mb-8">
                      {Object.entries(plan.features).map(([k, v]) => renderFeature(k, v, 'influencer'))}
                    </div>

                    <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} onClick={() => handlePlanSelect(plan)}
                      className={`w-full py-3.5 rounded-xl font-semibold text-sm transition-all ${i === 1 ? 'btn-premium' : 'bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 hover:bg-accent-50 dark:hover:bg-accent-950 hover:text-accent-600 dark:hover:text-accent-400'}`}>
                      {plan.price === 0 ? 'Commencer gratuitement' : 'Choisir ce plan →'}
                    </motion.button>
                  </div>
                </FadeIn>
              )) : (
                <div className="col-span-full text-center py-12 glass-card">
                  <p className="text-surface-500 text-lg">Aucun plan disponible.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ═══ Why Section ═══ */}
        <section className="py-20 mesh-bg">
          <div className="max-w-7xl mx-auto px-4">
            <FadeIn className="text-center mb-14">
              <h2 className="text-3xl md:text-display-md font-display font-bold text-surface-900 dark:text-white">
                Pourquoi choisir <span className="text-gradient">ShareYourSales</span> ?
              </h2>
              <p className="mt-3 text-surface-500 dark:text-surface-400 text-lg">La plateforme d'affiliation la plus performante</p>
            </FadeIn>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { icon: TrendingUp, title: 'ROI Garanti', desc: 'Analyses temps réel et insights actionnables', gradient: 'from-primary-500 to-primary-700' },
                { icon: Shield, title: 'Transparence Totale', desc: 'Tracking précis de toutes vos performances', gradient: 'from-accent-500 to-accent-700' },
                { icon: Zap, title: 'Paiements Rapides', desc: 'Commissions rapides et sécurisées', gradient: 'from-cyan-500 to-blue-600' },
              ].map((f, i) => (
                <FadeIn key={i} delay={i * 0.15}>
                  <div className="glass-card p-8 text-center group hover:shadow-neon-indigo dark:hover:shadow-neon-indigo transition-all duration-500">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mx-auto mb-5 shadow-lg group-hover:scale-110 transition-transform`}>
                      <f.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-display font-bold text-surface-900 dark:text-white mb-2">{f.title}</h3>
                    <p className="text-surface-500 dark:text-surface-400">{f.desc}</p>
                  </div>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        {/* ═══ CTA ═══ */}
        <section className="relative py-20 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800">
            <div className="absolute inset-0 aurora-bg opacity-50" />
            <div className="absolute inset-0 noise-overlay" />
          </div>
          <div className="relative max-w-4xl mx-auto text-center px-4">
            <FadeIn>
              <h2 className="text-3xl md:text-display-md font-display font-bold text-white mb-6">
                Prêt à maximiser vos revenus ?
              </h2>
              <p className="text-lg text-white/80 mb-10">
                Rejoignez des milliers d'entreprises et d'influenceurs
              </p>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Link to="/register" className="inline-flex items-center gap-2 px-10 py-4 bg-white text-primary-600 rounded-2xl font-bold text-lg shadow-xl hover:shadow-2xl transition-shadow">
                  Commencer maintenant <ArrowRight className="w-5 h-5" />
                </Link>
              </motion.div>
              <p className="mt-6 text-white/60 text-sm">Aucune carte bancaire requise</p>
            </FadeIn>
          </div>
        </section>

        {/* ═══ Footer ═══ */}
        <footer className="py-8 border-t border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-950">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-sm text-surface-400">© {new Date().getFullYear()} ShareYourSales. Tous droits réservés.</p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default Pricing;
