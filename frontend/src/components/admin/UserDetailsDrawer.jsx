import React, { useState, useEffect } from 'react';
import {
  Drawer, Descriptions, Tag, Button, Space, Tabs, Timeline, Card,
  Statistic, Row, Col, Empty, Avatar, Divider, message
} from 'antd';
import {
  UserOutlined, MailOutlined, PhoneOutlined, CalendarOutlined,
  ShopOutlined, TrophyOutlined, DollarOutlined, CrownOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined,
  TeamOutlined, EditOutlined, LockOutlined, UnlockOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { TabPane } = Tabs;

/**
 * Drawer de détails utilisateur avec onglets
 */
const UserDetailsDrawer = ({ visible, onClose, user, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [activity, setActivity] = useState([]);
  const [subscriptionDetails, setSubscriptionDetails] = useState(null);
  const [userStats, setUserStats] = useState(null);

  useEffect(() => {
    if (visible && user) {
      fetchDetails();
    }
  }, [visible, user]);

  const fetchDetails = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      const [activityRes, subRes, statsRes] = await Promise.all([
        api.get(`/api/admin/users/${user.id}/activity`).catch(() => ({ data: { activity: [] } })),
        api.get(`/api/admin/users/${user.id}/subscription`).catch(() => ({ data: { subscription: null } })),
        api.get(`/api/admin/users/${user.id}/stats`).catch(() => ({ data: { stats: null } }))
      ]);

      setActivity(activityRes.data.activity || []);
      setSubscriptionDetails(subRes.data.subscription);
      setUserStats(statsRes.data.stats);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspend = async () => {
    try {
      const newStatus = user.status === 'suspended' ? 'active' : 'suspended';
      await api.patch(`/api/admin/users/${user.id}/status`, { status: newStatus });
      message.success(`Utilisateur ${newStatus === 'suspended' ? 'suspendu' : 'réactivé'}`);
      onRefresh();
      onClose();
    } catch (error) {
      message.error('Erreur lors de la modification du statut');
    }
  };

  const handleResetPassword = async () => {
    try {
      await api.post(`/api/admin/users/${user.id}/reset-password`);
      message.success('Email de réinitialisation envoyé');
    } catch (error) {
      message.error('Erreur lors de l\'envoi');
    }
  };

  if (!user) return null;

  const getRoleIcon = (role) => {
    const icons = {
      admin: <CrownOutlined style={{ color: '#ff4d4f' }} />,
      merchant: <ShopOutlined style={{ color: '#1890ff' }} />,
      influencer: <TrophyOutlined style={{ color: '#722ed1' }} />,
      commercial: <TeamOutlined style={{ color: '#52c41a' }} />,
      sales_rep: <DollarOutlined style={{ color: '#faad14' }} />
    };
    return icons[role] || <UserOutlined />;
  };

  const getRoleTag = (role) => {
    const config = {
      admin: { color: 'red', text: 'Admin' },
      merchant: { color: 'blue', text: 'Marchand' },
      influencer: { color: 'purple', text: 'Influenceur' },
      commercial: { color: 'green', text: 'Commercial' },
      sales_rep: { color: 'orange', text: 'Représentant' },
      user: { color: 'default', text: 'Utilisateur' }
    };
    const roleConfig = config[role] || config.user;
    return (
      <Tag color={roleConfig.color} icon={getRoleIcon(role)}>
        {roleConfig.text}
      </Tag>
    );
  };

  const getStatusTag = (status) => {
    const config = {
      active: { color: 'success', icon: <CheckCircleOutlined />, text: 'Actif' },
      suspended: { color: 'error', icon: <CloseCircleOutlined />, text: 'Suspendu' },
      pending: { color: 'warning', icon: <ClockCircleOutlined />, text: 'En attente' }
    };
    const statusConfig = config[status] || config.active;
    return (
      <Tag color={statusConfig.color} icon={statusConfig.icon}>
        {statusConfig.text}
      </Tag>
    );
  };

  return (
    <Drawer
      title={
        <Space>
          <Avatar size={40} icon={<UserOutlined />} src={user.avatar} />
          <div>
            <div style={{ fontWeight: 500 }}>
              {user.first_name && user.last_name
                ? `${user.first_name} ${user.last_name}`
                : user.email}
            </div>
            <div style={{ fontSize: '12px', fontWeight: 'normal', color: '#888' }}>
              {user.email}
            </div>
          </div>
        </Space>
      }
      open={visible}
      onClose={onClose}
      width={600}
      extra={
        <Space>
          <Button
            icon={<EditOutlined />}
            onClick={() => {
              onClose();
              // Trigger edit modal from parent
            }}
          >
            Modifier
          </Button>
          <Button
            icon={user.status === 'suspended' ? <UnlockOutlined /> : <LockOutlined />}
            danger={user.status !== 'suspended'}
            onClick={handleSuspend}
          >
            {user.status === 'suspended' ? 'Réactiver' : 'Suspendre'}
          </Button>
        </Space>
      }
    >
      <Tabs defaultActiveKey="1">
        {/* Onglet Informations */}
        <TabPane tab="Informations" key="1">
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label={<><MailOutlined /> Email</>}>
              {user.email}
            </Descriptions.Item>

            {user.phone && (
              <Descriptions.Item label={<><PhoneOutlined /> Téléphone</>}>
                {user.phone}
              </Descriptions.Item>
            )}

            <Descriptions.Item label="Rôle">
              {getRoleTag(user.role)}
            </Descriptions.Item>

            <Descriptions.Item label="Statut">
              {getStatusTag(user.status || 'active')}
            </Descriptions.Item>

            {user.company && (
              <Descriptions.Item label={<><ShopOutlined /> Entreprise</>}>
                {user.company}
              </Descriptions.Item>
            )}

            <Descriptions.Item label={<><CalendarOutlined /> Inscription</>}>
              {user.created_at
                ? new Date(user.created_at).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : 'N/A'}
            </Descriptions.Item>

            <Descriptions.Item label="Dernière connexion">
              {user.last_login
                ? new Date(user.last_login).toLocaleDateString('fr-FR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : 'Jamais connecté'}
            </Descriptions.Item>

            {user.last_ip && (
              <Descriptions.Item label="Dernière IP">
                {user.last_ip}
              </Descriptions.Item>
            )}
          </Descriptions>

          <Divider />

          <Button
            block
            icon={<LockOutlined />}
            onClick={handleResetPassword}
          >
            Réinitialiser le mot de passe
          </Button>
        </TabPane>

        {/* Onglet Abonnement */}
        <TabPane tab="Abonnement" key="2">
          {subscriptionDetails ? (
            <Card>
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="Plan">
                  <Tag color="blue">{subscriptionDetails.plan_name}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Statut">
                  {getStatusTag(subscriptionDetails.status)}
                </Descriptions.Item>
                <Descriptions.Item label="Prix">
                  {subscriptionDetails.price} {subscriptionDetails.currency || 'MAD'}
                </Descriptions.Item>
                <Descriptions.Item label="Période">
                  Du {new Date(subscriptionDetails.current_period_start).toLocaleDateString('fr-FR')}
                  <br />
                  Au {new Date(subscriptionDetails.current_period_end).toLocaleDateString('fr-FR')}
                </Descriptions.Item>
                {subscriptionDetails.trial_end && (
                  <Descriptions.Item label="Fin d'essai">
                    {new Date(subscriptionDetails.trial_end).toLocaleDateString('fr-FR')}
                  </Descriptions.Item>
                )}
              </Descriptions>
            </Card>
          ) : (
            <Empty description="Aucun abonnement actif" />
          )}
        </TabPane>

        {/* Onglet Statistiques */}
        <TabPane tab="Statistiques" key="3">
          {userStats ? (
            <div>
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Card>
                    <Statistic
                      title="Connexions"
                      value={userStats.login_count || 0}
                      prefix={<UserOutlined />}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card>
                    <Statistic
                      title="Depuis"
                      value={
                        user.created_at
                          ? Math.floor(
                              (new Date() - new Date(user.created_at)) /
                                (1000 * 60 * 60 * 24)
                            )
                          : 0
                      }
                      suffix="jours"
                      prefix={<CalendarOutlined />}
                    />
                  </Card>
                </Col>
              </Row>

              {user.role === 'merchant' && (
                <>
                  <Divider />
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Card>
                        <Statistic
                          title="Produits"
                          value={userStats.products_count || 0}
                          prefix={<ShopOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card>
                        <Statistic
                          title="Campagnes"
                          value={userStats.campaigns_count || 0}
                          prefix={<TrophyOutlined />}
                        />
                      </Card>
                    </Col>
                  </Row>
                </>
              )}

              {user.role === 'influencer' && (
                <>
                  <Divider />
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Card>
                        <Statistic
                          title="Clics"
                          value={userStats.clicks_count || 0}
                          prefix={<TeamOutlined />}
                        />
                      </Card>
                    </Col>
                    <Col span={12}>
                      <Card>
                        <Statistic
                          title="Commissions"
                          value={userStats.commission_total || 0}
                          prefix={<DollarOutlined />}
                          suffix="MAD"
                        />
                      </Card>
                    </Col>
                  </Row>
                </>
              )}
            </div>
          ) : (
            <Empty description="Aucune statistique disponible" />
          )}
        </TabPane>

        {/* Onglet Activité */}
        <TabPane tab="Activité récente" key="4">
          {activity && activity.length > 0 ? (
            <Timeline mode="left">
              {activity.map((event, index) => (
                <Timeline.Item
                  key={index}
                  color={event.type === 'error' ? 'red' : 'blue'}
                >
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontWeight: 500 }}>{event.action}</div>
                    <div style={{ fontSize: '12px', color: '#888' }}>
                      {event.created_at
                        ? new Date(event.created_at).toLocaleDateString('fr-FR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })
                        : ''}
                    </div>
                    {event.details && (
                      <div style={{ fontSize: '12px', marginTop: '4px', color: '#666' }}>
                        {event.details}
                      </div>
                    )}
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          ) : (
            <Empty description="Aucune activité récente" />
          )}
        </TabPane>
      </Tabs>
    </Drawer>
  );
};

export default UserDetailsDrawer;
