import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Tag, Space, Card, Statistic, Row, Col, Modal, message } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  UserOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import api from '../../utils/api';
import SubscriptionFormModal from '../../components/admin/SubscriptionFormModal';
import SubscriptionDetailsModal from '../../components/admin/SubscriptionDetailsModal';

const { Option } = Select;
const { confirm } = Modal;

/**
 * Page de gestion complète des abonnements (Admin)
 * Permet de gérer les plans d'abonnement et les abonnements actifs
 */
const AdminSubscriptionsManager = () => {
  // ============================================
  // STATE MANAGEMENT
  // ============================================
  const [loading, setLoading] = useState(false);
  const [subscriptions, setSubscriptions] = useState([]);
  const [plans, setPlans] = useState([]);
  const [stats, setStats] = useState({
    totalSubscriptions: 0,
    activeSubscriptions: 0,
    totalRevenue: 0,
    trialSubscriptions: 0,
  });

  // Filtres et recherche
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [planFilter, setPlanFilter] = useState('all');

  // Modals
  const [formModalVisible, setFormModalVisible] = useState(false);
  const [detailsModalVisible, setDetailsModalVisible] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [modalMode, setModalMode] = useState('create'); // 'create' ou 'edit'

  // Vue active : 'subscriptions' ou 'plans'
  const [activeView, setActiveView] = useState('subscriptions');

  // ============================================
  // DATA FETCHING
  // ============================================

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSubscriptions(),
        fetchPlans(),
        fetchStats(),
      ]);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      message.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscriptions = async () => {
    try {
      const response = await api.get('/api/admin/subscriptions');
      if (response.data.success) {
        setSubscriptions(response.data.subscriptions || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des abonnements:', error);
    }
  };

  const fetchPlans = async () => {
    try {
      const response = await api.get('/api/subscriptions/plans');
      if (response.data.success) {
        setPlans(response.data.plans || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des plans:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/subscriptions/stats');
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    }
  };

  // ============================================
  // ACTIONS HANDLERS
  // ============================================

  const handleCreatePlan = () => {
    setSelectedPlan(null);
    setModalMode('create');
    setFormModalVisible(true);
  };

  const handleEditPlan = (plan) => {
    setSelectedPlan(plan);
    setModalMode('edit');
    setFormModalVisible(true);
  };

  const handleDeletePlan = (planId) => {
    confirm({
      title: 'Supprimer ce plan ?',
      content: 'Cette action est irréversible. Les abonnements existants ne seront pas affectés.',
      okText: 'Supprimer',
      okType: 'danger',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await api.delete(`/api/admin/subscriptions/plans/${planId}`);
          message.success('Plan supprimé avec succès');
          fetchData();
        } catch (error) {
          console.error('Erreur lors de la suppression:', error);
          message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
        }
      },
    });
  };

  const handleViewDetails = (subscription) => {
    setSelectedSubscription(subscription);
    setDetailsModalVisible(true);
  };

  const handleCancelSubscription = (subscriptionId) => {
    confirm({
      title: 'Annuler cet abonnement ?',
      content: 'L\'abonnement sera annulé à la fin de la période en cours.',
      okText: 'Annuler l\'abonnement',
      okType: 'danger',
      cancelText: 'Retour',
      onOk: async () => {
        try {
          await api.post(`/api/admin/subscriptions/${subscriptionId}/cancel`, {
            reason: 'Annulé par admin',
            immediate: false,
          });
          message.success('Abonnement annulé avec succès');
          fetchData();
        } catch (error) {
          console.error('Erreur lors de l\'annulation:', error);
          message.error(error.response?.data?.detail || 'Erreur lors de l\'annulation');
        }
      },
    });
  };

  const handleSaveForm = async (formData) => {
    try {
      if (modalMode === 'create') {
        await api.post('/api/admin/subscriptions/plans', formData);
        message.success('Plan créé avec succès');
      } else {
        await api.put(`/api/admin/subscriptions/plans/${selectedPlan.id}`, formData);
        message.success('Plan modifié avec succès');
      }
      setFormModalVisible(false);
      fetchData();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
      throw error;
    }
  };

  // ============================================
  // FILTRAGE DES DONNÉES
  // ============================================

  const filteredSubscriptions = subscriptions.filter((sub) => {
    const matchSearch = searchText === '' || 
      sub.user_email?.toLowerCase().includes(searchText.toLowerCase()) ||
      sub.user_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      sub.plan_name?.toLowerCase().includes(searchText.toLowerCase());
    
    const matchStatus = statusFilter === 'all' || sub.status === statusFilter;
    const matchPlan = planFilter === 'all' || sub.plan_id === planFilter;

    return matchSearch && matchStatus && matchPlan;
  });

  const filteredPlans = plans.filter((plan) => {
    return searchText === '' || 
      plan.name?.toLowerCase().includes(searchText.toLowerCase()) ||
      plan.code?.toLowerCase().includes(searchText.toLowerCase());
  });

  // ============================================
  // COLUMNS DEFINITIONS
  // ============================================

  const subscriptionColumns = [
    {
      title: 'Utilisateur',
      dataIndex: 'user_name',
      key: 'user_name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text || 'N/A'}</div>
          <div style={{ fontSize: '12px', color: '#888' }}>{record.user_email}</div>
        </div>
      ),
    },
    {
      title: 'Plan',
      dataIndex: 'plan_name',
      key: 'plan_name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#888' }}>{record.plan_type}</div>
        </div>
      ),
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusConfig = {
          active: { color: 'success', icon: <CheckCircleOutlined />, text: 'Actif' },
          trialing: { color: 'processing', icon: <SyncOutlined spin />, text: 'Essai' },
          past_due: { color: 'warning', icon: <CloseCircleOutlined />, text: 'En retard' },
          canceled: { color: 'default', icon: <CloseCircleOutlined />, text: 'Annulé' },
          incomplete: { color: 'error', icon: <CloseCircleOutlined />, text: 'Incomplet' },
        };
        const config = statusConfig[status] || statusConfig.active;
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: 'Prix',
      dataIndex: 'plan_price',
      key: 'plan_price',
      render: (price, record) => (
        <span style={{ fontWeight: 500 }}>
          {price ? `${price.toFixed(2)} ${record.currency || 'MAD'}` : 'Gratuit'}
        </span>
      ),
    },
    {
      title: 'Période',
      key: 'period',
      render: (_, record) => {
        const start = record.current_period_start ? new Date(record.current_period_start).toLocaleDateString('fr-FR') : 'N/A';
        const end = record.current_period_end ? new Date(record.current_period_end).toLocaleDateString('fr-FR') : 'N/A';
        return (
          <div style={{ fontSize: '12px' }}>
            <div>{start}</div>
            <div style={{ color: '#888' }}>→ {end}</div>
          </div>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
            title="Voir détails"
          />
          <Button
            type="text"
            size="small"
            danger
            icon={<CloseCircleOutlined />}
            onClick={() => handleCancelSubscription(record.id)}
            disabled={record.status === 'canceled'}
            title="Annuler"
          />
        </Space>
      ),
    },
  ];

  const planColumns = [
    {
      title: 'Nom',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#888' }}>{record.code}</div>
        </div>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => {
        const typeConfig = {
          standard: { color: 'blue', text: 'Standard' },
          enterprise: { color: 'purple', text: 'Entreprise' },
          marketplace: { color: 'green', text: 'Marketplace' },
        };
        const config = typeConfig[type] || { color: 'default', text: type };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: 'Prix',
      key: 'price',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {record.price_mad ? `${record.price_mad} MAD` : 'Gratuit'}
          </div>
          {record.price && (
            <div style={{ fontSize: '12px', color: '#888' }}>
              {record.price} {record.currency || 'EUR'}
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Limites',
      key: 'limits',
      render: (_, record) => (
        <div style={{ fontSize: '12px' }}>
          <div>👥 {record.max_team_members || '∞'} membres</div>
          <div>🌐 {record.max_domains || '∞'} domaines</div>
        </div>
      ),
    },
    {
      title: 'Statut',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Actif' : 'Inactif'}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditPlan(record)}
            title="Modifier"
          />
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeletePlan(record.id)}
            title="Supprimer"
          />
        </Space>
      ),
    },
  ];

  // ============================================
  // RENDER
  // ============================================

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          Gestion des Abonnements
        </h1>
        <p style={{ color: '#888', marginTop: '8px' }}>
          Gérez les plans d'abonnement et les abonnements actifs
        </p>
      </div>

      {/* Statistiques */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Abonnements"
              value={stats.totalSubscriptions}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Abonnements Actifs"
              value={stats.activeSubscriptions}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="En Essai"
              value={stats.trialSubscriptions}
              prefix={<SyncOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Revenu Mensuel"
              value={stats.totalRevenue}
              prefix={<DollarOutlined />}
              suffix="MAD"
              precision={2}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Toggle View + Actions */}
      <Card style={{ marginBottom: '24px' }}>
        <Space style={{ marginBottom: '16px', width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button
              type={activeView === 'subscriptions' ? 'primary' : 'default'}
              onClick={() => setActiveView('subscriptions')}
            >
              Abonnements ({subscriptions.length})
            </Button>
            <Button
              type={activeView === 'plans' ? 'primary' : 'default'}
              onClick={() => setActiveView('plans')}
            >
              Plans ({plans.length})
            </Button>
          </Space>
          {activeView === 'plans' && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreatePlan}
            >
              Nouveau Plan
            </Button>
          )}
        </Space>

        {/* Filtres */}
        <Space style={{ width: '100%' }} wrap>
          <Input
            placeholder="Rechercher..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          {activeView === 'subscriptions' && (
            <>
              <Select
                value={statusFilter}
                onChange={setStatusFilter}
                style={{ width: 150 }}
              >
                <Option value="all">Tous les statuts</Option>
                <Option value="active">Actifs</Option>
                <Option value="trialing">En essai</Option>
                <Option value="past_due">En retard</Option>
                <Option value="canceled">Annulés</Option>
              </Select>
              <Select
                value={planFilter}
                onChange={setPlanFilter}
                style={{ width: 150 }}
              >
                <Option value="all">Tous les plans</Option>
                {plans.map((plan) => (
                  <Option key={plan.id} value={plan.id}>
                    {plan.name}
                  </Option>
                ))}
              </Select>
            </>
          )}
        </Space>
      </Card>

      {/* Table */}
      <Card>
        {activeView === 'subscriptions' ? (
          <Table
            columns={subscriptionColumns}
            dataSource={filteredSubscriptions}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `Total: ${total} abonnements`,
            }}
            scroll={{ x: 1000 }}
          />
        ) : (
          <Table
            columns={planColumns}
            dataSource={filteredPlans}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showTotal: (total) => `Total: ${total} plans`,
            }}
            scroll={{ x: 1000 }}
          />
        )}
      </Card>

      {/* Modals */}
      <SubscriptionFormModal
        visible={formModalVisible}
        onCancel={() => setFormModalVisible(false)}
        onSave={handleSaveForm}
        plan={selectedPlan}
        mode={modalMode}
      />

      <SubscriptionDetailsModal
        visible={detailsModalVisible}
        onCancel={() => setDetailsModalVisible(false)}
        subscription={selectedSubscription}
        onRefresh={fetchData}
      />
    </div>
  );
};

export default AdminSubscriptionsManager;
