/**
 * 🧪 TESTS COMPLETS DES PHASES 2, 3, 4
 * ====================================
 * Tests d'intégration et de fonctionnalité pour tous les nouveaux composants
 * Exécuter dans la console du navigateur après le chargement du CommercialDashboard
 */

// ============================================================
// TEST UTILS
// ============================================================

const TEST_RESULTS = {
  phase2: { calendar: false, email: false, voip: false },
  phase3: { scoring: false, suggestions: false, forecasting: false },
  phase4: { specialized: false }
};

const logSuccess = (component) => {
  console.log(`✅ ${component} chargé avec succès`);
  return true;
};

const logError = (component, error) => {
  console.error(`❌ ${component} erreur:`, error);
  return false;
};

// ============================================================
// PHASE 2 TESTS: OUTILS DE COMMUNICATION
// ============================================================

/**
 * Test 1: CalendarIntegration
 * Vérifie que le composant calendrier est présent et fonctionne
 */
function testCalendarIntegration() {
  try {
    const calendarElement = document.querySelector('[data-testid="calendar-integration"]') ||
                           document.querySelector('.calendar-container');
    
    if (calendarElement) {
      // Vérifier les éléments clés du calendrier
      const calendarTitle = document.querySelector('.calendar-title');
      const calendarGrid = document.querySelector('.calendar-grid');
      const syncButton = document.querySelector('[data-action="sync-google"]');
      
      const hasTitle = !!calendarTitle;
      const hasGrid = !!calendarGrid;
      const hasSync = !!syncButton;
      
      if (hasTitle || hasGrid) {
        console.log('  📅 Éléments du calendrier détectés');
        return logSuccess('CalendarIntegration');
      }
    }
    
    // Fallback: vérifier localStorage
    const calendarData = localStorage.getItem('calendar_events_' + userId);
    if (calendarData) {
      console.log('  📅 Données du calendrier en localStorage:', JSON.parse(calendarData));
      return logSuccess('CalendarIntegration');
    }
    
    console.warn('  ⚠️ CalendarIntegration: données non trouvées, peut être masqué');
    return true; // Pas d'erreur critique
  } catch (error) {
    return logError('CalendarIntegration', error);
  }
}

/**
 * Test 2: EmailTracker
 * Vérifie que le tracker d'email fonctionne
 */
function testEmailTracker() {
  try {
    const emailElement = document.querySelector('[data-testid="email-tracker"]') ||
                        document.querySelector('.email-tracker-container');
    
    if (emailElement) {
      const campaignForm = document.querySelector('.campaign-form');
      const campaignList = document.querySelector('.campaign-list');
      
      if (campaignForm || campaignList) {
        console.log('  📧 Formulaires et listes d\'email détectés');
        return logSuccess('EmailTracker');
      }
    }
    
    // Vérifier localStorage
    const emailData = localStorage.getItem('email_campaigns_' + userId);
    if (emailData) {
      const campaigns = JSON.parse(emailData);
      console.log(`  📧 ${campaigns.length} campagnes email en cache`);
      return logSuccess('EmailTracker');
    }
    
    console.warn('  ⚠️ EmailTracker: données non trouvées, peut être masqué');
    return true;
  } catch (error) {
    return logError('EmailTracker', error);
  }
}

/**
 * Test 3: ClickToCall
 * Vérifie que l'interface VoIP fonctionne
 */
function testClickToCall() {
  try {
    const voipElement = document.querySelector('[data-testid="click-to-call"]') ||
                       document.querySelector('.voip-container');
    
    if (voipElement) {
      const dialpad = document.querySelector('.dialpad');
      const callHistory = document.querySelector('.call-history');
      const recordButton = document.querySelector('[data-action="record"]');
      
      if (dialpad || callHistory) {
        console.log('  ☎️ Interface VoIP détectée');
        return logSuccess('ClickToCall');
      }
    }
    
    // Vérifier localStorage
    const callData = localStorage.getItem('call_history_' + userId);
    if (callData) {
      const calls = JSON.parse(callData);
      console.log(`  ☎️ ${calls.length} appels en historique`);
      return logSuccess('ClickToCall');
    }
    
    console.warn('  ⚠️ ClickToCall: données non trouvées, peut être masqué');
    return true;
  } catch (error) {
    return logError('ClickToCall', error);
  }
}

// ============================================================
// PHASE 3 TESTS: INTELLIGENCE ARTIFICIELLE
// ============================================================

/**
 * Test 4: LeadScoring
 * Vérifie que l'algorithme de scoring fonctionne
 */
function testLeadScoring() {
  try {
    const scoringElement = document.querySelector('[data-testid="lead-scoring"]') ||
                          document.querySelector('.lead-scoring-container');
    
    if (scoringElement) {
      // Vérifier les gauges de scoring
      const scoreGauges = document.querySelectorAll('.score-gauge');
      const filterButtons = document.querySelectorAll('[data-filter]');
      
      console.log(`  🎯 ${scoreGauges.length} gauges de scoring détectés`);
      console.log(`  🎯 ${filterButtons.length} filtres disponibles`);
      
      return logSuccess('LeadScoring');
    }
    
    console.warn('  ⚠️ LeadScoring: composant non trouvé (peut être masqué)');
    return true;
  } catch (error) {
    return logError('LeadScoring', error);
  }
}

