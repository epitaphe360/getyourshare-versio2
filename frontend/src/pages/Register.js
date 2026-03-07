import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Phone, Building, Sparkles, AlertCircle, CheckCircle, Share2, ArrowRight, ArrowLeft, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003/api';

const Register = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState({
    email: '', password: '', confirmPassword: '', first_name: '', last_name: '', phone: '',
    company_name: '', username: ''
  });

  useEffect(() => {
    try {
      if (!searchParams) return;
      const urlRole = searchParams.get('role');
      const urlPlan = searchParams.get('plan');
      if (urlRole && (urlRole === 'merchant' || urlRole === 'influencer')) { setRole(urlRole); setStep(2); }
      if (urlPlan) setSelectedPlan(urlPlan);
    } catch (err) { console.error("Error parsing URL parameters:", err); }
  }, [searchParams]);

  const seoData = SEO_CONFIG?.register || {
    title: 'Inscription - ShareYourSales', description: 'Créez votre compte.',
    keywords: 'inscription, register', image: '', type: 'website', url: '', structuredData: null
  };

  const handleChange = (e) => { setFormData({ ...formData, [e.target.name]: e.target.value }); setError(''); };
  const handleRoleSelection = (selectedRole) => { setRole(selectedRole); setStep(2); };

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    if (formData.password !== formData.confirmPassword) { setError('Les mots de passe ne correspondent pas'); setLoading(false); return; }
    if (formData.password.length < 6) { setError('Le mot de passe doit contenir au moins 6 caractères'); setLoading(false); return; }
    try {
      const registerData = { email: formData.email, password: formData.password, role, first_name: formData.first_name, last_name: formData.last_name, phone: formData.phone, subscription_plan: selectedPlan || 'starter',
        ...(role === 'merchant' && { company_name: formData.company_name }), ...(role === 'influencer' && { username: formData.username }) };
      const response = await axios.post(`${API_URL}/auth/register`, registerData);
      if (response.data.success) { setSuccess(true); localStorage.setItem('pendingPlanSelection', selectedPlan); setTimeout(() => navigate('/login'), 3000); }
    } catch (err) { setError(err.response?.data?.detail || "Erreur lors de l'inscription"); }
    finally { setLoading(false); }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 p-4">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-10 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 mb-6 shadow-lg">
            <CheckCircle className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-display font-bold text-surface-900 dark:text-white mb-3">Inscription réussie ! 🎉</h2>
          <p className="text-surface-500 dark:text-surface-400 mb-6">Redirection vers la connexion...</p>
          <div className="flex justify-center"><svg className="animate-spin h-8 w-8 text-primary-500" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg></div>
        </motion.div>
      </div>
    );
  }

  const InputField = ({ id, name, type = 'text', value, icon: Icon, placeholder, label, required = true, autoComplete }) => (
    <div>
      <label htmlFor={id} className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">{label}</label>
      <div className="relative group">
        <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400 group-focus-within:text-primary-500 transition-colors" />
        <input id={id} type={type} name={name} value={value} onChange={handleChange}
          className="input-premium pl-12" placeholder={placeholder} required={required} autoComplete={autoComplete} />
      </div>
    </div>
  );

  return (
    <>
      <SEOHead {...seoData} />
      <div className="min-h-screen flex relative overflow-hidden bg-surface-50 dark:bg-surface-950">
        {/* ── Left panel ── */}
        <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center bg-gradient-to-br from-primary-600 via-accent-600 to-primary-800">
          <div className="absolute inset-0 aurora-bg opacity-60" />
          <div className="absolute inset-0 noise-overlay" />
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/3 right-1/4 w-48 h-48 bg-accent-400/20 rounded-full blur-3xl animate-morph" />

          <div className="relative z-10 max-w-md px-8">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
              <Link to="/" className="inline-flex items-center gap-2 mb-8">
                <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center">
                  <Share2 className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-display font-bold text-white">ShareYourSales</span>
              </Link>
              <h2 className="text-3xl font-display font-bold text-white mb-4">Rejoignez la révolution du marketing d'affiliation</h2>
              <p className="text-white/70 mb-8 leading-relaxed">Plus de 10,000 entreprises et influenceurs nous font confiance.</p>
              <div className="space-y-4">
                {[
                  { t: 'Tracking en temps réel', d: 'Suivez vos performances instantanément' },
                  { t: 'Paiements sécurisés', d: 'Recevez vos commissions rapidement' },
                  { t: 'Support 24/7', d: 'Une équipe dédiée à votre succès' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <CheckCircle className="w-3.5 h-3.5 text-white" />
                    </div>
                    <div>
                      <div className="font-semibold text-white text-sm">{item.t}</div>
                      <div className="text-xs text-white/60">{item.d}</div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* ── Right panel ── */}
        <div className="flex-1 flex items-center justify-center p-4 sm:p-8 overflow-y-auto">
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }} className="w-full max-w-md">
            {/* Mobile logo */}
            <div className="lg:hidden text-center mb-6">
              <Link to="/" className="inline-flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
                  <Share2 className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-display font-bold text-gradient">ShareYourSales</span>
              </Link>
            </div>

            <AnimatePresence mode="wait">
              {/* ── Step 1: Role Selection ── */}
              {step === 1 && (
                <motion.div key="step1" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <h2 className="text-2xl md:text-3xl font-display font-bold text-surface-900 dark:text-white mb-2">Créer un compte</h2>
                  <p className="text-surface-500 dark:text-surface-400 mb-8">Vous êtes ?</p>

                  <div className="space-y-4">
                    {[
                      { role: 'merchant', icon: Building, title: 'Entreprise', desc: 'Proposer mes produits et travailler avec des influenceurs', gradient: 'from-primary-500 to-primary-700' },
                      { role: 'influencer', icon: Sparkles, title: 'Influenceur / Commercial', desc: 'Promouvoir des produits et gagner des commissions', gradient: 'from-accent-500 to-accent-700' },
                    ].map((r) => (
                      <motion.button key={r.role} whileHover={{ scale: 1.02, y: -2 }} whileTap={{ scale: 0.98 }}
                        onClick={() => handleRoleSelection(r.role)}
                        className="w-full p-6 glass-card text-left group hover:shadow-neon-indigo dark:hover:shadow-neon-indigo transition-all duration-300">
                        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${r.gradient} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                          <r.icon className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="text-lg font-display font-bold text-surface-900 dark:text-white mb-1">{r.title}</h3>
                        <p className="text-sm text-surface-500 dark:text-surface-400">{r.desc}</p>
                      </motion.button>
                    ))}
                  </div>

                  <div className="mt-8 text-center space-y-3">
                    <Link to="/" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-surface-200 dark:border-surface-700 text-sm font-medium text-surface-600 dark:text-surface-400 hover:border-primary-300 dark:hover:border-primary-700 hover:text-primary-600 dark:hover:text-primary-400 transition-all">
                      <ArrowLeft className="w-4 h-4" /> Accueil
                    </Link>
                    <p className="text-surface-500 dark:text-surface-400 text-sm">
                      Déjà un compte ? <Link to="/login" className="font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">Se connecter</Link>
                    </p>
                  </div>
                </motion.div>
              )}

              {/* ── Step 2: Form ── */}
              {step === 2 && (
                <motion.div key="step2" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <button onClick={() => setStep(1)} className="flex items-center gap-1 text-sm text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-300 mb-4 transition-colors">
                    <ArrowLeft className="w-4 h-4" /> Retour
                  </button>

                  <h2 className="text-2xl font-display font-bold text-surface-900 dark:text-white mb-1">
                    {role === 'merchant' ? 'Inscription Entreprise' : 'Inscription Influenceur'}
                  </h2>
                  <p className="text-surface-500 dark:text-surface-400 mb-6 text-sm">Complétez vos informations</p>

                  {error && (
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                      className="mb-4 p-4 rounded-xl bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 flex items-center gap-3">
                      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                      <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
                    </motion.div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <InputField id="first_name" name="first_name" value={formData.first_name} icon={User} placeholder="Jean" label="Prénom" autoComplete="given-name" />
                      <div>
                        <label htmlFor="last_name" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Nom</label>
                        <input id="last_name" type="text" name="last_name" value={formData.last_name} onChange={handleChange}
                          className="input-premium" placeholder="Dupont" required autoComplete="family-name" />
                      </div>
                    </div>

                    {role === 'merchant' && (
                      <InputField id="company_name" name="company_name" value={formData.company_name} icon={Building} placeholder="Mon Entreprise SAS" label="Nom de l'entreprise" autoComplete="organization" />
                    )}
                    {role === 'influencer' && (
                      <InputField id="username" name="username" value={formData.username} icon={User} placeholder="mon_username" label="Nom d'utilisateur" autoComplete="username" />
                    )}

                    <InputField id="email" name="email" type="email" value={formData.email} icon={Mail} placeholder="email@exemple.com" label="Email" autoComplete="email" />
                    <InputField id="phone" name="phone" type="tel" value={formData.phone} icon={Phone} placeholder="+33612345678" label="Téléphone" autoComplete="tel" />

                    <div>
                      <label htmlFor="password" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Mot de passe</label>
                      <div className="relative group">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400 group-focus-within:text-primary-500 transition-colors" />
                        <input id="password" type={showPassword ? 'text' : 'password'} name="password" value={formData.password} onChange={handleChange}
                          className="input-premium pl-12 pr-12" placeholder="••••••••" required autoComplete="new-password" />
                        <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600">
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label htmlFor="confirmPassword" className="block text-sm font-semibold text-surface-700 dark:text-surface-300 mb-2">Confirmer le mot de passe</label>
                      <div className="relative group">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400 group-focus-within:text-primary-500 transition-colors" />
                        <input id="confirmPassword" type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange}
                          className="input-premium pl-12" placeholder="••••••••" required autoComplete="new-password" />
                      </div>
                    </div>

                    <div className="flex items-start gap-3">
                      <input type="checkbox" id="terms" className="mt-1 w-4 h-4 text-primary-600 border-surface-300 dark:border-surface-600 rounded focus:ring-primary-500" required />
                      <label htmlFor="terms" className="text-sm text-surface-600 dark:text-surface-400">
                        J'accepte les <Link to="/terms" className="text-primary-600 dark:text-primary-400 hover:underline">conditions générales</Link>
                      </label>
                    </div>

                    <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} type="submit" disabled={loading} className="btn-premium w-full !py-3.5 text-base">
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                          Inscription...
                        </span>
                      ) : (
                        <span className="flex items-center justify-center gap-2">Créer mon compte <ArrowRight className="w-4 h-4" /></span>
                      )}
                    </motion.button>
                  </form>

                  <div className="mt-6 text-center space-y-3">
                    <Link to="/" className="text-xs text-surface-400 hover:text-primary-500 transition-colors">← Accueil</Link>
                    <p className="text-sm text-surface-500 dark:text-surface-400">
                      Déjà un compte ? <Link to="/login" className="font-semibold text-primary-600 dark:text-primary-400">Se connecter</Link>
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default Register;
