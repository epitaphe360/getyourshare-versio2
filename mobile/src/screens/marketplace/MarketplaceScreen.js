/**
 * MarketplaceScreen — Catalogue produits / services
 */
import React, {useState, useEffect} from 'react';
import {
  View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity,
  Image, ActivityIndicator, RefreshControl,
} from 'react-native';
import api from '../../services/api';

const ProductCard = ({item, onPress}) => (
  <TouchableOpacity style={styles.card} onPress={() => onPress(item)}>
    {item.image_url ? (
      <Image source={{uri: item.image_url}} style={styles.cardImage} />
    ) : (
      <View style={[styles.cardImage, styles.noImage]}>
        <Text style={styles.noImageText}>📦</Text>
      </View>
    )}
    <View style={styles.cardBody}>
      <Text style={styles.cardTitle} numberOfLines={2}>{item.name}</Text>
      <Text style={styles.cardPrice}>{item.price} MAD</Text>
      <Text style={styles.cardCommission}>Commission : {item.commission_rate}%</Text>
    </View>
  </TouchableOpacity>
);

const MarketplaceScreen = ({navigation}) => {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchProducts = async (q = '') => {
    try {
      const res = await api.get('/marketplace/products', {params: {search: q, limit: 50}});
      setProducts(res.data?.products || res.data || []);
    } catch (_) {}
    setLoading(false);
  };

  useEffect(() => { fetchProducts(); }, []);

  const onRefresh = async () => { setRefreshing(true); await fetchProducts(search); setRefreshing(false); };

  if (loading) return <ActivityIndicator style={{flex: 1}} size="large" color="#3b82f6" />;

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.search}
        placeholder="Rechercher un produit..."
        value={search}
        onChangeText={(t) => { setSearch(t); fetchProducts(t); }}
      />
      <FlatList
        data={products}
        keyExtractor={(i) => String(i.id)}
        numColumns={2}
        renderItem={({item}) => (
          <ProductCard item={item} onPress={(p) => navigation.navigate('ProductDetail', {product: p})} />
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>Aucun produit trouvé</Text>}
        contentContainerStyle={{padding: 8}}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f8fafc'},
  search: {margin: 12, padding: 12, backgroundColor: '#fff', borderRadius: 12, elevation: 2, fontSize: 15},
  card: {flex: 1, margin: 6, backgroundColor: '#fff', borderRadius: 12, overflow: 'hidden', elevation: 2},
  cardImage: {width: '100%', height: 120},
  noImage: {backgroundColor: '#e2e8f0', alignItems: 'center', justifyContent: 'center'},
  noImageText: {fontSize: 40},
  cardBody: {padding: 10},
  cardTitle: {fontSize: 13, fontWeight: '600', color: '#1e293b', marginBottom: 4},
  cardPrice: {fontSize: 15, fontWeight: '700', color: '#3b82f6'},
  cardCommission: {fontSize: 11, color: '#10b981', marginTop: 2},
  empty: {textAlign: 'center', color: '#94a3b8', marginTop: 40},
});

export default MarketplaceScreen;
