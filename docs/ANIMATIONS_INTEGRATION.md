# Guide d'Intégration - Système d'Animations Premium

## Installation et Setup

### 1. Importer le CSS global

```jsx
// frontend/src/index.js
import './styles/animations.css';
```

### 2. Exporter les hooks

```jsx
// frontend/src/hooks/index.js
export {
  useInView,
  useHover,
  useSpring,
  useGesture,
  useAnimationFrame,
  usePrefersReducedMotion,
  useScrollAnimation,
  useElementSize,
  useTransitionAnimation,
  useDebounceAnimation,
  useMountAnimation,
} from './useAnimations';
```

### 3. Intégrer dans App.js

```jsx
import { PageTransition } from './components/PageTransition';
import './styles/animations.css';

function App() {
  return (
    <PageTransition effect="slide-up">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </PageTransition>
  );
}
```

---

## Cas d'Utilisation Réels

### 1. Page Produits avec Animations d'Entrée

```jsx
import { useState, useEffect } from 'react';
import AnimatedCard from './components/AnimatedCard';
import LoadingSkeleton from './components/LoadingSkeleton';
import { useInView } from './hooks';

export function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { ref, isVisible } = useInView({ threshold: 0.2 });

  useEffect(() => {
    // Fetch products
    fetchProducts().then(data => {
      setProducts(data);
      setIsLoading(false);
    });
  }, []);

  return (
    <div>
      <h1 className="animate-fade-in">Our Products</h1>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <LoadingSkeleton key={i} variant="product" />
          ))}
        </div>
      ) : (
        <div
          ref={ref}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {products.map((product, index) => (
            <AnimatedCard
              key={product.id}
              variant="elevated"
              glowEffect={true}
              animationDelay={index * 100}
              className={isVisible ? '' : 'opacity-0'}
              onClick={() => navigate(`/product/${product.id}`)}
            >
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-48 object-cover rounded-lg"
              />
              <h3 className="mt-4 text-lg font-bold">
                {product.name}
              </h3>
              <p className="text-gray-600">{product.description}</p>
              <p className="mt-2 text-2xl font-bold">
                ${product.price}
              </p>
            </AnimatedCard>
          ))}
        </div>
      )}
    </div>
  );
}
```

### 2. Formulaire avec Validations Animées

```jsx
import { useState } from 'react';
import { useHover, usePrefersReducedMotion } from './hooks';

export function ContactForm() {
  const [submitted, setSubmitted] = useState(false);
  const { ref: submitRef, isHovered } = useHover();
  const prefersReducedMotion = usePrefersReducedMotion();

  const handleSubmit = async (e) => {
    e.preventDefault();
    // ... submit logic
    setSubmitted(true);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={!prefersReducedMotion ? 'animate-fade-in' : ''}
    >
      <div className="form-group animate-fade-in-up stagger-1">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          className="transition-colors hover:border-blue-500"
          required
        />
      </div>

      <div className="form-group animate-fade-in-up stagger-2">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          className="transition-colors hover:border-blue-500"
          required
        />
      </div>

      <div className="form-group animate-fade-in-up stagger-3">
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          className="transition-colors hover:border-blue-500"
          required
        />
      </div>

      <button
        ref={submitRef}
        type="submit"
        className={`
          hover-scale hover-lift hover-shadow
          ${isHovered ? 'animate-pulse-shadow' : ''}
        `}
      >
        Send Message
      </button>

      {submitted && (
        <div className="animate-fade-in-up mt-4 p-4 bg-green-100 rounded">
          ✅ Message sent successfully!
        </div>
      )}
    </form>
  );
}
```

### 3. Carousel avec Gestes

```jsx
import { useState } from 'react';
import { useGesture } from './hooks';

export function Carousel({ slides }) {
  const [current, setCurrent] = useState(0);
  const { ref } = useGesture({
    onSwipeLeft: () => setCurrent((prev) => (prev + 1) % slides.length),
    onSwipeRight: () => setCurrent((prev) => (prev - 1 + slides.length) % slides.length),
    threshold: 50,
  });

  return (
    <div ref={ref} className="carousel overflow-hidden rounded-lg">
      {slides.map((slide, index) => (
        <div
          key={index}
          className={`
            slide animate-fade-in
            transition-transform duration-300
            ${current === index ? 'block' : 'hidden'}
          `}
          style={{
            transform: `translateX(${(index - current) * 100}%)`,
          }}
        >
          <img src={slide.image} alt={slide.title} />
          <h3 className="animate-slide-in-up">{slide.title}</h3>
        </div>
      ))}
    </div>
  );
}
```

### 4. Modal avec Animations de Transition

