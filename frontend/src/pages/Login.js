import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Mail, Lock, Sparkles, AlertCircle, Shield, Share2, ArrowRight, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [twoFACode, setTwoFACode] = useState('');
  const [tempToken, setTempToken] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showTestAccounts, setShowTestAccounts] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const testConnection = async () => {
    setDebugInfo("Test de connexion en cours...");
    try {
      const startTime = Date.now();
      const response = await api.get('/health');
      const duration = Date.now() - startTime;
      setDebugInfo(`✅ Backend connecté en ${duration}ms. Status: ${response.status}`);
    } catch (err) {
      setDebugInfo(`❌ Erreur connexion: ${err.message}. ${err.response ? `Status: ${err.response.status}` : 'Pas de réponse'}`);
    }
  };

  const handleRedirect = () => {
    const pendingPlan = localStorage.getItem('pendingPlanSelection');
    if (pendingPlan) { localStorage.removeItem('pendingPlanSelection'); navigate('/subscription/plans'); return; }
    const redirectPath = localStorage.getItem('redirectAfterLogin');
    if (redirectPath) { localStorage.removeItem('redirectAfterLogin'); navigate(redirectPath); }
    else navigate('/dashboard');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    const result = await login(email, password);
    if (result.success) { handleRedirect(); }
    else if (result.requires_2fa || result.requires2FA) { setRequires2FA(true); setTempToken(result.temp_token || result.tempToken); setError(''); }
    else setError(result.error);
    setLoading(false);
  };

  const quickLogin = async (testEmail, testPassword) => {
    setEmail(testEmail); setPassword(testPassword); setError(''); setLoading(true);
    const result = await login(testEmail, testPassword);
    if (result.success) { handleRedirect(); }
    else if (result.requires_2fa || result.requires2FA) { setRequires2FA(true); setTempToken(result.temp_token || result.tempToken); setError(''); }
    else setError(result.error);
    setLoading(false);
  };

  const handleVerify2FA = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const response = await api.post('/api/auth/verify-2fa', { email, code: twoFACode, temp_token: tempToken });
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        handleRedirect();
      }
    } catch (err) { setError(err.response?.data?.detail || 'Erreur lors de la vérification du code'); }
    finally { setLoading(false); }
  };

  const seoData = SEO_CONFIG?.login || {
    title: 'Connexion - ShareYourSales', description: 'Connectez-vous à votre compte.',
    keywords: 'connexion, login', image: '', type: 'website', url: '', structuredData: null
  };

  const testAccounts = [
    { label: 'Admin', sub: 'Enterprise - Accès Total', email: 'admin@getyourshare.com', pw: 'admin123', color: 'purple', icon: Shield },
    { label: 'Sarah El Fassi', sub: '250K • Fashion', email: 'influencer1@fashion.com', pw: 'Test123!', color: 'emerald', tier: 'STARTER' },
    { label: 'Pierre Tech', sub: '150K • Tech', email: 'influencer2@tech.com', pw: 'Test123!', color: 'amber', tier: 'PRO' },
    { label: 'Laura Lifestyle', sub: '180K • Lifestyle', email: 'influencer3@lifestyle.com', pw: 'Test123!', color: 'violet', tier: 'ENTERPRISE' },
    { label: 'Fashion Store', sub: 'Mode & Vêtements', email: 'merchant1@fashionstore.com', pw: 'Test123!', color: 'emerald', tier: 'STARTER' },
    { label: 'Tech Gadgets', sub: 'Technologie', email: 'merchant2@techgadgets.com', pw: 'Test123!', color: 'amber', tier: 'PRO' },
    { label: 'Beauty Paris', sub: 'Beauté', email: 'merchant3@beautyparis.com', pw: 'Test123!', color: 'violet', tier: 'ENTERPRISE' },
    { label: 'Lucas Commercial', sub: 'Business Dev', email: 'commercial1@getyourshare.com', pw: 'Test123!', color: 'blue', tier: 'ENTERPRISE' },
  ];

  const tierColors = { STARTER: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300', PRO: 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300', ENTERPRISE: 'bg-violet-100 text-violet-700 dark:bg-violet-900/50 dark:text-violet-300' };

  return (
    <>
      <SEOHead {...seoData} />
      <div className="min-h-screen flex relative overflow-hidden bg-surface-50 dark:bg-surface-950">
        {/* ── Left panel: Aurora background ── */}
        <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800">
          <div className="absolute inset-0 aurora-bg opacity-60" />
          <div className="absolute inset-0 noise-overlay" />
          {/* Floating orbs */}
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/3 right-1/4 w-48 h-48 bg-accent-400/20 rounded-full blur-3xl animate-morph" />

          <div className="relative z-10 max-w-md px-8 text-center">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-white/10 backdrop-blur-sm border border-white/20 mb-8 shadow-xl">
                <Share2 className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-4xl font-display font-extrabold text-white mb-4">ShareYourSales</h1>
              <p className="text-lg text-white/80 font-light leading-relaxed">
                Chaque partage devient une vente. Connectez-vous pour accéder à votre tableau de bord.
              </p>
              <div className="mt-10 grid grid-cols-3 gap-6">
                {[
                  { n: '5K+', l: 'Utilisateurs' },
                  { n: '98%', l: 'Satisfaction' },
                  { n: '12M+', l: 'Volume' },
                ].map((s, i) => (
                  <div key={i} className="text-center">
                    <div className="text-2xl font-display font-bold text-white">{s.n}</div>
                    <div className="text-xs text-white/60 mt-1">{s.l}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* ── Right panel: Login form ── */}
        <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full max-w-md"
          >
            {/* Mobile logo */}
            <div className="lg:hidden text-center mb-8">
              <Link to="/" className="inline-flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
                  <Share2 className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-display font-bold text-gradient">ShareYourSales</span>
              </Link>
            </div>

            <AnimatePresence mode="wait">
              {!requires2FA ? (
                <motion.div key="login" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div className="mb-8">
                    <h2 className="text-2xl md:text-3xl font-display font-bold text-surface-900 dark:text-white">Bon retour 👋</h2>
                    <p className="text-surface-500 dark:text-surface-400 mt-2">Accédez à votre tableau de bord</p>
                  </div>

                  {error && (
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4 p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 flex items-center gap-3" data-testid="error-message">
                      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                      <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
                    </motion.div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                      <label htmlFor="email" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Email</label>
                      <div className="relative group">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400 group-focus-within:text-primary-500 transition-colors" />
                        <input id="email" name="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                          className="input-premium pl-12" placeholder="votre@email.com" required data-testid="email-input" autoComplete="email" />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="password" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Mot de passe</label>
                      <div className="relative group">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400 group-focus-within:text-primary-500 transition-colors" />
                        <input id="password" name="password" type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                          className="input-premium pl-12 pr-12" placeholder="••••••••" required data-testid="password-input" autoComplete="current-password" />
                        <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 transition-colors">
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" disabled={loading}
                      className="btn-premium w-full !py-3.5 text-base" data-testid="login-button">
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                          Connexion...
                        </span>
                      ) : (
                        <span className="flex items-center justify-center gap-2">Se connecter <ArrowRight className="w-4 h-4" /></span>
                      )}
                    </motion.button>
                  </form>

                  <p className="mt-6 text-center text-surface-500 dark:text-surface-400">
                    Pas encore de compte ?{' '}
                    <Link to="/register" className="font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors">
                      S'inscrire gratuitement
                    </Link>
                  </p>

                  {/* ── Test Accounts (collapsible) ── */}
                  <div className="mt-8 border-t border-surface-200 dark:border-surface-800 pt-6">
                    <button onClick={() => setShowTestAccounts(!showTestAccounts)}
                      className="flex items-center justify-between w-full text-xs font-semibold text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-300 transition-colors">
                      <span className="flex items-center gap-1.5">🚀 Comptes de Test</span>
                      {showTestAccounts ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>

                    <AnimatePresence>
                      {showTestAccounts && (
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
                          <div className="mt-4 space-y-2 max-h-64 overflow-y-auto pr-1 custom-scrollbar">
                            {testAccounts.map((a, i) => (
                              <button key={i} onClick={() => quickLogin(a.email, a.pw)} disabled={loading}
                                className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl border border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 hover:bg-primary-50/50 dark:hover:bg-primary-950/30 transition-all group disabled:opacity-50">
                                <div className="flex items-center gap-3">
                                  <div className={`w-8 h-8 rounded-lg bg-${a.color}-100 dark:bg-${a.color}-900/50 flex items-center justify-center`}>
                                    {a.icon ? <a.icon className={`w-4 h-4 text-${a.color}-600 dark:text-${a.color}-400`} /> : <Sparkles className={`w-4 h-4 text-${a.color}-600 dark:text-${a.color}-400`} />}
                                  </div>
                                  <div className="text-left">
                                    <p className="text-xs font-semibold text-surface-800 dark:text-surface-200">{a.label}</p>
                                    <p className="text-[10px] text-surface-400">{a.sub}</p>
                                  </div>
                                </div>
                                {a.tier && <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${tierColors[a.tier]}`}>{a.tier}</span>}
                              </button>
                            ))}
                          </div>

                          <div className="mt-3 p-3 rounded-xl bg-surface-100 dark:bg-surface-800/50 text-[10px] text-surface-500 dark:text-surface-400 space-y-1">
                            <p><strong>Mots de passe :</strong> Admin: admin123 • Autres: Test123!</p>
                            <p><strong>Code 2FA :</strong> 123456</p>
                          </div>

                          {/* Debug */}
                          <div className="mt-2 flex items-center justify-between text-[10px] text-surface-400">
                            <span>MODE DEBUG</span>
                            <button onClick={testConnection} type="button" className="text-primary-500 hover:underline">Tester API</button>
                          </div>
                          {debugInfo && <div className={`mt-1 p-2 rounded-lg text-[10px] ${debugInfo.includes('✅') ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300' : 'bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300'}`}>{debugInfo}</div>}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              ) : (
                /* ── 2FA Verification ── */
                <motion.div key="2fa" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4 shadow-lg shadow-primary-500/25">
                      <Shield className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-display font-bold text-surface-900 dark:text-white">Vérification 2FA</h2>
                    <p className="text-surface-500 dark:text-surface-400 mt-2">Un code a été envoyé à votre téléphone</p>
                  </div>

                  {error && (
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4 p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 flex items-center gap-3">
                      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                      <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
                    </motion.div>
                  )}

                  <form onSubmit={handleVerify2FA} className="space-y-5">
                    <div>
                      <label htmlFor="twoFACode" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Code à 6 chiffres</label>
                      <input id="twoFACode" name="twoFACode" type="text" value={twoFACode} onChange={(e) => setTwoFACode(e.target.value)}
                        className="input-premium text-center text-2xl font-bold tracking-[0.3em]" placeholder="000000" maxLength="6" required autoComplete="one-time-code" />
                    </div>

                    <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" disabled={loading} className="btn-premium w-full !py-3.5 text-base">
                      {loading ? 'Vérification...' : 'Vérifier le code'}
                    </motion.button>

                    <button type="button" onClick={() => { setRequires2FA(false); setTwoFACode(''); setError(''); }}
                      className="w-full py-2 text-sm text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-300 transition-colors">
                      ← Retour à la connexion
                    </button>
                  </form>

                  <div className="mt-6 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                    <p className="text-xs text-emerald-700 dark:text-emerald-300"><strong>💡 Démo :</strong> Code <strong>123456</strong></p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Bottom links */}
            <div className="mt-8 text-center space-x-6">
              <Link to="/" className="text-xs text-surface-400 hover:text-primary-500 transition-colors">Accueil</Link>
              <Link to="/pricing" className="text-xs text-surface-400 hover:text-primary-500 transition-colors">Tarifs</Link>
            </div>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default Login;
