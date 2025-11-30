import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Button, Space, Typography, Table, Tag, Modal, Form,
  Input, Select, Tabs, Statistic, message
} from 'antd';
import {
  MailOutlined, SendOutlined, FileTextOutlined, ClockCircleOutlined,
  BarChartOutlined, PlusOutlined, EditOutlined, DeleteOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;

/**
 * EmailCampaigns - Système d'email marketing et automation
 */
const EmailCampaigns = () => {
  const [loading, setLoading] = useState(false);
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchCampaigns();
    fetchTemplates();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/emails/campaigns');
      setCampaigns(response.data.campaigns || []);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/api/emails/templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const handleCreateCampaign = async (values) => {
    try {
      await api.post('/api/emails/campaigns', values);
      message.success('Campagne créée');
      setModalVisible(false);
      form.resetFields();
      fetchCampaigns();
    } catch (error) {
      message.error('Erreur lors de la création');
    }
  };

  const columns = [
    { title: 'Nom', dataIndex: 'name', key: 'name' },
    {
      title: 'Statut',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={status === 'sent' ? 'success' : 'processing'}>{status}</Tag>
    },
    { title: 'Destinataires', dataIndex: 'recipients_count', key: 'recipients' },
    { title: 'Envoyés', dataIndex: 'sent_count', key: 'sent' },
    { title: 'Ouverts', dataIndex: 'opened_count', key: 'opened' },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<SendOutlined />}>Envoyer</Button>
          <Button size="small" icon={<EditOutlined />}>Modifier</Button>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={2}><MailOutlined /> Email Marketing</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          Nouvelle Campagne
        </Button>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Campagnes" value={campaigns.length} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Emails envoyés" value={1234} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Taux d'ouverture" value={45.2} suffix="%" /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Taux de clic" value={12.8} suffix="%" /></Card>
        </Col>
      </Row>

      <Card>
        <Tabs defaultActiveKey="campaigns">
          <TabPane tab="Campagnes" key="campaigns">
            <Table columns={columns} dataSource={campaigns} rowKey="id" />
          </TabPane>
          <TabPane tab="Templates" key="templates">
            <Row gutter={[16, 16]}>
              {templates.map(template => (
                <Col span={8} key={template.id}>
                  <Card title={template.name} extra={<Button size="small">Utiliser</Button>}>
                    <Text type="secondary">{template.description}</Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </TabPane>
        </Tabs>
      </Card>

      <Modal
        title="Nouvelle Campagne Email"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateCampaign}>
          <Form.Item name="name" label="Nom" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="subject" label="Sujet" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="template_id" label="Template">
            <Select>
              {templates.map(t => (
                <Select.Option key={t.id} value={t.id}>{t.name}</Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="recipients" label="Destinataires">
            <Select mode="multiple">
              <Select.Option value="all_users">Tous les utilisateurs</Select.Option>
              <Select.Option value="merchants">Marchands</Select.Option>
              <Select.Option value="influencers">Influenceurs</Select.Option>
            </Select>
          </Form.Item>
          <Button type="primary" htmlType="submit" block>Créer</Button>
        </Form>
      </Modal>
    </div>
  );
};

export default EmailCampaigns;
