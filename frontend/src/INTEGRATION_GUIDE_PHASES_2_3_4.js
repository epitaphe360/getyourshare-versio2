// ===============================================
// INTÉGRATION PHASE 2, 3, 4 - ADDITIONS AU CommercialDashboard
// ===============================================
// À ajouter dans les imports du CommercialDashboard.js

// === PHASE 2: Calendrier, Email, VoIP ===
import CalendarIntegration from '../../components/dashboard/CalendarIntegration';
import EmailTracker from '../../components/dashboard/EmailTracker';
import ClickToCall from '../../components/dashboard/ClickToCall';

// === PHASE 3: IA et Intelligence ===
import LeadScoring from '../../components/dashboard/LeadScoring';
import AISuggestions from '../../components/dashboard/AISuggestions';
import AIForecasting from '../../components/dashboard/AIForecasting';

// === PHASE 4: Dashboards Spécialisés ===
import SpecializedDashboards from '../../components/dashboard/SpecializedDashboards';

// ===============================================
// CODE À AJOUTER DANS LE JSX DU CommercialDashboard
// ===============================================

/*
  Placer ces composants après SubscriptionBanner et avant QuotaTracker

  {/* PHASE 2: CALENDRIER INTÉGRÉ */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.1 }}
  >
    <CalendarIntegration userId={userId} />
  </motion.section>

  {/* PHASE 2: EMAIL TRACKER */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.15 }}
  >
    <EmailTracker userId={userId} leads={leads} />
  </motion.section>

  {/* PHASE 2: CLICK-TO-CALL VOIP */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.2 }}
  >
    <ClickToCall userId={userId} leads={leads} />
  </motion.section>

  {/* PHASE 3: SCORING AUTOMATIQUE */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.25 }}
  >
    <LeadScoring leads={leads} />
  </motion.section>

  {/* PHASE 3: SUGGESTIONS IA */}
  {filteredLeads.length > 0 && (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <AISuggestions
        lead={filteredLeads[0]}
        leadHistory={leads}
      />
    </motion.section>
  )}

  {/* PHASE 3: PRÉVISIONS REVENUE */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.35 }}
  >
    <AIForecasting leads={leads} historicalData={performanceData} />
  </motion.section>

  {/* PHASE 4: DASHBOARDS SPÉCIALISÉS */}
  <motion.section
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.4 }}
  >
    <SpecializedDashboards leads={leads} user={userId} />
  </motion.section>
*/

// ===============================================
// DONNÉES SAMPLE POUR TESTER
// ===============================================

export const SAMPLE_LEADS = [
  {
    id: '1',
    name: 'Jean Dupont',
    email: 'jean@acme.fr',
    company: 'Acme Corporation',
    phone: '+33 6 12 34 56 78',
    temperature: 'hot',
    estimatedValue: 25000,
    lastContact: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    budget: true,
    decisionMakerIdentified: true,
    proposalViewed: true,
    emailOpens: 8,
    emailClicks: 3,
    pageVisits: 12,
    contentDownloads: 2,
    demoRequests: 1,
    formSubmissions: 1,
    needsAlignment: 8,
    hasNegativeSignal: false,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '2',
    name: 'Marie Bernard',
    email: 'marie@techstart.fr',
    company: 'TechStart Solutions',
    phone: '+33 6 98 76 54 32',
    temperature: 'warm',
    estimatedValue: 15000,
    lastContact: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    budget: false,
    decisionMakerIdentified: false,
    proposalViewed: true,
    emailOpens: 5,
    emailClicks: 2,
    pageVisits: 8,
    contentDownloads: 1,
    demoRequests: 0,
    formSubmissions: 0,
    needsAlignment: 6,
    hasNegativeSignal: false,
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '3',
    name: 'Pierre Laurent',
    email: 'pierre@innovate.fr',
    company: 'Innovation Group',
    phone: '+33 6 55 66 77 88',
    temperature: 'cold',
    estimatedValue: 8000,
    lastContact: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
    budget: false,
    decisionMakerIdentified: false,
    proposalViewed: false,
    emailOpens: 1,
    emailClicks: 0,
    pageVisits: 2,
    contentDownloads: 0,
    demoRequests: 0,
    formSubmissions: 0,
    needsAlignment: 3,
    hasNegativeSignal: false,
    createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: '4',
    name: 'Sophie Moreau',
    email: 'sophie@nexus.fr',
    company: 'Nexus Consulting',
    phone: '+33 6 33 44 55 66',
    temperature: 'hot',
    estimatedValue: 35000,
    lastContact: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    budget: true,
    decisionMakerIdentified: true,
    proposalViewed: true,
    emailOpens: 12,
    emailClicks: 5,
    pageVisits: 20,
    contentDownloads: 3,
    demoRequests: 2,
    formSubmissions: 1,
    needsAlignment: 9,
    hasNegativeSignal: false,
    createdAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

// ===============================================
// CHECKLIST D'INTÉGRATION
// ===============================================
/*
✅ Phase 1: COMPLÈTE
  ✅ AdvancedFilters.js
  ✅ exportUtils.js
  ✅ PeriodComparison.js
  ✅ NotificationCenter.js

✅ Phase 2: COMPLÈTE
  ✅ CalendarIntegration.js - Calendrier avec Google Sync + iCal
  ✅ EmailTracker.js - Tracking pixel + click tracking
  ✅ ClickToCall.js - VoIP avec enregistrement

✅ Phase 3: COMPLÈTE
  ✅ LeadScoring.js - Scoring IA (Engagement 30%, Achat 35%, Urgence 20%, ROT 15%)
  ✅ AISuggestions.js - Scripts, pricing, actions recommandées
  ✅ AIForecasting.js - Revenue forecast + Churn prediction + Growth opportunities

✅ Phase 4: COMPLÈTE
  ✅ SpecializedDashboards.js - Vendeur, Manager, Admin, Prospect

NEXT STEPS:
1. Importer tous les composants dans CommercialDashboard.js
2. Ajouter les sections JSX comme indiqué ci-dessus
3. Tester avec SAMPLE_LEADS ou vraies données
4. Configurer les API endpoints pour persistence
5. Ajouter authentification Google Calendar (OAuth2)
6. Configurer webhooks email tracking
7. Intégrer fournisseur VoIP (Twilio, Vonage, etc.)
8. Entrainer modèles ML si nécessaire
*/
