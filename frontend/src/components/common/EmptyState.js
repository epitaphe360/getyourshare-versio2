import React from 'react';
import { Package } from 'lucide-react';
import { motion } from 'framer-motion';

const EmptyState = ({ 
  icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryActionLabel,
  onSecondaryAction,
  loading
}) => {
  // Accept both icon components (Search) or ready-made elements (<Search />)
  const renderIcon = () => {
    if (React.isValidElement(icon)) {
      // Preserve existing props but ensure consistent sizing/styling
      return React.cloneElement(icon, {
        size: icon.props.size || 48,
        className: icon.props.className ? `${icon.props.className}` : 'text-gray-400'
      });
    }
    if (typeof icon === 'function') {
      const IconComponent = icon;
      return <IconComponent className="text-gray-400" size={48} />;
    }
    return <Package className="text-gray-400" size={48} />;
  };
  const displayTitle = title || "Aucune donnée disponible";
  const displayDescription = description || "Commencez par ajouter des éléments";
  const isLoading = loading || false;
  
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center justify-center py-16 px-4 text-center"
    >
      <motion.div 
        initial={{ y: -10 }}
        animate={{ y: 0 }}
        transition={{ 
          repeat: Infinity, 
          repeatType: "reverse", 
          duration: 2 
        }}
        className="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6 shadow-sm border border-gray-100"
      >
        {renderIcon()}
      </motion.div>
      <h3 className="text-xl font-bold text-gray-900 mb-3">{displayTitle}</h3>
      <p className="text-gray-500 text-center mb-8 max-w-md leading-relaxed">{displayDescription}</p>
      
      {(actionLabel || secondaryActionLabel) && (
        <div className="flex flex-col sm:flex-row gap-4">
          {actionLabel && (
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onAction} 
              disabled={isLoading} 
              className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {actionLabel}
            </motion.button>
          )}
          {secondaryActionLabel && (
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onSecondaryAction}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-white border border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-all duration-200 disabled:opacity-50"
            >
              {secondaryActionLabel}
            </motion.button>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default EmptyState;