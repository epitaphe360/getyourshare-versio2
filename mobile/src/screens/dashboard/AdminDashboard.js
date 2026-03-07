/**
 * AdminDashboard — Tableau de bord administrateur
 */
import React, {useState, useEffect} from 'react';
import {View, Text, StyleSheet, ScrollView, RefreshControl} from 'react-native';
import api from '../../services/api';

const StatCard = ({label, value, color}) => (
  <View style={[styles.statCard, {borderLeftColor: color}]}>
    <Text style={styles.statValue}>{value ?? '—'}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const res = await api.get('/admin/stats');
      setStats(res.data);
    } catch (_) {}
  };

  useEffect(() => { fetchStats(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchStats(); setRefreshing(false); };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.title}>Administration 🛡️</Text>
      <View style={styles.statsGrid}>
        <StatCard label="Utilisateurs" value={stats?.total_users} color="#3b82f6" />
        <StatCard label="Marchands" value={stats?.total_merchants} color="#10b981" />
        <StatCard label="Influenceurs" value={stats?.total_influencers} color="#f59e0b" />
        <StatCard label="CA total (MAD)" value={stats?.total_revenue} color="#ef4444" />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc', padding: 16},
  title: {fontSize: 22, fontWeight: '700', color: '#1e293b', marginBottom: 20},
  statsGrid: {flexDirection: 'row', flexWrap: 'wrap', gap: 12},
  statCard: {backgroundColor: '#fff', borderRadius: 12, padding: 16, width: '47%', borderLeftWidth: 4, elevation: 2},
  statValue: {fontSize: 24, fontWeight: '700', color: '#1e293b'},
  statLabel: {fontSize: 12, color: '#64748b', marginTop: 4},
});

export default AdminDashboard;
