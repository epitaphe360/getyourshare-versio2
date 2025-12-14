import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Tag, Progress, Space, Typography,
  DatePicker, Select, Spin, Tabs, Button, message, Tooltip
} from 'antd';
import {
  DollarOutlined, TrophyOutlined, EyeOutlined, LinkOutlined,
  LineChartOutlined, RiseOutlined, UserOutlined, ShoppingOutlined,
  PercentageOutlined, ThunderboltOutlined, CopyOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

/**
 * Dashboard Influenceur - Clics, conversions, commissions
 */
const InfluencerDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30');
  const [stats, setStats] = useState({
    total_clicks: 0,
    unique_clicks: 0,
    conversions: 0,
    conversion_rate: 0,
    commission_earned: 0,
    commission_pending: 0,
    avg_commission: 0,
    top_campaign: ''
  });
  const [clicksData, setClicksData] = useState([]);
  const [conversionsData, setConversionsData] = useState([]);
  const [campaignPerformance, setCampaignPerformance] = useState([]);
  const [productPerformance, setProductPerformance] = useState([]);
  const [affiliateLinks, setAffiliateLinks] = useState([]);
  const [commissionHistory, setCommissionHistory] = useState([]);

  useEffect(() => {
    fetchData();
  }, [timeRange]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Utiliser Promise.allSettled pour gérer les erreurs individuellement
      const results = await Promise.allSettled([
        api.get(`/api/influencer/stats?days=${timeRange}`),
        api.get(`/api/influencer/clicks?days=${timeRange}`),
        api.get(`/api/influencer/conversions?days=${timeRange}`),
        api.get(`/api/influencer/campaign-performance?days=${timeRange}`),
        api.get(`/api/influencer/product-performance?days=${timeRange}`),
        api.get('/api/influencer/affiliate-links'),
        api.get(`/api/influencer/commissions?days=${timeRange}`)
      ]);

      const [statsRes, clicksRes, conversionsRes, campaignsRes, productsRes, linksRes, commissionsRes] = results;

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data.stats || {});
      }
      if (clicksRes.status === 'fulfilled') {
        setClicksData(clicksRes.value.data.clicks || []);
      }
      if (conversionsRes.status === 'fulfilled') {
        setConversionsData(conversionsRes.value.data.conversions || []);
      }
      if (campaignsRes.status === 'fulfilled') {
        setCampaignPerformance(campaignsRes.value.data.campaigns || []);
      }
      if (productsRes.status === 'fulfilled') {
        setProductPerformance(productsRes.value.data.products || []);
      }
      if (linksRes.status === 'fulfilled') {
        setAffiliateLinks(linksRes.value.data.links || []);
      }
      if (commissionsRes.status === 'fulfilled') {
        setCommissionHistory(commissionsRes.value.data.history || []);
      }

      // Notifier si certaines données n'ont pas pu être chargées
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

  const handleCopyLink = (link) => {
    navigator.clipboard.writeText(link);
    message.success('Lien copié !');
  };

  const linksColumns = [
    {
      title: 'Campagne',
      dataIndex: 'campaign_name',
      key: 'campaign_name',
      render: (name, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.product_name}</Text>
        </Space>
      )
    },
    {
      title: 'Lien',
      dataIndex: 'link',
      key: 'link',
      render: (link) => (
        <Space>
          <LinkOutlined />
          <Text code style={{ fontSize: '12px', maxWidth: '200px', display: 'inline-block', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {link}
          </Text>
          <Tooltip title="Copier">
            <Button
              size="small"
              icon={<CopyOutlined />}
              onClick={() => handleCopyLink(link)}
            />
          </Tooltip>
        </Space>
      )
    },
    {
      title: 'Clics',
      dataIndex: 'clicks',
      key: 'clicks',
      render: (clicks) => (
        <Tag color="blue" icon={<EyeOutlined />}>
          {clicks}
        </Tag>
      )
    },
    {
      title: 'Conversions',
      dataIndex: 'conversions',
      key: 'conversions',
      render: (conversions) => (
        <Tag color="green" icon={<ShoppingOutlined />}>
          {conversions}
        </Tag>
      )
    },
    {
      title: 'Taux',
      key: 'rate',
      render: (_, record) => {
        const rate = record.clicks > 0 ? (record.conversions / record.clicks * 100) : 0;
        return <Progress percent={rate.toFixed(1)} size="small" />;
      }
    },
    {
      title: 'Commission',
      dataIndex: 'commission',
      key: 'commission',
      render: (commission) => (
        <Text strong style={{ color: '#52c41a' }}>
          {commission?.toLocaleString()} MAD
        </Text>
      )
    }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div style={{ padding: '24px' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <TrophyOutlined /> Dashboard Influenceur
          </Title>
          <Text type="secondary">
            Suivi de vos performances d'affiliation
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
                title="Clics Totaux"
                value={stats.total_clicks}
                prefix={<EyeOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {stats.unique_clicks} uniques
              </Text>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Conversions"
                value={stats.conversions}
                prefix={<ShoppingOutlined />}
                valueStyle={{ color: '#52c41a' }}
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
                title="Commission Moyenne"
                value={stats.avg_commission}
                precision={2}
                prefix={<PercentageOutlined />}
                suffix="MAD"
                valueStyle={{ color: '#722ed1' }}
              />
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Top: {stats.top_campaign || 'N/A'}
              </Text>
            </Card>
          </Col>
        </Row>

        {/* Onglets */}
        <Tabs defaultActiveKey="1">
          {/* Aperçu */}
          <TabPane tab={<span><LineChartOutlined /> Aperçu</span>} key="1">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={12}>
                <Card title="Évolution des Clics" bordered={false}>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={clicksData}>
                      <defs>
                        <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area 
                        type="monotone" 
                        dataKey="clicks" 
                        stroke="#1890ff" 
                        fillOpacity={1} 
                        fill="url(#colorClicks)"
                        name="Clics"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={12}>
                <Card title="Conversions & Revenus" bordered={false}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={conversionsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip />
                      <Legend />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="conversions" 
                        stroke="#52c41a" 
                        strokeWidth={2}
                        name="Conversions"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="#1890ff" 
                        strokeWidth={2}
                        name="Revenus (MAD)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Campagnes */}
          <TabPane tab={<span><ThunderboltOutlined /> Campagnes</span>} key="2">
            <Row gutter={[16, 16]}>
              <Col xs={24} lg={16}>
                <Card title="Performance par Campagne" bordered={false}>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={campaignPerformance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="campaign" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="clicks" fill="#1890ff" name="Clics" />
                      <Bar dataKey="conversions" fill="#52c41a" name="Conversions" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>
              </Col>

              <Col xs={24} lg={8}>
                <Card title="Top Produits" bordered={false}>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={productPerformance}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {productPerformance.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>

          {/* Liens */}
          <TabPane tab={<span><LinkOutlined /> Mes Liens</span>} key="3">
            <Card title="Liens d'Affiliation" bordered={false}>
              <Table
                columns={linksColumns}
                dataSource={affiliateLinks}
                rowKey="id"
                pagination={{ pageSize: 10 }}
              />
            </Card>
          </TabPane>

          {/* Commissions */}
          <TabPane tab={<span><DollarOutlined /> Commissions</span>} key="4">
            <Row gutter={[16, 16]}>
              <Col xs={24}>
                <Card title="Historique des Commissions" bordered={false}>
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart data={commissionHistory}>
                      <defs>
                        <linearGradient id="colorEarned" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#52c41a" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#52c41a" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="earned" 
                        stroke="#52c41a" 
                        fillOpacity={1} 
                        fill="url(#colorEarned)"
                        name="Commissions gagnées (MAD)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Card>
              </Col>
            </Row>
          </TabPane>
        </Tabs>
      </Spin>
    </div>
  );
};

export default InfluencerDashboard;