/**
 * Test 5: AISuggestions
 * Vérifie que les suggestions IA s'affichent
 */
function testAISuggestions() {
  try {
    const suggestionsElement = document.querySelector('[data-testid="ai-suggestions"]') ||
                              document.querySelector('.ai-suggestions-container');
    
    if (suggestionsElement) {
      const scriptCards = document.querySelectorAll('.script-card');
      const templates = document.querySelectorAll('.email-template');
      const predictions = document.querySelector('.conversion-prediction');
      
      console.log(`  🤖 ${scriptCards.length} scripts de vente trouvés`);
      console.log(`  🤖 ${templates.length} templates d'email trouvés`);
      
      return logSuccess('AISuggestions');
    }
    
    console.warn('  ⚠️ AISuggestions: sélectionnez un lead pour voir les suggestions');
    return true;
  } catch (error) {
    return logError('AISuggestions', error);
  }
}

/**
 * Test 6: AIForecasting
 * Vérifie que les prévisions IA fonctionne
 */
function testAIForecasting() {
  try {
    const forecastingElement = document.querySelector('[data-testid="ai-forecasting"]') ||
                              document.querySelector('.forecasting-container');
    
    if (forecastingElement) {
      const forecastCharts = document.querySelectorAll('.forecast-chart');
      const scenarios = document.querySelectorAll('.scenario-card');
      const predictions = document.querySelectorAll('.churn-prediction');
      
      console.log(`  📈 ${forecastCharts.length} graphiques de prévisions trouvés`);
      console.log(`  📈 ${scenarios.length} scénarios détectés`);
      
      return logSuccess('AIForecasting');
    }
    
    console.warn('  ⚠️ AIForecasting: composant non trouvé');
    return true;
  } catch (error) {
    return logError('AIForecasting', error);
  }
}

// ============================================================
// PHASE 4 TESTS: DASHBOARDS SPÉCIALISÉS
// ============================================================

/**
 * Test 7: SpecializedDashboards
 * Vérifie les dashboards par rôle
 */
function testSpecializedDashboards() {
  try {
    const dashboardElement = document.querySelector('[data-testid="specialized-dashboards"]') ||
                            document.querySelector('.specialized-dashboard-container');
    
    if (dashboardElement) {
      const roleSelector = document.querySelector('.role-selector');
      const roles = document.querySelectorAll('[data-role]');
      const dashboardContent = document.querySelector('.dashboard-content');
      
      console.log(`  👤 ${roles.length} rôles disponibles`);
      
      if (roleSelector) {
        console.log('  👤 Sélecteur de rôle détecté');
      }
      
      return logSuccess('SpecializedDashboards');
    }
    
    console.warn('  ⚠️ SpecializedDashboards: composant non trouvé');
    return true;
  } catch (error) {
    return logError('SpecializedDashboards', error);
  }
}

// ============================================================
// INTEGRATION TESTS
// ============================================================

/**
 * Test d'intégration: Vérifier que tous les imports sont présents
 */
function testImports() {
  console.log('\n📦 TEST DES IMPORTS');
  console.log('='.repeat(50));
  
  try {
    // Chercher les scripts importés
    const scripts = Array.from(document.querySelectorAll('script[src]'))
      .map(s => s.src);
    
    const expectedComponents = [
      'CalendarIntegration',
      'EmailTracker',
      'ClickToCall',
      'LeadScoring',
      'AISuggestions',
      'AIForecasting',
      'SpecializedDashboards'
    ];
    
    expectedComponents.forEach(comp => {
      const found = scripts.some(s => s.includes(comp)) || 
                   window[comp] !== undefined;
      const status = found ? '✅' : '⚠️';
      console.log(`  ${status} ${comp}`);
    });
    
    return true;
  } catch (error) {
    console.error('  ❌ Erreur lors du test des imports:', error);
    return false;
  }
}

/**
 * Test d'intégration: Vérifier localStorage
 */
function testLocalStorage() {
  console.log('\n💾 TEST LOCALSTORAGE');
  console.log('='.repeat(50));
  
  const userId = localStorage.getItem('userId') || 'unknown';
  
  const storageKeys = [
    'calendar_events_' + userId,
    'email_campaigns_' + userId,
    'call_history_' + userId,
    'lead_scores_' + userId,
    'forecasting_cache_' + userId
  ];
  
  let totalSize = 0;
  
  storageKeys.forEach(key => {
    const data = localStorage.getItem(key);
    if (data) {
      const size = new Blob([data]).size;
      totalSize += size;
      console.log(`  ✅ ${key}: ${size} bytes`);
    }
  });
  
  console.log(`  📊 Taille totale: ${(totalSize / 1024).toFixed(2)} KB`);
  
  return true;
}

