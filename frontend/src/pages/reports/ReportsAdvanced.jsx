import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Select, DatePicker, Button, Space, Table, Statistic,
  Tag, Typography, message, Spin, Tabs, Progress, Tooltip, Divider
} from 'antd';
import {
  FileExcelOutlined, FilePdfOutlined, FileTextOutlined, DownloadOutlined,
  BarChartOutlined, LineChartOutlined, PieChartOutlined, ClockCircleOutlined,
  DollarOutlined, UserOutlined, ShoppingOutlined, TrophyOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer
} from 'recharts';
import dayjs from 'dayjs';
import api from '../../utils/api';

const { Title, Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

/**
 * Advanced Reports - Système de rapports détaillés avec export multi-format
 */
const ReportsAdvanced = () => {
  const [loading, setLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [reportType, setReportType] = useState('sales');
  const [dateRange, setDateRange] = useState([
    dayjs().subtract(30, 'days'),
    dayjs()
  ]);
  const [comparisonPeriod, setComparisonPeriod] = useState('previous');
  
  const [reportData, setReportData] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [stats, setStats] = useState({
    total_revenue: 0,
    total_orders: 0,
    total_clicks: 0,
    conversion_rate: 0,
    avg_order_value: 0,
    growth_rate: 0
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  useEffect(() => {
    fetchReportData();
  }, [reportType, dateRange]);

  const fetchReportData = async () => {
    setLoading(true);
    try {
      const params = {
        report_type: reportType,
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        comparison_period: comparisonPeriod
      };

      const response = await api.get('/api/reports/generate', { params });
      setReportData(response.data.report || {});
      setChartData(response.data.chart_data || []);
      setStats(response.data.stats || {});
    } catch (error) {
      console.error('Erreur chargement rapport:', error);
      message.error('Erreur lors du chargement du rapport');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    setExportLoading(true);
    try {
      const params = {
        report_type: reportType,
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        format: format
      };

      const response = await api.get('/api/reports/export', {
        params,
        responseType: 'blob'
      });

      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportType}_${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success(`Rapport exporté en ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Erreur export:', error);
      message.error('Erreur lors de l\'export');
    } finally {
      setExportLoading(false);
    }
  };

  const handleScheduleReport = async () => {
    try {
      await api.post('/api/reports/schedule', {
        report_type: reportType,
        frequency: 'weekly',
        format: 'pdf',
        recipients: [] // TODO: Modal pour sélectionner destinataires
      });
      message.success('Rapport programmé avec succès');
    } catch (error) {
      console.error('Erreur programmation:', error);
      message.error('Erreur lors de la programmation');
    }
  };

  const StatCard = ({ title, value, prefix, suffix, change, icon, color }) => (
    <Card>
      <Statistic
        title={title}
        value={value}
        prefix={icon}
        suffix={suffix}
        valueStyle={{ color: color || '#3f8600' }}
      />
      {change !== undefined && (
        <div style={{ marginTop: 8 }}>
          <Tag color={change >= 0 ? 'success' : 'error'}>
            {change >= 0 ? '+' : ''}{change}% vs période précédente
          </Tag>
        </div>
      )}
    </Card>
  );

  const salesColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Produit',
      dataIndex: 'product_name',
      key: 'product_name'
    },
    {
      title: 'Quantité',
      dataIndex: 'quantity',
      key: 'quantity'
    },
    {
      title: 'Montant',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `${amount?.toLocaleString()} MAD`
    },
    {
      title: 'Commission',
      dataIndex: 'commission',
      key: 'commission',
      render: (commission) => `${commission?.toLocaleString()} MAD`
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'completed' ? 'success' : status === 'pending' ? 'warning' : 'default'}>
          {status === 'completed' ? 'Complété' : status === 'pending' ? 'En attente' : 'Annulé'}
        </Tag>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>
              <BarChartOutlined /> Rapports Avancés
            </Title>
            <Text type="secondary">
              Analysez vos performances et exportez vos données
            </Text>
          </div>
          <Space>
            <Button
              icon={<ClockCircleOutlined />}
              onClick={handleScheduleReport}
            >
              Programmer
            </Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => handleExport('csv')}
              loading={exportLoading}
            >
              Exporter
            </Button>
          </Space>
        </div>
      </div>

      {/* Filtres */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={8}>
            <Text strong>Type de rapport</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={reportType}
              onChange={setReportType}
            >
              <Select.Option value="sales">Ventes</Select.Option>
              <Select.Option value="commissions">Commissions</Select.Option>
              <Select.Option value="clicks">Clics & Conversions</Select.Option>
              <Select.Option value="affiliates">Affiliés</Select.Option>
              <Select.Option value="products">Produits</Select.Option>
              <Select.Option value="revenue">Revenus</Select.Option>
            </Select>
          </Col>
          <Col xs={24} md={10}>
            <Text strong>Période</Text>
            <RangePicker
              style={{ width: '100%', marginTop: 8 }}
              value={dateRange}
              onChange={setDateRange}
              format="DD/MM/YYYY"
            />
          </Col>
          <Col xs={24} md={6}>
            <Text strong>Comparer avec</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              value={comparisonPeriod}
              onChange={setComparisonPeriod}
            >
              <Select.Option value="previous">Période précédente</Select.Option>
              <Select.Option value="last_year">Année dernière</Select.Option>
              <Select.Option value="none">Aucune comparaison</Select.Option>
            </Select>
          </Col>
        </Row>
        <Divider />
        <Space wrap>
          <Button
            icon={<FileExcelOutlined />}
            onClick={() => handleExport('xlsx')}
            loading={exportLoading}
          >
            Excel
          </Button>
          <Button
            icon={<FilePdfOutlined />}
            onClick={() => handleExport('pdf')}
            loading={exportLoading}
          >
            PDF
          </Button>
          <Button
            icon={<FileTextOutlined />}
            onClick={() => handleExport('csv')}
            loading={exportLoading}
          >
            CSV
          </Button>
        </Space>
      </Card>

      <Spin spinning={loading}>
        {/* KPIs */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={12} lg={6}>
            <StatCard
              title="Revenus Total"
              value={stats.total_revenue}
              icon={<DollarOutlined />}
              suffix="MAD"
              change={stats.revenue_growth}
              color="#52c41a"
            />
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <StatCard
              title="Commandes"
              value={stats.total_orders}
              icon={<ShoppingOutlined />}
              change={stats.orders_growth}
              color="#1890ff"
            />
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <StatCard
              title="Taux de Conversion"
              value={stats.conversion_rate}
              icon={<TrophyOutlined />}
              suffix="%"
              change={stats.conversion_growth}
              color="#722ed1"
            />
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <StatCard
              title="Panier Moyen"
              value={stats.avg_order_value}
              icon={<DollarOutlined />}
              suffix="MAD"
              change={stats.aov_growth}
              color="#fa8c16"
            />
          </Col>
        </Row>

        {/* Graphiques et données */}
        <Card>
          <Tabs defaultActiveKey="chart">
            <TabPane
              tab={
                <span>
                  <LineChartOutlined />
                  Graphique
                </span>
              }
              key="chart"
            >
              {reportType === 'sales' && (
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#8884d8"
                      fill="#8884d8"
                      name="Revenus"
                    />
                    <Area
                      type="monotone"
                      dataKey="orders"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      name="Commandes"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}

              {reportType === 'commissions' && (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="earned" fill="#52c41a" name="Gagnées" />
                    <Bar dataKey="paid" fill="#1890ff" name="Payées" />
                    <Bar dataKey="pending" fill="#faad14" name="En attente" />
                  </BarChart>
                </ResponsiveContainer>
              )}

              {reportType === 'clicks' && (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="clicks"
                      stroke="#8884d8"
                      name="Clics"
                    />
                    <Line
                      type="monotone"
                      dataKey="conversions"
                      stroke="#82ca9d"
                      name="Conversions"
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}

              {reportType === 'products' && (
                <ResponsiveContainer width="100%" height={400}>
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name}: ${entry.value}`}
                      outerRadius={150}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </TabPane>

            <TabPane
              tab={
                <span>
                  <FileTextOutlined />
                  Données détaillées
                </span>
              }
              key="table"
            >
              <Table
                columns={salesColumns}
                dataSource={reportData?.transactions || []}
                pagination={{
                  pageSize: 10,
                  showSizeChanger: true,
                  showTotal: (total) => `Total: ${total} transactions`
                }}
                scroll={{ x: 800 }}
              />
            </TabPane>

            <TabPane
              tab={
                <span>
                  <PieChartOutlined />
                  Répartition
                </span>
              }
              key="breakdown"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} lg={12}>
                  <Card title="Top 5 Produits" size="small">
                    {reportData?.top_products?.map((product, index) => (
                      <div key={index} style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <Text>{product.name}</Text>
                          <Text strong>{product.revenue?.toLocaleString()} MAD</Text>
                        </div>
                        <Progress
                          percent={product.percentage}
                          strokeColor={COLORS[index % COLORS.length]}
                        />
                      </div>
                    ))}
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Top 5 Affiliés" size="small">
                    {reportData?.top_affiliates?.map((affiliate, index) => (
                      <div key={index} style={{ marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                          <Text>{affiliate.name}</Text>
                          <Text strong>{affiliate.commission?.toLocaleString()} MAD</Text>
                        </div>
                        <Progress
                          percent={affiliate.percentage}
                          strokeColor={COLORS[index % COLORS.length]}
                        />
                      </div>
                    ))}
                  </Card>
                </Col>
              </Row>
            </TabPane>
          </Tabs>
        </Card>
      </Spin>
    </div>
  );
};

export default ReportsAdvanced;
