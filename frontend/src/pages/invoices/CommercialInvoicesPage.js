import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Chip,
  TextField,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Tooltip,
  Divider
} from '@mui/material';
import {
  FileText,
  Download,
  Eye,
  Calendar,
  Globe,
  DollarSign,
  TrendingUp,
  Users,
  FileArchive,
  Filter,
  RefreshCw,
  Briefcase,
  Target,
  Award
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Configuration des pays
const COUNTRIES = {
  MA: { name: 'Maroc', flag: '🇲🇦', currency: 'MAD' },
  FR: { name: 'France', flag: '🇫🇷', currency: 'EUR' },
  US: { name: 'États-Unis', flag: '🇺🇸', currency: 'USD' }
};

// Types de commission
const COMMISSION_TYPES = {
  lead: { label: 'Lead', color: 'info', icon: Target },
  subscription: { label: 'Abonnement', color: 'success', icon: DollarSign },
  bonus: { label: 'Prime', color: 'warning', icon: Award },
  commission: { label: 'Commission', color: 'default', icon: Briefcase }
};

const CommercialInvoicesPage = () => {
  
  // États
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  
  // Filtres
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedCommercial, setSelectedCommercial] = useState('');
  const [selectedType, setSelectedType] = useState('');
  
  // Dialog détails
  const [detailDialog, setDetailDialog] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  
  // Liste des commerciaux (pour le filtre)
  const [commercials, setCommercials] = useState([]);

  // Années disponibles
  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  useEffect(() => {
    fetchInvoices();
    fetchStats();
    fetchCommercials();
  }, [selectedYear, selectedCountry, selectedCommercial, selectedType]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedYear) params.append('year', selectedYear);
      if (selectedCountry) params.append('country', selectedCountry);
      if (selectedCommercial) params.append('commercial_id', selectedCommercial);
      if (selectedType) params.append('commission_type', selectedType);
      
      const response = await axios.get(
        `${API_BASE_URL}/api/invoices/commercials?${params.toString()}`
      );
      
      if (response.data.success) {
        setInvoices(response.data.data || []);
      }
      setError(null);
    } catch (err) {
      console.error('Erreur chargement factures:', err);
      setError('Impossible de charger les factures');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedYear) params.append('year', selectedYear);
      if (selectedCommercial) params.append('commercial_id', selectedCommercial);
      
      const response = await axios.get(
        `${API_BASE_URL}/api/invoices/commercials/stats?${params.toString()}`
      );
      
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('Erreur chargement stats:', err);
    }
  };

  const fetchCommercials = async () => {
    try {
      // Récupérer la liste des commerciaux depuis les factures
      const response = await axios.get(`${API_BASE_URL}/api/invoices/commercials?limit=500`);
      if (response.data.success) {
        const uniqueCommercials = [];
        const seen = new Set();
        
        response.data.data.forEach(inv => {
          if (inv.commercial_id && !seen.has(inv.commercial_id)) {
            seen.add(inv.commercial_id);
            uniqueCommercials.push({
              id: inv.commercial_id,
              name: inv.commercial_name || 'N/A'
            });
          }
        });
        
        setCommercials(uniqueCommercials);
      }
    } catch (err) {
      console.error('Erreur chargement commerciaux:', err);
    }
  };

  const handleDownloadPdf = async (invoiceId, invoiceNumber) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/invoices/commercials/${invoiceId}/pdf`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${invoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erreur téléchargement PDF:', err);
      setError('Impossible de télécharger le PDF');
    }
  };

  const handleExportYear = async () => {
    try {
      const params = new URLSearchParams();
      params.append('year', selectedYear);
      if (selectedCommercial) params.append('commercial_id', selectedCommercial);
      
      const response = await axios.get(
        `${API_BASE_URL}/api/invoices/commercials/annual/export?${params.toString()}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `factures_commerciaux_${selectedYear}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erreur export:', err);
      setError('Impossible d\'exporter les factures');
    }
  };

  const formatCurrency = (amount, currency = 'EUR') => {
    const symbols = { EUR: '€', MAD: 'DH', USD: '$' };
    return `${amount?.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} ${symbols[currency] || currency}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('fr-FR');
  };

  const getTypeConfig = (type) => {
    return COMMISSION_TYPES[type] || COMMISSION_TYPES.commission;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Briefcase size={32} color="#059669" />
            Factures Commerciaux
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Gérez les factures des commissions commerciales pour vos déclarations fiscales
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshCw size={18} />}
            onClick={() => { fetchInvoices(); fetchStats(); }}
          >
            Actualiser
          </Button>
          <Button
            variant="contained"
            startIcon={<FileArchive size={18} />}
            onClick={handleExportYear}
            sx={{ bgcolor: '#059669', '&:hover': { bgcolor: '#047857' } }}
          >
            Exporter {selectedYear}
          </Button>
        </Box>
      </Box>

      {/* Message d'erreur */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistiques */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#ecfdf5' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Factures
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#059669' }}>
                      {stats.total_invoices || 0}
                    </Typography>
                  </Box>
                  <FileText size={24} color="#059669" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#f0fdf4' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Montant Brut
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#16a34a' }}>
                      {formatCurrency(stats.total_gross || 0)}
                    </Typography>
                  </Box>
                  <DollarSign size={24} color="#16a34a" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#fef3c7' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Taxes Retenues
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#d97706' }}>
                      {formatCurrency(stats.total_tax_withheld || 0)}
                    </Typography>
                  </Box>
                  <TrendingUp size={24} color="#d97706" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: '#dbeafe' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Net Payé
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#2563eb' }}>
                      {formatCurrency(stats.total_net_paid || 0)}
                    </Typography>
                  </Box>
                  <Users size={24} color="#2563eb" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Stats par type de commission */}
      {stats?.by_type && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {Object.entries(stats.by_type).map(([type, data]) => {
            const config = getTypeConfig(type);
            const Icon = config.icon;
            return (
              <Grid item xs={6} sm={3} key={type}>
                <Card variant="outlined">
                  <CardContent sx={{ py: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Icon size={18} />
                      <Typography variant="body2" color="text.secondary">
                        {config.label}
                      </Typography>
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {data.count} ({formatCurrency(data.total)})
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Répartition par pays */}
      {stats?.by_country && Object.keys(stats.by_country).length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Globe size={16} />
            Répartition par pays
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {Object.entries(stats.by_country).map(([code, data]) => {
              const country = COUNTRIES[code] || { name: code, flag: '🌍' };
              return (
                <Chip
                  key={code}
                  label={`${country.flag} ${country.name}: ${data.count} factures (${formatCurrency(data.total)})`}
                  variant="outlined"
                />
              );
            })}
          </Box>
        </Paper>
      )}

      {/* Filtres */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Filter size={18} />
          <Typography variant="subtitle2">Filtres</Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Année"
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              InputProps={{
                startAdornment: <Calendar size={16} style={{ marginRight: 8 }} />
              }}
            >
              {years.map(year => (
                <MenuItem key={year} value={year}>{year}</MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Pays"
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
            >
              <MenuItem value="">Tous les pays</MenuItem>
              {Object.entries(COUNTRIES).map(([code, info]) => (
                <MenuItem key={code} value={code}>
                  {info.flag} {info.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Commercial"
              value={selectedCommercial}
              onChange={(e) => setSelectedCommercial(e.target.value)}
            >
              <MenuItem value="">Tous les commerciaux</MenuItem>
              {commercials.map(com => (
                <MenuItem key={com.id} value={com.id}>
                  {com.name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={3}>
            <TextField
              select
              fullWidth
              size="small"
              label="Type"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <MenuItem value="">Tous les types</MenuItem>
              {Object.entries(COMMISSION_TYPES).map(([key, config]) => (
                <MenuItem key={key} value={key}>
                  {config.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Tableau des factures */}
      <TableContainer component={Paper}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : invoices.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <FileText size={48} color="#9ca3af" />
            <Typography color="text.secondary" sx={{ mt: 1 }}>
              Aucune facture trouvée pour cette période
            </Typography>
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: '#f9fafb' }}>
                <TableCell>N° Facture</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Commercial</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Pays</TableCell>
                <TableCell align="right">Brut</TableCell>
                <TableCell align="right">Taxes</TableCell>
                <TableCell align="right">Net</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoices.map((invoice) => {
                const country = COUNTRIES[invoice.commercial_country] || { flag: '🌍', name: invoice.commercial_country };
                const typeConfig = getTypeConfig(invoice.commission_type);
                
                return (
                  <TableRow key={invoice.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500, color: '#059669' }}>
                        {invoice.invoice_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{formatDate(invoice.invoice_date)}</TableCell>
                    <TableCell>
                      <Typography variant="body2">{invoice.commercial_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {invoice.commercial_email}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={typeConfig.label}
                        size="small"
                        color={typeConfig.color}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title={country.name}>
                        <span>{country.flag}</span>
                      </Tooltip>
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(invoice.gross_amount, invoice.currency)}
                    </TableCell>
                    <TableCell align="right" sx={{ color: invoice.tax_amount > 0 ? '#dc2626' : 'inherit' }}>
                      {invoice.tax_amount > 0 ? `-${formatCurrency(invoice.tax_amount, invoice.currency)}` : '-'}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 500, color: '#059669' }}>
                      {formatCurrency(invoice.net_amount, invoice.currency)}
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="Voir détails">
                        <IconButton 
                          size="small"
                          onClick={() => { setSelectedInvoice(invoice); setDetailDialog(true); }}
                        >
                          <Eye size={18} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Télécharger PDF">
                        <IconButton 
                          size="small" 
                          color="primary"
                          onClick={() => handleDownloadPdf(invoice.id, invoice.invoice_number)}
                        >
                          <Download size={18} />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </TableContainer>

      {/* Dialog Détails Facture */}
      <Dialog 
        open={detailDialog} 
        onClose={() => setDetailDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FileText size={20} color="#059669" />
          Détails de la facture
        </DialogTitle>
        <DialogContent>
          {selectedInvoice && (
            <Box>
              <Grid container spacing={3}>
                {/* Infos générales */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">Informations générales</Typography>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">N° Facture:</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>{selectedInvoice.invoice_number}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Date:</Typography>
                      <Typography variant="body2">{formatDate(selectedInvoice.invoice_date)}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Type:</Typography>
                      <Chip 
                        label={getTypeConfig(selectedInvoice.commission_type).label}
                        size="small"
                        color={getTypeConfig(selectedInvoice.commission_type).color}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Statut:</Typography>
                      <Chip label={selectedInvoice.status} size="small" color="success" />
                    </Box>
                  </Box>
                </Grid>

                {/* Infos commercial */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">Commercial</Typography>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Typography variant="body2">{selectedInvoice.commercial_name}</Typography>
                    <Typography variant="body2" color="text.secondary">{selectedInvoice.commercial_email}</Typography>
                    <Typography variant="body2">
                      {COUNTRIES[selectedInvoice.commercial_country]?.flag} {COUNTRIES[selectedInvoice.commercial_country]?.name}
                    </Typography>
                    {selectedInvoice.commercial_tax_id && (
                      <Typography variant="body2">
                        ID Fiscal: {selectedInvoice.commercial_tax_id}
                      </Typography>
                    )}
                  </Box>
                </Grid>

                {/* Montants */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">Montants</Typography>
                  <Divider sx={{ my: 1 }} />
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">Montant Brut</Typography>
                        <Typography variant="h6">{formatCurrency(selectedInvoice.gross_amount, selectedInvoice.currency)}</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">Taxes Retenues</Typography>
                        <Typography variant="h6" color="error">
                          {selectedInvoice.tax_amount > 0 ? `-${formatCurrency(selectedInvoice.tax_amount, selectedInvoice.currency)}` : '-'}
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="text.secondary">Montant Net</Typography>
                        <Typography variant="h6" sx={{ color: '#059669', fontWeight: 600 }}>
                          {formatCurrency(selectedInvoice.net_amount, selectedInvoice.currency)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>

                {/* Détails des taxes */}
                {selectedInvoice.tax_details && selectedInvoice.tax_details.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">Détail des taxes</Typography>
                    <Divider sx={{ my: 1 }} />
                    {selectedInvoice.tax_details.map((tax, idx) => (
                      <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">
                          {tax.name} ({tax.rate}%)
                          {tax.informative && <Chip label="Informatif" size="small" sx={{ ml: 1 }} />}
                        </Typography>
                        <Typography variant="body2" sx={{ color: tax.informative ? 'text.secondary' : 'error.main' }}>
                          {formatCurrency(tax.amount, selectedInvoice.currency)}
                        </Typography>
                      </Box>
                    ))}
                  </Grid>
                )}

                {/* Description */}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body2">{selectedInvoice.description || 'Commission commerciale'}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>Fermer</Button>
          <Button
            variant="contained"
            startIcon={<Download size={18} />}
            onClick={() => handleDownloadPdf(selectedInvoice.id, selectedInvoice.invoice_number)}
            sx={{ bgcolor: '#059669', '&:hover': { bgcolor: '#047857' } }}
          >
            Télécharger PDF
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CommercialInvoicesPage;