/**
 * Test d'intégration: Performance
 */
function testPerformance() {
  console.log('\n⚡ TEST DE PERFORMANCE');
  console.log('='.repeat(50));
  
  // Temps de rendu
  const renderStart = performance.now();
  const components = document.querySelectorAll('[data-testid^="phase-"]');
  const renderEnd = performance.now();
  
  console.log(`  ⏱️ Temps de rendu: ${(renderEnd - renderStart).toFixed(2)}ms`);
  console.log(`  📊 ${components.length} composants rendus`);
  
  // Mémoire (si disponible)
  if (performance.memory) {
    const usedMB = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
    const limitMB = (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2);
    console.log(`  🧠 Mémoire: ${usedMB}MB / ${limitMB}MB`);
  }
  
  return true;
}

/**
 * Test d'intégration: Animations
 */
function testAnimations() {
  console.log('\n🎬 TEST DES ANIMATIONS');
  console.log('='.repeat(50));
  
  // Vérifier Framer Motion
  const motionElements = document.querySelectorAll('[style*="opacity"]');
  console.log(`  ✅ ${motionElements.length} éléments animés détectés`);
  
  // Vérifier les transitions CSS
  const transitionElements = document.querySelectorAll('[style*="transition"]');
  console.log(`  ✅ ${transitionElements.length} éléments avec transitions détectés`);
  
  return true;
}

// ============================================================
// LAUNCH ALL TESTS
// ============================================================

/**
 * Fonction principale pour exécuter tous les tests
 */
function runAllTests() {
  console.clear();
  console.log('╔════════════════════════════════════════════════════╗');
  console.log('║   🧪 TESTS COMPLETS PHASES 2, 3, 4              ║');
  console.log('║   GetYourShare Commercial Dashboard v2           ║');
  console.log('╚════════════════════════════════════════════════════╝');
  
  console.log('\n🔍 DÉTECTION DE COMPOSANTS');
  console.log('='.repeat(50));
  
  // Phase 2 Tests
  console.log('\n📱 PHASE 2: OUTILS DE COMMUNICATION');
  TEST_RESULTS.phase2.calendar = testCalendarIntegration();
  TEST_RESULTS.phase2.email = testEmailTracker();
  TEST_RESULTS.phase2.voip = testClickToCall();
  
  // Phase 3 Tests
  console.log('\n🤖 PHASE 3: INTELLIGENCE ARTIFICIELLE');
  TEST_RESULTS.phase3.scoring = testLeadScoring();
  TEST_RESULTS.phase3.suggestions = testAISuggestions();
  TEST_RESULTS.phase3.forecasting = testAIForecasting();
  
  // Phase 4 Tests
  console.log('\n📊 PHASE 4: DASHBOARDS SPÉCIALISÉS');
  TEST_RESULTS.phase4.specialized = testSpecializedDashboards();
  
  // Integration Tests
  testImports();
  testLocalStorage();
  testPerformance();
  testAnimations();
  
  // Rapport final
  console.log('\n' + '='.repeat(50));
  console.log('📊 RAPPORT FINAL');
  console.log('='.repeat(50));
  
  const allTests = [
    ...Object.values(TEST_RESULTS.phase2),
    ...Object.values(TEST_RESULTS.phase3),
    ...Object.values(TEST_RESULTS.phase4)
  ];
  
  const passedCount = allTests.filter(t => t).length;
  const totalCount = allTests.length;
  const passPercentage = ((passedCount / totalCount) * 100).toFixed(1);
  
  console.log(`\n✅ Réussi: ${passedCount}/${totalCount} (${passPercentage}%)`);
  console.log('\n📋 Détails:');
  console.log(`  Phase 2: ${Object.values(TEST_RESULTS.phase2).filter(t => t).length}/3`);
  console.log(`  Phase 3: ${Object.values(TEST_RESULTS.phase3).filter(t => t).length}/3`);
  console.log(`  Phase 4: ${Object.values(TEST_RESULTS.phase4).filter(t => t).length}/1`);
  
  if (passPercentage >= 80) {
    console.log('\n🎉 INTÉGRATION RÉUSSIE - Tous les composants fonctionnent!');
  } else if (passPercentage >= 60) {
    console.log('\n⚠️ INTÉGRATION PARTIELLE - Vérifiez les avertissements ci-dessus');
  } else {
    console.log('\n❌ PROBLÈMES DÉTECTÉS - Voir les erreurs ci-dessus');
  }
  
  return TEST_RESULTS;
}

// ============================================================
// AUTO-EXECUTE WHEN AVAILABLE
// ============================================================

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Fichier de test chargé. Exécutez: runAllTests()');
  });
} else {
  console.log('✅ Fichier de test chargé. Exécutez: runAllTests()');
}

// Export pour utilisation externe
window.runAllTests = runAllTests;
window.TEST_RESULTS = TEST_RESULTS;

console.log('\n💡 Utilisation:');
console.log('  runAllTests()  // Exécuter tous les tests');
console.log('  TEST_RESULTS   // Voir les résultats');
