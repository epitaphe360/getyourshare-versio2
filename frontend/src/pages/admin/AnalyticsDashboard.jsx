import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Select, DatePicker, Space, Typography, Spin,
  Tabs, Table, Tag, Progress, message
} from 'antd';
import {
  ArrowUpOutlined, ArrowDownOutlined, UserOutlined, DollarOutlined,
  ShoppingOutlined, RiseOutlined, FallOutlined, TrophyOutlined,
  TeamOutlined, LineChartOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie,
  Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

/**
 * Dashboard Analytics Admin - Métriques et graphiques avancés
 */
const AnalyticsDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30'); // 7, 30, 90, 365 jours
  const [metrics, setMetrics] = useState({
    mrr: 0,
    arr: 0,
    churn_rate: 0,
    active_users: 0,
    new_users: 0,
    revenue_growth: 0
  });
  const [revenueData, setRevenueData] = useState([]);
  const [usersGrowthData, setUsersGrowthData] = useState([]);
  const [subscriptionsData, setSubscriptionsData] = useState([]);
  const [churnData, setChurnData] = useState([]);
  const [planDistribution, setPlanDistribution] = useState([]);
  const [topPerformers, setTopPerformers] = useState([]);
  const [revenueBySource, setRevenueBySource] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      // Utiliser Promise.allSettled pour gérer les erreurs individuellement
      const results = await Promise.allSettled([
        api.get(`/api/admin/analytics/metrics?days=${timeRange}`),
        api.get(`/api/admin/analytics/revenue?days=${timeRange}`),
        api.get(`/api/admin/analytics/users-growth?days=${timeRange}`),
        api.get(`/api/admin/analytics/subscriptions?days=${timeRange}`),
        api.get(`/api/admin/analytics/churn?days=${timeRange}`),
        api.get('/api/admin/analytics/plan-distribution'),
        api.get(`/api/admin/analytics/top-performers?days=${timeRange}`),
        api.get(`/api/admin/analytics/revenue-by-source?days=${timeRange}`)
      ]);

      const [
        metricsRes,
        revenueRes,
        usersRes,
        subscriptionsRes,
        churnRes,
        distributionRes,
        performersRes,
        sourceRes
      ] = results;

      if (metricsRes.status === 'fulfilled') {
        setMetrics(metricsRes.value.data.metrics || {});
      }
      if (revenueRes.status === 'fulfilled') {
        setRevenueData(revenueRes.value.data.data || []);
      }
      if (usersRes.status === 'fulfilled') {
        setUsersGrowthData(usersRes.value.data.data || []);
      }
      if (subscriptionsRes.status === 'fulfilled') {
        setSubscriptionsData(subscriptionsRes.value.data.data || []);
      }
      if (churnRes.status === 'fulfilled') {
        setChurnData(churnRes.value.data.data || []);
      }
      if (distributionRes.status === 'fulfilled') {
        setPlanDistribution(distributionRes.value.data.data || []);
      }
      if (performersRes.status === 'fulfilled') {
        setTopPerformers(performersRes.value.data.data || []);
      }
      if (sourceRes.status === 'fulfilled') {
        setRevenueBySource(sourceRes.value.data.data || []);
      }

      // Notifier si certaines données n'ont pas pu être chargées
      const failedRequests = results.filter(r => r.status === 'rejected');
      if (failedRequests.length > 0) {
        console.error('Certaines analytics n\'ont pas pu être chargées:', failedRequests);
        if (failedRequests.length === results.length) {
          message.error('Erreur lors du chargement des analytics');
        } else {
          message.warning('Certaines données sont temporairement indisponibles');
        }
      }
    } catch (error) {
      console.error('Erreur chargement analytics:', error);
      message.error('Erreur lors du chargement des analytics');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'MAD'
    }).format(value);
  };

  const topPerformersColumns = [
    {
      title: 'Rang',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      render: (rank) => (
        <Tag color={rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : 'default'}>
          #{rank}
        </Tag>
      )
    },
    {
      title: 'Utilisateur',
      dataIndex: 'user_name',
      key: 'user_name',
      render: (name, record) => (
        <Space>
          <UserOutlined />
          <div>
            <div style={{ fontWeight: 500 }}>{name}</div>
            <Text type="secondary" style={{ fontSize: '12px' }}>{record.email}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Rôle',
      dataIndex: 'role',
      key: 'role',
      render: (role) => {
        const roleConfig = {
          merchant: { color: 'blue', text: 'Marchand' },
          influencer: { color: 'purple', text: 'Influenceur' },
          commercial: { color: 'green', text: 'Commercial' }
        };
        const config = roleConfig[role] || { color: 'default', text: role };
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: 'Revenus générés',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (revenue) => (
        <Text strong style={{ color: '#52c41a' }}>
          {formatCurrency(revenue)}
        </Text>
      )
    },
    {
      title: 'Transactions',
      dataIndex: 'transactions_count',
      key: 'transactions_count'
    },
    {
      title: 'Performance',
      key: 'performance',
      render: (_, record) => {
        const percentage = (record.revenue / topPerformers[0]?.revenue * 100) || 0;
        return <Progress percent={percentage.toFixed(0)} size="small" />;
      }
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <LineChartOutlined /> Tableau de Bord Analytics
          </Title>
          <Text type="secondary">
            Analyse détaillée des performances de la plateforme
          </Text>
        </div>
        <Space>
          <Select
            id="time-range-select"
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 180 }}
          >
            <Select.Option value="7">7 derniers jours</Select.Option>
            <Select.Option value="30">30 derniers jours</Select.Option>
            <Select.Option value="90">90 derniers jours</Select.Option>
            <Select.Option value="365">12 derniers mois</Select.Option>
          </Select>
        </Space>
      </div>

      <Spin spinning={loading}>
        {/* KPIs principaux */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="MRR (Revenus Mensuels Récurrents)"
                value={metrics.mrr}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="MAD"
                valueStyle={{ color: '#3f8600' }}
              />
              <div style={{ marginTop: '8px' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  ARR: {formatCurrency(metrics.arr)}
                </Text>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Utilisateurs Actifs"
                value={metrics.active_users}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
              <div style={{ marginTop: '8px' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {metrics.new_users > 0 ? '+' : ''}{metrics.new_users} nouveaux
                </Text>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Taux de Churn"
                value={metrics.churn_rate}
                precision={2}
                suffix="%"
                prefix={metrics.churn_rate > 5 ? <FallOutlined /> : <RiseOutlined />}
                valueStyle={{ color: metrics.churn_rate > 5 ? '#cf1322' : '#3f8600' }}
              />
              <div style={{ marginTop: '8px' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {metrics.churn_rate > 5 ? 'Attention requise' : 'Excellent'}
                </Text>
              </div>
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Croissance Revenus"
                value={metrics.revenue_growth}
                precision={2}
                suffix="%"
                prefix={metrics.revenue_growth >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                valueStyle={{ color: metrics.revenue_growth >= 0 ? '#3f8600' : '#cf1322' }}
              />
              <div style={{ marginTop: '8px' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  vs période précédente
                </Text>
              </div>
            </Card>
          </Col>
        </Row>

        {/* Onglets avec graphiques */}
        <Tabs defaultActiveKey="1">
          {/* Onglet Revenus */}
          <TabPane tab={<span><DollarOutlined /> Revenus</span>} key="1">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <Card title="Évolution des Revenus" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={revenueData}>
                      <defs>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="#1890ff" 
                        fillOpacity={1} 
                        fill="url(#colorRevenue)"
                        name="Revenus"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="Revenus par Source" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={revenueBySource}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {revenueBySource.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(value)} />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Onglet Utilisateurs */}
          <TabPane tab={<span><UserOutlined /> Utilisateurs</span>} key="2">
            <Row gutter={[16, 16]}>
              <Col xs={24}>
                <Card title="Croissance des Utilisateurs" bordered={false}>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={usersGrowthData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="total_users" 
                        stroke="#1890ff" 
                        strokeWidth={2}
                        name="Total"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="merchants" 
                        stroke="#52c41a" 
                        strokeWidth={2}
                        name="Marchands"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="influencers" 
                        stroke="#722ed1" 
                        strokeWidth={2}
                        name="Influenceurs"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="commercials" 
                        stroke="#fa8c16" 
                        strokeWidth={2}
                        name="Commerciaux"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Onglet Abonnements */}
          <TabPane tab={<span><ShoppingOutlined /> Abonnements</span>} key="3">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card title="Nouveaux Abonnements" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <BarChart data={subscriptionsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="new_subscriptions" fill="#1890ff" name="Nouveaux" />
                      <Bar dataKey="cancelled_subscriptions" fill="#ff4d4f" name="Annulés" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="Distribution des Plans" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={planDistribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {planDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Onglet Churn */}
          <TabPane tab={<span><FallOutlined /> Churn Analysis</span>} key="4">
            <Row gutter={[16, 16]}>
              <Col xs={24}>
                <Card title="Évolution du Taux de Churn" bordered={false}>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={churnData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip formatter={(value) => `${value}%`} />
                      <Legend />
                      <Line 
                        type="monotone" 
                        dataKey="churn_rate" 
                        stroke="#ff4d4f" 
                        strokeWidth={2}
                        name="Taux de churn"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="retention_rate" 
                        stroke="#52c41a" 
                        strokeWidth={2}
                        name="Taux de rétention"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Onglet Top Performers */}
          <TabPane tab={<span><TrophyOutlined /> Top Performers</span>} key="5">
            <Card title="Meilleurs Performeurs" bordered={false}>
              <Table
                columns={topPerformersColumns}
                dataSource={topPerformers}
                rowKey="user_id"
                pagination={false}
              />
            </Card>
          </TabPane>
        </Tabs>
      </Spin>
    </div>
  );
};

export default AnalyticsDashboard;
