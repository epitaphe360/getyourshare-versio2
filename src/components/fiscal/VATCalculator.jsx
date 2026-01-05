/**
 * Calculateur TVA interactif - Multi-pays
 * Calcul HT ↔ TTC avec historique
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Radio, InputNumber, Statistic, Space,
  Button, Table, Tag, Divider, Alert
} from 'antd';
import {
  CalculatorOutlined,
  SwapOutlined,
  SaveOutlined,
  DeleteOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const VATCalculator = () => {
  const [mode, setMode] = useState('from_ht'); // 'from_ht' ou 'from_ttc'
  const [amount, setAmount] = useState(0);
  const [selectedRate, setSelectedRate] = useState(20);
  const [country, setCountry] = useState('MA');
  const [result, setResult] = useState({
    amount_ht: 0,
    vat_amount: 0,
    amount_ttc: 0
  });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchCountry();
    loadHistory();
  }, []);

  useEffect(() => {
    if (amount > 0) {
      calculateVAT();
    }
  }, [amount, selectedRate, mode]);

  const fetchCountry = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'MA');
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const loadHistory = () => {
    const saved = localStorage.getItem('vat_calculator_history');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  };

  const saveToHistory = () => {
    const newEntry = {
      id: Date.now(),
      date: dayjs().format('DD/MM/YYYY HH:mm'),
      mode,
      amount,
      rate: selectedRate,
      result: { ...result },
      country
    };

    const newHistory = [newEntry, ...history].slice(0, 10); // Garder 10 derniers
    setHistory(newHistory);
    localStorage.setItem('vat_calculator_history', JSON.stringify(newHistory));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('vat_calculator_history');
  };

  const loadFromHistory = (entry) => {
    setMode(entry.mode);
    setAmount(entry.amount);
    setSelectedRate(entry.rate);
    setResult(entry.result);
  };

  const calculateVAT = async () => {
    try {
      const response = await axios.post('/api/fiscal/vat/calculate', {
        amount,
        country,
        rate_type: getRateType(selectedRate)
      });

      if (mode === 'from_ht') {
        setResult({
          amount_ht: amount,
          vat_amount: response.data.vat_amount,
          amount_ttc: response.data.total_ttc
        });
      } else {
        // Calculer à partir du TTC
        const amountHT = amount / (1 + selectedRate / 100);
        const vatAmount = amount - amountHT;
        setResult({
          amount_ht: amountHT,
          vat_amount: vatAmount,
          amount_ttc: amount
        });
      }
    } catch (error) {
      console.error('Erreur calcul TVA:', error);
      // Calcul local de secours
      if (mode === 'from_ht') {
        const vatAmount = amount * (selectedRate / 100);
        setResult({
          amount_ht: amount,
          vat_amount: vatAmount,
          amount_ttc: amount + vatAmount
        });
      } else {
        const amountHT = amount / (1 + selectedRate / 100);
        const vatAmount = amount - amountHT;
        setResult({
          amount_ht: amountHT,
          vat_amount: vatAmount,
          amount_ttc: amount
        });
      }
    }
  };

  const getRateType = (rate) => {
    if (country === 'MA') {
      if (rate === 20) return 'standard';
      if (rate === 14) return 'reduced_14';
      if (rate === 10) return 'reduced_10';
      if (rate === 7) return 'reduced_7';
      return 'zero';
    } else if (country === 'FR') {
      if (rate === 20) return 'standard';
      if (rate === 10) return 'intermediate';
      if (rate === 5.5) return 'reduced';
      if (rate === 2.1) return 'super_reduced';
      return 'zero';
    } else {
      return 'standard';
    }
  };

  const getVATRates = () => {
    if (country === 'MA') {
      return [
        { value: 20, label: '20%', description: 'Taux normal' },
        { value: 14, label: '14%', description: 'Taux réduit' },
        { value: 10, label: '10%', description: 'Taux réduit' },
        { value: 7, label: '7%', description: 'Taux particulier' },
        { value: 0, label: '0%', description: 'Exonéré' }
      ];
    } else if (country === 'FR') {
      return [
        { value: 20, label: '20%', description: 'Taux normal' },
        { value: 10, label: '10%', description: 'Taux intermédiaire' },
        { value: 5.5, label: '5.5%', description: 'Taux réduit' },
        { value: 2.1, label: '2.1%', description: 'Taux super réduit' },
        { value: 0, label: '0%', description: 'Franchise TVA' }
      ];
    } else {
      return [
        { value: 0, label: '0%', description: 'No federal VAT' },
        { value: 5, label: '~5%', description: 'Average state tax' },
        { value: 7, label: '~7%', description: 'State + local' },
        { value: 10, label: '~10%', description: 'Some states' }
      ];
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

  const formatCurrency = (value) => {
    return `${parseFloat(value).toFixed(2)} ${getCurrency()}`;
  };

  const switchMode = () => {
    setMode(mode === 'from_ht' ? 'from_ttc' : 'from_ht');
    setAmount(0);
  };

  const historyColumns = [
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      width: 130
    },
    {
      title: 'Mode',
      dataIndex: 'mode',
      key: 'mode',
      width: 100,
      render: (mode) => (
        <Tag color={mode === 'from_ht' ? 'blue' : 'green'}>
          {mode === 'from_ht' ? 'HT → TTC' : 'TTC → HT'}
        </Tag>
      )
    },
    {
      title: 'Montant',
      dataIndex: 'amount',
      key: 'amount',
      render: (val) => formatCurrency(val),
      align: 'right'
    },
    {
      title: 'Taux',
      dataIndex: 'rate',
      key: 'rate',
      render: (rate) => `${rate}%`,
      align: 'center'
    },
    {
      title: 'Résultat',
      dataIndex: 'result',
      key: 'result',
      render: (result) => (
        <Space direction="vertical" size="small">
          <span>HT: {formatCurrency(result.amount_ht)}</span>
          <span>TVA: {formatCurrency(result.vat_amount)}</span>
          <strong>TTC: {formatCurrency(result.amount_ttc)}</strong>
        </Space>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => loadFromHistory(record)}
        >
          Recharger
        </Button>
      )
    }
  ];

  const getTaxLabel = () => {
    return country === 'US' ? 'Sales Tax' : 'TVA';
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16}>
        {/* Calculateur principal */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <CalculatorOutlined />
                <span>Calculateur {getTaxLabel()}</span>
                <span style={{ color: '#666', fontSize: 14 }}>
                  {country === 'MA' && '🇲🇦 Maroc'}
                  {country === 'FR' && '🇫🇷 France'}
                  {country === 'US' && '🇺🇸 USA'}
                </span>
              </Space>
            }
          >
            {/* Mode de calcul */}
            <div style={{ textAlign: 'center', marginBottom: 24 }}>
              <Radio.Group
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                size="large"
                buttonStyle="solid"
              >
                <Radio.Button value="from_ht">
                  Partir du montant HT (Hors Taxes)
                </Radio.Button>
                <Radio.Button value="from_ttc">
                  Partir du montant TTC (Toutes Taxes Comprises)
                </Radio.Button>
              </Radio.Group>
              <Button
                type="link"
                icon={<SwapOutlined />}
                onClick={switchMode}
                style={{ marginTop: 8 }}
              >
                Inverser le mode
              </Button>
            </div>

            <Divider />

            {/* Saisie montant */}
            <Row justify="center" style={{ marginBottom: 32 }}>
              <Col xs={24} sm={18} md={14}>
                <Card size="small" style={{ background: '#fafafa' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 16, marginBottom: 8, color: '#666' }}>
                      {mode === 'from_ht' ? 'Montant HT' : 'Montant TTC'}
                    </div>
                    <InputNumber
                      size="large"
                      value={amount}
                      onChange={setAmount}
                      min={0}
                      step={1}
                      precision={2}
                      style={{
                        width: '100%',
                        fontSize: 32,
                        fontWeight: 'bold',
                        textAlign: 'center'
                      }}
                      addonAfter={getCurrency()}
                    />
                  </div>
                </Card>
              </Col>
            </Row>

            {/* Sélection taux TVA */}
            <div style={{ marginBottom: 32 }}>
              <h3 style={{ textAlign: 'center', marginBottom: 16 }}>
                Sélectionner le taux {getTaxLabel()}
              </h3>
              <Row gutter={[16, 16]} justify="center">
                {getVATRates().map((rate) => (
                  <Col key={rate.value} xs={12} sm={8} md={6}>
                    <Card
                      hoverable
                      onClick={() => setSelectedRate(rate.value)}
                      style={{
                        textAlign: 'center',
                        border:
                          selectedRate === rate.value
                            ? '2px solid #1890ff'
                            : '1px solid #d9d9d9',
                        background:
                          selectedRate === rate.value ? '#e6f7ff' : '#fff',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ fontSize: 24, fontWeight: 'bold', color: '#1890ff' }}>
                        {rate.label}
                      </div>
                      <div style={{ fontSize: 12, color: '#666' }}>
                        {rate.description}
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>

            <Divider>Résultat du calcul</Divider>

            {/* Résultats */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col xs={24} sm={8}>
                <Card style={{ background: '#f0f5ff' }}>
                  <Statistic
                    title="Montant HT"
                    value={result.amount_ht}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ color: '#1890ff', fontSize: 24 }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card style={{ background: '#fff7e6' }}>
                  <Statistic
                    title={`${getTaxLabel()} (${selectedRate}%)`}
                    value={result.vat_amount}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ color: '#fa8c16', fontSize: 24 }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card style={{ background: '#f6ffed' }}>
                  <Statistic
                    title="Montant TTC"
                    value={result.amount_ttc}
                    precision={2}
                    suffix={getCurrency()}
                    valueStyle={{ color: '#52c41a', fontSize: 24, fontWeight: 'bold' }}
                  />
                </Card>
              </Col>
            </Row>

            {/* Formule */}
            <Alert
              message="Formule de calcul"
              description={
                <div style={{ fontSize: 14 }}>
                  {mode === 'from_ht' ? (
                    <>
                      <p>
                        <strong>Montant TTC</strong> = Montant HT × (1 +{' '}
                        {selectedRate}%)
                      </p>
                      <p>
                        = {formatCurrency(result.amount_ht)} × 1.
                        {selectedRate.toString().replace('.', '')} ={' '}
                        {formatCurrency(result.amount_ttc)}
                      </p>
                    </>
                  ) : (
                    <>
                      <p>
                        <strong>Montant HT</strong> = Montant TTC / (1 +{' '}
                        {selectedRate}%)
                      </p>
                      <p>
                        = {formatCurrency(result.amount_ttc)} / 1.
                        {selectedRate.toString().replace('.', '')} ={' '}
                        {formatCurrency(result.amount_ht)}
                      </p>
                    </>
                  )}
                </div>
              }
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            {/* Actions */}
            <Row justify="center">
              <Space size="large">
                <Button
                  type="primary"
                  size="large"
                  icon={<SaveOutlined />}
                  onClick={saveToHistory}
                  disabled={amount === 0}
                >
                  Enregistrer dans l'historique
                </Button>
                <Button
                  size="large"
                  onClick={() => {
                    setAmount(0);
                    setResult({ amount_ht: 0, vat_amount: 0, amount_ttc: 0 });
                  }}
                >
                  Réinitialiser
                </Button>
              </Space>
            </Row>
          </Card>
        </Col>

        {/* Historique */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <HistoryOutlined />
                <span>Historique des calculs</span>
              </Space>
            }
            extra={
              history.length > 0 && (
                <Button
                  type="link"
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={clearHistory}
                >
                  Effacer tout
                </Button>
              )
            }
          >
            {history.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                <HistoryOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>Aucun calcul enregistré</p>
                <p style={{ fontSize: 12 }}>
                  Vos 10 derniers calculs apparaîtront ici
                </p>
              </div>
            ) : (
              <Table
                dataSource={history}
                columns={historyColumns}
                rowKey="id"
                pagination={false}
                size="small"
                scroll={{ y: 600 }}
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default VATCalculator;
