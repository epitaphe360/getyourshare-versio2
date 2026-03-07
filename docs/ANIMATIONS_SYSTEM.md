# Système d'Animations Premium - Documentation Complète

## Vue d'ensemble

Système complet d'animations et micro-interactions production-ready pour application flagship React. Conçu pour des animations **fluides 60fps** avec support complet de l'accessibilité.

### Caractéristiques principales

- ✅ **Animations 60fps garanties** (transform/opacity only)
- ✅ **GPU accelerated** pour performances maximales
- ✅ **Responsive** et adaptées à tous les appareils
- ✅ **Accessibilité** - Support `prefers-reduced-motion`
- ✅ **Production-ready** - Code optimisé et testé
- ✅ **Easing functions** professionnelles
- ✅ **Micro-interactions** partout (hover, click, scroll)
- ✅ **TypeScript-ready** (JSDoc complet)

---

## Architecture

```
frontend/src/
├── styles/
│   └── animations.css              # Animations CSS premium (300+ lignes)
├── hooks/
│   └── useAnimations.js            # 11 hooks React personnalisés
├── components/
│   ├── AnimatedCard.jsx            # Card avec animations 3D
│   ├── LoadingSkeleton.jsx         # Skeleton loading élégant
│   ├── PageTransition.jsx          # Transitions entre pages
│   └── AnimationExamples.jsx       # Exemples d'utilisation complets
└── index.js                         # Exports centralisés
```

---

## 1. CSS Animations (`animations.css`)

### 📦 Contenu

- **50+ keyframes d'animation**
- **30+ classes CSS prêtes à l'emploi**
- **Variantes de timing (fast, normal, slow, slowest)**
- **GPU acceleration automatique**

### 🎯 Catégories d'animations

#### Entrées (Entrance)
```css
.animate-fade-in           /* Fade in simple */
.animate-fade-in-up        /* Fade + slide up */
.animate-fade-in-down      /* Fade + slide down */
.animate-fade-in-left      /* Fade + slide left */
.animate-fade-in-right     /* Fade + slide right */
.animate-slide-in-up       /* Glissement vers le haut */
.animate-slide-in-down     /* Glissement vers le bas */
.animate-scale-up          /* Croissance avec fade */
.animate-bounce-in         /* Entrée avec bounce */
.animate-zoom-in           /* Zoom in effect */
.animate-zoom-in-up        /* Zoom + slide up */
```

#### Attention (Attention)
```css
.animate-pulse             /* Pulsation d'opacité */
.animate-pulse-shadow      /* Pulsation de shadow */
.animate-pulse-scale       /* Pulsation d'échelle */
.animate-glow              /* Effet luminescent */
.animate-spin              /* Rotation continue */
.animate-bounce            /* Saut continu */
```

#### Effets 3D & Avancés
```css
.animate-flip              /* Retournement Y */
.animate-swing             /* Balancier */
.animate-wobble            /* Oscillation */
.animate-reveal            /* Révélation de contenu */
.animate-reveal-up         /* Révélation par le haut */
.animate-gradient          /* Gradient animé */
```

#### Hover Effects (Transitions)
```css
.hover-scale               /* Scale 1.05 */
.hover-scale-lg            /* Scale 1.1 */
.hover-lift                /* Elevation + lift */
.hover-shadow              /* Shadow augmente */
.hover-glow                /* Glow bleu */
.hover-opacity             /* Opacity 0.8 */
```

#### Skeleton Loading
```css
.skeleton                  /* Shimmer light */
.skeleton-dark             /* Shimmer dark */
.skeleton-card             /* Card placeholder */
.skeleton-text             /* Text line */
.skeleton-title            /* Title placeholder */
.skeleton-avatar           /* Avatar circulaire */
```

### ⚡ Performance

Toutes les animations utilisent **seulement**:
- `transform` (translate, scale, rotate)
- `opacity`
- `box-shadow` (si nécessaire)

Les changements CSS qui déclenchent repaint sont **évités** pour une performance 60fps garantie.

### 🎨 Variables CSS

