/**
 * ConversionsScreen — Liste des conversions
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, ActivityIndicator, RefreshControl,
} from 'react-native';
import api from '../../services/api';
import {useAuth} from '../../contexts/AuthContext';

const STATUS_COLORS = {
  completed: {bg: '#dcfce7', text: '#16a34a'},
  pending:   {bg: '#fef9c3', text: '#ca8a04'},
  rejected:  {bg: '#fee2e2', text: '#dc2626'},
};

const ConvRow = ({item}) => {
  const sc = STATUS_COLORS[item.status] || STATUS_COLORS.pending;
  return (
    <View style={styles.row}>
      <View style={styles.rowLeft}>
        <Text style={styles.rowProduct} numberOfLines={1}>{item.product_name || 'Produit'}</Text>
        <Text style={styles.rowDate}>{new Date(item.created_at).toLocaleDateString('fr-MA')}</Text>
      </View>
      <View style={styles.rowRight}>
        <Text style={styles.rowAmount}>{item.amount} MAD</Text>
        <View style={[styles.badge, {backgroundColor: sc.bg}]}>
          <Text style={[styles.badgeText, {color: sc.text}]}>{item.status}</Text>
        </View>
      </View>
    </View>
  );
};

const ConversionsScreen = () => {
  const {userRole} = useAuth();
  const [conversions, setConversions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchConversions = async (p = 1, append = false) => {
    try {
      const endpoint = userRole === 'merchant' ? '/merchant/conversions' : '/influencer/conversions';
      const res = await api.get(endpoint, {params: {page: p, limit: 20}});
      const items = res.data?.conversions || res.data || [];
      setConversions((prev) => append ? [...prev, ...items] : items);
      setHasMore(items.length === 20);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchConversions(1); }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    setPage(1);
    await fetchConversions(1);
    setRefreshing(false);
  };

  const loadMore = () => {
    if (!hasMore) return;
    const nextPage = page + 1;
    setPage(nextPage);
    fetchConversions(nextPage, true);
  };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <FlatList
      data={conversions}
      keyExtractor={(i) => String(i.id)}
      renderItem={({item}) => <ConvRow item={item} />}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      onEndReached={loadMore}
      onEndReachedThreshold={0.3}
      ListEmptyComponent={<Text style={styles.empty}>Aucune conversion pour le moment.</Text>}
    />
  );
};

const styles = StyleSheet.create({
  row: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#f1f5f9'},
  rowLeft: {flex: 1},
  rowProduct: {fontSize: 14, fontWeight: '600', color: '#1e293b', marginBottom: 4},
  rowDate: {fontSize: 12, color: '#94a3b8'},
  rowRight: {alignItems: 'flex-end'},
  rowAmount: {fontSize: 16, fontWeight: '700', color: '#1e293b', marginBottom: 4},
  badge: {borderRadius: 10, paddingHorizontal: 8, paddingVertical: 2},
  badgeText: {fontSize: 11, fontWeight: '600'},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 60},
});

export default ConversionsScreen;
