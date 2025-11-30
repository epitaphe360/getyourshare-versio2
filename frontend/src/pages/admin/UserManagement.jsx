import React, { useState, useEffect } from 'react';
import {
  Table, Button, Input, Select, Tag, Space, Card, Statistic, Row, Col,
  Modal, message, Dropdown, Menu, Avatar, Tooltip, Badge, Drawer
} from 'antd';
import {
  UserOutlined, SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined,
  LockOutlined, UnlockOutlined, MailOutlined, PhoneOutlined, CalendarOutlined,
  CheckCircleOutlined, CloseCircleOutlined, MoreOutlined, EyeOutlined,
  TeamOutlined, ShopOutlined, TrophyOutlined, DollarOutlined, CrownOutlined
} from '@ant-design/icons';
import api from '../../utils/api';
import UserFormModal from '../../components/admin/UserFormModal';
import UserDetailsDrawer from '../../components/admin/UserDetailsDrawer';

const { Option } = Select;
const { confirm } = Modal;

/**
 * PHASE 2A - GESTION AVANCÉE DES UTILISATEURS
 * Page complète de gestion des utilisateurs avec CRUD, statistiques, filtres avancés
 */
const UserManagement = () => {
  // ============================================
  // STATE MANAGEMENT
  // ============================================
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({
    totalUsers: 0,
    merchants: 0,
    influencers: 0,
    commercials: 0,
    admins: 0,
    activeUsers: 0,
    suspendedUsers: 0,
    newUsersThisMonth: 0
  });

  // Filtres et recherche
  const [searchText, setSearchText] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [subscriptionFilter, setSubscriptionFilter] = useState('all');

  // Modals & Drawers
  const [formModalVisible, setFormModalVisible] = useState(false);
  const [detailsDrawerVisible, setDetailsDrawerVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [modalMode, setModalMode] = useState('create'); // 'create' ou 'edit'

  // Pagination
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // ============================================
  // DATA FETCHING
  // ============================================

  useEffect(() => {
    fetchData();
  }, [roleFilter, statusFilter, subscriptionFilter, pagination.current]);

  const fetchData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchUsers(),
        fetchStats()
      ]);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
      message.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const params = {
        page: pagination.current,
        limit: pagination.pageSize
      };
      
      if (roleFilter !== 'all') params.role = roleFilter;
      if (statusFilter !== 'all') params.status = statusFilter;
      if (subscriptionFilter !== 'all') params.subscription = subscriptionFilter;

      const response = await api.get('/api/admin/users', { params });
      
      if (response.data.success) {
        setUsers(response.data.users || []);
        setPagination(prev => ({
          ...prev,
          total: response.data.total || 0
        }));
      }
    } catch (error) {
      console.error('Erreur lors du chargement des utilisateurs:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/admin/users/stats');
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des stats:', error);
    }
  };

  // ============================================
  // ACTIONS HANDLERS
  // ============================================

  const handleCreateUser = () => {
    setSelectedUser(null);
    setModalMode('create');
    setFormModalVisible(true);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setModalMode('edit');
    setFormModalVisible(true);
  };

  const handleViewDetails = (user) => {
    setSelectedUser(user);
    setDetailsDrawerVisible(true);
  };

  const handleDeleteUser = (userId, userName) => {
    confirm({
      title: `Supprimer l'utilisateur ${userName} ?`,
      content: 'Cette action est irréversible. Toutes les données associées seront supprimées.',
      okText: 'Supprimer',
      okType: 'danger',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await api.delete(`/api/admin/users/${userId}`);
          message.success('Utilisateur supprimé avec succès');
          fetchData();
        } catch (error) {
          console.error('Erreur lors de la suppression:', error);
          message.error(error.response?.data?.detail || 'Erreur lors de la suppression');
        }
      }
    });
  };

  const handleSuspendUser = async (userId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'suspended' ? 'active' : 'suspended';
      await api.patch(`/api/admin/users/${userId}/status`, { status: newStatus });
      message.success(`Utilisateur ${newStatus === 'suspended' ? 'suspendu' : 'réactivé'} avec succès`);
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de la modification du statut');
    }
  };

  const handleResetPassword = (userId, userEmail) => {
    confirm({
      title: 'Réinitialiser le mot de passe ?',
      content: `Un email de réinitialisation sera envoyé à ${userEmail}`,
      okText: 'Envoyer',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await api.post(`/api/admin/users/${userId}/reset-password`);
          message.success('Email de réinitialisation envoyé');
        } catch (error) {
          console.error('Erreur:', error);
          message.error('Erreur lors de l\'envoi');
        }
      }
    });
  };

  const handleSaveForm = async (formData) => {
    try {
      if (modalMode === 'create') {
        await api.post('/api/admin/users', formData);
        message.success('Utilisateur créé avec succès');
      } else {
        await api.put(`/api/admin/users/${selectedUser.id}`, formData);
        message.success('Utilisateur modifié avec succès');
      }
      setFormModalVisible(false);
      fetchData();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la sauvegarde');
      throw error;
    }
  };

  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
  };

  // ============================================
  // FILTRAGE DES DONNÉES
  // ============================================

  const filteredUsers = users.filter((user) => {
    if (searchText === '') return true;
    
    const searchLower = searchText.toLowerCase();
    return (
      user.email?.toLowerCase().includes(searchLower) ||
      user.first_name?.toLowerCase().includes(searchLower) ||
      user.last_name?.toLowerCase().includes(searchLower) ||
      user.company?.toLowerCase().includes(searchLower)
    );
  });

  // ============================================
  // RENDER HELPERS
  // ============================================

  const getRoleIcon = (role) => {
    const icons = {
      admin: <CrownOutlined style={{ color: '#ff4d4f' }} />,
      merchant: <ShopOutlined style={{ color: '#1890ff' }} />,
      influencer: <TrophyOutlined style={{ color: '#722ed1' }} />,
      commercial: <TeamOutlined style={{ color: '#52c41a' }} />,
      sales_rep: <DollarOutlined style={{ color: '#faad14' }} />
    };
    return icons[role] || <UserOutlined />;
  };

  const getRoleTag = (role) => {
    const config = {
      admin: { color: 'red', text: 'Admin' },
      merchant: { color: 'blue', text: 'Marchand' },
      influencer: { color: 'purple', text: 'Influenceur' },
      commercial: { color: 'green', text: 'Commercial' },
      sales_rep: { color: 'orange', text: 'Représentant' },
      user: { color: 'default', text: 'Utilisateur' }
    };
    const roleConfig = config[role] || config.user;
    return (
      <Tag color={roleConfig.color} icon={getRoleIcon(role)}>
        {roleConfig.text}
      </Tag>
    );
  };

  const getStatusTag = (status) => {
    const config = {
      active: { color: 'success', icon: <CheckCircleOutlined />, text: 'Actif' },
      suspended: { color: 'error', icon: <CloseCircleOutlined />, text: 'Suspendu' },
      pending: { color: 'warning', icon: <CalendarOutlined />, text: 'En attente' }
    };
    const statusConfig = config[status] || config.active;
    return (
      <Tag color={statusConfig.color} icon={statusConfig.icon}>
        {statusConfig.text}
      </Tag>
    );
  };

  const getActionsMenu = (user) => (
    <Menu>
      <Menu.Item
        key="view"
        icon={<EyeOutlined />}
        onClick={() => handleViewDetails(user)}
      >
        Voir détails
      </Menu.Item>
      <Menu.Item
        key="edit"
        icon={<EditOutlined />}
        onClick={() => handleEditUser(user)}
      >
        Modifier
      </Menu.Item>
      <Menu.Item
        key="reset"
        icon={<LockOutlined />}
        onClick={() => handleResetPassword(user.id, user.email)}
      >
        Réinitialiser mot de passe
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item
        key="suspend"
        icon={user.status === 'suspended' ? <UnlockOutlined /> : <LockOutlined />}
        onClick={() => handleSuspendUser(user.id, user.status)}
      >
        {user.status === 'suspended' ? 'Réactiver' : 'Suspendre'}
      </Menu.Item>
      <Menu.Item
        key="delete"
        icon={<DeleteOutlined />}
        danger
        onClick={() => handleDeleteUser(user.id, user.email)}
      >
        Supprimer
      </Menu.Item>
    </Menu>
  );

  // ============================================
  // COLUMNS DEFINITION
  // ============================================

  const columns = [
    {
      title: 'Utilisateur',
      key: 'user',
      fixed: 'left',
      width: 250,
      render: (_, user) => (
        <Space>
          <Avatar
            size={40}
            icon={<UserOutlined />}
            src={user.avatar}
            style={{ backgroundColor: user.avatar ? 'transparent' : '#1890ff' }}
          />
          <div>
            <div style={{ fontWeight: 500 }}>
              {user.first_name && user.last_name
                ? `${user.first_name} ${user.last_name}`
                : user.email}
            </div>
            <div style={{ fontSize: '12px', color: '#888' }}>
              <MailOutlined /> {user.email}
            </div>
            {user.phone && (
              <div style={{ fontSize: '12px', color: '#888' }}>
                <PhoneOutlined /> {user.phone}
              </div>
            )}
          </div>
        </Space>
      )
    },
    {
      title: 'Rôle',
      dataIndex: 'role',
      key: 'role',
      width: 130,
      render: (role) => getRoleTag(role)
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => getStatusTag(status || 'active')
    },
    {
      title: 'Abonnement',
      key: 'subscription',
      width: 150,
      render: (_, user) => {
        if (user.subscription_plan) {
          return (
            <Tooltip title={user.subscription_status}>
              <Tag color="blue">{user.subscription_plan}</Tag>
            </Tooltip>
          );
        }
        return <Tag>Gratuit</Tag>;
      }
    },
    {
      title: 'Entreprise',
      dataIndex: 'company',
      key: 'company',
      width: 150,
      render: (company) => company || <span style={{ color: '#ccc' }}>-</span>
    },
    {
      title: 'Inscription',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date) => date ? new Date(date).toLocaleDateString('fr-FR') : '-'
    },
    {
      title: 'Dernière connexion',
      dataIndex: 'last_login',
      key: 'last_login',
      width: 150,
      render: (date) => {
        if (!date) return <span style={{ color: '#ccc' }}>Jamais</span>;
        const lastLogin = new Date(date);
        const now = new Date();
        const diffDays = Math.floor((now - lastLogin) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return <Badge status="success" text="Aujourd'hui" />;
        if (diffDays === 1) return <Badge status="processing" text="Hier" />;
        if (diffDays < 7) return <Badge status="default" text={`Il y a ${diffDays}j`} />;
        return <span style={{ color: '#888' }}>{lastLogin.toLocaleDateString('fr-FR')}</span>;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 100,
      render: (_, user) => (
        <Space>
          <Tooltip title="Voir détails">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(user)}
            />
          </Tooltip>
          <Dropdown overlay={getActionsMenu(user)} trigger={['click']}>
            <Button type="text" size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      )
    }
  ];

  // ============================================
  // RENDER
  // ============================================

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          Gestion des Utilisateurs
        </h1>
        <p style={{ color: '#888', marginTop: '8px' }}>
          Gérez tous les utilisateurs de la plateforme
        </p>
      </div>

      {/* Statistiques */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Utilisateurs"
              value={stats.totalUsers}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Marchands"
              value={stats.merchants}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Influenceurs"
              value={stats.influencers}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Commerciaux"
              value={stats.commercials}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtres et Actions */}
      <Card style={{ marginBottom: '24px' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Space wrap>
            <Input
              placeholder="Rechercher par nom, email..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
              allowClear
            />
            <Select
              value={roleFilter}
              onChange={setRoleFilter}
              style={{ width: 150 }}
            >
              <Option value="all">Tous les rôles</Option>
              <Option value="admin">Admin</Option>
              <Option value="merchant">Marchand</Option>
              <Option value="influencer">Influenceur</Option>
              <Option value="commercial">Commercial</Option>
              <Option value="sales_rep">Représentant</Option>
            </Select>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 150 }}
            >
              <Option value="all">Tous les statuts</Option>
              <Option value="active">Actif</Option>
              <Option value="suspended">Suspendu</Option>
              <Option value="pending">En attente</Option>
            </Select>
            <Select
              value={subscriptionFilter}
              onChange={setSubscriptionFilter}
              style={{ width: 150 }}
            >
              <Option value="all">Tous abonnements</Option>
              <Option value="free">Gratuit</Option>
              <Option value="active">Abonné</Option>
              <Option value="trial">Essai</Option>
            </Select>
          </Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateUser}
          >
            Nouvel utilisateur
          </Button>
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredUsers}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} utilisateurs`,
            pageSizeOptions: ['10', '20', '50', '100']
          }}
          onChange={handleTableChange}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* Modals & Drawers */}
      <UserFormModal
        visible={formModalVisible}
        onCancel={() => setFormModalVisible(false)}
        onSave={handleSaveForm}
        user={selectedUser}
        mode={modalMode}
      />

      <UserDetailsDrawer
        visible={detailsDrawerVisible}
        onClose={() => setDetailsDrawerVisible(false)}
        user={selectedUser}
        onRefresh={fetchData}
      />
    </div>
  );
};

export default UserManagement;
