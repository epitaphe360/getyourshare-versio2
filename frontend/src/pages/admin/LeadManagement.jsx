import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Tag, Button, Space, Input, Select,
  DatePicker, message, Drawer, Descriptions, Timeline, Badge, Tooltip,
  Modal, Form, Tabs, Progress, Typography
} from 'antd';
import {
  TeamOutlined, DollarOutlined, CheckCircleOutlined, ClockCircleOutlined,
  CloseCircleOutlined, SearchOutlined, MailOutlined, PhoneOutlined,
  UserOutlined, ShopOutlined, TrophyOutlined, LineChartOutlined,
  DownloadOutlined, SendOutlined, EyeOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { TabPane } = Tabs;

/**
 * Lead Management System - Gestion complète des leads
 */
const LeadManagement = () => {
  const [loading, setLoading] = useState(false);
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    new: 0,
    contacted: 0,
    qualified: 0,
    converted: 0,
    conversion_rate: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    status: null,
    source: null,
    service_id: null,
    date_range: null
  });
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0
  });
  const [selectedLead, setSelectedLead] = useState(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [emailModalVisible, setEmailModalVisible] = useState(false);
  const [services, setServices] = useState([]);
  const [analyticsData, setAnalyticsData] = useState({
    conversionTrend: [],
    sourceDistribution: [],
    servicePerformance: []
  });

  const [emailForm] = Form.useForm();

  useEffect(() => {
    fetchLeads();
    fetchStats();
    fetchServices();
    fetchAnalytics();
  }, [filters, pagination.page, pagination.page_size]);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.page_size,
        ...filters
      };

      const response = await api.get('/api/services/admin/leads', { params });
      setLeads(response.data.leads || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.pagination?.total || 0
      }));
    } catch (error) {
      console.error('Erreur chargement leads:', error);
      message.error('Erreur lors du chargement des leads');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/services/admin/leads/stats');
      setStats(response.data.stats || {});
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
    }
  };

  const fetchServices = async () => {
    try {
      const response = await api.get('/api/services/admin/services');
      setServices(response.data.services || []);
    } catch (error) {
      console.error('Erreur chargement services:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/services/admin/leads/analytics');
      setAnalyticsData(response.data.analytics || {
        conversionTrend: [],
        sourceDistribution: [],
        servicePerformance: []
      });
    } catch (error) {
      console.error('Erreur chargement analytics:', error);
    }
  };

  const handleStatusChange = async (leadId, newStatus) => {
    try {
      await api.patch(`/api/services/admin/leads/${leadId}/status`, {
        status: newStatus
      });
      message.success('Statut mis à jour');
      fetchLeads();
      fetchStats();
    } catch (error) {
      message.error('Erreur lors de la mise à jour');
    }
  };

  const handleSendEmail = async (values) => {
    try {
      await api.post(`/api/services/admin/leads/${selectedLead.id}/send-email`, values);
      message.success('Email envoyé avec succès');
      emailModalVisible(false);
      emailForm.resetFields();
    } catch (error) {
      message.error('Erreur lors de l\'envoi de l\'email');
    }
  };

  const handleViewDetails = (lead) => {
    setSelectedLead(lead);
    setDetailsVisible(true);
  };

  const handleExport = async () => {
    try {
      const response = await api.get('/api/services/admin/leads/export', {
        params: filters,
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `leads_${new Date().toISOString()}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('Export réussi');
    } catch (error) {
      message.error('Erreur lors de l\'export');
    }
  };

  const getStatusTag = (status) => {
    const config = {
      new: { color: 'blue', icon: <ClockCircleOutlined />, text: 'Nouveau' },
      contacted: { color: 'orange', icon: <MailOutlined />, text: 'Contacté' },
      qualified: { color: 'cyan', icon: <CheckCircleOutlined />, text: 'Qualifié' },
      converted: { color: 'green', icon: <CheckCircleOutlined />, text: 'Converti' },
      rejected: { color: 'red', icon: <CloseCircleOutlined />, text: 'Rejeté' }
    };
    const statusConfig = config[status] || config.new;
    return (
      <Tag color={statusConfig.color} icon={statusConfig.icon}>
        {statusConfig.text}
      </Tag>
    );
  };

  const columns = [
    {
      title: 'Lead',
      key: 'lead',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{record.name}</Text>
          <Space size="small">
            <MailOutlined style={{ fontSize: '12px', color: '#888' }} />
            <Text type="secondary" style={{ fontSize: '12px' }}>{record.email}</Text>
          </Space>
          {record.phone && (
            <Space size="small">
              <PhoneOutlined style={{ fontSize: '12px', color: '#888' }} />
              <Text type="secondary" style={{ fontSize: '12px' }}>{record.phone}</Text>
            </Space>
          )}
        </Space>
      ),
      width: 250
    },
    {
      title: 'Service',
      dataIndex: 'service_name',
      key: 'service_name',
      render: (name) => (
        <Tag color="blue" icon={<ShopOutlined />}>
          {name}
        </Tag>
      )
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source) => {
        const sourceConfig = {
          website: { color: 'blue', text: 'Site Web' },
          referral: { color: 'purple', text: 'Référence' },
          campaign: { color: 'green', text: 'Campagne' },
          direct: { color: 'default', text: 'Direct' }
        };
        const config = sourceConfig[source] || sourceConfig.direct;
        return <Tag color={config.color}>{config.text}</Tag>;
      }
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status)
    },
    {
      title: 'Budget',
      dataIndex: 'budget',
      key: 'budget',
      render: (budget) => (
        <Text strong style={{ color: '#52c41a' }}>
          {budget ? `${budget.toLocaleString()} MAD` : 'N/A'}
        </Text>
      )
    },
    {
      title: 'Date',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString('fr-FR')
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="Voir détails">
            <Button
              icon={<EyeOutlined />}
              size="small"
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          <Tooltip title="Envoyer email">
            <Button
              icon={<SendOutlined />}
              size="small"
              type="primary"
              onClick={() => {
                setSelectedLead(record);
                setEmailModalVisible(true);
              }}
            />
          </Tooltip>
          <Select
            size="small"
            value={record.status}
            style={{ width: 120 }}
            onChange={(value) => handleStatusChange(record.id, value)}
          >
            <Select.Option value="new">Nouveau</Select.Option>
            <Select.Option value="contacted">Contacté</Select.Option>
            <Select.Option value="qualified">Qualifié</Select.Option>
            <Select.Option value="converted">Converti</Select.Option>
            <Select.Option value="rejected">Rejeté</Select.Option>
          </Select>
        </Space>
      ),
      width: 300
    }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div style={{ padding: '24px' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <TeamOutlined /> Gestion des Leads
          </Title>
          <Text type="secondary">
            Suivi et gestion des demandes de services
          </Text>
        </div>
        <Button
          icon={<DownloadOutlined />}
          onClick={handleExport}
        >
          Exporter CSV
        </Button>
      </div>

      {/* Statistiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Total Leads"
              value={stats.total}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Nouveaux"
              value={stats.new}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Contactés"
              value={stats.contacted}
              prefix={<MailOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Qualifiés"
              value={stats.qualified}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Convertis"
              value={stats.converted}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={4}>
          <Card>
            <Statistic
              title="Taux Conversion"
              value={stats.conversion_rate}
              suffix="%"
              precision={1}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Onglets */}
      <Tabs defaultActiveKey="1">
        {/* Onglet Liste */}
        <TabPane tab={<span><TeamOutlined /> Liste des Leads</span>} key="1">
          {/* Filtres */}
          <Card style={{ marginBottom: '16px' }}>
            <Space wrap>
              <Input
                placeholder="Rechercher..."
                prefix={<SearchOutlined />}
                style={{ width: 250 }}
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              />
              <Select
                placeholder="Statut"
                style={{ width: 150 }}
                allowClear
                value={filters.status}
                onChange={(value) => setFilters({ ...filters, status: value })}
              >
                <Select.Option value="new">Nouveau</Select.Option>
                <Select.Option value="contacted">Contacté</Select.Option>
                <Select.Option value="qualified">Qualifié</Select.Option>
                <Select.Option value="converted">Converti</Select.Option>
                <Select.Option value="rejected">Rejeté</Select.Option>
              </Select>
              <Select
                placeholder="Service"
                style={{ width: 200 }}
                allowClear
                value={filters.service_id}
                onChange={(value) => setFilters({ ...filters, service_id: value })}
              >
                {services.map(service => (
                  <Select.Option key={service.id} value={service.id}>
                    {service.title}
                  </Select.Option>
                ))}
              </Select>
              <Button type="primary" onClick={fetchLeads}>
                Rechercher
              </Button>
            </Space>
          </Card>

          {/* Table */}
          <Card>
            <Table
              columns={columns}
              dataSource={leads}
              rowKey="id"
              loading={loading}
              pagination={{
                current: pagination.page,
                pageSize: pagination.page_size,
                total: pagination.total,
                showSizeChanger: true,
                showTotal: (total) => `Total: ${total} leads`,
                onChange: (page, pageSize) => {
                  setPagination({ ...pagination, page, page_size: pageSize });
                }
              }}
            />
          </Card>
        </TabPane>

        {/* Onglet Analytics */}
        <TabPane tab={<span><LineChartOutlined /> Analytics</span>} key="2">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="Tendance de Conversion" bordered={false}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analyticsData.conversionTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Line type="monotone" dataKey="leads" stroke="#1890ff" name="Leads" />
                    <Line type="monotone" dataKey="converted" stroke="#52c41a" name="Convertis" />
                  </LineChart>
                </ResponsiveContainer>
              </Card>
            </Col>

            <Col xs={24} lg={12}>
              <Card title="Distribution par Source" bordered={false}>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData.sourceDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {analyticsData.sourceDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>

            <Col xs={24}>
              <Card title="Performance par Service" bordered={false}>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData.servicePerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="service" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="leads" fill="#1890ff" name="Leads" />
                    <Bar dataKey="converted" fill="#52c41a" name="Convertis" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>

      {/* Drawer de détails */}
      <Drawer
        title="Détails du Lead"
        open={detailsVisible}
        onClose={() => setDetailsVisible(false)}
        width={600}
      >
        {selectedLead && (
          <div>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Nom">{selectedLead.name}</Descriptions.Item>
              <Descriptions.Item label="Email">{selectedLead.email}</Descriptions.Item>
              <Descriptions.Item label="Téléphone">{selectedLead.phone || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="Entreprise">{selectedLead.company || 'N/A'}</Descriptions.Item>
              <Descriptions.Item label="Service">{selectedLead.service_name}</Descriptions.Item>
              <Descriptions.Item label="Budget">
                {selectedLead.budget ? `${selectedLead.budget.toLocaleString()} MAD` : 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Statut">
                {getStatusTag(selectedLead.status)}
              </Descriptions.Item>
              <Descriptions.Item label="Date de création">
                {new Date(selectedLead.created_at).toLocaleString('fr-FR')}
              </Descriptions.Item>
            </Descriptions>

            {selectedLead.message && (
              <Card title="Message" style={{ marginTop: '16px' }}>
                <Text>{selectedLead.message}</Text>
              </Card>
            )}
          </div>
        )}
      </Drawer>

      {/* Modal d'envoi d'email */}
      <Modal
        title="Envoyer un email"
        open={emailModalVisible}
        onCancel={() => {
          setEmailModalVisible(false);
          emailForm.resetFields();
        }}
        onOk={() => emailForm.submit()}
        okText="Envoyer"
        cancelText="Annuler"
      >
        <Form
          form={emailForm}
          layout="vertical"
          onFinish={handleSendEmail}
        >
          <Form.Item
            label="Destinataire"
            name="to"
            initialValue={selectedLead?.email}
          >
            <Input disabled />
          </Form.Item>
          <Form.Item
            label="Sujet"
            name="subject"
            rules={[{ required: true, message: 'Le sujet est obligatoire' }]}
          >
            <Input placeholder="Sujet de l'email" />
          </Form.Item>
          <Form.Item
            label="Message"
            name="message"
            rules={[{ required: true, message: 'Le message est obligatoire' }]}
          >
            <TextArea rows={6} placeholder="Votre message..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default LeadManagement;
