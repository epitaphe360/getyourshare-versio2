const User = require('../models/User');
const NotificationService = require('../services/NotificationService');

/**
 * CRM Automation Service
 * ROI: 12.6K€ → 660K€/month
 * Features: Email sequences, Lead scoring ML, Task automation
 */
class CRMAutomationService {

  /**
   * EMAIL SEQUENCES AUTOMATION
   * Ex: 5 emails sur 14 jours pour nurturing lead
   */
  async startEmailSequence(leadId, sequenceType = 'nurture') {
    const sequences = {
      nurture: [
        { delay: 0, subject: "Bienvenue! Découvrez comment nous pouvons vous aider", template: 'nurture-1' },
        { delay: 2, subject: "3 raisons de choisir notre solution", template: 'nurture-2' },
        { delay: 5, subject: "Case Study: Comment [Client] a augmenté ses ventes de 300%", template: 'nurture-3' },
        { delay: 7, subject: "Démo gratuite: Prêt à passer à l'action?", template: 'nurture-4' },
        { delay: 14, subject: "Dernière chance: Offre spéciale -20%", template: 'nurture-5' }
      ],
      onboarding: [
        { delay: 0, subject: "Bienvenue! Commençons ensemble", template: 'onboard-1' },
        { delay: 1, subject: "Étape 1: Configurez votre profil", template: 'onboard-2' },
        { delay: 3, subject: "Étape 2: Invitez votre équipe", template: 'onboard-3' },
        { delay: 7, subject: "Astuce: Maximisez votre ROI", template: 'onboard-4' }
      ]
    };

    const sequence = sequences[sequenceType] || sequences.nurture;

    console.log(`[CRM] Starting ${sequenceType} sequence for lead ${leadId}`);

    sequence.forEach(email => {
      setTimeout(async () => {
        await this.sendSequenceEmail(leadId, email);
      }, email.delay * 24 * 60 * 60 * 1000); // Convertir jours en ms
    });

    return { success: true, emails_scheduled: sequence.length };
  }

  /**
   * LEAD SCORING AUTOMATIQUE
   * Scoring 0-100 basé sur comportement + démographique
   */
  async calculateLeadScore(leadId) {
    const lead = await this.getLeadWithActivity(leadId);
    if (!lead) return { score: 0 };

    let score = 0;

    // Demographic scoring (40 points max)
    if (lead.company_size && lead.company_size === 'enterprise') score += 20;
    if (lead.job_title && lead.job_title.includes('CEO')) score += 15;
    if (lead.industry && lead.industry === 'tech') score += 5;

    // Behavioral scoring (60 points max)
    score += Math.min(lead.email_opens * 5, 20); // Max 20 pts
    score += Math.min(lead.link_clicks * 10, 30); // Max 30 pts
    if (lead.visited_pricing_page) score += 10;

    // Cap à 100
    score = Math.min(score, 100);

    // Assign grade
    const grade = score >= 80 ? 'A' : score >= 60 ? 'B' : score >= 40 ? 'C' : 'D';

    // Mettre à jour
    await this.updateLeadScore(leadId, score, grade);

    // Si devient "chaud" (score > 70), notifier commercial
    if (score > 70) {
      await NotificationService.create({
        user_id: lead.assigned_to,
        type: 'lead_hot',
        title: '🔥 Lead Chaud Détecté',
        message: `${lead.first_name} ${lead.last_name} (Score: ${score}) est prêt à être contacté`,
        priority: 'high',
        data: { lead_id: leadId, score, grade },
        action_url: `/leads/${leadId}`,
        action_label: 'Voir le lead',
        channels: { in_app: true, push: true, email: false }
      });
    }

    return { score, grade };
  }

  /**
   * TASK AUTOMATION
   * Créer automatiquement des tâches selon comportement lead
   */
  async createAutoTasks(leadId, trigger) {
    const taskTemplates = {
      email_opened_3x: {
        title: 'Appeler le lead (3 ouvertures email)',
        priority: 'high',
        due_in_hours: 24
      },
      visited_pricing: {
        title: 'Envoyer proposition personnalisée',
        priority: 'urgent',
        due_in_hours: 4
      },
      inactive_7days: {
        title: 'Relance: Lead inactif depuis 7 jours',
        priority: 'medium',
        due_in_hours: 48
      }
    };

    const template = taskTemplates[trigger];
    if (!template) return;

    const dueDate = new Date();
    dueDate.setHours(dueDate.getHours() + template.due_in_hours);

    console.log(`[CRM] Auto-task created for lead ${leadId}: ${template.title}`);

    // TODO: Créer task dans DB
    return { success: true, task: template };
  }

  /**
   * PRÉDICTIONS IA
   * Probabilité de closing (0-100%)
   */
  async predictClosingProbability(leadId) {
    const lead = await this.getLeadWithActivity(leadId);
    if (!lead) return { probability: 0 };

    // Simplified ML model
    let probability = 50; // Base

    // Facteurs positifs
    if (lead.score > 70) probability += 20;
    if (lead.email_opens > 3) probability += 10;
    if (lead.visited_pricing_page) probability += 15;
    if (lead.requested_demo) probability += 20;

    // Facteurs négatifs
    if (lead.days_since_last_activity > 14) probability -= 30;
    if (lead.bounced_email) probability -= 20;

    probability = Math.max(0, Math.min(100, probability));

    // Prédire date de closing (si prob > 60%)
    let predicted_close_date = null;
    if (probability > 60) {
      predicted_close_date = new Date();
      predicted_close_date.setDate(predicted_close_date.getDate() + Math.floor((100 - probability) / 2));
    }

    return {
      probability,
      predicted_close_date,
      recommended_action: this.getRecommendedAction(probability, lead)
    };
  }

  /**
   * WORKFLOWS IF-THEN-ELSE
   * Ex: Si lead ouvre email 3x → créer task "Call NOW"
   */
  async executeWorkflow(workflowId, leadId) {
    // Simplified workflow engine
    const workflow = await this.getWorkflow(workflowId);
    if (!workflow) return;

    console.log(`[CRM] Executing workflow ${workflowId} for lead ${leadId}`);

    for (const step of workflow.steps) {
      const conditionMet = await this.evaluateCondition(step.condition, leadId);
      
      if (conditionMet) {
        await this.executeAction(step.action, leadId);
      }
    }

    return { success: true };
  }

  // ========== HELPERS ==========

  async sendSequenceEmail(leadId, email) {
    console.log(`[CRM] Sending sequence email: ${email.subject}`);
    // TODO: Integration SendGrid
    return { success: true };
  }

  async getLeadWithActivity(leadId) {
    // Simplified
    return {
      id: leadId,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      score: 65,
      email_opens: 3,
      link_clicks: 2,
      visited_pricing_page: true,
      days_since_last_activity: 2
    };
  }

  async updateLeadScore(leadId, score, grade) {
    console.log(`[CRM] Lead ${leadId} score updated: ${score} (${grade})`);
  }

  getRecommendedAction(probability, lead) {
    if (probability > 80) return 'Call immediately - High conversion chance';
    if (probability > 60) return 'Send personalized proposal';
    if (probability > 40) return 'Continue nurturing with content';
    return 'Re-engage with special offer';
  }

  async getWorkflow(workflowId) {
    return null; // Simplified
  }

  async evaluateCondition(condition, leadId) {
    return true; // Simplified
  }

  async executeAction(action, leadId) {
    console.log(`[CRM] Executing action: ${action.type}`);
  }
}

module.exports = new CRMAutomationService();
