import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useInView, AnimatePresence } from 'framer-motion';
import CountUp from 'react-countup';
import {
  TrendingUp, Users, ShoppingBag, Sparkles, DollarSign,
  Target, Share2, BarChart3, Zap, CheckCircle, Shield,
  Globe, Award, ArrowRight, Star, ChevronRight,
  Link as LinkIcon, Eye, Lock, Smartphone, Briefcase, Menu, X,
  Rocket, Layers, Bot, CreditCard, PieChart, Activity
} from 'lucide-react';

/* ═══════════════════════════════════════════════════
   HOMEPAGE V3 — WORLD-CLASS PREMIUM DESIGN
   Glassmorphism · 3D Effects · Aurora · Animations
   ═══════════════════════════════════════════════════ */

// ─── Animated Section Wrapper ───
const FadeInSection = ({ children, delay = 0, direction = 'up', className = '' }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-80px' });

  const variants = {
    hidden: {
      opacity: 0,
      y: direction === 'up' ? 40 : direction === 'down' ? -40 : 0,
      x: direction === 'left' ? 40 : direction === 'right' ? -40 : 0,
      filter: 'blur(8px)',
    },
    visible: {
      opacity: 1, y: 0, x: 0, filter: 'blur(0px)',
      transition: { duration: 0.7, delay, ease: [0.25, 0.46, 0.45, 0.94] }
    }
  };

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      variants={variants}
      className={className}
    >
      {children}
    </motion.div>
  );
};

// ─── 3D Tilt Card ───
const TiltCard = ({ children, className = '' }) => {
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
  };

  const handleMouseLeave = () => {
    const card = cardRef.current;
    if (card) card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={`transition-transform duration-300 ease-out ${className}`}
      style={{ willChange: 'transform' }}
    >
      {children}
    </div>
  );
};

// ─── Floating Orbs (Background) ───
const FloatingOrbs = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl animate-float" />
    <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-accent-500/15 rounded-full blur-3xl animate-float-slow" />
    <div className="absolute bottom-1/4 left-1/2 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl animate-float-delayed" />
    <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-rose-500/8 rounded-full blur-3xl animate-morph" />
  </div>
);

// ─── Animated Counter Stat ───
const StatCounter = ({ end, suffix = '', prefix = '', label, icon: Icon }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <div ref={ref} className="text-center group">
      <div className="inline-flex items-center justify-center w-14 h-14 mb-3 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/20 group-hover:scale-110 group-hover:bg-white/20 transition-all duration-300">
        <Icon className="w-7 h-7 text-white" />
      </div>
      <div className="text-3xl md:text-4xl font-display font-extrabold text-white counter-value">
        {isInView ? (
          <CountUp start={0} end={end} duration={2.5} separator="," prefix={prefix} suffix={suffix} />
        ) : '0'}
      </div>
      <div className="text-sm text-white/70 mt-1 font-medium">{label}</div>
    </div>
  );
};

