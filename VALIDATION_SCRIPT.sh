#!/bin/bash
# ============================================================
# SCRIPT DE VALIDATION D'INTÉGRATION
# Phases 2, 3, 4 - Commercial Dashboard v2.0
# ============================================================
# Usage: Exécuter dans le navigateur (Console)
# ============================================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🚀 SCRIPT DE VALIDATION D'INTÉGRATION               ║"
echo "║     GetYourShare Commercial Dashboard v2.0            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 INSTRUCTIONS:"
echo "==============="
echo ""
echo "1. Ouvrir CommercialDashboard.js dans le navigateur"
echo "2. Appuyer sur F12 pour ouvrir la console"
echo "3. Coller et exécuter les commandes ci-dessous"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# ============================================================
# VALIDATION 1: Vérifier les imports
# ============================================================
cat << 'EOF'
## ✅ VALIDATION 1: IMPORTS
════════════════════════════════════════════════════════════

Commande:
```javascript
// Vérifier tous les imports sont présents
const imports = [
  'CalendarIntegration',
  'EmailTracker',
  'ClickToCall',
  'LeadScoring',
  'AISuggestions',
  'AIForecasting',
  'SpecializedDashboards'
];

imports.forEach(imp => {
  const found = window[imp] !== undefined || 
               document.querySelector(`[data-component="${imp}"]`);
  console.log(`${found ? '✅' : '❌'} ${imp}`);
});
```

Résultat attendu: Tous les ✅

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 2: ÉTATS"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Vérifier les états React
const statesRequired = [
  'userId',
  'leads',
  'selectedLeadForAI',
  'performanceData'
];

console.log('Vérifiez dans React DevTools (Composant CommercialDashboard):');
statesRequired.forEach(state => console.log(`  - ${state}`));
```

Résultat attendu: selectedLeadForAI présent dans les hooks

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 3: localStorage"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Vérifier les clés localStorage
const userId = localStorage.getItem('userId') || 'test';
const storageKeys = [
  'calendar_events_' + userId,
  'email_campaigns_' + userId,
  'call_history_' + userId,
  'suggestions_cache_' + userId,
  'forecasting_cache_' + userId
];

console.log('🔍 Clés localStorage attendues:');
storageKeys.forEach(key => {
  const exists = localStorage.getItem(key) !== null;
  console.log(`  ${exists ? '✅' : '⏳'} ${key}`);
});
```

Résultat attendu: Zéro, un ou plusieurs ✅ (selon usage)

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 4: DOM Elements"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Vérifier que les composants sont rendus dans le DOM
const components = {
  'CalendarIntegration': '.calendar-container',
  'EmailTracker': '.email-tracker-container',
  'ClickToCall': '.voip-container',
  'LeadScoring': '.lead-scoring-container',
  'AISuggestions': '.ai-suggestions-container',
  'AIForecasting': '.forecasting-container',
  'SpecializedDashboards': '.specialized-dashboard-container'
};

console.log('🔍 Composants rendus dans le DOM:');
Object.entries(components).forEach(([name, selector]) => {
  const found = document.querySelector(selector);
  console.log(`  ${found ? '✅' : '⏳'} ${name}`);
});
```

Résultat attendu: Certains peuvent être ⏳ s'ils ne sont pas visibles

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 5: TESTS AUTOMATISÉS (RECOMMANDÉ)"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Lancer le suite de tests complète
runAllTests()
```

Résultat attendu: Rapport détaillé avec pourcentage de réussite

Fichier de test: TESTS_PHASES_2_3_4.js
Durée: ~10 secondes

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 6: CONSOLE ERRORS"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Vérifier qu'il n'y a pas d'erreurs graves
const logs = [];
window.originalLog = console.error;
console.error = function(...args) {
  logs.push(args);
  window.originalLog(...args);
};

// Attendre quelques secondes puis vérifier
setTimeout(() => {
  console.log(`🔍 Erreurs détectées: ${logs.length}`);
  logs.forEach(log => console.log('  ❌', log));
}, 2000);
```

Résultat attendu: 0 erreurs

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## ✅ VALIDATION 7: PERFORMANCE"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Commande:
```javascript
// Vérifier la performance
if (performance.memory) {
  const usedMB = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
  const limitMB = (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2);
  console.log(`💾 Mémoire: ${usedMB}MB / ${limitMB}MB`);
}

const navTiming = performance.getEntriesByType('navigation')[0];
if (navTiming) {
  console.log(`⏱️ Temps de chargement: ${navTiming.loadEventEnd - navTiming.loadEventStart}ms`);
}

// Nombre de composants rendus
const motionElements = document.querySelectorAll('[style*="opacity"]');
console.log(`🎬 Éléments animés: ${motionElements.length}`);
```

Résultat attendu: Mémoire < 50MB, Chargement < 5s

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## 🧪 TESTS MANUELS"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
Après les tests automatisés, vérifier manuellement:

1. CALENDRIER (Phase 2):
   - Scrollez jusqu'à la section "CALENDRIER INTÉGRÉ"
   - Vérifiez que le calendrier est visible
   - Cliquez sur une date, ajoutez un événement
   - Rechargez la page → L'événement doit persister

2. EMAIL TRACKER (Phase 2):
   - Scrollez jusqu'à "EMAIL TRACKER"
   - Créez une campagne d'email
   - Vérifiez les statistiques
   - Rechargez → Campagne toujours présente

3. CLICK-TO-CALL (Phase 2):
   - Scrollez jusqu'à "CLICK-TO-CALL"
   - Testez le clavier VoIP
   - Vérifiez l'historique d'appels
   - Rechargez → Historique persiste

4. LEAD SCORING (Phase 3):
   - Consultez les scores des leads (0-100)
   - Testez les filtres (Hot/Warm/Cold)
   - Cliquez sur un lead

5. SUGGESTIONS IA (Phase 3):
   - Les suggestions devraient apparaître après avoir cliqué sur un lead
   - Consultez les scripts de vente
   - Consultez les templates d'email

6. AI FORECASTING (Phase 3):
   - Vérifiez les graphiques de prévisions
   - Consultez les 3 scénarios
   - Vérifiez la prédiction de churn

7. DASHBOARDS SPÉCIALISÉS (Phase 4):
   - Sélectionnez différents rôles
   - Vérifiez que le contenu change
   - Consultez les métriques role-specific

════════════════════════════════════════════════════════════
EOF

echo ""
echo "## 📋 RÉSUMÉ"
echo "════════════════════════════════════════════════════════════"
echo ""
cat << 'EOF'
✅ Étapes de validation:
  1. ✅ Vérifier les imports
  2. ✅ Vérifier les états
  3. ✅ Vérifier localStorage
  4. ✅ Vérifier les éléments DOM
  5. ✅ Exécuter runAllTests()
  6. ✅ Vérifier les erreurs console
  7. ✅ Vérifier la performance
  8. ✅ Tests manuels des 7 composants

📊 Résultat final:
  - Tous les tests doivent passer (ou être marqués ⏳)
  - Pas d'erreurs graves
  - Performance acceptable
  - Données persistées

🚀 Prochaines étapes:
  - Déployer vers staging
  - Faire un test complet en production
  - Valider avec les utilisateurs
  - Déployer en production

════════════════════════════════════════════════════════════
EOF

echo ""
echo "✅ FIN DU SCRIPT DE VALIDATION"
echo ""
echo "Pour plus d'informations, consultez:"
echo "  - GUIDE_INTEGRATION_COMPLET.js"
echo "  - TESTS_PHASES_2_3_4.js"
echo "  - CHECKLIST_INTEGRATION_ET_TEST.js"
echo ""