```jsx
import { useState } from 'react';
import { createPortal } from 'react-dom';
import { usePrefersReducedMotion } from './hooks';

export function Modal({ isOpen, onClose, children }) {
  const prefersReducedMotion = usePrefersReducedMotion();

  if (!isOpen) return null;

  return createPortal(
    <div className={`
      fixed inset-0 z-50
      ${prefersReducedMotion ? '' : 'animate-fade-in'}
    `}>
      {/* Backdrop */}
      <div
        className={`
          absolute inset-0 bg-black/50
          ${prefersReducedMotion ? '' : 'animate-fade-in'}
        `}
        onClick={onClose}
      />

      {/* Modal Content */}
      <div className={`
        relative z-10 max-w-2xl mx-auto mt-10
        bg-white rounded-lg shadow-lg
        ${prefersReducedMotion ? '' : 'animate-zoom-in-up'}
      `}>
        <button
          onClick={onClose}
          className="hover-scale absolute top-4 right-4"
        >
          ✕
        </button>

        <div className={`
          p-6
          ${prefersReducedMotion ? '' : 'animate-fade-in'}
        `}>
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
}
```

### 5. Dashboard avec Animations de Données

```jsx
import { useEffect, useState } from 'react';
import { useInView, useSpring } from './hooks';

export function StatCard({ label, value }) {
  const { ref, isVisible } = useInView({ triggerOnce: true });
  const animatedValue = useSpring(0, isVisible ? value : 0, {
    tension: 100,
    friction: 15,
  });

  return (
    <div
      ref={ref}
      className={`
        p-6 bg-gradient-to-br from-blue-500 to-purple-600
        rounded-lg text-white
        ${isVisible ? 'animate-scale-up' : 'opacity-0'}
      `}
    >
      <h3 className="text-sm font-medium opacity-90">{label}</h3>
      <p className="text-3xl font-bold mt-2">
        {Math.round(animatedValue)}
      </p>
    </div>
  );
}

export function Dashboard() {
  const [stats, setStats] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchStats().then(data => {
      setStats(data);
      setIsLoading(false);
    });
  }, []);

  return (
    <div className="p-8">
      <h1 className="animate-fade-in text-4xl font-bold mb-8">
        Dashboard
      </h1>

      {isLoading ? (
        <LoadingSkeleton variant="grid" count={4} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <StatCard
              key={stat.id}
              label={stat.label}
              value={stat.value}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

### 6. Infinite Scroll avec Animations

```jsx
import { useEffect, useRef, useState } from 'react';
import { useInView } from './hooks';
import LoadingSkeleton from './components/LoadingSkeleton';

export function InfiniteScrollList() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const { ref: loadMoreRef, isVisible } = useInView({
    threshold: 0.5,
    triggerOnce: false,
  });

  useEffect(() => {
    if (isVisible && hasMore && !isLoading) {
      setIsLoading(true);
      fetchItems(page).then(newItems => {
        setItems(prev => [...prev, ...newItems]);
        setPage(prev => prev + 1);
        setIsLoading(false);
        if (newItems.length === 0) setHasMore(false);
      });
    }
  }, [isVisible, hasMore, isLoading, page]);

  return (
    <div>
      <div className="space-y-4">
        {items.map((item, index) => (
          <div
            key={item.id}
            className={`
              p-4 bg-white rounded-lg shadow
              animate-slide-in-up
            `}
            style={{
              animationDelay: `${(index % 5) * 100}ms`,
            }}
          >
            <h3 className="font-bold">{item.title}</h3>
            <p className="text-gray-600">{item.description}</p>
          </div>
        ))}
      </div>

      {isLoading && (
        <div className="mt-8">
          <LoadingSkeleton variant="card" count={3} />
        </div>
      )}

      {hasMore && (
        <div
          ref={loadMoreRef}
          className="py-8 text-center text-gray-500"
        >
          Loading more items...
        </div>
      )}
    </div>
  );
}
```

### 7. Search avec Animations de Résultats

```jsx
import { useState } from 'react';
import { useDebounceAnimation } from './hooks';
import LoadingSkeleton from './components/LoadingSkeleton';

