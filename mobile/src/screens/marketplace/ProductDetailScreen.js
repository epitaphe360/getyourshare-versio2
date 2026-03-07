/**
 * ProductDetailScreen — Détails d'un produit + bouton d'affiliation
 */
import React, {useState} from 'react';
import {
  View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Alert,
} from 'react-native';
import api from '../../services/api';
import {useAuth} from '../../contexts/AuthContext';

const ProductDetailScreen = ({route}) => {
  const {product} = route.params;
  const {userRole} = useAuth();
  const [loading, setLoading] = useState(false);

  const requestAffiliation = async () => {
    setLoading(true);
    try {
      await api.post('/affiliate/requests', {product_id: product.id, merchant_id: product.merchant_id});
      Alert.alert('Succès', 'Demande d\'affiliation envoyée !');
    } catch (e) {
      Alert.alert('Erreur', e.response?.data?.detail || 'Erreur lors de la demande.');
    }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.container}>
      {product.image_url ? (
        <Image source={{uri: product.image_url}} style={styles.image} />
      ) : (
        <View style={[styles.image, styles.noImage]}>
          <Text style={{fontSize: 60}}>📦</Text>
        </View>
      )}

      <View style={styles.body}>
        <Text style={styles.name}>{product.name}</Text>
        <Text style={styles.price}>{product.price} MAD</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>Commission : {product.commission_rate}%</Text>
        </View>

        <Text style={styles.section}>Description</Text>
        <Text style={styles.description}>{product.description || 'Aucune description disponible.'}</Text>

        {product.category && (
          <>
            <Text style={styles.section}>Catégorie</Text>
            <Text style={styles.description}>{product.category}</Text>
          </>
        )}

        {userRole === 'influencer' && (
          <TouchableOpacity
            style={styles.btn}
            onPress={requestAffiliation}
            disabled={loading}>
            <Text style={styles.btnText}>
              {loading ? 'Envoi en cours...' : 'Demander l\'affiliation'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  image: {width: '100%', height: 250},
  noImage: {backgroundColor: '#e2e8f0', alignItems: 'center', justifyContent: 'center'},
  body: {padding: 20},
  name: {fontSize: 22, fontWeight: '700', color: '#1e293b', marginBottom: 8},
  price: {fontSize: 26, fontWeight: '700', color: '#3b82f6', marginBottom: 12},
  badge: {backgroundColor: '#dcfce7', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4, alignSelf: 'flex-start', marginBottom: 20},
  badgeText: {color: '#16a34a', fontWeight: '600'},
  section: {fontSize: 14, fontWeight: '700', color: '#64748b', marginBottom: 6, marginTop: 16, textTransform: 'uppercase'},
  description: {fontSize: 15, color: '#475569', lineHeight: 22},
  btn: {backgroundColor: '#3b82f6', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 32},
  btnText: {color: '#fff', fontWeight: '700', fontSize: 16},
});

export default ProductDetailScreen;
