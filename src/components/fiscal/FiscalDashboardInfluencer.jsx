/**
 * Dashboard Fiscal Influenceur - Focus Auto-entrepreneur
 * Suivi plafonds, retenue à la source, déclarations trimestrielles
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Progress, Alert, Button, Space,
  Tag, Table, Tooltip, Badge, Steps, Divider
} from 'antd';
import {
  DollarOutlined,
  TrophyOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
  DownloadOutlined,
  PercentageOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import axios from 'axios';
import dayjs from 'dayjs';

const FiscalDashboardInfluencer = () => {
  const [loading, setLoading] = useState(false);
  const [country, setCountry] = useState('MA');
  const [fiscalData, setFiscalData] = useState(null);
  const [taxStatus, setTaxStatus] = useState('auto_entrepreneur');

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (country) {
      fetchFiscalData();
    }
  }, [country]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'MA');
      setTaxStatus(response.data.tax_status || 'auto_entrepreneur');
    } catch (error) {
      console.error('Erreur chargement profil:', error);
    }
  };

  const fetchFiscalData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/fiscal/dashboard/influencer', {
        params: { country }
      });
      setFiscalData(response.data);
    } catch (error) {
      console.error('Erreur chargement données fiscales:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfig = () => {
    switch (country) {
      case 'MA':
        return {
          currency: 'DH',
          annualCap: 500000, // 500K MAD
          withholdingRate: 10,
          taxRate: 2, // IR auto-entrepreneur services 2%
          declarationPeriod: 'Trimestrielle',
          regime: 'Auto-entrepreneur'
        };
      case 'FR':
        return {
          currency: '€',
          annualCap: 77700, // Plafond BNC 2024
          withholdingRate: 0, // Pas de retenue
          socialChargesRate: 22, // Cotisations URSSAF BNC
          taxRate: 2.2, // Versement libératoire BNC
          declarationPeriod: 'Mensuelle ou Trimestrielle',
          regime: 'Micro-entreprise (BNC)'
        };
      case 'US':
        return {
          currency: '$',
          annualCap: null, // Pas de plafond
          withholdingRate: 24, // Backup withholding si pas W-9
          selfEmploymentTax: 15.3,
          declarationPeriod: 'Quarterly',
          regime: 'Sole Proprietor / 1099 Contractor'
        };
      default:
        return {};
    }
  };

  const config = getConfig();

  const formatCurrency = (value) => {
    if (!value) return `0 ${config.currency}`;
    return `${parseFloat(value).toLocaleString('fr-FR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })} ${config.currency}`;
  };

  // Mock data
  const mockData = {
    kpis: {
      gross_this_month: 12500,
      withholding_tax: country === 'MA' ? 1250 : country === 'US' ? 3000 : 0,
      social_charges: country === 'FR' ? 2750 : country === 'US' ? 1912 : 0,
      net_paid: country === 'MA' ? 11250 : country === 'FR' ? 9750 : country === 'US' ? 7588 : 0
    },
    annual: {
      total_revenue: 98500,
      cap: config.annualCap,
      percentage: config.annualCap ? (98500 / config.annualCap) * 100 : null
    },
    monthly_commissions: [
      { month: 'Jan', gross: 8500, net: country === 'MA' ? 7650 : 6800 },
      { month: 'Fév', gross: 9200, net: country === 'MA' ? 8280 : 7344 },
      { month: 'Mar', gross: 10500, net: country === 'MA' ? 9450 : 8400 },
      { month: 'Avr', gross: 11200, net: country === 'MA' ? 10080 : 9056 },
      { month: 'Mai', gross: 12800, net: country === 'MA' ? 11520 : 10240 },
      { month: 'Juin', gross: 12500, net: country === 'MA' ? 11250 : 10000 }
    ],
    payments: [
      {
        id: 1,
        date: '2024-06-05',
        gross: 12500,
        withholding: country === 'MA' ? 1250 : country === 'US' ? 3000 : 0,
        social: country === 'FR' ? 2750 : country === 'US' ? 1912 : 0,
        net: country === 'MA' ? 11250 : country === 'FR' ? 9750 : 7588,
        sales_count: 45
      },
      {
        id: 2,
        date: '2024-05-05',
        gross: 12800,
        withholding: country === 'MA' ? 1280 : country === 'US' ? 3072 : 0,
        social: country === 'FR' ? 2816 : country === 'US' ? 1958 : 0,
        net: country === 'MA' ? 11520 : country === 'FR' ? 9984 : 7770,
        sales_count: 48
      }
    ],
    next_declaration: {
      type: country === 'MA' ? 'Déclaration IR Trimestrielle' :
            country === 'FR' ? 'Déclaration URSSAF' :
            'Quarterly Tax Payment',
      due_date: '2024-06-30',
      status: 'pending'
    }
  };

  const data = fiscalData || mockData;

  const paymentColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Commissions brutes',
      dataIndex: 'gross',
      key: 'gross',
      render: (val) => <strong>{formatCurrency(val)}</strong>,
      align: 'right'
    },
    ...(country === 'MA' || country === 'US' ? [{
      title: country === 'MA' ? 'Retenue (10%)' : 'Withholding (24%)',
      dataIndex: 'withholding',
      key: 'withholding',
      render: (val) => (
        <span style={{ color: '#fa8c16' }}>{formatCurrency(val)}</span>
      ),
      align: 'right'
    }] : []),
    ...(country === 'FR' || country === 'US' ? [{
      title: country === 'FR' ? 'Cotisations (22%)' : 'Self-Emp Tax (15.3%)',
      dataIndex: 'social',
      key: 'social',
      render: (val) => (
        <span style={{ color: '#fa8c16' }}>{formatCurrency(val)}</span>
      ),
      align: 'right'
    }] : []),
    {
      title: 'Net versé',
      dataIndex: 'net',
      key: 'net',
      render: (val) => (
        <strong style={{ color: '#52c41a' }}>{formatCurrency(val)}</strong>
      ),
      align: 'right'
    },
    {
      title: 'Ventes',
      dataIndex: 'sales_count',
      key: 'sales_count',
      align: 'center'
    }
  ];

  const getProgressStatus = () => {
    if (!data.annual.percentage) return 'normal';
    if (data.annual.percentage < 50) return 'normal';
    if (data.annual.percentage < 80) return 'normal';
    if (data.annual.percentage < 95) return 'exception';
    return 'exception';
  };

  const getProgressColor = () => {
    if (!data.annual.percentage) return '#1890ff';
    if (data.annual.percentage < 50) return '#52c41a';
    if (data.annual.percentage < 80) return '#1890ff';
    if (data.annual.percentage < 95) return '#fa8c16';
    return '#f5222d';
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1><TrophyOutlined /> Mon Espace Fiscal Influenceur</h1>
          <Space>
            <Badge
              status="processing"
              text={
                <span style={{ fontSize: 16 }}>
                  {country === 'MA' && '🇲🇦 Maroc - Auto-entrepreneur'}
                  {country === 'FR' && '🇫🇷 France - Micro-entreprise BNC'}
                  {country === 'US' && '🇺🇸 USA - 1099 Contractor'}
                </span>
              }
            />
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<DownloadOutlined />} size="large">
            Télécharger mes documents
          </Button>
        </Col>
      </Row>

      {/* Alerte prochaine déclaration */}
      {data.next_declaration.status === 'pending' && (
        <Alert
          message={`${data.next_declaration.type} à effectuer`}
          description={`Échéance: ${dayjs(data.next_declaration.due_date).format('DD/MM/YYYY')} (${dayjs(data.next_declaration.due_date).diff(dayjs(), 'day')} jours restants)`}
          type="warning"
          icon={<WarningOutlined />}
          showIcon
          closable
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" type="primary">
              Préparer maintenant
            </Button>
          }
        />
      )}

      {/* KPIs mois en cours */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Commissions brutes (mois)"
              value={data.kpis.gross_this_month}
              prefix={<DollarOutlined />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        {(country === 'MA' || country === 'US') && (
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title={
                  country === 'MA'
                    ? 'Retenue à la source (10%)'
                    : 'Backup Withholding (24%)'
                }
                value={data.kpis.withholding_tax}
                prefix={<PercentageOutlined />}
                formatter={(val) => formatCurrency(val)}
                valueStyle={{ color: '#fa8c16' }}
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                {country === 'MA' && 'Retenue par le marchand'}
                {country === 'US' && 'Si pas de formulaire W-9'}
              </div>
            </Card>
          </Col>
        )}

        {(country === 'FR' || country === 'US') && (
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title={
                  country === 'FR'
                    ? 'Cotisations sociales (22%)'
                    : 'Self-Employment Tax (15.3%)'
                }
                value={data.kpis.social_charges}
                formatter={(val) => formatCurrency(val)}
                valueStyle={{ color: '#fa8c16' }}
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                {country === 'FR' && 'URSSAF (retraite, santé, etc.)'}
                {country === 'US' && 'Social Security + Medicare'}
              </div>
            </Card>
          </Col>
        )}

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Net versé"
              value={data.kpis.net_paid}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              {country === 'MA' && 'Après retenue'}
              {country === 'FR' && 'Après cotisations'}
              {country === 'US' && 'Après taxes'}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Plafond annuel (Maroc & France) */}
      {config.annualCap && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col xs={24}>
            <Card>
              <Row gutter={16}>
                <Col xs={24} md={16}>
                  <h3>
                    <InfoCircleOutlined /> Suivi du plafond annuel {config.regime}
                  </h3>
                  <Progress
                    percent={data.annual.percentage}
                    status={getProgressStatus()}
                    strokeColor={getProgressColor()}
                    strokeWidth={20}
                    format={(percent) => `${percent.toFixed(1)}%`}
                  />
                  <Row gutter={16} style={{ marginTop: 16 }}>
                    <Col span={8}>
                      <Statistic
                        title="Chiffre d'affaires annuel"
                        value={data.annual.total_revenue}
                        formatter={(val) => formatCurrency(val)}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Plafond autorisé"
                        value={config.annualCap}
                        formatter={(val) => formatCurrency(val)}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="Marge disponible"
                        value={config.annualCap - data.annual.total_revenue}
                        formatter={(val) => formatCurrency(val)}
                        valueStyle={{
                          color:
                            data.annual.percentage > 90 ? '#f5222d' : '#52c41a'
                        }}
                      />
                    </Col>
                  </Row>
                </Col>

                <Col xs={24} md={8}>
                  <Alert
                    message={
                      data.annual.percentage < 50
                        ? '✅ Tout va bien'
                        : data.annual.percentage < 80
                        ? '⚠️ Surveillez votre CA'
                        : data.annual.percentage < 95
                        ? '🚨 Attention au dépassement'
                        : '🛑 Plafond presque atteint'
                    }
                    description={
                      <div>
                        {data.annual.percentage < 50 && (
                          <p>
                            Vous êtes à {data.annual.percentage.toFixed(1)}% du
                            plafond. Continuez ainsi !
                          </p>
                        )}
                        {data.annual.percentage >= 50 &&
                          data.annual.percentage < 80 && (
                            <p>
                              Vous approchez de 80% du plafond. Surveillez votre
                              activité.
                            </p>
                          )}
                        {data.annual.percentage >= 80 &&
                          data.annual.percentage < 95 && (
                            <p>
                              ⚠️ Vous êtes proche du plafond. Envisagez un
                              changement de statut (société).
                            </p>
                          )}
                        {data.annual.percentage >= 95 && (
                          <p>
                            🛑 <strong>Urgent:</strong> Vous allez dépasser le
                            plafond. Contactez un comptable immédiatement.
                          </p>
                        )}
                      </div>
                    }
                    type={
                      data.annual.percentage < 50
                        ? 'success'
                        : data.annual.percentage < 80
                        ? 'info'
                        : data.annual.percentage < 95
                        ? 'warning'
                        : 'error'
                    }
                    showIcon
                  />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}

      {/* Graphiques */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={16}>
          <Card title="Évolution des commissions (6 derniers mois)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.monthly_commissions}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="gross"
                  stroke="#1890ff"
                  strokeWidth={2}
                  name="Brut"
                />
                <Line
                  type="monotone"
                  dataKey="net"
                  stroke="#52c41a"
                  strokeWidth={3}
                  name="Net"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card title="Décomposition fiscale (mois)">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  {
                    name: 'Juin',
                    Brut: data.kpis.gross_this_month,
                    Retenue: data.kpis.withholding_tax || data.kpis.social_charges,
                    Net: data.kpis.net_paid
                  }
                ]}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
                <Legend />
                <Bar dataKey="Brut" fill="#1890ff" />
                <Bar dataKey="Retenue" fill="#fa8c16" />
                <Bar dataKey="Net" fill="#52c41a" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Historique des paiements */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="Historique des versements de commissions">
            <Table
              dataSource={data.payments}
              columns={paymentColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Documents et ressources */}
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card title="Mes documents fiscaux">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Button block icon={<DownloadOutlined />} size="large">
                Certificat de revenus annuel
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Mes factures auto-générées
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                {country === 'FR'
                  ? 'Livre des recettes'
                  : 'Livre des commissions'}
              </Button>
              {country === 'MA' && (
                <Button block icon={<DownloadOutlined />} size="large">
                  Attestation retenue à la source
                </Button>
              )}
              {country === 'US' && (
                <Button block icon={<DownloadOutlined />} size="large">
                  Form 1099-NEC
                </Button>
              )}
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="Guide fiscal">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {country === 'MA' && (
                <div>
                  <h4>🇲🇦 Auto-entrepreneur Maroc</h4>
                  <ul style={{ paddingLeft: 20 }}>
                    <li>
                      <strong>Plafond:</strong> 500 000 DH/an
                    </li>
                    <li>
                      <strong>IR:</strong> 2% pour services
                    </li>
                    <li>
                      <strong>Retenue:</strong> 10% (déduite automatiquement)
                    </li>
                    <li>
                      <strong>Déclaration:</strong> Trimestrielle
                    </li>
                  </ul>
                </div>
              )}

              {country === 'FR' && (
                <div>
                  <h4>🇫🇷 Micro-entreprise France (BNC)</h4>
                  <ul style={{ paddingLeft: 20 }}>
                    <li>
                      <strong>Plafond:</strong> 77 700 € (2024)
                    </li>
                    <li>
                      <strong>Cotisations sociales:</strong> 22%
                    </li>
                    <li>
                      <strong>Versement libératoire IR:</strong> 2.2% (optionnel)
                    </li>
                    <li>
                      <strong>Franchise TVA:</strong> Jusqu'à 36 800 €
                    </li>
                    <li>
                      <strong>Déclaration:</strong> Mensuelle ou trimestrielle
                    </li>
                  </ul>
                </div>
              )}

              {country === 'US' && (
                <div>
                  <h4>🇺🇸 Independent Contractor (1099)</h4>
                  <ul style={{ paddingLeft: 20 }}>
                    <li>
                      <strong>Self-Employment Tax:</strong> 15.3%
                    </li>
                    <li>
                      <strong>Backup Withholding:</strong> 24% (si pas de W-9)
                    </li>
                    <li>
                      <strong>Form 1099-NEC:</strong> Si revenu > $600
                    </li>
                    <li>
                      <strong>Quarterly Taxes:</strong> À payer chaque trimestre
                    </li>
                  </ul>
                </div>
              )}

              <Button type="link" style={{ padding: 0 }}>
                Voir la documentation complète →
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FiscalDashboardInfluencer;
