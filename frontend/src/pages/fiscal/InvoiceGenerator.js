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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Alert,
  CircularProgress,
  Tooltip,
  InputAdornment,
  Autocomplete,
  Stepper,
  Step,
  StepLabel,
  Snackbar,
} from '@mui/material';
import fiscalService from '../../services/fiscalService';
import PDFViewer from '../../components/fiscal/PDFViewer';
import {
  FileText,
  Plus,
  Download,
  Eye,
  Trash2,
  Send,
  CheckCircle,
  Clock,
  AlertCircle,
  Search,
  Filter,
  Calendar,
  Building2,
  User,
  DollarSign,
  Euro,
  Receipt,
  Copy,
  Edit,
  MoreVertical,
  ArrowLeft,
  X,
} from 'lucide-react';

const CURRENCY_SYMBOLS = {
  MAD: 'DH',
  EUR: '€',
  USD: '$'
};

const TAX_RATES = {
  MA: { tva: 0.20, name: 'TVA Maroc' },
  FR: { tva: 0.20, name: 'TVA France' },
  US: { tax: 0, name: 'Sales Tax (varies by state)' }
};

const InvoiceGenerator = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [currentPdfUrl, setCurrentPdfUrl] = useState(null);
  const [currentPdfTitle, setCurrentPdfTitle] = useState('');
  
  // Form state for new invoice
  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    client_address: '',
    client_country: 'MA',
    client_tax_id: '',
    items: [{ description: '', quantity: 1, unit_price: 0 }],
    notes: '',
    payment_terms: 30,
    currency: 'MAD'
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      
      // ✅ APPEL API RÉEL
      const result = await fiscalService.getInvoices({ 
        status: filterStatus !== 'all' ? filterStatus : undefined 
      });
      
      // Mapper les données backend vers format frontend
      const mappedInvoices = (result.invoices || result.data || []).map(inv => ({
        id: inv.invoice_number || inv.id,
        client_name: inv.client_name,
        client_country: inv.country,
        amount: inv.amount_ht,
        tax_amount: inv.vat_amount,
        total: inv.amount_ttc,
        currency: inv.currency,
        status: inv.status,
        created_at: inv.issue_date,
        due_date: inv.due_date,
        raw: inv // Garder données brutes
      }));
      
      setInvoices(mappedInvoices);
      
    } catch (error) {
      console.error('Error fetching invoices:', error);
      setSnackbar({
        open: true,
        message: `Erreur chargement factures: ${error.message}`,
        severity: 'error'
      });
      
      // Fallback vers données mockées en cas d'erreur
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { description: '', quantity: 1, unit_price: 0 }]
    });
  };

  const handleRemoveItem = (index) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index][field] = value;
    setFormData({ ...formData, items: newItems });
  };

  const calculateSubtotal = () => {
    return formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  };

  const calculateTax = () => {
    const subtotal = calculateSubtotal();
    const taxRate = TAX_RATES[formData.client_country]?.tva || 0;
    return subtotal * taxRate;
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const handleCreateInvoice = async () => {
    try {
      setLoading(true);
      
      // Préparer données backend
      const invoiceData = {
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_address: formData.client_address,
        client_tax_id: formData.client_tax_id,
        country: formData.client_country,
        currency: formData.currency,
        amount_ht: calculateSubtotal(),
        vat_rate: (TAX_RATES[formData.client_country]?.tva || 0) * 100,
        vat_amount: calculateTax(),
        amount_ttc: calculateTotal(),
        payment_method: 'bank_transfer',
        status: 'draft',
        notes: formData.notes,
        items: formData.items.filter(item => item.description), // Enlever items vides
        due_date: new Date(Date.now() + formData.payment_terms * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      };
      
      // ✅ APPEL API RÉEL
      const result = await fiscalService.createInvoice(invoiceData);
      
      setSnackbar({
        open: true,
        message: `✅ Facture ${result.invoice_number || result.id} créée avec succès!`,
        severity: 'success'
      });
      
      // Fermer dialog et réinitialiser
      setShowCreateDialog(false);
      setActiveStep(0);
      setFormData({
        client_name: '',
        client_email: '',
        client_address: '',
        client_country: 'MA',
        client_tax_id: '',
        items: [{ description: '', quantity: 1, unit_price: 0 }],
        notes: '',
        payment_terms: 30,
        currency: 'MAD'
      });
      
      // Recharger liste
      fetchInvoices();
      
    } catch (error) {
      console.error('Error creating invoice:', error);
      setSnackbar({
        open: true,
        message: `❌ Erreur création facture: ${error.message}`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (status) => {
    const configs = {
      paid: { color: '#10b981', bg: '#10b98115', icon: CheckCircle, label: 'Payée' },
      pending: { color: '#f59e0b', bg: '#f59e0b15', icon: Clock, label: 'En attente' },
      overdue: { color: '#ef4444', bg: '#ef444415', icon: AlertCircle, label: 'En retard' },
      draft: { color: '#6b7280', bg: '#6b728015', icon: FileText, label: 'Brouillon' }
    };
    return configs[status] || configs.draft;
  };

  const formatCurrency = (amount, currency) => {
    return `${amount.toLocaleString()} ${CURRENCY_SYMBOLS[currency] || currency}`;
  };

  /**
   * ✅ Générer et afficher PDF inline
   */
  const handleDownloadPDF = async (invoiceId) => {
    try {
      setGeneratingPDF(true);
      
      // Générer le PDF et récupérer le blob URL
      const pdfBlob = await fiscalService.generateInvoicePDF(invoiceId);
      const pdfUrl = URL.createObjectURL(pdfBlob);
      
      // Trouver l'invoice pour le titre
      const invoice = invoices.find(inv => inv.id === invoiceId);
      const fileName = `Facture_${invoice?.invoice_number || invoiceId}.pdf`;
      
      // Ouvrir le viewer inline
      setCurrentPdfUrl(pdfUrl);
      setCurrentPdfTitle(fileName);
      setPdfViewerOpen(true);
      
      setSnackbar({
        open: true,
        message: '✅ PDF généré avec succès!',
        severity: 'success'
      });
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      setSnackbar({
        open: true,
        message: `❌ Erreur génération PDF: ${error.message}`,
        severity: 'error'
      });
    } finally {
      setGeneratingPDF(false);
    }
  };

  /**
   * Fermer le PDF viewer et nettoyer le blob URL
   */
  const handleClosePdfViewer = () => {
    if (currentPdfUrl) {
      URL.revokeObjectURL(currentPdfUrl);
    }
    setPdfViewerOpen(false);
    setCurrentPdfUrl(null);
    setCurrentPdfTitle('');
  };

  /**
   * ✅ Envoyer facture par email
   */
  const handleSendEmail = async (invoiceId) => {
    try {
      setSendingEmail(true);
      
      const result = await fiscalService.sendInvoiceEmail(invoiceId);
      
      setSnackbar({
        open: true,
        message: `✅ Email envoyé avec succès à ${result.to_email || 'client'}!`,
        severity: 'success'
      });
      
      // Recharger pour mettre à jour statut
      fetchInvoices();
      
    } catch (error) {
      console.error('Error sending email:', error);
      setSnackbar({
        open: true,
        message: `❌ Erreur envoi email: ${error.message}`,
        severity: 'error'
      });
    } finally {
      setSendingEmail(false);
    }
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         invoice.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || invoice.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const steps = ['Informations client', 'Articles & Services', 'Aperçu & Confirmation'];

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nom du client / Entreprise"
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.client_email}
                  onChange={(e) => setFormData({ ...formData, client_email: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Adresse"
                  multiline
                  rows={2}
                  value={formData.client_address}
                  onChange={(e) => setFormData({ ...formData, client_address: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  select
                  label="Pays"
                  value={formData.client_country}
                  onChange={(e) => {
                    const country = e.target.value;
                    const currencyMap = { MA: 'MAD', FR: 'EUR', US: 'USD' };
                    setFormData({ 
                      ...formData, 
                      client_country: country,
                      currency: currencyMap[country]
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
                  label={formData.client_country === 'MA' ? 'ICE / IF' : 
                         formData.client_country === 'FR' ? 'N° TVA Intra / SIRET' : 
                         'EIN / Tax ID'}
                  value={formData.client_tax_id}
                  onChange={(e) => setFormData({ ...formData, client_tax_id: e.target.value })}
                  helperText={
                    formData.client_country === 'MA' ? 'Identifiant Commun Entreprise' :
                    formData.client_country === 'FR' ? 'TVA intracommunautaire' :
                    'Employer Identification Number'
                  }
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  select
                  label="Conditions de paiement"
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                >
                  <MenuItem value={0}>Paiement immédiat</MenuItem>
                  <MenuItem value={15}>Net 15 jours</MenuItem>
                  <MenuItem value={30}>Net 30 jours</MenuItem>
                  <MenuItem value={45}>Net 45 jours</MenuItem>
                  <MenuItem value={60}>Net 60 jours</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Box>
        );
      
      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, color: '#6b7280' }}>
              Articles / Services
            </Typography>
            
            {formData.items.map((item, index) => (
              <Paper 
                key={index} 
                sx={{ 
                  p: 2, 
                  mb: 2, 
                  bgcolor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: 2
                }}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={5}>
                    <TextField
                      fullWidth
                      label="Description"
                      placeholder="Service d'influence marketing..."
                      value={item.description}
                      onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6} md={2}>
                    <TextField
                      fullWidth
                      label="Quantité"
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 0)}
                      size="small"
                      inputProps={{ min: 1 }}
                    />
                  </Grid>
                  <Grid item xs={6} md={2}>
                    <TextField
                      fullWidth
                      label="Prix unitaire"
                      type="number"
                      value={item.unit_price}
                      onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                      size="small"
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            {CURRENCY_SYMBOLS[formData.currency]}
                          </InputAdornment>
                        )
                      }}
                    />
                  </Grid>
                  <Grid item xs={10} md={2}>
                    <Typography variant="body2" color="text.secondary">
                      Total: <strong>{formatCurrency(item.quantity * item.unit_price, formData.currency)}</strong>
                    </Typography>
                  </Grid>
                  <Grid item xs={2} md={1}>
                    {formData.items.length > 1 && (
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleRemoveItem(index)}
                      >
                        <Trash2 size={18} />
                      </IconButton>
                    )}
                  </Grid>
                </Grid>
              </Paper>
            ))}
            
            <Button
              startIcon={<Plus size={18} />}
              onClick={handleAddItem}
              sx={{ mb: 3 }}
            >
              Ajouter un article
            </Button>

            <Divider sx={{ my: 3 }} />

            {/* Totaux */}
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Box sx={{ width: 300 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Sous-total:</Typography>
                  <Typography fontWeight={500}>
                    {formatCurrency(calculateSubtotal(), formData.currency)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">
                    {TAX_RATES[formData.client_country]?.name || 'TVA'} 
                    ({(TAX_RATES[formData.client_country]?.tva || 0) * 100}%):
                  </Typography>
                  <Typography fontWeight={500}>
                    {formatCurrency(calculateTax(), formData.currency)}
                  </Typography>
                </Box>
                <Divider sx={{ my: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography fontWeight={600}>Total TTC:</Typography>
                  <Typography fontWeight={700} sx={{ color: '#2563eb', fontSize: '1.1rem' }}>
                    {formatCurrency(calculateTotal(), formData.currency)}
                  </Typography>
                </Box>
              </Box>
            </Box>

            <TextField
              fullWidth
              label="Notes / Mentions légales"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              sx={{ mt: 3 }}
              placeholder="Conditions particulières, informations bancaires..."
            />
          </Box>
        );
      
      case 2:
        return (
          <Box sx={{ mt: 3 }}>
            <Paper 
              sx={{ 
                p: 4, 
                background: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
                border: '1px solid #e2e8f0',
                borderRadius: 3
              }}
            >
              {/* En-tête facture */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
                <Box>
                  <Typography variant="h4" fontWeight={700} sx={{ color: '#1e293b' }}>
                    FACTURE
                  </Typography>
                  <Typography color="text.secondary">
                    N° INV-2024-XXX
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography fontWeight={600}>GetYourShare</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Plateforme d'influence marketing
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ mb: 3 }} />

              {/* Infos client */}
              <Grid container spacing={4} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    FACTURER À
                  </Typography>
                  <Typography fontWeight={600}>{formData.client_name || '---'}</Typography>
                  <Typography variant="body2">{formData.client_email}</Typography>
                  <Typography variant="body2">{formData.client_address || '---'}</Typography>
                  {formData.client_tax_id && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      ID Fiscal: {formData.client_tax_id}
                    </Typography>
                  )}
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                      DÉTAILS
                    </Typography>
                    <Typography variant="body2">
                      Date: {new Date().toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">
                      Échéance: {new Date(Date.now() + formData.payment_terms * 24 * 60 * 60 * 1000).toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">
                      Devise: {formData.currency}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {/* Tableau des articles */}
              <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: '#f1f5f9' }}>
                    <TableRow>
                      <TableCell><strong>Description</strong></TableCell>
                      <TableCell align="center"><strong>Qté</strong></TableCell>
                      <TableCell align="right"><strong>Prix unit.</strong></TableCell>
                      <TableCell align="right"><strong>Total</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formData.items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.description || '---'}</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(item.unit_price, formData.currency)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(item.quantity * item.unit_price, formData.currency)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Totaux */}
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Box sx={{ width: 280 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                    <Typography>Sous-total HT:</Typography>
                    <Typography fontWeight={500}>
                      {formatCurrency(calculateSubtotal(), formData.currency)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                    <Typography>TVA ({(TAX_RATES[formData.client_country]?.tva || 0) * 100}%):</Typography>
                    <Typography fontWeight={500}>
                      {formatCurrency(calculateTax(), formData.currency)}
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    py: 1.5,
                    bgcolor: '#2563eb10',
                    px: 2,
                    borderRadius: 1
                  }}>
                    <Typography fontWeight={700}>TOTAL TTC:</Typography>
                    <Typography fontWeight={700} sx={{ color: '#2563eb', fontSize: '1.2rem' }}>
                      {formatCurrency(calculateTotal(), formData.currency)}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              {formData.notes && (
                <Box sx={{ mt: 4, p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    Notes
                  </Typography>
                  <Typography variant="body2">{formData.notes}</Typography>
                </Box>
              )}
            </Paper>
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mb: 4 
      }}>
        <Box>
          <Typography variant="h4" fontWeight={700} sx={{ 
            background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Gestion des Factures
          </Typography>
          <Typography color="text.secondary">
            Créez et gérez vos factures conformes pour le Maroc, France et USA
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Plus size={20} />}
          onClick={() => setShowCreateDialog(true)}
          sx={{
            background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
            px: 3,
            py: 1.5,
            borderRadius: 2
          }}
        >
          Nouvelle Facture
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { 
            title: 'Total Facturé', 
            value: '26,000 DH', 
            subvalue: '+12% ce mois',
            icon: Receipt, 
            gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)' 
          },
          { 
            title: 'Payées', 
            value: '3', 
            subvalue: '18,000 DH',
            icon: CheckCircle, 
            gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' 
          },
          { 
            title: 'En Attente', 
            value: '2', 
            subvalue: '5,500 DH',
            icon: Clock, 
            gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)' 
          },
          { 
            title: 'En Retard', 
            value: '1', 
            subvalue: '2,500 DH',
            icon: AlertCircle, 
            gradient: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)' 
          }
        ].map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ 
              background: stat.gradient,
              color: 'white',
              borderRadius: 3,
              position: 'relative',
              overflow: 'hidden'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9, mb: 0.5 }}>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stat.value}
                    </Typography>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      {stat.subvalue}
                    </Typography>
                  </Box>
                  <Box sx={{ 
                    p: 1.5, 
                    bgcolor: 'rgba(255,255,255,0.2)', 
                    borderRadius: 2 
                  }}>
                    <stat.icon size={24} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Rechercher par client ou n° facture..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              size="small"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search size={18} color="#9ca3af" />
                  </InputAdornment>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              size="small"
              label="Statut"
            >
              <MenuItem value="all">Tous les statuts</MenuItem>
              <MenuItem value="paid">Payées</MenuItem>
              <MenuItem value="pending">En attente</MenuItem>
              <MenuItem value="overdue">En retard</MenuItem>
              <MenuItem value="draft">Brouillons</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Download size={18} />}
            >
              Exporter
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Invoices Table */}
      <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#f8fafc' }}>
              <TableRow>
                <TableCell><strong>N° Facture</strong></TableCell>
                <TableCell><strong>Client</strong></TableCell>
                <TableCell><strong>Pays</strong></TableCell>
                <TableCell align="right"><strong>Montant HT</strong></TableCell>
                <TableCell align="right"><strong>TVA</strong></TableCell>
                <TableCell align="right"><strong>Total TTC</strong></TableCell>
                <TableCell><strong>Statut</strong></TableCell>
                <TableCell><strong>Date</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 5 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredInvoices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 5 }}>
                    <Typography color="text.secondary">
                      Aucune facture trouvée
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredInvoices.map((invoice) => {
                  const statusConfig = getStatusConfig(invoice.status);
                  const StatusIcon = statusConfig.icon;
                  return (
                    <TableRow 
                      key={invoice.id}
                      sx={{ 
                        '&:hover': { bgcolor: '#f8fafc' },
                        transition: 'background 0.2s'
                      }}
                    >
                      <TableCell>
                        <Typography fontWeight={600} sx={{ color: '#2563eb' }}>
                          {invoice.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{
                            width: 36,
                            height: 36,
                            borderRadius: 1,
                            bgcolor: '#e0e7ff',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <Building2 size={18} color="#4f46e5" />
                          </Box>
                          <Typography fontWeight={500}>{invoice.client_name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={invoice.client_country === 'MA' ? '🇲🇦 Maroc' :
                                 invoice.client_country === 'FR' ? '🇫🇷 France' : '🇺🇸 USA'}
                          size="small"
                          sx={{ bgcolor: '#f1f5f9' }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(invoice.amount, invoice.currency)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(invoice.tax_amount, invoice.currency)}
                      </TableCell>
                      <TableCell align="right">
                        <Typography fontWeight={600}>
                          {formatCurrency(invoice.total, invoice.currency)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={<StatusIcon size={14} />}
                          label={statusConfig.label}
                          size="small"
                          sx={{
                            bgcolor: statusConfig.bg,
                            color: statusConfig.color,
                            fontWeight: 500,
                            '& .MuiChip-icon': { color: statusConfig.color }
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(invoice.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                          <Tooltip title="Voir">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedInvoice(invoice);
                                setShowPreviewDialog(true);
                              }}
                            >
                              <Eye size={18} />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Télécharger PDF">
                            <IconButton 
                              size="small"
                              onClick={() => handleDownloadPDF(invoice.id)}
                              disabled={generatingPDF}
                            >
                              {generatingPDF ? (
                                <CircularProgress size={18} />
                              ) : (
                                <Download size={18} />
                              )}
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Envoyer par email">
                            <IconButton 
                              size="small"
                              onClick={() => handleSendEmail(invoice.id)}
                              disabled={sendingEmail}
                            >
                              {sendingEmail ? (
                                <CircularProgress size={18} />
                              ) : (
                                <Send size={18} />
                              )}
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create Invoice Dialog */}
      <Dialog 
        open={showCreateDialog} 
        onClose={() => setShowCreateDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ 
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <FileText color="white" size={20} />
            </Box>
            <Typography variant="h6" fontWeight={600}>
              Nouvelle Facture
            </Typography>
          </Box>
          <IconButton onClick={() => setShowCreateDialog(false)}>
            <X size={20} />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ pt: 3 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {renderStepContent(activeStep)}
        </DialogContent>
        
        <DialogActions sx={{ p: 3, borderTop: '1px solid #e2e8f0' }}>
          <Button
            onClick={() => setShowCreateDialog(false)}
            sx={{ color: '#6b7280' }}
          >
            Annuler
          </Button>
          {activeStep > 0 && (
            <Button onClick={() => setActiveStep(activeStep - 1)}>
              Retour
            </Button>
          )}
          {activeStep < steps.length - 1 ? (
            <Button 
              variant="contained" 
              onClick={() => setActiveStep(activeStep + 1)}
              disabled={activeStep === 0 && !formData.client_name}
            >
              Suivant
            </Button>
          ) : (
            <Button
              variant="contained"
              startIcon={<CheckCircle size={18} />}
              onClick={handleCreateInvoice}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
              }}
            >
              Créer la Facture
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog
        open={showPreviewDialog}
        onClose={() => setShowPreviewDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" fontWeight={600}>
              Aperçu Facture {selectedInvoice?.id}
            </Typography>
            <IconButton onClick={() => setShowPreviewDialog(false)}>
              <X size={20} />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ p: 4 }}>
          {selectedInvoice && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                Cette facture est conforme aux exigences fiscales de{' '}
                {selectedInvoice.client_country === 'MA' ? 'Maroc (TVA 20%)' :
                 selectedInvoice.client_country === 'FR' ? 'France (TVA 20%)' : 'USA'}
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Client</Typography>
                  <Typography fontWeight={600}>{selectedInvoice.client_name}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Montant Total</Typography>
                  <Typography variant="h5" fontWeight={700} sx={{ color: '#2563eb' }}>
                    {formatCurrency(selectedInvoice.total, selectedInvoice.currency)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid #e2e8f0' }}>
          <Button 
            startIcon={<Download size={18} />} 
            variant="outlined"
            onClick={() => selectedInvoice && handleDownloadPDF(selectedInvoice.id)}
            disabled={generatingPDF}
          >
            {generatingPDF ? 'Génération...' : 'Télécharger PDF'}
          </Button>
          <Button 
            startIcon={<Send size={18} />} 
            variant="contained"
            onClick={() => selectedInvoice && handleSendEmail(selectedInvoice.id)}
            disabled={sendingEmail}
          >
            {sendingEmail ? 'Envoi...' : 'Envoyer au client'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* ✅ PDF Viewer Modal */}
      <PDFViewer
        open={pdfViewerOpen}
        onClose={handleClosePdfViewer}
        pdfUrl={currentPdfUrl}
        fileName={currentPdfTitle}
        title={currentPdfTitle}
      />

      {/* ✅ Snackbar pour notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default InvoiceGenerator;
