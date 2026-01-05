import React, { useState, useEffect } from 'react';
import { Modal, Tabs, Descriptions, Tag, Timeline, Card, Button, Space, message, Empty } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  UserOutlined,
  CalendarOutlined,
  DollarOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import api from '../../utils/api';

const { TabPane } = Tabs;

/**
 * Modal affichant les détails d'un abonnement
 */
const SubscriptionDetailsModal = ({ visible, onCancel, subscription, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [details, setDetails] = useState(null);
  const [history, setHistory] = useState([]);
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    if (visible && subscription) {
      fetchDetails();
    }
  }, [visible, subscription]);

  const fetchDetails = async () => {
    if (!subscription?.id) return;
    
    setLoading(true);
    try {
      // Récupérer les détails complets
      const [detailsRes, historyRes, usageRes] = await Promise.all([
        api.get(`/api/admin/subscriptions/${subscription.id}`),
        api.get(`/api/admin/subscriptions/${subscription.id}/history`).catch(() => ({ data: { history: [] } })),
        api.get(`/api/admin/subscriptions/${subscription.id}/usage`).catch(() => ({ data: { usage: null } })),
      ]);

      if (detailsRes.data.success) {
        setDetails(detailsRes.data.subscription);
      }
      if (historyRes.data.history) {
        setHistory(historyRes.data.history);
      }
      if (usageRes.data.usage) {
        setUsage(usageRes.data.usage);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des détails:', error);
      message.error('Erreur lors du chargement des détails');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await api.post(`/api/admin/subscriptions/${subscription.id}/cancel`, {
        reason: 'Annulé par admin',
        immediate: false,
      });
      message.success('Abonnement annulé avec succès');
      onRefresh();
      onCancel();
    } catch (error) {
      console.error('Erreur lors de l\'annulation:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de l\'annulation');
    }
  };

  const handleReactivate = async () => {
    try {
      await api.post(`/api/admin/subscriptions/${subscription.id}/reactivate`);
      message.success('Abonnement réactivé avec succès');
      onRefresh();
      fetchDetails();
    } catch (error) {
      console.error('Erreur lors de la réactivation:', error);
      message.error(error.response?.data?.detail || 'Erreur lors de la réactivation');
    }
  };

  if (!subscription) return null;

  const statusConfig = {
    active: { color: 'success', icon: <CheckCircleOutlined />, text: 'Actif' },
    trialing: { color: 'processing', icon: <SyncOutlined spin />, text: 'Essai gratuit' },
    past_due: { color: 'warning', icon: <CloseCircleOutlined />, text: 'Paiement en retard' },
    canceled: { color: 'default', icon: <CloseCircleOutlined />, text: 'Annulé' },
    incomplete: { color: 'error', icon: <CloseCircleOutlined />, text: 'Incomplet' },
  };

  const currentStatus = statusConfig[subscription.status] || statusConfig.active;

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>Détails de l'Abonnement</span>
          <Tag color={currentStatus.color} icon={currentStatus.icon}>
            {currentStatus.text}
          </Tag>
        </div>
      }
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="close" onClick={onCancel}>
          Fermer
        </Button>,
        subscription.status === 'canceled' ? (
          <Button key="reactivate" type="primary" onClick={handleReactivate}>
            Réactiver
          </Button>
        ) : subscription.status === 'active' && (
          <Button key="cancel" danger onClick={handleCancelSubscription}>
            Annuler l'abonnement
          </Button>
        ),
      ]}
      width={800}
    >
      <Tabs defaultActiveKey="1">
        {/* Onglet Informations */}
        <TabPane tab="Informations" key="1">
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label={<><UserOutlined /> Utilisateur</>}>
              <div>
                <div style={{ fontWeight: 500 }}>{subscription.user_name || 'N/A'}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>{subscription.user_email}</div>
              </div>
            </Descriptions.Item>

            <Descriptions.Item label="Plan">
              <div>
                <div style={{ fontWeight: 500 }}>{subscription.plan_name}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>
                  {subscription.plan_type} • Code: {subscription.plan_code || 'N/A'}
                </div>
              </div>
            </Descriptions.Item>

            <Descriptions.Item label={<><DollarOutlined /> Prix</>}>
              <div style={{ fontWeight: 500 }}>
                {subscription.plan_price 
                  ? `${subscription.plan_price.toFixed(2)} ${subscription.currency || 'MAD'}`
                  : 'Gratuit'
                }
              </div>
            </Descriptions.Item>

            <Descriptions.Item label="Statut">
              <Tag color={currentStatus.color} icon={currentStatus.icon}>
                {currentStatus.text}
              </Tag>
            </Descriptions.Item>

            <Descriptions.Item label={<><CalendarOutlined /> Période actuelle</>}>
              <div style={{ fontSize: '12px' }}>
                <div>
                  Début: {subscription.current_period_start 
                    ? new Date(subscription.current_period_start).toLocaleDateString('fr-FR', { 
                        year: 'numeric', month: 'long', day: 'numeric' 
                      })
                    : 'N/A'
                  }
                </div>
                <div>
                  Fin: {subscription.current_period_end 
                    ? new Date(subscription.current_period_end).toLocaleDateString('fr-FR', { 
                        year: 'numeric', month: 'long', day: 'numeric' 
                      })
                    : 'N/A'
                  }
                </div>
              </div>
            </Descriptions.Item>

            {subscription.trial_end && (
              <Descriptions.Item label={<><ClockCircleOutlined /> Essai gratuit</>}>
                Jusqu'au {new Date(subscription.trial_end).toLocaleDateString('fr-FR', {
                  year: 'numeric', month: 'long', day: 'numeric'
                })}
              </Descriptions.Item>
            )}

            {subscription.canceled_at && (
              <Descriptions.Item label="Date d'annulation">
                {new Date(subscription.canceled_at).toLocaleDateString('fr-FR', {
                  year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                })}
              </Descriptions.Item>
            )}

            {subscription.cancellation_reason && (
              <Descriptions.Item label="Raison d'annulation">
                {subscription.cancellation_reason}
              </Descriptions.Item>
            )}

            {subscription.cancel_at_period_end && (
              <Descriptions.Item label="Annulation programmée">
                <Tag color="warning">
                  Sera annulé le {new Date(subscription.current_period_end).toLocaleDateString('fr-FR')}
                </Tag>
              </Descriptions.Item>
            )}

            <Descriptions.Item label="Créé le">
              {subscription.created_at 
                ? new Date(subscription.created_at).toLocaleDateString('fr-FR', {
                    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                  })
                : 'N/A'
              }
            </Descriptions.Item>
          </Descriptions>
        </TabPane>

        {/* Onglet Utilisation */}
        <TabPane tab="Utilisation" key="2">
          {usage ? (
            <Card>
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="Membres d'équipe">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500 }}>
                        {usage.team_members_used} / {usage.team_members_limit || '∞'}
                      </div>
                      <div style={{ fontSize: '12px', color: '#888' }}>
                        {usage.team_members_limit 
                          ? `${((usage.team_members_used / usage.team_members_limit) * 100).toFixed(0)}% utilisé`
                          : 'Illimité'
                        }
                      </div>
                    </div>
                    {usage.team_members_limit && (
                      <Tag color={usage.team_members_used >= usage.team_members_limit ? 'error' : 'success'}>
                        {usage.team_members_used >= usage.team_members_limit ? 'Limite atteinte' : 'Disponible'}
                      </Tag>
                    )}
                  </div>
                </Descriptions.Item>

                <Descriptions.Item label="Domaines">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500 }}>
                        {usage.domains_used} / {usage.domains_limit || '∞'}
                      </div>
                      <div style={{ fontSize: '12px', color: '#888' }}>
                        {usage.domains_limit 
                          ? `${((usage.domains_used / usage.domains_limit) * 100).toFixed(0)}% utilisé`
                          : 'Illimité'
                        }
                      </div>
                    </div>
                    {usage.domains_limit && (
                      <Tag color={usage.domains_used >= usage.domains_limit ? 'error' : 'success'}>
                        {usage.domains_used >= usage.domains_limit ? 'Limite atteinte' : 'Disponible'}
                      </Tag>
                    )}
                  </div>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          ) : (
            <Empty description="Aucune donnée d'utilisation disponible" />
          )}
        </TabPane>

        {/* Onglet Historique */}
        <TabPane tab="Historique" key="3">
          {history && history.length > 0 ? (
            <Timeline mode="left">
              {history.map((event, index) => {
                const eventIcons = {
                  created: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
                  updated: <SyncOutlined style={{ color: '#1890ff' }} />,
                  canceled: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
                  reactivated: <CheckCircleOutlined style={{ color: '#722ed1' }} />,
                };

                return (
                  <Timeline.Item
                    key={index}
                    dot={eventIcons[event.action] || <ClockCircleOutlined />}
                    color={event.action === 'canceled' ? 'red' : 'blue'}
                  >
                    <div style={{ marginBottom: '8px' }}>
                      <div style={{ fontWeight: 500 }}>{event.description || event.action}</div>
                      <div style={{ fontSize: '12px', color: '#888' }}>
                        {event.created_at 
                          ? new Date(event.created_at).toLocaleDateString('fr-FR', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : 'Date inconnue'
                        }
                      </div>
                      {event.details && (
                        <div style={{ fontSize: '12px', marginTop: '4px', color: '#666' }}>
                          {JSON.stringify(event.details)}
                        </div>
                      )}
                    </div>
                  </Timeline.Item>
                );
              })}
            </Timeline>
          ) : (
            <Empty description="Aucun historique disponible" />
          )}
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default SubscriptionDetailsModal;
