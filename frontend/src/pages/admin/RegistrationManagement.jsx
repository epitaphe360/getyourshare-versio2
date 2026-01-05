import React, { useState, useEffect } from 'react';
import {
  Table, Button, Input, Select, Tag, Space, Card, Statistic, Row, Col,
  Modal, message, Badge, Drawer, Tabs, Form, Divider, Descriptions,
  Popconfirm, Tooltip, Typography, Alert
} from 'antd';
import {
  CheckCircleOutlined, CloseCircleOutlined, SearchOutlined, 
  EyeOutlined, MailOutlined, PhoneOutlined, GlobalOutlined,
  ShopOutlined, DollarOutlined, FileTextOutlined, ClockCircleOutlined,
  CheckOutlined, CloseOutlined, SendOutlined, FilterOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Option } = Select;
const { TextArea } = Input;
const { Text, Title } = Typography;
const { TabPane } = Tabs;

/**
 * Page de gestion des demandes d'inscription des annonceurs
 * Admin only - Approbation/Rejet des nouvelles inscriptions
 */
const RegistrationManagement = () => {
  const [loading, setLoading] = useState(false);
  const [registrations, setRegistrations] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0
  });

  // Filtres
  const [statusFilter, setStatusFilter] = useState('pending');
  const [countryFilter, setCountryFilter] = useState('all');
  const [searchText, setSearchText] = useState('');

  // Modals & Drawers
  const [detailsDrawerVisible, setDetailsDrawerVisible] = useState(false);
  const [noteModalVisible, setNoteModalVisible] = useState(false);
  const [messageModalVisible, setMessageModalVisible] = useState(false);
  const [selectedRegistration, setSelectedRegistration] = useState(null);
  const [selectedRows, setSelectedRows] = useState([]);

  const [form] = Form.useForm();
  const [messageForm] = Form.useForm();

  useEffect(() => {
    fetchData();
  }, [statusFilter, countryFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchRegistrations(),
        fetchStats()
      ]);
    } catch (error) {
      console.error('Erreur chargement:', error);
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const fetchRegistrations = async () => {
    try {
      const params = {};
      if (statusFilter !== 'all') params.status = statusFilter;
      if (countryFilter !== 'all') params.country = countryFilter;
      if (searchText) params.search = searchText;

      const response = await api.get('/api/admin/registration-requests', { params });
      if (response.data.success) {
        setRegistrations(response.data.registrations || []);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/registration-requests/stats');
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Erreur stats:', error);
    }
  };

  const handleApprove = async (registrationId) => {
    try {
      await api.post(`/api/admin/registration-requests/${registrationId}/approve`);
      message.success('Demande approuvée avec succès');
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de l\'approbation');
    }
  };

  const handleReject = async (registrationId, reason) => {
    try {
      await api.post(`/api/admin/registration-requests/${registrationId}/reject`, {
        reason: reason || 'Non conforme aux critères'
      });
      message.success('Demande rejetée');
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors du rejet');
    }
  };

  const handleBulkApprove = async () => {
    if (selectedRows.length === 0) {
      message.warning('Sélectionnez au moins une demande');
      return;
    }

    try {
      await api.post('/api/admin/registration-requests/bulk-action', {
        registration_ids: selectedRows,
        action: 'approve'
      });
      message.success(`${selectedRows.length} demande(s) approuvée(s)`);
      setSelectedRows([]);
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de l\'action groupée');
    }
  };

  const handleBulkReject = async () => {
    if (selectedRows.length === 0) {
      message.warning('Sélectionnez au moins une demande');
      return;
    }

    Modal.confirm({
      title: `Rejeter ${selectedRows.length} demande(s) ?`,
      content: 'Cette action enverra un email de refus à chaque annonceur.',
      okText: 'Rejeter',
      okType: 'danger',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await api.post('/api/admin/registration-requests/bulk-action', {
            registration_ids: selectedRows,
            action: 'reject'
          });
          message.success(`${selectedRows.length} demande(s) rejetée(s)`);
          setSelectedRows([]);
          fetchData();
        } catch (error) {
          console.error('Erreur:', error);
          message.error('Erreur lors de l\'action groupée');
        }
      }
    });
  };

  const handleAddNote = async (values) => {
    try {
      await api.post(`/api/admin/registration-requests/${selectedRegistration.id}/note`, {
        note: values.note
      });
      message.success('Note ajoutée');
      setNoteModalVisible(false);
      form.resetFields();
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de l\'ajout de la note');
    }
  };

  const handleSendMessage = async (values) => {
    try {
      await api.post(`/api/admin/registration-requests/${selectedRegistration.id}/send-message`, {
        subject: values.subject,
        message: values.message
      });
      message.success('Message envoyé');
      setMessageModalVisible(false);
      messageForm.resetFields();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de l\'envoi');
    }
  };

  const handleViewDetails = (registration) => {
    setSelectedRegistration(registration);
    setDetailsDrawerVisible(true);
  };

  const getStatusTag = (status) => {
    const config = {
      pending: { color: 'orange', icon: <ClockCircleOutlined />, text: 'En attente' },
      approved: { color: 'green', icon: <CheckCircleOutlined />, text: 'Approuvé' },
      rejected: { color: 'red', icon: <CloseCircleOutlined />, text: 'Rejeté' }
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
      title: 'Entreprise',
      key: 'company',
      width: 250,
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{record.company_name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            <MailOutlined /> {record.email}
          </Text>
          {record.phone && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              <PhoneOutlined /> {record.phone}
            </Text>
          )}
        </Space>
      )
    },
    {
      title: 'Contact',
      dataIndex: 'contact_person',
      key: 'contact_person',
      width: 150
    },
    {
      title: 'Pays',
      dataIndex: 'country',
      key: 'country',
      width: 120,
      render: (country) => (
        <Tag icon={<GlobalOutlined />}>{country}</Tag>
      )
    },
    {
      title: 'Type d\'activité',
      dataIndex: 'business_type',
      key: 'business_type',
      width: 150
    },
    {
      title: 'Budget estimé',
      dataIndex: 'estimated_budget',
      key: 'estimated_budget',
      width: 130,
      render: (budget) => budget ? `${budget.toLocaleString('fr-FR')} €` : '-'
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (status) => getStatusTag(status)
    },
    {
      title: 'Date de demande',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date) => new Date(date).toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title="Voir détails">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          {record.status === 'pending' && (
            <>
              <Popconfirm
                title="Approuver cette demande ?"
                description="Un compte sera créé pour cet annonceur"
                onConfirm={() => handleApprove(record.id)}
                okText="Approuver"
                cancelText="Annuler"
              >
                <Button
                  type="primary"
                  size="small"
                  icon={<CheckOutlined />}
                >
                  Approuver
                </Button>
              </Popconfirm>
              <Popconfirm
                title="Rejeter cette demande ?"
                description="L'annonceur sera notifié par email"
                onConfirm={() => handleReject(record.id)}
                okText="Rejeter"
                okType="danger"
                cancelText="Annuler"
              >
                <Button
                  danger
                  size="small"
                  icon={<CloseOutlined />}
                >
                  Rejeter
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      )
    }
  ];

  const rowSelection = {
    selectedRowKeys: selectedRows,
    onChange: (selectedRowKeys) => {
      setSelectedRows(selectedRowKeys);
    },
    getCheckboxProps: (record) => ({
      disabled: record.status !== 'pending'
    })
  };

  const filteredData = registrations.filter((item) => {
    if (!searchText) return true;
    const search = searchText.toLowerCase();
    return (
      item.company_name?.toLowerCase().includes(search) ||
      item.email?.toLowerCase().includes(search) ||
      item.contact_person?.toLowerCase().includes(search)
    );
  });

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>Gestion des Demandes d'Inscription</Title>
        <Text type="secondary">
          Gérez les demandes d'inscription des nouveaux annonceurs
        </Text>
      </div>

      {/* Statistiques */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total"
              value={stats.total}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="En attente"
              value={stats.pending}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Approuvées"
              value={stats.approved}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Rejetées"
              value={stats.rejected}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtres */}
      <Card style={{ marginBottom: '24px' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Space wrap>
            <Input
              placeholder="Rechercher..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 250 }}
              allowClear
            />
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 150 }}
              suffixIcon={<FilterOutlined />}
            >
              <Option value="all">Tous les statuts</Option>
              <Option value="pending">En attente</Option>
              <Option value="approved">Approuvées</Option>
              <Option value="rejected">Rejetées</Option>
            </Select>
            <Select
              value={countryFilter}
              onChange={setCountryFilter}
              style={{ width: 150 }}
            >
              <Option value="all">Tous les pays</Option>
              <Option value="France">France</Option>
              <Option value="Morocco">Maroc</Option>
              <Option value="Belgium">Belgique</Option>
              <Option value="Switzerland">Suisse</Option>
            </Select>
          </Space>
          {selectedRows.length > 0 && (
            <Space>
              <Badge count={selectedRows.length}>
                <Button
                  type="primary"
                  icon={<CheckOutlined />}
                  onClick={handleBulkApprove}
                >
                  Approuver la sélection
                </Button>
              </Badge>
              <Button
                danger
                icon={<CloseOutlined />}
                onClick={handleBulkReject}
              >
                Rejeter la sélection
              </Button>
            </Space>
          )}
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          loading={loading}
          rowSelection={rowSelection}
          scroll={{ x: 1400 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} demandes`
          }}
        />
      </Card>

      {/* Drawer Détails */}
      <Drawer
        title="Détails de la demande"
        placement="right"
        width={600}
        open={detailsDrawerVisible}
        onClose={() => setDetailsDrawerVisible(false)}
      >
        {selectedRegistration && (
          <div>
            <Alert
              message={`Statut: ${selectedRegistration.status}`}
              type={
                selectedRegistration.status === 'approved' ? 'success' :
                selectedRegistration.status === 'rejected' ? 'error' : 'warning'
              }
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Descriptions column={1} bordered>
              <Descriptions.Item label="Entreprise">
                {selectedRegistration.company_name}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {selectedRegistration.email}
              </Descriptions.Item>
              <Descriptions.Item label="Contact">
                {selectedRegistration.contact_person}
              </Descriptions.Item>
              <Descriptions.Item label="Téléphone">
                {selectedRegistration.phone || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Site web">
                {selectedRegistration.website ? (
                  <a href={selectedRegistration.website} target="_blank" rel="noopener noreferrer">
                    {selectedRegistration.website}
                  </a>
                ) : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Pays">
                {selectedRegistration.country}
              </Descriptions.Item>
              <Descriptions.Item label="Type d'activité">
                {selectedRegistration.business_type}
              </Descriptions.Item>
              <Descriptions.Item label="Budget estimé">
                {selectedRegistration.estimated_budget ? 
                  `${selectedRegistration.estimated_budget.toLocaleString('fr-FR')} €` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Date de demande">
                {new Date(selectedRegistration.created_at).toLocaleString('fr-FR')}
              </Descriptions.Item>
            </Descriptions>

            {selectedRegistration.notes && (
              <div style={{ marginTop: 24 }}>
                <Title level={5}>Notes internes</Title>
                <Card size="small">{selectedRegistration.notes}</Card>
              </div>
            )}

            <Divider />

            <Space style={{ width: '100%', justifyContent: 'center' }}>
              {selectedRegistration.status === 'pending' && (
                <>
                  <Button
                    type="primary"
                    icon={<CheckOutlined />}
                    onClick={() => handleApprove(selectedRegistration.id)}
                  >
                    Approuver
                  </Button>
                  <Button
                    danger
                    icon={<CloseOutlined />}
                    onClick={() => handleReject(selectedRegistration.id)}
                  >
                    Rejeter
                  </Button>
                </>
              )}
              <Button
                icon={<FileTextOutlined />}
                onClick={() => {
                  setDetailsDrawerVisible(false);
                  setNoteModalVisible(true);
                }}
              >
                Ajouter une note
              </Button>
              <Button
                icon={<SendOutlined />}
                onClick={() => {
                  setDetailsDrawerVisible(false);
                  setMessageModalVisible(true);
                }}
              >
                Envoyer un message
              </Button>
            </Space>
          </div>
        )}
      </Drawer>

      {/* Modal Note */}
      <Modal
        title="Ajouter une note interne"
        open={noteModalVisible}
        onCancel={() => setNoteModalVisible(false)}
        onOk={() => form.submit()}
        okText="Ajouter"
        cancelText="Annuler"
      >
        <Form form={form} onFinish={handleAddNote} layout="vertical">
          <Form.Item
            name="note"
            label="Note"
            rules={[{ required: true, message: 'Veuillez saisir une note' }]}
          >
            <TextArea rows={4} placeholder="Note interne..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal Message */}
      <Modal
        title="Envoyer un message"
        open={messageModalVisible}
        onCancel={() => setMessageModalVisible(false)}
        onOk={() => messageForm.submit()}
        okText="Envoyer"
        cancelText="Annuler"
        width={600}
      >
        <Form form={messageForm} onFinish={handleSendMessage} layout="vertical">
          <Form.Item
            name="subject"
            label="Sujet"
            rules={[{ required: true, message: 'Veuillez saisir un sujet' }]}
          >
            <Input placeholder="Sujet de l'email..." />
          </Form.Item>
          <Form.Item
            name="message"
            label="Message"
            rules={[{ required: true, message: 'Veuillez saisir un message' }]}
          >
            <TextArea rows={6} placeholder="Votre message..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RegistrationManagement;
