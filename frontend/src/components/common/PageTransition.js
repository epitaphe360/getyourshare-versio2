import React from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 12, filter: 'blur(4px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)' },
  exit: { opacity: 0, y: -8, filter: 'blur(4px)' },
};

const pageTransition = {
  type: 'tween',
  ease: [0.25, 0.46, 0.45, 0.94],
  duration: 0.35,
};

const PageTransition = ({ children }) => (
  <motion.div
    initial="initial"
    animate="animate"
    exit="exit"
    variants={pageVariants}
    transition={pageTransition}
  >
    {children}
  </motion.div>
);

export default PageTransition;
