/**
 * EditProfileScreen — Modifier son profil
 */
import React, {useState} from 'react';
import {
  View, Text, StyleSheet, ScrollView, TextInput,
  TouchableOpacity, Alert,
} from 'react-native';
import {useAuth} from '../../contexts/AuthContext';
import api from '../../services/api';

const Field = ({label, ...props}) => (
  <View style={styles.field}>
    <Text style={styles.label}>{label}</Text>
    <TextInput style={styles.input} placeholderTextColor="#94a3b8" {...props} />
  </View>
);

const EditProfileScreen = ({navigation}) => {
  const {user, setUser} = useAuth();
  const [form, setForm] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    city: user?.city || '',
    country: user?.country || 'Maroc',
    bio: user?.bio || '',
  });
  const [loading, setLoading] = useState(false);

  const set = (key, val) => setForm((p) => ({...p, [key]: val}));

  const submit = async () => {
    setLoading(true);
    try {
      const res = await api.put('/users/profile', form);
      if (setUser) setUser((prev) => ({...prev, ...res.data}));
      Alert.alert('Succès', 'Profil mis à jour !');
      navigation.goBack();
    } catch (e) {
      Alert.alert('Erreur', e.response?.data?.detail || 'Impossible de mettre à jour le profil.');
    }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{padding: 16}}>
      <Text style={styles.title}>Modifier le profil</Text>
      <Field label="Nom complet" value={form.name} onChangeText={(v) => set('name', v)} placeholder="Votre nom" />
      <Field label="Téléphone" value={form.phone} onChangeText={(v) => set('phone', v)} placeholder="+212 6xx xxx xxx" keyboardType="phone-pad" />
      <Field label="Ville" value={form.city} onChangeText={(v) => set('city', v)} placeholder="Casablanca" />
      <Field label="Pays" value={form.country} onChangeText={(v) => set('country', v)} placeholder="Maroc" />
      <Field label="Bio" value={form.bio} onChangeText={(v) => set('bio', v)} placeholder="Décrivez-vous en quelques mots…" multiline numberOfLines={4} />
      <TouchableOpacity style={styles.btn} onPress={submit} disabled={loading}>
        <Text style={styles.btnText}>{loading ? 'Sauvegarde...' : 'Sauvegarder'}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  title: {fontSize: 20, fontWeight: '700', color: '#1e293b', marginBottom: 20},
  field: {marginBottom: 16},
  label: {fontSize: 13, fontWeight: '600', color: '#475569', marginBottom: 6},
  input: {backgroundColor: '#fff', borderRadius: 10, padding: 12, fontSize: 15, color: '#1e293b', elevation: 1, borderWidth: 1, borderColor: '#e2e8f0'},
  btn: {backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 8},
  btnText: {color: '#fff', fontWeight: '700', fontSize: 16},
});

export default EditProfileScreen;
