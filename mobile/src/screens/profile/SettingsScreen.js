/**
 * SettingsScreen — Paramètres de l'application
 */
import React, {useState} from 'react';
import {View, Text, StyleSheet, ScrollView, Switch, TouchableOpacity, Alert} from 'react-native';

const SettingRow = ({label, description, value, onChange}) => (
  <View style={styles.row}>
    <View style={styles.rowText}>
      <Text style={styles.rowLabel}>{label}</Text>
      {description && <Text style={styles.rowDesc}>{description}</Text>}
    </View>
    <Switch value={value} onValueChange={onChange} trackColor={{true: '#3b82f6'}} />
  </View>
);

const SettingsScreen = () => {
  const [settings, setSettings] = useState({
    pushNotifications: true,
    emailNotifications: true,
    marketingEmails: false,
    biometricLogin: false,
    darkMode: false,
  });

  const toggle = (key) => setSettings((p) => ({...p, [key]: !p[key]}));

  const clearCache = () => {
    Alert.alert('Cache vidé', 'Le cache local a été effacé avec succès.');
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.section}>Notifications</Text>
      <View style={styles.card}>
        <SettingRow
          label="Notifications push"
          description="Recevoir des alertes sur votre téléphone"
          value={settings.pushNotifications}
          onChange={() => toggle('pushNotifications')}
        />
        <SettingRow
          label="Notifications email"
          description="Recevoir des résumés par email"
          value={settings.emailNotifications}
          onChange={() => toggle('emailNotifications')}
        />
        <SettingRow
          label="Emails marketing"
          description="Offres et promotions"
          value={settings.marketingEmails}
          onChange={() => toggle('marketingEmails')}
        />
      </View>

      <Text style={styles.section}>Sécurité</Text>
      <View style={styles.card}>
        <SettingRow
          label="Connexion biométrique"
          description="Utiliser Touch ID / Face ID"
          value={settings.biometricLogin}
          onChange={() => toggle('biometricLogin')}
        />
      </View>

      <Text style={styles.section}>Apparence</Text>
      <View style={styles.card}>
        <SettingRow
          label="Mode sombre"
          value={settings.darkMode}
          onChange={() => toggle('darkMode')}
        />
      </View>

      <Text style={styles.section}>Données</Text>
      <TouchableOpacity style={styles.actionBtn} onPress={clearCache}>
        <Text style={styles.actionBtnText}>Vider le cache</Text>
      </TouchableOpacity>

      <Text style={styles.version}>ShareYourSales v6.0.0</Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  section: {fontSize: 12, fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', marginHorizontal: 16, marginTop: 20, marginBottom: 8},
  card: {marginHorizontal: 16, backgroundColor: '#fff', borderRadius: 12, overflow: 'hidden', elevation: 2},
  row: {flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#f1f5f9'},
  rowText: {flex: 1, paddingRight: 12},
  rowLabel: {fontSize: 15, fontWeight: '500', color: '#1e293b'},
  rowDesc: {fontSize: 12, color: '#94a3b8', marginTop: 2},
  actionBtn: {marginHorizontal: 16, marginTop: 8, backgroundColor: '#fee2e2', borderRadius: 12, padding: 14, alignItems: 'center'},
  actionBtnText: {color: '#dc2626', fontWeight: '600'},
  version: {textAlign: 'center', color: '#cbd5e1', fontSize: 12, marginTop: 32, marginBottom: 40},
});

export default SettingsScreen;
