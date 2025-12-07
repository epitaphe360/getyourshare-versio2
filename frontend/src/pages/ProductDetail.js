import React, { useMemo, memo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, ChevronLeft, AlertCircle } from 'lucide-react';
import SEOHead from '../components/SEO/SEOHead';
import SEO_CONFIG from '../config/seo';
import './MarketplaceAnimations.css';

// Custom hook
import { useProductDetail } from '../hooks/useProductDetail';

// Components
import ProductDetailHeader from '../components/ProductDetail/ProductDetailHeader';
import ProductDetailInfo from '../components/ProductDetail/ProductDetailInfo';
import ProductDetailActions from '../components/ProductDetail/ProductDetailActions';
import ProductDetailReviews from '../components/ProductDetail/ProductDetailReviews';
import ProductDetailAffiliateModal from '../components/ProductDetail/ProductDetailAffiliateModal';

/**
 * Product Detail Page - Refactored with useReducer + React.memo
 * Orchestrator component (~250 lines instead of 1135)
 *
 * Key improvements:
 * - Replaced 18 useState with single useReducer in custom hook
 * - Parallel API calls with Promise.all() in useProductDetail
 * - 6 memoized child components for performance
 * - Extracted all business logic into custom hook
 * - Clean separation of concerns
 * - Stable refs to prevent infinite re-renders
 */
const ProductDetail = memo(() => {
  const navigate = useNavigate();
  const location = useLocation();
  const isDashboard = location.pathname.startsWith('/dashboard');
  const backPath = isDashboard ? '/dashboard/marketplace' : '/marketplace';

  const { user } = useAuth();
  const { state, actions } = useProductDetail();

  // Memoized data parsers
  const images = useMemo(() => {
    const mainImage = state.product?.image_url ||
                     (state.product?.type === 'service'
                       ? `https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop&q=80`
                       : `https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop&q=80`);

    if (state.product?.images) {
      if (Array.isArray(state.product.images)) {
        return [mainImage, ...state.product.images];
      }
      if (typeof state.product.images === 'string') {
        try {
          const parsed = JSON.parse(state.product.images);
          if (Array.isArray(parsed)) {
            return [mainImage, ...parsed];
          }
        } catch {
          // Ignore parsing error
        }
      }
    }
    return [mainImage];
  }, [state.product]);

  const highlights = useMemo(() => {
    if (!state.product?.highlights) return [];
    if (Array.isArray(state.product.highlights)) return state.product.highlights;
    if (typeof state.product.highlights === 'string') {
      try {
        return JSON.parse(state.product.highlights);
      } catch {
        return [];
      }
    }
    return [];
  }, [state.product]);

  const faq = useMemo(() => {
    if (!state.product?.faq) return [];
    if (Array.isArray(state.product.faq)) return state.product.faq;
    if (typeof state.product.faq === 'string') {
      try {
        return JSON.parse(state.product.faq);
      } catch {
        return [];
      }
    }
    return [];
  }, [state.product]);

  const hasDiscount = useMemo(() => {
    return state.product?.discount_percentage && state.product.discount_percentage > 0;
  }, [state.product]);

  // Loading state
  if (state.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-cyan-600 mx-auto"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <Sparkles className="text-cyan-600 animate-pulse" size={32} />
            </div>
          </div>
          <p className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent animate-pulse">
            Chargement du produit...
          </p>
        </div>
      </div>
    );
  }

  // Product not found
  if (!state.product) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex flex-col items-center justify-center p-8">
        <div className="bg-white rounded-2xl shadow-2xl p-12 text-center max-w-lg hover-lift">
          <div className="mb-6">
            <AlertCircle className="w-24 h-24 text-gray-300 mx-auto mb-4 animate-pulse" />
          </div>
          <h2 className="text-3xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-4">
            Produit non trouvé
          </h2>
          <p className="text-gray-600 mb-8 text-lg">
            Ce produit n'existe pas ou a été supprimé
          </p>
          <button
            onClick={() => navigate(backPath)}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 text-white rounded-xl font-bold hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center gap-2 mx-auto"
          >
            <ChevronLeft size={20} />
            Retour au Marketplace
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* SEO */}
      <SEOHead
        title={state.product.name}
        description={state.product.description}
        keywords={`${state.product.name}, marketplace, ${state.product.category || 'produit'}, Maroc`}
        image={state.product.image_url}
        type="product"
      />

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Back Button */}
          <button
            onClick={() => navigate(backPath)}
            className="group flex items-center gap-2 px-6 py-3 bg-white/80 backdrop-blur-sm rounded-xl font-bold text-gray-700 hover:text-cyan-600 transition-all duration-300 shadow-md hover:shadow-xl transform hover:scale-105 mb-8"
          >
            <ChevronLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
            Retour au Marketplace
          </button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
            {/* Left Column - Header & Info */}
            <div className="lg:col-span-2 space-y-6">
              {/* Header Component - Images, Title, Rating */}
              <ProductDetailHeader
                product={state.product}
                images={images}
                currentImageIndex={state.currentImageIndex}
                onImageChange={actions.setImageIndex}
                hasDiscount={hasDiscount}
              />

              {/* Info Component - Highlights, FAQ, Conditions */}
              <ProductDetailInfo
                product={state.product}
                highlights={highlights}
                faq={faq}
              />

              {/* Reviews Component */}
              <ProductDetailReviews
                reviews={state.reviews}
                user={user}
                showReviewForm={state.showReviewForm}
                reviewData={state.reviewData}
                onToggleReviewForm={actions.toggleReviewForm}
                onUpdateReviewData={actions.updateReviewData}
                onSubmitReview={actions.handleSubmitReview}
              />
            </div>

            {/* Right Column - Actions Component */}
            <div className="lg:sticky lg:top-8 lg:self-start">
              <ProductDetailActions
                product={state.product}
                user={user}
                onRequestAffiliation={actions.handleRequestAffiliation}
                hasDiscount={hasDiscount}
              />
            </div>
          </div>

          {/* Affiliate Modal Component */}
          <ProductDetailAffiliateModal
            show={state.showAffiliateModal}
            user={user}
            product={state.product}
            userProfile={state.userProfile}
            validationStatus={state.validationStatus}
            isValidating={state.isValidating}
            affiliateData={state.affiliateData}
            onClose={() => actions.toggleAffiliateModal(false)}
            onUpdateAffiliateData={actions.updateAffiliateData}
            onSubmit={actions.handleSubmitAffiliateRequest}
            onValidateStats={actions.validateStatsWithAI}
          />
        </div>
      </div>
    </>
  );
});

ProductDetail.displayName = 'ProductDetail';

export default ProductDetail;
