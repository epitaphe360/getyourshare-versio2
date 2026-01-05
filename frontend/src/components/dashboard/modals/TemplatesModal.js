import React from 'react';
import { motion } from 'framer-motion';
import { Copy } from 'lucide-react';
import { toast } from 'react-toastify';

const TemplatesModal = ({ templates, onClose, tier }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
    >
      <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">📝 Templates Marketing</h2>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-800">
          ✕
        </button>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {templates.map((template) => (
            <div key={template.id} className="border rounded-lg p-4 hover:shadow-lg transition">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-800">{template.title}</h3>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                  {template.category}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3 whitespace-pre-wrap">{template.content.substring(0, 150)}...</p>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(template.content);
                  toast.success('Template copié !');
                }}
                className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition"
              >
                <Copy size={16} className="inline mr-2" />
                Copier le template
              </button>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  </div>
);

export default TemplatesModal;
