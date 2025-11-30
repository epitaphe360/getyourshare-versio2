import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Form, Input, Button, Select, Space, Typography, message,
  Divider, Switch, Upload, ColorPicker, Tabs, Table, Tag, Modal
} from 'antd';
import {
  SettingOutlined, MailOutlined, SaveOutlined, UploadOutlined,
  BgColorsOutlined, LockOutlined, UserOutlined, TeamOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

/**
 * AdvancedPlatformSettings - Configuration avancée SMTP, permissions, branding
 */
const AdvancedPlatformSettings = () => {
  const [loading, setLoading] = useState(false);
  const [smtpForm] = Form.useForm();
  const [brandingForm] = Form.useForm();
  const [settings, setSettings] = useState({});

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/settings/platform');
      setSettings(response.data.settings || {});
      smtpForm.setFieldsValue(response.data.settings?.smtp || {});
      brandingForm.setFieldsValue(response.data.settings?.branding || {});
    } catch (error) {
      console.error('Erreur chargement paramètres:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSMTPSave = async (values) => {
    try {
      await api.put('/api/settings/smtp', { smtp_config: values });
      message.success('Configuration SMTP sauvegardée');
    } catch (error) {
      message.error('Erreur lors de la sauvegarde');
    }
  };

  const handleBrandingSave = async (values) => {
    try {
      await api.put('/api/settings/branding', { branding: values });
      message.success('Personnalisation sauvegardée');
    } catch (error) {
      message.error('Erreur lors de la sauvegarde');
    }
  };

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      <Title level={2}><SettingOutlined /> Paramètres Avancés</Title>

      <Tabs defaultActiveKey="smtp">
        <TabPane tab={<><MailOutlined /> SMTP</>} key="smtp">
          <Card>
            <Form form={smtpForm} layout="vertical" onFinish={handleSMTPSave}>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="host" label="Serveur SMTP" rules={[{ required: true }]}>
                    <Input placeholder="smtp.gmail.com" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="port" label="Port" rules={[{ required: true }]}>
                    <Input placeholder="587" />
                  </Form.Item>
                </Col>
                <Col span={6}>
                  <Form.Item name="encryption" label="Chiffrement">
                    <Select>
                      <Select.Option value="tls">TLS</Select.Option>
                      <Select.Option value="ssl">SSL</Select.Option>
                      <Select.Option value="none">Aucun</Select.Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item name="username" label="Nom d'utilisateur">
                    <Input />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="password" label="Mot de passe">
                    <Input.Password />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="from_email" label="Email expéditeur">
                <Input placeholder="noreply@getyourshare.com" />
              </Form.Item>
              <Form.Item name="from_name" label="Nom expéditeur">
                <Input placeholder="GetYourShare" />
              </Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                Sauvegarder
              </Button>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab={<><BgColorsOutlined /> Branding</>} key="branding">
          <Card>
            <Form form={brandingForm} layout="vertical" onFinish={handleBrandingSave}>
              <Form.Item name="platform_name" label="Nom de la plateforme">
                <Input placeholder="GetYourShare" />
              </Form.Item>
              <Form.Item name="tagline" label="Slogan">
                <Input placeholder="Votre plateforme d'affiliation" />
              </Form.Item>
              <Row gutter={16}>
                <Col span={8}>
                  <Form.Item name="primary_color" label="Couleur primaire">
                    <Input type="color" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="secondary_color" label="Couleur secondaire">
                    <Input type="color" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="accent_color" label="Couleur accent">
                    <Input type="color" />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="logo" label="Logo">
                <Upload>
                  <Button icon={<UploadOutlined />}>Télécharger</Button>
                </Upload>
              </Form.Item>
              <Form.Item name="favicon" label="Favicon">
                <Upload>
                  <Button icon={<UploadOutlined />}>Télécharger</Button>
                </Upload>
              </Form.Item>
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                Sauvegarder
              </Button>
            </Form>
          </Card>
        </TabPane>

        <TabPane tab={<><LockOutlined /> Permissions</>} key="permissions">
          <Card title="Rôles et Permissions">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {['admin', 'merchant', 'influencer', 'commercial'].map(role => (
                <Card key={role} size="small" title={role.toUpperCase()}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {['products', 'campaigns', 'reports', 'users'].map(permission => (
                      <div key={permission} style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text>{permission}</Text>
                        <Switch defaultChecked={role === 'admin'} />
                      </div>
                    ))}
                  </Space>
                </Card>
              ))}
            </Space>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default AdvancedPlatformSettings;
