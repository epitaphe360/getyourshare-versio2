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
  LinearProgress,
  Tabs,
  Tab,
  Avatar,
} from '@mui/material';
import {
  FileText,
  Download,
  Eye,
  Search,
  Filter,
  Calendar,
  Building2,
  User,
  DollarSign,
  Euro,
  Receipt,
  Archive,
  TrendingUp,
  Globe,
  CheckCircle,
  Clock,
  AlertCircle,
  X,
  Users,
  PieChart,
  BarChart3,
  FileSpreadsheet,
  FolderArchive,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003/api';

const CURRENCY_SYMBOLS = {
  MAD: 'DH',
  EUR: '€',
  USD: '$'
};

const COUNTRY_FLAGS = {
  MA: '🇲🇦',
  FR: '🇫🇷',
  US: '🇺🇸'
};

const COUNTRY_NAMES = {
  MA: 'Maroc',
  FR: 'France',
  US: 'États-Unis'
};

const InfluencerInvoicesPage = () => {
  const { user } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [exporting, setExporting] = useState(false);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterYear, setFilterYear] = useState(new Date().getFullYear());
  const [filterCountry, setFilterCountry] = useState('all');
  const [filterInfluencer, setFilterInfluencer] = useState('all');
  
  // Liste des influenceurs pour le filtre
  const [influencersList, setInfluencersList] = useState([]);

  const currentYear = new Date().getFullYear();
  const years = [currentYear, currentYear - 1, currentYear - 2, currentYear - 3];

  useEffect(() => {
    fetchInvoices();
    fetchStats();
    fetchInfluencersList();
  }, [filterYear, filterCountry, filterInfluencer]);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (user?.id) params.append('merchant_id', user.id);
      if (filterYear) params.append('year', filterYear);
      if (filterInfluencer !== 'all') params.append('influencer_id', filterInfluencer);
      
      const response = await fetch(`${API_URL}/invoices/influencers?${params}`);
      const data = await response.json();
      
      if (data.success) {
        let filtered = data.data || [];
        if (filterCountry !== 'all') {
          filtered = filtered.filter(inv => inv.influencer_country === filterCountry);
        }
        setInvoices(filtered);
      }
    } catch (error) {
      console.error('Error fetching invoices:', error);
      // Données de démo
      setInvoices([
        {
          id: '1',
          invoice_number: 'INV-2025-00001',
          influencer_name: 'Fatima El Amrani',
          influencer_country: 'MA',
          influencer_tax_id: '001234567890123',
          gross_amount: 15000,
          tax_amount: 1500,
          net_amount: 13500,
          currency: 'MAD',
          status: 'generated',
          invoice_date: '2025-01-15T10:00:00Z',
          description: 'Commission affiliation Q4 2024'
        },
        {
          id: '2',
          invoice_number: 'INV-2025-00002',
          influencer_name: 'Jean Dupont',
          influencer_country: 'FR',
          influencer_tax_id: '12345678901234',
          gross_amount: 2500,
          tax_amount: 0,
          net_amount: 2500,
          currency: 'EUR',
          status: 'generated',
          invoice_date: '2025-01-20T14:00:00Z',
          description: 'Commission affiliation Janvier 2025'
        },
        {
          id: '3',
          invoice_number: 'INV-2025-00003',
          influencer_name: 'John Smith',
          influencer_country: 'US',
          influencer_tax_id: '',
          gross_amount: 5000,
          tax_amount: 1200,
          net_amount: 3800,
          currency: 'USD',
          status: 'generated',
          invoice_date: '2025-01-25T09:00:00Z',
          description: 'Commission affiliation Janvier 2025'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const params = new URLSearchParams();
      if (user?.id) params.append('merchant_id', user.id);
      if (filterYear) params.append('year', filterYear);
      
      const response = await fetch(`${API_URL}/invoices/influencers/stats?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      // Stats de démo
      setStats({
        total_invoices: 45,
        total_gross: 125000,
        total_tax_withheld: 12500,
        total_net_paid: 112500,
        by_country: {
          MA: { count: 25, total: 75000 },
          FR: { count: 15, total: 35000 },
          US: { count: 5, total: 15000 }
        }
      });
    }
  };

  const fetchInfluencersList = async () => {
    try {
      const params = new URLSearchParams();
      if (user?.id) params.append('merchant_id', user.id);
      if (filterYear) params.append('year', filterYear);
      
      const response = await fetch(`${API_URL}/invoices/influencers/list?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setInfluencersList(data.data || []);
      }
    } catch (error) {
      console.error('Error fetching influencers:', error);
      setInfluencersList([
        { id: '1', name: 'Fatima El Amrani', country: 'MA' },
        { id: '2', name: 'Jean Dupont', country: 'FR' },
        { id: '3', name: 'John Smith', country: 'US' }
      ]);
    }
  };

  const handleDownloadPDF = async (invoiceId, invoiceNumber) => {
    try {
      const response = await fetch(`${API_URL}/invoices/influencers/${invoiceId}/pdf`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${invoiceNumber}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Erreur lors du téléchargement du PDF');
    }
  };

  const handleExportAnnual = async () => {
    try {
      setExporting(true);
      const params = new URLSearchParams();
      if (user?.id) params.append('merchant_id', user.id);
      params.append('year', filterYear);
      
      const response = await fetch(`${API_URL}/invoices/influencers/annual/export?${params}`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `factures_influenceurs_${filterYear}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting:', error);
      alert('Erreur lors de l\'export');
    } finally {
      setExporting(false);
    }
  };

  const formatCurrency = (amount, currency) => {
    return `${amount?.toLocaleString() || 0} ${CURRENCY_SYMBOLS[currency] || currency}`;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('fr-FR');
  };

  const filteredInvoices = invoices.filter(inv => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      inv.invoice_number?.toLowerCase().includes(search) ||
      inv.influencer_name?.toLowerCase().includes(search) ||
      inv.influencer_tax_id?.toLowerCase().includes(search)
    );
  });

  const renderStatsCards = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {[
        {
          title: 'Total Factures',
          value: stats?.total_invoices || 0,
          icon: FileText,
          color: '#2563eb',
          gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)'
        },
        {
          title: 'Montant Brut Total',
          value: formatCurrency(stats?.total_gross || 0, 'EUR'),
          icon: TrendingUp,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
        },
        {
          title: 'Retenues/Taxes',
          value: formatCurrency(stats?.total_tax_withheld || 0, 'EUR'),
          icon: Receipt,
          color: '#f59e0b',
          gradient: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)'
        },
        {
          title: 'Net Payé',
          value: formatCurrency(stats?.total_net_paid || 0, 'EUR'),
          icon: CheckCircle,
          color: '#8b5cf6',
          gradient: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)'
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
                  <Typography variant="h5" fontWeight={700}>
                    {stat.value}
                  </Typography>
                </Box>
                <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.2)', borderRadius: 2 }}>
                  <stat.icon size={24} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  const renderCountryBreakdown = () => (
    <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Globe size={20} />
        Répartition par Pays
      </Typography>
      <Grid container spacing={3}>
        {Object.entries(stats?.by_country || {}).map(([country, data]) => (
          <Grid item xs={12} md={4} key={country}>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                borderRadius: 2,
                borderLeft: `4px solid ${country === 'MA' ? '#ef4444' : country === 'FR' ? '#3b82f6' : '#10b981'}`
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Typography variant="h4">{COUNTRY_FLAGS[country]}</Typography>
                <Box>
                  <Typography fontWeight={600}>{COUNTRY_NAMES[country]}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {data.count} factures
                  </Typography>
                </Box>
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ color: '#2563eb' }}>
                {formatCurrency(data.total, country === 'MA' ? 'MAD' : country === 'FR' ? 'EUR' : 'USD')}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );

  const renderFilters = () => (
    <Paper sx={{ p: 2, mb: 3, borderRadius: 2 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={3}>
          <TextField
            fullWidth
            placeholder="Rechercher facture, influenceur..."
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
        <Grid item xs={6} md={2}>
          <TextField
            fullWidth
            select
            value={filterYear}
            onChange={(e) => setFilterYear(e.target.value)}
            size="small"
            label="Année"
          >
            {years.map(year => (
              <MenuItem key={year} value={year}>{year}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={6} md={2}>
          <TextField
            fullWidth
            select
            value={filterCountry}
            onChange={(e) => setFilterCountry(e.target.value)}
            size="small"
            label="Pays"
          >
            <MenuItem value="all">Tous les pays</MenuItem>
            <MenuItem value="MA">🇲🇦 Maroc</MenuItem>
            <MenuItem value="FR">🇫🇷 France</MenuItem>
            <MenuItem value="US">🇺🇸 États-Unis</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={12} md={3}>
          <TextField
            fullWidth
            select
            value={filterInfluencer}
            onChange={(e) => setFilterInfluencer(e.target.value)}
            size="small"
            label="Influenceur"
          >
            <MenuItem value="all">Tous les influenceurs</MenuItem>
            {influencersList.map(inf => (
              <MenuItem key={inf.id} value={inf.id}>
                {COUNTRY_FLAGS[inf.country]} {inf.name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} md={2}>
          <Button
            fullWidth
            variant="contained"
            startIcon={exporting ? <CircularProgress size={18} color="inherit" /> : <FolderArchive size={18} />}
            onClick={handleExportAnnual}
            disabled={exporting}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
              '&:hover': { background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)' }
            }}
          >
            {exporting ? 'Export...' : `Export ${filterYear}`}
          </Button>
        </Grid>
      </Grid>
    </Paper>
  );

  const renderInvoicesTable = () => (
    <Paper sx={{ borderRadius: 3, overflow: 'hidden' }}>
      <TableContainer>
        <Table>
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell><strong>N° Facture</strong></TableCell>
              <TableCell><strong>Influenceur</strong></TableCell>
              <TableCell><strong>Pays</strong></TableCell>
              <TableCell><strong>ID Fiscal</strong></TableCell>
              <TableCell align="right"><strong>Brut</strong></TableCell>
              <TableCell align="right"><strong>Retenue</strong></TableCell>
              <TableCell align="right"><strong>Net</strong></TableCell>
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
                  <Box sx={{ textAlign: 'center' }}>
                    <FileText size={48} color="#9ca3af" style={{ marginBottom: 16 }} />
                    <Typography color="text.secondary">
                      Aucune facture trouvée pour {filterYear}
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              filteredInvoices.map((invoice) => (
                <TableRow
                  key={invoice.id}
                  sx={{
                    '&:hover': { bgcolor: '#f8fafc' },
                    transition: 'background 0.2s'
                  }}
                >
                  <TableCell>
                    <Typography fontWeight={600} sx={{ color: '#2563eb' }}>
                      {invoice.invoice_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: '#e0e7ff', color: '#4f46e5', fontSize: 14 }}>
                        {invoice.influencer_name?.charAt(0) || 'I'}
                      </Avatar>
                      <Typography fontWeight={500}>{invoice.influencer_name}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={`${COUNTRY_FLAGS[invoice.influencer_country]} ${COUNTRY_NAMES[invoice.influencer_country] || invoice.influencer_country}`}
                      size="small"
                      sx={{ bgcolor: '#f1f5f9' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {invoice.influencer_tax_id || 
                        <Chip label="Non renseigné" size="small" color="warning" variant="outlined" />
                      }
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography fontWeight={500}>
                      {formatCurrency(invoice.gross_amount, invoice.currency)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {invoice.tax_amount > 0 ? (
                      <Typography color="error.main" fontWeight={500}>
                        -{formatCurrency(invoice.tax_amount, invoice.currency)}
                      </Typography>
                    ) : (
                      <Typography color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Typography fontWeight={700} sx={{ color: '#10b981' }}>
                      {formatCurrency(invoice.net_amount, invoice.currency)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(invoice.invoice_date)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                      <Tooltip title="Voir détails">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedInvoice(invoice);
                            setShowDetailDialog(true);
                          }}
                        >
                          <Eye size={18} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Télécharger PDF">
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadPDF(invoice.id, invoice.invoice_number)}
                        >
                          <Download size={18} />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} sx={{
          background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Factures Influenceurs
        </Typography>
        <Typography color="text.secondary">
          Gérez et téléchargez les factures de paiement pour votre déclaration fiscale
        </Typography>
      </Box>

      {/* Info Alert */}
      <Alert 
        severity="info" 
        sx={{ mb: 3, borderRadius: 2 }}
        icon={<Receipt size={20} />}
      >
        <Typography variant="body2">
          <strong>Pour vos impôts :</strong> Exportez toutes les factures d'une année fiscale en un clic. 
          Le ZIP contient tous les PDFs + un fichier CSV récapitulatif pour votre comptable.
        </Typography>
      </Alert>

      {/* Stats Cards */}
      {renderStatsCards()}

      {/* Country Breakdown */}
      {stats?.by_country && Object.keys(stats.by_country).length > 0 && renderCountryBreakdown()}

      {/* Filters */}
      {renderFilters()}

      {/* Invoices Table */}
      {renderInvoicesTable()}

      {/* Detail Dialog */}
      <Dialog
        open={showDetailDialog}
        onClose={() => setShowDetailDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { borderRadius: 3 } }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid #e2e8f0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  {selectedInvoice?.invoice_number}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatDate(selectedInvoice?.invoice_date)}
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={() => setShowDetailDialog(false)}>
              <X size={20} />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          {selectedInvoice && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  INFLUENCEUR (Prestataire)
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                  <Typography fontWeight={600}>{selectedInvoice.influencer_name}</Typography>
                  <Typography variant="body2">
                    {COUNTRY_FLAGS[selectedInvoice.influencer_country]} {COUNTRY_NAMES[selectedInvoice.influencer_country]}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    ID Fiscal: <strong>{selectedInvoice.influencer_tax_id || 'Non renseigné'}</strong>
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  MONTANTS
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Brut:</Typography>
                    <Typography fontWeight={500}>
                      {formatCurrency(selectedInvoice.gross_amount, selectedInvoice.currency)}
                    </Typography>
                  </Box>
                  {selectedInvoice.tax_amount > 0 && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography color="error.main">Retenue:</Typography>
                      <Typography color="error.main" fontWeight={500}>
                        -{formatCurrency(selectedInvoice.tax_amount, selectedInvoice.currency)}
                      </Typography>
                    </Box>
                  )}
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography fontWeight={600}>Net payé:</Typography>
                    <Typography fontWeight={700} sx={{ color: '#10b981', fontSize: '1.1rem' }}>
                      {formatCurrency(selectedInvoice.net_amount, selectedInvoice.currency)}
                    </Typography>
                  </Box>
                </Paper>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  DESCRIPTION
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: '#f8fafc' }}>
                  <Typography>{selectedInvoice.description || 'Commission d\'affiliation'}</Typography>
                </Paper>
              </Grid>

              {/* Info fiscale par pays */}
              <Grid item xs={12}>
                <Alert 
                  severity={selectedInvoice.influencer_country === 'MA' ? 'warning' : 'info'}
                  sx={{ borderRadius: 2 }}
                >
                  {selectedInvoice.influencer_country === 'MA' && (
                    <Typography variant="body2">
                      <strong>Maroc:</strong> Retenue à la source de 10% appliquée conformément à l'article 15 du CGI.
                      Cette retenue doit être déclarée et reversée à la DGI.
                    </Typography>
                  )}
                  {selectedInvoice.influencer_country === 'FR' && (
                    <Typography variant="body2">
                      <strong>France:</strong> Pas de retenue à la source. L'influenceur déclare ses revenus 
                      et paie ses cotisations URSSAF (22% micro-entreprise).
                    </Typography>
                  )}
                  {selectedInvoice.influencer_country === 'US' && (
                    <Typography variant="body2">
                      <strong>USA:</strong> {selectedInvoice.tax_amount > 0 
                        ? "Backup withholding de 24% appliqué (pas de W-9 fourni)." 
                        : "Formulaire W-9 reçu. Déclaration 1099-NEC requise si &gt; $600/an."
                      }
                    </Typography>
                  )}
                </Alert>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid #e2e8f0' }}>
          <Button onClick={() => setShowDetailDialog(false)}>
            Fermer
          </Button>
          <Button
            variant="contained"
            startIcon={<Download size={18} />}
            onClick={() => {
              handleDownloadPDF(selectedInvoice?.id, selectedInvoice?.invoice_number);
              setShowDetailDialog(false);
            }}
          >
            Télécharger PDF
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InfluencerInvoicesPage;
