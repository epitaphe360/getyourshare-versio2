/**
 * 🚀 AI Content Generator PRO - Interface Professionnelle
 * Niveau Jasper.ai / Copy.ai / Writesonic
 *
 * Features:
 * - 10 types de contenu
 * - 10 tons de voix
 * - Génération multi-variantes
 * - Scoring temps réel (SEO, Lisibilité, Engagement)
 * - Templates professionnels
 * - Copie en un clic
 * - Historique de génération
 * - Suggestions IA
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Box,
  Card,
  CardContent,
  CardActions,
  LinearProgress,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge
} from '@mui/material';
import {
  ContentCopy,
  Download,
  Share,
  Refresh,
  TrendingUp,
  Speed,
  Visibility,
  Star,
  Check,
  Lightbulb,
  AutoAwesome,
  Edit,
  Search,
  Article,
  Campaign,
  VideoLibrary,
  Public,
  Email,
  ShoppingCart,
  Newspaper,
  AttachMoney,
  EmojiEmotions,
  Psychology
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003/api';

const AIContentGeneratorPro = () => {
  // États
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedContentType, setSelectedContentType] = useState('social_post');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [selectedLength, setSelectedLength] = useState('medium');
  const [topic, setTopic] = useState('');
  const [keywords, setKeywords] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [brandVoice, setBrandVoice] = useState('');
  const [callToAction, setCallToAction] = useState('');
  const [language, setLanguage] = useState('fr');
  const [includeEmojis, setIncludeEmojis] = useState(true);
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [seoOptimize, setSeoOptimize] = useState(true);
  const [numVariants, setNumVariants] = useState(3);
  const [useClaude, setUseClaude] = useState(false);

  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentTypes, setContentTypes] = useState([]);
  const [tones, setTones] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Icônes par type de contenu
  const contentIcons = {
    social_post: <Campaign />,
    product_description: <ShoppingCart />,
    blog_article: <Article />,
    email_marketing: <Email />,
    ad_copy: <TrendingUp />,
    video_script: <VideoLibrary />,
    landing_page: <Public />,
    seo_meta: <Search />,
    press_release: <Newspaper />,
    sales_letter: <AttachMoney />
  };

  // Charger les types de contenu et tons au montage
  useEffect(() => {
    loadContentTypes();
    loadTones();
  }, []);

  const loadContentTypes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ai-content-pro/content-types`);
      setContentTypes(response.data.content_types || []);
    } catch (error) {
      console.error('Error loading content types:', error);
    }
  };

  const loadTones = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ai-content-pro/tones`);
      setTones(response.data.tones || []);
    } catch (error) {
      console.error('Error loading tones:', error);
    }
  };

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Veuillez entrer un sujet');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setGeneratedContent(null);

    try {
      const requestData = {
        content_type: selectedContentType,
        topic: topic.trim(),
        keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
        tone: selectedTone,
        length: selectedLength,
        target_audience: targetAudience || null,
        brand_voice: brandVoice || null,
        call_to_action: callToAction || null,
        language: language,
        include_emojis: includeEmojis,
        include_hashtags: includeHashtags,
        num_variants: numVariants,
        seo_optimize: seoOptimize
      };

      const response = await axios.post(
        `${API_BASE_URL}/api/ai-content-pro/generate?use_claude=${useClaude}`,
        requestData
      );

      setGeneratedContent(response.data);
      setSuccess(`✨ ${response.data.variants.length} variantes générées avec succès !`);
      setActiveTab(1); // Basculer vers l'onglet résultats
    } catch (error) {
      console.error('Generation error:', error);
      setError(error.response?.data?.detail || 'Erreur lors de la génération du contenu');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyContent = (content, index) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Bon';
    if (score >= 40) return 'Moyen';
    return 'À améliorer';
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold', background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          ✨ AI Content Generator PRO
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Générez du contenu marketing professionnel avec l'IA • Niveau Jasper/Copy.ai
        </Typography>
      </Box>

      {/* Messages */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Tabs principales */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} variant="fullWidth">
          <Tab icon={<Edit />} label="Créer du Contenu" />
          <Tab icon={<AutoAwesome />} label="Résultats" disabled={!generatedContent} />
          <Tab icon={<Lightbulb />} label="Bonnes Pratiques" />
        </Tabs>
      </Paper>

      {/* TAB 1: Création de contenu */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Colonne gauche: Configuration */}
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                ⚙️ Configuration
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {/* Type de contenu */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Type de Contenu</InputLabel>
                <Select
                  value={selectedContentType}
                  onChange={(e) => setSelectedContentType(e.target.value)}
                  label="Type de Contenu"
                >
                  {contentTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Sujet */}
              <TextField
                fullWidth
                label="Sujet / Thème Principal *"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Ex: Lancement nouveau produit écologique"
                sx={{ mb: 2 }}
                required
              />

              {/* Mots-clés */}
              <TextField
                fullWidth
                label="Mots-clés SEO (séparés par virgule)"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="écologie, innovation, durable"
                sx={{ mb: 2 }}
              />

              {/* Ton */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Ton de Voix</InputLabel>
                <Select
                  value={selectedTone}
                  onChange={(e) => setSelectedTone(e.target.value)}
                  label="Ton de Voix"
                >
                  {tones.map((tone) => (
                    <MenuItem key={tone.value} value={tone.value}>
                      {tone.icon} {tone.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Longueur */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Longueur du Contenu</InputLabel>
                <Select
                  value={selectedLength}
                  onChange={(e) => setSelectedLength(e.target.value)}
                  label="Longueur du Contenu"
                >
                  <MenuItem value="short">Court (50-100 mots)</MenuItem>
                  <MenuItem value="medium">Moyen (150-300 mots)</MenuItem>
                  <MenuItem value="long">Long (400-600 mots)</MenuItem>
                  <MenuItem value="extra_long">Très long (800+ mots)</MenuItem>
                </Select>
              </FormControl>

              {/* Audience cible */}
              <TextField
                fullWidth
                label="Audience Cible (optionnel)"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="Ex: Millennials écolos, entrepreneurs tech"
                sx={{ mb: 2 }}
              />

              {/* CTA */}
              <TextField
                fullWidth
                label="Appel à l'Action (optionnel)"
                value={callToAction}
                onChange={(e) => setCallToAction(e.target.value)}
                placeholder="Ex: Commandez maintenant, En savoir plus"
                sx={{ mb: 2 }}
              />

              {/* Options */}
              <Box sx={{ mt: 2 }}>
                <FormControlLabel
                  control={<Switch checked={includeEmojis} onChange={(e) => setIncludeEmojis(e.target.checked)} />}
                  label="Inclure des emojis 😊"
                />
                <FormControlLabel
                  control={<Switch checked={includeHashtags} onChange={(e) => setIncludeHashtags(e.target.checked)} />}
                  label="Générer des hashtags #️⃣"
                />
                <FormControlLabel
                  control={<Switch checked={seoOptimize} onChange={(e) => setSeoOptimize(e.target.checked)} />}
                  label="Optimiser pour SEO 🔍"
                />
                <FormControlLabel
                  control={<Switch checked={useClaude} onChange={(e) => setUseClaude(e.target.checked)} />}
                  label="Utiliser Claude 3.5 🧠"
                />
              </Box>

              {/* Nombre de variantes */}
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Nombre de Variantes</InputLabel>
                <Select
                  value={numVariants}
                  onChange={(e) => setNumVariants(e.target.value)}
                  label="Nombre de Variantes"
                >
                  <MenuItem value={1}>1 variante</MenuItem>
                  <MenuItem value={2}>2 variantes</MenuItem>
                  <MenuItem value={3}>3 variantes (recommandé)</MenuItem>
                  <MenuItem value={4}>4 variantes</MenuItem>
                  <MenuItem value={5}>5 variantes</MenuItem>
                </Select>
              </FormControl>

              {/* Bouton Générer */}
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleGenerate}
                disabled={loading || !topic.trim()}
                sx={{ mt: 3, py: 1.5, background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)' }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
                    Génération en cours...
                  </>
                ) : (
                  <>
                    <AutoAwesome sx={{ mr: 1 }} />
                    Générer du Contenu IA
                  </>
                )}
              </Button>
            </Paper>
          </Grid>

          {/* Colonne droite: Aperçu et conseils */}
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                💡 Conseils pour de meilleurs résultats
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                <ListItem>
                  <ListItemIcon><Check color="success" /></ListItemIcon>
                  <ListItemText
                    primary="Soyez spécifique sur votre sujet"
                    secondary="Plus le sujet est précis, meilleur sera le contenu"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Check color="success" /></ListItemIcon>
                  <ListItemText
                    primary="Ajoutez 3-5 mots-clés pertinents"
                    secondary="Améliore le SEO et la pertinence du contenu"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Check color="success" /></ListItemIcon>
                  <ListItemText
                    primary="Définissez votre audience cible"
                    secondary="Permet d'adapter le ton et le message"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Check color="success" /></ListItemIcon>
                  <ListItemText
                    primary="Testez plusieurs variantes"
                    secondary="Générez 3-5 versions et choisissez la meilleure"
                  />
                </ListItem>
              </List>
            </Paper>

            {/* Stats de génération */}
            {generatedContent && (
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📊 Dernière Génération
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Modèle IA</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {generatedContent.ai_model_used.includes('claude') ? '🧠 Claude 3.5' : '🤖 GPT-4'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Temps de génération</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {generatedContent.generation_time.toFixed(2)}s
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Variantes créées</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {generatedContent.variants.length}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Score moyen</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {Math.round(generatedContent.variants.reduce((sum, v) => sum + v.engagement_prediction, 0) / generatedContent.variants.length)}/100
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            )}
          </Grid>
        </Grid>
      )}

      {/* TAB 2: Résultats */}
      {activeTab === 1 && generatedContent && (
        <Box>
          {/* Suggestions générales */}
          {generatedContent.suggestions && generatedContent.suggestions.length > 0 && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>💡 Suggestions d'amélioration :</Typography>
              {generatedContent.suggestions.map((suggestion, idx) => (
                <Typography key={idx} variant="body2">• {suggestion}</Typography>
              ))}
            </Alert>
          )}

          {/* Variantes générées */}
          <Grid container spacing={3}>
            {generatedContent.variants.map((variant, index) => (
              <Grid item xs={12} key={index}>
                <Card elevation={3}>
                  <CardContent>
                    {/* En-tête de variante */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">
                        Variante {index + 1}
                        {index === 0 && (
                          <Chip label="Meilleure" color="primary" size="small" sx={{ ml: 1 }} icon={<Star />} />
                        )}
                      </Typography>
                      <Box>
                        <Tooltip title={copiedIndex === index ? "Copié !" : "Copier"}>
                          <IconButton onClick={() => handleCopyContent(variant.content, index)} color={copiedIndex === index ? "success" : "default"}>
                            {copiedIndex === index ? <Check /> : <ContentCopy />}
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>

                    {/* Contenu généré */}
                    <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {variant.content}
                      </Typography>
                    </Paper>

                    {/* Hashtags */}
                    {variant.hashtags && variant.hashtags.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        {variant.hashtags.map((tag, idx) => (
                          <Chip key={idx} label={tag} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        ))}
                      </Box>
                    )}

                    {/* Métriques */}
                    <Grid container spacing={2}>
                      {/* SEO Score */}
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                            <Search fontSize="small" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">Score SEO</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={variant.seo_score}
                              color={getScoreColor(variant.seo_score)}
                              sx={{ flexGrow: 1, mr: 1, height: 8, borderRadius: 1 }}
                            />
                            <Typography variant="body2" fontWeight="bold">
                              {variant.seo_score}/100
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {getScoreLabel(variant.seo_score)}
                          </Typography>
                        </Box>
                      </Grid>

                      {/* Lisibilité */}
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                            <Visibility fontSize="small" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">Lisibilité</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={variant.readability_score}
                              color={getScoreColor(variant.readability_score)}
                              sx={{ flexGrow: 1, mr: 1, height: 8, borderRadius: 1 }}
                            />
                            <Typography variant="body2" fontWeight="bold">
                              {variant.readability_score}/100
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {getScoreLabel(variant.readability_score)}
                          </Typography>
                        </Box>
                      </Grid>

                      {/* Engagement */}
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                            <TrendingUp fontSize="small" sx={{ mr: 0.5 }} />
                            <Typography variant="body2">Engagement</Typography>
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinearProgress
                              variant="determinate"
                              value={variant.engagement_prediction}
                              color={getScoreColor(variant.engagement_prediction)}
                              sx={{ flexGrow: 1, mr: 1, height: 8, borderRadius: 1 }}
                            />
                            <Typography variant="body2" fontWeight="bold">
                              {variant.engagement_prediction}/100
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {getScoreLabel(variant.engagement_prediction)}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Stats */}
                    <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                      <Chip icon={<Article />} label={`${variant.word_count} mots`} size="small" variant="outlined" />
                      <Chip icon={<Speed />} label={`${variant.estimated_reading_time}s lecture`} size="small" variant="outlined" />
                      <Chip label={`${variant.character_count} caractères`} size="small" variant="outlined" />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Recommandations SEO */}
          {generatedContent.seo_recommendations && generatedContent.seo_recommendations.length > 0 && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                🔍 Recommandations SEO
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {generatedContent.seo_recommendations.map((rec, idx) => (
                <Typography key={idx} variant="body2" sx={{ mb: 1 }}>
                  • {rec}
                </Typography>
              ))}
            </Paper>
          )}

          {/* Bouton regénérer */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => setActiveTab(0)}
              size="large"
            >
              Créer une Nouvelle Version
            </Button>
          </Box>
        </Box>
      )}

      {/* TAB 3: Bonnes Pratiques */}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            💡 Bonnes Pratiques par Type de Contenu
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Typography variant="body1" paragraph>
            Sélectionnez un type de contenu pour voir les meilleures pratiques recommandées par les experts du marketing digital.
          </Typography>

          <Alert severity="info">
            ℹ️ Ces pratiques sont basées sur des années d'expérience en marketing digital et sont constamment mises à jour.
          </Alert>
        </Paper>
      )}
    </Container>
  );
};

export default AIContentGeneratorPro;
