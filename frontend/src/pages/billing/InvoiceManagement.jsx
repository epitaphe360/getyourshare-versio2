import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Statistic, Table, Tag, Button, Space, Input, Select,
  DatePicker, message, Drawer, Descriptions, Modal, Form, Spin, Typography,
  Tooltip, Badge
} from 'antd';
import {
  DollarOutlined, FileTextOutlined, DownloadOutlined, EyeOutlined,
  CheckCircleOutlined, ClockCircleOutlined, CloseCircleOutlined,
  SearchOutlined, PlusOutlined, SendOutlined, WarningOutlined
} from '@ant-design/icons';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer
} from 'recharts';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

/**
 * Invoice Management System - Gestion des factures
 */
const InvoiceManagement = () => {
  const [loading, setLoading] = useState(false);
  const [invoices, setInvoices] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    paid: 0,
    pending: 0,
    overdue: 0,
    total_amount: 0,
    paid_amount: 0,
    pending_amount: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    status: null,
    date_range: null
  });
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0
  });
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [revenueChart, setRevenueChart] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);

  const [form] = Form.useForm();

  useEffect(() => {
    fetchInvoices();
    fetchStats();
    fetchChartData();
  }, [filters, pagination.page, pagination.page_size]);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.page_size,
        ...filters
      };

      const response = await api.get('/api/invoices', { params });
      setInvoices(response.data.invoices || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.pagination?.total || 0
      }));
    } catch (error) {
      console.error('Erreur chargement factures:', error);
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/invoices/stats');
      setStats(response.data.stats || {});
    } catch (error) {
      console.error('Erreur stats:', error);
    }
  };

  const fetchChartData = async () => {
    try {
      const [revenueRes, distributionRes] = await Promise.all([
        api.get('/api/invoices/revenue-chart'),
        api.get('/api/invoices/status-distribution')
      ]);
      setRevenueChart(revenueRes.data.data || []);
      setStatusDistribution(distributionRes.data.data || []);
    } catch (error) {
      console.error('Erreur graphiques:', error);
    }
  };

  const handleCreate = async (values) => {
    try {
      await api.post('/api/invoices', values);
      message.success('Facture créée');
      setCreateModalVisible(false);
      form.resetFields();
      fetchInvoices();
      fetchStats();
    } catch (error) {
      message.error('Erreur lors de la création');
    }
  };

  const handleDownloadPDF = async (invoiceId) => {
    try {
      const response = await api.get(`/api/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `facture_${invoiceId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('Facture téléchargée');
    } catch (error) {
      message.error('Erreur lors du téléchargement');
    }
  };

  const handleSendReminder = async (invoiceId) => {
    try {
      await api.post(`/api/invoices/${invoiceId}/remind`);
      message.success('Rappel envoyé');
    } catch (error) {
      message.error('Erreur lors de l\'envoi');
    }
  };

  const handleMarkAsPaid = async (invoiceId) => {
    try {
      await api.patch(`/api/invoices/${invoiceId}/status`, { status: 'paid' });
      message.success('Facture marquée comme payée');
      fetchInvoices();
      fetchStats();
    } catch (error) {
      message.error('Erreur lors de la mise à jour');
    }
  };

  const getStatusTag = (status) => {
    const config = {
      paid: { color: 'success', icon: <CheckCircleOutlined />, text: 'Payée' },
      pending: { color: 'warning', icon: <ClockCircleOutlined />, text: 'En attente' },
      overdue: { color: 'error', icon: <WarningOutlined />, text: 'En retard' },
      cancelled: { color: 'default', icon: <CloseCircleOutlined />, text: 'Annulée' }
    };
    const statusConfig = config[status] || config.pending;
    return (
      <Tag color={statusConfig.color} icon={statusConfig.icon}>
        {statusConfig.text}
      </Tag>
    );
  };

  const columns = [
    {
      title: 'N° Facture',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      render: (number) => <Text code strong>{number}</Text>
    },
    {
      title: 'Client',
      key: 'client',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <Text strong>{record.client_name}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>{record.client_email}</Text>
        </Space>
      )
    },
    {
      title: 'Date',
      dataIndex: 'invoice_date',
      key: 'invoice_date',
      render: (date) => new Date(date).toLocaleDateString('fr-FR')
    },
    {
      title: 'Échéance',
      dataIndex: 'due_date',
      key: 'due_date',
      render: (date) => {
        const dueDate = new Date(date);
        const isOverdue = dueDate < new Date();
        return (
          <Text type={isOverdue ? 'danger' : 'secondary'}>
            {dueDate.toLocaleDateString('fr-FR')}
          </Text>
        );
      }
    },
    {
      title: 'Montant',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount) => (
        <Text strong style={{ color: '#52c41a' }}>
          {amount?.toLocaleString()} MAD
        </Text>
      )
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusTag(status)
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
              onClick={() => {
                setSelectedInvoice(record);
                setDetailsVisible(true);
              }}
            />
          </Tooltip>
          <Tooltip title="Télécharger PDF">
            <Button
              icon={<DownloadOutlined />}
              size="small"
              type="primary"
              onClick={() => handleDownloadPDF(record.id)}
            />
          </Tooltip>
          {record.status === 'pending' && (
            <>
              <Tooltip title="Envoyer rappel">
                <Button
                  icon={<SendOutlined />}
                  size="small"
                  onClick={() => handleSendReminder(record.id)}
                />
              </Tooltip>
              <Tooltip title="Marquer comme payée">
                <Button
                  icon={<CheckCircleOutlined />}
                  size="small"
                  onClick={() => handleMarkAsPaid(record.id)}
                />
              </Tooltip>
            </>
          )}
        </Space>
      ),
      width: 200
    }
  ];

  const COLORS = ['#52c41a', '#faad14', '#ff4d4f', '#d9d9d9'];

  return (
    <div style={{ padding: '24px' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <FileTextOutlined /> Gestion des Factures
          </Title>
          <Text type="secondary">
            Créer, suivre et gérer vos factures
          </Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          Nouvelle Facture
        </Button>
      </div>

      {/* Statistiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Factures"
              value={stats.total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Payées"
              value={stats.paid}
              prefix={<CheckCircleOutlined />}
              suffix={`/ ${stats.total}`}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="En Attente"
              value={stats.pending}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="En Retard"
              value={stats.overdue}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Montants */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="Montant Total"
              value={stats.total_amount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="MAD"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="Montant Payé"
              value={stats.paid_amount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="MAD"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card>
            <Statistic
              title="Montant En Attente"
              value={stats.pending_amount}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="MAD"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Graphiques */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={16}>
          <Card title="Évolution des Revenus" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={revenueChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="invoiced" fill="#1890ff" name="Facturé" />
                <Bar dataKey="paid" fill="#52c41a" name="Payé" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Distribution par Statut" bordered={false}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

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
            <Select.Option value="paid">Payée</Select.Option>
            <Select.Option value="pending">En attente</Select.Option>
            <Select.Option value="overdue">En retard</Select.Option>
            <Select.Option value="cancelled">Annulée</Select.Option>
          </Select>
          <Button type="primary" onClick={fetchInvoices}>
            Rechercher
          </Button>
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={invoices}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.page,
            pageSize: pagination.page_size,
            total: pagination.total,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} factures`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, page, page_size: pageSize });
            }
          }}
        />
      </Card>

      {/* Drawer de détails */}
      <Drawer
        title="Détails de la Facture"
        open={detailsVisible}
        onClose={() => setDetailsVisible(false)}
        width={600}
      >
        {selectedInvoice && (
          <div>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="N° Facture">{selectedInvoice.invoice_number}</Descriptions.Item>
              <Descriptions.Item label="Client">{selectedInvoice.client_name}</Descriptions.Item>
              <Descriptions.Item label="Email">{selectedInvoice.client_email}</Descriptions.Item>
              <Descriptions.Item label="Date">{new Date(selectedInvoice.invoice_date).toLocaleDateString('fr-FR')}</Descriptions.Item>
              <Descriptions.Item label="Échéance">{new Date(selectedInvoice.due_date).toLocaleDateString('fr-FR')}</Descriptions.Item>
              <Descriptions.Item label="Montant">{selectedInvoice.total_amount?.toLocaleString()} MAD</Descriptions.Item>
              <Descriptions.Item label="Statut">{getStatusTag(selectedInvoice.status)}</Descriptions.Item>
            </Descriptions>

            {selectedInvoice.items && (
              <Card title="Articles" style={{ marginTop: '16px' }}>
                <Table
                  dataSource={selectedInvoice.items}
                  columns={[
                    { title: 'Description', dataIndex: 'description', key: 'description' },
                    { title: 'Quantité', dataIndex: 'quantity', key: 'quantity' },
                    { title: 'Prix Unit.', dataIndex: 'unit_price', key: 'unit_price', render: (p) => `${p} MAD` },
                    { title: 'Total', dataIndex: 'total', key: 'total', render: (t) => `${t} MAD` }
                  ]}
                  pagination={false}
                  size="small"
                />
              </Card>
            )}
          </div>
        )}
      </Drawer>

      {/* Modal de création */}
      <Modal
        title="Nouvelle Facture"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        okText="Créer"
        cancelText="Annuler"
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Client"
                name="client_name"
                rules={[{ required: true, message: 'Le client est obligatoire' }]}
              >
                <Input placeholder="Nom du client" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Email Client"
                name="client_email"
                rules={[
                  { required: true, message: 'L\'email est obligatoire' },
                  { type: 'email', message: 'Email invalide' }
                ]}
              >
                <Input placeholder="client@example.com" />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Date Facture"
                name="invoice_date"
                rules={[{ required: true, message: 'La date est obligatoire' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Date Échéance"
                name="due_date"
                rules={[{ required: true, message: 'L\'échéance est obligatoire' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item
            label="Montant Total"
            name="total_amount"
            rules={[{ required: true, message: 'Le montant est obligatoire' }]}
          >
            <Input type="number" suffix="MAD" placeholder="0.00" />
          </Form.Item>
          <Form.Item
            label="Description"
            name="description"
          >
            <Input.TextArea rows={3} placeholder="Description de la facture..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default InvoiceManagement;