// ═══════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════
const HomepageV3 = () => {
  const navigate = useNavigate();
  const [mobileMenu, setMobileMenu] = useState(false);
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '30%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  const features = [
    { icon: LinkIcon, title: 'Liens Traçables', desc: 'Créez des liens uniques avec tracking en temps réel', gradient: 'from-blue-500 to-cyan-500', glow: 'group-hover:shadow-neon-cyan' },
    { icon: BarChart3, title: 'Analytics Avancés', desc: 'Dashboard temps réel avec métriques de conversion', gradient: 'from-primary-500 to-accent-500', glow: 'group-hover:shadow-neon-indigo' },
    { icon: DollarSign, title: 'Commissions Auto', desc: 'Paiements automatiques et transparents', gradient: 'from-emerald-500 to-teal-500', glow: 'group-hover:shadow-[0_0_20px_rgba(16,185,129,0.3)]' },
    { icon: Eye, title: 'Rapports Pro', desc: 'Analyses par produit, canal et influenceur', gradient: 'from-orange-500 to-rose-500', glow: 'group-hover:shadow-[0_0_20px_rgba(244,63,94,0.3)]' },
    { icon: Bot, title: 'IA Marketing', desc: 'Contenu et stratégies générés par intelligence artificielle', gradient: 'from-violet-500 to-purple-500', glow: 'group-hover:shadow-neon-purple' },
    { icon: Shield, title: 'Anti-Fraude', desc: 'Protection avancée avec détection automatique', gradient: 'from-amber-500 to-orange-500', glow: 'group-hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]' },
  ];

  const roles = [
    { icon: Briefcase, title: 'Entreprises', desc: 'Lancez votre programme d\'affiliation et boostez vos ventes grâce à un réseau de partenaires qualifiés.', features: ['Programme d\'affiliation', 'Gestion des produits', 'Analytics avancés', 'Anti-fraude'], gradient: 'from-primary-500 to-primary-700', delay: 0 },
    { icon: TrendingUp, title: 'Commerciaux', desc: 'Gérez vos leads, suivez vos performances et maximisez votre chiffre d\'affaires.', features: ['CRM intégré', 'Lead scoring', 'Suivi en temps réel', 'Commissions auto'], gradient: 'from-accent-500 to-accent-700', delay: 0.15 },
    { icon: Sparkles, title: 'Influenceurs', desc: 'Monétisez votre communauté en recommandant des produits que vous aimez.', features: ['Liens personnalisés', 'Dashboard dédié', 'Paiements rapides', 'Marketplace'], gradient: 'from-cyan-500 to-blue-600', delay: 0.3 },
  ];

  const testimonials = [
    { name: 'Sarah M.', role: 'CEO, TechStyle', text: 'Notre taux de conversion a augmenté de 340% en 3 mois. La plateforme est incroyablement intuitive.', avatar: 'S', rating: 5 },
    { name: 'Mohamed K.', role: 'Influenceur, 500k abonnés', text: 'Enfin une plateforme qui simplifie la monétisation. Les paiements sont rapides et transparents.', avatar: 'M', rating: 5 },
    { name: 'Julie D.', role: 'Directrice Marketing, BioFresh', text: 'Le ROI est exceptionnel. L\'IA marketing nous fait gagner des heures chaque semaine.', avatar: 'J', rating: 5 },
  ];

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-950 overflow-hidden">

      {/* ═══ NAVBAR ═══ */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-surface">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2 cursor-pointer"
              onClick={() => navigate('/')}
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
                <Share2 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-display font-bold text-gradient hidden sm:block">ShareYourSales</span>
            </motion.div>

            <div className="hidden md:flex items-center gap-8">
              {['Fonctionnalités', 'Tarifs', 'Marketplace'].map((item, i) => (
                <motion.button
                  key={item}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * i }}
                  onClick={() => navigate(item === 'Tarifs' ? '/pricing' : item === 'Marketplace' ? '/marketplace' : '#features')}
                  className="text-sm font-medium text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                >
                  {item}
                </motion.button>
              ))}
            </div>

            <div className="hidden md:flex items-center gap-3">
              <motion.button
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                onClick={() => navigate('/login')}
                className="px-5 py-2.5 text-sm font-semibold text-surface-700 dark:text-surface-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                Connexion
              </motion.button>
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/register')}
                className="btn-premium text-sm !py-2.5 !px-5"
              >
                Commencer gratuitement
              </motion.button>
            </div>

            <button className="md:hidden p-2" onClick={() => setMobileMenu(!mobileMenu)}>
              {mobileMenu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        <AnimatePresence>
          {mobileMenu && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-surface-200/50 dark:border-surface-700/50 bg-white/90 dark:bg-surface-900/90 backdrop-blur-xl"
            >
              <div className="px-4 py-4 space-y-3">
                {['Fonctionnalités', 'Tarifs', 'Marketplace'].map(item => (
                  <button key={item} onClick={() => { setMobileMenu(false); navigate(item === 'Tarifs' ? '/pricing' : item === 'Marketplace' ? '/marketplace' : '/'); }} className="block w-full text-left py-2 text-surface-700 dark:text-surface-300 font-medium">{item}</button>
                ))}
                <div className="flex gap-3 pt-2">
                  <button onClick={() => navigate('/login')} className="flex-1 py-2.5 text-center rounded-xl border border-surface-200 dark:border-surface-700 font-semibold text-sm">Connexion</button>
                  <button onClick={() => navigate('/register')} className="flex-1 py-2.5 text-center rounded-xl btn-premium text-sm">S'inscrire</button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* ═══ HERO SECTION ═══ */}
      <section ref={heroRef} className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
        {/* Aurora Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800">
          <div className="absolute inset-0 aurora-bg" />
          <FloatingOrbs />
          <div className="absolute inset-0 noise-overlay" />
        </div>

        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/90 text-sm font-medium mb-8"
            >
              <Sparkles className="w-4 h-4" />
              Plateforme d'affiliation #1 au Maroc
              <ChevronRight className="w-4 h-4" />
            </motion.div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-display-xl font-display font-extrabold text-white leading-tight mb-6">
              <span className="block">Chaque partage</span>
              <span className="block mt-2 bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 via-white to-purple-300">
                devient une vente
              </span>
            </h1>

            <p className="max-w-2xl mx-auto text-lg md:text-xl text-white/80 mb-10 font-light leading-relaxed">
              Connectez entreprises, commerciaux et influenceurs sur une plateforme unique.
              Générez des revenus à chaque recommandation.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/register')}
                className="group relative px-8 py-4 bg-white text-primary-600 font-bold rounded-2xl text-lg shadow-xl shadow-black/20 hover:shadow-2xl transition-shadow overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Démarrer gratuitement
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-primary-50 to-accent-50 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/pricing')}
                className="btn-glass text-lg"
              >
                Voir les tarifs
              </motion.button>
            </div>
          </motion.div>

          {/* Stats Bar */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            <StatCounter end={5000} suffix="+" icon={Users} label="Utilisateurs actifs" />
            <StatCounter end={12} suffix="M+" prefix="" icon={DollarSign} label="Volume de ventes" />
            <StatCounter end={98} suffix="%" icon={Activity} label="Satisfaction client" />
            <StatCounter end={150} suffix="+" icon={Globe} label="Pays couverts" />
          </motion.div>
        </motion.div>

        {/* Wave separator */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
            <path d="M0 120L60 108C120 96 240 72 360 66C480 60 600 72 720 78C840 84 960 84 1080 78C1200 72 1320 60 1380 54L1440 48V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" className="fill-surface-50 dark:fill-surface-950"/>
          </svg>
        </div>
      </section>

      {/* ═══ FEATURES SECTION ═══ */}
      <section id="features" className="relative py-24 md:py-32 mesh-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FadeInSection className="text-center mb-16">
            <span className="badge-premium mb-4 inline-flex">
              <Zap className="w-3.5 h-3.5 mr-1.5" /> Fonctionnalités
            </span>
            <h2 className="text-3xl md:text-display-md font-display font-bold text-surface-900 dark:text-white">
              Tout ce dont vous avez <span className="text-gradient">besoin</span>
            </h2>
            <p className="mt-4 text-lg text-surface-500 dark:text-surface-400 max-w-2xl mx-auto">
              Des outils puissants conçus pour maximiser vos performances d'affiliation
            </p>
          </FadeInSection>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <FadeInSection key={i} delay={i * 0.1}>
                <TiltCard>
                  <div className={`group glass-card p-6 h-full cursor-default ${f.glow} transition-shadow duration-500`}>
                    <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${f.gradient} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                      <f.icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-display font-bold text-surface-900 dark:text-white mb-2">{f.title}</h3>
                    <p className="text-surface-500 dark:text-surface-400 text-sm leading-relaxed">{f.desc}</p>
                  </div>
                </TiltCard>
              </FadeInSection>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-24 md:py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-surface-50 via-primary-50/30 to-surface-50 dark:from-surface-950 dark:via-primary-950/20 dark:to-surface-950" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FadeInSection className="text-center mb-16">
            <span className="badge-premium mb-4 inline-flex">
              <Rocket className="w-3.5 h-3.5 mr-1.5" /> Comment ça marche
            </span>
            <h2 className="text-3xl md:text-display-md font-display font-bold text-surface-900 dark:text-white">
              Commencez en <span className="text-gradient">3 étapes</span>
            </h2>
          </FadeInSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connecting line */}
            <div className="hidden md:block absolute top-24 left-1/6 right-1/6 h-0.5 bg-gradient-to-r from-primary-500 via-accent-500 to-cyan-500 opacity-20" />

            {[
              { step: '01', title: 'Inscrivez‑vous', desc: 'Créez votre compte gratuitement en moins de 2 minutes', icon: Sparkles },
              { step: '02', title: 'Connectez‑vous', desc: 'Trouvez vos partenaires idéaux sur notre marketplace', icon: Users },
              { step: '03', title: 'Gagnez', desc: 'Générez des revenus à chaque vente ou recommandation', icon: DollarSign },
            ].map((s, i) => (
              <FadeInSection key={i} delay={i * 0.2}>
                <div className="relative text-center group">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-primary-500 to-accent-500 text-white text-2xl font-display font-bold mb-6 shadow-xl shadow-primary-500/25 group-hover:scale-110 group-hover:shadow-2xl group-hover:shadow-primary-500/30 transition-all duration-500">
                    <s.icon className="w-9 h-9" />
                  </div>
                  <div className="absolute -top-2 -right-2 md:right-auto md:-top-3 md:left-1/2 md:ml-6 w-8 h-8 rounded-full bg-white dark:bg-surface-800 shadow-lg flex items-center justify-center text-xs font-bold text-primary-600 dark:text-primary-400 border-2 border-primary-200 dark:border-primary-800">
                    {s.step}
                  </div>
                  <h3 className="text-xl font-display font-bold text-surface-900 dark:text-white mb-2">{s.title}</h3>
                  <p className="text-surface-500 dark:text-surface-400">{s.desc}</p>
                </div>
              </FadeInSection>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ ROLES SECTION ═══ */}
      <section className="py-24 md:py-32 relative">
        <div className="absolute inset-0 mesh-bg" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FadeInSection className="text-center mb-16">
            <span className="badge-premium mb-4 inline-flex">
              <Layers className="w-3.5 h-3.5 mr-1.5" /> Pour chaque profil
            </span>
            <h2 className="text-3xl md:text-display-md font-display font-bold text-surface-900 dark:text-white">
              Une solution <span className="text-gradient">adaptée</span>
            </h2>
          </FadeInSection>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {roles.map((r, i) => (
              <FadeInSection key={i} delay={r.delay}>
                <TiltCard className="h-full">
                  <div className="glass-card p-8 h-full relative overflow-hidden group">
                    {/* Glow orb */}
                    <div className={`absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br ${r.gradient} rounded-full blur-3xl opacity-10 group-hover:opacity-25 transition-opacity duration-700`} />

                    <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${r.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                      <r.icon className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="text-2xl font-display font-bold text-surface-900 dark:text-white mb-3">{r.title}</h3>
                    <p className="text-surface-500 dark:text-surface-400 mb-6 leading-relaxed">{r.desc}</p>
                    <ul className="space-y-3">
                      {r.features.map((feat, fi) => (
                        <li key={fi} className="flex items-center gap-3 text-sm">
                          <div className={`w-5 h-5 rounded-full bg-gradient-to-br ${r.gradient} flex items-center justify-center flex-shrink-0`}>
                            <CheckCircle className="w-3 h-3 text-white" />
                          </div>
                          <span className="text-surface-600 dark:text-surface-300">{feat}</span>
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={() => navigate('/register')}
                      className="mt-8 w-full py-3 rounded-xl font-semibold text-sm bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 hover:bg-primary-50 dark:hover:bg-primary-950 hover:text-primary-600 dark:hover:text-primary-400 transition-all group-hover:bg-primary-50 dark:group-hover:bg-primary-950 group-hover:text-primary-600 dark:group-hover:text-primary-400"
                    >
                      Commencer →
                    </button>
                  </div>
                </TiltCard>
              </FadeInSection>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ TESTIMONIALS ═══ */}
      <section className="py-24 md:py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800">
          <div className="absolute inset-0 aurora-bg opacity-50" />
          <div className="absolute inset-0 noise-overlay" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <FadeInSection className="text-center mb-16">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/90 text-sm font-medium mb-4">
              <Star className="w-3.5 h-3.5" /> Témoignages
            </span>
            <h2 className="text-3xl md:text-display-md font-display font-bold text-white">
              Ils nous font confiance
            </h2>
          </FadeInSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t, i) => (
              <FadeInSection key={i} delay={i * 0.15}>
                <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/15 transition-all duration-300 hover:-translate-y-2 h-full">
                  <div className="flex gap-1 mb-4">
                    {[...Array(t.rating)].map((_, si) => (
                      <Star key={si} className="w-4 h-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                  <p className="text-white/90 mb-6 leading-relaxed italic">"{t.text}"</p>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-bold text-sm">
                      {t.avatar}
                    </div>
                    <div>
                      <div className="text-white font-semibold text-sm">{t.name}</div>
                      <div className="text-white/60 text-xs">{t.role}</div>
                    </div>
                  </div>
                </div>
              </FadeInSection>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ CTA FINAL ═══ */}
      <section className="py-24 md:py-32 relative overflow-hidden mesh-bg">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <FadeInSection>
            <h2 className="text-3xl md:text-display-lg font-display font-bold text-surface-900 dark:text-white mb-6">
              Prêt à transformer vos <span className="text-gradient">recommandations en revenus</span> ?
            </h2>
            <p className="text-lg text-surface-500 dark:text-surface-400 mb-10 max-w-2xl mx-auto">
              Rejoignez des milliers d'entreprises et d'influenceurs qui utilisent ShareYourSales pour développer leur business.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/register')}
                className="btn-premium text-lg !px-10 !py-4"
              >
                <span className="flex items-center gap-2">
                  Commencer gratuitement <ArrowRight className="w-5 h-5" />
                </span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/contact')}
                className="px-10 py-4 rounded-xl font-semibold text-lg border-2 border-surface-200 dark:border-surface-700 text-surface-700 dark:text-surface-300 hover:border-primary-300 dark:hover:border-primary-600 hover:text-primary-600 dark:hover:text-primary-400 transition-all"
              >
                Nous contacter
              </motion.button>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="py-16 border-t border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                  <Share2 className="w-4.5 h-4.5 text-white" />
                </div>
                <span className="text-lg font-display font-bold text-gradient">ShareYourSales</span>
              </div>
              <p className="text-sm text-surface-500 dark:text-surface-400 leading-relaxed">
                La plateforme d'affiliation qui connecte entreprises, commerciaux et influenceurs.
              </p>
            </div>
            {[
              { title: 'Produit', links: ['Fonctionnalités', 'Tarifs', 'Marketplace', 'API'] },
              { title: 'Entreprise', links: ['À propos', 'Contact', 'Blog', 'Carrières'] },
              { title: 'Légal', links: ['Confidentialité', 'CGU', 'Mentions légales'] },
            ].map((col, i) => (
              <div key={i}>
                <h4 className="font-display font-semibold text-surface-900 dark:text-white mb-4">{col.title}</h4>
                <ul className="space-y-2.5">
                  {col.links.map((link, li) => (
                    <li key={li}>
                      <button className="text-sm text-surface-500 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                        {link}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="pt-8 border-t border-surface-200 dark:border-surface-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-surface-400">
              © {new Date().getFullYear()} ShareYourSales. Tous droits réservés.
            </p>
            <div className="flex items-center gap-6">
              <span className="text-xs text-surface-400">Fait avec ❤️ au Maroc</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomepageV3;
