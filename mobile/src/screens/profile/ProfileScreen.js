/**
 * ProfileScreen — Profil utilisateur
 */
import React from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert,
} from 'react-native';
import {useAuth} from '../../contexts/AuthContext';

const InfoRow = ({label, value}) => (
  <View style={styles.row}>
    <Text style={styles.rowLabel}>{label}</Text>
    <Text style={styles.rowValue}>{value || '—'}</Text>
  </View>
);

const ROLE_LABELS = {influencer: 'Influenceur', merchant: 'Marchand', admin: 'Administrateur', commercial: 'Commercial'};
const ROLE_COLORS = {influencer: '#8b5cf6', merchant: '#3b82f6', admin: '#ef4444', commercial: '#f59e0b'};

const ProfileScreen = ({navigation}) => {
  const {user, userRole, logout} = useAuth();

  const confirmLogout = () => {
    Alert.alert('Déconnexion', 'Voulez-vous vraiment vous déconnecter ?', [
      {text: 'Annuler', style: 'cancel'},
      {text: 'Déconnexion', style: 'destructive', onPress: logout},
    ]);
  };

  const roleColor = ROLE_COLORS[userRole] || '#64748b';

  return (
    <ScrollView style={styles.container}>
      {/* Avatar */}
      <View style={styles.header}>
        <View style={[styles.avatar, {backgroundColor: roleColor}]}>
          <Text style={styles.avatarText}>{(user?.name || user?.email || '?')[0].toUpperCase()}</Text>
        </View>
        <Text style={styles.name}>{user?.name || 'Utilisateur'}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        <View style={[styles.roleBadge, {backgroundColor: roleColor}]}>
          <Text style={styles.roleText}>{ROLE_LABELS[userRole] || userRole}</Text>
        </View>
      </View>

      {/* Infos */}
      <View style={styles.card}>
        <Text style={styles.section}>Informations</Text>
        <InfoRow label="Nom" value={user?.name} />
        <InfoRow label="Email" value={user?.email} />
        <InfoRow label="Téléphone" value={user?.phone} />
        <InfoRow label="Ville" value={user?.city} />
        <InfoRow label="Pays" value={user?.country} />
      </View>

      {/* Actions */}
      <TouchableOpacity style={styles.editBtn} onPress={() => navigation.navigate('EditProfile')}>
        <Text style={styles.editBtnText}>Modifier le profil</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.settingsBtn} onPress={() => navigation.navigate('Settings')}>
        <Text style={styles.settingsBtnText}>Paramètres</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.logoutBtn} onPress={confirmLogout}>
        <Text style={styles.logoutBtnText}>Se déconnecter</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  header: {alignItems: 'center', paddingVertical: 32, backgroundColor: '#fff'},
  avatar: {width: 80, height: 80, borderRadius: 40, alignItems: 'center', justifyContent: 'center', marginBottom: 12},
  avatarText: {color: '#fff', fontSize: 32, fontWeight: '700'},
  name: {fontSize: 20, fontWeight: '700', color: '#1e293b'},
  email: {fontSize: 13, color: '#64748b', marginTop: 2},
  roleBadge: {borderRadius: 20, paddingHorizontal: 14, paddingVertical: 5, marginTop: 10},
  roleText: {color: '#fff', fontWeight: '600', fontSize: 13},
  card: {margin: 16, backgroundColor: '#fff', borderRadius: 12, padding: 16, elevation: 2},
  section: {fontSize: 12, fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 12},
  row: {flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#f1f5f9'},
  rowLabel: {fontSize: 14, color: '#64748b'},
  rowValue: {fontSize: 14, fontWeight: '500', color: '#1e293b'},
  editBtn: {margin: 16, marginTop: 0, backgroundColor: '#3b82f6', borderRadius: 12, padding: 14, alignItems: 'center'},
  editBtnText: {color: '#fff', fontWeight: '700', fontSize: 15},
  settingsBtn: {marginHorizontal: 16, marginBottom: 12, backgroundColor: '#e0e7ff', borderRadius: 12, padding: 14, alignItems: 'center'},
  settingsBtnText: {color: '#3730a3', fontWeight: '600', fontSize: 15},
  logoutBtn: {marginHorizontal: 16, marginBottom: 32, backgroundColor: '#fee2e2', borderRadius: 12, padding: 14, alignItems: 'center'},
  logoutBtnText: {color: '#dc2626', fontWeight: '700', fontSize: 15},
});

export default ProfileScreen;
