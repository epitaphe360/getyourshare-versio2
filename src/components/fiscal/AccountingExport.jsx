/**
 * Export Comptable - Multi-formats
 * FEC (France obligatoire), CSV, Sage, EBP, Cegid
 */

import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Form, Select, DatePicker, Button, Space,
  Table, Alert, Progress, message, Radio, InputNumber, Divider,
  Checkbox, Tag, Statistic
} from 'antd';
import {
  DownloadOutlined,
  FileExcelOutlined,
  EyeOutlined,
  HistoryOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

const AccountingExport = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [exportType, setExportType] = useState('fec');
  const [country, setCountry] = useState('FR');
  const [period, setPeriod] = useState([
    dayjs().startOf('year'),
    dayjs()
  ]);
  const [preview, setPreview] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({
    total_transactions: 0,
    total_amount: 0,
    estimated_size_kb: 0
  });

  useEffect(() => {
    fetchCountry();
    fetchHistory();
  }, []);

  useEffect(() => {
    if (period) {
      fetchStats();
    }
  }, [period, exportType]);

  const fetchCountry = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setCountry(response.data.country || 'FR');
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/accounting/exports');
      setHistory(response.data);
    } catch (error) {
      console.error('Erreur chargement historique:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const [start, end] = period;
      const response = await axios.get('/api/accounting/stats', {
        params: {
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD')
        }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const handlePreview = async () => {
    try {
      setLoading(true);
      const [start, end] = period;
      const response = await axios.get('/api/accounting/preview', {
        params: {
          export_type: exportType,
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD'),
          limit: 50
        }
      });
      setPreview(response.data);
      setShowPreview(true);
    } catch (error) {
      message.error('Erreur lors de l\'aperçu');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      const [start, end] = period;
      const values = await form.validateFields();
      
      const response = await axios.post(
        '/api/accounting/export',
        {
          export_type: exportType,
          start_date: start.format('YYYY-MM-DD'),
          end_date: end.format('YYYY-MM-DD'),
          options: values
        },
        { responseType: 'blob' }
      );

      const filename = getFilename();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Export généré avec succès !');
      fetchHistory(); // Rafraîchir l'historique
    } catch (error) {
      message.error('Erreur lors de l\'export');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getFilename = () => {
    const [start, end] = period;
    const dateRange = `${start.format('YYYYMMDD')}_${end.format('YYYYMMDD')}`;
    
    switch (exportType) {
      case 'fec':
        return `${dayjs().format('YYYYMMDD')}FEC.txt`;
      case 'csv':
        return `Export_Comptable_${dateRange}.csv`;
      case 'sage':
        return `Export_Sage_${dateRange}.txt`;
      case 'ebp':
        return `Export_EBP_${dateRange}.txt`;
      case 'cegid':
        return `Export_Cegid_${dateRange}.txt`;
      default:
        return `Export_${dateRange}.txt`;
    }
  };

  const getExportFormats = () => {
    const formats = [
      {
        value: 'fec',
        label: 'FEC - Fichier des Écritures Comptables',
        description: '🇫🇷 Format obligatoire en France',
        mandatory: country === 'FR',
        icon: '📄'
      },
      {
        value: 'csv',
        label: 'CSV - Format générique',
        description: 'Compatible tous logiciels',
        mandatory: false,
        icon: '📊'
      },
      {
        value: 'sage',
        label: 'Sage 100',
        description: 'Format Sage Compta & Gestion',
        mandatory: false,
        icon: '💼'
      },
      {
        value: 'ebp',
        label: 'EBP Compta',
        description: 'Format EBP Comptabilité',
        mandatory: false,
        icon: '🧾'
      },
      {
        value: 'cegid',
        label: 'Cegid',
        description: 'Format Cegid Expert',
        mandatory: false,
        icon: '🏢'
      }
    ];

    return formats;
  };

  const historyColumns = [
    {
      title: 'Date',
      dataIndex: 'exported_at',
      key: 'exported_at',
      render: (date) => dayjs(date).format('DD/MM/YYYY HH:mm'),
      width: 150
    },
    {
      title: 'Type',
      dataIndex: 'export_type',
      key: 'export_type',
      render: (type) => {
        const format = getExportFormats().find(f => f.value === type);
        return (
          <Tag color="blue">
            {format?.icon} {format?.label || type.toUpperCase()}
          </Tag>
        );
      }
    },
    {
      title: 'Période',
      key: 'period',
      render: (_, record) => (
        <span>
          {dayjs(record.period_start).format('DD/MM/YYYY')} →{' '}
          {dayjs(record.period_end).format('DD/MM/YYYY')}
        </span>
      )
    },
    {
      title: 'Lignes',
      dataIndex: 'line_count',
      key: 'line_count',
      render: (count) => count?.toLocaleString() || '-',
      align: 'right'
    },
    {
      title: 'Taille',
      dataIndex: 'file_size_kb',
      key: 'file_size_kb',
      render: (size) => `${(size || 0).toFixed(1)} KB`,
      align: 'right'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<DownloadOutlined />}
          onClick={() => handleRedownload(record.id)}
        >
          Re-télécharger
        </Button>
      )
    }
  ];

  const handleRedownload = async (exportId) => {
    try {
      const response = await axios.get(`/api/accounting/exports/${exportId}/download`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'export.txt');
      document.body.appendChild(link);
      link.click();
      link.remove();

      message.success('Fichier re-téléchargé !');
    } catch (error) {
      message.error('Erreur lors du téléchargement');
      console.error(error);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16}>
        {/* Configuration export */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <FileExcelOutlined />
                <span>Générer un export comptable</span>
                <span style={{ color: '#666', fontSize: 14 }}>
                  {country === 'FR' && '🇫🇷 France'}
                  {country === 'MA' && '🇲🇦 Maroc'}
                  {country === 'US' && '🇺🇸 USA'}
                </span>
              </Space>
            }
          >
            <Form form={form} layout="vertical">
              {/* Sélection format */}
              <Form.Item label="Format d'export">
                <Radio.Group
                  value={exportType}
                  onChange={(e) => setExportType(e.target.value)}
                  buttonStyle="solid"
                  size="large"
                >
                  {getExportFormats().map(format => (
                    <Radio.Button
                      key={format.value}
                      value={format.value}
                      style={{ height: 'auto', padding: '12px 16px' }}
                    >
                      <div>
                        <div style={{ fontSize: 16, fontWeight: 'bold' }}>
                          {format.icon} {format.label}
                        </div>
                        <div style={{ fontSize: 12, color: '#666' }}>
                          {format.description}
                        </div>
                        {format.mandatory && (
                          <Tag color="red" style={{ marginTop: 4 }}>
                            Obligatoire
                          </Tag>
                        )}
                      </div>
                    </Radio.Button>
                  ))}
                </Radio.Group>
              </Form.Item>

              {/* Période */}
              <Form.Item
                label="Période d'export"
                name="period"
                rules={[{ required: true, message: 'Sélectionnez une période' }]}
              >
                <RangePicker
                  value={period}
                  onChange={setPeriod}
                  format="DD/MM/YYYY"
                  style={{ width: '100%' }}
                  size="large"
                />
              </Form.Item>

              <Alert
                message={`Période: ${period[0].format('DD MMMM YYYY')} au ${period[1].format('DD MMMM YYYY')}`}
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />

              {/* Options selon format */}
              {exportType === 'fec' && (
                <Alert
                  message="Format FEC - Normes françaises"
                  description={
                    <div>
                      <p>Le fichier sera généré selon les normes de la DGI (BOI-CF-IOR-60-40-20):</p>
                      <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                        <li>Séparateur: | (pipe)</li>
                        <li>Encodage: UTF-8</li>
                        <li>Format date: YYYYMMDD</li>
                        <li>18 colonnes obligatoires</li>
                        <li>Nom fichier: YYYYMMDDSIRETFEC.txt</li>
                      </ul>
                    </div>
                  }
                  type="warning"
                  showIcon
                  style={{ marginBottom: 24 }}
                />
              )}

              {exportType === 'csv' && (
                <>
                  <Form.Item
                    label="Séparateur"
                    name="delimiter"
                    initialValue=","
                  >
                    <Radio.Group>
                      <Radio.Button value=",">Virgule (,)</Radio.Button>
                      <Radio.Button value=";">Point-virgule (;)</Radio.Button>
                      <Radio.Button value="\t">Tabulation</Radio.Button>
                    </Radio.Group>
                  </Form.Item>

                  <Form.Item
                    label="Encodage"
                    name="encoding"
                    initialValue="UTF-8"
                  >
                    <Select>
                      <Option value="UTF-8">UTF-8</Option>
                      <Option value="ISO-8859-1">ISO-8859-1 (Latin-1)</Option>
                      <Option value="Windows-1252">Windows-1252</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="Séparateur décimal"
                    name="decimal_separator"
                    initialValue="."
                  >
                    <Radio.Group>
                      <Radio.Button value=".">Point (.)</Radio.Button>
                      <Radio.Button value=",">Virgule (,)</Radio.Button>
                    </Radio.Group>
                  </Form.Item>

                  <Form.Item name="include_headers" valuePropName="checked" initialValue={true}>
                    <Checkbox>Inclure la ligne d'en-têtes</Checkbox>
                  </Form.Item>
                </>
              )}

              <Divider />

              {/* Statistiques */}
              <Row gutter={16} style={{ marginBottom: 24 }}>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="Transactions"
                      value={stats.total_transactions}
                      suffix="écritures"
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="Montant total"
                      value={stats.total_amount}
                      precision={2}
                      suffix="€"
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small">
                    <Statistic
                      title="Taille estimée"
                      value={stats.estimated_size_kb}
                      precision={1}
                      suffix="KB"
                      valueStyle={{ fontSize: 20 }}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Actions */}
              <Space style={{ width: '100%' }} direction="vertical" size="middle">
                <Button
                  size="large"
                  icon={<EyeOutlined />}
                  onClick={handlePreview}
                  loading={loading}
                  block
                >
                  Aperçu des données (50 premières lignes)
                </Button>

                <Button
                  type="primary"
                  size="large"
                  icon={<DownloadOutlined />}
                  onClick={handleExport}
                  loading={loading}
                  block
                  style={{ height: 56, fontSize: 16, fontWeight: 'bold' }}
                >
                  Générer et télécharger l'export
                </Button>
              </Space>

              {exportType === 'fec' && country === 'FR' && (
                <Alert
                  message="Rappel légal"
                  description="Le FEC est obligatoire pour tout contrôle fiscal en France. Conservez une copie de chaque export généré."
                  type="error"
                  showIcon
                  icon={<ExclamationCircleOutlined />}
                  style={{ marginTop: 24 }}
                />
              )}
            </Form>
          </Card>

          {/* Aperçu */}
          {showPreview && preview && (
            <Card
              title="Aperçu des données"
              style={{ marginTop: 16 }}
              extra={
                <Button
                  type="link"
                  onClick={() => setShowPreview(false)}
                >
                  Masquer
                </Button>
              }
            >
              <Alert
                message={`${preview.total_lines} lignes au total (affichage des 50 premières)`}
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <div style={{
                background: '#f5f5f5',
                padding: '16px',
                borderRadius: '4px',
                maxHeight: '400px',
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: '12px'
              }}>
                <pre style={{ margin: 0 }}>
                  {preview.sample_data}
                </pre>
              </div>
            </Card>
          )}
        </Col>

        {/* Historique */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <HistoryOutlined />
                <span>Historique des exports</span>
              </Space>
            }
          >
            {history.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                <FileExcelOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>Aucun export généré</p>
                <p style={{ fontSize: 12 }}>
                  Vos exports apparaîtront ici
                </p>
              </div>
            ) : (
              <Table
                dataSource={history}
                columns={historyColumns}
                rowKey="id"
                pagination={{ pageSize: 10 }}
                scroll={{ y: 600 }}
                size="small"
              />
            )}
          </Card>

          {/* Aide */}
          <Card
            title="📚 Guide des formats"
            style={{ marginTop: 16 }}
            size="small"
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <h4>FEC (Fichier des Écritures Comptables)</h4>
                <p style={{ fontSize: 12, color: '#666' }}>
                  Format obligatoire en France depuis 2014. Contient toutes les écritures
                  comptables de l'exercice. Doit être fourni lors d'un contrôle fiscal.
                </p>
                <Tag color="red">Obligatoire FR</Tag>
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <div>
                <h4>CSV (Comma-Separated Values)</h4>
                <p style={{ fontSize: 12, color: '#666' }}>
                  Format générique compatible avec Excel, LibreOffice, et la plupart des
                  logiciels comptables. Personnalisable (séparateur, encodage).
                </p>
                <Tag color="blue">Universel</Tag>
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <div>
                <h4>Sage 100</h4>
                <p style={{ fontSize: 12, color: '#666' }}>
                  Format spécifique pour l'import dans Sage Compta & Gestion.
                </p>
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <div>
                <h4>EBP Compta</h4>
                <p style={{ fontSize: 12, color: '#666' }}>
                  Format adapté pour EBP Comptabilité (PME françaises).
                </p>
              </div>

              <Divider style={{ margin: '8px 0' }} />

              <div>
                <h4>Cegid</h4>
                <p style={{ fontSize: 12, color: '#666' }}>
                  Format pour Cegid Expert (cabinets comptables).
                </p>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AccountingExport;
