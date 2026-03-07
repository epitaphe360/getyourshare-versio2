/**
 * ProductsListScreen — Liste des produits du marchand
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl, Alert,
} from 'react-native';
import api from '../../services/api';

const ProductRow = ({item, onEdit, onToggle}) => (
  <View style={styles.row}>
    <View style={styles.rowInfo}>
      <Text style={styles.rowName} numberOfLines={1}>{item.name}</Text>
      <Text style={styles.rowPrice}>{item.price} MAD · Com. {item.commission_rate}%</Text>
    </View>
    <View style={styles.rowActions}>
      <TouchableOpacity style={styles.editBtn} onPress={() => onEdit(item)}>
        <Text style={styles.editBtnText}>✏️</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={[styles.toggleBtn, {backgroundColor: item.is_active ? '#fee2e2' : '#dcfce7'}]}
        onPress={() => onToggle(item)}>
        <Text style={{fontSize: 12}}>{item.is_active ? '⏸' : '▶️'}</Text>
      </TouchableOpacity>
    </View>
  </View>
);

const ProductsListScreen = ({navigation}) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchProducts = async () => {
    try {
      const res = await api.get('/merchant/products');
      setProducts(res.data?.products || res.data || []);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchProducts(); }, []);
  const onRefresh = async () => { setRefreshing(true); await fetchProducts(); setRefreshing(false); };

  const handleToggle = async (product) => {
    try {
      await api.patch(`/merchant/products/${product.id}`, {is_active: !product.is_active});
      fetchProducts();
    } catch (_) {
      Alert.alert('Erreur', 'Impossible de modifier le statut.');
    }
  };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.addBtn}
        onPress={() => navigation.navigate('CreateProduct')}>
        <Text style={styles.addBtnText}>+ Ajouter un produit</Text>
      </TouchableOpacity>
      <FlatList
        data={products}
        keyExtractor={(i) => String(i.id)}
        renderItem={({item}) => (
          <ProductRow item={item} onEdit={(p) => navigation.navigate('CreateProduct', {product: p})} onToggle={handleToggle} />
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucun produit. Ajoutez votre premier produit !</Text>}
        contentContainerStyle={{padding: 12}}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  addBtn: {margin: 12, backgroundColor: '#3b82f6', borderRadius: 12, padding: 14, alignItems: 'center'},
  addBtnText: {color: '#fff', fontWeight: '700', fontSize: 15},
  row: {backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 10, flexDirection: 'row', alignItems: 'center', elevation: 2},
  rowInfo: {flex: 1},
  rowName: {fontSize: 15, fontWeight: '600', color: '#1e293b', marginBottom: 2},
  rowPrice: {fontSize: 12, color: '#64748b'},
  rowActions: {flexDirection: 'row', gap: 8},
  editBtn: {backgroundColor: '#e0e7ff', borderRadius: 8, padding: 8},
  editBtnText: {fontSize: 16},
  toggleBtn: {borderRadius: 8, padding: 8},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 60, paddingHorizontal: 32},
});

export default ProductsListScreen;
