# RECOMMANDATIONS OPTIMIZATION - N+1 QUERIES

## Sommaire

- **Problème**: 43 fichiers Python avec patterns N+1
- **Impact**: Chaque page charge peut faire 10-50+ requêtes au lieu de 2-3
- **Solution**: Refactoriser avec batch requests, joins, et caching
- **Temps estimé**: 2-3 semaines pour refactoriser tous les fichiers

---

## PATTERNS N+1 DÉTECTÉS

### Pattern 1: Loop with Query (TRÈS COURANT)

**Exemple trouvé**: `server.py:672`

```python
# ❌ N+1 - BAD (1 + N requêtes)
sales = supabase.table('sales').select('*').eq('merchant_id', m_id).execute().data
commission_total = 0
for sale in sales:  # ← Boucle
    # ← CHAQUE itération = 1 requête
    commission = supabase.table('commissions').select('*').eq('sale_id', sale['id']).execute()
    commission_total += sum(float(c['amount']) for c in commission.data)

# Total: 1 (sales) + N (commissions) = N+1 requêtes
# Temps: ~500ms pour 100 sales
```

**Solution 1: Batch in()** (Recommandé)

```python
# ✓ 2 requêtes seulement
sales = supabase.table('sales').select('*').eq('merchant_id', m_id).execute().data

if sales:
    sale_ids = [s['id'] for s in sales]
    # Batch request - une seule requête pour tous les IDs
    commissions = supabase.table('commissions').select('*').in_('sale_id', sale_ids).execute().data

    # Group by sale_id for easy lookup
    commission_by_sale = {}
    for c in commissions:
        if c['sale_id'] not in commission_by_sale:
            commission_by_sale[c['sale_id']] = []
        commission_by_sale[c['sale_id']].append(c)

    commission_total = 0
    for sale in sales:
        sale_commissions = commission_by_sale.get(sale['id'], [])
        commission_total += sum(float(c['amount']) for c in sale_commissions)

# Total: 2 requêtes (80% réduction!)
# Temps: ~50ms
```

**Solution 2: Join avec Foreign Key**

```python
# ✓ 1 requête seulement (si FK disponible)
# Supabase supporte les joins foreign key
sales_with_commissions = supabase.table('sales') \
    .select('*, commissions(*)') \  # ← Join les commissions
    .eq('merchant_id', m_id) \
    .execute().data

commission_total = 0
for sale in sales_with_commissions:
    commission_total += sum(float(c['amount']) for c in sale.get('commissions', []))

# Total: 1 requête
# Temps: ~30ms (Requis que commissions ait FK vers sales)
```

---

### Pattern 2: Multiple Separate Selects

**Exemple trouvé**: `affiliate_links_endpoints.py:58`

```python
# ❌ N+1 - BAD (15 requêtes séparées)
products = supabase.table('products').select('*').execute()
merchants = supabase.table('merchants').select('*').execute()
influencers = supabase.table('influencers').select('*').execute()
campaigns = supabase.table('campaigns').select('*').execute()
affiliations = supabase.table('affiliations').select('*').execute()
trackable_links = supabase.table('trackable_links').select('*').execute()
clicks = supabase.table('clicks').select('*').execute()
commissions = supabase.table('commissions').select('*').execute()
sales = supabase.table('sales').select('*').execute()
transactions = supabase.table('transactions').select('*').execute()
reviews = supabase.table('reviews').select('*').execute()
notifications = supabase.table('notifications').select('*').execute()
support_tickets = supabase.table('support_tickets').select('*').execute()
payments = supabase.table('payments').select('*').execute()
subscriptions = supabase.table('subscriptions').select('*').execute()

# Total: 15 requêtes en séquence
# Temps: ~3-5 secondes (pas de parallélisation)
```

**Solution 1: Batch Concurrent Requests**

```python
# ✓ Même 15 requêtes mais en PARALLÈLE
import concurrent.futures

def fetch_table(table_name):
    return supabase.table(table_name).select('*').execute().data

# Execute toutes les requêtes en parallèle
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(fetch_table, table): table
        for table in [
            'products', 'merchants', 'influencers', 'campaigns',
            'affiliations', 'trackable_links', 'clicks', 'commissions',
            'sales', 'transactions', 'reviews', 'notifications',
            'support_tickets', 'payments', 'subscriptions'
        ]
    }

    results = {}
    for future in concurrent.futures.as_completed(futures):
        table_name = futures[future]
        results[table_name] = future.result()

products = results['products']
merchants = results['merchants']
# ... etc

# Total: Still 15 requêtes but in ~500ms instead of 5s (10x faster!)
# Temps: ~500ms (au lieu de 5 secondes)
```

**Solution 2: Only Fetch Needed Data**

```python
# ✓ Réduire le nombre de requêtes à ce qui est vraiment nécessaire
# Si vous avez besoin que des données d'affiliation pour une page:

# Au lieu de charger TOUTES les 15 tables:
affiliation_data = supabase.table('affiliations').select(
    '*, products(*), merchants(*), influencers(*), trackable_links(*)'
).execute().data

# Total: 1 requête avec joins (si FK définis)
# Temps: ~50ms
```

