import React, { memo } from 'react';
import { Star, Heart, Share2, ChevronLeft, ChevronRight, Award, MapPin } from 'lucide-react';

/**
 * ProductDetailHeader - Images carousel, title, rating
 * React.memo for performance optimization
 */
const ProductDetailHeader = memo(({
  product,
  images = [],
  currentImageIndex,
  onImageChange,
  hasDiscount
}) => {
  if (!product) return null;

  const nextImage = () => {
    onImageChange((currentImageIndex + 1) % images.length);
  };

  const prevImage = () => {
    onImageChange((currentImageIndex - 1 + images.length) % images.length);
  };

  return (
    <div className="space-y-6">
      {/* Image Gallery - Ultra-moderne */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden hover-lift">
        {images.length > 0 ? (
          <div className="relative group">
            <img
              src={images[currentImageIndex]}
              alt={product.name}
              className="w-full h-[500px] object-cover"
              onError={(e) => {
                e.target.onerror = null;
                if (product?.type === 'service') {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%233b82f6" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EService%3C/text%3E%3C/svg%3E';
                } else {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="800" height="600"%3E%3Crect fill="%230891b2" width="800" height="600"/%3E%3Ctext fill="%23ffffff" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3EProduit%3C/text%3E%3C/svg%3E';
                }
              }}
            />
            {hasDiscount && (
              <div className="absolute top-6 right-6 bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-3 rounded-2xl font-black text-xl shadow-2xl animate-pulse z-10">
                -{product.discount_percentage}%
              </div>
            )}
            {images.length > 1 && (
              <>
                <button
                  onClick={prevImage}
                  className="absolute left-6 top-1/2 transform -translate-y-1/2 bg-white/95 backdrop-blur-sm p-4 rounded-xl hover:bg-white shadow-xl opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-110"
                  aria-label="Previous image"
                >
                  <ChevronLeft className="w-7 h-7 text-gray-800" />
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-6 top-1/2 transform -translate-y-1/2 bg-white/95 backdrop-blur-sm p-4 rounded-xl hover:bg-white shadow-xl opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-110"
                  aria-label="Next image"
                >
                  <ChevronRight className="w-7 h-7 text-gray-800" />
                </button>
                <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex space-x-3 bg-black/30 backdrop-blur-md px-4 py-3 rounded-full">
                  {images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => onImageChange(index)}
                      className={`transition-all duration-300 rounded-full ${
                        index === currentImageIndex
                          ? 'w-10 h-3 bg-white'
                          : 'w-3 h-3 bg-white/50 hover:bg-white/75'
                      }`}
                      aria-label={`Go to image ${index + 1}`}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="w-full h-[500px] bg-gradient-to-br from-blue-100 via-cyan-100 to-teal-100 flex items-center justify-center">
            <div className="text-center">
              <Award className="w-32 h-32 text-cyan-400 mx-auto mb-6 animate-pulse" />
              <p className="text-gray-600 font-bold text-xl">Image du produit</p>
            </div>
          </div>
        )}
      </div>

      {/* Product Title & Description - Ultra-moderne */}
      <div className="bg-white rounded-2xl shadow-xl p-8 hover-lift">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <h1 className="text-4xl font-black bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent mb-3 leading-tight">
              {product.name}
            </h1>
            <p className="text-gray-600 text-lg font-semibold flex items-center gap-2">
              <Award className="w-5 h-5 text-cyan-600" />
              {product.merchant?.company_name || product.merchant?.name || product.merchant_name || 'Marchand Certifié'}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              className="p-4 bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl hover:shadow-xl transition-all duration-300 group hover:scale-110"
              aria-label="Add to favorites"
            >
              <Heart className="w-6 h-6 text-pink-500 group-hover:fill-pink-500 transition-all" />
            </button>
            <button
              className="p-4 bg-gradient-to-br from-blue-50 to-cyan-100 rounded-xl hover:shadow-xl transition-all duration-300 group hover:scale-110"
              aria-label="Share product"
            >
              <Share2 className="w-6 h-6 text-cyan-600 group-hover:rotate-12 transition-all" />
            </button>
          </div>
        </div>

        {/* Rating */}
        {product.rating_average > 0 && (
          <div className="flex items-center mb-6 bg-gradient-to-r from-yellow-50 to-orange-50 px-4 py-3 rounded-xl">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-6 h-6 ${
                    i < Math.floor(product.rating_average)
                      ? 'text-yellow-400 fill-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="ml-3 text-gray-800 font-bold text-lg">
              {product.rating_average.toFixed(1)}
            </span>
            <span className="ml-2 text-gray-600 font-medium">
              ({product.rating_count} avis)
            </span>
          </div>
        )}

        {/* Location for services */}
        {product.is_service && product.location && (
          <div className="flex items-center gap-3 text-gray-700 mb-6 bg-gradient-to-r from-blue-50 to-cyan-50 px-4 py-3 rounded-xl">
            <MapPin className="w-6 h-6 text-cyan-600" />
            <span className="font-semibold">
              {product.location.address}, {product.location.city}
            </span>
          </div>
        )}

        {/* Description */}
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed text-lg">{product.description}</p>
        </div>
      </div>
    </div>
  );
});

ProductDetailHeader.displayName = 'ProductDetailHeader';

export default ProductDetailHeader;
