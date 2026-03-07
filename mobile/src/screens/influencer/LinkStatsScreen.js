/**
 * LinkStatsScreen — Statistiques détaillées d'un lien
 */
import React, {useState, useEffect} from 'react';
import {View, Text, StyleSheet, ScrollView, ActivityIndicator, RefreshControl} from 'react-native';
import api from '../../services/api';

const StatRow = ({label, value}) => (
  <View style={styles.row}>
    <Text style={styles.rowLabel}>{label}</Text>
    <Text style={styles.rowValue}>{value ?? '—'}</Text>
  </View>
);

const LinkStatsScreen = ({route}) => {
  const {link} = route.params;
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const res = await api.get(`/influencer/tracking-links/${link.id}/stats`);
      setStats(res.data);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchStats(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchStats(); setRefreshing(false); };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.title}>{link.name || 'Statistiques du lien'}</Text>
      <Text style={styles.url}>{link.short_url || link.tracking_url}</Text>

      <View style={styles.card}>
        <Text style={styles.section}>Résumé global</Text>
        <StatRow label="Clics totaux" value={stats?.total_clicks} />
        <StatRow label="Conversions" value={stats?.total_conversions} />
        <StatRow label="Taux de conversion" value={stats?.conversion_rate ? `${stats.conversion_rate}%` : null} />
        <StatRow label="Gains totaux" value={stats?.total_earnings ? `${stats.total_earnings} MAD` : null} />
      </View>

      <View style={styles.card}>
        <Text style={styles.section}>Appareils</Text>
        <StatRow label="Mobile" value={stats?.device_mobile} />
        <StatRow label="Desktop" value={stats?.device_desktop} />
        <StatRow label="Tablette" value={stats?.device_tablet} />
      </View>

      <View style={styles.card}>
        <Text style={styles.section}>Période</Text>
        <StatRow label="Aujourd'hui" value={stats?.clicks_today} />
        <StatRow label="Cette semaine" value={stats?.clicks_week} />
        <StatRow label="Ce mois" value={stats?.clicks_month} />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc', padding: 16},
  title: {fontSize: 18, fontWeight: '700', color: '#1e293b', marginBottom: 4},
  url: {fontSize: 12, color: '#3b82f6', marginBottom: 20},
  card: {backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16, elevation: 2},
  section: {fontSize: 13, fontWeight: '700', color: '#64748b', textTransform: 'uppercase', marginBottom: 12},
  row: {flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f1f5f9'},
  rowLabel: {fontSize: 14, color: '#475569'},
  rowValue: {fontSize: 14, fontWeight: '600', color: '#1e293b'},
});

export default LinkStatsScreen;
