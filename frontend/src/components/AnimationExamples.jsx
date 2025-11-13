import React, { useState } from 'react';
import AnimatedCard from './AnimatedCard';
import LoadingSkeleton from './LoadingSkeleton';
import PageTransition from './PageTransition';
import {
  useInView,
  useHover,
  useSpring,
  useGesture,
  usePrefersReducedMotion,
} from '../hooks/useAnimations';
import '../styles/animations.css';

/**
 * ===================================================================
 * EXAMPLES SHOWCASE - SYSTÈME D'ANIMATIONS PREMIUM
 * Démontre tous les composants et hooks d'animation
 * ===================================================================
 */

/**
 * Exemple 1: InView Animation (Animate on Scroll)
 */
const InViewExample = () => {
  const { ref, isVisible } = useInView({ threshold: 0.5 });

  return (
    <section className="example-section">
      <h2>Animate on Scroll (useInView)</h2>
      <div
        ref={ref}
        className={isVisible ? 'animate-fade-in-up' : ''}
        style={{
          padding: '40px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: '12px',
          textAlign: 'center',
        }}
      >
        <h3>This animates when scrolled into view</h3>
        <p>Visible: {isVisible ? 'Yes' : 'No'}</p>
      </div>
    </section>
  );
};

/**
 * Exemple 2: Hover Effects avec Hook
 */
const HoverExample = () => {
  const { ref, isHovered } = useHover({
    onEnter: () =>,
    onLeave: () =>,
  });

  return (
    <section className="example-section">
      <h2>Hover Effects (useHover)</h2>
      <div
        ref={ref}
        className="hover-scale hover-lift hover-shadow"
        style={{
          padding: '30px',
          background: '#3b82f6',
          color: 'white',
          borderRadius: '12px',
          cursor: 'pointer',
          transition: 'all 0.3s ease-out',
        }}
      >
        <h3>Hover over me</h3>
        <p>Status: {isHovered ? 'Hovered' : 'Normal'}</p>
      </div>
    </section>
  );
};

/**
 * Exemple 3: Spring Animation Physics
 */
const SpringExample = () => {
  const [target, setTarget] = useState(0);
  const value = useSpring(0, target, {
    tension: 170,
    friction: 26,
  });

  return (
    <section className="example-section">
      <h2>Spring Physics (useSpring)</h2>
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setTarget(100)}
          className="hover-scale"
          style={{
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          Animate to 100
        </button>
        <button
          onClick={() => setTarget(-100)}
          style={{
            padding: '12px 24px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
          }}
        >
          Animate to -100
        </button>
      </div>
      <div
        style={{
          marginTop: '20px',
          padding: '20px',
          background: '#f3f4f6',
          borderRadius: '8px',
          textAlign: 'center',
        }}
      >
        <p>Current Value: {Math.round(value)}</p>
        <div
          style={{
            width: '50px',
            height: '50px',
            background: '#3b82f6',
            borderRadius: '8px',
            margin: '20px auto',
            transform: `translateX(${value}px)`,
            transition: 'transform 0.016s linear',
          }}
        />
      </div>
    </section>
  );
};

/**
 * Exemple 4: Gesture Detection
 */
const GestureExample = () => {
  const [gesture, setGesture] = useState('');
  const { ref } = useGesture({
    onSwipeLeft: () => setGesture('Swiped Left'),
    onSwipeRight: () => setGesture('Swiped Right'),
    onSwipeUp: () => setGesture('Swiped Up'),
    onSwipeDown: () => setGesture('Swiped Down'),
  });

  return (
    <section className="example-section">
      <h2>Gesture Detection (useGesture)</h2>
      <div
        ref={ref}
        style={{
          padding: '40px',
          background: '#10b981',
          color: 'white',
          borderRadius: '12px',
          textAlign: 'center',
          minHeight: '200px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          touchAction: 'none',
        }}
      >
        <h3>Swipe gestures (mobile friendly)</h3>
        <p style={{ fontSize: '24px', marginTop: '20px' }}>{gesture}</p>
      </div>
    </section>
  );
};

/**
 * Exemple 5: Animated Cards
 */
const CardExamples = () => {
  const cards = [
    { id: 1, title: 'Card 1', desc: 'Default variant' },
    { id: 2, title: 'Card 2', desc: 'Elevated variant' },
    { id: 3, title: 'Card 3', desc: 'Interactive variant' },
  ];

  return (
    <section className="example-section">
      <h2>Animated Cards (AnimatedCard)</h2>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
        }}
      >
        <AnimatedCard variant="default" glowEffect={false}>
          <h3>Default Card</h3>
          <p>Hover for smooth elevation</p>
        </AnimatedCard>

        <AnimatedCard variant="elevated" glowEffect={true}>
          <h3>Elevated Card</h3>
          <p>With glow effect on hover</p>
        </AnimatedCard>

        <AnimatedCard
          variant="interactive"
          onClick={() => alert('Card clicked!')}
        >
          <h3>Interactive Card</h3>
          <p>Click me for action</p>
        </AnimatedCard>
      </div>
    </section>
  );
};

/**
 * Exemple 6: Loading Skeletons
 */
