import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Tag, Progress, Space, Typography,
  DatePicker, Select, Spin, Tabs, Timeline, Avatar, message
} from 'antd';
import {
  DollarOutlined, TrophyOutlined, TeamOutlined, RiseOutlined,
  UserOutlined, CheckCircleOutlined, ClockCircleOutlined,
  LineChartOutlined, FunnelPlotOutlined, BarChartOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

/**
 * Dashboard Commercial - Pipeline, commissions, performances
 */
const CommercialDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30');
  const [stats, setStats] = useState({
    total_leads: 0,
    qualified_leads: 0,
    conversions: 0,
    commission_earned: 0,
    commission_pending: 0,
    conversion_rate: 0,
    avg_deal_value: 0,
    deals_this_month: 0
  });
  const [pipelineData, setPipelineData] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);
  const [commissionHistory, setCommissionHistory] = useState([]);
  const [recentDeals, setRecentDeals] = useState([]);
  const [topClients, setTopClients] = useState([]);

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Utiliser Promise.allSettled pour gérer les erreurs individuellement
      const results = await Promise.allSettled([
        api.get(`/api/commercial/stats?days=${timeRange}`),
        api.get(`/api/commercial/pipeline?days=${timeRange}`),
        api.get(`/api/commercial/performance?days=${timeRange}`),
        api.get(`/api/commercial/commissions?days=${timeRange}`),
        api.get('/api/commercial/recent-deals'),
        api.get(`/api/commercial/top-clients?days=${timeRange}`)
      ]);

      // Extraire les données de chaque résultat, avec fallback sur valeur par défaut
      const [statsRes, pipelineRes, perfRes, commissionRes, dealsRes, clientsRes] = results;

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data.stats || {});
      }
      if (pipelineRes.status === 'fulfilled') {
        setPipelineData(pipelineRes.value.data.pipeline || []);
      }
      if (perfRes.status === 'fulfilled') {
        setPerformanceData(perfRes.value.data.performance || []);
      }
      if (commissionRes.status === 'fulfilled') {
        setCommissionHistory(commissionRes.value.data.history || []);
      }
      if (dealsRes.status === 'fulfilled') {
        setRecentDeals(dealsRes.value.data.deals || []);
      }
      if (clientsRes.status === 'fulfilled') {
        setTopClients(clientsRes.value.data.clients || []);
      }

      // Vérifier s'il y a des erreurs et notifier l'utilisateur
      const failedRequests = results.filter(r => r.status === 'rejected');
      if (failedRequests.length > 0) {
        console.error('Certaines données n\'ont pas pu être chargées:', failedRequests);
        if (failedRequests.length === results.length) {
          message.error('Erreur lors du chargement des données');
        } else {
          message.warning('Certaines données sont temporairement indisponibles');
        }
      }
    } catch (error) {
      console.error('Erreur chargement données:', error);
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const dealsColumns = [
    {
      title: 'Client',
      dataIndex: 'client_name',
      key: 'client_name',
      render: (name, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <div>
            <div style={{ fontWeight: 500 }}>{name}</div>
            <Text type="secondary" style={{ fontSize: '12px' }}>{record.company}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Type',
      dataIndex: 'deal_type',
      key: 'deal_type',
      render: (type) => {
        const config = {
          subscription: { color: 'blue', text: 'Abonnement' },
          service: { color: 'green', text: 'Service' },
          product: { color: 'orange', text: 'Produit' }
        };
        const typeConfig = config[type] || config.subscription;
        return <Tag color={typeConfig.color}>{typeConfig.text}</Tag>;
      }
    },
    {
      title: 'Valeur',
      dataIndex: 'value',
      key: 'value',
      render: (value) => (
        <Text strong style={{ color: '#52c41a' }}>
          {value?.toLocaleString()} MAD
        </Text>
      )
    },
    {
      title: 'Commission',
      dataIndex: 'commission',
      key: 'commission',
      render: (commission) => (
        <Text strong style={{ color: '#1890ff' }}>
          {commission?.toLocaleString()} MAD
        </Text>
      )
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const config = {
          closed: { color: 'success', icon: <CheckCircleOutlined />, text: 'Conclu' },
          pending: { color: 'warning', icon: <ClockCircleOutlined />, text: 'En cours' }
        };
        const statusConfig = config[status] || config.pending;
        return <Tag color={statusConfig.color} icon={statusConfig.icon}>{statusConfig.text}</Tag>;
      }
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => new Date(date).toLocaleDateString('fr-FR')
    }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div style={{ padding: '24px' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <TeamOutlined /> Dashboard Commercial
          </Title>
          <Text type="secondary">
            Suivi de vos performances et commissions
          </Text>
        </div>
        <Select
          id="time-range-select"
          value={timeRange}
          onChange={setTimeRange}
          style={{ width: 180 }}
        >
          <Select.Option value="7">7 derniers jours</Select.Option>
          <Select.Option value="30">30 derniers jours</Select.Option>
          <Select.Option value="90">90 derniers jours</Select.Option>
        </Select>
      </div>

      <Spin spinning={loading}>
        {/* KPIs */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Leads Totaux"
                value={stats.total_leads}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Conversions"
                value={stats.conversions}
                prefix={<TrophyOutlined />}
                valueStyle={{ color: '#52c41a' }}
                suffix={`/ ${stats.total_leads}`}
              />
              <Progress
                percent={stats.conversion_rate}
                size="small"
                status="active"
                style={{ marginTop: '8px' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Commissions Gagnées"
                value={stats.commission_earned}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="MAD"
                valueStyle={{ color: '#52c41a' }}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                En attente: {stats.commission_pending?.toLocaleString()} MAD
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Valeur Moyenne Deal"
                value={stats.avg_deal_value}
                precision={0}
                prefix={<BarChartOutlined />}
                suffix="MAD"
                valueStyle={{ color: '#722ed1' }}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {stats.deals_this_month} deals ce mois
              </Text>
            </Card>
          </Col>
        </Row>

        {/* Onglets */}
        <Tabs defaultActiveKey="1">
          {/* Pipeline */}
          <TabPane tab={<span><FunnelPlotOutlined /> Pipeline</span>} key="1">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <Card title="Évolution du Pipeline" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={pipelineData}>
                      <defs>
                        <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorConversions" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#52c41a" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#52c41a" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="leads" 
                        stroke="#1890ff" 
                        fillOpacity={1} 
                        fill="url(#colorLeads)"
                        name="Leads"
                      />
                      <Area 
                        type="monotone" 
                        dataKey="conversions" 
                        stroke="#52c41a" 
                        fillOpacity={1} 
                        fill="url(#colorConversions)"
                        name="Conversions"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="Top Clients" bordered={false}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {topClients.map((client, index) => (
                      <Card key={index} size="small">
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <Text strong>{client.name}</Text>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Text type="secondary">{client.deals} deals</Text>
                            <Text strong style={{ color: '#52c41a' }}>
                              {client.value?.toLocaleString()} MAD
                            </Text>
                          </div>
                        </Space>
                      </Card>
                    ))}
                  </Space>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Performance */}
          <TabPane tab={<span><LineChartOutlined /> Performance</span>} key="2">
            <Card title="Performance Mensuelle" bordered={false}>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="deals" fill="#1890ff" name="Deals" />
                  <Bar dataKey="revenue" fill="#52c41a" name="Revenus (MAD)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </TabPane>

          {/* Commissions */}
          <TabPane tab={<span><DollarOutlined /> Commissions</span>} key="3">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <Card title="Historique des Commissions" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={commissionHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="earned" 
                        stroke="#52c41a" 
                        strokeWidth={2}
                        name="Commissions gagnées"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="pending" 
                        stroke="#faad14" 
                        strokeWidth={2}
                        name="En attente"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="Résumé Commissions" bordered={false}>
                  <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <Statistic
                      title="Total Gagné"
                      value={stats.commission_earned}
                      precision={2}
                      suffix="MAD"
                      valueStyle={{ color: '#52c41a' }}
                    />
                    <Statistic
                      title="En Attente"
                      value={stats.commission_pending}
                      precision={2}
                      suffix="MAD"
                      valueStyle={{ color: '#faad14' }}
                    />
                    <Statistic
                      title="Total Cumulé"
                      value={(stats.commission_earned || 0) + (stats.commission_pending || 0)}
                      precision={2}
                      suffix="MAD"
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Space>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Deals Récents */}
          <TabPane tab={<span><TrophyOutlined /> Deals Récents</span>} key="4">
            <Card title="Derniers Deals Conclus" bordered={false}>
              <Table
                columns={dealsColumns}
                dataSource={recentDeals}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Spin>
    </div>
  );
};

export default CommercialDashboard;
