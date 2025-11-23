import React, { useState } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import { X, Heart, Info, ShieldCheck, DollarSign, Users } from 'lucide-react';

const SwipeCard = ({ item, onSwipe, style }) => {
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);
  const background = useTransform(
    x,
    [-200, 0, 200],
    ['rgba(239, 68, 68, 0.2)', 'rgba(255, 255, 255, 0.1)', 'rgba(34, 197, 94, 0.2)']
  );

  const handleDragEnd = (event, info) => {
    if (info.offset.x > 100) {
      onSwipe('right', item);
    } else if (info.offset.x < -100) {
      onSwipe('left', item);
    }
  };

  return (
    <motion.div
      style={{ x, rotate, opacity, background, ...style }}
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      className="absolute top-0 left-0 w-full h-full rounded-3xl shadow-2xl cursor-grab active:cursor-grabbing overflow-hidden border border-white/20 backdrop-blur-xl"
    >
      {/* Image Section */}
      <div className="h-3/5 w-full relative">
        <img 
          src={item.image || 'https://via.placeholder.com/400x600'} 
          alt={item.title} 
          className="w-full h-full object-cover pointer-events-none"
        />
        <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-black/80 to-transparent pointer-events-none" />
        <div className="absolute bottom-4 left-4 text-white pointer-events-none">
          <h3 className="text-2xl font-bold shadow-black drop-shadow-md">{item.title}</h3>
          <p className="text-sm opacity-90">{item.subtitle}</p>
        </div>
      </div>

      {/* Info Section - Glassmorphism */}
      <div className="h-2/5 w-full p-6 flex flex-col justify-between text-white">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm font-medium text-purple-200">
            <ShieldCheck size={16} className="text-green-400" />
            <span>Paiement Sécurisé (Escrow)</span>
          </div>
          
          <p className="text-sm text-gray-300 line-clamp-3">
            {item.description}
          </p>

          <div className="flex justify-between items-center mt-4">
            <div className="flex flex-col">
              <span className="text-xs text-gray-400">Budget</span>
              <span className="text-lg font-bold text-green-400 flex items-center">
                <DollarSign size={16} /> {item.budget}
              </span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-xs text-gray-400">Audience</span>
              <span className="text-lg font-bold text-blue-400 flex items-center gap-1">
                <Users size={16} /> {item.audience}
              </span>
            </div>
          </div>
        </div>

        <div className="flex justify-center gap-8 mt-4">
          <div className="text-red-400 text-xs font-bold uppercase tracking-widest opacity-50">Passer</div>
          <div className="text-green-400 text-xs font-bold uppercase tracking-widest opacity-50">Postuler</div>
        </div>
      </div>

      {/* Overlay Labels */}
      <motion.div 
        style={{ opacity: useTransform(x, [20, 100], [0, 1]) }}
        className="absolute top-8 left-8 border-4 border-green-500 text-green-500 rounded-lg px-4 py-2 text-2xl font-bold transform -rotate-12"
      >
        LIKE
      </motion.div>
      <motion.div 
        style={{ opacity: useTransform(x, [-100, -20], [1, 0]) }}
        className="absolute top-8 right-8 border-4 border-red-500 text-red-500 rounded-lg px-4 py-2 text-2xl font-bold transform rotate-12"
      >
        NOPE
      </motion.div>
    </motion.div>
  );
};

const SwipeMatching = ({ items = [], onMatch, onReject }) => {
  const [currentIndex, setCurrentIndex] = useState(items.length - 1);
  const [lastDirection, setLastDirection] = useState(null);

  const handleSwipe = (direction, item) => {
    setLastDirection(direction);
    if (direction === 'right') {
      onMatch(item);
    } else {
      onReject(item);
    }
    setTimeout(() => setCurrentIndex(prev => prev - 1), 200);
  };

  if (currentIndex < 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] w-full max-w-md mx-auto bg-gray-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-8 text-center">
        <div className="bg-gray-800/50 p-4 rounded-full mb-4">
          <Info size={48} className="text-purple-400" />
        </div>
        <h3 className="text-2xl font-bold text-white mb-2">Plus de profils !</h3>
        <p className="text-gray-400 mb-6">Vous avez vu toutes les campagnes disponibles pour le moment.</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-purple-500/30 transition"
        >
          Rafraîchir
        </button>
      </div>
    );
  }

  return (
    <div className="relative w-full max-w-md h-[600px] mx-auto perspective-1000">
      <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
        {/* Controls (Visual only, interaction is on card) */}
      </div>
      
      {items.map((item, index) => (
        index <= currentIndex && (
          <SwipeCard
            key={item.id}
            item={item}
            onSwipe={handleSwipe}
            style={{
              zIndex: index,
              scale: index === currentIndex ? 1 : 0.95,
              y: index === currentIndex ? 0 : 10,
            }}
          />
        )
      ))}

      {/* Bottom Actions */}
      <div className="absolute -bottom-20 left-0 w-full flex justify-center gap-6">
        <button 
          onClick={() => handleSwipe('left', items[currentIndex])}
          className="p-4 bg-gray-800/80 backdrop-blur-md rounded-full text-red-500 shadow-lg hover:bg-gray-700 transition transform hover:scale-110"
        >
          <X size={32} />
        </button>
        <button 
          onClick={() => handleSwipe('right', items[currentIndex])}
          className="p-4 bg-gray-800/80 backdrop-blur-md rounded-full text-green-500 shadow-lg hover:bg-gray-700 transition transform hover:scale-110"
        >
          <Heart size={32} fill="currentColor" />
        </button>
      </div>
    </div>
  );
};

export default SwipeMatching;