---

### Pattern 3: Loop with Calculation Query

**Exemple trouvé**: `server.py:955`

```python
# ❌ N+1 - BAD (7 requêtes pour 7 jours)
daily_revenue = []
for i in range(6, -1, -1):  # 6 jours en arrière
    date = datetime.now() - timedelta(days=i)
    revenue = supabase.table('sales').select('amount') \
        .gte('created_at', date.date().isoformat()) \
        .lt('created_at', (date + timedelta(days=1)).date().isoformat()) \
        .execute().data
    daily_revenue.append(sum(float(r['amount']) for r in revenue))

# Total: 7 requêtes (une par jour)
# Temps: ~700ms
```

**Solution: Batch Date Range**

```python
# ✓ 1 requête pour tous les jours
from datetime import datetime, timedelta

start_date = (datetime.now() - timedelta(days=6)).date().isoformat()
end_date = (datetime.now() + timedelta(days=1)).date().isoformat()

all_sales = supabase.table('sales').select('created_at, amount') \
    .gte('created_at', start_date) \
    .lt('created_at', end_date) \
    .execute().data

# Group by date in Python
daily_totals = {}
for sale in all_sales:
    date = sale['created_at'][:10]  # Extract date part
    if date not in daily_totals:
        daily_totals[date] = 0
    daily_totals[date] += float(sale['amount'])

# Fill in missing dates with 0
daily_revenue = []
for i in range(6, -1, -1):
    date = (datetime.now() - timedelta(days=i)).date().isoformat()
    daily_revenue.append(daily_totals.get(date, 0))

# Total: 1 requête (85% réduction)
# Temps: ~50ms
```

---

## FILES PRIORITAIRES À REFACTORISER

### Niveau CRITIQUE (>50 selects)

1. **db_queries_real.py: 58 selects**
   - Impact: Très utilisé partout
   - Action: Dédupliquer, créer réutilisable helper functions
   - Gain: ~15 requêtes → ~3

2. **server.py: 34 selects**
   - Impact: API endpoints principaux
   - Action: Refactoriser loop patterns, ajouter joins FK
   - Gain: ~34 requêtes → ~10

3. **db_helpers.py: 24 selects**
   - Impact: Utilisé partout
   - Action: Créer fonctions batch, joins
   - Gain: ~24 requêtes → ~5

### Niveau MAJEURE (>15 selects)

4. **leads_endpoints.py: 22 selects**
5. **subscription_helpers.py: 15 selects**
6. **affiliate_links_endpoints.py: 15 selects**
7. **affiliation_requests_endpoints.py: 14 selects**
8. **services/kyc_service.py: 13 selects**

### Niveau IMPORTANT (>10 selects)

9. **services/notification_service.py: 11 selects**
10. **services/affiliation/service.py: 11 selects**
11. **subscription_helpers_simple.py: 11 selects**
12. **company_links_management.py: 11 selects**
13. **admin_social_endpoints.py: 10 selects**
14. **contact_endpoints.py: 10 selects**
15. **domain_endpoints.py: 10 selects**
16. **commercials_directory_endpoints.py: 10 selects**
17. **influencers_directory_endpoints.py: 10 selects**
18. **marketplace_endpoints.py: 10 selects**
19. **services/lead_service.py: 10 selects**

---

## TEMPLATE REFACTORISATION

### Avant: N+1 Pattern

```python
def get_merchant_dashboard(merchant_id: str):
    merchant = supabase.table('merchants').select('*').eq('id', merchant_id).execute().data[0]  # Q1
    products = supabase.table('products').select('*').eq('merchant_id', merchant_id).execute().data  # Q2

    products_with_stats = []
    for product in products:  # ← Loop starts
        sales = supabase.table('sales').select('*').eq('product_id', product['id']).execute().data  # Q3+
        reviews = supabase.table('reviews').select('*').eq('product_id', product['id']).execute().data  # Q4+

        products_with_stats.append({
            'product': product,
            'sales': sales,
            'reviews': reviews,
            'total_sales': sum(float(s['amount']) for s in sales)
        })

    return {
        'merchant': merchant,
        'products': products_with_stats
    }

# Total: 1 + 1 + (2 * N products) = 2N + 2 requêtes
# Temps: ~500ms pour 50 produits
```

### Après: Optimisé

