import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  TrendingUp, Users, BarChart3, Shield, Zap, Globe, 
  Menu, X, Check, ArrowRight, Star,
  Target, DollarSign, Award, Link2,
  Eye, Wallet, Lock, FileCheck, Building2, UserCheck,
  ShoppingBag, Sparkles, Rocket, CheckCircle2, Play
} from 'lucide-react';
import Button from '../components/common/Button';

const LandingPageNew = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSpace, setActiveSpace] = useState('entreprises');
  const [stats, setStats] = useState({ affiliates: 0, companies: 0, commissions: 0 });
  const [loading] = useState(false);

  // Animation stats
  useEffect(() => {
    const intervals = [
      setInterval(() => setStats(prev => ({ ...prev, affiliates: Math.min(prev.affiliates + 500, 15000) })), 30),
      setInterval(() => setStats(prev => ({ ...prev, companies: Math.min(prev.companies + 20, 500) })), 50),
      setInterval(() => setStats(prev => ({ ...prev, commissions: Math.min(prev.commissions + 200000, 5000000) })), 20)
    ];
    return () => intervals.forEach(clearInterval);
  }, []);

  // Plans tarifaires en DIRHAM MAROCAIN
  const pricingPlans = [
    {
      name: "Small",
      price: "199",
      currency: "DH",
      period: "mois",
      description: "Idéal pour lancer votre activité",
      features: [
        "2 membres de l'équipe",
        "1 nom de domaine",
        "Tracking intelligent",
        "Dashboard temps réel",
        "Support par email",
        "Rapports mensuels",
        "Commissions automatiques"
      ],
      cta: "Démarrer maintenant",
      popular: false,
      highlight: false
    },
    {
      name: "Medium",
      price: "499",
      currency: "DH",
      period: "mois",
      description: "Pour entreprises en croissance",
      features: [
        "10 membres de l'équipe",
        "2 noms de domaine",
        "Tout de Small +",
        "Système MLM avancé",
        "White-label complet",
        "API REST complète",
        "Support prioritaire",
        "Analytics avancés",
        "Intégrations premium"
      ],
      cta: "Essayer gratuitement",
      popular: true,
      highlight: true
    },
    {
      name: "Large",
      price: "799",
      currency: "DH",
      period: "mois",
      description: "Solution enterprise complète",
      features: [
        "30 membres de l'équipe",
        "Domaines illimités",
        "Tout de Medium +",
        "Serveur dédié",
        "Support 24/7",
        "SLA garanti 99.9%",
        "Formation équipe",
        "Développements custom",
        "Account manager dédié"
      ],
      cta: "Contacter un expert",
      popular: false,
      highlight: false
    },
    {
      name: "Marketplace",
      price: "99",
      currency: "DH",
      period: "mois",
      description: "Pour commerciaux & influenceurs",
      features: [
        "Accès marketplace exclusif",
        "Centaines de produits",
        "Commissions immédiates",
        "Dashboard personnel",
        "Liens de tracking illimités",
        "Support communauté",
        "Formations gratuites",
        "Paiements automatiques"
      ],
      cta: "Rejoindre le marketplace",
      popular: false,
      highlight: false,
      special: true
    }
  ];

  // 4 étapes du processus
  const processSteps = [
    {
      number: "01",
      icon: <Link2 className="w-10 h-10" />,
      title: "Générez votre lien",
      description: "Créez en 2 clics des liens de tracking personnalisés avec tous les paramètres UTM automatiques.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      number: "02",
      icon: <Rocket className="w-10 h-10" />,
      title: "Partagez-le partout",
      description: "Diffusez vos liens sur tous vos canaux : réseaux sociaux, email, SMS, blog, vidéos...",
      color: "from-purple-500 to-pink-500"
    },
    {
      number: "03",
      icon: <Eye className="w-10 h-10" />,
      title: "Suivez en temps réel",
      description: "Visualisez instantanément chaque clic, chaque vente, chaque commission.",
      color: "from-orange-500 to-red-500"
    },
    {
      number: "04",
      icon: <Wallet className="w-10 h-10" />,
      title: "Encaissez vos commissions",
      description: "Paiements 100% automatiques. Virement bancaire, PayPal, ou portefeuille virtuel.",
      color: "from-green-500 to-emerald-500"
    }
  ];

  // Trois espaces utilisateurs
  const userSpaces = {
    entreprises: {
      icon: <Building2 className="w-12 h-12" />,
      title: "Espace Entreprises",
      subtitle: "Développez votre force de vente exponentielle",
      description: "Créez votre réseau d'affiliés en quelques minutes. Gérez vos produits, définissez vos commissions, et laissez des milliers de commerciaux vendre pour vous.",
      benefits: [
        { icon: <Users className="w-5 h-5" />, text: "Recrutez des affiliés qualifiés partout au Maroc" },
        { icon: <BarChart3 className="w-5 h-5" />, text: "Suivez chaque vente avec précision chirurgicale" },
        { icon: <DollarSign className="w-5 h-5" />, text: "Payez uniquement à la performance (5% commission)" },
        { icon: <Shield className="w-5 h-5" />, text: "Protection anti-fraude & conformité RGPD" },
        { icon: <Zap className="w-5 h-5" />, text: "Calcul automatique des commissions multi-niveaux" },
        { icon: <Target className="w-5 h-5" />, text: "Campagnes ciblées par région, profil, performance" }
      ],
      cta: "Créer mon réseau d'affiliés",
      pricing: "À partir de 199 DH/mois",
      color: "blue"
    },
    commerciaux: {
      icon: <UserCheck className="w-12 h-12" />,
      title: "Espace Commerciaux & Influenceurs",
      subtitle: "Transformez votre audience en revenus",
      description: "Accédez à des centaines de produits marocains à promouvoir. Générez vos liens, partagez-les, et gagnez des commissions.",
      benefits: [
        { icon: <ShoppingBag className="w-5 h-5" />, text: "Catalogue exclusif de produits vérifiés" },
        { icon: <Link2 className="w-5 h-5" />, text: "Liens de tracking illimités et personnalisables" },
        { icon: <Wallet className="w-5 h-5" />, text: "Commissions versées automatiquement" },
        { icon: <BarChart3 className="w-5 h-5" />, text: "Dashboard personnel avec stats temps réel" },
        { icon: <Sparkles className="w-5 h-5" />, text: "Formations gratuites & conseils d'experts" },
        { icon: <Award className="w-5 h-5" />, text: "Programme de récompenses et bonus" }
      ],
      cta: "Commencer à gagner",
      pricing: "99 DH/mois seulement",
      color: "purple"
    },
    marketplace: {
      icon: <ShoppingBag className="w-12 h-12" />,
      title: "Marketplace Exclusif",
      subtitle: "La première plateforme B2B/B2C hybride au Maroc",
      description: "Vendeurs et acheteurs se rencontrent dans un écosystème sécurisé. Paiements garantis, produits vérifiés.",
      benefits: [
        { icon: <CheckCircle2 className="w-5 h-5" />, text: "Centaines d'entreprises marocaines vérifiées" },
        { icon: <Globe className="w-5 h-5" />, text: "Tous secteurs : mode, tech, formation, services..." },
        { icon: <Lock className="w-5 h-5" />, text: "Transactions 100% sécurisées et traçables" },
        { icon: <FileCheck className="w-5 h-5" />, text: "Vérification RC, IF, CNIE obligatoire" },
        { icon: <DollarSign className="w-5 h-5" />, text: "Commissions attractives et versements rapides" },
        { icon: <Star className="w-5 h-5" />, text: "Notation transparente vendeurs/acheteurs" }
      ],
      cta: "Explorer le marketplace",
      pricing: "Accès : 99 DH/mois",
      color: "emerald"
    }
  };

  // TOUTES LES FONCTIONNALITÉS UNIQUES - Section enrichie
  const coreFeatures = [
    {
      icon: <Link2 className="w-8 h-8" />,
      title: "Liens traçables intelligents",
      description: "Génération automatique avec UTM, short links, QR codes, et attribution multi-touch.",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "Dashboard temps réel",
      description: "Visualisation instantanée : clics, conversions, commissions, ROI, taux de conversion.",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: <DollarSign className="w-8 h-8" />,
      title: "Commissions automatiques",
      description: "Calcul instantané, MLM multi-niveaux, règles personnalisables, paiements schedulés.",
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: <FileCheck className="w-8 h-8" />,
      title: "Rapports avancés",
      description: "Exports Excel/PDF, analyses comparatives, prévisions IA, alertes intelligentes.",
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: <Target className="w-8 h-8" />,
      title: "Analyse comportementale",
      description: "Heatmaps, parcours utilisateur, A/B testing, optimisation conversions.",
      gradient: "from-indigo-500 to-purple-500"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Sécurité maximale",
      description: "Anti-fraude IA, conformité RGPD, encryption AES-256, audits permanents.",
      gradient: "from-red-500 to-pink-500"
    }
  ];

  // OUTILS EXCLUSIFS PAR TYPE D'UTILISATEUR - Ce qui rend ShareYourSales unique
  const uniqueToolsByRole = {
    merchant: [
      {
        icon: <Sparkles className="w-6 h-6" />,
        title: "AI Recommendations & Insights",
        description: "Intelligence artificielle qui analyse vos ventes et suggère les meilleures stratégies, produits à promouvoir, et périodes optimales.",
        badge: "IA"
      },
      {
        icon: <Play className="w-6 h-6" />,
        title: "Live Shopping Multi-plateformes",
        description: "Vendez en direct sur Instagram Live, TikTok Live, YouTube Live et Facebook Live avec tracking automatique des ventes.",
        badge: "LIVE"
      },
      {
        icon: <FileCheck className="w-6 h-6" />,
        title: "Content Studio",
        description: "Créez du contenu professionnel en quelques clics : templates personnalisables, planification multi-canaux, bibliothèque de médias.",
        badge: "STUDIO"
      },
      {
        icon: <Award className="w-6 h-6" />,
        title: "Gamification complète",
        description: "Système de badges, missions, classements et récompenses pour motiver vos affiliés et commerciaux.",
        badge: "GAME"
      },
      {
        icon: <Users className="w-6 h-6" />,
        title: "Parrainage multi-niveaux (MLM)",
        description: "Créez un réseau exponentiel : vos affiliés recrutent d'autres affiliés, et vous gagnez sur plusieurs niveaux.",
        badge: "MLM"
      },
      {
        icon: <Zap className="w-6 h-6" />,
        title: "WhatsApp Business Integration",
        description: "Envoyez des campagnes automatiques, notifications de vente, et messages personnalisés via WhatsApp Business API.",
        badge: "WHATSAPP"
      },
      {
        icon: <ShoppingBag className="w-6 h-6" />,
        title: "TikTok Shop Sync",
        description: "Synchronisation automatique de vos produits TikTok Shop, gestion des commandes et tracking des ventes.",
        badge: "TIKTOK"
      },
      {
        icon: <BarChart3 className="w-6 h-6" />,
        title: "ROI Calculator & Predictive Analytics",
        description: "Calculez votre retour sur investissement en temps réel et prédisez vos revenus futurs avec l'IA prédictive.",
        badge: "ANALYTICS"
      },
      {
        icon: <Star className="w-6 h-6" />,
        title: "Trust Score System",
        description: "Score de confiance automatique pour vendeurs et acheteurs, basé sur historique, vérifications et comportement.",
        badge: "TRUST"
      },
      {
        icon: <Wallet className="w-6 h-6" />,
        title: "Paiements multiples",
        description: "PayPal, virement bancaire, Mobile Money Maroc (Cash Plus, Orange Money), portefeuille virtuel intégré.",
        badge: "PAY"
      },
      {
        icon: <Globe className="w-6 h-6" />,
        title: "White-Label & API complète",
        description: "Votre marque, votre domaine, vos couleurs. API REST complète pour intégrer ShareYourSales dans vos systèmes existants.",
        badge: "API"
      },
      {
        icon: <Target className="w-6 h-6" />,
        title: "Segmentation intelligente",
        description: "Ciblez vos affiliés par région, performance, audience, et créez des campagnes ultra-personnalisées.",
        badge: "TARGETING"
      }
    ],
    influencer: [
      {
        icon: <ShoppingBag className="w-6 h-6" />,
        title: "Marketplace exclusif vérifié",
        description: "Accès à des centaines de produits marocains de qualité, tous vérifiés (RC, IF, CNIE).",
        badge: "MARKET"
      },
      {
        icon: <Sparkles className="w-6 h-6" />,
        title: "AI Product Recommendations",
        description: "L'IA vous suggère les produits les plus rentables pour VOTRE audience spécifique.",
        badge: "IA"
      },
      {
        icon: <Play className="w-6 h-6" />,
        title: "Live Shopping Integration",
        description: "Vendez pendant vos lives Instagram, TikTok, YouTube avec liens automatiques et tracking.",
        badge: "LIVE"
      },
      {
        icon: <FileCheck className="w-6 h-6" />,
        title: "Content Studio",
        description: "Templates professionnels pour stories, posts, vidéos - créez du contenu qui convertit.",
        badge: "STUDIO"
      },
      {
        icon: <Link2 className="w-6 h-6" />,
        title: "Liens illimités personnalisables",
        description: "Short links branded, QR codes personnalisés, liens bio optimisés, UTM automatiques.",
        badge: "LINKS"
      },
      {
        icon: <Award className="w-6 h-6" />,
        title: "Gamification & Badges",
        description: "Débloquez des badges, accomplissez des missions, montez dans les classements et gagnez des bonus.",
        badge: "GAME"
      },
      {
        icon: <Users className="w-6 h-6" />,
        title: "Programme de parrainage",
        description: "Recrutez d'autres influenceurs et gagnez une commission sur leurs ventes à vie.",
        badge: "REFER"
      },
      {
        icon: <BarChart3 className="w-6 h-6" />,
        title: "Dashboard analytics avancé",
        description: "Stats temps réel : clics, conversions, meilleurs produits, revenus prévisionnels, ROI par produit.",
        badge: "ANALYTICS"
      },
      {
        icon: <Wallet className="w-6 h-6" />,
        title: "Paiements rapides multiples",
        description: "PayPal, virement, Mobile Money - recevez vos commissions automatiquement chaque semaine.",
        badge: "PAY"
      },
      {
        icon: <Zap className="w-6 h-6" />,
        title: "Formations gratuites",
        description: "Accès à des masterclasses, webinaires, et ressources pour maximiser vos conversions.",
        badge: "LEARN"
      }
    ]
  };

  // POURQUOI SHAREYOURSALES EST UNIQUE
  const whyUnique = [
    {
      icon: <Sparkles className="w-8 h-8" />,
      title: "IA intégrée partout",
      points: [
        "Recommandations produits personnalisées",
        "Prédictions de revenus avec machine learning",
        "Détection anti-fraude automatique",
        "Suggestions stratégiques en temps réel"
      ]
    },
    {
      icon: <Play className="w-8 h-8" />,
      title: "Live Shopping révolutionnaire",
      points: [
        "4 plateformes : Instagram, TikTok, YouTube, Facebook",
        "Tracking automatique pendant les lives",
        "Commissions calculées en temps réel",
        "Première au Maroc avec cette technologie"
      ]
    },
    {
      icon: <Award className="w-8 h-8" />,
      title: "Gamification complète",
      points: [
        "Système de badges et missions",
        "Classements par région et secteur",
        "Récompenses et bonus progressifs",
        "Compétitions et challenges"
      ]
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "MLM & Parrainage puissant",
      points: [
        "Commissions multi-niveaux illimitées",
        "Recrutement en cascade",
        "Réseau exponentiel automatique",
        "Suivi généalogique complet"
      ]
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Intégrations exclusives",
      points: [
        "WhatsApp Business API",
        "TikTok Shop automatique",
        "API REST complète",
        "White-label personnalisable"
      ]
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Sécurité maximale Maroc",
      points: [
        "Vérification RC/IF/CNIE obligatoire",
        "Conformité RGPD + lois marocaines",
        "Trust Score pour chaque utilisateur",
        "Paiements 100% sécurisés"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-lg shadow-sm sticky top-0 z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ShareYourSales
              </span>
            </Link>

            {/* Desktop Menu */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#process" className="text-gray-700 hover:text-blue-600 font-medium transition">Comment ça marche</a>
              <a href="#spaces" className="text-gray-700 hover:text-blue-600 font-medium transition">Nos espaces</a>
              <a href="#features" className="text-gray-700 hover:text-blue-600 font-medium transition">Fonctionnalités</a>
              <a href="#pricing" className="text-gray-700 hover:text-blue-600 font-medium transition">Tarifs</a>
              <Button variant="outline" disabled={loading} onClick={() => navigate('/login')}>
                Connexion
              </Button>
              <Button disabled={loading} onClick={() => navigate('/register')} className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl">
                <Sparkles className="w-4 h-4 mr-2" />
                Commencer gratuitement
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <button disabled={loading} onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-gray-700 hover:text-blue-600">
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100">
            <div className="px-4 py-4 space-y-3">
              <a href="#process" className="block text-gray-700 hover:text-blue-600 font-medium py-2">Comment ça marche</a>
              <a href="#spaces" className="block text-gray-700 hover:text-blue-600 font-medium py-2">Nos espaces</a>
              <a href="#features" className="block text-gray-700 hover:text-blue-600 font-medium py-2">Fonctionnalités</a>
              <a href="#pricing" className="block text-gray-700 hover:text-blue-600 font-medium py-2">Tarifs</a>
              <Button variant="outline" disabled={loading} onClick={() => navigate('/login')} className="w-full">
                Connexion
              </Button>
              <Button disabled={loading} onClick={() => navigate('/register')} className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                Commencer gratuitement
              </Button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section - ULTRA VENDEUR */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100 via-purple-50 to-pink-100 opacity-50"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-full text-sm font-semibold mb-6 shadow-lg">
              <Sparkles className="w-4 h-4 mr-2 animate-pulse" />
              🇲🇦 Première plateforme d'affiliation marocaine B2B/B2C
            </div>

            <h1 className="text-5xl lg:text-7xl font-extrabold text-gray-900 mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Chaque partage<br />devient une vente
              </span>
            </h1>

            <p className="text-xl lg:text-2xl text-gray-700 mb-8 max-w-3xl mx-auto leading-relaxed">
              Transformez votre réseau en machine à vendre. Générez des liens intelligents, 
              suivez chaque clic en temps réel, et <span className="font-bold text-purple-600">encaissez des commissions automatiquement</span>.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button 
                onClick={() => navigate('/register')} 
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg px-10 py-6 rounded-xl shadow-2xl"
              >
                <Rocket className="w-5 h-5 mr-2" />
                Essai gratuit 14 jours
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                variant="outline" 
                onClick={() => navigate('/pricing')}
                className="text-lg px-10 py-6 rounded-xl border-2 border-gray-300 hover:border-blue-600"
              >
                <Play className="w-5 h-5 mr-2" />
                Voir la démo
              </Button>
            </div>

            {/* Offre Pilote GRATUITE */}
            <div className="inline-block bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-2xl p-6 shadow-xl max-w-2xl mx-auto">
              <div className="flex items-center justify-center mb-3">
                <Star className="w-6 h-6 text-yellow-500 mr-2" />
                <span className="text-xl font-bold text-gray-900">🎁 Offre Pilote GRATUITE</span>
                <Star className="w-6 h-6 text-yellow-500 ml-2" />
              </div>
              <p className="text-gray-700 text-lg">
                Testez gratuitement : <span className="font-bold">1 produit</span> • <span className="font-bold">1 lien de tracking</span> • <span className="font-bold">10 clics gratuits</span>
              </p>
              <p className="text-sm text-gray-600 mt-2">Aucune carte bancaire requise • Accès immédiat</p>
            </div>
          </div>

          {/* Stats animées */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100 text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-2">
                {stats.affiliates.toLocaleString()}+
              </div>
              <div className="text-gray-600 font-medium">Affiliés actifs</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100 text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                {stats.companies.toLocaleString()}+
              </div>
              <div className="text-gray-600 font-medium">Entreprises partenaires</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100 text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-2">
                {(stats.commissions / 1000000).toFixed(1)}M DH
              </div>
              <div className="text-gray-600 font-medium">Commissions versées</div>
            </div>
          </div>
        </div>
      </section>

      {/* 4 ÉTAPES - Comment ça marche */}
      <section id="process" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Comment ça marche ?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              4 étapes simples pour transformer votre réseau en revenus
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {processSteps.map((step, index) => (
              <div key={index} className="relative group">
                <div className="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all border border-gray-100 h-full">
                  {/* Numéro de l'étape */}
                  <div className={`absolute -top-4 -right-4 w-16 h-16 bg-gradient-to-br ${step.color} rounded-full flex items-center justify-center shadow-xl`}>
                    <span className="text-white font-bold text-xl">{step.number}</span>
                  </div>

                  {/* Icône */}
                  <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-br ${step.color} text-white mb-6 shadow-lg`}>
                    {step.icon}
                  </div>

                  {/* Contenu */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{step.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* CTA après les 4 étapes */}
          <div className="text-center mt-16">
            <Button 
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg px-12 py-6 rounded-xl shadow-2xl"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Commencer maintenant - Essai gratuit
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* TROIS ESPACES UTILISATEURS */}
      <section id="spaces" className="py-20 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Trois espaces, une plateforme
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Que vous soyez entreprise, commercial ou acheteur, ShareYourSales s'adapte à vos besoins
            </p>
          </div>

          {/* Tabs */}
          <div className="flex justify-center mb-12 flex-wrap gap-4">
            {Object.keys(userSpaces).map((key) => (
              <button
                key={key}
                onClick={() => setActiveSpace(key)}
                className={`px-8 py-4 rounded-xl font-semibold text-lg transition-all ${
                  activeSpace === key
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl'
                    : 'bg-white text-gray-700 hover:bg-gray-50 shadow-md'
                }`}
              >
                {userSpaces[key].title}
              </button>
            ))}
          </div>

          {/* Contenu de l'espace actif */}
          {Object.keys(userSpaces).map((key) => {
            const space = userSpaces[key];
            if (activeSpace !== key) return null;

            return (
              <div key={key} className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
                <div className="grid lg:grid-cols-2 gap-0">
                  {/* Colonne gauche - Info */}
                  <div className="p-12 lg:p-16">
                    <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-white mb-6 shadow-lg">
                      {space.icon}
                    </div>

                    <h3 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
                      {space.title}
                    </h3>
                    <p className="text-xl text-gray-600 mb-6">{space.subtitle}</p>
                    <p className="text-lg text-gray-700 mb-8 leading-relaxed">{space.description}</p>

                    {/* Pricing */}
                    <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-400 rounded-xl p-6 mb-8">
                      <div className="text-3xl font-bold text-gray-900 mb-2">{space.pricing}</div>
                      <div className="text-sm text-gray-600">Sans engagement • Annulez à tout moment</div>
                    </div>

                    <Button 
                      onClick={() => navigate('/register')}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg py-6 rounded-xl shadow-xl"
                    >
                      {space.cta}
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>
                  </div>

                  {/* Colonne droite - Bénéfices */}
                  <div className="bg-gradient-to-br from-blue-50 to-purple-100 p-12 lg:p-16">
                    <h4 className="text-2xl font-bold text-gray-900 mb-8">Vos avantages</h4>
                    <div className="space-y-6">
                      {space.benefits.map((benefit, idx) => (
                        <div key={idx} className="flex items-start space-x-4">
                          <div className="flex-shrink-0 p-3 bg-white rounded-lg text-blue-600 shadow-md">
                            {benefit.icon}
                          </div>
                          <p className="text-gray-700 text-lg leading-relaxed pt-2">{benefit.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 6 FONCTIONNALITÉS PRINCIPALES */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Une plateforme complète et puissante
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Tous les outils dont vous avez besoin pour réussir dans l'affiliation
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {coreFeatures.map((feature, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-white to-gray-50 rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all border border-gray-100"
              >
                <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${feature.gradient} text-white mb-6 shadow-lg`}>
                  {feature.icon}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* POURQUOI SHAREYOURSALES EST UNIQUE */}
      <section className="py-20 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-full text-sm font-semibold mb-6 shadow-lg">
              <Star className="w-4 h-4 mr-2" />
              CE QUI NOUS REND UNIQUE
            </div>
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Pourquoi ShareYourSales ?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              La seule plateforme d'affiliation au Maroc combinant IA avancée, Live Shopping multi-plateformes,
              et gamification complète pour maximiser vos revenus
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {whyUnique.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all border-2 border-purple-100"
              >
                <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 text-white mb-6 shadow-lg">
                  {item.icon}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-6">{item.title}</h3>
                <ul className="space-y-3">
                  {item.points.map((point, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      <CheckCircle2 className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {/* CTA fort */}
          <div className="text-center mt-16">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-12 shadow-2xl text-white">
              <h3 className="text-3xl lg:text-4xl font-bold mb-4">
                Prêt à transformer votre business ?
              </h3>
              <p className="text-xl mb-8 opacity-90">
                Rejoignez les 15,000+ affiliés qui gagnent déjà avec ShareYourSales
              </p>
              <Button
                onClick={() => navigate('/register')}
                className="bg-white text-purple-600 text-lg px-12 py-6 rounded-xl shadow-xl hover:shadow-2xl font-bold"
              >
                <Rocket className="w-5 h-5 mr-2" />
                Commencer gratuitement maintenant
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* TOUS LES OUTILS PAR RÔLE */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Tous les outils pour votre rôle
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Des fonctionnalités puissantes et exclusives adaptées à chaque type d'utilisateur
            </p>
          </div>

          {/* OUTILS POUR MERCHANTS */}
          <div className="mb-20">
            <div className="text-center mb-12">
              <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-100 to-purple-100 px-8 py-4 rounded-2xl">
                <Building2 className="w-8 h-8 text-blue-600" />
                <h3 className="text-3xl font-bold text-gray-900">Outils pour Entreprises (Merchants)</h3>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {uniqueToolsByRole.merchant.map((tool, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-br from-white to-blue-50 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all border border-blue-100"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg text-white">
                      {tool.icon}
                    </div>
                    <span className="text-xs font-bold bg-gradient-to-r from-blue-600 to-purple-600 text-white px-3 py-1 rounded-full">
                      {tool.badge}
                    </span>
                  </div>
                  <h4 className="text-xl font-bold text-gray-900 mb-3">{tool.title}</h4>
                  <p className="text-gray-600 text-sm leading-relaxed">{tool.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* OUTILS POUR INFLUENCERS / COMMERCIALS */}
          <div>
            <div className="text-center mb-12">
              <div className="inline-flex items-center space-x-3 bg-gradient-to-r from-purple-100 to-pink-100 px-8 py-4 rounded-2xl">
                <UserCheck className="w-8 h-8 text-purple-600" />
                <h3 className="text-3xl font-bold text-gray-900">Outils pour Influenceurs & Commerciaux</h3>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {uniqueToolsByRole.influencer.map((tool, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-br from-white to-purple-50 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all border border-purple-100"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg text-white">
                      {tool.icon}
                    </div>
                    <span className="text-xs font-bold bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1 rounded-full">
                      {tool.badge}
                    </span>
                  </div>
                  <h4 className="text-xl font-bold text-gray-900 mb-3">{tool.title}</h4>
                  <p className="text-gray-600 text-sm leading-relaxed">{tool.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* CTA final */}
          <div className="text-center mt-16">
            <Button
              onClick={() => navigate('/register')}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg px-12 py-6 rounded-xl shadow-2xl"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Découvrir tous les outils - Essai gratuit
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      {/* SÉCURITÉ & CONFORMITÉ */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
            <div className="grid lg:grid-cols-2 gap-0">
              {/* Colonne gauche */}
              <div className="p-12 lg:p-16">
                <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-red-500 to-pink-600 text-white mb-6 shadow-lg">
                  <Shield className="w-12 h-12" />
                </div>

                <h2 className="text-4xl font-bold text-gray-900 mb-6">
                  Sécurité & Conformité garanties
                </h2>
                <p className="text-lg text-gray-700 mb-8 leading-relaxed">
                  Votre confiance est notre priorité. ShareYourSales respecte les normes les plus strictes 
                  de sécurité et de conformité légale au Maroc et en Europe.
                </p>

                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 p-3 bg-green-100 rounded-lg text-green-600">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 mb-2">Conformité RGPD</h4>
                      <p className="text-gray-600">Respect total du règlement européen sur la protection des données personnelles.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 p-3 bg-blue-100 rounded-lg text-blue-600">
                      <FileCheck className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 mb-2">Vérification légale</h4>
                      <p className="text-gray-600">Contrôle obligatoire RC (Registre Commerce), IF (Identifiant Fiscal), CNIE pour tous les vendeurs.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 p-3 bg-purple-100 rounded-lg text-purple-600">
                      <Lock className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 mb-2">Encryption AES-256</h4>
                      <p className="text-gray-600">Toutes vos données sont cryptées avec les standards bancaires les plus avancés.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 p-3 bg-red-100 rounded-lg text-red-600">
                      <Shield className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-900 mb-2">Anti-fraude IA</h4>
                      <p className="text-gray-600">Détection automatique des clics frauduleux et transactions suspectes par intelligence artificielle.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Colonne droite - Stats sécurité */}
              <div className="bg-gradient-to-br from-red-50 to-pink-50 p-12 lg:p-16 flex flex-col justify-center">
                <div className="space-y-8">
                  <div className="bg-white rounded-2xl p-8 shadow-lg text-center">
                    <div className="text-5xl font-bold text-red-600 mb-2">99.9%</div>
                    <div className="text-gray-700 font-medium">Uptime garanti</div>
                    <div className="text-sm text-gray-500 mt-2">SLA contractuel</div>
                  </div>

                  <div className="bg-white rounded-2xl p-8 shadow-lg text-center">
                    <div className="text-5xl font-bold text-blue-600 mb-2">24/7</div>
                    <div className="text-gray-700 font-medium">Surveillance</div>
                    <div className="text-sm text-gray-500 mt-2">Monitoring permanent</div>
                  </div>

                  <div className="bg-white rounded-2xl p-8 shadow-lg text-center">
                    <div className="text-5xl font-bold text-green-600 mb-2">100%</div>
                    <div className="text-gray-700 font-medium">Vendeurs vérifiés</div>
                    <div className="text-sm text-gray-500 mt-2">RC/IF/CNIE validés</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TARIFS EN DIRHAM */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Tarifs transparents en Dirham
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Choisissez le plan qui correspond à vos ambitions. Sans engagement, annulez à tout moment.
            </p>
            <div className="inline-flex items-center bg-green-100 text-green-700 px-6 py-3 rounded-full mt-6 font-semibold">
              <Sparkles className="w-5 h-5 mr-2" />
              14 jours d'essai gratuit sur tous les plans
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {pricingPlans.map((plan, index) => (
              <div 
                key={index}
                className={`rounded-3xl shadow-xl border-2 overflow-hidden transition-all ${
                  plan.highlight 
                    ? 'border-purple-500 shadow-purple-200 shadow-2xl scale-105' 
                    : plan.special
                    ? 'border-emerald-500 shadow-emerald-200'
                    : 'border-gray-200'
                }`}
              >
                {/* Badge populaire */}
                {plan.popular && (
                  <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-center py-2 font-semibold text-sm">
                    ⭐ PLUS POPULAIRE
                  </div>
                )}
                {plan.special && (
                  <div className="bg-gradient-to-r from-emerald-600 to-green-600 text-white text-center py-2 font-semibold text-sm">
                    💎 ACCÈS EXCLUSIF
                  </div>
                )}

                <div className="p-8 bg-gradient-to-br from-white to-gray-50">
                  {/* Nom du plan */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-6">{plan.description}</p>

                  {/* Prix */}
                  <div className="mb-8">
                    <div className="flex items-baseline justify-center">
                      {plan.currency && (
                        <>
                          <span className="text-5xl font-extrabold text-gray-900">{plan.price}</span>
                          <span className="text-2xl font-bold text-gray-600 ml-2">{plan.currency}</span>
                        </>
                      )}
                      {!plan.currency && (
                        <span className="text-3xl font-extrabold text-gray-900">{plan.price}</span>
                      )}
                    </div>
                    {plan.period && (
                      <div className="text-gray-500 text-center mt-2">par {plan.period}</div>
                    )}
                  </div>

                  {/* Fonctionnalités */}
                  <ul className="space-y-4 mb-8">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start space-x-3">
                        <Check className={`w-5 h-5 flex-shrink-0 ${plan.highlight ? 'text-purple-600' : plan.special ? 'text-emerald-600' : 'text-blue-600'}`} />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA */}
                  <Button 
                    onClick={() => navigate('/register')}
                    className={`w-full py-4 rounded-xl font-semibold shadow-lg ${
                      plan.highlight
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                        : plan.special
                        ? 'bg-gradient-to-r from-emerald-600 to-green-600 text-white'
                        : 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white'
                    }`}
                  >
                    {plan.cta}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Note commission */}
          <div className="mt-12 text-center bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-2xl p-8 max-w-3xl mx-auto">
            <DollarSign className="w-12 h-12 text-blue-600 mx-auto mb-4" />
            <h4 className="text-2xl font-bold text-gray-900 mb-3">
              Commission plateforme : 5% seulement
            </h4>
            <p className="text-lg text-gray-700">
              ShareYourSales prélève uniquement 5% de commission sur chaque vente réalisée via la plateforme. 
              <span className="font-bold"> Le reste est pour vous !</span>
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">ShareYourSales</span>
              </div>
              <p className="text-sm text-gray-400">
                La première plateforme d'affiliation B2B/B2C marocaine. Chaque partage devient une vente.
              </p>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Produit</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition">Fonctionnalités</a></li>
                <li><a href="#pricing" className="hover:text-white transition">Tarifs</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Entreprise</h4>
              <ul className="space-y-2 text-sm">
                <li><button disabled={loading} onClick={() => navigate('/about')} className="hover:text-white transition">À propos</button></li>
                <li><button disabled={loading} onClick={() => navigate('/blog')} className="hover:text-white transition">Blog</button></li>
              </ul>
            </div>

            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li><button disabled={loading} onClick={() => navigate('/support')} className="hover:text-white transition">Centre d'aide</button></li>
                <li><button disabled={loading} onClick={() => navigate('/contact')} className="hover:text-white transition">Contact</button></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-400">
              © 2024 ShareYourSales. Tous droits réservés. Fait avec ❤️ au Maroc 🇲🇦
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <button disabled={loading} onClick={() => navigate('/privacy')} className="text-gray-400 hover:text-white transition">Confidentialité</button>
              <button disabled={loading} onClick={() => navigate('/terms')} className="text-gray-400 hover:text-white transition">CGU</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPageNew;
