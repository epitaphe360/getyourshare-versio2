import React, { useState, useEffect } from 'react';
import {
  Card, Row, Col, Input, Select, Slider, Button, Space, Tag, Rate,
  Checkbox, Drawer, Typography, Badge, Avatar, message, Spin, Pagination,
  Tabs, Empty, Tooltip, Divider, Image
} from 'antd';
import {
  SearchOutlined, ShoppingCartOutlined, HeartOutlined, HeartFilled,
  FilterOutlined, SortAscendingOutlined, EyeOutlined, ShopOutlined,
  StarOutlined, DollarOutlined, TagsOutlined, AppstoreOutlined
} from '@ant-design/icons';
import api from '../../utils/api';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

/**
 * Advanced Marketplace - Marketplace enrichie avec filtres, notes, panier
 */
const AdvancedMarketplace = () => {
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  
  // Filtres
  const [filters, setFilters] = useState({
    search: '',
    category: null,
    minPrice: 0,
    maxPrice: 10000,
    minRating: 0,
    tags: [],
    inStock: false,
    sortBy: 'newest'
  });

  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 12,
    total: 0
  });

  const [selectedProduct, setSelectedProduct] = useState(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [cartVisible, setCartVisible] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  useEffect(() => {
    fetchProducts();
    fetchCategories();
    loadCart();
    loadWishlist();
  }, [filters, pagination.page, pagination.pageSize]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...filters
      };

      const response = await api.get('/api/marketplace/products', { params });
      setProducts(response.data.products || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.pagination?.total || 0
      }));
    } catch (error) {
      console.error('Erreur chargement produits:', error);
      message.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/marketplace/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Erreur chargement catégories:', error);
    }
  };

  const loadCart = () => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      setCart(JSON.parse(savedCart));
    }
  };

  const loadWishlist = () => {
    const savedWishlist = localStorage.getItem('wishlist');
    if (savedWishlist) {
      setWishlist(JSON.parse(savedWishlist));
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    let newCart;
    
    if (existingItem) {
      newCart = cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      );
    } else {
      newCart = [...cart, { ...product, quantity: 1 }];
    }
    
    setCart(newCart);
    localStorage.setItem('cart', JSON.stringify(newCart));
    message.success('Produit ajouté au panier');
  };

  const removeFromCart = (productId) => {
    const newCart = cart.filter(item => item.id !== productId);
    setCart(newCart);
    localStorage.setItem('cart', JSON.stringify(newCart));
    message.success('Produit retiré du panier');
  };

  const updateQuantity = (productId, quantity) => {
    if (quantity < 1) {
      removeFromCart(productId);
      return;
    }
    
    const newCart = cart.map(item =>
      item.id === productId ? { ...item, quantity } : item
    );
    setCart(newCart);
    localStorage.setItem('cart', JSON.stringify(newCart));
  };

  const toggleWishlist = (product) => {
    const isInWishlist = wishlist.some(item => item.id === product.id);
    let newWishlist;
    
    if (isInWishlist) {
      newWishlist = wishlist.filter(item => item.id !== product.id);
      message.success('Retiré des favoris');
    } else {
      newWishlist = [...wishlist, product];
      message.success('Ajouté aux favoris');
    }
    
    setWishlist(newWishlist);
    localStorage.setItem('wishlist', JSON.stringify(newWishlist));
  };

  const getTotalCart = () => {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  };

  const handleCheckout = () => {
    message.info('Redirection vers le paiement...');
    // TODO: Implémenter le processus de paiement
  };

  const ProductCard = ({ product }) => {
    const isInWishlist = wishlist.some(item => item.id === product.id);
    const isInCart = cart.some(item => item.id === product.id);

    return (
      <Card
        hoverable
        cover={
          <div style={{ position: 'relative', height: 200, overflow: 'hidden' }}>
            <Image
              alt={product.name}
              src={(product.image || 'https://placehold.co/300x200').replace('via.placeholder.com', 'placehold.co')}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              preview={false}
            />
            {product.discount && (
              <Tag color="red" style={{ position: 'absolute', top: 10, right: 10 }}>
                -{product.discount}%
              </Tag>
            )}
            {!product.in_stock && (
              <Tag color="default" style={{ position: 'absolute', top: 10, left: 10 }}>
                Rupture de stock
              </Tag>
            )}
            <Button
              type={isInWishlist ? 'primary' : 'default'}
              shape="circle"
              icon={isInWishlist ? <HeartFilled /> : <HeartOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                toggleWishlist(product);
              }}
              style={{ position: 'absolute', top: 10, left: 10 }}
            />
          </div>
        }
        actions={[
          <Tooltip title="Voir détails">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => {
                setSelectedProduct(product);
                setDetailsVisible(true);
              }}
            >
              Détails
            </Button>
          </Tooltip>,
          <Button
            type="primary"
            icon={<ShoppingCartOutlined />}
            onClick={() => addToCart(product)}
            disabled={!product.in_stock || isInCart}
          >
            {isInCart ? 'Dans le panier' : 'Ajouter'}
          </Button>
        ]}
      >
        <Card.Meta
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <Text strong ellipsis style={{ flex: 1 }}>
                {product.name}
              </Text>
            </div>
          }
          description={
            <Space direction="vertical" style={{ width: '100%' }} size="small">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Rate disabled defaultValue={product.rating || 0} style={{ fontSize: 14 }} />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  ({product.reviews_count || 0})
                </Text>
              </div>
              <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 0, fontSize: 12 }}>
                {product.description}
              </Paragraph>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text strong style={{ fontSize: 18, color: '#52c41a' }}>
                  {product.price?.toLocaleString()} MAD
                </Text>
                {product.original_price && (
                  <Text delete type="secondary" style={{ fontSize: 14 }}>
                    {product.original_price?.toLocaleString()} MAD
                  </Text>
                )}
              </div>
              <Space size="small" wrap>
                <Tag color="blue" icon={<ShopOutlined />}>
                  {product.merchant_name}
                </Tag>
                {product.category && (
                  <Tag color="default">{product.category}</Tag>
                )}
              </Space>
            </Space>
          }
        />
      </Card>
    );
  };

  return (
    <div style={{ padding: '24px', backgroundColor: '#f0f2f5', minHeight: '100vh' }}>
      {/* En-tête */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={2} style={{ margin: 0 }}>
            <AppstoreOutlined /> Marketplace
          </Title>
          <Text type="secondary">
            Découvrez nos produits et services
          </Text>
        </div>
        <Badge count={cart.length} showZero>
          <Button
            type="primary"
            size="large"
            icon={<ShoppingCartOutlined />}
            onClick={() => setCartVisible(true)}
          >
            Panier ({getTotalCart().toLocaleString()} MAD)
          </Button>
        </Badge>
      </div>

      <Row gutter={[16, 16]}>
        {/* Filtres latéraux */}
        <Col xs={24} lg={6}>
          <Card title={<><FilterOutlined /> Filtres</>}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* Recherche */}
              <div>
                <Text strong>Recherche</Text>
                <Input
                  placeholder="Rechercher un produit..."
                  prefix={<SearchOutlined />}
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  style={{ marginTop: 8 }}
                />
              </div>

              <Divider style={{ margin: 0 }} />

              {/* Catégories */}
              <div>
                <Text strong>Catégorie</Text>
                <Select
                  placeholder="Toutes les catégories"
                  style={{ width: '100%', marginTop: 8 }}
                  allowClear
                  value={filters.category}
                  onChange={(value) => setFilters({ ...filters, category: value })}
                >
                  {categories.map(cat => (
                    <Select.Option key={cat.id} value={cat.id}>
                      {cat.name}
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <Divider style={{ margin: 0 }} />

              {/* Prix */}
              <div>
                <Text strong>Fourchette de Prix (MAD)</Text>
                <Slider
                  range
                  min={0}
                  max={10000}
                  step={100}
                  value={[filters.minPrice, filters.maxPrice]}
                  onChange={(value) => setFilters({ ...filters, minPrice: value[0], maxPrice: value[1] })}
                  style={{ marginTop: 8 }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text type="secondary">{filters.minPrice} MAD</Text>
                  <Text type="secondary">{filters.maxPrice} MAD</Text>
                </div>
              </div>

              <Divider style={{ margin: 0 }} />

              {/* Note minimale */}
              <div>
                <Text strong>Note minimale</Text>
                <Rate
                  value={filters.minRating}
                  onChange={(value) => setFilters({ ...filters, minRating: value })}
                  style={{ marginTop: 8, display: 'block' }}
                />
              </div>

              <Divider style={{ margin: 0 }} />

              {/* Disponibilité */}
              <Checkbox
                checked={filters.inStock}
                onChange={(e) => setFilters({ ...filters, inStock: e.target.checked })}
              >
                En stock uniquement
              </Checkbox>

              <Divider style={{ margin: 0 }} />

              {/* Trier */}
              <div>
                <Text strong>Trier par</Text>
                <Select
                  style={{ width: '100%', marginTop: 8 }}
                  value={filters.sortBy}
                  onChange={(value) => setFilters({ ...filters, sortBy: value })}
                >
                  <Select.Option value="newest">Plus récents</Select.Option>
                  <Select.Option value="price_asc">Prix croissant</Select.Option>
                  <Select.Option value="price_desc">Prix décroissant</Select.Option>
                  <Select.Option value="rating">Meilleures notes</Select.Option>
                  <Select.Option value="popular">Plus populaires</Select.Option>
                </Select>
              </div>

              <Button
                type="primary"
                block
                onClick={fetchProducts}
              >
                Appliquer les filtres
              </Button>
            </Space>
          </Card>
        </Col>

        {/* Grille de produits */}
        <Col xs={24} lg={18}>
          <Spin spinning={loading}>
            {products.length === 0 ? (
              <Card>
                <Empty description="Aucun produit trouvé" />
              </Card>
            ) : (
              <>
                <Row gutter={[16, 16]}>
                  {products.map(product => (
                    <Col xs={24} sm={12} lg={8} key={product.id}>
                      <ProductCard product={product} />
                    </Col>
                  ))}
                </Row>

                {/* Pagination */}
                <div style={{ marginTop: 24, textAlign: 'center' }}>
                  <Pagination
                    current={pagination.page}
                    pageSize={pagination.pageSize}
                    total={pagination.total}
                    showSizeChanger
                    showTotal={(total) => `Total: ${total} produits`}
                    onChange={(page, pageSize) => {
                      setPagination({ ...pagination, page, pageSize });
                    }}
                  />
                </div>
              </>
            )}
          </Spin>
        </Col>
      </Row>

      {/* Drawer Panier */}
      <Drawer
        title={
          <Space>
            <ShoppingCartOutlined />
            <Text strong>Mon Panier</Text>
            <Badge count={cart.length} />
          </Space>
        }
        open={cartVisible}
        onClose={() => setCartVisible(false)}
        width={400}
        footer={
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <div>
              <Text type="secondary">Total:</Text>
              <Title level={4} style={{ margin: 0, color: '#52c41a' }}>
                {getTotalCart().toLocaleString()} MAD
              </Title>
            </div>
            <Button
              type="primary"
              size="large"
              onClick={handleCheckout}
              disabled={cart.length === 0}
            >
              Commander
            </Button>
          </Space>
        }
      >
        {cart.length === 0 ? (
          <Empty description="Votre panier est vide" />
        ) : (
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {cart.map(item => (
              <Card key={item.id} size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text strong>{item.name}</Text>
                    <Button
                      type="text"
                      danger
                      size="small"
                      onClick={() => removeFromCart(item.id)}
                    >
                      Retirer
                    </Button>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Space>
                      <Button
                        size="small"
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      >
                        -
                      </Button>
                      <Text>{item.quantity}</Text>
                      <Button
                        size="small"
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      >
                        +
                      </Button>
                    </Space>
                    <Text strong style={{ color: '#52c41a' }}>
                      {(item.price * item.quantity).toLocaleString()} MAD
                    </Text>
                  </div>
                </Space>
              </Card>
            ))}
          </Space>
        )}
      </Drawer>

      {/* Drawer Détails Produit */}
      <Drawer
        title="Détails du Produit"
        open={detailsVisible}
        onClose={() => setDetailsVisible(false)}
        width={600}
      >
        {selectedProduct && (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Image
              src={selectedProduct.image || 'https://placehold.co/600x400'}
              alt={selectedProduct.name}
              style={{ width: '100%', borderRadius: 8 }}
            />
            
            <div>
              <Title level={3}>{selectedProduct.name}</Title>
              <Space>
                <Rate disabled defaultValue={selectedProduct.rating || 0} />
                <Text type="secondary">({selectedProduct.reviews_count || 0} avis)</Text>
              </Space>
            </div>

            <div>
              <Text strong style={{ fontSize: 24, color: '#52c41a' }}>
                {selectedProduct.price?.toLocaleString()} MAD
              </Text>
              {selectedProduct.original_price && (
                <Text delete type="secondary" style={{ marginLeft: 12, fontSize: 18 }}>
                  {selectedProduct.original_price?.toLocaleString()} MAD
                </Text>
              )}
            </div>

            <Divider />

            <div>
              <Title level={5}>Description</Title>
              <Paragraph>{selectedProduct.description}</Paragraph>
            </div>

            <div>
              <Title level={5}>Informations</Title>
              <Space direction="vertical">
                <Text><strong>Catégorie:</strong> {selectedProduct.category}</Text>
                <Text><strong>Marchand:</strong> {selectedProduct.merchant_name}</Text>
                <Text><strong>Stock:</strong> {selectedProduct.in_stock ? 'Disponible' : 'Rupture'}</Text>
              </Space>
            </div>

            <Button
              type="primary"
              size="large"
              block
              icon={<ShoppingCartOutlined />}
              onClick={() => {
                addToCart(selectedProduct);
                setDetailsVisible(false);
              }}
              disabled={!selectedProduct.in_stock}
            >
              Ajouter au panier
            </Button>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default AdvancedMarketplace;
