import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, Switch, Space, Divider, message } from 'antd';
import { MailOutlined, PhoneOutlined, UserOutlined, LockOutlined } from '@ant-design/icons';

const { Option } = Select;

/**
 * Modal de création/édition d'utilisateur
 */
const UserFormModal = ({ visible, onCancel, onSave, user, mode }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      if (mode === 'edit' && user) {
        form.setFieldsValue({
          email: user.email,
          first_name: user.first_name,
          last_name: user.last_name,
          phone: user.phone,
          company: user.company,
          role: user.role,
          status: user.status || 'active',
        });
      } else {
        form.resetFields();
        form.setFieldsValue({
          role: 'user',
          status: 'active',
        });
      }
    }
  }, [visible, user, mode, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await onSave(values);
      form.resetFields();
    } catch (error) {
      console.error('Erreur validation:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title={mode === 'edit' ? 'Modifier l\'utilisateur' : 'Nouvel utilisateur'}
      open={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={600}
      okText={mode === 'edit' ? 'Mettre à jour' : 'Créer'}
      cancelText="Annuler"
    >
      <Form
        form={form}
        layout="vertical"
        requiredMark="optional"
      >
        <Divider orientation="left">Informations personnelles</Divider>

        <Form.Item
          label="Email"
          name="email"
          rules={[
            { required: true, message: 'L\'email est obligatoire' },
            { type: 'email', message: 'Email invalide' }
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="utilisateur@example.com"
            disabled={mode === 'edit'}
          />
        </Form.Item>

        {mode === 'create' && (
          <Form.Item
            label="Mot de passe"
            name="password"
            rules={[
              { required: true, message: 'Le mot de passe est obligatoire' },
              { min: 8, message: 'Minimum 8 caractères' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="••••••••"
            />
          </Form.Item>
        )}

        <Space style={{ width: '100%' }} size="large">
          <Form.Item
            label="Prénom"
            name="first_name"
            style={{ flex: 1, marginBottom: 0 }}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Jean"
            />
          </Form.Item>

          <Form.Item
            label="Nom"
            name="last_name"
            style={{ flex: 1, marginBottom: 0 }}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Dupont"
            />
          </Form.Item>
        </Space>

        <Form.Item
          label="Téléphone"
          name="phone"
        >
          <Input
            prefix={<PhoneOutlined />}
            placeholder="+212600000000"
          />
        </Form.Item>

        <Form.Item
          label="Entreprise"
          name="company"
        >
          <Input placeholder="Nom de l'entreprise" />
        </Form.Item>

        <Divider orientation="left">Paramètres du compte</Divider>

        <Space style={{ width: '100%' }} size="large">
          <Form.Item
            label="Rôle"
            name="role"
            rules={[{ required: true, message: 'Le rôle est obligatoire' }]}
            style={{ flex: 1, marginBottom: 0 }}
          >
            <Select>
              <Option value="user">Utilisateur</Option>
              <Option value="merchant">Marchand</Option>
              <Option value="influencer">Influenceur</Option>
              <Option value="commercial">Commercial</Option>
              <Option value="sales_rep">Représentant</Option>
              <Option value="admin">Admin</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Statut"
            name="status"
            rules={[{ required: true, message: 'Le statut est obligatoire' }]}
            style={{ flex: 1, marginBottom: 0 }}
          >
            <Select>
              <Option value="active">Actif</Option>
              <Option value="suspended">Suspendu</Option>
              <Option value="pending">En attente</Option>
            </Select>
          </Form.Item>
        </Space>

        {mode === 'create' && (
          <Form.Item
            label="Envoyer un email de bienvenue"
            name="send_welcome_email"
            valuePropName="checked"
            initialValue={true}
          >
            <Switch />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default UserFormModal;
