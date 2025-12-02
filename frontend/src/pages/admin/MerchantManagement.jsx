import React, { useState, useEffect, useCallback } from 'react';
import {
  Table, Button, Input, Select, Tag, Space, Card, Statistic, Row, Col,
  Modal, message, Badge, Drawer, Descriptions, Avatar, Tooltip,
  Switch, Progress, Typography, Divider
} from 'antd';
import {
  ShopOutlined, SearchOutlined, EyeOutlined, EditOutlined,
  DollarOutlined, TrophyOutlined, LineChartOutlined, UserOutlined,
  CheckCircleOutlined, CloseCircleOutlined, LockOutlined, UnlockOutlined,
  MailOutlined, PhoneOutlined, GlobalOutlined, CalendarOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Option } = Select;
const { Text, Title } = Typography;

/**
 * Page de gestion des annonceurs (merchants)
 * Admin only - Vue complète sur tous les marchands
 */
const MerchantManagement = () => {
  const [loading, setLoading] = useState(false);
  const [merchants, setMerchants] = useState([]);
  const [stats, setStats] = useState({
    totalMerchants: 0,
    activeMerchants: 0,
    totalRevenue: 0,
    totalProducts: 0,
    totalCampaigns: 0
  });

  // Filtres
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [subscriptionFilter, setSubscriptionFilter] = useState('all');

  // Drawer
  const [detailsDrawerVisible, setDetailsDrawerVisible] = useState(false);
  const [selectedMerchant, setSelectedMerchant] = useState(null);
  const [merchantDetails, setMerchantDetails] = useState(null);

  const fetchMerchants = useCallback(async (signal) => {
    try {
      const params = { role: 'merchant' };
      if (statusFilter && statusFilter !== 'all') params.status = statusFilter;
      if (subscriptionFilter && subscriptionFilter !== 'all') params.subscription = subscriptionFilter;
      if (searchText) params.search = searchText;

      const response = await api.get('/api/admin/users', { params, signal });
      if (response.data.success) {
        const merchantsData = response.data.users || [];
        // Ajouter des valeurs par défaut pour les compteurs
        const enrichedMerchants = merchantsData.map(m => ({
          ...m,
          products_count: m.products_count || 0,
          campaigns_count: m.campaigns_count || 0,
          total_revenue: m.total_revenue || 0
        }));
        setMerchants(enrichedMerchants);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur:', error);
        message.error('Erreur lors du chargement des annonceurs');
      }
    }
  }, [statusFilter, subscriptionFilter, searchText]);

  const fetchStats = useCallback(async (signal) => {
    try {
      const response = await api.get('/api/admin/merchants/stats', { signal });
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur:', error);
      }
    }
  }, []);

  const fetchData = useCallback(async (signal) => {
    setLoading(true);
    try {
      await Promise.all([
        fetchMerchants(signal),
        fetchStats(signal)
      ]);
    } catch (error) {
      if (error.name !== 'AbortError' && error.name !== 'CanceledError') {
        console.error('Erreur:', error);
        message.error('Erreur lors du chargement');
      }
    } finally {
      setLoading(false);
    }
  }, [fetchMerchants, fetchStats]);

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller.signal);
    return () => controller.abort();
  }, [fetchData]);

  const fetchMerchantDetails = async (merchantId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/admin/merchants/${merchantId}/details`);
      if (response.data.success) {
        setMerchantDetails(response.data.details);
      }
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors du chargement des détails');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (merchant) => {
    setSelectedMerchant(merchant);
    setDetailsDrawerVisible(true);
    await fetchMerchantDetails(merchant.id);
  };

  const handleToggleStatus = async (merchantId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'suspended' : 'active';
      await api.patch(`/api/admin/users/${merchantId}/status`, { status: newStatus });
      message.success(`Annonceur ${newStatus === 'suspended' ? 'suspendu' : 'réactivé'}`);
      fetchData();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de la modification');
    }
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

  const columns = [
    {
      title: 'Annonceur',
      key: 'merchant',
      fixed: 'left',
      width: 250,
      render: (_, merchant) => (
        <Space>
          <Avatar
            size={40}
            icon={<ShopOutlined />}
            style={{ backgroundColor: '#1890ff' }}
          />
          <div>
            <div style={{ fontWeight: 500 }}>
              {merchant.username || merchant.email.split('@')[0]}
            </div>
            <div style={{ fontSize: '12px', color: '#888' }}>
              <MailOutlined /> {merchant.email}
            </div>
          </div>
        </Space>
      )
    },
    {
      title: 'Contact',
      key: 'contact',
      width: 180,
      render: (_, merchant) => (
        <Space direction="vertical" size={0}>
          {merchant.first_name && (
            <Text>{`${merchant.first_name} ${merchant.last_name || ''}`}</Text>
          )}
          {merchant.phone && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              <PhoneOutlined /> {merchant.phone}
            </Text>
          )}
        </Space>
      )
    },
    {
      title: 'Abonnement',
      key: 'subscription',
      width: 150,
      render: (_, merchant) => {
        if (merchant.subscription_plan) {
          return <Tag color="blue">{merchant.subscription_plan}</Tag>;
        }
        return <Tag>Gratuit</Tag>;
      }
    },
    {
      title: 'Produits',
      dataIndex: 'products_count',
      key: 'products_count',
      width: 100,
      align: 'center',
      render: (count) => (
        <Badge
          count={count || 0}
          showZero
          style={{ backgroundColor: '#52c41a' }}
        />
      )
    },
    {
      title: 'Campagnes',
      dataIndex: 'campaigns_count',
      key: 'campaigns_count',
      width: 110,
      align: 'center',
      render: (count) => (
        <Badge
          count={count || 0}
          showZero
          style={{ backgroundColor: '#1890ff' }}
        />
      )
    },
    {
      title: 'CA généré',
      dataIndex: 'total_revenue',
      key: 'total_revenue',
      width: 130,
      render: (revenue) => {
        const value = revenue || 0;
        return (
          <Text strong style={{ color: '#52c41a' }}>
            {value.toLocaleString('fr-FR')} €
          </Text>
        );
      }
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => getStatusTag(status || 'active')
    },
    {
      title: 'Inscription',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date) => date ? new Date(date).toLocaleDateString('fr-FR') : '-'
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 150,
      render: (_, merchant) => (
        <Space>
          <Tooltip title="Voir détails">
            <Button
              type="text"
              size="small"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(merchant)}
            />
          </Tooltip>
          <Tooltip title={merchant.status === 'active' ? 'Suspendre' : 'Réactiver'}>
            <Switch
              size="small"
              checked={merchant.status === 'active'}
              onChange={() => handleToggleStatus(merchant.id, merchant.status)}
              checkedChildren={<UnlockOutlined />}
              unCheckedChildren={<LockOutlined />}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  const filteredData = merchants.filter((merchant) => {
    if (!searchText) return true;
    const search = searchText.toLowerCase();
    return (
      merchant.email?.toLowerCase().includes(search) ||
      merchant.company?.toLowerCase().includes(search) ||
      merchant.first_name?.toLowerCase().includes(search) ||
      merchant.last_name?.toLowerCase().includes(search)
    );
  });

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>Gestion des Annonceurs</Title>
        <Text type="secondary">
          Vue d'ensemble et gestion de tous les annonceurs de la plateforme
        </Text>
      </div>

      {/* Statistiques */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Annonceurs"
              value={stats.totalMerchants}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Actifs"
              value={stats.activeMerchants}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="CA Total"
              value={stats.totalRevenue}
              prefix={<DollarOutlined />}
              suffix="€"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Produits Total"
              value={stats.totalProducts}
              prefix={<LineChartOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filtres */}
      <Card style={{ marginBottom: '24px' }}>
        <Space wrap>
          <Input
            placeholder="Rechercher..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 150 }}
          >
            <Option value="all">Tous les statuts</Option>
            <Option value="active">Actifs</Option>
            <Option value="suspended">Suspendus</Option>
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
          </Select>
        </Space>
      </Card>

      {/* Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `Total: ${total} annonceurs`
          }}
        />
      </Card>

      {/* Drawer Détails */}
      <Drawer
        title="Détails de l'annonceur"
        placement="right"
        width={700}
        open={detailsDrawerVisible}
        onClose={() => {
          setDetailsDrawerVisible(false);
          setMerchantDetails(null);
        }}
      >
        {selectedMerchant && (
          <div>
            {/* Infos de base */}
            <Card style={{ marginBottom: 16 }}>
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div style={{ textAlign: 'center' }}>
                  <Avatar size={80} icon={<ShopOutlined />} style={{ backgroundColor: '#1890ff' }} />
                  <Title level={4} style={{ marginTop: 16 }}>
                    {selectedMerchant.company || selectedMerchant.email}
                  </Title>
                  {getStatusTag(selectedMerchant.status || 'active')}
                </div>

                <Descriptions column={1} bordered>
                  <Descriptions.Item label="Email">
                    {selectedMerchant.email}
                  </Descriptions.Item>
                  <Descriptions.Item label="Contact">
                    {selectedMerchant.first_name} {selectedMerchant.last_name}
                  </Descriptions.Item>
                  <Descriptions.Item label="Téléphone">
                    {selectedMerchant.phone || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="Abonnement">
                    {selectedMerchant.subscription_plan || 'Gratuit'}
                  </Descriptions.Item>
                  <Descriptions.Item label="Inscription">
                    {new Date(selectedMerchant.created_at).toLocaleDateString('fr-FR')}
                  </Descriptions.Item>
                </Descriptions>
              </Space>
            </Card>

            {/* Statistiques détaillées */}
            {merchantDetails && (
              <>
                <Title level={5}>Statistiques</Title>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="Produits"
                        value={merchantDetails.products_count}
                        prefix={<LineChartOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="Campagnes"
                        value={merchantDetails.campaigns_count}
                        prefix={<TrophyOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="Ventes"
                        value={merchantDetails.total_sales}
                        prefix={<DollarOutlined />}
                      />
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card size="small">
                      <Statistic
                        title="CA généré"
                        value={merchantDetails.total_revenue}
                        suffix="€"
                        prefix={<DollarOutlined />}
                      />
                    </Card>
                  </Col>
                </Row>

                <Divider />

                {/* Produits populaires */}
                {merchantDetails.top_products && merchantDetails.top_products.length > 0 && (
                  <>
                    <Title level={5}>Produits les plus vendus</Title>
                    <Card size="small" style={{ marginBottom: 16 }}>
                      {merchantDetails.top_products.map((product, index) => (
                        <div key={index} style={{ marginBottom: 12 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                            <Text strong>{product.name}</Text>
                            <Text>{product.sales} ventes</Text>
                          </div>
                          <Progress
                            percent={(product.sales / merchantDetails.top_products[0].sales) * 100}
                            showInfo={false}
                            strokeColor="#52c41a"
                          />
                        </div>
                      ))}
                    </Card>
                  </>
                )}

                {/* Influenceurs actifs */}
                {merchantDetails.active_influencers && merchantDetails.active_influencers.length > 0 && (
                  <>
                    <Title level={5}>Influenceurs actifs</Title>
                    <Card size="small">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {merchantDetails.active_influencers.map((influencer, index) => (
                          <div key={index} style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Space>
                              <Avatar size="small" icon={<UserOutlined />} />
                              <Text>{influencer.name}</Text>
                            </Space>
                            <Badge count={influencer.sales} style={{ backgroundColor: '#52c41a' }} />
                          </div>
                        ))}
                      </Space>
                    </Card>
                  </>
                )}
              </>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default MerchantManagement;
