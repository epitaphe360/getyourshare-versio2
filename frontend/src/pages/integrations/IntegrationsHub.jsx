import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Button, Space, Typography, Steps, Form, Input, Select,
  Table, Tag, Switch, message, Modal, Spin, Tabs, Divider, Alert, Progress
} from 'antd';
import {
  ShopOutlined, SyncOutlined, CheckCircleOutlined, LinkOutlined,
  SettingOutlined, ShoppingCartOutlined, ApiOutlined, CloudSyncOutlined,
  KeyOutlined, DatabaseOutlined, ImportOutlined, ExportOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Title, Text, Paragraph } = Typography;
const { Step } = Steps;
const { TabPane } = Tabs;
const { TextArea } = Input;

/**
 * IntegrationsHub - Hub d'intégrations Shopify/WooCommerce/API externes
 */
const IntegrationsHub = () => {
  const [loading, setLoading] = useState(false);
  const [integrations, setIntegrations] = useState([]);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [configModalVisible, setConfigModalVisible] = useState(false);
  const [syncModalVisible, setSyncModalVisible] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [form] = Form.useForm();

  const availableIntegrations = [
    {
      id: 'shopify',
      name: 'Shopify',
      icon: <ShopOutlined />,
      color: '#96bf48',
      description: 'Synchronisez vos produits depuis votre boutique Shopify',
      features: ['Import produits', 'Sync commandes', 'Webhooks', 'Stock temps réel'],
      oauth: true
    },
    {
      id: 'woocommerce',
      name: 'WooCommerce',
      icon: <ShoppingCartOutlined />,
      color: '#96588a',
      description: 'Connectez votre boutique WooCommerce',
      features: ['Import produits', 'Sync automatique', 'API REST', 'Webhooks'],
      oauth: false
    },
    {
      id: 'api',
      name: 'API Personnalisée',
      icon: <ApiOutlined />,
      color: '#1890ff',
      description: 'Connectez votre propre API ou système',
      features: ['Endpoints custom', 'Authentification', 'Webhooks', 'Format flexible'],
      oauth: false
    }
  ];

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/integrations');
      setIntegrations(response.data.integrations || []);
    } catch (error) {
      console.error('Erreur chargement intégrations:', error);
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (integrationType) => {
    const integration = availableIntegrations.find(i => i.id === integrationType);
    
    if (integration.oauth) {
      // OAuth flow (Shopify)
      try {
        const response = await api.post('/api/integrations/oauth/init', {
          type: integrationType
        });
        
        if (response.data.auth_url) {
          // Rediriger vers la page OAuth
          window.location.href = response.data.auth_url;
        }
      } catch (error) {
        console.error('Erreur OAuth:', error);
        message.error('Erreur lors de l\'authentification');
      }
    } else {
      // Configuration manuelle
      setSelectedIntegration(integration);
      setConfigModalVisible(true);
    }
  };

  const handleConfigSubmit = async (values) => {
    try {
      const response = await api.post('/api/integrations/connect', {
        type: selectedIntegration.id,
        config: values
      });
      
      if (response.data.success) {
        message.success('Intégration configurée avec succès');
        setConfigModalVisible(false);
        form.resetFields();
        fetchIntegrations();
      }
    } catch (error) {
      console.error('Erreur configuration:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la configuration');
    }
  };

  const handleTestConnection = async (integrationId) => {
    try {
      const response = await api.post(`/api/integrations/${integrationId}/test`);
      if (response.data.success) {
        message.success('Connexion testée avec succès');
      }
    } catch (error) {
      console.error('Erreur test connexion:', error);
      message.error('Échec du test de connexion');
    }
  };

  const handleSync = async (integrationId) => {
    setSyncModalVisible(true);
    setSyncProgress(0);
    
    try {
      // Simuler progression
      const interval = setInterval(() => {
        setSyncProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return prev;
          }
          return prev + 10;
        });
      }, 500);
      
      const response = await api.post(`/api/integrations/${integrationId}/sync`);
      
      clearInterval(interval);
      setSyncProgress(100);
      
      setTimeout(() => {
        setSyncModalVisible(false);
        message.success(`${response.data.synced_count} produits synchronisés`);
        fetchIntegrations();
      }, 1000);
    } catch (error) {
      console.error('Erreur synchronisation:', error);
      setSyncModalVisible(false);
      message.error('Erreur lors de la synchronisation');
    }
  };

  const handleDisconnect = async (integrationId) => {
    Modal.confirm({
      title: 'Déconnecter l\'intégration',
      content: 'Êtes-vous sûr de vouloir déconnecter cette intégration ?',
      okText: 'Déconnecter',
      okType: 'danger',
      cancelText: 'Annuler',
      onOk: async () => {
        try {
          await api.delete(`/api/integrations/${integrationId}`);
          message.success('Intégration déconnectée');
          fetchIntegrations();
        } catch (error) {
          console.error('Erreur déconnexion:', error);
          message.error('Erreur lors de la déconnexion');
        }
      }
    });
  };

  const handleToggleSync = async (integrationId, enabled) => {
    try {
      await api.patch(`/api/integrations/${integrationId}/auto-sync`, {
        enabled
      });
      message.success(`Synchronisation automatique ${enabled ? 'activée' : 'désactivée'}`);
      fetchIntegrations();
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors de la mise à jour');
    }
  };

  const columns = [
    {
      title: 'Intégration',
      dataIndex: 'type',
      key: 'type',
      render: (type) => {
        const integration = availableIntegrations.find(i => i.id === type);
        return (
          <Space>
            {integration?.icon}
            <Text strong>{integration?.name}</Text>
          </Space>
        );
      }
    },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'connected' ? 'success' : status === 'error' ? 'error' : 'default'}>
          {status === 'connected' ? 'Connecté' : status === 'error' ? 'Erreur' : 'Déconnecté'}
        </Tag>
      )
    },
    {
      title: 'Produits synchronisés',
      dataIndex: 'products_count',
      key: 'products_count',
      render: (count) => count?.toLocaleString() || 0
    },
    {
      title: 'Dernière sync',
      dataIndex: 'last_sync',
      key: 'last_sync',
      render: (date) => date ? new Date(date).toLocaleString('fr-FR') : 'Jamais'
    },
    {
      title: 'Sync auto',
      dataIndex: 'auto_sync',
      key: 'auto_sync',
      render: (enabled, record) => (
        <Switch
          checked={enabled}
          onChange={(checked) => handleToggleSync(record.id, checked)}
        />
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button
            size="small"
            icon={<SyncOutlined />}
            onClick={() => handleSync(record.id)}
          >
            Synchroniser
          </Button>
          <Button
            size="small"
            icon={<CheckCircleOutlined />}
            onClick={() => handleTestConnection(record.id)}
          >
            Tester
          </Button>
          <Button
            size="small"
            icon={<SettingOutlined />}
            onClick={() => {
              // TODO: Modal de configuration
            }}
          >
            Configurer
          </Button>
          <Button
            size="small"
            danger
            onClick={() => handleDisconnect(record.id)}
          >
            Déconnecter
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ margin: 0 }}>
          <CloudSyncOutlined /> Hub d'Intégrations
        </Title>
        <Text type="secondary">
          Connectez vos boutiques et plateformes externes
        </Text>
      </div>

      {/* Intégrations disponibles */}
      <Card title="Intégrations Disponibles" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          {availableIntegrations.map(integration => {
            const connected = integrations.find(i => i.type === integration.id && i.status === 'connected');
            
            return (
              <Col xs={24} md={8} key={integration.id}>
                <Card
                  hoverable
                  style={{
                    borderLeft: `4px solid ${integration.color}`,
                    height: '100%'
                  }}
                >
                  <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <Space>
                        <div style={{
                          fontSize: 40,
                          color: integration.color
                        }}>
                          {integration.icon}
                        </div>
                        <div>
                          <Title level={4} style={{ margin: 0 }}>
                            {integration.name}
                          </Title>
                          {connected && <Tag color="success">Connecté</Tag>}
                        </div>
                      </Space>
                    </div>
                    
                    <Paragraph type="secondary">
                      {integration.description}
                    </Paragraph>
                    
                    <div>
                      <Text strong>Fonctionnalités:</Text>
                      <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                        {integration.features.map((feature, index) => (
                          <li key={index}>
                            <Text type="secondary">{feature}</Text>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <Button
                      type={connected ? 'default' : 'primary'}
                      block
                      icon={connected ? <CheckCircleOutlined /> : <LinkOutlined />}
                      onClick={() => !connected && handleConnect(integration.id)}
                      disabled={connected}
                    >
                      {connected ? 'Déjà connecté' : 'Connecter'}
                    </Button>
                  </Space>
                </Card>
              </Col>
            );
          })}
        </Row>
      </Card>

      {/* Intégrations actives */}
      <Card title="Intégrations Actives">
        <Spin spinning={loading}>
          {integrations.length === 0 ? (
            <Alert
              message="Aucune intégration"
              description="Connectez votre première intégration pour commencer à synchroniser vos produits."
              type="info"
              showIcon
            />
          ) : (
            <Table
              columns={columns}
              dataSource={integrations}
              rowKey="id"
              pagination={false}
            />
          )}
        </Spin>
      </Card>

      {/* Modal Configuration */}
      <Modal
        title={`Configurer ${selectedIntegration?.name}`}
        open={configModalVisible}
        onCancel={() => {
          setConfigModalVisible(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        {selectedIntegration && (
          <Form
            form={form}
            layout="vertical"
            onFinish={handleConfigSubmit}
          >
            {selectedIntegration.id === 'woocommerce' && (
              <>
                <Form.Item
                  name="store_url"
                  label="URL de la boutique"
                  rules={[{ required: true, message: 'Veuillez entrer l\'URL' }]}
                >
                  <Input placeholder="https://votreboutique.com" prefix={<LinkOutlined />} />
                </Form.Item>
                <Form.Item
                  name="consumer_key"
                  label="Consumer Key"
                  rules={[{ required: true, message: 'Veuillez entrer la clé' }]}
                >
                  <Input placeholder="ck_..." prefix={<KeyOutlined />} />
                </Form.Item>
                <Form.Item
                  name="consumer_secret"
                  label="Consumer Secret"
                  rules={[{ required: true, message: 'Veuillez entrer le secret' }]}
                >
                  <Input.Password placeholder="cs_..." prefix={<KeyOutlined />} />
                </Form.Item>
              </>
            )}
            
            {selectedIntegration.id === 'api' && (
              <>
                <Form.Item
                  name="api_url"
                  label="URL de l'API"
                  rules={[{ required: true, message: 'Veuillez entrer l\'URL' }]}
                >
                  <Input placeholder="https://api.example.com" prefix={<ApiOutlined />} />
                </Form.Item>
                <Form.Item
                  name="api_key"
                  label="Clé API"
                  rules={[{ required: true, message: 'Veuillez entrer la clé' }]}
                >
                  <Input.Password placeholder="Votre clé API" prefix={<KeyOutlined />} />
                </Form.Item>
                <Form.Item
                  name="webhook_url"
                  label="URL Webhook (optionnel)"
                >
                  <Input placeholder="https://example.com/webhook" />
                </Form.Item>
              </>
            )}
            
            <Form.Item>
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button onClick={() => setConfigModalVisible(false)}>
                  Annuler
                </Button>
                <Button type="primary" htmlType="submit">
                  Connecter
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>

      {/* Modal Synchronisation */}
      <Modal
        title="Synchronisation en cours"
        open={syncModalVisible}
        footer={null}
        closable={false}
        centered
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Progress
            percent={syncProgress}
            status={syncProgress === 100 ? 'success' : 'active'}
          />
          <Text type="secondary">
            {syncProgress === 100 ? 'Synchronisation terminée' : 'Synchronisation des produits...'}
          </Text>
        </Space>
      </Modal>
    </div>
  );
};

export default IntegrationsHub;
