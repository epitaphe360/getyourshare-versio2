/**
 * CreateProductScreen — Créer / modifier un produit (Marchand)
 */
import React, {useState} from 'react';
import {
  View, Text, StyleSheet, ScrollView, TextInput,
  TouchableOpacity, Alert, Switch,
} from 'react-native';
import api from '../../services/api';

const Field = ({label, ...props}) => (
  <View style={styles.field}>
    <Text style={styles.label}>{label}</Text>
    <TextInput style={styles.input} placeholderTextColor="#94a3b8" {...props} />
  </View>
);

const CreateProductScreen = ({route, navigation}) => {
  const existing = route.params?.product;
  const [form, setForm] = useState({
    name: existing?.name || '',
    description: existing?.description || '',
    price: String(existing?.price || ''),
    commission_rate: String(existing?.commission_rate || '10'),
    category: existing?.category || '',
    image_url: existing?.image_url || '',
    is_active: existing?.is_active ?? true,
  });
  const [loading, setLoading] = useState(false);

  const set = (key, val) => setForm((prev) => ({...prev, [key]: val}));

  const submit = async () => {
    if (!form.name || !form.price) {
      Alert.alert('Erreur', 'Le nom et le prix sont obligatoires.');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...form,
        price: parseFloat(form.price),
        commission_rate: parseFloat(form.commission_rate),
      };
      if (existing?.id) {
        await api.put(`/merchant/products/${existing.id}`, payload);
        Alert.alert('Succès', 'Produit mis à jour !');
      } else {
        await api.post('/merchant/products', payload);
        Alert.alert('Succès', 'Produit créé !');
      }
      navigation.goBack();
    } catch (e) {
      Alert.alert('Erreur', e.response?.data?.detail || 'Erreur lors de la sauvegarde.');
    }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{padding: 16}}>
      <Text style={styles.title}>{existing ? 'Modifier le produit' : 'Nouveau produit'}</Text>

      <Field label="Nom *" value={form.name} onChangeText={(v) => set('name', v)} placeholder="Nom du produit" />
      <Field label="Description" value={form.description} onChangeText={(v) => set('description', v)} placeholder="Description" multiline numberOfLines={4} style={styles.textarea} />
      <Field label="Prix (MAD) *" value={form.price} onChangeText={(v) => set('price', v)} placeholder="0.00" keyboardType="numeric" />
      <Field label="Taux de commission (%)" value={form.commission_rate} onChangeText={(v) => set('commission_rate', v)} placeholder="10" keyboardType="numeric" />
      <Field label="Catégorie" value={form.category} onChangeText={(v) => set('category', v)} placeholder="ex: Mode, Beauté…" />
      <Field label="URL de l'image" value={form.image_url} onChangeText={(v) => set('image_url', v)} placeholder="https://…" keyboardType="url" />

      <View style={styles.switchRow}>
        <Text style={styles.label}>Produit actif</Text>
        <Switch value={form.is_active} onValueChange={(v) => set('is_active', v)} trackColor={{true: '#3b82f6'}} />
      </View>

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
  textarea: {height: 90, textAlignVertical: 'top'},
  switchRow: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20},
  btn: {backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 8},
  btnText: {color: '#fff', fontWeight: '700', fontSize: 16},
});

export default CreateProductScreen;
