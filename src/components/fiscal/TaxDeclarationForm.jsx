/**
 * Formulaire de déclaration fiscale - Multi-pays
 * Maroc: TVA mensuelle, France: CA3/CA12, USA: Quarterly Tax
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Steps, Form, DatePicker, InputNumber, Button,
  Table, Space, Statistic, Divider, Alert, Checkbox, message,
  Upload, Tag, Modal
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  UploadOutlined,
  DownloadOutlined,
  SendOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { Step } = Steps;
const { RangePicker } = DatePicker;

const TaxDeclarationForm = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [country, setCountry] = useState('MA');
  const [declarationType, setDeclarationType] = useState('monthly');
  const [period, setPeriod] = useState([dayjs().subtract(1, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')]);
  const [invoices, setInvoices] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [calculation, setCalculation] = useState({
    vat_collected: 0,
    vat_deductible: 0,
    vat_to_pay: 0
  });
  const [checklist, setChecklist] = useState({
    all_invoices: false,
    all_purchases: false,
    bank_reconciled: false,
    documents_ready: false
  });

  useEffect(() => {
    fetchCountry();
  }, []);

  useEffect(() => {
    if (country && period) {
      fetchInvoices();
    }
  }, [country, period]);

  const fetchCountry = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'MA');
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchInvoices = async () => {
    try {
      const [start, end] = period;
      const response = await axios.get('/api/invoices', {
        params: {
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD'),
          status: 'paid'
        }
      });
      setInvoices(response.data);
      calculateVATCollected(response.data);
    } catch (error) {
      console.error('Erreur chargement factures:', error);
    }
  };

  const calculateVATCollected = (invoiceList) => {
    const total = invoiceList.reduce((sum, inv) => sum + (inv.vat_amount || 0), 0);
    setCalculation(prev => ({
      ...prev,
      vat_collected: total,
      vat_to_pay: total - prev.vat_deductible
    }));
  };

  const addPurchase = () => {
    const newPurchase = {
      id: Date.now(),
      description: '',
      amount_ht: 0,
      vat_rate: 20,
      vat_amount: 0,
      supplier: ''
    };
    setPurchases([...purchases, newPurchase]);
  };

  const updatePurchase = (id, field, value) => {
    const updated = purchases.map(p => {
      if (p.id !== id) return p;
      
      const newPurchase = { ...p, [field]: value };
      
      if (field === 'amount_ht' || field === 'vat_rate') {
        const amountHT = newPurchase.amount_ht || 0;
        const rate = newPurchase.vat_rate || 0;
        newPurchase.vat_amount = amountHT * (rate / 100);
      }
      
      return newPurchase;
    });
    
    setPurchases(updated);
    
    const totalDeductible = updated.reduce((sum, p) => sum + (p.vat_amount || 0), 0);
    setCalculation(prev => ({
      ...prev,
      vat_deductible: totalDeductible,
      vat_to_pay: prev.vat_collected - totalDeductible
    }));
  };

  const removePurchase = (id) => {
    const updated = purchases.filter(p => p.id !== id);
    setPurchases(updated);
    
    const totalDeductible = updated.reduce((sum, p) => sum + (p.vat_amount || 0), 0);
    setCalculation(prev => ({
      ...prev,
      vat_deductible: totalDeductible,
      vat_to_pay: prev.vat_collected - totalDeductible
    }));
  };

  const getCurrency = () => {
    switch (country) {
      case 'MA': return 'DH';
      case 'FR': return '€';
      case 'US': return '$';
      default: return '';
    }
  };

  const formatCurrency = (value) => {
    return `${parseFloat(value || 0).toFixed(2)} ${getCurrency()}`;
  };

  const getDeclarationLabel = () => {
    if (country === 'MA') return 'Déclaration TVA Mensuelle';
    if (country === 'FR') return declarationType === 'monthly' ? 'Déclaration CA3 (mensuelle)' : 'Déclaration CA12 (annuelle)';
    if (country === 'US') return 'Quarterly Tax Payment';
    return 'Tax Declaration';
  };

  const handleGeneratePDF = async () => {
    try {
      setLoading(true);
      
      const [start, end] = period;
      const declarationData = {
        country,
        declaration_type: country === 'MA' ? 'TVA_MONTHLY' : country === 'FR' ? (declarationType === 'monthly' ? 'CA3' : 'CA12') : 'QUARTERLY',
        period_start: start.format('YYYY-MM-DD'),
        period_end: end.format('YYYY-MM-DD'),
        vat_collected: calculation.vat_collected,
        vat_deductible: calculation.vat_deductible,
        vat_to_pay: calculation.vat_to_pay,
        invoices: invoices.map(inv => inv.id),
        purchases
      };
      
      const response = await axios.post('/api/fiscal/vat/declare', declarationData, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Declaration_${getDeclarationLabel()}_${dayjs().format('YYYY-MM')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      message.success('Déclaration PDF générée avec succès !');
    } catch (error) {
      message.error('Erreur lors de la génération du PDF');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      const [start, end] = period;
      const declarationData = {
        country,
        declaration_type: country === 'MA' ? 'TVA_MONTHLY' : country === 'FR' ? (declarationType === 'monthly' ? 'CA3' : 'CA12') : 'QUARTERLY',
        period_start: start.format('YYYY-MM-DD'),
        period_end: end.format('YYYY-MM-DD'),
        vat_collected: calculation.vat_collected,
        vat_deductible: calculation.vat_deductible,
        vat_to_pay: calculation.vat_to_pay,
        status: 'submitted',
        submission_date: dayjs().format('YYYY-MM-DD')
      };
      
      await axios.post('/api/fiscal/vat/declarations', declarationData);
      
      message.success('Déclaration enregistrée avec succès !');
      
      // Réinitialiser le formulaire
      setCurrentStep(0);
      setPurchases([]);
      setCalculation({ vat_collected: 0, vat_deductible: 0, vat_to_pay: 0 });
      setChecklist({
        all_invoices: false,
        all_purchases: false,
        bank_reconciled: false,
        documents_ready: false
      });
    } catch (error) {
      message.error('Erreur lors de la soumission');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const invoiceColumns = [
    {
      title: 'N° Facture',
      dataIndex: 'invoice_number',
      key: 'invoice_number'
    },
    {
      title: 'Date',
      dataIndex: 'issue_date',
      key: 'issue_date',
      render: (date) => dayjs(date).format('DD/MM/YYYY')
    },
    {
      title: 'Client',
      dataIndex: 'client_name',
      key: 'client_name'
    },
    {
      title: 'Montant HT',
      dataIndex: 'amount_ht',
      key: 'amount_ht',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: country === 'US' ? 'Sales Tax' : 'TVA',
      dataIndex: 'vat_amount',
      key: 'vat_amount',
      render: (val) => <strong>{formatCurrency(val)}</strong>,
      align: 'right'
    },
    {
      title: 'Montant TTC',
      dataIndex: 'amount_ttc',
      key: 'amount_ttc',
      render: (val) => formatCurrency(val),
      align: 'right'
    }
  ];

  const purchaseColumns = [
    {
      title: 'Fournisseur',
      dataIndex: 'supplier',
      key: 'supplier',
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => updatePurchase(record.id, 'supplier', e.target.value)}
          placeholder="Nom du fournisseur"
        />
      )
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => updatePurchase(record.id, 'description', e.target.value)}
          placeholder="Description de l'achat"
        />
      )
    },
    {
      title: 'Montant HT',
      dataIndex: 'amount_ht',
      key: 'amount_ht',
      render: (value, record) => (
        <InputNumber
          value={value}
          onChange={(val) => updatePurchase(record.id, 'amount_ht', val)}
          min={0}
          step={0.01}
          style={{ width: '100%' }}
        />
      ),
      width: 150
    },
    {
      title: 'Taux TVA',
      dataIndex: 'vat_rate',
      key: 'vat_rate',
      render: (value, record) => (
        <InputNumber
          value={value}
          onChange={(val) => updatePurchase(record.id, 'vat_rate', val)}
          min={0}
          max={100}
          suffix="%"
          style={{ width: '100%' }}
        />
      ),
      width: 120
    },
    {
      title: 'TVA déductible',
      dataIndex: 'vat_amount',
      key: 'vat_amount',
      render: (val) => <strong>{formatCurrency(val)}</strong>,
      align: 'right',
      width: 150
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removePurchase(record.id)}
        />
      ),
      width: 80
    }
  ];

  const steps = [
    {
      title: 'Période',
      description: 'Sélection de la période'
    },
    {
      title: 'Données',
      description: 'Collecte des données'
    },
    {
      title: 'Calcul',
      description: 'Calcul de la TVA'
    },
    {
      title: 'Validation',
      description: 'Vérification finale'
    },
    {
      title: 'Soumission',
      description: 'Enregistrement'
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>{getDeclarationLabel()}</span>
            <span style={{ color: '#666', fontSize: 14 }}>
              {country === 'MA' && '🇲🇦 Maroc'}
              {country === 'FR' && '🇫🇷 France'}
              {country === 'US' && '🇺🇸 USA'}
            </span>
          </Space>
        }
      >
        <Steps current={currentStep} style={{ marginBottom: 32 }}>
          {steps.map(step => (
            <Step key={step.title} title={step.title} description={step.description} />
          ))}
        </Steps>

        {/* Étape 0 : Sélection période */}
        {currentStep === 0 && (
          <div>
            <Row justify="center" style={{ marginBottom: 24 }}>
              <Col xs={24} md={12}>
                <Card>
                  <Form.Item label="Type de déclaration" style={{ marginBottom: 16 }}>
                    {country === 'FR' ? (
                      <Radio.Group value={declarationType} onChange={(e) => setDeclarationType(e.target.value)}>
                        <Radio.Button value="monthly">CA3 (Mensuelle)</Radio.Button>
                        <Radio.Button value="annual">CA12 (Annuelle)</Radio.Button>
                      </Radio.Group>
                    ) : (
                      <Tag color="blue" style={{ fontSize: 16, padding: '8px 16px' }}>
                        {getDeclarationLabel()}
                      </Tag>
                    )}
                  </Form.Item>

                  <Form.Item label="Période de déclaration">
                    <RangePicker
                      value={period}
                      onChange={setPeriod}
                      picker={declarationType === 'annual' ? 'year' : 'month'}
                      format="MMMM YYYY"
                      style={{ width: '100%' }}
                      size="large"
                    />
                  </Form.Item>

                  <Alert
                    message={`Période sélectionnée: ${period[0].format('DD/MM/YYYY')} au ${period[1].format('DD/MM/YYYY')}`}
                    type="info"
                    showIcon
                  />
                </Card>
              </Col>
            </Row>

            <Row justify="center">
              <Button type="primary" size="large" onClick={() => setCurrentStep(1)}>
                Suivant →
              </Button>
            </Row>
          </div>
        )}

        {/* Étape 1 : Données */}
        {currentStep === 1 && (
          <div>
            <h3>📊 Données de la période</h3>
            
            <Card title={`${country === 'US' ? 'Sales Tax' : 'TVA'} Collectée (Ventes)`} style={{ marginBottom: 16 }}>
              <Alert
                message={`${invoices.length} facture(s) trouvée(s) pour cette période`}
                type="success"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <Table
                dataSource={invoices}
                columns={invoiceColumns}
                rowKey="id"
                pagination={{ pageSize: 10 }}
                scroll={{ x: 800 }}
                summary={() => (
                  <Table.Summary fixed>
                    <Table.Summary.Row>
                      <Table.Summary.Cell index={0} colSpan={4}>
                        <strong>Total</strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={4}>
                        <strong style={{ color: '#1890ff' }}>
                          {formatCurrency(calculation.vat_collected)}
                        </strong>
                      </Table.Summary.Cell>
                      <Table.Summary.Cell index={5} />
                    </Table.Summary.Row>
                  </Table.Summary>
                )}
              />
            </Card>

            <Card title={`${country === 'US' ? 'Tax' : 'TVA'} Déductible (Achats professionnels)`}>
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={addPurchase}
                block
                style={{ marginBottom: 16 }}
              >
                Ajouter un achat professionnel
              </Button>

              <Table
                dataSource={purchases}
                columns={purchaseColumns}
                rowKey="id"
                pagination={false}
                scroll={{ x: 1000 }}
              />

              <Divider />

              <Row justify="end">
                <Statistic
                  title={`Total ${country === 'US' ? 'Tax' : 'TVA'} déductible`}
                  value={calculation.vat_deductible}
                  precision={2}
                  suffix={getCurrency()}
                  valueStyle={{ color: '#fa8c16', fontSize: 24 }}
                />
              </Row>
            </Card>

            <Divider />

            <Row justify="center" gutter={16}>
              <Col>
                <Button size="large" onClick={() => setCurrentStep(0)}>
                  ← Précédent
                </Button>
              </Col>
              <Col>
                <Button type="primary" size="large" onClick={() => setCurrentStep(2)}>
                  Suivant →
                </Button>
              </Col>
            </Row>
          </div>
        )}

        {/* Étape 2 : Calcul */}
        {currentStep === 2 && (
          <div>
            <h3>🧮 Calcul de la {country === 'US' ? 'Tax' : 'TVA'}</h3>

            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={8}>
                <Card style={{ background: '#f0f5ff' }}>
                  <Statistic
                    title={`${country === 'US' ? 'Sales Tax' : 'TVA'} Collectée`}
                    value={calculation.vat_collected}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ color: '#1890ff', fontSize: 28 }}
                  />
                  <div style={{ marginTop: 8, color: '#666' }}>
                    Sur {invoices.length} facture(s)
                  </div>
                </Card>
              </Col>

              <Col xs={24} sm={8}>
                <Card style={{ background: '#fff7e6' }}>
                  <Statistic
                    title={`${country === 'US' ? 'Tax' : 'TVA'} Déductible`}
                    value={calculation.vat_deductible}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ color: '#fa8c16', fontSize: 28 }}
                  />
                  <div style={{ marginTop: 8, color: '#666' }}>
                    Sur {purchases.length} achat(s)
                  </div>
                </Card>
              </Col>

              <Col xs={24} sm={8}>
                <Card style={{ background: calculation.vat_to_pay > 0 ? '#fff2e8' : '#f6ffed' }}>
                  <Statistic
                    title={`${country === 'US' ? 'Tax' : 'TVA'} à payer`}
                    value={calculation.vat_to_pay}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{
                      color: calculation.vat_to_pay > 0 ? '#f5222d' : '#52c41a',
                      fontSize: 32,
                      fontWeight: 'bold'
                    }}
                  />
                </Card>
              </Col>
            </Row>

            <Alert
              message="Formule de calcul"
              description={
                <div style={{ fontSize: 16 }}>
                  <p>
                    <strong>{country === 'US' ? 'Tax' : 'TVA'} à payer</strong> ={' '}
                    {country === 'US' ? 'Sales Tax Collectée' : 'TVA Collectée'} -{' '}
                    {country === 'US' ? 'Tax Déductible' : 'TVA Déductible'}
                  </p>
                  <p>
                    = {formatCurrency(calculation.vat_collected)} - {formatCurrency(calculation.vat_deductible)} ={' '}
                    <strong style={{ color: '#f5222d' }}>
                      {formatCurrency(calculation.vat_to_pay)}
                    </strong>
                  </p>
                </div>
              }
              type="info"
              showIcon
            />

            <Divider />

            <Row justify="center" gutter={16}>
              <Col>
                <Button size="large" onClick={() => setCurrentStep(1)}>
                  ← Précédent
                </Button>
              </Col>
              <Col>
                <Button type="primary" size="large" onClick={() => setCurrentStep(3)}>
                  Suivant →
                </Button>
              </Col>
            </Row>
          </div>
        )}

        {/* Étape 3 : Validation */}
        {currentStep === 3 && (
          <div>
            <h3>✅ Vérification avant soumission</h3>

            <Card>
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Checkbox
                  checked={checklist.all_invoices}
                  onChange={(e) => setChecklist({ ...checklist, all_invoices: e.target.checked })}
                >
                  <strong>Toutes les factures de vente sont bien comptabilisées</strong>
                  <div style={{ color: '#666', fontSize: 12 }}>
                    {invoices.length} facture(s) incluse(s)
                  </div>
                </Checkbox>

                <Checkbox
                  checked={checklist.all_purchases}
                  onChange={(e) => setChecklist({ ...checklist, all_purchases: e.target.checked })}
                >
                  <strong>Tous les achats professionnels sont saisis</strong>
                  <div style={{ color: '#666', fontSize: 12 }}>
                    {purchases.length} achat(s) déclaré(s)
                  </div>
                </Checkbox>

                <Checkbox
                  checked={checklist.bank_reconciled}
                  onChange={(e) => setChecklist({ ...checklist, bank_reconciled: e.target.checked })}
                >
                  <strong>Rapprochement bancaire effectué</strong>
                </Checkbox>

                <Checkbox
                  checked={checklist.documents_ready}
                  onChange={(e) => setChecklist({ ...checklist, documents_ready: e.target.checked })}
                >
                  <strong>Tous les justificatifs sont disponibles</strong>
                </Checkbox>
              </Space>

              <Divider />

              {Object.values(checklist).every(v => v) ? (
                <Alert
                  message="Prêt pour la soumission !"
                  description="Toutes les vérifications sont effectuées. Vous pouvez procéder à la déclaration."
                  type="success"
                  icon={<CheckCircleOutlined />}
                  showIcon
                />
              ) : (
                <Alert
                  message="Vérifications incomplètes"
                  description="Veuillez cocher toutes les cases avant de continuer."
                  type="warning"
                  icon={<ExclamationCircleOutlined />}
                  showIcon
                />
              )}
            </Card>

            <Divider />

            <Row justify="center" gutter={16}>
              <Col>
                <Button size="large" onClick={() => setCurrentStep(2)}>
                  ← Précédent
                </Button>
              </Col>
              <Col>
                <Button
                  type="primary"
                  size="large"
                  onClick={() => setCurrentStep(4)}
                  disabled={!Object.values(checklist).every(v => v)}
                >
                  Suivant →
                </Button>
              </Col>
            </Row>
          </div>
        )}

        {/* Étape 4 : Soumission */}
        {currentStep === 4 && (
          <div>
            <h3>📤 Soumission de la déclaration</h3>

            <Card style={{ marginBottom: 24 }}>
              <h4>Résumé de la déclaration</h4>
              <Row gutter={16}>
                <Col span={12}>
                  <p><strong>Type:</strong> {getDeclarationLabel()}</p>
                  <p><strong>Période:</strong> {period[0].format('MMMM YYYY')}</p>
                  <p><strong>Date de soumission:</strong> {dayjs().format('DD/MM/YYYY')}</p>
                </Col>
                <Col span={12}>
                  <Statistic
                    title={`${country === 'US' ? 'Tax' : 'TVA'} à payer`}
                    value={calculation.vat_to_pay}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ fontSize: 32, color: '#f5222d', fontWeight: 'bold' }}
                  />
                </Col>
              </Row>
            </Card>

            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Button
                type="primary"
                size="large"
                icon={<DownloadOutlined />}
                onClick={handleGeneratePDF}
                loading={loading}
                block
              >
                Générer le PDF de déclaration
              </Button>

              <Button
                size="large"
                icon={<UploadOutlined />}
                block
              >
                Joindre des documents (facultatif)
              </Button>

              <Button
                type="primary"
                size="large"
                icon={<SendOutlined />}
                onClick={handleSubmit}
                loading={loading}
                block
                style={{ background: '#52c41a', borderColor: '#52c41a' }}
              >
                Enregistrer la déclaration
              </Button>

              <Alert
                message="Après soumission"
                description={
                  <div>
                    {country === 'MA' && (
                      <p>
                        Vous devrez effectuer le paiement avant le 20 du mois suivant via le
                        portail SIMPL de la DGI.
                      </p>
                    )}
                    {country === 'FR' && (
                      <p>
                        Le paiement sera prélevé automatiquement si vous avez activé le
                        prélèvement SEPA. Sinon, payez via impots.gouv.fr avant le 24 du mois.
                      </p>
                    )}
                    {country === 'US' && (
                      <p>
                        Make your quarterly tax payment via IRS Direct Pay or EFTPS by the
                        due date (April 15, June 15, September 15, January 15).
                      </p>
                    )}
                  </div>
                }
                type="info"
                showIcon
              />
            </Space>

            <Divider />

            <Row justify="center">
              <Button size="large" onClick={() => setCurrentStep(3)}>
                ← Précédent
              </Button>
            </Row>
          </div>
        )}
      </Card>
    </div>
  );
};

export default TaxDeclarationForm;
