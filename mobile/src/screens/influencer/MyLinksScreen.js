/**
 * MyLinksScreen — Mes liens d'affiliation (Influenceur)
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  Share, ActivityIndicator, RefreshControl,
} from 'react-native';
import api from '../../services/api';

const LinkItem = ({item, onShare, onStats}) => (
  <View style={styles.card}>
    <View style={styles.cardHeader}>
      <Text style={styles.linkName} numberOfLines={1}>{item.name || item.product_name || 'Lien'}</Text>
      <View style={[styles.statusBadge, {backgroundColor: item.is_active ? '#dcfce7' : '#fee2e2'}]}>
        <Text style={{color: item.is_active ? '#16a34a' : '#dc2626', fontSize: 11, fontWeight: '600'}}>
          {item.is_active ? 'Actif' : 'Inactif'}
        </Text>
      </View>
    </View>
    <Text style={styles.shortUrl} numberOfLines={1}>{item.short_url || item.tracking_url}</Text>
    <View style={styles.statsRow}>
      <Text style={styles.stat}>👆 {item.click_count || 0} clics</Text>
      <Text style={styles.stat}>✅ {item.conversion_count || 0} conv.</Text>
    </View>
    <View style={styles.actions}>
      <TouchableOpacity style={styles.actionBtn} onPress={() => onShare(item)}>
        <Text style={styles.actionBtnText}>Partager</Text>
      </TouchableOpacity>
      <TouchableOpacity style={[styles.actionBtn, {backgroundColor: '#e0e7ff'}]} onPress={() => onStats(item)}>
        <Text style={[styles.actionBtnText, {color: '#4338ca'}]}>Stats</Text>
      </TouchableOpacity>
    </View>
  </View>
);

const MyLinksScreen = ({navigation}) => {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchLinks = async () => {
    try {
      const res = await api.get('/influencer/tracking-links');
      setLinks(res.data?.links || res.data || []);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchLinks(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchLinks(); setRefreshing(false); };

  const handleShare = async (link) => {
    await Share.share({
      message: `Découvrez ce produit : ${link.short_url || link.tracking_url}`,
      url: link.short_url || link.tracking_url,
    });
  };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <FlatList
      data={links}
      keyExtractor={(i) => String(i.id)}
      renderItem={({item}) => (
        <LinkItem
          item={item}
          onShare={handleShare}
          onStats={(l) => navigation.navigate('LinkStats', {link: l})}
        />
      )}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      ListEmptyComponent={<Text style={styles.empty}>Aucun lien d'affiliation. Rejoignez des campagnes sur la marketplace.</Text>}
      contentContainerStyle={{padding: 12}}
    />
  );
};

const styles = StyleSheet.create({
  card: {backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 12, elevation: 2},
  cardHeader: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6},
  linkName: {flex: 1, fontSize: 15, fontWeight: '600', color: '#1e293b'},
  statusBadge: {borderRadius: 20, paddingHorizontal: 10, paddingVertical: 3, marginLeft: 8},
  shortUrl: {fontSize: 12, color: '#3b82f6', marginBottom: 10},
  statsRow: {flexDirection: 'row', gap: 16, marginBottom: 12},
  stat: {fontSize: 13, color: '#64748b'},
  actions: {flexDirection: 'row', gap: 10},
  actionBtn: {flex: 1, backgroundColor: '#dbeafe', borderRadius: 8, paddingVertical: 8, alignItems: 'center'},
  actionBtnText: {color: '#1d4ed8', fontWeight: '600', fontSize: 13},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 60, paddingHorizontal: 32, lineHeight: 22},
});

export default MyLinksScreen;
