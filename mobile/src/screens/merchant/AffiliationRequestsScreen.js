/**
 * AffiliationRequestsScreen — Demandes d'affiliation reçues (Marchand)
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl, Alert,
} from 'react-native';
import api from '../../services/api';

const RequestCard = ({item, onAccept, onReject}) => (
  <View style={styles.card}>
    <Text style={styles.name}>{item.influencer_name || 'Influenceur'}</Text>
    <Text style={styles.product}>Produit : {item.product_name || item.product_id}</Text>
    <Text style={styles.date}>
      {new Date(item.created_at).toLocaleDateString('fr-MA')}
    </Text>
    {item.status === 'pending' && (
      <View style={styles.actions}>
        <TouchableOpacity style={styles.acceptBtn} onPress={() => onAccept(item)}>
          <Text style={styles.acceptText}>Accepter</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.rejectBtn} onPress={() => onReject(item)}>
          <Text style={styles.rejectText}>Refuser</Text>
        </TouchableOpacity>
      </View>
    )}
    {item.status !== 'pending' && (
      <View style={[styles.statusBadge, {backgroundColor: item.status === 'approved' ? '#dcfce7' : '#fee2e2'}]}>
        <Text style={{color: item.status === 'approved' ? '#16a34a' : '#dc2626', fontSize: 12, fontWeight: '600'}}>
          {item.status === 'approved' ? '✓ Accepté' : '✗ Refusé'}
        </Text>
      </View>
    )}
  </View>
);

const AffiliationRequestsScreen = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchRequests = async () => {
    try {
      const res = await api.get('/merchant/affiliation-requests');
      setRequests(res.data?.requests || res.data || []);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchRequests(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchRequests(); setRefreshing(false); };

  const handle = async (item, action) => {
    try {
      await api.patch(`/merchant/affiliation-requests/${item.id}`, {status: action});
      fetchRequests();
    } catch (_) {
      Alert.alert('Erreur', 'Action impossible.');
    }
  };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <FlatList
      data={requests}
      keyExtractor={(i) => String(i.id)}
      renderItem={({item}) => (
        <RequestCard item={item} onAccept={(r) => handle(r, 'approved')} onReject={(r) => handle(r, 'rejected')} />
      )}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      ListEmptyComponent={<Text style={styles.empty}>Aucune demande d'affiliation en attente.</Text>}
      contentContainerStyle={{padding: 12}}
    />
  );
};

const styles = StyleSheet.create({
  card: {backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 10, elevation: 2},
  name: {fontSize: 16, fontWeight: '700', color: '#1e293b', marginBottom: 2},
  product: {fontSize: 13, color: '#64748b', marginBottom: 2},
  date: {fontSize: 12, color: '#94a3b8', marginBottom: 12},
  actions: {flexDirection: 'row', gap: 10},
  acceptBtn: {flex: 1, backgroundColor: '#dcfce7', borderRadius: 8, padding: 10, alignItems: 'center'},
  acceptText: {color: '#16a34a', fontWeight: '700'},
  rejectBtn: {flex: 1, backgroundColor: '#fee2e2', borderRadius: 8, padding: 10, alignItems: 'center'},
  rejectText: {color: '#dc2626', fontWeight: '700'},
  statusBadge: {borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4, alignSelf: 'flex-start'},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 60, paddingHorizontal: 32},
});

export default AffiliationRequestsScreen;
