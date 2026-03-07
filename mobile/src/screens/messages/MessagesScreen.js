/**
 * MessagesScreen — Liste des conversations
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import api from '../../services/api';

const ConvItem = ({item, onPress}) => (
  <TouchableOpacity style={styles.row} onPress={() => onPress(item)}>
    <View style={styles.avatar}>
      <Text style={styles.avatarText}>{(item.other_user_name || '?')[0].toUpperCase()}</Text>
    </View>
    <View style={styles.rowContent}>
      <View style={styles.rowTop}>
        <Text style={styles.userName}>{item.other_user_name || 'Utilisateur'}</Text>
        <Text style={styles.time}>
          {item.last_message_at ? new Date(item.last_message_at).toLocaleDateString('fr-MA', {day: '2-digit', month: 'short'}) : ''}
        </Text>
      </View>
      <Text style={styles.lastMsg} numberOfLines={1}>
        {item.last_message || 'Aucun message'}
      </Text>
    </View>
    {item.unread_count > 0 && (
      <View style={styles.badge}>
        <Text style={styles.badgeText}>{item.unread_count}</Text>
      </View>
    )}
  </TouchableOpacity>
);

const MessagesScreen = ({navigation}) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchConversations = async () => {
    try {
      const res = await api.get('/messages/conversations');
      setConversations(res.data?.conversations || res.data || []);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchConversations(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchConversations(); setRefreshing(false); };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <FlatList
      data={conversations}
      keyExtractor={(i) => String(i.id)}
      renderItem={({item}) => (
        <ConvItem item={item} onPress={(c) => navigation.navigate('Chat', {conversation: c})} />
      )}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      ListEmptyComponent={<Text style={styles.empty}>Aucune conversation. Contactez un marchand ou un influenceur !</Text>}
    />
  );
};

const styles = StyleSheet.create({
  row: {flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#f1f5f9', backgroundColor: '#fff'},
  avatar: {width: 46, height: 46, borderRadius: 23, backgroundColor: '#3b82f6', alignItems: 'center', justifyContent: 'center', marginRight: 12},
  avatarText: {color: '#fff', fontWeight: '700', fontSize: 18},
  rowContent: {flex: 1},
  rowTop: {flexDirection: 'row', justifyContent: 'space-between', marginBottom: 3},
  userName: {fontSize: 15, fontWeight: '600', color: '#1e293b'},
  time: {fontSize: 12, color: '#94a3b8'},
  lastMsg: {fontSize: 13, color: '#64748b'},
  badge: {backgroundColor: '#3b82f6', borderRadius: 12, paddingHorizontal: 7, paddingVertical: 3, marginLeft: 8},
  badgeText: {color: '#fff', fontSize: 11, fontWeight: '700'},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 60, paddingHorizontal: 32, lineHeight: 22},
});

export default MessagesScreen;
