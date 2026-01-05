import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Tabs,
  Tab,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  AutoAwesome,
  CalendarMonth,
  Link as LinkIcon,
  Analytics,
  Settings,
  Instagram,
  Twitter,
  LinkedIn,
  Facebook,
  ContentCopy,
  Send,
  Schedule,
  TrendingUp
} from '@mui/icons-material';

const MediaAutomationDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // États pour la génération de contenu
  const [selectedPlatform, setSelectedPlatform] = useState('instagram');
  const [prompt, setPrompt] = useState('');
  const [tone, setTone] = useState('professional');
  const [numVariants, setNumVariants] = useState(3);
  const [generatedContent, setGeneratedContent] = useState(null);

  // États pour les connexions
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);

  // États pour le calendrier
  const [scheduledPosts, setScheduledPosts] = useState([]);

  // États pour les analytics
  const [stats, setStats] = useState({
    totalPosts: 0,
    totalEngagement: 0,
    avgEngagementRate: 0
  });

  // Platformes disponibles
  const platforms = [
    { value: 'instagram', label: 'Instagram', icon: <Instagram /> },
    { value: 'twitter', label: 'Twitter/X', icon: <Twitter /> },
    { value: 'linkedin', label: 'LinkedIn', icon: <LinkedIn /> },
    { value: 'facebook', label: 'Facebook', icon: <Facebook /> }
  ];

  // Tons de voix
  const tones = [
    'professional', 'casual', 'friendly', 'luxury', 'playful',
    'authoritative', 'empathetic', 'witty', 'inspirational', 'educational'
  ];

  // ============================================
  // GÉNÉRATION DE CONTENU
  // ============================================

  const handleGenerateContent = async () => {
    if (!prompt.trim()) {
      setMessage({ type: 'error', text: 'Veuillez saisir un sujet' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('/api/media/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          platform: selectedPlatform,
          prompt: prompt,
          tone: tone,
          include_hashtags: true,
          include_emojis: true,
          num_variants: numVariants,
          ai_model: 'gpt-4-turbo'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedContent(data);
        setMessage({
          type: 'success',
          text: `${data.length} variante(s) générée(s) avec succès!`
        });
      } else {
        throw new Error('Erreur lors de la génération');
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Erreur: ' + error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCopyContent = (text) => {
    navigator.clipboard.writeText(text);
    setMessage({ type: 'success', text: 'Contenu copié!' });
  };

  // ============================================
  // CONNEXION PLATEFORMES
  // ============================================

  const handleConnectPlatform = async (platform) => {
    setLoading(true);

    try {
      const response = await fetch(`/api/media/platforms/${platform}/connect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          redirect_uri: `${window.location.origin}/api/media/platforms/callback`
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Rediriger vers l'URL d'autorisation
        window.location.href = data.authorization_url;
      } else {
        throw new Error('Erreur lors de la connexion');
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setLoading(false);
    }
  };

  const loadConnectedPlatforms = async () => {
    try {
      const response = await fetch('/api/media/platforms');
      if (response.ok) {
        const data = await response.json();
        setConnectedPlatforms(data);
      }
    } catch (error) {
      console.error('Erreur chargement plateformes:', error);
    }
  };

  // ============================================
  // STATISTIQUES
  // ============================================

  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/media/statistics');
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalPosts: data.total_posts_published,
          totalEngagement: data.total_engagement,
          avgEngagementRate: data.avg_engagement_rate
        });
      }
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  useEffect(() => {
    loadConnectedPlatforms();
    loadStatistics();
  }, []);

  // ============================================
  // ONGLET 1: GÉNÉRATION DE CONTENU
  // ============================================

  const renderGenerationTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        🎨 Générateur de Contenu IA
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Créez du contenu optimisé pour chaque plateforme en quelques secondes
      </Typography>

      <Grid container spacing={3}>
        {/* Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Plateforme</InputLabel>
                <Select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  label="Plateforme"
                >
                  {platforms.map((p) => (
                    <MenuItem key={p.value} value={p.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {p.icon}
                        {p.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                fullWidth
                multiline
                rows={4}
                label="Sujet / Prompt"
                placeholder="Ex: Annonce du lancement de notre nouveau service IA..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                sx={{ mb: 2 }}
              />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Ton de voix</InputLabel>
                <Select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  label="Ton de voix"
                >
                  {tones.map((t) => (
                    <MenuItem key={t} value={t}>
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Nombre de variantes</InputLabel>
                <Select
                  value={numVariants}
                  onChange={(e) => setNumVariants(e.target.value)}
                  label="Nombre de variantes"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <MenuItem key={n} value={n}>{n}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
                onClick={handleGenerateContent}
                disabled={loading}
              >
                {loading ? 'Génération...' : 'Générer du Contenu'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Résultats */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Résultats Générés
              </Typography>

              {!generatedContent ? (
                <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
                  <AutoAwesome sx={{ fontSize: 64, opacity: 0.3, mb: 2 }} />
                  <Typography>
                    Le contenu généré apparaîtra ici
                  </Typography>
                </Box>
              ) : (
                <Box>
                  {generatedContent.map((content, index) => (
                    <Paper
                      key={index}
                      sx={{ p: 2, mb: 2, border: '1px solid #e0e0e0' }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Chip
                          label={`Variante ${index + 1}`}
                          size="small"
                          color="primary"
                        />
                        <Box>
                          <Chip
                            label={`SEO: ${content.quality_score || 0}%`}
                            size="small"
                            sx={{ mr: 0.5 }}
                          />
                          <Chip
                            label={`Engagement: ${content.engagement_prediction || 0}%`}
                            size="small"
                            color="success"
                          />
                        </Box>
                      </Box>

                      <Typography sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
                        {content.generated_text}
                      </Typography>

                      {content.generated_hashtags && content.generated_hashtags.length > 0 && (
                        <Box sx={{ mb: 1 }}>
                          {content.generated_hashtags.map((tag, i) => (
                            <Chip
                              key={i}
                              label={tag}
                              size="small"
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                        </Box>
                      )}

                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          size="small"
                          startIcon={<ContentCopy />}
                          onClick={() => handleCopyContent(content.generated_text)}
                        >
                          Copier
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Schedule />}
                          variant="outlined"
                        >
                          Planifier
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Send />}
                          variant="contained"
                        >
                          Publier
                        </Button>
                      </Box>
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  // ============================================
  // ONGLET 2: CONNEXIONS PLATEFORMES
  // ============================================

  const renderPlatformsTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        🔌 Connexions aux Plateformes
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Connectez vos comptes sociaux pour publier automatiquement
      </Typography>

      <Grid container spacing={3}>
        {platforms.map((platform) => {
          const isConnected = connectedPlatforms.some(
            (p) => p.platform === platform.value
          );

          return (
            <Grid item xs={12} sm={6} md={3} key={platform.value}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ fontSize: 48, mb: 2 }}>
                    {platform.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {platform.label}
                  </Typography>

                  {isConnected ? (
                    <>
                      <Chip
                        label="Connecté"
                        color="success"
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <Button
                        fullWidth
                        variant="outlined"
                        size="small"
                        color="error"
                      >
                        Déconnecter
                      </Button>
                    </>
                  ) : (
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleConnectPlatform(platform.value)}
                      disabled={loading}
                    >
                      Connecter
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );

  // ============================================
  // ONGLET 3: CALENDRIER
  // ============================================

  const renderCalendarTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        📅 Calendrier Éditorial
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Planifiez et gérez vos publications
      </Typography>

      <Box sx={{ textAlign: 'center', py: 8 }}>
        <CalendarMonth sx={{ fontSize: 80, opacity: 0.3, mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Calendrier en cours de développement
        </Typography>
        <Typography color="text.secondary">
          Intégration FullCalendar avec drag & drop à venir
        </Typography>
      </Box>
    </Box>
  );

  // ============================================
  // ONGLET 4: ANALYTICS
  // ============================================

  const renderAnalyticsTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        📊 Analytics & Performance
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Analysez les performances de vos publications
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Publications Totales
              </Typography>
              <Typography variant="h3">
                {stats.totalPosts}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                <Typography color="success.main">+12%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Engagement Total
              </Typography>
              <Typography variant="h3">
                {stats.totalEngagement.toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                <Typography color="success.main">+25%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Taux d'Engagement Moyen
              </Typography>
              <Typography variant="h3">
                {stats.avgEngagementRate.toFixed(1)}%
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                <Typography color="success.main">+8%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  // ============================================
  // RENDER PRINCIPAL
  // ============================================

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          🚀 Automation Média Multi-Plateformes
        </Typography>
        <Typography color="text.secondary">
          Générez, planifiez et publiez du contenu sur tous vos réseaux sociaux
        </Typography>
      </Box>

      {message && (
        <Alert
          severity={message.type}
          onClose={() => setMessage(null)}
          sx={{ mb: 3 }}
        >
          {message.text}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab
            label="Génération"
            icon={<AutoAwesome />}
            iconPosition="start"
          />
          <Tab
            label="Plateformes"
            icon={<LinkIcon />}
            iconPosition="start"
          />
          <Tab
            label="Calendrier"
            icon={<CalendarMonth />}
            iconPosition="start"
          />
          <Tab
            label="Analytics"
            icon={<Analytics />}
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      <Paper>
        {activeTab === 0 && renderGenerationTab()}
        {activeTab === 1 && renderPlatformsTab()}
        {activeTab === 2 && renderCalendarTab()}
        {activeTab === 3 && renderAnalyticsTab()}
      </Paper>
    </Container>
  );
};

export default MediaAutomationDashboard;
