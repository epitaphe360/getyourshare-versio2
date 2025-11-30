import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Switch,
  FormControlLabel,
  MenuItem,
  Divider,
  Alert,
  Chip,
  IconButton,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  Tooltip,
} from '@mui/material';
import {
  Settings,
  Building2,
  User,
  CreditCard,
  FileText,
  Bell,
  Shield,
  CheckCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  Plus,
  Trash2,
  Edit,
  Save,
  Globe,
  Percent,
  Calendar,
  Lock,
  DollarSign,
  Euro,
  Receipt,
  Briefcase,
  X,
} from 'lucide-react';

const TaxSettings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [saving, setSaving] = useState(false);
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  
  // Profil fiscal principal
  const [profile, setProfile] = useState({
    // Informations entreprise/auto-entrepreneur
    business_type: 'auto_entrepreneur',
    legal_name: '',
    trading_name: '',
    country: 'MA',
    address: '',
    city: '',
    postal_code: '',
    
    // Identifiants fiscaux
    tax_id: '', // ICE (Maroc), SIRET (France), EIN (USA)
    vat_number: '', // N° TVA intra (France)
    rc_number: '', // Registre Commerce (Maroc)
    patente: '', // Patente (Maroc)
    cnss_number: '', // CNSS (Maroc)
    
    // USA specifics
    ssn_ein: '',
    w9_on_file: false,
    state_tax_id: '',
    
    // France specifics
    siret: '',
    ape_code: '',
    urssaf_number: '',
    micro_enterprise: true,
    
    // Préférences
    default_currency: 'MAD',
    fiscal_year_end: '12',
    auto_calculate_tax: true,
    include_tax_in_prices: false
  });

  // Taux de taxes personnalisés
  const [customTaxRates, setCustomTaxRates] = useState([
    { id: 1, name: 'TVA Standard', rate: 20, country: 'MA', active: true },
    { id: 2, name: 'TVA Réduite', rate: 10, country: 'MA', active: true },
    { id: 3, name: 'TVA Super Réduite', rate: 7, country: 'MA', active: true }
  ]);

  // Alertes et rappels
  const [notifications, setNotifications] = useState({
    tax_deadline_reminder: true,
    invoice_overdue_alert: true,
    quarterly_report_reminder: true,
    annual_declaration_reminder: true,
    reminder_days_before: 7
  });

  // Informations bancaires pour les factures
  const [bankInfo, setBankInfo] = useState({
    bank_name: '',
    iban: '',
    bic: '',
    account_holder: ''
  });

  const handleSave = async () => {
    setSaving(true);
    try {
      // Appel API pour sauvegarder
      await new Promise(resolve => setTimeout(resolve, 1000));
      setShowSuccessAlert(true);
      setTimeout(() => setShowSuccessAlert(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const getCountryRequirements = (country) => {
    const requirements = {
      MA: {
        name: 'Maroc',
        flag: '🇲🇦',
        required: [
          { field: 'ICE', description: 'Identifiant Commun Entreprise (15 chiffres)', key: 'tax_id' },
          { field: 'IF', description: "Identifiant Fiscal", key: 'patente' },
          { field: 'RC', description: 'Registre de Commerce', key: 'rc_number' },
          { field: 'CNSS', description: 'Caisse Nationale de Sécurité Sociale', key: 'cnss_number' }
        ],
        taxRates: [
          { name: 'TVA Standard', rate: '20%' },
          { name: 'Retenue à la source', rate: '10% (prestations services)' },
          { name: 'IR Auto-entrepreneur', rate: '0.5% - 2%' }
        ]
      },
      FR: {
        name: 'France',
        flag: '🇫🇷',
        required: [
          { field: 'SIRET', description: 'Numéro SIRET (14 chiffres)', key: 'siret' },
          { field: 'N° TVA Intra', description: 'Numéro de TVA intracommunautaire', key: 'vat_number' },
          { field: 'Code APE', description: 'Activité Principale Exercée', key: 'ape_code' },
          { field: 'URSSAF', description: 'Numéro URSSAF', key: 'urssaf_number' }
        ],
        taxRates: [
          { name: 'TVA Standard', rate: '20%' },
          { name: 'Cotisations URSSAF', rate: '22% (micro-entreprise)' },
          { name: 'CFE', rate: 'Variable selon commune' }
        ]
      },
      US: {
        name: 'États-Unis',
        flag: '🇺🇸',
        required: [
          { field: 'EIN ou SSN', description: 'Employer Identification Number ou Social Security Number', key: 'ssn_ein' },
          { field: 'State Tax ID', description: 'Identifiant fiscal de l\'État', key: 'state_tax_id' },
          { field: 'Formulaire W-9', description: 'Attestation fiscale requise', key: 'w9_on_file' }
        ],
        taxRates: [
          { name: 'Federal Income Tax', rate: '10% - 37%' },
          { name: 'Self-Employment Tax', rate: '15.3%' },
          { name: 'State Tax', rate: 'Variable (0% - 13.3%)' }
        ]
      }
    };
    return requirements[country] || requirements.MA;
  };

  const renderProfileTab = () => {
    const countryInfo = getCountryRequirements(profile.country);
    
    return (
      <Box>
        {/* Sélection du pays et type d'activité */}
        <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Globe size={20} />
            Configuration Pays & Activité
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Pays de résidence fiscale"
                value={profile.country}
                onChange={(e) => {
                  const currencyMap = { MA: 'MAD', FR: 'EUR', US: 'USD' };
                  setProfile({ 
                    ...profile, 
                    country: e.target.value,
                    default_currency: currencyMap[e.target.value]
                  });
                }}
              >
                <MenuItem value="MA">🇲🇦 Maroc</MenuItem>
                <MenuItem value="FR">🇫🇷 France</MenuItem>
                <MenuItem value="US">🇺🇸 États-Unis</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Type d'activité"
                value={profile.business_type}
                onChange={(e) => setProfile({ ...profile, business_type: e.target.value })}
              >
                <MenuItem value="auto_entrepreneur">Auto-entrepreneur</MenuItem>
                <MenuItem value="individual">Indépendant / Freelance</MenuItem>
                <MenuItem value="sarl">SARL / LLC</MenuItem>
                <MenuItem value="sas">SAS / Corporation</MenuItem>
                <MenuItem value="other">Autre</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Devise par défaut"
                value={profile.default_currency}
                onChange={(e) => setProfile({ ...profile, default_currency: e.target.value })}
              >
                <MenuItem value="MAD">🇲🇦 Dirham (MAD)</MenuItem>
                <MenuItem value="EUR">🇪🇺 Euro (EUR)</MenuItem>
                <MenuItem value="USD">🇺🇸 Dollar US (USD)</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        {/* Informations légales */}
        <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Building2 size={20} />
            Informations Légales
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Raison sociale / Nom légal"
                value={profile.legal_name}
                onChange={(e) => setProfile({ ...profile, legal_name: e.target.value })}
                placeholder="Votre nom ou nom d'entreprise"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Nom commercial (optionnel)"
                value={profile.trading_name}
                onChange={(e) => setProfile({ ...profile, trading_name: e.target.value })}
                placeholder="Nom sous lequel vous opérez"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Adresse complète"
                multiline
                rows={2}
                value={profile.address}
                onChange={(e) => setProfile({ ...profile, address: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Ville"
                value={profile.city}
                onChange={(e) => setProfile({ ...profile, city: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Code postal"
                value={profile.postal_code}
                onChange={(e) => setProfile({ ...profile, postal_code: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                select
                label="Fin d'exercice fiscal"
                value={profile.fiscal_year_end}
                onChange={(e) => setProfile({ ...profile, fiscal_year_end: e.target.value })}
              >
                {[...Array(12)].map((_, i) => (
                  <MenuItem key={i} value={String(i + 1).padStart(2, '0')}>
                    {new Date(2024, i, 1).toLocaleString('fr', { month: 'long' })}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        {/* Identifiants fiscaux spécifiques au pays */}
        <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FileText size={20} />
              Identifiants Fiscaux - {countryInfo.flag} {countryInfo.name}
            </Typography>
            <Chip 
              label={`${countryInfo.required.length} champs requis`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              Ces informations sont obligatoires pour la conformité fiscale et apparaîtront sur vos factures.
            </Typography>
          </Alert>
          
          <Grid container spacing={3}>
            {countryInfo.required.map((req, index) => (
              <Grid item xs={12} md={6} key={index}>
                {req.key === 'w9_on_file' ? (
                  <FormControlLabel
                    control={
                      <Switch
                        checked={profile.w9_on_file}
                        onChange={(e) => setProfile({ ...profile, w9_on_file: e.target.checked })}
                        color="primary"
                      />
                    }
                    label={
                      <Box>
                        <Typography fontWeight={500}>{req.field}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {req.description}
                        </Typography>
                      </Box>
                    }
                  />
                ) : (
                  <TextField
                    fullWidth
                    label={req.field}
                    value={profile[req.key] || ''}
                    onChange={(e) => setProfile({ ...profile, [req.key]: e.target.value })}
                    helperText={req.description}
                    InputProps={{
                      endAdornment: profile[req.key] ? (
                        <InputAdornment position="end">
                          <CheckCircle size={18} color="#10b981" />
                        </InputAdornment>
                      ) : null
                    }}
                  />
                )}
              </Grid>
            ))}
          </Grid>

          {/* Taux de taxes du pays */}
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
              Taux d'imposition applicables
            </Typography>
            <Grid container spacing={2}>
              {countryInfo.taxRates.map((tax, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      bgcolor: '#f8fafc',
                      borderRadius: 2
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      {tax.name}
                    </Typography>
                    <Typography variant="h6" fontWeight={600} sx={{ color: '#2563eb' }}>
                      {tax.rate}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Paper>

        {/* Options de préférences */}
        <Paper sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Settings size={20} />
            Préférences de Calcul
          </Typography>
          
          <List>
            <ListItem>
              <ListItemIcon>
                <Percent size={20} />
              </ListItemIcon>
              <ListItemText
                primary="Calcul automatique des taxes"
                secondary="Appliquer automatiquement la TVA lors de la création de factures"
              />
              <ListItemSecondaryAction>
                <Switch
                  checked={profile.auto_calculate_tax}
                  onChange={(e) => setProfile({ ...profile, auto_calculate_tax: e.target.checked })}
                />
              </ListItemSecondaryAction>
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <DollarSign size={20} />
              </ListItemIcon>
              <ListItemText
                primary="Prix TTC par défaut"
                secondary="Afficher les prix toutes taxes comprises"
              />
              <ListItemSecondaryAction>
                <Switch
                  checked={profile.include_tax_in_prices}
                  onChange={(e) => setProfile({ ...profile, include_tax_in_prices: e.target.checked })}
                />
              </ListItemSecondaryAction>
            </ListItem>
            {profile.country === 'FR' && (
              <>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <Briefcase size={20} />
                  </ListItemIcon>
                  <ListItemText
                    primary="Régime micro-entreprise"
                    secondary="Bénéficier du régime fiscal simplifié (plafond CA applicable)"
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={profile.micro_enterprise}
                      onChange={(e) => setProfile({ ...profile, micro_enterprise: e.target.checked })}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </>
            )}
          </List>
        </Paper>
      </Box>
    );
  };

  const renderBankTab = () => (
    <Paper sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <CreditCard size={20} />
        Informations Bancaires
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Ces informations apparaîtront sur vos factures pour le paiement par virement.
      </Alert>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Nom de la banque"
            value={bankInfo.bank_name}
            onChange={(e) => setBankInfo({ ...bankInfo, bank_name: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Titulaire du compte"
            value={bankInfo.account_holder}
            onChange={(e) => setBankInfo({ ...bankInfo, account_holder: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} md={8}>
          <TextField
            fullWidth
            label="IBAN / RIB"
            value={bankInfo.iban}
            onChange={(e) => setBankInfo({ ...bankInfo, iban: e.target.value })}
            placeholder={profile.country === 'MA' ? 'MA76...' : profile.country === 'FR' ? 'FR76...' : 'Routing + Account'}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="BIC / SWIFT"
            value={bankInfo.bic}
            onChange={(e) => setBankInfo({ ...bankInfo, bic: e.target.value })}
          />
        </Grid>
      </Grid>
    </Paper>
  );

  const renderNotificationsTab = () => (
    <Paper sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Bell size={20} />
        Rappels & Alertes Fiscales
      </Typography>
      
      <List>
        <ListItem>
          <ListItemIcon>
            <Calendar size={20} />
          </ListItemIcon>
          <ListItemText
            primary="Rappel échéances fiscales"
            secondary="Recevoir une notification avant les dates limites de déclaration"
          />
          <ListItemSecondaryAction>
            <Switch
              checked={notifications.tax_deadline_reminder}
              onChange={(e) => setNotifications({ ...notifications, tax_deadline_reminder: e.target.checked })}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <Divider />
        <ListItem>
          <ListItemIcon>
            <AlertTriangle size={20} />
          </ListItemIcon>
          <ListItemText
            primary="Alertes factures en retard"
            secondary="Être notifié quand une facture dépasse son échéance"
          />
          <ListItemSecondaryAction>
            <Switch
              checked={notifications.invoice_overdue_alert}
              onChange={(e) => setNotifications({ ...notifications, invoice_overdue_alert: e.target.checked })}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <Divider />
        <ListItem>
          <ListItemIcon>
            <FileText size={20} />
          </ListItemIcon>
          <ListItemText
            primary="Rappel rapports trimestriels"
            secondary="Notification pour préparer les déclarations trimestrielles"
          />
          <ListItemSecondaryAction>
            <Switch
              checked={notifications.quarterly_report_reminder}
              onChange={(e) => setNotifications({ ...notifications, quarterly_report_reminder: e.target.checked })}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <Divider />
        <ListItem>
          <ListItemIcon>
            <Receipt size={20} />
          </ListItemIcon>
          <ListItemText
            primary="Rappel déclaration annuelle"
            secondary="Notification pour la déclaration de revenus annuelle"
          />
          <ListItemSecondaryAction>
            <Switch
              checked={notifications.annual_declaration_reminder}
              onChange={(e) => setNotifications({ ...notifications, annual_declaration_reminder: e.target.checked })}
            />
          </ListItemSecondaryAction>
        </ListItem>
        <Divider />
        <ListItem>
          <ListItemIcon>
            <Bell size={20} />
          </ListItemIcon>
          <ListItemText
            primary="Délai de rappel"
            secondary="Nombre de jours avant l'échéance pour recevoir le rappel"
          />
          <ListItemSecondaryAction>
            <TextField
              type="number"
              size="small"
              value={notifications.reminder_days_before}
              onChange={(e) => setNotifications({ 
                ...notifications, 
                reminder_days_before: parseInt(e.target.value) || 7 
              })}
              sx={{ width: 80 }}
              InputProps={{
                endAdornment: <InputAdornment position="end">jours</InputAdornment>
              }}
            />
          </ListItemSecondaryAction>
        </ListItem>
      </List>
    </Paper>
  );

  const renderTaxRatesTab = () => (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" fontWeight={600} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Percent size={20} />
            Taux de Taxes Personnalisés
          </Typography>
          <Button startIcon={<Plus size={18} />} variant="outlined" size="small">
            Ajouter un taux
          </Button>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Configurez des taux de taxes personnalisés en plus des taux standards de votre pays.
        </Alert>
        
        {customTaxRates.map((rate) => (
          <Paper 
            key={rate.id} 
            variant="outlined" 
            sx={{ 
              p: 2, 
              mb: 2, 
              display: 'flex', 
              alignItems: 'center',
              justifyContent: 'space-between',
              bgcolor: rate.active ? '#f8fafc' : '#fef2f2',
              borderRadius: 2
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                bgcolor: rate.active ? '#e0e7ff' : '#fee2e2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Percent size={20} color={rate.active ? '#4f46e5' : '#ef4444'} />
              </Box>
              <Box>
                <Typography fontWeight={600}>{rate.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {rate.country === 'MA' ? '🇲🇦' : rate.country === 'FR' ? '🇫🇷' : '🇺🇸'} · 
                  {rate.active ? ' Actif' : ' Inactif'}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h6" fontWeight={700} sx={{ color: '#2563eb' }}>
                {rate.rate}%
              </Typography>
              <Switch
                checked={rate.active}
                onChange={(e) => {
                  setCustomTaxRates(customTaxRates.map(r => 
                    r.id === rate.id ? { ...r, active: e.target.checked } : r
                  ));
                }}
              />
              <IconButton size="small">
                <Edit size={18} />
              </IconButton>
              <IconButton size="small" color="error">
                <Trash2 size={18} />
              </IconButton>
            </Box>
          </Paper>
        ))}
      </Paper>

      {/* Échéances fiscales */}
      <Paper sx={{ p: 3, borderRadius: 2 }}>
        <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Calendar size={20} />
          Calendrier Fiscal - {profile.country === 'MA' ? '🇲🇦 Maroc' : profile.country === 'FR' ? '🇫🇷 France' : '🇺🇸 USA'}
        </Typography>

        {profile.country === 'MA' && (
          <Grid container spacing={2}>
            {[
              { month: 'Janvier', deadline: '20', desc: 'Déclaration TVA décembre' },
              { month: 'Février', deadline: '28', desc: 'Déclaration IR annuel' },
              { month: 'Mars', deadline: '31', desc: 'Bilan annuel' },
              { month: 'Avril', deadline: '20', desc: 'Déclaration TVA T1' }
            ].map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                  <Typography variant="body2" color="text.secondary">{item.month}</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#2563eb' }}>
                    {item.deadline}
                  </Typography>
                  <Typography variant="caption">{item.desc}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {profile.country === 'FR' && (
          <Grid container spacing={2}>
            {[
              { month: 'Janvier', deadline: '15', desc: 'Déclaration CA (micro)' },
              { month: 'Avril', deadline: '15', desc: 'Déclaration CA T1' },
              { month: 'Mai', deadline: '31', desc: 'Déclaration revenus' },
              { month: 'Juillet', deadline: '15', desc: 'Déclaration CA T2' }
            ].map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                  <Typography variant="body2" color="text.secondary">{item.month}</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#2563eb' }}>
                    {item.deadline}
                  </Typography>
                  <Typography variant="caption">{item.desc}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {profile.country === 'US' && (
          <Grid container spacing={2}>
            {[
              { month: 'Janvier', deadline: '15', desc: 'Q4 Estimated Tax' },
              { month: 'Avril', deadline: '15', desc: 'Annual Tax Return' },
              { month: 'Juin', deadline: '15', desc: 'Q2 Estimated Tax' },
              { month: 'Septembre', deadline: '15', desc: 'Q3 Estimated Tax' }
            ].map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Paper variant="outlined" sx={{ p: 2, textAlign: 'center', borderRadius: 2 }}>
                  <Typography variant="body2" color="text.secondary">{item.month}</Typography>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#2563eb' }}>
                    {item.deadline}
                  </Typography>
                  <Typography variant="caption">{item.desc}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
    </Box>
  );

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} sx={{ 
          background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          mb: 1
        }}>
          Paramètres Fiscaux
        </Typography>
        <Typography color="text.secondary">
          Configurez votre profil fiscal pour le Maroc, France ou États-Unis
        </Typography>
      </Box>

      {/* Success Alert */}
      {showSuccessAlert && (
        <Alert 
          severity="success" 
          sx={{ mb: 3, borderRadius: 2 }}
          icon={<CheckCircle size={20} />}
        >
          Paramètres sauvegardés avec succès !
        </Alert>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs 
          value={activeTab} 
          onChange={(e, v) => setActiveTab(v)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab 
            icon={<User size={18} />} 
            iconPosition="start" 
            label="Profil Fiscal" 
          />
          <Tab 
            icon={<CreditCard size={18} />} 
            iconPosition="start" 
            label="Informations Bancaires" 
          />
          <Tab 
            icon={<Percent size={18} />} 
            iconPosition="start" 
            label="Taux & Échéances" 
          />
          <Tab 
            icon={<Bell size={18} />} 
            iconPosition="start" 
            label="Notifications" 
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ mb: 4 }}>
        {activeTab === 0 && renderProfileTab()}
        {activeTab === 1 && renderBankTab()}
        {activeTab === 2 && renderTaxRatesTab()}
        {activeTab === 3 && renderNotificationsTab()}
      </Box>

      {/* Save Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button variant="outlined" sx={{ px: 4 }}>
          Annuler
        </Button>
        <Button
          variant="contained"
          startIcon={saving ? null : <Save size={18} />}
          onClick={handleSave}
          disabled={saving}
          sx={{
            px: 4,
            background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)'
          }}
        >
          {saving ? 'Sauvegarde...' : 'Sauvegarder'}
        </Button>
      </Box>
    </Box>
  );
};

export default TaxSettings;
