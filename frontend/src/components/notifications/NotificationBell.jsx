import React, { useState, useEffect } from 'react';
import {
  Badge, Dropdown, Button, List, Typography, Avatar, Space, Tag, Empty,
  Drawer, Tabs, Spin, Switch, message, Divider
} from 'antd';
import {
  BellOutlined, CheckOutlined, DeleteOutlined, SettingOutlined,
  ShoppingOutlined, DollarOutlined, UserOutlined, MessageOutlined,
  TrophyOutlined, WarningOutlined, InfoCircleOutlined
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import api from '../../utils/api';
import './NotificationBell.css';

const { Text, Title } = Typography;
const { TabPane } = Tabs;

/**
 * NotificationBell - Cloche de notifications avec dropdown
 */
const NotificationBell = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [settings, setSettings] = useState({
    email: true,
    push: true,
    sms: false,
    sales: true,
    payments: true,
    messages: true,
    system: true
  });
  const [ws, setWs] = useState(null);

  useEffect(() => {
    if (user) {
      fetchNotifications();
      connectWebSocket();
      loadSettings();
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [user]);

  const getNotificationTitle = (eventType) => {
    const titles = {
      commission_created: '💰 Nouvelle Commission',
      commission_updated: '📝 Commission Mise à Jour',
      payment_created: '💳 Nouveau Paiement',
      payment_status_changed: '🔄 Statut Paiement',
      sale_created: '🛒 Nouvelle Vente',
      dashboard_update: '📊 Mise à Jour Dashboard'
    };
    return titles[eventType] || 'Nouvelle Notification';
  };

  const formatNotificationMessage = (data) => {
    const { type, data: eventData } = data;
    switch(type) {
      case 'commission_created':
        return `Nouvelle commission de ${eventData.amount}€`;
      case 'payment_status_changed':
        return `Paiement ${eventData.status}: ${eventData.amount}€`;
      case 'sale_created':
        return `Nouvelle vente enregistrée`;
      default:
        return 'Vous avez une nouvelle notification';
    }
  };

  const mapEventType = (eventType) => {
    const typeMap = {
      commission_created: 'payment',
      commission_updated: 'payment',
      payment_created: 'payment',
      payment_status_changed: 'payment',
      sale_created: 'sale',
      dashboard_update: 'info'
    };
    return typeMap[eventType] || 'info';
  };

  const connectWebSocket = () => {
    try {
      const token = localStorage.getItem('token');
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://127.0.0.1:5000'}/ws`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('WebSocket notifications connecté');
        // S'authentifier avec le token
        if (user?.id) {
          websocket.send(JSON.stringify({
            type: 'auth',
            user_id: user.id
          }));
        }
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Ignorer les messages système (auth_success, pong, etc.)
          if (data.type === 'auth_success' || data.type === 'pong') {
            console.log('WebSocket:', data.type);
            return;
          }
          // Traiter les vraies notifications
          if (data.type && data.data) {
            handleNewNotification({
              id: Date.now(),
              title: getNotificationTitle(data.type),
              message: formatNotificationMessage(data),
              type: mapEventType(data.type),
              created_at: new Date().toISOString(),
              read: false
            });
          }
        } catch (error) {
          console.error('Erreur parsing WebSocket message:', error);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      websocket.onclose = () => {
        console.log('WebSocket notifications fermé');
        // Reconnexion après 30s (évite les boucles rapides)
        if (user?.id) {
          setTimeout(connectWebSocket, 30000);
        }
      };

      setWs(websocket);
    } catch (error) {
      console.error('Erreur connexion WebSocket:', error);
    }
  };

  const handleNewNotification = (notification) => {
    // Ajouter la nouvelle notification
    setNotifications(prev => [notification, ...prev]);
    setUnreadCount(prev => prev + 1);

    // Notification navigateur
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/logo192.png'
      });
    }

    // Son notification (optionnel)
    const audio = new Audio('/notification.mp3');
    audio.play().catch(() => {});
  };

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/notifications');
      setNotifications(response.data.notifications || []);
      setUnreadCount(response.data.unread_count || 0);
    } catch (error) {
      console.error('Erreur chargement notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await api.get('/api/notifications/settings');
      setSettings(response.data.settings || settings);
    } catch (error) {
      console.error('Erreur chargement paramètres:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.patch(`/api/notifications/${notificationId}/read`);
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Erreur marquage notification:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/api/notifications/mark-all-read');
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
      message.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      console.error('Erreur:', error);
      message.error('Erreur lors du marquage');
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await api.delete(`/api/notifications/${notificationId}`);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      message.success('Notification supprimée');
    } catch (error) {
      console.error('Erreur suppression:', error);
      message.error('Erreur lors de la suppression');
    }
  };

  const updateSettings = async (newSettings) => {
    try {
      await api.put('/api/notifications/settings', { settings: newSettings });
      setSettings(newSettings);
      message.success('Paramètres mis à jour');
    } catch (error) {
      console.error('Erreur mise à jour:', error);
      message.error('Erreur lors de la mise à jour');
    }
  };

  const getNotificationIcon = (type) => {
    const iconMap = {
      sale: <ShoppingOutlined style={{ color: '#52c41a' }} />,
      payment: <DollarOutlined style={{ color: '#1890ff' }} />,
      message: <MessageOutlined style={{ color: '#722ed1' }} />,
      user: <UserOutlined style={{ color: '#fa8c16' }} />,
      achievement: <TrophyOutlined style={{ color: '#faad14' }} />,
      warning: <WarningOutlined style={{ color: '#ff4d4f' }} />,
      info: <InfoCircleOutlined style={{ color: '#1890ff' }} />
    };
    return iconMap[type] || <BellOutlined />;
  };

  const getNotificationColor = (type) => {
    const colorMap = {
      sale: '#52c41a',
      payment: '#1890ff',
      message: '#722ed1',
      user: '#fa8c16',
      achievement: '#faad14',
      warning: '#ff4d4f',
      info: '#1890ff'
    };
    return colorMap[type] || '#d9d9d9';
  };

  const renderNotificationItem = (item) => (
    <List.Item
      key={item.id}
      style={{
        backgroundColor: item.read ? 'transparent' : '#f0f5ff',
        padding: '12px',
        cursor: 'pointer',
        borderLeft: `3px solid ${getNotificationColor(item.type)}`
      }}
      onClick={() => !item.read && markAsRead(item.id)}
    >
      <List.Item.Meta
        avatar={
          <Avatar
            style={{ backgroundColor: getNotificationColor(item.type) }}
            icon={getNotificationIcon(item.type)}
          />
        }
        title={
          <Space>
            <Text strong={!item.read}>{item.title}</Text>
            {!item.read && <Badge status="processing" />}
          </Space>
        }
        description={
          <>
            <Text type="secondary">{item.message}</Text>
            <div style={{ marginTop: 4 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {new Date(item.created_at).toLocaleString('fr-FR')}
              </Text>
            </div>
          </>
        }
      />
      <Space>
        {!item.read && (
          <Button
            type="text"
            size="small"
            icon={<CheckOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              markAsRead(item.id);
            }}
          />
        )}
        <Button
          type="text"
          size="small"
          danger
          icon={<DeleteOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            deleteNotification(item.id);
          }}
        />
      </Space>
    </List.Item>
  );

  const dropdownContent = (
    <div style={{ width: 380, maxHeight: 500, overflow: 'auto' }}>
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={5} style={{ margin: 0 }}>
            Notifications
          </Title>
          <Space size="small">
            {unreadCount > 0 && (
              <Button type="link" size="small" onClick={markAllAsRead}>
                Tout marquer lu
              </Button>
            )}
            <Button
              type="text"
              size="small"
              icon={<SettingOutlined />}
              onClick={() => setDrawerVisible(true)}
            />
          </Space>
        </Space>
      </div>

      <Spin spinning={loading}>
        {notifications.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Aucune notification"
            style={{ padding: '40px 0' }}
          />
        ) : (
          <List
            dataSource={notifications.slice(0, 10)}
            renderItem={renderNotificationItem}
            style={{ padding: 0 }}
          />
        )}
      </Spin>

      {notifications.length > 10 && (
        <div style={{ textAlign: 'center', padding: 12, borderTop: '1px solid #f0f0f0' }}>
          <Button type="link" onClick={() => setDrawerVisible(true)}>
            Voir toutes les notifications
          </Button>
        </div>
      )}
    </div>
  );

  return (
    <>
      <Dropdown
        popupRender={() => dropdownContent}
        trigger={['click']}
        placement="bottomRight"
      >
        <Badge count={unreadCount} overflowCount={99}>
          <Button
            type="text"
            icon={<BellOutlined style={{ fontSize: 20 }} />}
            style={{ padding: '4px 12px' }}
          />
        </Badge>
      </Dropdown>

      {/* Drawer Paramètres et Historique Complet */}
      <Drawer
        title="Centre de Notifications"
        placement="right"
        width={500}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        <Tabs defaultActiveKey="all">
          <TabPane tab="Toutes" key="all">
            <List
              dataSource={notifications}
              renderItem={renderNotificationItem}
              locale={{ emptyText: 'Aucune notification' }}
            />
          </TabPane>

          <TabPane tab="Non lues" key="unread">
            <List
              dataSource={notifications.filter(n => !n.read)}
              renderItem={renderNotificationItem}
              locale={{ emptyText: 'Aucune notification non lue' }}
            />
          </TabPane>

          <TabPane tab={<><SettingOutlined /> Paramètres</>} key="settings">
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <div>
                <Title level={5}>Canaux de notification</Title>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Email</Text>
                    <Switch
                      checked={settings.email}
                      onChange={(checked) => updateSettings({ ...settings, email: checked })}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Notifications push</Text>
                    <Switch
                      checked={settings.push}
                      onChange={(checked) => updateSettings({ ...settings, push: checked })}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>SMS</Text>
                    <Switch
                      checked={settings.sms}
                      onChange={(checked) => updateSettings({ ...settings, sms: checked })}
                    />
                  </div>
                </Space>
              </div>

              <Divider />

              <div>
                <Title level={5}>Types de notifications</Title>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Ventes</Text>
                    <Switch
                      checked={settings.sales}
                      onChange={(checked) => updateSettings({ ...settings, sales: checked })}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Paiements</Text>
                    <Switch
                      checked={settings.payments}
                      onChange={(checked) => updateSettings({ ...settings, payments: checked })}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Messages</Text>
                    <Switch
                      checked={settings.messages}
                      onChange={(checked) => updateSettings({ ...settings, messages: checked })}
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text>Système</Text>
                    <Switch
                      checked={settings.system}
                      onChange={(checked) => updateSettings({ ...settings, system: checked })}
                    />
                  </div>
                </Space>
              </div>
            </Space>
          </TabPane>
        </Tabs>
      </Drawer>
    </>
  );
};

export default NotificationBell;
