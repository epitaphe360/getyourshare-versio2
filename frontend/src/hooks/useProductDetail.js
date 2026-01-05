import { useReducer, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../utils/api';
import { getErrorMessage } from '../utils/errorHandler';

// Initial state
const initialState = {
  product: null,
  reviews: [],
  userProfile: null,
  validationStatus: null,
  loading: true,
  isValidating: false,
  currentImageIndex: 0,
  showReviewForm: false,
  showAffiliateModal: false,
  reviewData: {
    rating: 5,
    title: '',
    comment: ''
  },
  affiliateData: {
    selectedProduct: '',
    message: ''
  }
};

// Action types
const ACTIONS = {
  SET_PRODUCT: 'SET_PRODUCT',
  SET_REVIEWS: 'SET_REVIEWS',
  SET_USER_PROFILE: 'SET_USER_PROFILE',
  SET_VALIDATION_STATUS: 'SET_VALIDATION_STATUS',
  SET_LOADING: 'SET_LOADING',
  SET_VALIDATING: 'SET_VALIDATING',
  SET_IMAGE_INDEX: 'SET_IMAGE_INDEX',
  TOGGLE_REVIEW_FORM: 'TOGGLE_REVIEW_FORM',
  TOGGLE_AFFILIATE_MODAL: 'TOGGLE_AFFILIATE_MODAL',
  UPDATE_REVIEW_DATA: 'UPDATE_REVIEW_DATA',
  UPDATE_AFFILIATE_DATA: 'UPDATE_AFFILIATE_DATA',
  RESET_REVIEW_DATA: 'RESET_REVIEW_DATA',
  RESET_AFFILIATE_DATA: 'RESET_AFFILIATE_DATA',
  SET_ALL_DATA: 'SET_ALL_DATA'
};

// Reducer
function productDetailReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_PRODUCT:
      return { ...state, product: action.payload };
    case ACTIONS.SET_REVIEWS:
      return { ...state, reviews: action.payload };
    case ACTIONS.SET_USER_PROFILE:
      return { ...state, userProfile: action.payload };
    case ACTIONS.SET_VALIDATION_STATUS:
      return { ...state, validationStatus: action.payload };
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_VALIDATING:
      return { ...state, isValidating: action.payload };
    case ACTIONS.SET_IMAGE_INDEX:
      return { ...state, currentImageIndex: action.payload };
    case ACTIONS.TOGGLE_REVIEW_FORM:
      return { ...state, showReviewForm: !state.showReviewForm };
    case ACTIONS.TOGGLE_AFFILIATE_MODAL:
      return { ...state, showAffiliateModal: action.payload };
    case ACTIONS.UPDATE_REVIEW_DATA:
      return { ...state, reviewData: { ...state.reviewData, ...action.payload } };
    case ACTIONS.UPDATE_AFFILIATE_DATA:
      return { ...state, affiliateData: { ...state.affiliateData, ...action.payload } };
    case ACTIONS.RESET_REVIEW_DATA:
      return { ...state, reviewData: initialState.reviewData };
    case ACTIONS.RESET_AFFILIATE_DATA:
      return { ...state, affiliateData: initialState.affiliateData };
    case ACTIONS.SET_ALL_DATA:
      return { ...state, ...action.payload };
    default:
      return state;
  }
}

/**
 * Custom hook pour gérer l'état et la logique de ProductDetail
 * Utilise useReducer pour centraliser 18 useState en un seul state
 */
