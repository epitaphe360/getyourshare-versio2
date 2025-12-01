import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

/**
 * Modal de base réutilisable pour toute l'application
 * @param {boolean} isOpen - Modal ouvert ou fermé
 * @param {function} onClose - Fonction appelée à la fermeture
 * @param {string} title - Titre de la modal
 * @param {React.Node} children - Contenu de la modal
 * @param {string} size - Taille: 'sm', 'md', 'lg', 'xl', '2xl'
 * @param {React.Node} footer - Contenu du footer (boutons)
 * @param {boolean} closeOnOverlay - Fermer en cliquant sur l'overlay
 * @param {boolean} showCloseButton - Afficher le bouton X
 */
const BaseModal = ({
  isOpen = false,
  onClose,
  title,
  children,
  size = 'md',
  footer,
  closeOnOverlay = true,
  showCloseButton = true,
  className = ''
}) => {
  // Tailles de modal
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    full: 'max-w-full mx-4'
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && closeOnOverlay && onClose) {
      onClose();
    }
  };

  const handleClose = () => {
    if (onClose) onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto"
          onClick={handleOverlayClick}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className={`bg-white rounded-lg shadow-xl w-full ${sizeClasses[size]} max-h-[90vh] flex flex-col ${className}`}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                {title && <h3 className="text-xl font-semibold text-gray-900">{title}</h3>}
                {showCloseButton && (
                  <button
                    onClick={handleClose}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    aria-label="Fermer"
                  >
                    <X size={24} />
                  </button>
                )}
              </div>
            )}

            {/* Body */}
            <div className="p-6 overflow-y-auto flex-1">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default BaseModal;