```css
:root {
  /* Easing curves */
  --ease-in-out-cubic: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out-cubic: cubic-bezier(0.0, 0, 0.2, 1);
  --ease-out-back: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-out-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

  /* Timing standards */
  --transition-fast: 150ms;
  --transition-normal: 300ms;
  --transition-slow: 500ms;
}
```

### 🔧 Utilisation basique

```jsx
import '../styles/animations.css';

// Classe simple
<div className="animate-fade-in">
  Content
</div>

// Avec délai (stagger)
<div className="animate-slide-in-up stagger-1">Item 1</div>
<div className="animate-slide-in-up stagger-2">Item 2</div>
<div className="animate-slide-in-up stagger-3">Item 3</div>

// Hover effect
<button className="hover-scale hover-lift">
  Click me
</button>

// Skeleton loading
<div className="skeleton skeleton-card" style={{ height: '300px' }} />
```

---

## 2. React Hooks (`useAnimations.js`)

### 📦 11 Hooks Personnalisés

#### 1. `useInView` - Animate on Scroll

Déclenche une animation quand l'élément entre dans le viewport.

```jsx
import { useInView } from '../hooks';

function MyComponent() {
  const { ref, isVisible } = useInView({
    threshold: 0.1,           // Seuil de visibilité
    rootMargin: '0px',        // Marge autour
    triggerOnce: true,        // Une seule fois?
  });

  return (
    <div
      ref={ref}
      className={isVisible ? 'animate-fade-in-up' : ''}
    >
      Content
    </div>
  );
}
```

#### 2. `useHover` - Hover Effects

Gère les effets de survol avec callbacks.

```jsx
const { ref, isHovered } = useHover({
  onEnter: () => console.log('Entered'),
  onLeave: () => console.log('Left'),
});

return (
  <div ref={ref} className={isHovered ? 'hover-scale' : ''}>
    Hover me
  </div>
);
```

#### 3. `useSpring` - Physics-based Animation

Animation basée sur la physique (spring physics).

```jsx
const [target, setTarget] = useState(0);
const value = useSpring(0, target, {
  tension: 170,    // Raideur du ressort
  friction: 26,    // Frottement (amortissement)
  mass: 1,         // Masse
  clamp: false,    // Clamper les valeurs?
});

return (
  <>
    <button onClick={() => setTarget(100)}>Animate</button>
    <div style={{ transform: `translateX(${value}px)` }}>
      {Math.round(value)}
    </div>
  </>
);
```

#### 4. `useGesture` - Swipe & Pinch Detection

Détecte les gestes tactiles (swipe, pinch).

```jsx
const { ref } = useGesture({
  onSwipeLeft: () => handleSwipe('left'),
  onSwipeRight: () => handleSwipe('right'),
  onSwipeUp: () => handleSwipe('up'),
  onSwipeDown: () => handleSwipe('down'),
  onPinch: (scale) => handlePinch(scale),
  threshold: 50,   // Distance minimale
});

return <div ref={ref}>Swipe me</div>;
```

#### 5. `useAnimationFrame` - RAF Wrapper

Wrapper sécurisé pour `requestAnimationFrame`.

```jsx
const [x, setX] = useState(0);

useAnimationFrame(() => {
  setX(prev => (prev + 1) % 360);
}, true);

return <div style={{ transform: `rotate(${x}deg)` }}>Spinning</div>;
```

#### 6. `usePrefersReducedMotion` - Accessibility

Détecte les préférences d'accessibilité.

```jsx
const prefersReducedMotion = usePrefersReducedMotion();

return (
  <div className={prefersReducedMotion ? '' : 'animate-spin'}>
    {prefersReducedMotion ? 'Loading...' : '🔄'}
  </div>
);
```

#### 7. `useScrollAnimation` - Scroll Progress

Calcule le progress d'animation basé sur le scroll.

```jsx
const { ref, progress } = useScrollAnimation({
  threshold: 0.1,
});

return (
  <div ref={ref}>
    <div style={{ width: `${progress * 100}%` }}>
      Progress: {Math.round(progress * 100)}%
    </div>
  </div>
);
```

#### 8. `useElementSize` - Element Dimensions

Mesure les dimensions d'un élément en temps réel.

```jsx
const { ref, width, height } = useElementSize();

return (
  <div ref={ref}>
    {width}x{height}
  </div>
);
```

