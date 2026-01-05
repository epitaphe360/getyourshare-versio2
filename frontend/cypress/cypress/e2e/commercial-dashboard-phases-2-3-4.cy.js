// cypress/e2e/commercial-dashboard-phases-2-3-4.cy.js
// ============================================================
// Tests E2E pour Commercial Dashboard - Phases 2, 3, 4
// ============================================================
// Tests Cypress pour les 7 nouveaux composants:
// Phase 2: CalendarIntegration, EmailTracker, ClickToCall
// Phase 3: LeadScoring, AISuggestions, AIForecasting
// Phase 4: SpecializedDashboards
// ============================================================

describe('Commercial Dashboard - Phases 2, 3, 4 Integration Tests', () => {
  
  // ============================================================
  // SETUP
  // ============================================================
  
  beforeEach(() => {
    // Intercepter les appels API
    cy.intercept('GET', '**/api/dashboard/stats', {
      statusCode: 200,
      body: {
        total_leads: 42,
        total_revenue: 15000,
        conversion_rate: 0.25,
        avg_deal_value: 1500
      }
    }).as('getDashboardStats');

    cy.intercept('GET', '**/api/leads', {
      statusCode: 200,
      body: [
        {
          id: 1,
          name: 'Lead Test 1',
          email: 'lead1@test.com',
          company: 'Test Co 1',
          status: 'qualifie',
          temperature: 'hot',
          value: 5000,
          engagement_score: 85,
          purchase_intent: 90,
          urgency: 80,
          roi_potential: 75
        },
        {
          id: 2,
          name: 'Lead Test 2',
          email: 'lead2@test.com',
          company: 'Test Co 2',
          status: 'en_negociation',
          temperature: 'warm',
          value: 3000,
          engagement_score: 65,
          purchase_intent: 70,
          urgency: 60,
          roi_potential: 65
        },
        {
          id: 3,
          name: 'Lead Test 3',
          email: 'lead3@test.com',
          company: 'Test Co 3',
          status: 'nouveau',
          temperature: 'cold',
          value: 1000,
          engagement_score: 35,
          purchase_intent: 40,
          urgency: 30,
          roi_potential: 35
        }
      ]
    }).as('getLeads');

    // Visiter la page Commercial Dashboard
    cy.visit('/commercial/dashboard');
    
    // Attendre le chargement
    cy.wait('@getDashboardStats');
    cy.wait('@getLeads');
  });

  // ============================================================
  // PHASE 2: TESTS DE COMMUNICATION
  // ============================================================
  
  describe('Phase 2: Communication Tools', () => {
    
    // ----- CALENDRIER INTÉGRÉ -----
    describe('CalendarIntegration', () => {
      
      it('should display calendar component', () => {
        cy.get('[class*="calendar"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should render calendar with current month', () => {
        cy.get('[class*="calendar-header"]')
          .should('contain.text', new Date().getFullYear());
      });

      it('should add a new calendar event', () => {
        // Cliquer sur une date
        cy.get('[class*="calendar-day"]').first().click();

        // Remplir le formulaire modal
        cy.get('[data-testid="event-title"]')
          .type('Test Meeting');

        cy.get('[data-testid="event-description"]')
          .type('Meeting with Lead Test 1');

        // Sauvegarder
        cy.get('[data-testid="save-event"]').click();

        // Vérifier que l'événement est ajouté
        cy.get('[class*="event-item"]')
          .should('contain.text', 'Test Meeting');
      });

      it('should persist events in localStorage', () => {
        const userId = localStorage.getItem('userId') || 'test-user';
        const storageKey = `calendar_events_${userId}`;

        // Créer un événement
        cy.get('[class*="calendar-day"]').first().click();
        cy.get('[data-testid="event-title"]').type('Persistent Event');
        cy.get('[data-testid="save-event"]').click();

        // Vérifier localStorage
        cy.window().then((win) => {
          const events = localStorage.getItem(storageKey);
          expect(events).to.not.be.null;
        });
      });
    });

    // ----- EMAIL TRACKER -----
    describe('EmailTracker', () => {
      
      it('should display email tracker component', () => {
        cy.get('[class*="email-tracker"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should create a new email campaign', () => {
        // Cliquer sur "Créer Campagne"
        cy.get('[data-action="create-campaign"]').click();

        // Remplir le formulaire
        cy.get('[name="campaign_subject"]')
          .type('Test Campaign');

        cy.get('[name="campaign_content"]')
          .type('This is a test email campaign');

        // Sélectionner des leads
        cy.get('[data-testid="lead-checkbox"]')
          .first()
          .check();

        // Envoyer
        cy.get('[data-action="send-campaign"]').click();

        // Vérifier la création
        cy.get('[class*="campaign-item"]')
          .should('contain.text', 'Test Campaign');
      });

      it('should track campaign statistics', () => {
        // Créer une campagne
        cy.get('[data-action="create-campaign"]').click();
        cy.get('[name="campaign_subject"]').type('Stats Test');
        cy.get('[name="campaign_content"]').type('Test content');
        cy.get('[data-action="send-campaign"]').click();

        // Vérifier les stats
        cy.get('[class*="campaign-stats"]')
          .should('contain.text', 'Envoyés')
          .and('contain.text', '0');
      });

      it('should persist campaigns in localStorage', () => {
        const userId = localStorage.getItem('userId') || 'test-user';
        const storageKey = `email_campaigns_${userId}`;

        // Créer une campagne
        cy.get('[data-action="create-campaign"]').click();
        cy.get('[name="campaign_subject"]').type('Persist Test');
        cy.get('[data-action="send-campaign"]').click();

        // Vérifier localStorage
        cy.window().then((win) => {
          const campaigns = localStorage.getItem(storageKey);
          expect(campaigns).to.not.be.null;
        });
      });
    });

    // ----- CLICK-TO-CALL -----
    describe('ClickToCall', () => {
      
      it('should display VoIP interface', () => {
        cy.get('[class*="voip"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should display dial pad', () => {
        cy.get('[class*="dialpad"]')
          .should('exist');

        // Vérifier les touches 0-9
        for (let i = 0; i <= 9; i++) {
          cy.get(`[data-dial="${i}"]`)
            .should('exist');
        }
      });

      it('should dial numbers correctly', () => {
        // Cliquer sur les touches
        cy.get('[data-dial="1"]').click();
        cy.get('[data-dial="2"]').click();
        cy.get('[data-dial="3"]').click();

        // Vérifier le numéro affiché
        cy.get('[class*="phone-display"]')
          .should('contain.text', '123');
      });

      it('should simulate a call', () => {
        // Remplir le numéro
        cy.get('[data-dial="1"]').click();
        cy.get('[data-dial="5"]').click();

        // Appeler
        cy.get('[data-action="call"]').click();

        // Vérifier que l'appel est enregistré
        cy.get('[class*="call-history"]')
          .should('contain.text', '15');
      });

      it('should persist call history in localStorage', () => {
        const userId = localStorage.getItem('userId') || 'test-user';
        const storageKey = `call_history_${userId}`;

        // Simuler un appel
        cy.get('[data-dial="9"]').click();
        cy.get('[data-action="call"]').click();

        // Vérifier localStorage
        cy.window().then((win) => {
          const history = localStorage.getItem(storageKey);
          expect(history).to.not.be.null;
        });
      });
    });
  });

  // ============================================================
  // PHASE 3: TESTS INTELLIGENCE ARTIFICIELLE
  // ============================================================
  
  describe('Phase 3: AI Intelligence', () => {
    
    // ----- LEAD SCORING -----
    describe('LeadScoring', () => {
      
      it('should display lead scoring section', () => {
        cy.get('[class*="lead-scoring"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should display all leads with scores', () => {
        cy.get('[class*="lead-score-card"]')
          .should('have.length.at.least', 3);
      });

      it('should calculate scores correctly', () => {
        // Lead 1 devrait être "Hot" (score 80+)
        cy.get('[class*="lead-score-card"]')
          .first()
          .within(() => {
            cy.get('[class*="score-value"]')
              .then(($el) => {
                const score = parseInt($el.text());
                expect(score).to.be.at.least(80);
              });
          });
      });

      it('should filter leads by temperature', () => {
        // Cliquer sur filtre "Hot"
        cy.get('[data-filter="hot"]').click();

        // Vérifier que seuls les hot leads sont visibles
        cy.get('[class*="lead-score-card"]')
          .each(($el) => {
            cy.wrap($el)
              .should('contain.text', 'Hot');
          });
      });

      it('should allow sorting by score', () => {
        // Cliquer sur le bouton de tri
        cy.get('[data-sort="score"]').click();

        // Vérifier que les scores sont en ordre décroissant
        cy.get('[class*="score-value"]')
          .then(($scores) => {
            const scores = Array.from($scores).map(el => parseInt(el.textContent));
            for (let i = 0; i < scores.length - 1; i++) {
              expect(scores[i]).to.be.at.least(scores[i + 1]);
            }
          });
      });

      it('should select a lead for AI suggestions', () => {
        // Cliquer sur un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Vérifier que le lead est sélectionné (classe active)
        cy.get('[class*="lead-score-card"]')
          .first()
          .should('have.class', 'active');
      });
    });

    // ----- AI SUGGESTIONS -----
    describe('AISuggestions', () => {
      
      it('should display AI suggestions only when lead is selected', () => {
        // Au début, la section ne devrait pas être visible
        cy.get('[class*="ai-suggestions"]', { timeout: 2000 })
          .should('not.exist');

        // Sélectionner un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Maintenant les suggestions doivent s'afficher
        cy.get('[class*="ai-suggestions"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should display sales scripts', () => {
        // Sélectionner un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Vérifier les scripts
        cy.get('[class*="script-card"]', { timeout: 5000 })
          .should('have.length.at.least', 1);

        cy.get('[class*="script-card"]')
          .first()
          .should('contain.text', 'Script');
      });

      it('should display email templates', () => {
        // Sélectionner un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Vérifier les templates
        cy.get('[class*="email-template"]', { timeout: 5000 })
          .should('have.length.at.least', 1);
      });

      it('should display conversion predictions', () => {
        // Sélectionner un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Vérifier les prédictions
        cy.get('[class*="conversion-prediction"]', { timeout: 5000 })
          .should('exist')
          .and('contain.text', '%');
      });

      it('should save suggestion feedback', () => {
        // Sélectionner un lead
        cy.get('[class*="lead-score-card"]')
          .first()
          .click();

        // Cliquer "Utile"
        cy.get('[data-feedback="useful"]')
          .first()
          .click();

        // Vérifier le feedback est enregistré
        cy.get('[data-feedback="useful"]')
          .first()
          .should('have.class', 'selected');
      });
    });

    // ----- AI FORECASTING -----
    describe('AIForecasting', () => {
      
      it('should display forecasting section', () => {
        cy.get('[class*="forecasting"]', { timeout: 5000 })
          .should('exist')
          .and('be.visible');
      });

      it('should display revenue forecast charts', () => {
        cy.get('[class*="forecast-chart"]')
          .should('have.length.at.least', 1);
      });

      it('should display three scenarios', () => {
        cy.get('[class*="scenario-card"]')
          .should('have.length', 3);

        // Vérifier les noms des scénarios
        cy.get('[class*="scenario-card"]')
          .should('contain.text', 'Conservative')
          .and('contain.text', 'Realistic')
          .and('contain.text', 'Optimistic');
      });

      it('should display churn prediction', () => {
        cy.get('[class*="churn-prediction"]')
          .should('exist')
          .and('contain.text', '%');
      });

      it('should display growth opportunities', () => {
        cy.get('[class*="growth-opportunities"]')
          .should('exist');

        cy.get('[class*="opportunity-item"]')
          .should('have.length.at.least', 1);
      });

      it('should display AI insights', () => {
        cy.get('[class*="ai-insights"]')
          .should('exist')
          .and('not.be.empty');
      });
    });
  });

  // ============================================================
  // PHASE 4: TESTS DASHBOARDS SPÉCIALISÉS
  // ============================================================
  
  describe('Phase 4: Specialized Dashboards', () => {
    
    it('should display specialized dashboards section', () => {
      cy.get('[class*="specialized-dashboard"]', { timeout: 5000 })
        .should('exist')
        .and('be.visible');
    });

    it('should display role selector', () => {
      cy.get('[class*="role-selector"]')
        .should('exist');

      cy.get('[data-role]')
        .should('have.length', 4);
    });

    describe('Vendeur Dashboard', () => {
      
      it('should display vendeur dashboard', () => {
        cy.get('[data-role="vendeur"]')
          .click();

        cy.get('[class*="dashboard-vendeur"]')
          .should('be.visible');
      });

      it('should display personal pipeline', () => {
        cy.get('[data-role="vendeur"]').click();

        cy.get('[class*="pipeline"]')
          .should('exist');
      });

      it('should display objectives', () => {
        cy.get('[data-role="vendeur"]').click();

        cy.get('[class*="objectives"]')
          .should('exist');
      });

      it('should display commissions info', () => {
        cy.get('[data-role="vendeur"]').click();

        cy.get('[class*="commissions"]')
          .should('exist');
      });
    });

    describe('Manager Dashboard', () => {
      
      it('should display manager dashboard', () => {
        cy.get('[data-role="manager"]')
          .click();

        cy.get('[class*="dashboard-manager"]')
          .should('be.visible');
      });

      it('should display team performance', () => {
        cy.get('[data-role="manager"]').click();

        cy.get('[class*="team-performance"]')
          .should('exist');
      });

      it('should display comparisons', () => {
        cy.get('[data-role="manager"]').click();

        cy.get('[class*="comparisons"]')
          .should('exist');
      });
    });

    describe('Admin Dashboard', () => {
      
      it('should display admin dashboard', () => {
        cy.get('[data-role="admin"]')
          .click();

        cy.get('[class*="dashboard-admin"]')
          .should('be.visible');
      });

      it('should display system health', () => {
        cy.get('[data-role="admin"]').click();

        cy.get('[class*="system-health"]')
          .should('exist');
      });

      it('should display alerts', () => {
        cy.get('[data-role="admin"]').click();

        cy.get('[class*="alerts"]')
          .should('exist');
      });
    });

    describe('Prospect Dashboard', () => {
      
      it('should display prospect dashboard', () => {
        cy.get('[data-role="prospect"]')
          .click();

        cy.get('[class*="dashboard-prospect"]')
          .should('be.visible');
      });

      it('should display proposals', () => {
        cy.get('[data-role="prospect"]').click();

        cy.get('[class*="proposals"]')
          .should('exist');
      });

      it('should display tracking', () => {
        cy.get('[data-role="prospect"]').click();

        cy.get('[class*="tracking"]')
          .should('exist');
      });
    });
  });

  // ============================================================
  // TESTS D'INTÉGRATION GLOBALE
  // ============================================================
  
  describe('Global Integration Tests', () => {
    
    it('should load all components without errors', () => {
      // Vérifier qu'il n'y a pas d'erreurs dans la console
      cy.window().then((win) => {
        cy.spy(win.console, 'error');
      });

      cy.get('body').should('exist');

      cy.window().then((win) => {
        expect(win.console.error).not.to.have.been.called;
      });
    });

    it('should display all phase 2 components', () => {
      cy.get('[class*="calendar"]').should('exist');
      cy.get('[class*="email-tracker"]').should('exist');
      cy.get('[class*="voip"]').should('exist');
    });

    it('should display all phase 3 components', () => {
      cy.get('[class*="lead-scoring"]').should('exist');
      cy.get('[class*="forecasting"]').should('exist');
      // AISuggestions est conditionnel
    });

    it('should display all phase 4 components', () => {
      cy.get('[class*="specialized-dashboard"]').should('exist');
    });

    it('should have animations working', () => {
      // Vérifier les éléments animés
      cy.get('[style*="opacity"]')
        .should('have.length.at.least', 10);
    });

    it('should persist data across page reloads', () => {
      // Ajouter un événement calendrier
      cy.get('[class*="calendar-day"]').first().click();
      cy.get('[data-testid="event-title"]').type('Persist Test');
      cy.get('[data-testid="save-event"]').click();

      // Recharger la page
      cy.reload();

      // Attendre le rechargement
      cy.wait('@getDashboardStats');
      cy.wait('@getLeads');

      // Vérifier que l'événement est toujours là
      cy.get('[class*="event-item"]')
        .should('contain.text', 'Persist Test');
    });

    it('should handle user interactions smoothly', () => {
      // Sélectionner un lead
      cy.get('[class*="lead-score-card"]')
        .first()
        .click();

      // Attendre les suggestions
      cy.get('[class*="ai-suggestions"]', { timeout: 5000 })
        .should('be.visible');

      // Changer le rôle du dashboard
      cy.get('[data-role="manager"]').click();

      // Vérifier le changement
      cy.get('[class*="dashboard-manager"]')
        .should('be.visible');
    });

    it('should display correct metrics', () => {
      // Vérifier les stats principales
      cy.get('[class*="stat-card"]')
        .should('have.length.at.least', 4);

      // Vérifier les valeurs
      cy.get('[class*="stat-value"]')
        .each(($el) => {
          expect($el.text()).to.not.be.empty;
        });
    });
  });

  // ============================================================
  // TESTS DE PERFORMANCE
  // ============================================================
  
  describe('Performance Tests', () => {
    
    it('should load dashboard in reasonable time', () => {
      const startTime = Date.now();

      cy.visit('/commercial/dashboard');
      cy.get('[class*="dashboard-card"]', { timeout: 5000 })
        .should('have.length.at.least', 1);

      const loadTime = Date.now() - startTime;
      expect(loadTime).to.be.lessThan(5000); // 5 secondes max
    });

    it('should handle rapid user interactions', () => {
      // Rapid clicks on different components
      cy.get('[class*="lead-score-card"]').first().click();
      cy.get('[data-role="manager"]').click();
      cy.get('[data-role="vendeur"]').click();
      cy.get('[class*="lead-score-card"]').last().click();

      // Tout devrait fonctionner correctement
      cy.get('body').should('exist');
    });
  });
});
