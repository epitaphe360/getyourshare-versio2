import React, { useState, useEffect } from 'react';
import { Lightbulb, Copy, ThumbsUp, ThumbsDown, Sparkles, MessageSquare, DollarSign, TrendingUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './AISuggestions.css';

const AISuggestions = ({ lead, leadHistory = [] }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [selectedScript, setSelectedScript] = useState(null);
  const [copiedScript, setCopiedScript] = useState(null);
  const [feedback, setFeedback] = useState({});

  useEffect(() => {
    if (lead) {
      generateSuggestions(lead);
    }
  }, [lead]);

  const generateSuggestions = (lead) => {
    const generatedSuggestions = [];

    // 1. Script de vente personnalisé
    if (lead.temperature === 'hot' || lead.temperature === 'warm') {
      generatedSuggestions.push({
        id: 'script_pitch',
        type: 'sales_script',
        title: 'Script de présentation optimisé',
        icon: <MessageSquare size={20} />,
        content: generatePitchScript(lead),
        confidence: 92,
        actionCount: lead.contactHistory?.length || 0,
      });
    }

    // 2. Stratégie de pricing
    generatedSuggestions.push({
      id: 'pricing_strategy',
      type: 'pricing',
      title: 'Stratégie de pricing suggérée',
      icon: <DollarSign size={20} />,
      content: generatePricingStrategy(lead),
      confidence: 85,
      estimatedValue: lead.estimatedValue || 0,
    });

    // 3. Prochaine action recommandée
    generatedSuggestions.push({
      id: 'next_action',
      type: 'action',
      title: 'Action recommandée',
      icon: <Lightbulb size={20} />,
      content: generateNextAction(lead),
      confidence: 88,
      urgency: lead.temperature === 'hot' ? 'high' : 'medium',
    });

    // 4. Prévision de conversion
    if (leadHistory.length > 0) {
      generatedSuggestions.push({
        id: 'conversion_prediction',
        type: 'prediction',
        title: 'Prévision de conversion',
        icon: <TrendingUp size={20} />,
        content: generateConversionPrediction(lead, leadHistory),
        confidence: 78,
        probability: calculateConversionProbability(lead, leadHistory),
      });
    }

    // 5. Email template optimisé
    generatedSuggestions.push({
      id: 'email_template',
      type: 'email',
      title: 'Template email optimisé (A/B test)',
      icon: <Sparkles size={20} />,
      content: generateEmailTemplate(lead),
      confidence: 90,
      abVariant: true,
    });

    setSuggestions(generatedSuggestions);
  };

  const generatePitchScript = (lead) => {
    const scripts = {
      hot: `Bonjour ${lead.name},

Je viens de voir que vous avez téléchargé notre whitepaper sur l'optimisation des processus commerciaux. C'est exactement le problème que nous resolvons pour des entreprises comme ${lead.company}.

En fait, nous venons d'aider une entreprise similaire à réduire leurs délais de clôture de 40% en seulement 3 mois.

Auriez-vous 15 minutes cette semaine pour que je vous montre comment nous pourrions faire la même chose pour ${lead.company}?`,

      warm: `Bonjour ${lead.name},

Suite à notre dernier échange sur vos défis de ${lead.painPoint || 'croissance'}, j'aimerais partager une approche que nous avons testée avec des résultats impressionnants.

Les entreprises dans votre secteur voient généralement une amélioration de 30-50% dans leurs ${lead.metric || 'conversions'} en mettant en place notre solution.

Serais-tu disponible pour un appel court cette semaine?`,

      cold: `Bonjour ${lead.name},

Je vous contacte car j'ai trouvé votre profil intéressant suite à vos activités récentes dans le domaine de ${lead.industry || 'votre secteur'}.

Nous aidons des entreprises comme ${lead.company} à ${lead.goalEstimate || 'atteindre leurs objectifs plus rapidement'}.

Seriez-vous ouvert à une brève conversation?`,
    };

    return scripts[lead.temperature] || scripts.cold;
  };

  const generatePricingStrategy = (lead) => {
    const baseValue = lead.estimatedValue || 10000;
    const budget = lead.budget || 'unknown';
    const decisionSpeed = lead.decisionSpeed || 'medium';

    let strategy = `📊 Stratégie de Pricing Recommandée pour ${lead.company}\n\n`;

    // Valeur estimée
    strategy += `💰 Valeur Estimée: ${baseValue.toLocaleString('fr-FR')}€\n`;

    // Package recommandé
    if (baseValue > 50000) {
      strategy += `\n📦 Package Recommandé: ENTERPRISE\n`;
      strategy += `• Tarif de base: ${(baseValue * 0.15).toLocaleString('fr-FR')}€\n`;
      strategy += `• Réduction volume (15-20%): ${(baseValue * 0.15 * 0.85).toLocaleString('fr-FR')}€\n`;
      strategy += `• Marge négociable: 10%\n`;
    } else if (baseValue > 20000) {
      strategy += `\n📦 Package Recommandé: GROWTH\n`;
      strategy += `• Tarif de base: ${(baseValue * 0.12).toLocaleString('fr-FR')}€\n`;
      strategy += `• Possibilité de réduction (10%): ${(baseValue * 0.12 * 0.9).toLocaleString('fr-FR')}€\n`;
    } else {
      strategy += `\n📦 Package Recommandé: STARTER\n`;
      strategy += `• Tarif fixe: ${Math.max(3000, baseValue * 0.1).toLocaleString('fr-FR')}€\n`;
      strategy += `• Possibilité d'upsell après 3 mois\n`;
    }

    // Stratégie de négociation
    strategy += `\n🎯 Stratégie de Négociation:\n`;
    if (decisionSpeed === 'fast') {
      strategy += `• Offrir 5% si décision cette semaine\n`;
      strategy += `• Créer urgence avec "offre limitée"\n`;
    } else {
      strategy += `• Proposer essai gratuit 30 jours\n`;
      strategy += `• Plan de paiement flexible\n`;
    }

    strategy += `• Point de rupture: -20% maximum\n`;

    return strategy;
  };

  const generateNextAction = (lead) => {
    let action = `🎯 Prochaine Action Recommandée\n\n`;

    const lastContact = lead.lastContact ? new Date(lead.lastContact) : null;
    const daysSinceContact = lastContact
      ? Math.floor((Date.now() - lastContact) / (1000 * 60 * 60 * 24))
      : 'unknown';

    if (lead.temperature === 'hot') {
      action += `⏰ URGENCE: Contacter dans les 24 heures\n`;
      action += `📞 Moyen préféré: Appel téléphonique\n`;
      action += `💬 Objet: "Démo exclusive - [Company Name]"\n`;
      action += `🎁 Offre: Session de stratégie gratuite (30 min)\n`;
      action += `⏳ Tentative 1: Appel direct\n`;
      action += `⏳ Tentative 2: Email + lien calendrier\n`;
      action += `⏳ Tentative 3: Message LinkedIn personnalisé\n`;
    } else if (lead.temperature === 'warm') {
      action += `⏰ À faire cette semaine\n`;
      action += `📧 Moyen préféré: Email personnalisé\n`;
      action += `💬 Contenu: Cas d'étude pertinent\n`;
      action += `🎯 Objectif: Obtenir un rendez-vous pour la semaine prochaine\n`;
      action += `🔄 Fréquence suivi: 2-3 jours\n`;
    } else {
      action += `⏰ À faire ce mois-ci\n`;
      action += `📱 Moyen préféré: LinkedIn + Email\n`;
      action += `💬 Contenu: Contenu éducatif pertinent\n`;
      action += `🎯 Objectif: Réchauffer le lead\n`;
    }

    return action;
  };

  const generateConversionPrediction = (lead, history) => {
    const probability = calculateConversionProbability(lead, history);
    const expectedCloseDate = calculateExpectedCloseDate(lead, history);

    let prediction = `📈 Analyse de Conversion\n\n`;
    prediction += `Probabilité de conversion: ${probability}%\n`;
    prediction += `Date de fermeture estimée: ${expectedCloseDate}\n`;
    prediction += `\nFacteurs positifs:\n`;
    prediction += lead.budget ? `✓ Budget confirmé\n` : '';
    prediction += lead.decisionMakerIdentified ? `✓ Décideur identifié\n` : '';
    prediction += lead.proposalViewed ? `✓ Proposition consultée\n` : '';

    prediction += `\nFacteurs à améliorer:\n`;
    if (!lead.budget) prediction += `• Confirmer le budget\n`;
    if (!lead.decisionMakerIdentified) prediction += `• Identifier le décideur final\n`;
    if (lead.temperature === 'cold') prediction += `• Augmenter le niveau d'engagement\n`;

    return prediction;
  };

  const generateEmailTemplate = (lead) => {
    return {
      variant_a: `Sujet: ${lead.company} - Augmentez vos conversions de 40%\n\nBonjour ${lead.name},\n\nJe viens de terminer une analyse de votre présence en ligne. Vous avez du potentiel!\n\nNous aidons des entreprises comme la vôtre à augmenter leurs conversions rapidement.\n\n[CTA: Regarder la démo]`,
      variant_b: `Sujet: Chez ${lead.company}, comment gagnez-vous vos clients?\n\nBonjour ${lead.name},\n\nJe suis curieux de connaître votre processus de vente actuel.\n\nJe viens de voir que ${lead.company} a grandi de 30% cette année - impressionnant!\n\n[CTA: Calendrier]`,
    };
  };

  const calculateConversionProbability = (lead, history) => {
    let probability = 40;

    if (lead.budget) probability += 15;
    if (lead.decisionMakerIdentified) probability += 15;
    if (lead.proposalViewed) probability += 20;
    if (lead.temperature === 'hot') probability += 20;
    if (lead.temperature === 'warm') probability += 10;

    return Math.min(95, probability);
  };

  const calculateExpectedCloseDate = (lead, history) => {
    const now = new Date();
    let daysToAdd = 45;

    if (lead.temperature === 'hot') daysToAdd = 10;
    else if (lead.temperature === 'warm') daysToAdd = 30;
    else daysToAdd = 90;

    const closeDate = new Date(now.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
    return closeDate.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedScript(id);
    setTimeout(() => setCopiedScript(null), 2000);
  };

  if (!lead) {
    return (
      <div className="ai-suggestions empty">
        <Sparkles size={48} />
        <p>Sélectionnez un lead pour voir les suggestions IA</p>
      </div>
    );
  }

  return (
    <motion.div
      className="ai-suggestions"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.4 }}
    >
      <div className="suggestions-header">
        <Sparkles size={24} />
        <h3>Suggestions IA pour {lead.name}</h3>
      </div>

      <div className="suggestions-list">
        <AnimatePresence>
          {suggestions.map(suggestion => (
            <motion.div
              key={suggestion.id}
              className={`suggestion-card ${suggestion.type}`}
              layout
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <div className="suggestion-header">
                <div className="suggestion-title">
                  {suggestion.icon}
                  <div>
                    <h4>{suggestion.title}</h4>
                    <span className="confidence-badge">{suggestion.confidence}% confiance</span>
                  </div>
                </div>
                {suggestion.type === 'email' && (
                  <span className="ab-badge">A/B Test</span>
                )}
              </div>

              <div className="suggestion-content">
                {typeof suggestion.content === 'string' ? (
                  <pre className="content-text">{suggestion.content}</pre>
                ) : (
                  <div className="email-variants">
                    <div className="variant">
                      <h5>Variante A</h5>
                      <pre>{suggestion.content.variant_a}</pre>
                    </div>
                    <div className="variant">
                      <h5>Variante B</h5>
                      <pre>{suggestion.content.variant_b}</pre>
                    </div>
                  </div>
                )}
              </div>

              <div className="suggestion-actions">
                <button
                  className="copy-btn"
                  onClick={() => {
                    const text = typeof suggestion.content === 'string'
                      ? suggestion.content
                      : suggestion.content.variant_a + '\n---\n' + suggestion.content.variant_b;
                    copyToClipboard(text, suggestion.id);
                  }}
                  title="Copier"
                >
                  <Copy size={16} />
                  {copiedScript === suggestion.id ? 'Copié!' : 'Copier'}
                </button>

                <div className="feedback-buttons">
                  <button
                    className={`feedback-btn ${feedback[suggestion.id] === 'up' ? 'active' : ''}`}
                    onClick={() => setFeedback({ ...feedback, [suggestion.id]: 'up' })}
                    title="Utile"
                  >
                    <ThumbsUp size={16} />
                  </button>
                  <button
                    className={`feedback-btn ${feedback[suggestion.id] === 'down' ? 'active' : ''}`}
                    onClick={() => setFeedback({ ...feedback, [suggestion.id]: 'down' })}
                    title="Moins utile"
                  >
                    <ThumbsDown size={16} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default AISuggestions;