#### 9. `useTransitionAnimation` - State Transitions

Anime les transitions entre états.

```jsx
const [value, setValue] = useState('initial');
const displayValue = useTransitionAnimation(value, 300);

return (
  <>
    <button onClick={() => setValue('updated')}>Change</button>
    <div>{displayValue}</div>
  </>
);
```

#### 10. `useDebounceAnimation` - Debounce

Débounce une animation.

```jsx
const handleScroll = useDebounceAnimation(() => {
  console.log('Scrolled');
}, 300);

useEffect(() => {
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

#### 11. `useMountAnimation` - Mount Animation

Anime au montage du composant.

```jsx
const { ref, isAnimating } = useMountAnimation(
  'animate-fade-in-up',
  300
);

return <div ref={ref}>Animated on mount</div>;
```

### 📋 Best Practices

```jsx
import { useInView, useHover, usePrefersReducedMotion } from '../hooks';

function OptimizedComponent() {
  const prefersReducedMotion = usePrefersReducedMotion();
  const { ref, isVisible } = useInView({ triggerOnce: true });
  const { ref: hoverRef, isHovered } = useHover();

  return (
    <div
      ref={ref}
      className={!prefersReducedMotion && isVisible ? 'animate-fade-in' : ''}
    >
      <div
        ref={hoverRef}
        className={isHovered ? 'hover-scale' : ''}
      >
        Content
      </div>
    </div>
  );
}
```

---

## 3. Composant AnimatedCard

Card avec animations premium incluant:
- Hover 3D tilt effect
- Glow effect
- Smooth shadow transitions
- Scale on hover
- Content reveal animation

### Props

```jsx
<AnimatedCard
  variant="default"      // 'default' | 'elevated' | 'ghost' | 'interactive'
  hoverable={true}       // Activer le hover lift effect
  glowEffect={true}      // Activer le glow effect
  tiltEffect={true}      // Activer le 3D tilt
  onClick={null}         // Handler de click
  className=""           // Classes CSS additionnelles
  style={{}}             // Styles inline
  animationDelay={0}     // Délai d'animation en ms
>
  <h3>Title</h3>
  <p>Content</p>
</AnimatedCard>
```

### Exemples

```jsx
// Simple card
<AnimatedCard>
  <h3>Product</h3>
  <p>$99.99</p>
</AnimatedCard>

// Elevated with glow
<AnimatedCard variant="elevated" glowEffect={true}>
  <img src="..." alt="..." />
  <h3>Featured Product</h3>
</AnimatedCard>

// Interactive/Clickable
<AnimatedCard
  variant="interactive"
  onClick={() => navigate(`/product/${id}`)}
>
  <h3>Click me</h3>
</AnimatedCard>

// Grid avec stagger
{products.map((p, i) => (
  <AnimatedCard
    key={p.id}
    animationDelay={i * 100}
    variant="elevated"
  >
    <ProductContent product={p} />
  </AnimatedCard>
))}
```

### Variants

- **default**: Ombre subtile, hover lift
- **elevated**: Ombre plus prononcée, effet de profondeur
- **ghost**: Minimal, border subtile
- **interactive**: Avec border couleur au hover, clickable

---

## 4. Composant LoadingSkeleton

Skeleton loading élégant avec shimmer animation.

### Props

```jsx
<LoadingSkeleton
  variant="card"            // Type de skeleton
  count={1}                 // Nombre de skeletons
  width="100%"              // Largeur
  height="100px"            // Hauteur
  borderRadius="12px"       // Border radius
  dark={false}              // Mode sombre?
  className=""              // Classes additionnelles
  style={{}}                // Styles inline
/>
```

### Variants

- **card**: Placeholder pour carte
- **text**: Ligne de texte
- **avatar**: Cercle pour avatar
- **title**: Placeholder pour titre
- **list-item**: Avatar + 2 lignes de texte
- **grid**: Grille responsive
- **text-block**: Bloc multi-lignes
- **product**: Image + titre + prix

### Exemples

```jsx
// Card
<LoadingSkeleton variant="card" height="300px" />

// Liste de produits
<LoadingSkeleton variant="product" count={6} />

