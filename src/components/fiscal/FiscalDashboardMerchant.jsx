/**
 * Dashboard Fiscal Marchand - Vue personnalisée selon le pays
 * Obligations TVA, factures, exports comptables
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Alert, Button, Space,
  Tag, Progress, Select, DatePicker, Tabs, Divider, Tooltip
} from 'antd';
import {
  DollarOutlined,
  WarningOutlined,
  FileTextOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import axios from 'axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const COLORS = ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1'];

const FiscalDashboardMerchant = () => {
  const [loading, setLoading] = useState(false);
  const [country, setCountry] = useState('MA'); // Depuis profil utilisateur
  const [fiscalData, setFiscalData] = useState(null);
  const [period, setPeriod] = useState([
    dayjs().startOf('month'),
    dayjs().endOf('month')
  ]);

  useEffect(() => {
    // Récupérer le pays depuis le profil utilisateur
    fetchUserCountry();
  }, []);

  useEffect(() => {
    if (country) {
      fetchFiscalData();
    }
  }, [country, period]);

  const fetchUserCountry = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'MA');
    } catch (error) {
      console.error('Erreur chargement profil:', error);
    }
  };

  const fetchFiscalData = async () => {
    try {
      setLoading(true);
      const [start, end] = period;
      const response = await axios.get('/api/fiscal/dashboard/merchant', {
        params: {
          country,
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD')
        }
      });
      setFiscalData(response.data);
    } catch (error) {
      console.error('Erreur chargement données fiscales:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrencyInfo = () => {
    switch (country) {
      case 'MA': return { symbol: 'DH', name: 'Dirham marocain' };
      case 'FR': return { symbol: '€', name: 'Euro' };
      case 'US': return { symbol: '$', name: 'Dollar américain' };
      default: return { symbol: '', name: '' };
    }
  };

  const formatCurrency = (value) => {
    const { symbol } = getCurrencyInfo();
    if (!value) return `0 ${symbol}`;
    return `${parseFloat(value).toLocaleString('fr-FR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })} ${symbol}`;
  };

  // Mock data
  const mockData = {
    kpis: {
      sales_ht: 125000,
      vat_collected: 25000,
      commissions_paid: 12500,
      net_revenue: 112500
    },
    alerts: [
      {
        type: 'warning',
        message: country === 'MA' 
          ? 'Déclaration TVA mensuelle à soumettre avant le 20/07/2024'
          : country === 'FR'
          ? 'Déclaration CA3 à soumettre avant le 24/07/2024'
          : 'Quarterly tax payment due July 15, 2024',
        days_left: 18
      }
    ],
    missing_invoices: [],
    monthly_sales: [
      { month: 'Jan', sales: 98000 },
      { month: 'Fév', sales: 105000 },
      { month: 'Mar', sales: 112000 },
      { month: 'Avr', sales: 108000 },
      { month: 'Mai', sales: 118000 },
      { month: 'Juin', sales: 125000 }
    ],
    commission_breakdown: [
      { name: 'Influenceurs', value: 8500, percent: 68 },
      { name: 'Commerciaux', value: 2800, percent: 22.4 },
      { name: 'Affiliation directe', value: 1200, percent: 9.6 }
    ],
    invoices: [
      {
        id: 1,
        invoice_number: 'FA-2024-00156',
        amount_ht: 8500,
        vat: 1700,
        amount_ttc: 10200,
        status: 'paid',
        payment_date: '2024-06-20',
        client: 'Client ABC'
      },
      {
        id: 2,
        invoice_number: 'FA-2024-00157',
        amount_ht: 12000,
        vat: 2400,
        amount_ttc: 14400,
        status: 'pending',
        due_date: '2024-07-10',
        client: 'Client XYZ'
      },
      {
        id: 3,
        invoice_number: 'FA-2024-00145',
        amount_ht: 5500,
        vat: 1100,
        amount_ttc: 6600,
        status: 'overdue',
        due_date: '2024-06-15',
        client: 'Client DEF',
        overdue_days: 7
      }
    ],
    tax_obligations: {
      next_declaration: country === 'MA' ? 'TVA Mensuelle' : country === 'FR' ? 'CA3' : 'Quarterly Tax',
      due_date: '2024-07-20',
      estimated_amount: 25000
    }
  };

  const data = fiscalData || mockData;

  const invoiceColumns = [
    {
      title: 'N° Facture',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Client',
      dataIndex: 'client',
      key: 'client'
    },
    {
      title: 'Montant HT',
      dataIndex: 'amount_ht',
      key: 'amount_ht',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: country === 'US' ? 'Sales Tax' : 'TVA',
      dataIndex: 'vat',
      key: 'vat',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: 'Montant TTC',
      dataIndex: 'amount_ttc',
      key: 'amount_ttc',
      render: (val) => <strong>{formatCurrency(val)}</strong>,
      align: 'right'
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status, record) => {
        if (status === 'paid') {
          return (
            <Tag color="green" icon={<CheckCircleOutlined />}>
              Payée {record.payment_date && `le ${dayjs(record.payment_date).format('DD/MM')}`}
            </Tag>
          );
        }
        if (status === 'pending') {
          return (
            <Tag color="orange" icon={<ClockCircleOutlined />}>
              En attente (échéance: {dayjs(record.due_date).format('DD/MM')})
            </Tag>
          );
        }
        if (status === 'overdue') {
          return (
            <Tag color="red" icon={<ExclamationCircleOutlined />}>
              En retard ({record.overdue_days}j)
            </Tag>
          );
        }
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" icon={<DownloadOutlined />}>
            PDF
          </Button>
          {record.status === 'pending' && (
            <Button type="link" size="small">
              Relancer
            </Button>
          )}
        </Space>
      )
    }
  ];

  const getTaxLabel = () => {
    switch (country) {
      case 'MA': return 'TVA';
      case 'FR': return 'TVA';
      case 'US': return 'Sales Tax';
      default: return 'Tax';
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1><DollarOutlined /> Mon Tableau de Bord Fiscal</h1>
          <p style={{ color: '#666', marginBottom: 0 }}>
            {country === 'MA' && 'Maroc 🇲🇦 - Dirhams (DH)'}
            {country === 'FR' && 'France 🇫🇷 - Euros (€)'}
            {country === 'US' && 'États-Unis 🇺🇸 - Dollars ($)'}
          </p>
        </Col>
        <Col>
          <Space>
            <RangePicker
              value={period}
              onChange={setPeriod}
              format="DD/MM/YYYY"
            />
            <Button type="primary" icon={<DownloadOutlined />}>
              Exporter mes documents
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Alertes */}
      {data.alerts.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {data.alerts.map((alert, idx) => (
            <Alert
              key={idx}
              message={alert.message}
              type={alert.type}
              icon={<WarningOutlined />}
              showIcon
              closable
              style={{ marginBottom: 8 }}
              action={
                <Button size="small" type="primary">
                  Préparer maintenant
                </Button>
              }
            />
          ))}
        </div>
      )}

      {data.missing_invoices.length > 0 && (
        <Alert
          message={`${data.missing_invoices.length} transaction(s) sans facture`}
          description="Certaines ventes n'ont pas de facture associée. Créez-les pour être en conformité."
          type="error"
          icon={<ExclamationCircleOutlined />}
          showIcon
          closable
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" danger>
              Générer les factures manquantes
            </Button>
          }
        />
      )}

      {/* KPIs */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Ventes HT (période)"
              value={data.kpis.sales_ht}
              prefix={<DollarOutlined />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={`${getTaxLabel()} collectée`}
              value={data.kpis.vat_collected}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              À reverser à l'administration
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Commissions versées"
              value={data.kpis.commissions_paid}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              Influenceurs & Commerciaux
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Chiffre d'affaires net"
              value={data.kpis.net_revenue}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#722ed1', fontWeight: 'bold' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              Après commissions
            </div>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="Évolution des ventes (6 derniers mois)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.monthly_sales}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sales"
                  stroke="#52c41a"
                  strokeWidth={3}
                  name="Ventes"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card title="Répartition des commissions">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.commission_breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${percent.toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.commission_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Factures */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card
            title="Mes factures"
            extra={
              <Space>
                <Button type="primary" icon={<FileTextOutlined />}>
                  Créer une facture
                </Button>
                <Button icon={<DownloadOutlined />}>
                  Télécharger toutes (ZIP)
                </Button>
              </Space>
            }
          >
            <Table
              dataSource={data.invoices}
              columns={invoiceColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Obligations fiscales */}
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card
            title={<span><WarningOutlined /> Prochaine obligation fiscale</span>}
            headStyle={{ background: '#fff7e6' }}
          >
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <h3>{data.tax_obligations.next_declaration}</h3>
                <p style={{ fontSize: 16, marginBottom: 0 }}>
                  Échéance: <strong>{dayjs(data.tax_obligations.due_date).format('DD MMMM YYYY')}</strong>
                </p>
                <Progress
                  percent={Math.round(
                    (dayjs().diff(dayjs().startOf('month'), 'day') /
                      dayjs(data.tax_obligations.due_date).diff(dayjs().startOf('month'), 'day')) *
                      100
                  )}
                  status="active"
                  strokeColor={{
                    '0%': '#52c41a',
                    '70%': '#fa8c16',
                    '100%': '#f5222d'
                  }}
                />
              </div>

              <Divider />

              <div>
                <p style={{ color: '#666' }}>Montant estimé à payer:</p>
                <h2 style={{ color: '#f5222d', marginTop: 0 }}>
                  {formatCurrency(data.tax_obligations.estimated_amount)}
                </h2>
              </div>

              <Button type="primary" size="large" block icon={<FileTextOutlined />}>
                Préparer ma déclaration
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="Documents fiscaux" headStyle={{ background: '#f0f5ff' }}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Button block icon={<DownloadOutlined />} size="large">
                Certificat fiscal annuel
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Toutes mes factures (ZIP)
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Export comptable (FEC/CSV)
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Livre des recettes
              </Button>

              <Divider />

              <Card size="small" style={{ background: '#fafafa' }}>
                <h4>Aide & Ressources</h4>
                {country === 'MA' && (
                  <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                    <li>Guide TVA Maroc (20%, 14%, 10%, 7%)</li>
                    <li>Calcul retenue à la source (10%)</li>
                    <li>Mentions obligatoires factures</li>
                  </ul>
                )}
                {country === 'FR' && (
                  <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                    <li>Guide TVA France (20%, 10%, 5.5%, 2.1%)</li>
                    <li>Franchise en base TVA</li>
                    <li>Déclaration CA3/CA12</li>
                    <li>Cotisations URSSAF</li>
                  </ul>
                )}
                {country === 'US' && (
                  <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                    <li>State Sales Tax rates</li>
                    <li>Self-employment tax (15.3%)</li>
                    <li>Quarterly tax payments</li>
                    <li>Form 1099-NEC requirements</li>
                  </ul>
                )}
                <Button type="link" style={{ padding: 0, marginTop: 8 }}>
                  Voir toute la documentation →
                </Button>
              </Card>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FiscalDashboardMerchant;
