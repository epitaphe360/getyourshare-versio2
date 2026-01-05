/**
 * Dashboard Fiscal Commercial - Employé (CDI/CDD)
 * Commissions, charges sociales, bulletins de paie
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Tag, Button, Space,
  Timeline, Descriptions, Divider, Alert
} from 'antd';
import {
  DollarOutlined,
  UserOutlined,
  FileTextOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import axios from 'axios';
import dayjs from 'dayjs';

const FiscalDashboardCommercial = () => {
  const [loading, setLoading] = useState(false);
  const [country, setCountry] = useState('MA');
  const [fiscalData, setFiscalData] = useState(null);
  const [contractType, setContractType] = useState('CDI');

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
      setContractType(response.data.contract_type || 'CDI');
    } catch (error) {
      console.error('Erreur chargement profil:', error);
    }
  };

  const fetchFiscalData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/fiscal/dashboard/commercial', {
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
          socialChargesEmployer: 20.48, // Charges patronales ~20%
          socialChargesEmployee: 6.56, // Charges salariales (CNSS 4.48% + AMO 2.26%)
          incomeTax: 10, // IR moyen simplifié
          totalCharges: 26.56
        };
      case 'FR':
        return {
          currency: '€',
          socialChargesEmployer: 42, // Charges patronales
          socialChargesEmployee: 22, // Charges salariales
          incomeTax: 12, // Prélèvement à la source moyen
          totalCharges: 64
        };
      case 'US':
        return {
          currency: '$',
          socialChargesEmployer: 7.65, // FICA employer (Social Security 6.2% + Medicare 1.45%)
          socialChargesEmployee: 7.65, // FICA employee
          incomeTax: 22, // Federal tax withholding moyen
          totalCharges: 15.3
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
    contract: {
      type: contractType,
      start_date: '2023-01-15',
      position: 'Commercial Senior',
      base_salary: country === 'MA' ? 8000 : country === 'FR' ? 2500 : 4000
    },
    monthly: {
      gross_commissions: 15000,
      social_charges_employee: 15000 * (config.socialChargesEmployee / 100),
      income_tax: 15000 * (config.incomeTax / 100),
      net_paid:
        15000 -
        15000 * (config.socialChargesEmployee / 100) -
        15000 * (config.incomeTax / 100)
    },
    annual: {
      gross_ytd: 105000,
      social_charges_ytd: 105000 * (config.socialChargesEmployee / 100),
      income_tax_ytd: 105000 * (config.incomeTax / 100),
      net_ytd:
        105000 -
        105000 * (config.socialChargesEmployee / 100) -
        105000 * (config.incomeTax / 100)
    },
    monthly_evolution: [
      {
        month: 'Jan',
        gross: 12000,
        social: 12000 * (config.socialChargesEmployee / 100),
        net:
          12000 -
          12000 * (config.socialChargesEmployee / 100) -
          12000 * (config.incomeTax / 100)
      },
      {
        month: 'Fév',
        gross: 13500,
        social: 13500 * (config.socialChargesEmployee / 100),
        net:
          13500 -
          13500 * (config.socialChargesEmployee / 100) -
          13500 * (config.incomeTax / 100)
      },
      {
        month: 'Mar',
        gross: 14200,
        social: 14200 * (config.socialChargesEmployee / 100),
        net:
          14200 -
          14200 * (config.socialChargesEmployee / 100) -
          14200 * (config.incomeTax / 100)
      },
      {
        month: 'Avr',
        gross: 16500,
        social: 16500 * (config.socialChargesEmployee / 100),
        net:
          16500 -
          16500 * (config.socialChargesEmployee / 100) -
          16500 * (config.incomeTax / 100)
      },
      {
        month: 'Mai',
        gross: 17800,
        social: 17800 * (config.socialChargesEmployee / 100),
        net:
          17800 -
          17800 * (config.socialChargesEmployee / 100) -
          17800 * (config.incomeTax / 100)
      },
      {
        month: 'Juin',
        gross: 15000,
        social: 15000 * (config.socialChargesEmployee / 100),
        net:
          15000 -
          15000 * (config.socialChargesEmployee / 100) -
          15000 * (config.incomeTax / 100)
      }
    ],
    payslips: [
      {
        id: 1,
        month: 'Juin 2024',
        gross: 15000,
        social: 15000 * (config.socialChargesEmployee / 100),
        tax: 15000 * (config.incomeTax / 100),
        net:
          15000 -
          15000 * (config.socialChargesEmployee / 100) -
          15000 * (config.incomeTax / 100),
        payment_date: '2024-07-05'
      },
      {
        id: 2,
        month: 'Mai 2024',
        gross: 17800,
        social: 17800 * (config.socialChargesEmployee / 100),
        tax: 17800 * (config.incomeTax / 100),
        net:
          17800 -
          17800 * (config.socialChargesEmployee / 100) -
          17800 * (config.incomeTax / 100),
        payment_date: '2024-06-05'
      },
      {
        id: 3,
        month: 'Avril 2024',
        gross: 16500,
        social: 16500 * (config.socialChargesEmployee / 100),
        tax: 16500 * (config.incomeTax / 100),
        net:
          16500 -
          16500 * (config.socialChargesEmployee / 100) -
          16500 * (config.incomeTax / 100),
        payment_date: '2024-05-05'
      }
    ]
  };

  const data = fiscalData || mockData;

  const payslipColumns = [
    {
      title: 'Période',
      dataIndex: 'month',
      key: 'month',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Commissions brutes',
      dataIndex: 'gross',
      key: 'gross',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: 'Charges sociales',
      dataIndex: 'social',
      key: 'social',
      render: (val) => (
        <span style={{ color: '#fa8c16' }}>{formatCurrency(val)}</span>
      ),
      align: 'right'
    },
    {
      title: country === 'MA' ? 'IR' : country === 'FR' ? 'Prélèvement' : 'Tax',
      dataIndex: 'tax',
      key: 'tax',
      render: (val) => (
        <span style={{ color: '#fa8c16' }}>{formatCurrency(val)}</span>
      ),
      align: 'right'
    },
    {
      title: 'Net à payer',
      dataIndex: 'net',
      key: 'net',
      render: (val) => (
        <strong style={{ color: '#52c41a' }}>{formatCurrency(val)}</strong>
      ),
      align: 'right'
    },
    {
      title: 'Date de paiement',
      dataIndex: 'payment_date',
      key: 'payment_date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <Button type="link" size="small" icon={<DownloadOutlined />}>
          Bulletin
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1>
            <UserOutlined /> Mon Espace Fiscal Salarié
          </h1>
          <Space>
            <Tag color="blue" style={{ fontSize: 14 }}>
              {contractType}
            </Tag>
            <span style={{ fontSize: 14, color: '#666' }}>
              {country === 'MA' && '🇲🇦 Maroc'}
              {country === 'FR' && '🇫🇷 France'}
              {country === 'US' && '🇺🇸 États-Unis'}
            </span>
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<DownloadOutlined />} size="large">
            Télécharger mes bulletins
          </Button>
        </Col>
      </Row>

      {/* Informations contrat */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="📋 Informations contractuelles">
            <Descriptions bordered column={{ xs: 1, sm: 2, md: 4 }}>
              <Descriptions.Item label="Type de contrat">
                <Tag color={contractType === 'CDI' ? 'green' : 'blue'}>
                  {contractType}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Date d'embauche">
                {dayjs(data.contract.start_date).format('DD/MM/YYYY')}
              </Descriptions.Item>
              <Descriptions.Item label="Ancienneté">
                {dayjs().diff(dayjs(data.contract.start_date), 'month')} mois
              </Descriptions.Item>
              <Descriptions.Item label="Poste">
                {data.contract.position}
              </Descriptions.Item>
              <Descriptions.Item label="Salaire de base">
                {formatCurrency(data.contract.base_salary)}
              </Descriptions.Item>
              <Descriptions.Item label="Commissions mois">
                {formatCurrency(data.monthly.gross_commissions)}
              </Descriptions.Item>
              <Descriptions.Item label="Total brut mois">
                {formatCurrency(
                  data.contract.base_salary + data.monthly.gross_commissions
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Net à payer">
                <strong style={{ color: '#52c41a' }}>
                  {formatCurrency(data.monthly.net_paid)}
                </strong>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      {/* KPIs mois en cours */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Commissions brutes (mois)"
              value={data.monthly.gross_commissions}
              prefix={<DollarOutlined />}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={`Charges sociales (${config.socialChargesEmployee.toFixed(1)}%)`}
              value={data.monthly.social_charges_employee}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              {country === 'MA' && 'CNSS + AMO'}
              {country === 'FR' && 'Sécu + Retraite + Chômage'}
              {country === 'US' && 'Social Security + Medicare'}
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title={
                country === 'MA'
                  ? 'IR'
                  : country === 'FR'
                  ? 'Prélèvement à la source'
                  : 'Federal Tax'
              }
              value={data.monthly.income_tax}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
              ~{config.incomeTax}% du brut
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Net versé"
              value={data.monthly.net_paid}
              formatter={(val) => formatCurrency(val)}
              valueStyle={{ color: '#52c41a', fontWeight: 'bold' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Cumul annuel */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card title="📊 Cumul annuel (Année en cours)">
            <Row gutter={16}>
              <Col xs={24} sm={6}>
                <Statistic
                  title="Brut cumulé"
                  value={data.annual.gross_ytd}
                  formatter={(val) => formatCurrency(val)}
                  valueStyle={{ fontSize: 24 }}
                />
              </Col>
              <Col xs={24} sm={6}>
                <Statistic
                  title="Charges sociales"
                  value={data.annual.social_charges_ytd}
                  formatter={(val) => formatCurrency(val)}
                  valueStyle={{ fontSize: 24, color: '#fa8c16' }}
                />
              </Col>
              <Col xs={24} sm={6}>
                <Statistic
                  title={country === 'FR' ? 'Impôt prélevé' : 'Impôt retenu'}
                  value={data.annual.income_tax_ytd}
                  formatter={(val) => formatCurrency(val)}
                  valueStyle={{ fontSize: 24, color: '#fa8c16' }}
                />
              </Col>
              <Col xs={24} sm={6}>
                <Statistic
                  title="Net cumulé"
                  value={data.annual.net_ytd}
                  formatter={(val) => formatCurrency(val)}
                  valueStyle={{ fontSize: 24, color: '#52c41a', fontWeight: 'bold' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={14}>
          <Card title="Évolution mensuelle (6 derniers mois)">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.monthly_evolution}>
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

        <Col xs={24} lg={10}>
          <Card title="Comparaison Brut vs Net (Juin)">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  {
                    category: 'Brut',
                    amount: data.monthly.gross_commissions
                  },
                  {
                    category: 'Charges sociales',
                    amount: -data.monthly.social_charges_employee
                  },
                  {
                    category: 'Impôt',
                    amount: -data.monthly.income_tax
                  },
                  {
                    category: 'Net',
                    amount: data.monthly.net_paid
                  }
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <RechartsTooltip formatter={(val) => formatCurrency(val)} />
                <Bar
                  dataKey="amount"
                  fill={(entry) => {
                    if (entry.category === 'Brut') return '#1890ff';
                    if (entry.category === 'Net') return '#52c41a';
                    return '#fa8c16';
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Historique bulletins */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24}>
          <Card
            title="Historique des bulletins de paie"
            extra={
              <Button icon={<DownloadOutlined />}>
                Télécharger tous (ZIP)
              </Button>
            }
          >
            <Table
              dataSource={data.payslips}
              columns={payslipColumns}
              rowKey="id"
              pagination={{ pageSize: 12 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Documents et informations */}
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card title="Mes documents">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Button block icon={<DownloadOutlined />} size="large">
                Tous mes bulletins de paie
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Attestation fiscale annuelle
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Attestation employeur
              </Button>
              <Button block icon={<DownloadOutlined />} size="large">
                Contrat de travail
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={12}>
          <Card title="Informations fiscales">
            <Alert
              message="Statut salarié - Charges automatiques"
              description={
                <div>
                  <p>
                    En tant que salarié, vos charges sociales et votre impôt sur le
                    revenu sont automatiquement prélevés sur votre salaire brut.
                  </p>
                  <Divider />
                  <h4>Décomposition des charges:</h4>
                  {country === 'MA' && (
                    <ul style={{ paddingLeft: 20 }}>
                      <li>
                        <strong>CNSS:</strong> 4.48% (Caisse Nationale de Sécurité
                        Sociale)
                      </li>
                      <li>
                        <strong>AMO:</strong> 2.26% (Assurance Maladie
                        Obligatoire)
                      </li>
                      <li>
                        <strong>IR:</strong> Barème progressif selon revenus
                      </li>
                    </ul>
                  )}
                  {country === 'FR' && (
                    <ul style={{ paddingLeft: 20 }}>
                      <li>
                        <strong>Sécurité sociale:</strong> ~15%
                      </li>
                      <li>
                        <strong>Retraite:</strong> ~11%
                      </li>
                      <li>
                        <strong>Chômage:</strong> ~2.4%
                      </li>
                      <li>
                        <strong>CSG/CRDS:</strong> ~9.7%
                      </li>
                      <li>
                        <strong>Prélèvement IR:</strong> Selon taux personnalisé
                      </li>
                    </ul>
                  )}
                  {country === 'US' && (
                    <ul style={{ paddingLeft: 20 }}>
                      <li>
                        <strong>Social Security:</strong> 6.2%
                      </li>
                      <li>
                        <strong>Medicare:</strong> 1.45%
                      </li>
                      <li>
                        <strong>Federal Tax:</strong> Selon bracket
                      </li>
                      <li>
                        <strong>State Tax:</strong> Selon État
                      </li>
                    </ul>
                  )}
                </div>
              }
              type="info"
              icon={<InfoCircleOutlined />}
              showIcon
            />

            <Divider />

            <Timeline style={{ marginTop: 16 }}>
              <Timeline.Item color="green" dot={<CheckCircleOutlined />}>
                Pas de déclaration fiscale à faire
              </Timeline.Item>
              <Timeline.Item color="green" dot={<CheckCircleOutlined />}>
                Charges sociales automatiques
              </Timeline.Item>
              <Timeline.Item color="green" dot={<CheckCircleOutlined />}>
                {country === 'FR'
                  ? 'Prélèvement à la source actif'
                  : 'Impôt prélevé automatiquement'}
              </Timeline.Item>
            </Timeline>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default FiscalDashboardCommercial;