const SkeletonExamples = () => {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <section className="example-section">
      <h2>Loading Skeletons (LoadingSkeleton)</h2>
      <button
        onClick={() => setIsLoading(!isLoading)}
        style={{
          padding: '12px 24px',
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        Toggle Loading
      </button>

      {isLoading ? (
        <div style={{ display: 'grid', gap: '16px' }}>
          <LoadingSkeleton variant="product" count={3} />
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px',
          }}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="animate-fade-in"
              style={{
                padding: '20px',
                background: '#f3f4f6',
                borderRadius: '12px',
                textAlign: 'center',
              }}
            >
              <h4>Product {i}</h4>
              <p>$99.99</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

/**
 * Exemple 7: CSS Animation Classes
 */
const AnimationClassesExample = () => {
  const animations = [
    { class: 'animate-fade-in', label: 'Fade In' },
    { class: 'animate-slide-in-up', label: 'Slide Up' },
    { class: 'animate-bounce-in', label: 'Bounce In' },
    { class: 'animate-scale-up', label: 'Scale Up' },
    { class: 'animate-spin', label: 'Spin' },
    { class: 'animate-pulse', label: 'Pulse' },
  ];

  return (
    <section className="example-section">
      <h2>CSS Animation Classes</h2>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
        }}
      >
        {animations.map(({ class: animClass, label }) => (
          <div
            key={animClass}
            className={animClass}
            style={{
              padding: '20px',
              background: '#3b82f6',
              color: 'white',
              borderRadius: '8px',
              textAlign: 'center',
            }}
          >
            {label}
          </div>
        ))}
      </div>
    </section>
  );
};

/**
 * Exemple 8: Préférences de réduction de mouvement
 */
const ReducedMotionExample = () => {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <section className="example-section">
      <h2>Accessibility: Reduced Motion (usePrefersReducedMotion)</h2>
      <div
        style={{
          padding: '20px',
          background: prefersReducedMotion ? '#fecaca' : '#d1fae5',
          borderRadius: '8px',
        }}
      >
        <p>
          <strong>Reduced Motion Preference:</strong>{' '}
          {prefersReducedMotion ? 'ON' : 'OFF'}
        </p>
        <p>
          {prefersReducedMotion
            ? 'Animations are disabled for accessibility'
            : 'Animations are enabled'}
        </p>
      </div>
    </section>
  );
};

/**
 * Composant Principal - Showcase
 */
const AnimationExamples = () => {
  return (
    <PageTransition effect="fade">
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '40px 20px',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}
      >
        <h1 className="animate-fade-in">
          Animation & Micro-interactions Premium System
        </h1>
        <p className="animate-fade-in-up" style={{ fontSize: '18px' }}>
          Comprehensive examples of 60fps animations, interactive effects, and
          micro-interactions
        </p>

        <style>{`
          .example-section {
            margin: 60px 0;
            padding: 40px;
            background: #f9fafb;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
          }

          .example-section h2 {
            margin-top: 0;
            color: #111827;
            font-size: 24px;
            font-weight: 600;
          }

          .example-section p {
            color: #6b7280;
            font-size: 16px;
          }

          button {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          }

          button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
          }

          button:active {
            transform: translateY(0);
          }

          @media (prefers-color-scheme: dark) {
            .example-section {
              background: #1f2937;
              border-color: #374151;
            }

            .example-section h2 {
              color: #f3f4f6;
            }

            .example-section p {
              color: #9ca3af;
            }
          }
        `}</style>

        <InViewExample />
        <HoverExample />
        <SpringExample />
        <GestureExample />
        <CardExamples />
        <SkeletonExamples />
        <AnimationClassesExample />
        <ReducedMotionExample />

        <section className="example-section" style={{ marginBottom: '60px' }}>
          <h2>Quick Start Guide</h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '20px',
            }}
          >
            <div>
              <h3>CSS Classes</h3>
              <pre style={{ background: '#fff', padding: '12px', overflow: 'auto' }}>
{`// Entrées
.animate-fade-in
.animate-slide-in-up
.animate-scale-up
.animate-bounce-in

// Animations continues
.animate-spin
.animate-pulse
.animate-glow

// Hover Effects
.hover-scale
.hover-lift
.hover-shadow`}
              </pre>
            </div>
            <div>
              <h3>React Hooks</h3>
              <pre style={{ background: '#fff', padding: '12px', overflow: 'auto' }}>
{`import { useInView, useHover } from '@/hooks';

const { ref, isVisible } = useInView();
const { ref, isHovered } = useHover();
const value = useSpring(0, 100);
const { ref } = useGesture({...})`}
              </pre>
            </div>
            <div>
              <h3>Composants</h3>
              <pre style={{ background: '#fff', padding: '12px', overflow: 'auto' }}>
{`<AnimatedCard variant="elevated">
  Content
</AnimatedCard>

<LoadingSkeleton variant="card" />

<PageTransition effect="fade">
  Page content
</PageTransition>`}
              </pre>
            </div>
          </div>
        </section>
      </div>
    </PageTransition>
  );
};

export default AnimationExamples;
