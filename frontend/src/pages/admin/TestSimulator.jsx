import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Grid, 
  Select, 
  MenuItem, 
  FormControl, 
  InputLabel,
  Alert,
  Divider,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import { 
  PlayArrow as PlayIcon, 
  AttachMoney as MoneyIcon,
  TouchApp as ClickIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

/**
 * TestSimulator - Panel Admin pour simuler des opérations de test
 * 
 * Permet de :
 * - Simuler des conversions
 * - Simuler des clics
 * - Créer des abonnements manuels
 * - Nettoyer les données de test
 */
export default function TestSimulator() {
  const [trackingLinks, setTrackingLinks] = useState([]);
  const [users, setUsers] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  
  // États pour les formulaires
  const [conversionData, setConversionData] = useState({
    tracking_link_id: '',
    sale_amount: 100,
    commission_rate: 10,
    status: 'completed',
    payment_method: 'credit_card',
    customer_email: 'test@example.com'
  });
  
  const [clickData, setClickData] = useState({
    tracking_link_id: '',
    ip_address: '192.168.1.1',
    country: 'France',
    city: 'Paris',
    device_type: 'mobile',
    browser: 'Chrome',
    referrer: 'https://instagram.com'
  });
  
  const [subscriptionData, setSubscriptionData] = useState({
    user_id: '',
    plan_id: '',
    status: 'active',
    duration_days: 30
  });
  
  // Charger les données au montage
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      const [linksRes, usersRes, plansRes] = await Promise.all([
        api.get('/api/affiliate-links/my-links'),
        api.get('/api/admin/users'),
        api.get('/api/plans')
      ]);
      
      setTrackingLinks(linksRes.data?.links || []);
      setUsers(usersRes.data?.users || []);
      setPlans(plansRes.data || []);
    } catch (error) {
      console.error('Erreur chargement données:', error);
    }
  };
  
  // Simuler une conversion
  const handleSimulateConversion = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await api.post('/api/test/conversions/simulate', conversionData);
      
      setMessage({
        type: 'success',
        text: `Conversion simulée avec succès ! ID: ${response.data.conversion.id}`
      });
      
      // Réinitialiser le formulaire
      setConversionData({
        ...conversionData,
        sale_amount: 100
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erreur : ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Simuler un clic
  const handleSimulateClick = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await api.post('/api/test/tracking/simulate-click', clickData);
      
      setMessage({
        type: 'success',
        text: `Clic simulé avec succès ! Total clics: ${response.data.event.total_clicks}`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erreur : ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Créer un abonnement manuel
  const handleCreateSubscription = async () => {
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await api.post('/api/test/subscriptions/create', subscriptionData);
      
      setMessage({
        type: 'success',
        text: `Abonnement créé avec succès ! ID: ${response.data.subscription.id}`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erreur : ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Nettoyer les données de test
  const handleCleanup = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer toutes les données de test ?')) {
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      const response = await api.delete('/api/test/cleanup');
      
      setMessage({
        type: 'success',
        text: `Nettoyage effectué : ${JSON.stringify(response.data.deleted)}`
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erreur : ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🧪 Simulateur de Tests
      </Typography>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Créez des données de test pour valider le fonctionnement de l'application
      </Typography>
      
      {message && (
        <Alert severity={message.type} sx={{ mb: 3 }} onClose={() => setMessage(null)}>
          {message.text}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Simuler une Conversion */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MoneyIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Simuler une Conversion</Typography>
              </Box>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Lien de Tracking</InputLabel>
                <Select
                  value={conversionData.tracking_link_id}
                  onChange={(e) => setConversionData({ 
                    ...conversionData, 
                    tracking_link_id: e.target.value 
                  })}
                >
                  <MenuItem value="">Sélectionner un lien</MenuItem>
                  {trackingLinks.map((link) => (
                    <MenuItem key={link.id} value={link.id}>
                      {link.unique_code} - {link.product_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Montant de vente (EUR)"
                type="number"
                value={conversionData.sale_amount}
                onChange={(e) => setConversionData({ 
                  ...conversionData, 
                  sale_amount: parseFloat(e.target.value) 
                })}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Taux de commission (%)"
                type="number"
                value={conversionData.commission_rate}
                onChange={(e) => setConversionData({ 
                  ...conversionData, 
                  commission_rate: parseFloat(e.target.value) 
                })}
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Statut</InputLabel>
                <Select
                  value={conversionData.status}
                  onChange={(e) => setConversionData({ 
                    ...conversionData, 
                    status: e.target.value 
                  })}
                >
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="refunded">Refunded</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Email client"
                type="email"
                value={conversionData.customer_email}
                onChange={(e) => setConversionData({ 
                  ...conversionData, 
                  customer_email: e.target.value 
                })}
                sx={{ mb: 2 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                color="success"
                startIcon={<PlayIcon />}
                onClick={handleSimulateConversion}
                disabled={loading || !conversionData.tracking_link_id}
              >
                Simuler Conversion
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Simuler un Clic */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ClickIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Simuler un Clic</Typography>
              </Box>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Lien de Tracking</InputLabel>
                <Select
                  value={clickData.tracking_link_id}
                  onChange={(e) => setClickData({ 
                    ...clickData, 
                    tracking_link_id: e.target.value 
                  })}
                >
                  <MenuItem value="">Sélectionner un lien</MenuItem>
                  {trackingLinks.map((link) => (
                    <MenuItem key={link.id} value={link.id}>
                      {link.unique_code} - {link.product_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Pays"
                    value={clickData.country}
                    onChange={(e) => setClickData({ 
                      ...clickData, 
                      country: e.target.value 
                    })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Ville"
                    value={clickData.city}
                    onChange={(e) => setClickData({ 
                      ...clickData, 
                      city: e.target.value 
                    })}
                  />
                </Grid>
              </Grid>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Device</InputLabel>
                    <Select
                      value={clickData.device_type}
                      onChange={(e) => setClickData({ 
                        ...clickData, 
                        device_type: e.target.value 
                      })}
                    >
                      <MenuItem value="mobile">Mobile</MenuItem>
                      <MenuItem value="desktop">Desktop</MenuItem>
                      <MenuItem value="tablet">Tablet</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Navigateur</InputLabel>
                    <Select
                      value={clickData.browser}
                      onChange={(e) => setClickData({ 
                        ...clickData, 
                        browser: e.target.value 
                      })}
                    >
                      <MenuItem value="Chrome">Chrome</MenuItem>
                      <MenuItem value="Safari">Safari</MenuItem>
                      <MenuItem value="Firefox">Firefox</MenuItem>
                      <MenuItem value="Edge">Edge</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
              
              <TextField
                fullWidth
                label="Referrer (optionnel)"
                value={clickData.referrer}
                onChange={(e) => setClickData({ 
                  ...clickData, 
                  referrer: e.target.value 
                })}
                sx={{ mb: 2 }}
                placeholder="https://instagram.com"
              />
              
              <Button
                fullWidth
                variant="contained"
                color="primary"
                startIcon={<PlayIcon />}
                onClick={handleSimulateClick}
                disabled={loading || !clickData.tracking_link_id}
              >
                Simuler Clic
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Créer Abonnement Manuel */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📅 Créer un Abonnement Manuel
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Utilisateur</InputLabel>
                <Select
                  value={subscriptionData.user_id}
                  onChange={(e) => setSubscriptionData({ 
                    ...subscriptionData, 
                    user_id: e.target.value 
                  })}
                >
                  <MenuItem value="">Sélectionner un utilisateur</MenuItem>
                  {users.map((user) => (
                    <MenuItem key={user.id} value={user.id}>
                      {user.email} ({user.role})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Plan</InputLabel>
                <Select
                  value={subscriptionData.plan_id}
                  onChange={(e) => setSubscriptionData({ 
                    ...subscriptionData, 
                    plan_id: e.target.value 
                  })}
                >
                  <MenuItem value="">Sélectionner un plan</MenuItem>
                  {plans.map((plan) => (
                    <MenuItem key={plan.id} value={plan.id}>
                      {plan.name} - {plan.price} {plan.currency}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                label="Durée (jours)"
                type="number"
                value={subscriptionData.duration_days}
                onChange={(e) => setSubscriptionData({ 
                  ...subscriptionData, 
                  duration_days: parseInt(e.target.value) 
                })}
                sx={{ mb: 2 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                startIcon={<PlayIcon />}
                onClick={handleCreateSubscription}
                disabled={loading || !subscriptionData.user_id || !subscriptionData.plan_id}
              >
                Créer Abonnement
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Nettoyage */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error">
                🗑️ Nettoyer les Données de Test
              </Typography>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Supprime toutes les conversions, clics et abonnements marqués comme "test".
                Cette action est irréversible.
              </Typography>
              
              <Button
                fullWidth
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleCleanup}
                disabled={loading}
              >
                Nettoyer les Données de Test
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