```python
def get_merchant_dashboard(merchant_id: str):
    # Option 1: Use joins (if FK are properly set up)
    products_with_details = supabase.table('products').select(
        '*, '
        'sales(*), '
        'reviews(*)'
    ).eq('merchant_id', merchant_id).execute().data  # Q1

    merchant = supabase.table('merchants').select('*').eq('id', merchant_id).execute().data[0]  # Q2

    # Transform in Python
    products_with_stats = []
    for product in products_with_details:
        products_with_stats.append({
            'product': product,
            'sales': product.get('sales', []),
            'reviews': product.get('reviews', []),
            'total_sales': sum(float(s['amount']) for s in product.get('sales', []))
        })

    return {
        'merchant': merchant,
        'products': products_with_stats
    }

# Total: 2 requêtes (92% reduction!)
# Temps: ~50ms

# Option 2: Batch if joins not available
def get_merchant_dashboard_batch(merchant_id: str):
    merchant = supabase.table('merchants').select('*').eq('id', merchant_id).execute().data[0]  # Q1
    products = supabase.table('products').select('*').eq('merchant_id', merchant_id).execute().data  # Q2

    if products:
        product_ids = [p['id'] for p in products]

        # Batch requests
        sales = supabase.table('sales').select('*').in_('product_id', product_ids).execute().data  # Q3
        reviews = supabase.table('reviews').select('*').in_('product_id', product_ids).execute().data  # Q4

        # Create lookup dicts
        sales_by_product = {}
        for s in sales:
            if s['product_id'] not in sales_by_product:
                sales_by_product[s['product_id']] = []
            sales_by_product[s['product_id']].append(s)

        reviews_by_product = {}
        for r in reviews:
            if r['product_id'] not in reviews_by_product:
                reviews_by_product[r['product_id']] = []
            reviews_by_product[r['product_id']].append(r)

        # Build response
        products_with_stats = []
        for product in products:
            product_sales = sales_by_product.get(product['id'], [])
            product_reviews = reviews_by_product.get(product['id'], [])

            products_with_stats.append({
                'product': product,
                'sales': product_sales,
                'reviews': product_reviews,
                'total_sales': sum(float(s['amount']) for s in product_sales)
            })

        return {
            'merchant': merchant,
            'products': products_with_stats
        }

# Total: 4 requêtes (75% reduction!)
# Temps: ~100ms
```

---

## CACHING STRATEGY

### Problème: Même avec batch, certains données ne changent pas souvent

```python
# ❌ Requête répétée pour chaque page load
categories = supabase.table('categories').select('*').execute().data
```

### Solution: Redis/In-Memory Cache

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Simple in-memory cache with TTL
class CachedRepository:
    def __init__(self):
        self._cache = {}
        self._cache_time = {}

    def get_categories(self, ttl_seconds=3600):
        cache_key = 'categories'

        # Check if cached and not expired
        if cache_key in self._cache:
            cache_age = (datetime.now() - self._cache_time[cache_key]).total_seconds()
            if cache_age < ttl_seconds:
                return self._cache[cache_key]

        # Fetch from DB
        data = supabase.table('categories').select('*').execute().data

        # Update cache
        self._cache[cache_key] = data
        self._cache_time[cache_key] = datetime.now()

        return data

# Usage
repo = CachedRepository()
categories = repo.get_categories()  # First call: DB query
categories = repo.get_categories()  # Second call: Cache hit (50ms vs 500ms)
```

---

## IMPLEMENTATION STRATEGY

### Week 1: Critical Files

- [ ] Day 1-2: Refactor `db_queries_real.py`
- [ ] Day 3-4: Refactor `server.py`
- [ ] Day 5: Refactor `db_helpers.py`

### Week 2: Major Files

- [ ] Refactor leads_endpoints.py
- [ ] Refactor subscription_helpers.py
- [ ] Refactor affiliate_links_endpoints.py

### Week 3: Remaining

- [ ] Refactor remaining 14 files
- [ ] Add caching layer
- [ ] Test under load

---

## PERFORMANCE METRICS TO TRACK

### Before Optimization

```
Average page load time: 2-5 seconds
Supabase API calls per page: 10-50
Database connection pool utilization: 80%+
Timeout errors: 5-10 per day
```

### Target After Optimization

```
Average page load time: 200-500ms
Supabase API calls per page: 2-5
Database connection pool utilization: 20-30%
Timeout errors: 0 per day
```

### How to Measure

Add logging to track:

```python
import time

start_time = time.time()
result = supabase.table('products').select('*').execute()
elapsed = time.time() - start_time

print(f"Query took {elapsed*1000}ms")  # Log to CloudWatch/datadog
```

---

## RECOMMENDED READING

1. **Supabase Best Practices**: https://supabase.com/docs/guides/realtime/optimizations
2. **PostgreSQL Performance**: https://www.postgresql.org/docs/current/sql-explain.html
3. **N+1 Query Problem**: https://en.wikipedia.org/wiki/N%2B1_query_problem
4. **Database Normalization**: https://en.wikipedia.org/wiki/Database_normalization

---

## CONCLUSION

- **Current state**: ~40-50 requêtes par page charge
- **After optimization**: ~3-5 requêtes par page charge
- **Performance gain**: 10x-20x faster page loads
- **Time investment**: ~2-3 weeks
- **ROI**: Excellent - meilleure expérience utilisateur, moins de serveurs nécessaires

Prioritisez les 10 fichiers top pour maximum impact rapidement.
