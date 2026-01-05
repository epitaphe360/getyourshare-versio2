import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Select, Switch, Space, Button, Divider, Tag, message } from 'antd';
import { PlusOutlined, MinusCircleOutlined } from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

/**
 * Modal de création/édition de plans d'abonnement
 */
const SubscriptionFormModal = ({ visible, onCancel, onSave, plan, mode }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [features, setFeatures] = useState([]);

  useEffect(() => {
    if (visible) {
      if (mode === 'edit' && plan) {
        // Mode édition : remplir le formulaire
        const featuresArray = Array.isArray(plan.features) 
          ? plan.features 
          : typeof plan.features === 'object' && plan.features !== null
          ? Object.entries(plan.features).map(([key, value]) => ({ key, value: String(value) }))
          : [];

        setFeatures(featuresArray);
        
        form.setFieldsValue({
          name: plan.name,
          code: plan.code,
          type: plan.type || 'standard',
          price_mad: plan.price_mad || 0,
          price: plan.price || 0,
          currency: plan.currency || 'EUR',
          max_team_members: plan.max_team_members,
          max_domains: plan.max_domains,
          description: plan.description,
          is_active: plan.is_active !== undefined ? plan.is_active : true,
          display_order: plan.display_order || 0,
        });
      } else {
        // Mode création : réinitialiser
        form.resetFields();
        setFeatures([]);
        form.setFieldsValue({
          type: 'standard',
          currency: 'EUR',
          is_active: true,
          display_order: 0,
        });
      }
    }
  }, [visible, plan, mode, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // Convertir features en objet
      const featuresObject = features.reduce((acc, feature) => {
        if (feature.key && feature.value) {
          acc[feature.key] = feature.value;
        }
        return acc;
      }, {});

      const formData = {
        ...values,
        features: featuresObject,
      };

      await onSave(formData);
      form.resetFields();
      setFeatures([]);
    } catch (error) {
      console.error('Erreur validation:', error);
      message.error('Veuillez remplir tous les champs obligatoires');
    } finally {
      setLoading(false);
    }
  };

  const addFeature = () => {
    setFeatures([...features, { key: '', value: '' }]);
  };

  const removeFeature = (index) => {
    const newFeatures = features.filter((_, i) => i !== index);
    setFeatures(newFeatures);
  };

  const updateFeature = (index, field, value) => {
    const newFeatures = [...features];
    newFeatures[index][field] = value;
    setFeatures(newFeatures);
  };

  return (
    <Modal
      title={mode === 'edit' ? 'Modifier le Plan' : 'Nouveau Plan d\'Abonnement'}
      open={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={700}
      okText="Enregistrer"
      cancelText="Annuler"
    >
      <Form
        form={form}
        layout="vertical"
        requiredMark="optional"
      >
        {/* Informations de base */}
        <Divider orientation="left">Informations de base</Divider>

        <Form.Item
          label="Nom du plan"
          name="name"
          rules={[{ required: true, message: 'Le nom est obligatoire' }]}
        >
          <Input placeholder="Ex: Plan Standard" />
        </Form.Item>

        <Form.Item
          label="Code"
          name="code"
          rules={[
            { required: true, message: 'Le code est obligatoire' },
            { pattern: /^[a-z0-9_-]+$/, message: 'Uniquement lettres minuscules, chiffres, _ et -' }
          ]}
        >
          <Input placeholder="Ex: standard-plan" />
        </Form.Item>

        <Form.Item
          label="Type"
          name="type"
          rules={[{ required: true, message: 'Le type est obligatoire' }]}
        >
          <Select>
            <Option value="standard">Standard</Option>
            <Option value="enterprise">Entreprise</Option>
            <Option value="marketplace">Marketplace</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="Description"
          name="description"
        >
          <TextArea rows={3} placeholder="Décrivez les avantages de ce plan..." />
        </Form.Item>

        {/* Prix */}
        <Divider orientation="left">Tarification</Divider>

        <Space style={{ width: '100%' }} size="large">
          <Form.Item
            label="Prix (MAD)"
            name="price_mad"
            rules={[{ required: true, message: 'Prix MAD requis' }]}
            style={{ marginBottom: 0 }}
          >
            <InputNumber
              min={0}
              precision={2}
              style={{ width: 150 }}
              placeholder="0.00"
              addonAfter="MAD"
            />
          </Form.Item>

          <Form.Item
            label="Prix (International)"
            name="price"
            style={{ marginBottom: 0 }}
          >
            <InputNumber
              min={0}
              precision={2}
              style={{ width: 150 }}
              placeholder="0.00"
            />
          </Form.Item>

          <Form.Item
            label="Devise"
            name="currency"
            style={{ marginBottom: 0 }}
          >
            <Select style={{ width: 100 }}>
              <Option value="EUR">EUR</Option>
              <Option value="USD">USD</Option>
              <Option value="MAD">MAD</Option>
            </Select>
          </Form.Item>
        </Space>

        {/* Limites */}
        <Divider orientation="left">Limites</Divider>

        <Space style={{ width: '100%' }} size="large">
          <Form.Item
            label="Max. Membres d'équipe"
            name="max_team_members"
            tooltip="Laissez vide pour illimité"
          >
            <InputNumber
              min={0}
              style={{ width: 150 }}
              placeholder="Illimité"
            />
          </Form.Item>

          <Form.Item
            label="Max. Domaines"
            name="max_domains"
            tooltip="Laissez vide pour illimité"
          >
            <InputNumber
              min={0}
              style={{ width: 150 }}
              placeholder="Illimité"
            />
          </Form.Item>
        </Space>

        {/* Fonctionnalités */}
        <Divider orientation="left">Fonctionnalités</Divider>

        <div style={{ marginBottom: '16px' }}>
          {features.map((feature, index) => (
            <Space key={index} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
              <Input
                placeholder="Nom de la fonctionnalité"
                value={feature.key}
                onChange={(e) => updateFeature(index, 'key', e.target.value)}
                style={{ width: 250 }}
              />
              <Input
                placeholder="Valeur (ex: true, 100, premium)"
                value={feature.value}
                onChange={(e) => updateFeature(index, 'value', e.target.value)}
                style={{ width: 250 }}
              />
              <MinusCircleOutlined
                onClick={() => removeFeature(index)}
                style={{ color: '#ff4d4f', cursor: 'pointer' }}
              />
            </Space>
          ))}
          <Button
            type="dashed"
            onClick={addFeature}
            block
            icon={<PlusOutlined />}
          >
            Ajouter une fonctionnalité
          </Button>
        </div>

        {/* Autres paramètres */}
        <Divider orientation="left">Autres paramètres</Divider>

        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Form.Item
            label="Ordre d'affichage"
            name="display_order"
            tooltip="Plus le nombre est élevé, plus le plan apparaît en premier"
          >
            <InputNumber min={0} style={{ width: 120 }} />
          </Form.Item>

          <Form.Item
            label="Statut"
            name="is_active"
            valuePropName="checked"
          >
            <Switch
              checkedChildren="Actif"
              unCheckedChildren="Inactif"
            />
          </Form.Item>
        </Space>

        {/* Preview des fonctionnalités */}
        {features.length > 0 && (
          <div style={{ marginTop: '16px', padding: '12px', background: '#f5f5f5', borderRadius: '4px' }}>
            <div style={{ marginBottom: '8px', fontWeight: 500 }}>Aperçu des fonctionnalités:</div>
            <Space wrap>
              {features.map((feature, index) => (
                feature.key && (
                  <Tag key={index} color="blue">
                    {feature.key}: {feature.value}
                  </Tag>
                )
              ))}
            </Space>
          </div>
        )}
      </Form>
    </Modal>
  );
};

export default SubscriptionFormModal;
