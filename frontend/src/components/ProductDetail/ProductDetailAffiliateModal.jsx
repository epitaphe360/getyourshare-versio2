import React, { memo } from 'react';
import {
  X, Sparkles, Users, AlertCircle, Check, Award, MapPin, Tag, Briefcase,
  Shield, ShieldCheck, CheckCircle
} from 'lucide-react';

/**
 * ProductDetailAffiliateModal - Affiliation request modal
 * React.memo for performance optimization
 */
const ProductDetailAffiliateModal = memo(({
  show,
  user,
  product,
  userProfile,
  validationStatus,
  isValidating,
  affiliateData,
  onClose,
  onUpdateAffiliateData,
  onSubmit,
  onValidateStats
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header - Dynamique selon le rôle */}
        <div
          className={`sticky top-0 ${
            user?.role === 'influencer'
              ? 'bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-600'
              : 'bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600'
          } text-white p-6 rounded-t-2xl`}
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold flex items-center">
                <Sparkles className="w-6 h-6 mr-2" />
                {user?.role === 'influencer'
                  ? 'Devenir Partenaire Influenceur'
                  : 'Devenir Partenaire Commercial'}
              </h2>
              <p className="text-white/90 text-sm mt-1">
                {user?.role === 'influencer'
                  ? 'Monétisez votre audience en promouvant des produits de qualité'
                  : 'Développez votre réseau et gagnez des commissions'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full p-2 transition"
              aria-label="Close modal"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Profil automatiquement détecté */}
          {userProfile && (
            <div
              className={`mb-6 p-6 rounded-2xl border-2 ${
                user?.role === 'influencer'
                  ? 'bg-gradient-to-br from-pink-50 to-purple-50 border-pink-200'
                  : 'bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-gray-900 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Votre Profil
                  {/* Badge Vérifié */}
                  {validationStatus?.verified && (
                    <span className="ml-2 inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-bold rounded-full animate-pulse-glow">
                      <ShieldCheck className="w-4 h-4" />
                      Vérifié IA
                    </span>
                  )}
                </h3>

                {/* Bouton de validation IA (uniquement pour influenceurs non vérifiés) */}
                {user?.role === 'influencer' && !validationStatus?.verified && (
                  <button
                    onClick={onValidateStats}
                    disabled={isValidating}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
                  >
                    {isValidating ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Validation...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4" />
                        Valider mes Stats
                      </>
                    )}
                  </button>
                )}
              </div>

              {user?.role === 'influencer' ? (
                // Profil Influenceur
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                      {(() => {
                        const count = Number(userProfile.followers_count);
                        return isNaN(count) ? '0' : (count / 1000).toFixed(1);
                      })()}
                      K
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1 flex items-center justify-center gap-1">
                      Followers
                      {validationStatus?.verified && (
                        <CheckCircle className="w-3 h-3 text-green-500" />
                      )}
                    </div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                      {(() => {
                        const rate = Number(userProfile.engagement_rate);
                        return isNaN(rate) ? '0' : rate;
                      })()}%
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">Engagement</div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
                      {userProfile.campaigns_completed || 0}
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">Campagnes</div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center relative">
                    <div className="text-2xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                      {(userProfile.rating || 4.5) + (validationStatus?.bonus_rating || 0)}⭐
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">
                      Note
                      {validationStatus?.bonus_rating > 0 && (
                        <span className="text-green-600 ml-1">
                          (+{validationStatus.bonus_rating})
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                // Profil Commercial
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                      {userProfile.total_sales || 0}
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">Ventes</div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                      {userProfile.commission_earned || 0}
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">DH Gagnés</div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-teal-600 to-green-600 bg-clip-text text-transparent">
                      {userProfile.territory || 'National'}
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">Territoire</div>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl text-center">
                    <div className="text-2xl font-black bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                      {userProfile.rating || 4.5}⭐
                    </div>
                    <div className="text-xs text-gray-600 font-semibold mt-1">Note</div>
                  </div>
                </div>
              )}

              {/* Informations supplémentaires */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="flex items-center gap-2 text-sm">
                    <MapPin className="w-4 h-4 text-gray-500" />
                    <span className="font-semibold">{userProfile.city || 'Maroc'}</span>
                  </div>
                  {user?.role === 'influencer' && userProfile.niche && (
                    <div className="flex items-center gap-2 text-sm">
                      <Tag className="w-4 h-4 text-gray-500" />
                      <span className="font-semibold">{userProfile.niche}</span>
                    </div>
                  )}
                  {user?.role === 'commercial' && userProfile.department && (
                    <div className="flex items-center gap-2 text-sm">
                      <Briefcase className="w-4 h-4 text-gray-500" />
                      <span className="font-semibold">{userProfile.department}</span>
                    </div>
                  )}
                </div>

                {/* Badges de validation IA */}
                {validationStatus?.validation_badges &&
                  validationStatus.validation_badges.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <h4 className="text-xs font-bold text-gray-600 mb-2">
                        Certifications IA
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {validationStatus.validation_badges.map((badge, idx) => (
                          <div
                            key={idx}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 text-xs font-semibold rounded-full border border-purple-300"
                            title={badge.description}
                          >
                            {badge.icon === 'shield-check' && <ShieldCheck className="w-3 h-3" />}
                            {badge.icon === 'shield' && <Shield className="w-3 h-3" />}
                            {badge.icon === 'check-circle' && <CheckCircle className="w-3 h-3" />}
                            {badge.icon === 'users-check' && <Users className="w-3 h-3" />}
                            {badge.name}
                          </div>
                        ))}
                      </div>
                      {validationStatus.confidence_score && (
                        <p className="text-xs text-gray-500 mt-2">
                          Score de confiance IA:{' '}
                          <span className="font-bold text-green-600">
                            {validationStatus.confidence_score}%
                          </span>
                        </p>
                      )}
                    </div>
                  )}
              </div>
            </div>
          )}

          {/* How it works */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              Comment ça fonctionne ?
            </h3>
            <p className="text-blue-800 text-sm leading-relaxed">
              {validationStatus?.verified
                ? "✅ Votre profil vérifié par IA augmente vos chances d'approbation ! Le marchand verra votre badge et votre note bonifiée."
                : "Votre profil a été automatiquement récupéré. Faites valider vos stats par l'IA pour obtenir un badge 'Vérifié' et un bonus de note !"}{' '}
              Un lien de tracking unique sera créé pour vous après approbation.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={onSubmit} className="space-y-6">
            {/* Product Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Produit sélectionné <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={affiliateData.selectedProduct}
                  readOnly
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg bg-gray-50 text-gray-700 font-medium cursor-not-allowed"
                  placeholder="Choisir un produit..."
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Check className="w-5 h-5 text-green-600" />
                </div>
              </div>
            </div>

            {/* Message to Merchant */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Message de motivation <span className="text-red-500">*</span>
              </label>
              <textarea
                value={affiliateData.message}
                onChange={(e) => onUpdateAffiliateData({ message: e.target.value })}
                rows="5"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 transition resize-none"
                placeholder={
                  user?.role === 'influencer'
                    ? 'Expliquez comment vous allez promouvoir ce produit auprès de votre audience...\nExemple: Stories Instagram, vidéos TikTok, posts sponsorisés...'
                    : 'Expliquez votre stratégie commerciale pour ce produit...\nExemple: Réseau de clients, zone géographique, expérience secteur...'
                }
                required
              />
              <div className="flex items-start mt-2 text-xs text-gray-500">
                <AlertCircle className="w-4 h-4 mr-1 mt-0.5 flex-shrink-0" />
                <p>
                  {user?.role === 'influencer'
                    ? 'Décrivez votre stratégie de contenu et plateformes que vous utiliserez'
                    : 'Présentez votre expérience et votre réseau commercial'}
                </p>
              </div>
            </div>

            {/* Product Info Card */}
            {product && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4">
                <div className="flex items-start space-x-4">
                  <img
                    src={product.image_url || '/logo.png'}
                    alt={product.name}
                    className="w-20 h-20 object-cover rounded-lg shadow-md"
                    onError={(e) => {
                      e.target.src = '/logo.png';
                    }}
                  />
                  <div className="flex-1">
                    <h4 className="font-bold text-gray-900 mb-1">{product.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {product.description?.substring(0, 100)}...
                    </p>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <Award className="w-4 h-4 text-green-600 mr-1" />
                        <span className="text-sm font-semibold text-green-700">
                          {product.commission_rate || 15}% commission
                        </span>
                      </div>
                      {product.price && (
                        <span className="text-sm font-bold text-gray-900">
                          {product.price} DH
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Commission Info */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <Award className="w-6 h-6 text-yellow-600" />
                </div>
                <div className="ml-3">
                  <h4 className="font-semibold text-yellow-900 mb-1">
                    💰 Commission de {product?.commission_rate || 15}%
                  </h4>
                  <p className="text-sm text-yellow-800">
                    {user?.role === 'influencer'
                      ? `Pour chaque vente générée via votre lien d'affiliation, vous recevez ${
                          product?.commission_rate || 15
                        }% du montant.`
                      : `Commission de ${
                          product?.commission_rate || 15
                        }% sur chaque vente réalisée dans votre zone.`}
                  </p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition"
              >
                Annuler
              </button>
              <button
                type="submit"
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-bold hover:from-green-600 hover:to-emerald-700 transition flex items-center justify-center shadow-lg"
              >
                <Sparkles className="w-5 h-5 mr-2" />
                Envoyer la Demande
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
});

ProductDetailAffiliateModal.displayName = 'ProductDetailAffiliateModal';

export default ProductDetailAffiliateModal;
