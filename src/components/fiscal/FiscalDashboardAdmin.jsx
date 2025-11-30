/**
 * Dashboard Fiscal Admin - Vue d'ensemble globale multi-pays
 * Maroc (MAD), France (EUR), USA (USD)
 */

import React, { useState, useEffect } from 'react';
import { 
  Card, Row, Col, Statistic, Table, DatePicker, Select, 
  Button, Tag, Space, Tooltip, Alert, Spin, Tabs, Progress
} from 'antd';
import {
  DollarOutlined,
  PercentageOutlined,
  FileTextOutlined,
  WarningOutlined,
  DownloadOutlined,
  BarChartOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  Legend, ResponsiveContainer
} from 'recharts';
import axios from 'axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const COLORS = {
  blue: '#1890ff',
  green: '#52c41a',
  orange: '#fa8c16',
  red: '#f5222d',
  purple: '#722ed1',
  cyan: '#13c2c2'
};

const COUNTRIES = [
  { code: 'MA', name: 'Maroc', currency: 'MAD', flag: '🇲🇦' },
  { code: 'FR', name: 'France', currency: 'EUR', flag: '🇫🇷' },
  { code: 'US', name: 'États-Unis', currency: 'USD', flag: '🇺🇸' }
];

const FiscalDashboardAdmin = () => {
  const [loading, setLoading] = useState(true);
  const [fiscalData, setFiscalData] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState('MA');
  const [period, setPeriod] = useState([
    dayjs().startOf('year'),
    dayjs().endOf('month')
  ]);
  const [taxRates, setTaxRates] = useState(null);

  useEffect(() => {
    fetchFiscalData();
    fetchTaxRates();
  }, [selectedCountry, period]);

  const fetchFiscalData = async () => {
    try {
      setLoading(true);
      const [start, end] = period;
      const response = await axios.get('/api/fiscal/dashboard/admin', {
        params: {
          country: selectedCountry,
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

  const fetchTaxRates = async () => {
    try {
      const response = await axios.get(`/api/fiscal/rates/${selectedCountry}`);
      setTaxRates(response.data);
    } catch (error) {
      console.error('Erreur chargement taux fiscaux:', error);
    }
  };

  const getCurrencySymbol = () => {
    const country = COUNTRIES.find(c => c.code === selectedCountry);
    switch (country?.currency) {
      case 'MAD': return 'DH';
      case 'EUR': return '€';
      case 'USD': return '$';
      default: return '';
    }
  };

  const formatCurrency = (value) => {
    const symbol = getCurrencySymbol();
    if (!value) return `0 ${symbol}`;
    return `${parseFloat(value).toLocaleString('fr-FR', { 
      minimumFractionDigits: 2,
      maximumFractionDigits: 2 
    })} ${symbol}`;
  };

  // Mock data pour démonstration
  const mockData = {
    kpis: {
      monthly_revenue_ht: 285000,
      vat_collected: 57000,
      vat_deductible: 12000,
      vat_to_pay: 45000,
      withholding_tax: 15000,
      social_charges: 28500
    },
    revenue_evolution: [
      { month: 'Jan', ht: 220000, ttc: 264000 },
      { month: 'Fév', ht: 245000, ttc: 294000 },
      { month: 'Mar', ht: 268000, ttc: 321600 },
      { month: 'Avr', ht: 255000, ttc: 306000 },
      { month: 'Mai', ht: 275000, ttc: 330000 },
      { month: 'Juin', ht: 285000, ttc: 342000 }
    ],
    vat_breakdown: [
      { name: 'TVA 20%', value: 38000, rate: 20 },
      { name: 'TVA 14%', value: 12000, rate: 14 },
      { name: 'TVA 10%', value: 5000, rate: 10 },
      { name: 'TVA 7%', value: 2000, rate: 7 }
    ],
    recent_invoices: [
      {
        id: 1,
        invoice_number: 'FA-2024-00234',
        merchant: 'TechStore Morocco',
        amount_ht: 15000,
        vat: 3000,
        amount_ttc: 18000,
        status: 'paid',
        date: '2024-06-15'
      },
      {
        id: 2,
        invoice_number: 'FA-2024-00235',
        merchant: 'Fashion Boutique',
        amount_ht: 8500,
        vat: 1700,
        amount_ttc: 10200,
        status: 'pending',
        date: '2024-06-14'
      },
      {
        id: 3,
        invoice_number: 'FA-2024-00236',
        merchant: 'Digital Services',
        amount_ht: 22000,
        vat: 4400,
        amount_ttc: 26400,
        status: 'overdue',
        date: '2024-05-28'
      }
    ],
    tax_deadlines: [
      {
        id: 1,
        type: selectedCountry === 'MA' ? 'TVA Mensuelle' : selectedCountry === 'FR' ? 'CA3' : 'Quarterly Tax',
        due_date: '2024-07-20',
        amount_estimated: 45000,
        status: 'upcoming',
        days_left: 18
      },
      {
        id: 2,
        type: selectedCountry === 'MA' ? 'IR Trimestrielle' : selectedCountry === 'FR' ? 'URSSAF' : 'Self-Employment',
        due_date: '2024-06-30',
        amount_estimated: 28500,
        status: 'urgent',
        days_left: 8
      }
    ],
    merchants_by_country: [
      { country: 'MA', count: 145, revenue: 1250000 },
      { country: 'FR', count: 89, revenue: 850000 },
      { country: 'US', count: 34, revenue: 420000 }
    ]
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
      title: 'Marchand',
      dataIndex: 'merchant',
      key: 'merchant'
    },
    {
      title: 'Montant HT',
      dataIndex: 'amount_ht',
      key: 'amount_ht',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: 'TVA',
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
      render: (status) => {
        const colors = { paid: 'green', pending: 'orange', overdue: 'red' };
        const labels = { paid: 'Payée', pending: 'En attente', overdue: 'En retard' };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      }
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    }
  ];

  const deadlineColumns = [
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Échéance',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Montant estimé',
      dataIndex: 'amount_estimated',
      key: 'amount_estimated',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: 'Jours restants',
      dataIndex: 'days_left',
      key: 'days_left',
      render: (days, record) => {
        let color = 'green';
        if (days <= 7) color = 'red';
        else if (days <= 15) color = 'orange';
        return (
          <Tag color={color} icon={days <= 7 ? <WarningOutlined /> : null}>
            {days} jours
          </Tag>
        );
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small">Préparer</Button>
          <Button type="link" size="small">Détails</Button>
        </Space>
      )
    }
  ];

  if (loading && !fiscalData) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Chargement des données fiscales..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header avec sélection pays et période */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1>
            <GlobalOutlined /> Tableau de Bord Fiscal Global
          </h1>
          <p style={{ color: '#666', marginBottom: 0 }}>
            Vue d'ensemble des obligations fiscales multi-pays
          </p>
        </Col>
        <Col>
          <Space>
            <Select
              value={selectedCountry}
              onChange={setSelectedCountry}
              style={{ width: 200 }}
              size="large"
            >
              {COUNTRIES.map(country => (
                <Option key={country.code} value={country.code}>
                  <span style={{ marginRight: 8 }}>{country.flag}</span>
                  {country.name} ({country.currency})
                </Option>
              ))}
            </Select>
            <RangePicker
              value={period}
              onChange={setPeriod}
              format="DD/MM/YYYY"
              size="large"
            />
            <Button type="primary" icon={<DownloadOutlined />} size="large">
              Exporter
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Alertes urgentes */}
      {data.tax_deadlines.some(d => d.days_left <= 7) && (
        <Alert
          message="Échéances fiscales urgentes"
          description={`${data.tax_deadlines.filter(d => d.days_left <= 7).length} échéance(s) dans moins de 7 jours`}
          type="error"
          icon={<WarningOutlined />}
          showIcon
          closable
          style={{ marginBottom: 24 }}
        />
      )}

      {/* KPIs principaux */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Chiffre d'affaires HT"
              value={data.kpis.monthly_revenue_ht}
              prefix={<DollarOutlined style={{ color: COLORS.green }} />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: COLORS.green }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              <BarChartOutlined /> +12% vs mois précédent
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={selectedCountry === 'US' ? 'Sales Tax Collectée' : 'TVA Collectée'}
              value={data.kpis.vat_collected}
              prefix={<PercentageOutlined style={{ color: COLORS.blue }} />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: COLORS.blue }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              {selectedCountry === 'MA' && 'Taux moyen: 18.5%'}
              {selectedCountry === 'FR' && 'Taux moyen: 19.2%'}
              {selectedCountry === 'US' && 'Variable par État'}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={selectedCountry === 'US' ? 'Déductions fiscales' : 'TVA Déductible'}
              value={data.kpis.vat_deductible}
              prefix={<FileTextOutlined style={{ color: COLORS.orange }} />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: COLORS.orange }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              Achats professionnels
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={selectedCountry === 'US' ? 'Impôts à payer' : 'TVA à payer'}
              value={data.kpis.vat_to_pay}
              prefix={<WarningOutlined style={{ color: COLORS.red }} />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: COLORS.red }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              Échéance: {dayjs().add(20, 'day').format('DD/MM/YYYY')}
            </div>
          </Card>
        </Col>
      </Row>

      {/* KPIs secondaires */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title={
                selectedCountry === 'MA' ? 'Retenue à la source (10%)' :
                selectedCountry === 'FR' ? 'Cotisations URSSAF' :
                'Self-Employment Tax (15.3%)'
              }
              value={data.kpis.withholding_tax}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ fontSize: 20 }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card>
            <Statistic
              title="Charges sociales"
              value={data.kpis.social_charges}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ fontSize: 20 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="Évolution du chiffre d'affaires (6 derniers mois)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.revenue_evolution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="ht" 
                  stroke={COLORS.green} 
                  strokeWidth={2}
                  name="Montant HT"
                />
                <Line 
                  type="monotone" 
                  dataKey="ttc" 
                  stroke={COLORS.blue} 
                  strokeWidth={2}
                  name="Montant TTC"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card title={selectedCountry === 'US' ? 'Répartition Sales Tax' : 'Répartition TVA par taux'}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data.vat_breakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.vat_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={Object.values(COLORS)[index]} />
                  ))}
                </Pie>
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Répartition par pays */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="Activité par pays">
            <Row gutter={16}>
              {data.merchants_by_country.map(item => {
                const country = COUNTRIES.find(c => c.code === item.country);
                return (
                  <Col xs={24} sm={8} key={item.country}>
                    <Card size="small" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 48, marginBottom: 8 }}>{country?.flag}</div>
                      <h3>{country?.name}</h3>
                      <Statistic
                        title="Marchands actifs"
                        value={item.count}
                        valueStyle={{ fontSize: 24, color: COLORS.blue }}
                      />
                      <Statistic
                        title="CA généré"
                        value={item.revenue}
                        formatter={(val) => {
                          const symbol = country?.currency === 'MAD' ? 'DH' : 
                                        country?.currency === 'EUR' ? '€' : '$';
                          return `${(val / 1000).toFixed(0)}K ${symbol}`;
                        }}
                        valueStyle={{ fontSize: 18, color: COLORS.green }}
                      />
                    </Card>
                  </Col>
                );
              })}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Tableaux */}
      <Row gutter={16}>
        <Col xs={24} lg={14}>
          <Card 
            title="Dernières factures" 
            extra={<Button type="link">Voir tout</Button>}
          >
            <Table
              dataSource={data.recent_invoices}
              columns={invoiceColumns}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card 
            title={<span><WarningOutlined /> Échéances fiscales</span>}
            extra={<Button type="primary">Préparer déclarations</Button>}
          >
            <Table
              dataSource={data.tax_deadlines}
              columns={deadlineColumns}
              rowKey="id"
              pagination={false}
              size="small"
            />
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button type="primary" block icon={<DownloadOutlined />}>
                  Générer Déclaration {selectedCountry === 'MA' ? 'TVA' : selectedCountry === 'FR' ? 'CA3' : 'Quarterly'}
                </Button>
                <Button block icon={<DownloadOutlined />}>
                  Exporter FEC
                </Button>
                <Button block>
                  Rapprochement bancaire
                </Button>
              </Space>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Référence taux fiscaux */}
      {taxRates && (
        <Row style={{ marginTop: 24 }}>
          <Col xs={24}>
            <Card title={`Taux fiscaux - ${taxRates.country}`} size="small">
              <Tabs>
                <Tabs.TabPane tab={selectedCountry === 'US' ? 'Sales Tax' : 'TVA'} key="vat">
                  <Row gutter={16}>
                    {Object.entries(taxRates.vat || {}).map(([key, value]) => (
                      <Col xs={12} sm={8} md={6} key={key}>
                        <Card size="small">
                          <Statistic
                            title={key.replace('_', ' ')}
                            value={value}
                            valueStyle={{ fontSize: 20, color: COLORS.blue }}
                          />
                        </Card>
                      </Col>
                    ))}
                  </Row>
                </Tabs.TabPane>
                
                {selectedCountry !== 'US' && (
                  <Tabs.TabPane tab="Charges sociales" key="social">
                    <Row gutter={16}>
                      {selectedCountry === 'MA' && (
                        <>
                          <Col xs={12} sm={8}>
                            <Card size="small">
                              <Statistic title="Retenue à la source" value="10%" />
                            </Card>
                          </Col>
                          <Col xs={12} sm={8}>
                            <Card size="small">
                              <Statistic title="IR Auto-entrepreneur Services" value="2%" />
                            </Card>
                          </Col>
                        </>
                      )}
                      {selectedCountry === 'FR' && (
                        <>
                          <Col xs={12} sm={8}>
                            <Card size="small">
                              <Statistic title="Cotisations BNC" value="22%" />
                            </Card>
                          </Col>
                          <Col xs={12} sm={8}>
                            <Card size="small">
                              <Statistic title="Versement libératoire BNC" value="2.2%" />
                            </Card>
                          </Col>
                        </>
                      )}
                    </Row>
                  </Tabs.TabPane>
                )}

                {selectedCountry === 'US' && (
                  <Tabs.TabPane tab="Federal Tax" key="federal">
                    <Alert
                      message="Self-Employment Tax: 15.3%"
                      description="Social Security (12.4%) + Medicare (2.9%)"
                      type="info"
                      showIcon
                    />
                  </Tabs.TabPane>
                )}
              </Tabs>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default FiscalDashboardAdmin;
