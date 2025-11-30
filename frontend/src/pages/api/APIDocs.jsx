import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Button, Space, Typography, Table, Tag, Tabs, Input,
  Modal, Form, message, Descriptions, Divider, Alert, Switch
} from 'antd';
import {
  ApiOutlined, KeyOutlined, FileTextOutlined, CopyOutlined,
  PlusOutlined, DeleteOutlined, CodeOutlined, LockOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

/**
 * APIDocs - Documentation API publique + gestion des clés API
 */
const APIDocs = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const fetchAPIKeys = async () => {
    try {
      const response = await api.get('/api/v1/keys');
      setApiKeys(response.data.keys || []);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleCreateKey = async (values) => {
    try {
      const response = await api.post('/api/v1/keys', values);
      message.success('Clé API créée');
      setModalVisible(false);
      form.resetFields();
      
      // Afficher la clé une seule fois
      Modal.info({
        title: 'Votre clé API',
        content: (
          <div>
            <Alert type="warning" message="Copiez cette clé maintenant, elle ne sera plus affichée" />
            <Input.Password
              value={response.data.api_key}
              readOnly
              addonAfter={
                <Button
                  type="link"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(response.data.api_key);
                    message.success('Clé copiée');
                  }}
                />
              }
            />
          </div>
        )
      });
      
      fetchAPIKeys();
    } catch (error) {
      message.error('Erreur lors de la création');
    }
  };

  const handleDeleteKey = async (keyId) => {
    try {
      await api.delete(`/api/v1/keys/${keyId}`);
      message.success('Clé supprimée');
      fetchAPIKeys();
    } catch (error) {
      message.error('Erreur lors de la suppression');
    }
  };

  const columns = [
    { title: 'Nom', dataIndex: 'name', key: 'name' },
    {
      title: 'Clé',
      dataIndex: 'key_preview',
      key: 'key',
      render: (preview) => <Text code>{preview}...</Text>
    },
    {
      title: 'Statut',
      dataIndex: 'active',
      key: 'active',
      render: (active) => <Tag color={active ? 'success' : 'default'}>{active ? 'Active' : 'Inactive'}</Tag>
    },
    { title: 'Dernière utilisation', dataIndex: 'last_used', key: 'last_used' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button size="small" danger icon={<DeleteOutlined />} onClick={() => handleDeleteKey(record.id)}>
          Supprimer
        </Button>
      )
    }
  ];

  const endpoints = [
    {
      method: 'GET',
      path: '/api/v1/products',
      description: 'Liste des produits',
      params: 'page, limit, search'
    },
    {
      method: 'POST',
      path: '/api/v1/products',
      description: 'Créer un produit',
      params: 'name, price, description'
    },
    {
      method: 'GET',
      path: '/api/v1/campaigns',
      description: 'Liste des campagnes',
      params: 'page, limit'
    },
    {
      method: 'GET',
      path: '/api/v1/statistics',
      description: 'Statistiques globales',
      params: 'start_date, end_date'
    }
  ];

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <Title level={2}><ApiOutlined /> API Documentation</Title>

      <Tabs defaultActiveKey="docs">
        <TabPane tab={<><FileTextOutlined /> Documentation</>} key="docs">
          <Card>
            <Title level={3}>Authentification</Title>
            <Paragraph>
              Toutes les requêtes API nécessitent une clé API dans le header:
            </Paragraph>
            <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
              {`Authorization: Bearer YOUR_API_KEY`}
            </pre>

            <Divider />

            <Title level={3}>Endpoints</Title>
            {endpoints.map((endpoint, index) => (
              <Card key={index} size="small" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space>
                    <Tag color={endpoint.method === 'GET' ? 'blue' : 'green'}>{endpoint.method}</Tag>
                    <Text code>{endpoint.path}</Text>
                  </Space>
                  <Text>{endpoint.description}</Text>
                  {endpoint.params && (
                    <Text type="secondary">Paramètres: {endpoint.params}</Text>
                  )}
                </Space>
              </Card>
            ))}

            <Divider />

            <Title level={3}>Exemple de Requête</Title>
            <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
              {`curl -X GET "https://api.getyourshare.com/api/v1/products" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`}
            </pre>

            <Title level={3}>Rate Limiting</Title>
            <Paragraph>
              <ul>
                <li>1000 requêtes par heure par clé API</li>
                <li>Headers de réponse incluent: X-RateLimit-Limit, X-RateLimit-Remaining</li>
              </ul>
            </Paragraph>
          </Card>
        </TabPane>

        <TabPane tab={<><KeyOutlined /> Clés API</>} key="keys">
          <Card
            extra={
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
                Nouvelle Clé
              </Button>
            }
          >
            <Table columns={columns} dataSource={apiKeys} rowKey="id" />
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title="Créer une Clé API"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateKey}>
          <Form.Item name="name" label="Nom" rules={[{ required: true }]}>
            <Input placeholder="Production API Key" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Description de l'utilisation" />
          </Form.Item>
          <Form.Item name="permissions" label="Permissions">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Lecture</Text>
                <Switch defaultChecked />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Écriture</Text>
                <Switch />
              </div>
            </Space>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Créer</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default APIDocs;
