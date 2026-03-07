/**
 * DashboardScreen — Tableau de bord par défaut (rôle non reconnu)
 */
import React from 'react';
import {View, Text, StyleSheet, ScrollView} from 'react-native';
import {useAuth} from '../../contexts/AuthContext';

const DashboardScreen = () => {
  const {user} = useAuth();

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Tableau de Bord</Text>
      <Text style={styles.subtitle}>Bienvenue, {user?.name || 'Utilisateur'}</Text>
      <View style={styles.card}>
        <Text style={styles.cardText}>Chargement de votre espace en cours…</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, padding: 16, backgroundColor: '#f8fafc'},
  title: {fontSize: 24, fontWeight: '700', color: '#1e293b', marginBottom: 4},
  subtitle: {fontSize: 14, color: '#64748b', marginBottom: 20},
  card: {backgroundColor: '#fff', borderRadius: 12, padding: 16, elevation: 2},
  cardText: {color: '#475569'},
});

export default DashboardScreen;
