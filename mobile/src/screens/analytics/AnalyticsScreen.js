/**
 * AnalyticsScreen — Analytics et statistiques avancées
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, RefreshControl,
} from 'react-native';
import api from '../../services/api';
import {useAuth} from '../../contexts/AuthContext';

const PERIODS = [
  {label: '7j', value: '7d'},
  {label: '30j', value: '30d'},
  {label: '90j', value: '90d'},
];

const StatCard = ({label, value, sub, color}) => (
  <View style={[styles.statCard, {borderTopColor: color, borderTopWidth: 3}]}>
    <Text style={styles.statValue}>{value ?? '—'}</Text>
    <Text style={styles.statLabel}>{label}</Text>
    {sub && <Text style={styles.statSub}>{sub}</Text>}
  </View>
);

const AnalyticsScreen = ({navigation}) => {
  const {userRole} = useAuth();
  const [period, setPeriod] = useState('30d');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalytics = async (p = period) => {
    try {
      const endpoint = userRole === 'merchant' ? '/merchant/analytics' : '/influencer/analytics';
      const res = await api.get(endpoint, {params: {period: p}});
      setData(res.data);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchAnalytics(period); }, [period]);
  const onRefresh = async () => { setRefreshing(true); await fetchAnalytics(period); setRefreshing(false); };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}>

      {/* Sélecteur de période */}
      <View style={styles.periodSelector}>
        {PERIODS.map((p) => (
          <TouchableOpacity
            key={p.value}
            style={[styles.periodBtn, period === p.value && styles.periodBtnActive]}
            onPress={() => setPeriod(p.value)}>
            <Text style={[styles.periodBtnText, period === p.value && styles.periodBtnTextActive]}>
              {p.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Stats */}
      <View style={styles.statsGrid}>
        <StatCard label="Clics" value={data?.total_clicks} color="#3b82f6" />
        <StatCard label="Conversions" value={data?.total_conversions} color="#10b981" />
        <StatCard label="Taux conv." value={data?.conversion_rate ? `${data.conversion_rate}%` : null} color="#f59e0b" />
        <StatCard label="Revenus" value={data?.total_revenue ? `${data.total_revenue} MAD` : null} color="#8b5cf6" />
      </View>

      {/* Lien vers détails conversions */}
      <TouchableOpacity
        style={styles.cta}
        onPress={() => navigation.navigate('Conversions')}>
        <Text style={styles.ctaText}>Voir toutes les conversions →</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc', padding: 16},
  periodSelector: {flexDirection: 'row', backgroundColor: '#e2e8f0', borderRadius: 10, padding: 4, marginBottom: 20},
  periodBtn: {flex: 1, paddingVertical: 8, borderRadius: 8, alignItems: 'center'},
  periodBtnActive: {backgroundColor: '#fff', elevation: 2},
  periodBtnText: {fontSize: 14, color: '#64748b', fontWeight: '500'},
  periodBtnTextActive: {color: '#3b82f6', fontWeight: '700'},
  statsGrid: {flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 20},
  statCard: {backgroundColor: '#fff', borderRadius: 12, padding: 16, width: '47%', elevation: 2},
  statValue: {fontSize: 22, fontWeight: '700', color: '#1e293b'},
  statLabel: {fontSize: 12, color: '#64748b', marginTop: 4},
  statSub: {fontSize: 11, color: '#94a3b8', marginTop: 2},
  cta: {backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center'},
  ctaText: {color: '#fff', fontWeight: '600', fontSize: 15},
});

export default AnalyticsScreen;
