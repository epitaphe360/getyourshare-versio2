import React, { useState, useEffect, useCallback } from 'react';
import { Mail, Eye, MousePointerClick, TrendingUp, BarChart3, Download, Send } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './EmailTracker.css';

const EmailTracker = ({ userId, leads = [] }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showCampaignForm, setShowCampaignForm] = useState(false);
  const [formData, setFormData] = useState({
    campaignName: '',
    subject: '',
    recipients: [],
    templateType: 'pitch', // pitch, followup, proposal
  });

  // Load campaigns from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(`email_campaigns_${userId}`);
    if (stored) {
      setCampaigns(JSON.parse(stored));
    }
  }, [userId]);

  // Save campaigns to localStorage
  useEffect(() => {
    localStorage.setItem(`email_campaigns_${userId}`, JSON.stringify(campaigns));
  }, [campaigns, userId]);

  // Simulate email tracking events
  useEffect(() => {
    const interval = setInterval(() => {
      setCampaigns(prevCampaigns =>
        prevCampaigns.map(campaign => {
          const updatedEmails = campaign.emails.map(email => {
            if (email.status === 'sent') {
              // 70% chance of open
              if (Math.random() < 0.7 && !email.openedAt) {
                return {
                  ...email,
                  openedAt: new Date().toISOString(),
                  opens: email.opens + 1,
                };
              }
              // 40% chance of click if opened
              if (email.openedAt && Math.random() < 0.4 && !email.firstClickAt) {
                return {
                  ...email,
                  firstClickAt: new Date().toISOString(),
                  clicks: email.clicks + 1,
                };
              }
            }
            return email;
          });

          return {
            ...campaign,
            emails: updatedEmails,
          };
        })
      );
    }, 15000); // Every 15 seconds for demo

    return () => clearInterval(interval);
  }, []);

  // Handle create campaign
  const handleCreateCampaign = (e) => {
    e.preventDefault();

    if (!formData.campaignName || !formData.recipients.length) {
      alert('Veuillez remplir les champs requis');
      return;
    }

    const newCampaign = {
      id: `campaign_${Date.now()}`,
      campaignName: formData.campaignName,
      subject: formData.subject,
      templateType: formData.templateType,
      createdAt: new Date().toISOString(),
      sentAt: null,
      stats: {
        sent: 0,
        opened: 0,
        clicked: 0,
        replied: 0,
      },
      emails: formData.recipients.map((recipient, idx) => ({
        id: `email_${Date.now()}_${idx}`,
        leadId: recipient.id,
        leadName: recipient.name,
        leadEmail: recipient.email,
        status: 'draft',
        sentAt: null,
        openedAt: null,
        firstClickAt: null,
        opens: 0,
        clicks: 0,
        replied: false,
      })),
    };

    setCampaigns([...campaigns, newCampaign]);
    setShowCampaignForm(false);
    setFormData({
      campaignName: '',
      subject: '',
      recipients: [],
      templateType: 'pitch',
    });
  };

  // Handle send campaign
  const handleSendCampaign = (campaignId) => {
    setCampaigns(campaigns.map(c =>
      c.id === campaignId
        ? {
            ...c,
            sentAt: new Date().toISOString(),
            stats: {
              ...c.stats,
              sent: c.emails.length,
            },
            emails: c.emails.map(email => ({
              ...email,
              status: 'sent',
              sentAt: new Date().toISOString(),
            })),
          }
        : c
    ));
  };

  // Calculate campaign stats
  const calculateStats = (campaign) => {
    const opened = campaign.emails.filter(e => e.openedAt).length;
    const clicked = campaign.emails.filter(e => e.firstClickAt).length;
    const replied = campaign.emails.filter(e => e.replied).length;

    return {
      sent: campaign.emails.length,
      opened,
      clicked,
      replied,
      openRate: campaign.emails.length ? ((opened / campaign.emails.length) * 100).toFixed(1) : 0,
      clickRate: campaign.emails.length ? ((clicked / campaign.emails.length) * 100).toFixed(1) : 0,
      replyRate: campaign.emails.length ? ((replied / campaign.emails.length) * 100).toFixed(1) : 0,
    };
  };

  // Generate tracking pixel
  const generateTrackingPixel = (campaignId, emailId) => {
    return `<img src="https://api.getyourshare.com/track/pixel/${campaignId}/${emailId}" width="1" height="1" alt="" style="display:none;" />`;
  };

  // Get email templates
  const getEmailTemplate = (templateType) => {
    const templates = {
      pitch: {
        subject: 'Proposition commerciale - Augmentez vos ventes',
        body: `Bonjour,

Je voudrais vous présenter notre solution qui a aidé 500+ entreprises à augmenter leur chiffre d'affaires de 35%.

[CALL TO ACTION]

Cordialement,
Votre Équipe GetYourShare`,
      },
      followup: {
        subject: 'Suivi de notre discussion - Disponible demain',
        body: `Bonjour,

Suite à nos échanges, j'aimerais vous montrer comment nous pourrions collaborer.

[CALL TO ACTION]

À bientôt,
Votre Équipe GetYourShare`,
      },
      proposal: {
        subject: 'Votre devis personnalisé - Échéance 48h',
        body: `Bonjour,

Voici votre devis personnalisé. Je reste disponible pour discuter des détails.

[CALL TO ACTION]

Merci,
Votre Équipe GetYourShare`,
      },
    };

    return templates[templateType] || templates.pitch;
  };

  // Render campaign stats card
  const renderStatsCard = (campaign) => {
    const stats = calculateStats(campaign);

    return (
      <motion.div
        className="campaign-stats-card"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h4>{campaign.campaignName}</h4>

        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-icon sent">
              <Send size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Envoyés</span>
              <span className="stat-value">{stats.sent}</span>
            </div>
          </div>

          <div className="stat-item">
            <div className="stat-icon opened">
              <Eye size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Ouvert</span>
              <span className="stat-value">{stats.opened}</span>
              <span className="stat-percentage">{stats.openRate}%</span>
            </div>
          </div>

          <div className="stat-item">
            <div className="stat-icon clicked">
              <MousePointerClick size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Cliqué</span>
              <span className="stat-value">{stats.clicked}</span>
              <span className="stat-percentage">{stats.clickRate}%</span>
            </div>
          </div>

          <div className="stat-item">
            <div className="stat-icon replied">
              <Mail size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-label">Réponse</span>
              <span className="stat-value">{stats.replied}</span>
              <span className="stat-percentage">{stats.replyRate}%</span>
            </div>
          </div>
        </div>

        <div className="campaign-timeline">
          <div className="timeline-item">
            <span className="timeline-label">Créé:</span>
            <span className="timeline-value">
              {new Date(campaign.createdAt).toLocaleDateString('fr-FR')}
            </span>
          </div>
          {campaign.sentAt && (
            <div className="timeline-item">
              <span className="timeline-label">Envoyé:</span>
              <span className="timeline-value">
                {new Date(campaign.sentAt).toLocaleDateString('fr-FR')}
              </span>
            </div>
          )}
        </div>

        <div className="campaign-actions">
          {campaign.emails[0]?.status === 'draft' ? (
            <button
              className="send-btn"
              onClick={() => handleSendCampaign(campaign.id)}
            >
              <Send size={16} />
              Envoyer la campagne
            </button>
          ) : null}
          <button
            className="details-btn"
            onClick={() => setSelectedCampaign(campaign.id)}
          >
            <BarChart3 size={16} />
            Détails
          </button>
        </div>
      </motion.div>
    );
  };

  return (
    <motion.div
      className="email-tracker"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <div className="tracker-header">
        <h2>📧 Email Tracker Pro</h2>
        <button
          className="new-campaign-btn"
          onClick={() => setShowCampaignForm(true)}
        >
          <TrendingUp size={18} />
          Nouvelle campagne
        </button>
      </div>

      <AnimatePresence>
        {selectedCampaign ? (
          <motion.div
            className="campaign-details"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            {campaigns
              .find(c => c.id === selectedCampaign)
              ?.emails.map(email => (
                <motion.div
                  key={email.id}
                  className="email-detail-row"
                  layout
                >
                  <div className="email-recipient">
                    <p className="recipient-name">{email.leadName}</p>
                    <p className="recipient-email">{email.leadEmail}</p>
                  </div>

                  <div className="email-status">
                    <span className={`status-badge ${email.status}`}>
                      {email.status === 'sent' ? '✓ Envoyé' : 'Brouillon'}
                    </span>
                  </div>

                  <div className="email-tracking">
                    <div className="tracking-item">
                      <Eye size={16} />
                      <span>
                        {email.openedAt
                          ? `Ouvert ${new Date(email.openedAt).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}`
                          : 'Non ouvert'}
                      </span>
                    </div>
                    <div className="tracking-item">
                      <MousePointerClick size={16} />
                      <span>
                        {email.firstClickAt
                          ? `Cliqué ${new Date(email.firstClickAt).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}`
                          : 'Pas de clic'}
                      </span>
                    </div>
                  </div>

                  <button
                    className="copy-pixel-btn"
                    onClick={() => {
                      const pixel = generateTrackingPixel(selectedCampaign, email.id);
                      navigator.clipboard.writeText(pixel);
                      alert('Code de suivi copié!');
                    }}
                    title="Copier le code de suivi"
                  >
                    <Download size={16} />
                  </button>
                </motion.div>
              ))}

            <button
              className="close-details-btn"
              onClick={() => setSelectedCampaign(null)}
            >
              Fermer les détails
            </button>
          </motion.div>
        ) : (
          <div className="campaigns-grid">
            {campaigns.map(campaign => (
              <div key={campaign.id}>
                {renderStatsCard(campaign)}
              </div>
            ))}
            {campaigns.length === 0 && (
              <div className="empty-state">
                <Mail size={48} />
                <p>Aucune campagne email</p>
                <p className="empty-hint">Créez votre première campagne de suivi</p>
              </div>
            )}
          </div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showCampaignForm && (
          <motion.div
            className="form-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowCampaignForm(false)}
          >
            <motion.form
              className="campaign-form"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
              onSubmit={handleCreateCampaign}
            >
              <h3>Créer une campagne email</h3>

              <input
                type="text"
                placeholder="Nom de la campagne"
                value={formData.campaignName}
                onChange={e => setFormData({ ...formData, campaignName: e.target.value })}
                required
              />

              <select
                value={formData.templateType}
                onChange={e => {
                  const template = getEmailTemplate(e.target.value);
                  setFormData({
                    ...formData,
                    templateType: e.target.value,
                    subject: template.subject,
                  });
                }}
              >
                <option value="pitch">Proposition commerciale</option>
                <option value="followup">Relance</option>
                <option value="proposal">Devis</option>
              </select>

              <input
                type="text"
                placeholder="Sujet de l'email"
                value={formData.subject}
                onChange={e => setFormData({ ...formData, subject: e.target.value })}
              />

              <label>Sélectionner les destinataires:</label>
              <div className="recipients-list">
                {leads.map(lead => (
                  <label key={lead.id} className="recipient-checkbox">
                    <input
                      type="checkbox"
                      checked={formData.recipients.some(r => r.id === lead.id)}
                      onChange={e => {
                        if (e.target.checked) {
                          setFormData({
                            ...formData,
                            recipients: [...formData.recipients, lead],
                          });
                        } else {
                          setFormData({
                            ...formData,
                            recipients: formData.recipients.filter(r => r.id !== lead.id),
                          });
                        }
                      }}
                    />
                    <span>{lead.name} ({lead.email})</span>
                  </label>
                ))}
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowCampaignForm(false)}
                >
                  Annuler
                </button>
                <button type="submit" className="submit-btn">
                  Créer la campagne
                </button>
              </div>
            </motion.form>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default EmailTracker;