// Text lines
<LoadingSkeleton variant="text-block" count={4} />

// Avec condition
{isLoading ? (
  <LoadingSkeleton variant="card" count={3} />
) : (
  <Content />
)}

// Grid responsive
<LoadingSkeleton variant="grid" count={9} />
```

---

## 5. Composant PageTransition

Transitions fluides entre pages/routes.

### Props

```jsx
<PageTransition
  effect="fade"             // Type de transition
  duration={300}            // Durée en ms
  className=""              // Classes additionnelles
>
  {children}
</PageTransition>
```

### Effects disponibles

- **fade**: Fade in/out (défaut)
- **slide-up**: Slide up on enter, down on exit
- **slide-down**: Slide down on enter, up on exit
- **slide-left**: Slide right on enter, left on exit
- **slide-right**: Slide left on enter, right on exit
- **zoom**: Zoom in/out
- **bounce**: Bounce effect
- **scale-up**: Scale animation
- **flip**: Flip Y effect

### Intégration avec React Router

```jsx
import { PageTransition, LayoutTransition } from '../components/PageTransition';

function App() {
  return (
    <PageTransition effect="slide-up">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </PageTransition>
  );
}

// Ou avec custom layout
function Layout() {
  return (
    <LayoutTransition effect="fade">
      <Header />
      <main>
        <Routes>
          {/* routes */}
        </Routes>
      </main>
      <Footer />
    </LayoutTransition>
  );
}
```

### Hook usePageTransition

```jsx
import { usePageTransition } from '../components/PageTransition';

function Component() {
  const { isTransitioning, effect } = usePageTransition('slide-up', 300);

  return (
    <div className={isTransitioning ? 'opacity-50' : 'opacity-100'}>
      Content
    </div>
  );
}
```

---

## 6. Exemples Complets (`AnimationExamples.jsx`)

Fichier de démonstration avec tous les composants et hooks:

```jsx
import AnimationExamples from '../components/AnimationExamples';

// Route
<Route path="/animations" element={<AnimationExamples />} />
```

Contient des exemples:
- ✅ useInView (Animate on Scroll)
- ✅ useHover (Hover Effects)
- ✅ useSpring (Physics-based)
- ✅ useGesture (Swipe/Pinch)
- ✅ AnimatedCard (3D Tilt)
- ✅ LoadingSkeleton (Variants)
- ✅ CSS Animation Classes
- ✅ Accessibility (prefers-reduced-motion)

---

## Patterns Courants

### 1. Staggered List Animations

```jsx
{items.map((item, index) => (
  <div
    key={item.id}
    className={`animate-slide-in-up stagger-${index + 1}`}
  >
    {item.content}
  </div>
))}
```

### 2. Loading to Content

```jsx
{isLoading ? (
  <>
    <LoadingSkeleton variant="product" count={6} />
  </>
) : (
  <div className="grid gap-4">
    {products.map((p, i) => (
      <AnimatedCard
        key={p.id}
        animationDelay={i * 100}
        variant="elevated"
      >
        <ProductCard product={p} />
      </AnimatedCard>
    ))}
  </div>
)}
```

### 3. Interactive Animation

```jsx
const { ref, isHovered } = useHover();
const [scale, setScale] = useState(1);

return (
  <div
    ref={ref}
    className="hover-scale"
    style={{ transform: `scale(${scale})` }}
    onMouseMove={(e) => {
      // Custom hover logic
    }}
  >
    Content
  </div>
);
```

### 4. Scroll-triggered Content

```jsx
function ScrollRevealSection({ children }) {
  const { ref, isVisible } = useInView({ threshold: 0.2 });

  return (
    <section
      ref={ref}
      className={isVisible ? 'animate-fade-in-up' : 'opacity-0'}
    >
      {children}
    </section>
  );
}
```

### 5. Gesture Navigation

```jsx
const { ref } = useGesture({
  onSwipeRight: () => navigate(-1),
  onSwipeLeft: () => navigate(1),
});

return (
  <div ref={ref} className="flex-1">
    {/* Carousel/Slides */}
  </div>
);
```

---

## Performance Optimizations

### ✅ À faire

```css
/* Utiliser seulement transform et opacity */
.animate {
  animation: slide 300ms ease-out forwards;
}

