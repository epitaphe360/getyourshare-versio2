/**
 * Générateur de factures conformes - Multi-pays
 * Numérotation séquentielle, mentions légales, PDF
 */

import React, { useState, useEffect } from 'react';
import {
  Form, Input, InputNumber, Select, DatePicker, Button, Card,
  Table, Space, Row, Col, Divider, Alert, message, Modal
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  EyeOutlined,
  DownloadOutlined,
  SendOutlined,
  SaveOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;

const InvoiceGenerator = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [country, setCountry] = useState('MA');
  const [lineItems, setLineItems] = useState([
    { id: 1, description: '', quantity: 1, unit_price: 0, vat_rate: 20, total_ht: 0, total_ttc: 0 }
  ]);
  const [clients, setClients] = useState([]);
  const [nextInvoiceNumber, setNextInvoiceNumber] = useState('FA-2024-00001');
  const [previewVisible, setPreviewVisible] = useState(false);
  const [vatRates, setVatRates] = useState([]);

  useEffect(() => {
    fetchCountry();
    fetchClients();
    fetchNextInvoiceNumber();
  }, []);

  useEffect(() => {
    if (country) {
      fetchVatRates();
    }
  }, [country]);

  const fetchCountry = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'MA');
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await axios.get('/api/clients');
      setClients(response.data);
    } catch (error) {
      console.error('Erreur chargement clients:', error);
    }
  };

  const fetchNextInvoiceNumber = async () => {
    try {
      const response = await axios.get('/api/invoices/next-number');
      setNextInvoiceNumber(response.data.next_number);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchVatRates = async () => {
    try {
      const response = await axios.get(`/api/fiscal/rates/${country}`);
      const rates = response.data.vat;
      
      // Parser les taux TVA selon le pays
      const rateList = [];
      if (country === 'MA') {
        rateList.push(
          { value: 20, label: '20% (Taux normal)' },
          { value: 14, label: '14% (Taux réduit)' },
          { value: 10, label: '10% (Taux réduit)' },
          { value: 7, label: '7% (Taux particulier)' },
          { value: 0, label: '0% (Exonéré)' }
        );
      } else if (country === 'FR') {
        rateList.push(
          { value: 20, label: '20% (Taux normal)' },
          { value: 10, label: '10% (Taux intermédiaire)' },
          { value: 5.5, label: '5.5% (Taux réduit)' },
          { value: 2.1, label: '2.1% (Taux super réduit)' },
          { value: 0, label: '0% (Franchise TVA)' }
        );
      } else if (country === 'US') {
        rateList.push(
          { value: 0, label: '0% (No federal VAT)' },
          { value: 5, label: '~5% (State sales tax - varies)' },
          { value: 7, label: '~7% (State + local)' },
          { value: 10, label: '~10% (Some states)' }
        );
      }
      setVatRates(rateList);
    } catch (error) {
      console.error('Erreur chargement taux TVA:', error);
    }
  };

  const getCurrency = () => {
    switch (country) {
      case 'MA': return 'DH';
      case 'FR': return '€';
      case 'US': return '$';
      default: return '';
    }
  };

  const addLineItem = () => {
    const newId = Math.max(...lineItems.map(item => item.id), 0) + 1;
    setLineItems([
      ...lineItems,
      {
        id: newId,
        description: '',
        quantity: 1,
        unit_price: 0,
        vat_rate: 20,
        total_ht: 0,
        total_ttc: 0
      }
    ]);
  };

  const removeLineItem = (id) => {
    if (lineItems.length === 1) {
      message.warning('Il doit y avoir au moins une ligne');
      return;
    }
    setLineItems(lineItems.filter(item => item.id !== id));
  };

  const updateLineItem = (id, field, value) => {
    const updatedItems = lineItems.map(item => {
      if (item.id !== id) return item;

      const updated = { ...item, [field]: value };

      // Recalculer les totaux
      const quantity = updated.quantity || 0;
      const unitPrice = updated.unit_price || 0;
      const vatRate = updated.vat_rate || 0;

      const totalHT = quantity * unitPrice;
      const totalTTC = totalHT * (1 + vatRate / 100);

      return {
        ...updated,
        total_ht: totalHT,
        total_ttc: totalTTC
      };
    });

    setLineItems(updatedItems);
  };

  const calculateTotals = () => {
    const totalHT = lineItems.reduce((sum, item) => sum + item.total_ht, 0);
    const totalVAT = lineItems.reduce(
      (sum, item) => sum + item.total_ht * (item.vat_rate / 100),
      0
    );
    const totalTTC = totalHT + totalVAT;

    return { totalHT, totalVAT, totalTTC };
  };

  const formatCurrency = (value) => {
    return `${parseFloat(value).toFixed(2)} ${getCurrency()}`;
  };

  const handleSaveDraft = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const invoiceData = {
        ...values,
        line_items: lineItems,
        status: 'draft',
        country
      };

      const response = await axios.post('/api/invoices', invoiceData);
      message.success('Brouillon enregistré !');
      
      // Réinitialiser le formulaire
      form.resetFields();
      setLineItems([
        { id: 1, description: '', quantity: 1, unit_price: 0, vat_rate: 20, total_ht: 0, total_ttc: 0 }
      ]);
      fetchNextInvoiceNumber();
    } catch (error) {
      message.error('Erreur lors de l\'enregistrement');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendInvoice = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const invoiceData = {
        ...values,
        line_items: lineItems,
        status: 'sent',
        country
      };

      const response = await axios.post('/api/invoices', invoiceData);
      
      // Envoyer par email
      await axios.post(`/api/invoices/${response.data.id}/send-email`);
      
      message.success('Facture créée et envoyée par email !');
      
      // Réinitialiser
      form.resetFields();
      setLineItems([
        { id: 1, description: '', quantity: 1, unit_price: 0, vat_rate: 20, total_ht: 0, total_ttc: 0 }
      ]);
      fetchNextInvoiceNumber();
    } catch (error) {
      message.error('Erreur lors de l\'envoi');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const invoiceData = {
        ...values,
        line_items: lineItems,
        status: 'draft',
        country
      };

      const response = await axios.post('/api/invoices', invoiceData);
      
      // Télécharger le PDF
      const pdfResponse = await axios.get(
        `/api/invoices/${response.data.id}/pdf`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([pdfResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${nextInvoiceNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('PDF téléchargé !');
    } catch (error) {
      message.error('Erreur lors de la génération du PDF');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '#',
      dataIndex: 'id',
      key: 'id',
      width: 50,
      render: (id, record, index) => index + 1
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      width: '30%',
      render: (text, record) => (
        <TextArea
          value={text}
          onChange={(e) => updateLineItem(record.id, 'description', e.target.value)}
          placeholder="Description du produit/service"
          autoSize={{ minRows: 1, maxRows: 3 }}
        />
      )
    },
    {
      title: 'Qté',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (value, record) => (
        <InputNumber
          min={1}
          value={value}
          onChange={(val) => updateLineItem(record.id, 'quantity', val)}
          style={{ width: '100%' }}
        />
      )
    },
    {
      title: `Prix unitaire HT (${getCurrency()})`,
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 150,
      render: (value, record) => (
        <InputNumber
          min={0}
          step={0.01}
          value={value}
          onChange={(val) => updateLineItem(record.id, 'unit_price', val)}
          style={{ width: '100%' }}
        />
      )
    },
    {
      title: country === 'US' ? 'Sales Tax' : 'TVA',
      dataIndex: 'vat_rate',
      key: 'vat_rate',
      width: 150,
      render: (value, record) => (
        <Select
          value={value}
          onChange={(val) => updateLineItem(record.id, 'vat_rate', val)}
          style={{ width: '100%' }}
        >
          {vatRates.map(rate => (
            <Option key={rate.value} value={rate.value}>
              {rate.label}
            </Option>
          ))}
        </Select>
      )
    },
    {
      title: `Total HT (${getCurrency()})`,
      dataIndex: 'total_ht',
      key: 'total_ht',
      width: 120,
      render: (value) => <strong>{formatCurrency(value)}</strong>,
      align: 'right'
    },
    {
      title: `Total TTC (${getCurrency()})`,
      dataIndex: 'total_ttc',
      key: 'total_ttc',
      width: 120,
      render: (value) => <strong>{formatCurrency(value)}</strong>,
      align: 'right'
    },
    {
      title: 'Action',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeLineItem(record.id)}
        />
      )
    }
  ];

  const { totalHT, totalVAT, totalTTC } = calculateTotals();

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <span style={{ fontSize: 20 }}>📄 Créer une facture</span>
            <span style={{ color: '#666', fontSize: 14 }}>
              {country === 'MA' && '🇲🇦 Maroc'}
              {country === 'FR' && '🇫🇷 France'}
              {country === 'US' && '🇺🇸 USA'}
            </span>
          </Space>
        }
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item label="N° Facture" name="invoice_number">
                <Input
                  value={nextInvoiceNumber}
                  disabled
                  style={{ fontWeight: 'bold', fontSize: 16 }}
                />
              </Form.Item>
            </Col>

            <Col xs={24} md={8}>
              <Form.Item
                label="Client"
                name="client_id"
                rules={[{ required: true, message: 'Sélectionnez un client' }]}
              >
                <Select
                  placeholder="Choisir un client"
                  showSearch
                  filterOption={(input, option) =>
                    option.children.toLowerCase().includes(input.toLowerCase())
                  }
                >
                  {clients.map(client => (
                    <Option key={client.id} value={client.id}>
                      {client.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} md={4}>
              <Form.Item
                label="Date d'émission"
                name="issue_date"
                initialValue={dayjs()}
                rules={[{ required: true }]}
              >
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>

            <Col xs={24} md={4}>
              <Form.Item
                label="Date d'échéance"
                name="due_date"
                initialValue={dayjs().add(30, 'days')}
                rules={[{ required: true }]}
              >
                <DatePicker format="DD/MM/YYYY" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Divider>Lignes de facturation</Divider>

          <Table
            dataSource={lineItems}
            columns={columns}
            rowKey="id"
            pagination={false}
            scroll={{ x: 1200 }}
            footer={() => (
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={addLineItem}
                block
              >
                Ajouter une ligne
              </Button>
            )}
          />

          <Divider />

          {/* Totaux */}
          <Row justify="end">
            <Col xs={24} sm={12} md={8}>
              <Card size="small" style={{ background: '#fafafa' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Row justify="space-between">
                    <span>Total HT:</span>
                    <strong style={{ fontSize: 16 }}>
                      {formatCurrency(totalHT)}
                    </strong>
                  </Row>
                  <Row justify="space-between">
                    <span>{country === 'US' ? 'Sales Tax:' : 'TVA:'}</span>
                    <strong style={{ fontSize: 16, color: '#1890ff' }}>
                      {formatCurrency(totalVAT)}
                    </strong>
                  </Row>
                  <Divider style={{ margin: '8px 0' }} />
                  <Row justify="space-between">
                    <strong style={{ fontSize: 18 }}>Total TTC:</strong>
                    <strong style={{ fontSize: 20, color: '#52c41a' }}>
                      {formatCurrency(totalTTC)}
                    </strong>
                  </Row>
                </Space>
              </Card>
            </Col>
          </Row>

          <Divider />

          {/* Notes et mentions légales */}
          <Row gutter={16}>
            <Col xs={24}>
              <Form.Item label="Notes / Conditions de paiement" name="notes">
                <TextArea
                  rows={3}
                  placeholder={
                    country === 'MA'
                      ? 'Ex: Paiement par virement bancaire sous 30 jours...'
                      : country === 'FR'
                      ? 'Ex: Escompte pour paiement anticipé. Pénalités de retard: 3 fois le taux légal...'
                      : 'Ex: Payment due within 30 days. Late fees may apply...'
                  }
                />
              </Form.Item>
            </Col>
          </Row>

          <Alert
            message="Mentions légales automatiques"
            description={
              <div>
                {country === 'MA' && (
                  <p>
                    Les mentions légales obligatoires (ICE, IF, RC, TVA, Capital,
                    adresse, etc.) seront automatiquement ajoutées sur la facture PDF.
                  </p>
                )}
                {country === 'FR' && (
                  <p>
                    Les mentions légales obligatoires (SIRET, TVA, RCS, Capital, Franchise
                    TVA si applicable, etc.) seront automatiquement ajoutées.
                  </p>
                )}
                {country === 'US' && (
                  <p>
                    Tax ID (EIN), business address, and other required information will
                    be automatically included on the invoice.
                  </p>
                )}
              </div>
            }
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />

          {/* Actions */}
          <Row gutter={16} justify="end">
            <Col>
              <Button
                size="large"
                icon={<EyeOutlined />}
                onClick={() => setPreviewVisible(true)}
              >
                Aperçu
              </Button>
            </Col>
            <Col>
              <Button
                size="large"
                icon={<SaveOutlined />}
                onClick={handleSaveDraft}
                loading={loading}
              >
                Enregistrer brouillon
              </Button>
            </Col>
            <Col>
              <Button
                size="large"
                icon={<DownloadOutlined />}
                onClick={handleDownloadPDF}
                loading={loading}
              >
                Télécharger PDF
              </Button>
            </Col>
            <Col>
              <Button
                type="primary"
                size="large"
                icon={<SendOutlined />}
                onClick={handleSendInvoice}
                loading={loading}
              >
                Enregistrer et envoyer
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* Modal aperçu */}
      <Modal
        title={`Aperçu - ${nextInvoiceNumber}`}
        visible={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={800}
      >
        <div style={{ padding: '24px', background: '#fff', border: '1px solid #d9d9d9' }}>
          <h2>FACTURE {nextInvoiceNumber}</h2>
          <p>Date: {dayjs().format('DD/MM/YYYY')}</p>
          <Divider />
          <h3>Lignes:</h3>
          {lineItems.map((item, idx) => (
            <p key={idx}>
              {idx + 1}. {item.description} - Qté: {item.quantity} x{' '}
              {formatCurrency(item.unit_price)} = {formatCurrency(item.total_ttc)}
            </p>
          ))}
          <Divider />
          <h3>Totaux:</h3>
          <p>Total HT: {formatCurrency(totalHT)}</p>
          <p>{country === 'US' ? 'Sales Tax' : 'TVA'}: {formatCurrency(totalVAT)}</p>
          <p>
            <strong>Total TTC: {formatCurrency(totalTTC)}</strong>
          </p>
        </div>
      </Modal>
    </div>
  );
};

export default InvoiceGenerator;
