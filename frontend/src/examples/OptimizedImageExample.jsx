/**
 * Exemples d'utilisation du composant OptimizedImage
 * Démontre tous les cas d'usage et configurations
 */
import React from 'react';
import OptimizedImage from '../components/OptimizedImage';

const OptimizedImageExample = () => {
  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Exemples d'Optimisation d'Images</h1>

      {/* Exemple 1: Image simple avec lazy loading */}
      <section style={{ marginBottom: '60px' }}>
        <h2>1. Image Simple avec Lazy Loading</h2>
        <p>Image basique avec chargement différé et skeleton</p>
        <OptimizedImage
          src="https://example.com/images/product.jpg"
          alt="Produit exemple"
          width="400px"
          height="300px"
          loading="lazy"
          showSkeleton={true}
        />
      </section>

      {/* Exemple 2: Image responsive avec srcset */}
      <section style={{ marginBottom: '60px' }}>
        <h2>2. Image Responsive avec Srcset</h2>
        <p>Multiple formats et tailles pour performances optimales</p>
        <OptimizedImage
          src="https://cdn.example.com/images/hero_large.jpg"
          alt="Image hero responsive"
          srcSetWebP="https://cdn.example.com/images/hero_small.webp 320w,
                     https://cdn.example.com/images/hero_medium.webp 640w,
                     https://cdn.example.com/images/hero_large.webp 1024w,
                     https://cdn.example.com/images/hero_xl.webp 1920w"
          srcSetJpeg="https://cdn.example.com/images/hero_small.jpg 320w,
                     https://cdn.example.com/images/hero_medium.jpg 640w,
                     https://cdn.example.com/images/hero_large.jpg 1024w,
                     https://cdn.example.com/images/hero_xl.jpg 1920w"
          sizes="(max-width: 640px) 100vw,
                 (max-width: 1024px) 50vw,
                 33vw"
          width="100%"
          height="auto"
          objectFit="cover"
        />
      </section>

      {/* Exemple 3: Image avec AVIF + WebP + JPEG fallback */}
      <section style={{ marginBottom: '60px' }}>
        <h2>3. Multi-Format (AVIF + WebP + JPEG)</h2>
        <p>Utilise le meilleur format supporté par le navigateur</p>
        <OptimizedImage
          src="https://cdn.example.com/images/product_large.jpg"
          alt="Produit haute qualité"
          srcSetAvif="https://cdn.example.com/images/product_small.avif 320w,
                     https://cdn.example.com/images/product_medium.avif 640w,
                     https://cdn.example.com/images/product_large.avif 1024w"
          srcSetWebP="https://cdn.example.com/images/product_small.webp 320w,
                     https://cdn.example.com/images/product_medium.webp 640w,
                     https://cdn.example.com/images/product_large.webp 1024w"
          srcSetJpeg="https://cdn.example.com/images/product_small.jpg 320w,
                     https://cdn.example.com/images/product_medium.jpg 640w,
                     https://cdn.example.com/images/product_large.jpg 1024w"
          sizes="(max-width: 768px) 100vw, 50vw"
          width="600px"
          height="450px"
          blurhash="#4287f5"
        />
      </section>

      {/* Exemple 4: Image prioritaire (above the fold) */}
      <section style={{ marginBottom: '60px' }}>
        <h2>4. Image Prioritaire (Above the Fold)</h2>
        <p>Chargement immédiat sans lazy loading pour les images critiques</p>
        <OptimizedImage
          src="https://cdn.example.com/images/hero.jpg"
          alt="Hero principal"
          priority={true}
          loading="eager"
          width="100%"
          height="500px"
          objectFit="cover"
          objectPosition="center"
          showSkeleton={false}
        />
      </section>

      {/* Exemple 5: Image avec blur placeholder */}
      <section style={{ marginBottom: '60px' }}>
        <h2>5. Blur Placeholder</h2>
        <p>Placeholder coloré avec effet blur pendant le chargement</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
          <OptimizedImage
            src="https://cdn.example.com/images/product1.jpg"
            alt="Produit 1"
            blurhash="#ff6b6b"
            blurAmount={25}
            width="100%"
            height="250px"
          />
          <OptimizedImage
            src="https://cdn.example.com/images/product2.jpg"
            alt="Produit 2"
            blurhash="#4ecdc4"
            blurAmount={25}
            width="100%"
            height="250px"
          />
          <OptimizedImage
            src="https://cdn.example.com/images/product3.jpg"
            alt="Produit 3"
            blurhash="#45b7d1"
            blurAmount={25}
            width="100%"
            height="250px"
          />
        </div>
      </section>

      {/* Exemple 6: Grille d'images avec lazy loading */}
      <section style={{ marginBottom: '60px' }}>
        <h2>6. Grille d'Images avec Lazy Loading</h2>
        <p>Optimisation des performances avec intersection observer</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
          {Array.from({ length: 12 }, (_, i) => (
            <OptimizedImage
              key={i}
              src={`https://cdn.example.com/images/gallery_${i + 1}.jpg`}
              alt={`Image galerie ${i + 1}`}
              width="100%"
              height="200px"
              objectFit="cover"
              loading="lazy"
              threshold={0.1}
              rootMargin="100px"
              blurhash="#cccccc"
            />
          ))}
        </div>
      </section>

      {/* Exemple 7: Image avec fallback en cas d'erreur */}
      <section style={{ marginBottom: '60px' }}>
        <h2>7. Gestion d'Erreur avec Fallback</h2>
        <p>Affiche une image de remplacement si l'image principale échoue</p>
        <OptimizedImage
          src="https://cdn.example.com/images/nonexistent.jpg"
          fallbackSrc="https://cdn.example.com/images/placeholder.jpg"
          alt="Image avec fallback"
          width="400px"
          height="300px"
          onError={(e) => console.error('Erreur chargement image:', e)}
        />
      </section>

      {/* Exemple 8: Images avec différents object-fit */}
      <section style={{ marginBottom: '60px' }}>
        <h2>8. Différents Modes Object-Fit</h2>
        <p>Cover, contain, fill, etc.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
          <div>
            <h3>Cover</h3>
            <OptimizedImage
              src="https://cdn.example.com/images/landscape.jpg"
              alt="Object-fit cover"
              width="100%"
              height="200px"
              objectFit="cover"
            />
          </div>
          <div>
            <h3>Contain</h3>
            <OptimizedImage
              src="https://cdn.example.com/images/landscape.jpg"
              alt="Object-fit contain"
              width="100%"
              height="200px"
              objectFit="contain"
            />
          </div>
          <div>
            <h3>Fill</h3>
            <OptimizedImage
              src="https://cdn.example.com/images/landscape.jpg"
              alt="Object-fit fill"
              width="100%"
              height="200px"
              objectFit="fill"
            />
          </div>
        </div>
      </section>

      {/* Exemple 9: Avatar avec circle crop */}
      <section style={{ marginBottom: '60px' }}>
        <h2>9. Avatars Circulaires</h2>
        <p>Images de profil optimisées</p>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          {['small', 'medium', 'large'].map((size) => {
            const sizes = { small: '50px', medium: '100px', large: '150px' };
            return (
              <OptimizedImage
                key={size}
                src={`https://cdn.example.com/avatars/user_${size}.jpg`}
                alt={`Avatar ${size}`}
                width={sizes[size]}
                height={sizes[size]}
                objectFit="cover"
                className="avatar-circle"
                style={{ borderRadius: '50%' }}
              />
            );
          })}
        </div>
      </section>

      {/* Exemple 10: E-commerce product cards */}
      <section style={{ marginBottom: '60px' }}>
        <h2>10. Cartes Produits E-commerce</h2>
        <p>Configuration optimale pour marketplace</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '30px' }}>
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              style={{
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                overflow: 'hidden',
                backgroundColor: '#fff',
              }}
            >
              <OptimizedImage
                src={`https://cdn.example.com/products/product_${i}.jpg`}
                alt={`Produit ${i}`}
                srcSetWebP={`https://cdn.example.com/products/product_${i}_small.webp 320w,
                           https://cdn.example.com/products/product_${i}_medium.webp 640w`}
                srcSetJpeg={`https://cdn.example.com/products/product_${i}_small.jpg 320w,
                           https://cdn.example.com/products/product_${i}_medium.jpg 640w`}
                sizes="(max-width: 768px) 100vw, 33vw"
                width="100%"
                height="300px"
                objectFit="cover"
                blurhash="#f5f5f5"
                loading="lazy"
              />
              <div style={{ padding: '15px' }}>
                <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>
                  Produit Exemple {i}
                </h3>
                <p style={{ margin: '0', color: '#666', fontSize: '14px' }}>
                  Description du produit avec optimisation d'image
                </p>
                <p style={{ margin: '10px 0 0 0', fontSize: '18px', fontWeight: 'bold' }}>
                  {(29.99 + i * 10).toFixed(2)} €
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Exemple 11: Callbacks et événements */}
      <section style={{ marginBottom: '60px' }}>
        <h2>11. Callbacks et Événements</h2>
        <p>Gestion des événements de chargement</p>
        <OptimizedImage
          src="https://cdn.example.com/images/callback-demo.jpg"
          alt="Démonstration callbacks"
          width="500px"
          height="350px"
          onLoad={(e) => {

            // Tracking analytics
            // gtag('event', 'image_loaded', { image_name: 'callback-demo' });
          }}
          onError={(e) => {
            console.error('Erreur chargement:', e);
            // Error tracking
            // Sentry.captureMessage('Image failed to load');
          }}
        />
      </section>

      {/* Exemple 12: Performance monitoring */}
      <section style={{ marginBottom: '60px' }}>
        <h2>12. Configuration Performance Optimale</h2>
        <p>Settings recommandés pour performances maximales</p>
        <OptimizedImage
          src="https://cdn.example.com/images/performance.jpg"
          alt="Image optimisée performance"
          srcSetWebP="https://cdn.example.com/images/performance_320.webp 320w,
                     https://cdn.example.com/images/performance_640.webp 640w,
                     https://cdn.example.com/images/performance_1024.webp 1024w,
                     https://cdn.example.com/images/performance_1920.webp 1920w"
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          width="100%"
          height="auto"
          loading="lazy"
          threshold={0.01}
          rootMargin="50px"
          showSkeleton={true}
          blurhash="#e8e8e8"
          blurAmount={20}
          quality={85}
        />
      </section>

      <style>{`
        .avatar-circle {
          border-radius: 50%;
          object-fit: cover;
        }

        section {
          background: #f9f9f9;
          padding: 20px;
          border-radius: 8px;
        }

        h2 {
          color: #333;
          margin-top: 0;
        }

        p {
          color: #666;
          margin-bottom: 20px;
        }
      `}</style>
    </div>
  );
};

export default OptimizedImageExample;