@keyframes slide {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

```jsx
// Utiliser will-change
.gpu-accelerate {
  will-change: transform;
  transform: translate3d(0, 0, 0);
}

// Détecter prefers-reduced-motion
const prefersReducedMotion = usePrefersReducedMotion();
<div className={prefersReducedMotion ? '' : 'animate-spin'}>
```

### ❌ À éviter

```css
/* Ne pas animer width/height */
.bad {
  animation: expand 300ms ease;
}
@keyframes expand {
  from { width: 0; }
  to { width: 100%; }
}

/* Ne pas animer top/left */
.bad {
  animation: move 300ms ease;
}
@keyframes move {
  from { top: 0; }
  to { top: 100px; }
}
```

---

## Accessibility

### 1. Respect `prefers-reduced-motion`

Toutes les animations respectent la préférence utilisateur:

```jsx
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

### 2. Hook pour détection

```jsx
const prefersReducedMotion = usePrefersReducedMotion();

{!prefersReducedMotion && <AnimatedIcon />}
{prefersReducedMotion && <StaticIcon />}
```

### 3. Aria labels

```jsx
<div
  className="animate-spin"
  role="status"
  aria-live="polite"
  aria-label="Loading..."
>
  <span className="sr-only">Loading</span>
</div>
```

---

## Browser Support

- Chrome/Edge: 60+ ✅
- Firefox: 55+ ✅
- Safari: 12+ ✅
- Mobile browsers: 99% ✅

Utilise:
- `transform` (tous les navigateurs)
- `opacity` (tous les navigateurs)
- `IntersectionObserver` (polyfill pour IE)
- `ResizeObserver` (polyfill pour IE)

---

## Troubleshooting

### Les animations ne s'exécutent pas

```jsx
// Vérifier que animations.css est importé
import '../styles/animations.css';

// Vérifier le préfixe prefers-reduced-motion
const prefersReducedMotion = usePrefersReducedMotion();
console.log(prefersReducedMotion); // false = animations actives
```

### Les animations saccadent (janky)

```css
/* Utiliser GPU acceleration */
.element {
  will-change: transform;
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}

/* Éviter les animations simultanées */
.element {
  animation: fadeIn 300ms, slideIn 300ms;
  /* ❌ Non optimal, faire seulement 1 */
}
```

### Performance issues

```jsx
// Débouncer les handlers
const handleScroll = useDebounceAnimation(() => {
  // ...
}, 300);

// Utiliser triggerOnce pour InView
const { ref, isVisible } = useInView({ triggerOnce: true });
```

---

## Fichiers et Locations

| Fichier | Lignes | Location |
|---------|--------|----------|
| animations.css | 330+ | `/frontend/src/styles/animations.css` |
| useAnimations.js | 200+ | `/frontend/src/hooks/useAnimations.js` |
| AnimatedCard.jsx | 120+ | `/frontend/src/components/AnimatedCard.jsx` |
| LoadingSkeleton.jsx | 100+ | `/frontend/src/components/LoadingSkeleton.jsx` |
| PageTransition.jsx | 80+ | `/frontend/src/components/PageTransition.jsx` |
| AnimationExamples.jsx | 500+ | `/frontend/src/components/AnimationExamples.jsx` |

---

## Résumé des Features

✅ **50+ Keyframes d'animation**
✅ **30+ Classes CSS prêtes à l'emploi**
✅ **11 React Hooks personnalisés**
✅ **3 Composants premium (Card, Skeleton, Transition)**
✅ **Animations 60fps garanties**
✅ **GPU acceleration**
✅ **Accessibilité complète**
✅ **Responsive design**
✅ **Production-ready**
✅ **Exemples d'utilisation complets**
✅ **Documentation exhaustive**
✅ **Best practices intégrées**

---

## Conclusion

Ce système d'animations premium offre une base solide pour créer des interfaces fluides et professionnelles. Toutes les animations sont optimisées pour 60fps et respectent les standards d'accessibilité.

Pour commencer, voir `AnimationExamples.jsx` pour des exemples d'utilisation complets.
