# 🏛️ Architecture GetYourShare

## Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture Système](#architecture-système)
- [Backend](#backend)
- [Frontend](#frontend)
- [Base de Données](#base-de-données)
- [Sécurité](#sécurité)
- [Performance](#performance)
- [Scalabilité](#scalabilité)

## 🎯 Vue d'ensemble

GetYourShare suit une architecture **client-serveur moderne** avec :

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Dashboard│  │Marketplace│  │ Analytics│   +50 pages │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Auth   │  │   CRUD   │  │WebSocket │   +200 EP   │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
         ↓                ↓                    ↓
┌────────────────┐  ┌──────────┐  ┌────────────────────┐
│   PostgreSQL   │  │  Redis   │  │  External APIs     │
│   (Supabase)   │  │  (Cache) │  │ (Shopify, Stripe)  │
└────────────────┘  └──────────┘  └────────────────────┘
```

## 🏗️ Architecture Système

### Modèle MVC Étendu

```
Model (Database)
    ↓
Controller (Backend API)
    ↓
View (React Frontend)
    ↓
User
```

### Couches Applicatives

1. **Présentation** (Frontend)
   - React Components
   - State Management (Context API)
   - Routing (React Router)

2. **Application** (Backend)
   - API Endpoints (FastAPI)
   - Business Logic
   - Validators (Pydantic)

3. **Domaine**
   - Modèles métier
   - Services
   - Use Cases

4. **Infrastructure**
   - Database (Supabase)
   - Cache (Redis)
   - File Storage
   - External APIs

## 🔧 Backend

### Structure des Fichiers

```
backend/
├── server.py                    # Point d'entrée principal
├── auth.py                      # Authentification JWT
├── supabase_client.py           # Client DB
│
├── endpoints/                   # Routes API par domaine
│   ├── admin_*.py              # Endpoints admin
│   ├── marketplace_*.py        # Marketplace
│   ├── services_leads_*.py     # Leads
│   ├── notifications_*.py      # Notifications
│   ├── reports_*.py            # Rapports
│   └── ...                     # +50 fichiers
│
├── middleware/
│   ├── security.py             # Rate limiting, CORS
│   └── logging.py              # Audit logs
│
├── services/
│   ├── payment_service.py      # Paiements
│   ├── email_service.py        # Emails
│   └── cache_service.py        # Cache Redis
│
└── utils/
    ├── logger.py
    └── helpers.py
```

### Patterns Utilisés

#### 1. Dependency Injection (FastAPI)

```python
@router.get("/users")
async def get_users(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user injecté automatiquement
    pass
```

#### 2. Repository Pattern

```python
class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, user_id: str):
        return self.db.table('users').select('*').eq('id', user_id).execute()
```

#### 3. Service Layer

```python
class PaymentService:
    def __init__(self, payment_gateway):
        self.gateway = payment_gateway
    
    async def process_payment(self, amount, method):
        # Business logic
        return await self.gateway.charge(amount, method)
```

### API Design

#### RESTful Conventions

```
GET    /api/products       # Liste
GET    /api/products/:id   # Détail
POST   /api/products       # Création
PUT    /api/products/:id   # Mise à jour complète
PATCH  /api/products/:id   # Mise à jour partielle
DELETE /api/products/:id   # Suppression
```

#### Réponses Standardisées

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### Gestion Erreurs

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email already exists",
    "details": {...}
  }
}
```

### Authentification Flow

```
1. Login
   POST /api/auth/login
   { email, password }
   
2. Serveur vérifie credentials
   
3. Génère JWT token
   { user_id, role, exp: 24h }
   
4. Client stocke token
   localStorage.setItem('token', jwt)
   
5. Requêtes suivantes
   Header: Authorization: Bearer {jwt}
   
6. Middleware vérifie token
   jwt.decode(token, SECRET_KEY)
   
7. Injecte current_user
   Depends(get_current_user)
```

### WebSocket (Notifications)

```python
# Backend
@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = verify_token(token)
    await manager.connect(websocket, user.id)
    
    while True:
        data = await websocket.receive_text()
        # Process message

# Frontend
const ws = new WebSocket('ws://localhost:8000/ws/notifications?token=xxx');
ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    showNotification(notification);
};
```

## 🎨 Frontend

### Architecture Composants

```
src/
├── App.js                      # Root component
├── index.js                    # Entry point
│
├── components/                 # Composants réutilisables
│   ├── common/                # Buttons, Inputs, Cards
│   ├── layout/                # Header, Sidebar, Footer
│   ├── forms/                 # Form components
│   └── charts/                # Graphiques
│
├── pages/                     # Pages principales
│   ├── Dashboard.jsx
│   ├── Login.jsx
│   ├── marketplace/
│   ├── admin/
│   └── ...                    # +60 pages
│
├── context/                   # Context API
│   ├── AuthContext.jsx       # Authentification
│   ├── ThemeContext.jsx      # Theme dark/light
│   └── ToastContext.jsx      # Notifications
│
├── hooks/                     # Custom hooks
│   ├── useAuth.js
│   ├── useApi.js
│   └── useDebounce.js
│
├── utils/
│   ├── api.js                # Axios instance
│   ├── helpers.js
│   └── constants.js
│
└── i18n/                     # Internationalisation
    ├── fr.json
    ├── en.json
    └── es.json
```

### State Management (Context API)

```javascript
// AuthContext.jsx
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    setUser(response.data.user);
    localStorage.setItem('token', response.data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Usage
const { user, login, logout } = useAuth();
```

### Routing

```javascript
<BrowserRouter>
  <Routes>
    {/* Public routes */}
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    
    {/* Protected routes */}
    <Route element={<ProtectedRoute />}>
      <Route path="/dashboard" element={<Dashboard />} />
      
      {/* Role-based routes */}
      <Route element={<RoleProtectedRoute allowedRoles={['admin']} />}>
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Route>
    </Route>
  </Routes>
</BrowserRouter>
```

### API Communication

```javascript
// utils/api.js
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercepteur token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 💾 Base de Données

### Schéma Principal

```sql
-- Users (base)
users
├── id (uuid, PK)
├── email (unique)
├── password_hash
├── role (admin/merchant/influencer/commercial)
├── subscription_tier_id (FK)
└── metadata (jsonb)

-- Products
products
├── id (uuid, PK)
├── user_id (FK -> users)
├── name
├── price
├── commission_rate
└── stock

-- Campaigns
campaigns
├── id (uuid, PK)
├── merchant_id (FK -> users)
├── name
├── budget
└── status

-- Affiliate Links
affiliate_links
├── id (uuid, PK)
├── influencer_id (FK -> users)
├── campaign_id (FK -> campaigns)
├── short_code (unique)
└── click_count

-- Transactions
transactions
├── id (uuid, PK)
├── link_id (FK -> affiliate_links)
├── amount
├── commission
└── status

-- Subscriptions
subscriptions
├── id (uuid, PK)
├── user_id (FK -> users)
├── plan_id (FK -> subscription_plans)
├── status (active/cancelled/expired)
└── current_period_end
```

### Relations

```
users (1) ─────────< (N) products
users (1) ─────────< (N) campaigns
users (1) ─────────< (N) affiliate_links
campaigns (1) ──────< (N) affiliate_links
affiliate_links (1) < (N) transactions
```

### Indexes

```sql
-- Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_links_short_code ON affiliate_links(short_code);
CREATE INDEX idx_transactions_date ON transactions(created_at DESC);
CREATE INDEX idx_clicks_link_id ON clicks(link_id);
```

### Row Level Security (RLS)

```sql
-- Exemple: Users peuvent voir seulement leurs données
CREATE POLICY "Users can view own data"
ON products
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all"
ON products
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM users
    WHERE users.id = auth.uid()
    AND users.role = 'admin'
  )
);
```

## 🔒 Sécurité

### Layers de Sécurité

```
1. Network Layer
   ├── SSL/TLS (HTTPS)
   ├── CORS policy
   └── Rate limiting

2. Application Layer
   ├── JWT authentication
   ├── 2FA (TOTP)
   ├── Input validation (Pydantic)
   └── SQL injection protection (ORM)

3. Data Layer
   ├── Encryption at rest
   ├── Row Level Security (RLS)
   └── Audit logs

4. Infrastructure
   ├── Firewall
   ├── DDoS protection
   └── Regular backups
```

### Authentification Flow Détaillé

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│ Client  │                 │   API   │                 │   DB     │
└────┬────┘                 └────┬────┘                 └────┬─────┘
     │                           │                           │
     │  1. POST /login           │                           │
     │  {email, password}        │                           │
     ├──────────────────────────>│                           │
     │                           │  2. Verify credentials    │
     │                           ├──────────────────────────>│
     │                           │<──────────────────────────┤
     │                           │  3. Generate JWT          │
     │                           │  {uid, role, exp}         │
     │  4. Return token          │                           │
     │<──────────────────────────┤                           │
     │  {token, user}            │                           │
     │                           │                           │
     │  5. GET /api/products     │                           │
     │  Header: Bearer {token}   │                           │
     ├──────────────────────────>│                           │
     │                           │  6. Verify & decode JWT   │
     │                           │                           │
     │                           │  7. Query with user_id    │
     │                           ├──────────────────────────>│
     │                           │<──────────────────────────┤
     │  8. Return data           │                           │
     │<──────────────────────────┤                           │
```

### Rate Limiting

```python
# Per IP
@limiter.limit("100/hour")

# Per user
@limiter.limit("1000/hour", key_func=lambda: current_user.id)

# Per endpoint
@limiter.limit("10/minute")  # Login attempts
```

## ⚡ Performance

### Stratégies de Cache

```python
# Cache Redis
@cache_result(ttl=3600)  # 1 heure
def get_products():
    return db.query(Product).all()

# Cache invalide automatic
@invalidate_cache('products:*')
def create_product(product):
    db.add(product)
    db.commit()
```

### Pagination Optimisée

```python
# Cursor-based pagination
@router.get("/products")
def get_products(
    cursor: Optional[str] = None,
    limit: int = 20
):
    query = db.query(Product)
    if cursor:
        query = query.filter(Product.id > cursor)
    
    products = query.limit(limit + 1).all()
    has_more = len(products) > limit
    
    return {
        'data': products[:limit],
        'next_cursor': products[limit].id if has_more else None,
        'has_more': has_more
    }
```

### Optimisation Requêtes

```python
# ❌ N+1 problem
users = db.query(User).all()
for user in users:
    user.products  # +1 query per user

# ✅ Eager loading
users = db.query(User).options(
    joinedload(User.products)
).all()  # 1 query total
```

## 📈 Scalabilité

### Horizontal Scaling

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  App 1   │     │  App 2   │     │  App 3   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     └────────────────┴────────────────┘
                      │
              ┌───────┴────────┐
              │ Load Balancer  │
              └────────────────┘
```

### Database Scaling

```
┌─────────────────┐
│   Primary DB    │ (Write)
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼───┐  ┌───▼───┐
│Replica│  │Replica│ (Read)
└───────┘  └───────┘
```

### Microservices (Future)

```
┌────────────┐   ┌────────────┐   ┌────────────┐
│   Auth     │   │  Products  │   │  Payments  │
│  Service   │   │  Service   │   │  Service   │
└────────────┘   └────────────┘   └────────────┘
       │                │                 │
       └────────────────┴─────────────────┘
                        │
                  ┌─────┴──────┐
                  │  API       │
                  │  Gateway   │
                  └────────────┘
```

## 📊 Monitoring & Observabilité

### Métriques Clés

1. **Performance**
   - Response time (p50, p95, p99)
   - Throughput (requests/sec)
   - Error rate

2. **Business**
   - Active users
   - Conversions
   - Revenue (MRR, ARR)

3. **Infrastructure**
   - CPU, Memory
   - Database connections
   - Cache hit rate

### Logging

```python
# Structured logging
logger.info("User login", extra={
    'user_id': user.id,
    'ip': request.client.host,
    'user_agent': request.headers.get('user-agent'),
    'timestamp': datetime.utcnow()
})
```

### Health Checks

```python
@router.get("/health")
def health_check():
    return {
        'status': 'healthy',
        'database': check_db_connection(),
        'redis': check_redis_connection(),
        'version': '1.0.0',
        'uptime': get_uptime()
    }
```

---

**📚 Pour plus de détails, consultez :**
- [README.md](README.md) - Vue d'ensemble
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - Documentation API
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Guide déploiement