export const useProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const toast = useToast();
  const [state, dispatch] = useReducer(productDetailReducer, initialState);
  const hasFetchedRef = useRef(false);
  const productIdRef = useRef(productId);

  // Fetch product and reviews
  const fetchAllData = async () => {
    if (!productId || hasFetchedRef.current) return;

    try {
      dispatch({ type: ACTIONS.SET_LOADING, payload: true });
      hasFetchedRef.current = true;

      let productData = null;

      // 1. Try fetching as product
      try {
        const productResponse = await api.get(`/api/marketplace/products/${productId}`);
        if (productResponse.data.success) {
          productData = productResponse.data.product;
        }
      } catch (error) {
        // If 404, try fetching as service
        if (error.response && error.response.status === 404) {
          try {
            const serviceResponse = await api.get(`/api/services/${productId}`);
            if (serviceResponse.data) {
              const service = serviceResponse.data;
              // Normalize service data to match product structure
              productData = {
                ...service,
                type: 'service',
                is_service: true,
                images: service.images || (service.image ? [service.image] : []),
                rating_average: service.rating || 0,
                rating_count: service.rating_count || 0,
                merchant: service.merchant || { name: "Service Provider" }
              };
            }
          } catch (serviceError) {
            console.error('Service fetch failed:', serviceError);
          }
        } else {
          console.error('Product fetch error:', error);
        }
      }

      if (productData) {
        dispatch({ type: ACTIONS.SET_PRODUCT, payload: productData });

        // 2. Try fetching reviews (might fail for services if not implemented)
        try {
          const reviewsResponse = await api.get(`/api/marketplace/products/${productId}/reviews`);
          if (reviewsResponse.data.success) {
            dispatch({ type: ACTIONS.SET_REVIEWS, payload: reviewsResponse.data.reviews || [] });
          }
        } catch (reviewError) {
          console.warn('Reviews fetch failed or not available:', reviewError);
          dispatch({ type: ACTIONS.SET_REVIEWS, payload: [] });
        }
      } else {
        // If neither product nor service found
        toast?.error('Produit ou service introuvable');
      }

    } catch (error) {
      console.error('Error in fetchAllData:', error);
      toast?.error('Erreur lors du chargement');
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Fetch user profile
  const fetchUserProfile = async () => {
    if (!user) return;

    try {
      let endpoint = '';
      if (user.role === 'influencer') {
        endpoint = '/api/influencers/profile';
      } else if (user.role === 'commercial') {
        endpoint = '/api/commercials/profile';
      }

      if (endpoint) {
        const response = await api.get(endpoint);
        if (response.data) {
          const profileData = response.data.profile || response.data.commercial || response.data;
          dispatch({ type: ACTIONS.SET_USER_PROFILE, payload: profileData });

          // Check if profile is verified by AI
          if (profileData.verified) {
            dispatch({
              type: ACTIONS.SET_VALIDATION_STATUS,
              payload: {
                verified: true,
                verified_at: profileData.verified_at,
                confidence_score: profileData.confidence_score,
                bonus_rating: profileData.bonus_rating || 0,
                validation_badges: profileData.validation_badges || []
              }
            });
          }
        }
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  // Validate stats with AI
  const validateStatsWithAI = async () => {
    if (!user || user.role !== 'influencer') return;

    dispatch({ type: ACTIONS.SET_VALIDATING, payload: true });
    try {
      const response = await api.post('/api/influencers/validate-stats');
      if (response.data.success) {
        dispatch({ type: ACTIONS.SET_VALIDATION_STATUS, payload: response.data });

        // Update user profile with new status
        await fetchUserProfile();

        if (response.data.is_verified) {
          toast?.success(`✅ Profil vérifié ! Score: ${response.data.confidence_score}% - Bonus de note: +${response.data.bonus_rating}⭐`);
        } else {
          toast?.info('🔍 Validation en cours. Améliorez vos statistiques pour être vérifié.');
        }
      }
    } catch (error) {
      console.error('Error validating stats:', error);
      toast?.error('Erreur lors de la validation IA');
    } finally {
      dispatch({ type: ACTIONS.SET_VALIDATING, payload: false });
    }
  };

  // Handle affiliation request
  const handleRequestAffiliation = useCallback(async () => {
    if (!user) {
      toast.info('Veuillez vous connecter pour demander une affiliation');
      localStorage.setItem('redirectAfterLogin', window.location.pathname);
      localStorage.setItem('openAffiliateModal', 'true');
      navigate('/login');
      return;
    }

    if (user.role !== 'influencer' && user.role !== 'commercial') {
      toast.warning('Vous devez être un influenceur ou commercial pour demander une affiliation');
      return;
    }

    await fetchUserProfile();

    dispatch({ type: ACTIONS.TOGGLE_AFFILIATE_MODAL, payload: true });
    dispatch({
      type: ACTIONS.UPDATE_AFFILIATE_DATA,
      payload: {
        selectedProduct: state.product?.name || '',
        message: ''
      }
    });
  }, [user, state.product, navigate, toast, fetchUserProfile]);

  // Submit affiliation request
  const handleSubmitAffiliateRequest = useCallback(async (e) => {
    e.preventDefault();

    if (!state.affiliateData.message.trim()) {
      toast.warning('Veuillez rédiger un message de présentation');
      return;
    }

    try {
      const response = await api.post(`/api/marketplace/products/${productId}/request-affiliate`, {
        message: state.affiliateData.message
      });

      if (response.data.success) {
        toast.success('Demande d\'affiliation envoyée avec succès!');
        if (response.data.affiliate_link) {
          toast.info(`Votre lien: ${response.data.affiliate_link}`);
        }
        dispatch({ type: ACTIONS.TOGGLE_AFFILIATE_MODAL, payload: false });
        dispatch({ type: ACTIONS.RESET_AFFILIATE_DATA });
      }
    } catch (error) {
      toast.error(getErrorMessage(error, 'Erreur lors de la demande'));
    }
  }, [productId, state.affiliateData, toast]);

  // Submit review
  const handleSubmitReview = useCallback(async (e) => {
    e.preventDefault();
    if (!user) {
      toast.warning('Vous devez être connecté pour laisser un avis');
      return;
    }

    try {
      const response = await api.post(`/api/marketplace/products/${productId}/review`, state.reviewData);
      if (response.data.success) {
        toast.success('Votre avis a été soumis et sera vérifié par nos modérateurs');
        dispatch({ type: ACTIONS.TOGGLE_REVIEW_FORM });
        dispatch({ type: ACTIONS.RESET_REVIEW_DATA });
      }
    } catch (error) {
      toast.error(getErrorMessage(error, 'Erreur lors de l\'envoi de l\'avis'));
    }
  }, [user, productId, state.reviewData, toast]);

  // Fetch all data on mount and handle productId change
  useEffect(() => {
    // Reset if productId changes
    if (productIdRef.current !== productId) {
      hasFetchedRef.current = false;
      productIdRef.current = productId;
    }
    
    fetchAllData();
  }, [productId]);

  // Check if user returned after login to open affiliate modal
  useEffect(() => {
    if (user && state.product) {
      const shouldOpenAffiliate = localStorage.getItem('openAffiliateModal');
      if (shouldOpenAffiliate === 'true') {
        localStorage.removeItem('openAffiliateModal');
        dispatch({ type: ACTIONS.TOGGLE_AFFILIATE_MODAL, payload: true });
        dispatch({
          type: ACTIONS.UPDATE_AFFILIATE_DATA,
          payload: {
            selectedProduct: state.product.name,
            message: ''
          }
        });
      }
    }
  }, [user, state.product]);

  return {
    state,
    dispatch,
    actions: {
      setImageIndex: (index) => dispatch({ type: ACTIONS.SET_IMAGE_INDEX, payload: index }),
      toggleReviewForm: () => dispatch({ type: ACTIONS.TOGGLE_REVIEW_FORM }),
      toggleAffiliateModal: (show) => dispatch({ type: ACTIONS.TOGGLE_AFFILIATE_MODAL, payload: show }),
      updateReviewData: (data) => dispatch({ type: ACTIONS.UPDATE_REVIEW_DATA, payload: data }),
      updateAffiliateData: (data) => dispatch({ type: ACTIONS.UPDATE_AFFILIATE_DATA, payload: data }),
      fetchUserProfile,
      validateStatsWithAI,
      handleRequestAffiliation,
      handleSubmitAffiliateRequest,
      handleSubmitReview,
      fetchAllData
    }
  };
};
