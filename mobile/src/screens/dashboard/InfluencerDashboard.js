/**
 * InfluencerDashboard — Tableau de bord influenceur
 */
import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import {useAuth} from '../../contexts/AuthContext';
import api from '../../services/api';

const StatCard = ({label, value, color}) => (
  <View style={[styles.statCard, {borderLeftColor: color}]}>
    <Text style={styles.statValue}>{value ?? '—'}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const InfluencerDashboard = ({navigation}) => {
  const {user} = useAuth();
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const res = await api.get('/influencer/stats');
      setStats(res.data);
    } catch (_) {}
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchStats();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>
      <Text style={styles.greeting}>Bonjour, {user?.name} 👋</Text>
      <Text style={styles.period}>Vue d'ensemble du mois</Text>

      <View style={styles.statsGrid}>
        <StatCard label="Clics" value={stats?.total_clicks} color="#3b82f6" />
        <StatCard label="Conversions" value={stats?.total_conversions} color="#10b981" />
        <StatCard label="Gains (MAD)" value={stats?.total_earnings} color="#f59e0b" />
        <StatCard label="Liens actifs" value={stats?.active_links} color="#8b5cf6" />
      </View>

      <TouchableOpacity
        style={styles.cta}
        onPress={() => navigation.navigate('MyLinks')}>
        <Text style={styles.ctaText}>Mes liens d'affiliation →</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.cta, {backgroundColor: '#10b981'}]}
        onPress={() => navigation.navigate('Analytics')}>
        <Text style={styles.ctaText}>Voir mes analytics →</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc', padding: 16},
  greeting: {fontSize: 22, fontWeight: '700', color: '#1e293b', marginBottom: 2},
  period: {fontSize: 13, color: '#64748b', marginBottom: 20},
  statsGrid: {flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 20},
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    width: '47%',
    borderLeftWidth: 4,
    elevation: 2,
  },
  statValue: {fontSize: 24, fontWeight: '700', color: '#1e293b'},
  statLabel: {fontSize: 12, color: '#64748b', marginTop: 4},
  cta: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  ctaText: {color: '#fff', fontWeight: '600', fontSize: 15},
});

export default InfluencerDashboard;