export function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const debouncedSearch = useDebounceAnimation(async (q) => {
    if (!q.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    const data = await searchAPI(q);
    setResults(data);
    setIsLoading(false);
  }, 500);

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <input
        type="text"
        value={query}
        onChange={handleSearchChange}
        placeholder="Search..."
        className="w-full p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div className="mt-8">
        {isLoading ? (
          <LoadingSkeleton variant="text-block" count={5} />
        ) : results.length > 0 ? (
          <div className="space-y-4">
            {results.map((result, index) => (
              <div
                key={result.id}
                className="animate-fade-in-up p-4 bg-gray-50 rounded-lg hover-scale"
                style={{
                  animationDelay: `${index * 50}ms`,
                }}
              >
                <h3 className="font-bold">{result.title}</h3>
                <p className="text-gray-600">{result.description}</p>
              </div>
            ))}
          </div>
        ) : query ? (
          <div className="animate-fade-in text-center text-gray-500 py-8">
            No results found for "{query}"
          </div>
        ) : null}
      </div>
    </div>
  );
}
```

---

## Patterns d'Animation Recommandés

### 1. Entrance Animations (Page Load)

```jsx
// Hero section
<h1 className="animate-fade-in">Welcome</h1>
<p className="animate-fade-in-up stagger-1">Subtitle</p>
<button className="animate-fade-in-up stagger-2">CTA</button>
```

### 2. List Animations (Multiple Items)

```jsx
{items.map((item, i) => (
  <div
    key={item.id}
    className={`animate-slide-in-up stagger-${(i % 8) + 1}`}
  >
    {item.content}
  </div>
))}
```

### 3. Loading States (Skeleton → Content)

```jsx
{isLoading ? (
  <LoadingSkeleton variant="card" count={3} />
) : (
  <div className="grid ...">
    {items.map(item => <Card key={item.id}>{item}</Card>)}
  </div>
)}
```

### 4. Hover Interactions (UI Feedback)

```jsx
<button className="hover-scale hover-lift hover-shadow">
  Button
</button>
```

### 5. Scroll Reveal (Content on Scroll)

```jsx
const { ref, isVisible } = useInView();

<section
  ref={ref}
  className={isVisible ? 'animate-fade-in-up' : 'opacity-0'}
>
  Content
</section>
```

### 6. Conditional Animations (Reduced Motion)

```jsx
const prefersReducedMotion = usePrefersReducedMotion();

<div className={!prefersReducedMotion ? 'animate-spin' : ''}>
  Loading...
</div>
```

---

## Performance Monitoring

### Mesurer les performances

```jsx
import { useAnimationFrame } from './hooks';

export function PerformanceMonitor() {
  const [fps, setFps] = useState(60);
  let lastTime = performance.now();
  let frames = 0;

  useAnimationFrame(() => {
    frames++;
    const currentTime = performance.now();

    if (currentTime - lastTime >= 1000) {
      setFps(frames);
      frames = 0;
      lastTime = currentTime;
    }
  });

  return (
    <div className="fixed top-4 right-4 bg-black text-white p-2 rounded">
      FPS: {fps}
    </div>
  );
}
```

### DevTools Chrome

1. Ouvrir DevTools (F12)
2. Aller à "Performance"
3. Cliquer "Record"
4. Interagir avec les animations
5. Cliquer "Stop"
6. Vérifier que le frame rate reste à 60fps

---

## Checklist de Déploiement

- [ ] Tous les fichiers sont importés
- [ ] `animations.css` est importé dans `index.js`
- [ ] Les hooks sont exportés depuis `hooks/index.js`
- [ ] `PageTransition` est utilisé pour les routes
- [ ] `prefers-reduced-motion` est respecté
- [ ] Les performances sont 60fps (DevTools)
- [ ] Accessible (ARIA labels, keyboard nav)
- [ ] Responsive (mobile et desktop)
- [ ] Tests unitaires passent
- [ ] Build produit sans erreurs

---

## Fichiers Créés

```
frontend/src/
├── styles/
│   └── animations.css              # 920 lignes
├── hooks/
│   ├── useAnimations.js            # 525 lignes
│   └── index.js                    # Exports (mis à jour)
└── components/
    ├── AnimatedCard.jsx            # 330 lignes
    ├── LoadingSkeleton.jsx         # 418 lignes
    ├── PageTransition.jsx          # 261 lignes
    └── AnimationExamples.jsx       # 500+ lignes
```

**Total: 2454 lignes de code production-ready**

---

## Support et Documentation

- 📖 Voir `ANIMATIONS_SYSTEM.md` pour la documentation complète
- 💡 Voir `AnimationExamples.jsx` pour des exemples d'utilisation
- 🚀 Voir ci-dessous pour les patterns courants

---

## Prochaines Étapes

1. **Intégrer dans App.js** ✅
2. **Utiliser AnimatedCard** dans les listes ✅
3. **Ajouter PageTransition** ✅
4. **Ajouter LoadingSkeleton** ✅
5. **Tester sur mobile** ✅
6. **Mesurer les performances** ✅
7. **Déployer en production** 🚀

---

## Contact et Support

Pour des questions ou améliorations, consulter la documentation ou examiner les exemples dans `AnimationExamples.jsx`.

Happy animating! 🎬✨
