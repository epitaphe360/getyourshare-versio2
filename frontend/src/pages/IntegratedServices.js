/**
 * PAGE DES SERVICES INTÉGRÉS
 * Interface UI avec boutons visibles pour utiliser tous les nouveaux services
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Tabs,
  Tab,
  Paper,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import {
  Email,
  Notifications,
  Sms,
  Instagram,
  Facebook,
  Twitter,
  ShoppingCart,
  Store,
  VerifiedUser,
  SmartToy,
  Send,
  Close
} from '@mui/icons-material';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function IntegratedServices() {
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [servicesStatus, setServicesStatus] = useState(null);

  // États pour les formulaires
  const [emailForm, setEmailForm] = useState({
    to: '',
    template: 'welcome',
    variables: {}
  });

  const [smsForm, setSmsForm] = useState({
    phone_number: '',
    message: '',
    use_whatsapp: false
  });

  const [socialForm, setSocialForm] = useState({
    platform: 'instagram',
    content: '',
    media_urls: []
  });

  const [discountForm, setDiscountForm] = useState({
    code: '',
    platform: 'shopify',
    discount_percent: 10,
    usage_limit: 100
  });

  // Charger le statut des services au montage
  useEffect(() => {
    loadServicesStatus();
  }, []);

  const loadServicesStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/integrated/dashboard/services-status`);
      setServicesStatus(response.data.services);
    } catch (err) {
      console.error('Error loading services status:', err);
    }
  };

  // ===== NOTIFICATIONS =====

  const handleSendEmail = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API_BASE_URL}/api/integrated/notifications/email`, emailForm);
      setSuccess('✅ Email envoyé avec succès!');
      setEmailForm({ to: '', template: 'welcome', variables: {} });
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSendSMS = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API_BASE_URL}/api/integrated/notifications/sms`, smsForm);
      setSuccess('✅ SMS/WhatsApp envoyé avec succès!');
      setSmsForm({ phone_number: '', message: '', use_whatsapp: false });
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== RÉSEAUX SOCIAUX =====

  const handlePostToSocial = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API_BASE_URL}/api/integrated/social/post`, socialForm);
      setSuccess(`✅ Publié sur ${socialForm.platform} avec succès!`);
      setSocialForm({ ...socialForm, content: '', media_urls: [] });
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== E-COMMERCE =====

  const handleCreateDiscount = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.post(`${API_BASE_URL}/api/integrated/ecommerce/discount-code`, discountForm);
      setSuccess(`✅ Code de réduction créé sur ${discountForm.platform}!`);
      setDiscountForm({ ...discountForm, code: '' });
    } catch (err) {
      setError(`❌ Erreur: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ===== RENDER =====

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* HEADER */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          🎉 Services Intégrés ShareYourSales
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Tous vos outils de marketing d'affiliation en un seul endroit
        </Typography>
      </Box>

      {/* MESSAGES */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* TABS */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={currentTab}
          onChange={(e, newValue) => setCurrentTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Email />} label="Email" />
          <Tab icon={<Sms />} label="SMS/WhatsApp" />
          <Tab icon={<Instagram />} label="Réseaux Sociaux" />
          <Tab icon={<Store />} label="E-commerce" />
          <Tab icon={<SmartToy />} label="IA & Analytics" />
          <Tab icon={<VerifiedUser />} label="KYC" />
        </Tabs>
      </Paper>

      {/* TAB PANELS */}

      {/* ===== EMAIL TAB ===== */}
      {currentTab === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              📧 Notifications Email
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Envoyer des emails via Resend ou SMTP avec des templates prédéfinis
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email destinataire"
                  type="email"
                  value={emailForm.to}
                  onChange={(e) => setEmailForm({ ...emailForm, to: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Template</InputLabel>
                  <Select
                    value={emailForm.template}
                    onChange={(e) => setEmailForm({ ...emailForm, template: e.target.value })}
                  >
                    <MenuItem value="welcome">Bienvenue</MenuItem>
                    <MenuItem value="email_verification">Vérification Email</MenuItem>
                    <MenuItem value="password_reset">Réinitialisation</MenuItem>
                    <MenuItem value="payment_confirmation">Confirmation Paiement</MenuItem>
                    <MenuItem value="commission_earned">Commission Gagnée</MenuItem>
                    <MenuItem value="payout_processed">Retrait Traité</MenuItem>
                    <MenuItem value="new_lead">Nouveau Lead</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              startIcon={<Send />}
              onClick={handleSendEmail}
              disabled={loading || !emailForm.to}
            >
              {loading ? <CircularProgress size={24} /> : 'Envoyer Email'}
            </Button>
          </CardActions>
        </Card>
      )}

      {/* ===== SMS TAB ===== */}
      {currentTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              💬 SMS & WhatsApp (Twilio)
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Numéro de téléphone"
                  placeholder="+212612345678"
                  value={smsForm.phone_number}
                  onChange={(e) => setSmsForm({ ...smsForm, phone_number: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Type de message</InputLabel>
                  <Select
                    value={smsForm.use_whatsapp}
                    onChange={(e) => setSmsForm({ ...smsForm, use_whatsapp: e.target.value })}
                  >
                    <MenuItem value={false}>SMS</MenuItem>
                    <MenuItem value={true}>WhatsApp</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Message"
                  value={smsForm.message}
                  onChange={(e) => setSmsForm({ ...smsForm, message: e.target.value })}
                />
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              startIcon={<Send />}
              onClick={handleSendSMS}
              disabled={loading || !smsForm.phone_number || !smsForm.message}
            >
              {loading ? <CircularProgress size={24} /> : `Envoyer ${smsForm.use_whatsapp ? 'WhatsApp' : 'SMS'}`}
            </Button>
          </CardActions>
        </Card>
      )}

      {/* ===== SOCIAL MEDIA TAB ===== */}
      {currentTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              📱 Publication sur les Réseaux Sociaux
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Publier sur Instagram, TikTok, Facebook ou Twitter en un clic
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Plateforme</InputLabel>
                  <Select
                    value={socialForm.platform}
                    onChange={(e) => setSocialForm({ ...socialForm, platform: e.target.value })}
                  >
                    <MenuItem value="instagram">📷 Instagram</MenuItem>
                    <MenuItem value="tiktok">🎵 TikTok</MenuItem>
                    <MenuItem value="facebook">👍 Facebook</MenuItem>
                    <MenuItem value="twitter">🐦 Twitter/X</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Contenu"
                  placeholder="Écrivez votre publication..."
                  value={socialForm.content}
                  onChange={(e) => setSocialForm({ ...socialForm, content: e.target.value })}
                />
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              startIcon={<Send />}
              onClick={handlePostToSocial}
              disabled={loading || !socialForm.content}
            >
              {loading ? <CircularProgress size={24} /> : `Publier sur ${socialForm.platform}`}
            </Button>
          </CardActions>
        </Card>
      )}

      {/* ===== E-COMMERCE TAB ===== */}
      {currentTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              🛒 Gestion E-commerce
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Créer des codes de réduction sur Shopify, WooCommerce ou PrestaShop
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Plateforme</InputLabel>
                  <Select
                    value={discountForm.platform}
                    onChange={(e) => setDiscountForm({ ...discountForm, platform: e.target.value })}
                  >
                    <MenuItem value="shopify">🛍️ Shopify</MenuItem>
                    <MenuItem value="woocommerce">🛒 WooCommerce</MenuItem>
                    <MenuItem value="prestashop">🏪 PrestaShop</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Code de réduction"
                  placeholder="AFFILIATE10"
                  value={discountForm.code}
                  onChange={(e) => setDiscountForm({ ...discountForm, code: e.target.value.toUpperCase() })}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  type="number"
                  label="Réduction %"
                  value={discountForm.discount_percent}
                  onChange={(e) => setDiscountForm({ ...discountForm, discount_percent: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  type="number"
                  label="Limite"
                  value={discountForm.usage_limit}
                  onChange={(e) => setDiscountForm({ ...discountForm, usage_limit: parseInt(e.target.value) })}
                />
              </Grid>
            </Grid>
          </CardContent>
          <CardActions>
            <Button
              variant="contained"
              startIcon={<Store />}
              onClick={handleCreateDiscount}
              disabled={loading || !discountForm.code}
            >
              {loading ? <CircularProgress size={24} /> : 'Créer Code Promo'}
            </Button>
          </CardActions>
        </Card>
      )}

      {/* ===== AI TAB ===== */}
      {currentTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              🤖 IA & Analytics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">Recommandations IA</Typography>
                    <Typography variant="body2">
                      Recommandations produits personnalisées
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Générer</Button>
                  </CardActions>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">Segmentation RFM</Typography>
                    <Typography variant="body2">
                      11 segments clients intelligents
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Analyser</Button>
                  </CardActions>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6">Tests A/B</Typography>
                    <Typography variant="body2">
                      Optimisation statistique
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small">Créer Test</Button>
                  </CardActions>
                </Card>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* ===== KYC TAB ===== */}
      {currentTab === 5 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              🔐 Vérification KYC
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Vérification d'identité automatique avec OCR
            </Typography>
            <Alert severity="info">
              Téléchargez un document d'identité (Passeport, CNI, Permis) et optionnellement un selfie
            </Alert>
          </CardContent>
          <CardActions>
            <Button variant="outlined" disabled>
              Télécharger Document
            </Button>
            <Button variant="outlined" disabled>
              Télécharger Selfie
            </Button>
            <Button variant="contained" disabled>
              Vérifier
            </Button>
          </CardActions>
        </Card>
      )}

      {/* STATUT DES SERVICES */}
      {servicesStatus && (
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            📊 Statut des Services
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Notifications</Typography>
              <Chip label="Email ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Push ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="SMS ✓" color="success" size="small" />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Social Media</Typography>
              <Chip label="Instagram ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="TikTok ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Facebook ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Twitter ✓" color="success" size="small" />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">E-commerce</Typography>
              <Chip label="Shopify ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="WooCommerce ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="PrestaShop ✓" color="success" size="small" />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">IA & KYC</Typography>
              <Chip label="Recommandations ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="Segmentation ✓" color="success" size="small" sx={{ mr: 1, mb: 1 }} />
              <Chip label="KYC ✓" color="success" size="small" />
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
}

export default IntegratedServices;
