import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Wand2, Instagram, Copy, Check, Clock, Calendar,
  Hash, MessageSquare, Video, Image as ImageIcon, Sparkles
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const ContentStudio = ({ userId }) => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [platform, setPlatform] = useState('instagram');
  const [contentType, setContentType] = useState('post');
  const [language, setLanguage] = useState('fr');
  const [tone, setTone] = useState('professional');
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [copiedField, setCopiedField] = useState('');
  const [myTemplates, setMyTemplates] = useState([]);
  const toast = useToast();

  useEffect(() => {
    fetchProducts();
    fetchMyTemplates();
  }, [userId]);

  const fetchProducts = async () => {
    try {
      // Récupérer produits (pour marchands) ou recommendations (pour influenceurs)
      const response = await api.get(`/api/products?limit=50`);
      setProducts(response.data || []);
    } catch (error) {
      // Silent fail
    }
  };

  const fetchMyTemplates = async () => {
    try {
      const response = await api.get(`/api/ai/content-templates/${userId}`);
      setMyTemplates(response.data.templates || []);
    } catch (error) {
      // Silent fail
    }
  };

  const generateContent = async () => {
    if (!selectedProduct) {
      toast?.error('Sélectionne un produit');
      return;
    }

    try {
      setGenerating(true);
      const response = await api.post('/api/ai/generate-content', {
        product_id: selectedProduct,
        platform,
        content_type: contentType,
        language,
        tone
      }, {
        params: { influencer_id: userId }
      });

      setGeneratedContent(response.data.content);
      toast?.success('Contenu généré avec succès!');

      // Refresh templates
      await fetchMyTemplates();
    } catch (error) {
      toast?.error('Erreur génération contenu');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    toast?.success('Copié!');
    setTimeout(() => setCopiedField(''), 2000);
  };

  const getPlatformIcon = (plat) => {
    const icons = {
      instagram: <Instagram className="w-5 h-5" />,
      tiktok: <Video className="w-5 h-5" />,
      facebook: <MessageSquare className="w-5 h-5" />
    };
    return icons[plat] || <ImageIcon className="w-5 h-5" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
              <Wand2 className="w-7 h-7" />
              Content Studio IA
            </h2>
            <p className="text-indigo-100">
              Génère du contenu optimisé en quelques secondes
            </p>
          </div>
          <Sparkles className="w-16 h-16 opacity-30" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Générateur */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Générer du Contenu</h3>

          <div className="space-y-4">
            {/* Sélection produit */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Produit à promouvoir
              </label>
              <select
                value={selectedProduct}
                onChange={(e) => setSelectedProduct(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Sélectionne un produit</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} - {product.price}€
                  </option>
                ))}
              </select>
            </div>

            {/* Plateforme */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plateforme
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['instagram', 'tiktok', 'facebook'].map((plat) => (
                  <button
                    key={plat}
                    onClick={() => setPlatform(plat)}
                    className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg border-2 transition ${
                      platform === plat
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {getPlatformIcon(plat)}
                    <span className="capitalize text-sm font-medium">{plat}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Type de contenu */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de contenu
              </label>
              <div className="grid grid-cols-2 gap-2">
                {['post', 'story', 'reel', 'caption'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setContentType(type)}
                    className={`px-4 py-2 rounded-lg border-2 transition capitalize ${
                      contentType === type
                        ? 'border-purple-600 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Langue */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Langue
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
              >
                <option value="fr">Français</option>
                <option value="ar">العربية</option>
                <option value="darija">Darija</option>
                <option value="en">English</option>
              </select>
            </div>

            {/* Ton */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ton du contenu
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
              >
                <option value="professional">Professionnel</option>
                <option value="casual">Décontracté</option>
                <option value="funny">Amusant</option>
                <option value="inspirational">Inspirant</option>
              </select>
            </div>

            {/* Generate Button */}
            <button
              onClick={generateContent}
              disabled={generating || !selectedProduct}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Wand2 className="w-5 h-5 animate-spin" />
                  Génération en cours...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Générer avec IA
                </>
              )}
            </button>
          </div>
        </div>

        {/* Aperçu du contenu généré */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Contenu Généré</h3>

          <AnimatePresence mode="wait">
            {generatedContent ? (
              <motion.div
                key="content"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4"
              >
                {/* Titre */}
                {generatedContent.title && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700">Titre</label>
                      <button
                        onClick={() => copyToClipboard(generatedContent.title, 'title')}
                        className="text-purple-600 hover:text-purple-700 text-sm flex items-center gap-1"
                      >
                        {copiedField === 'title' ? (
                          <>
                            <Check className="w-4 h-4" /> Copié
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" /> Copier
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-gray-900 font-medium">{generatedContent.title}</p>
                  </div>
                )}

                {/* Contenu principal */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">Contenu</label>
                    <button
                      onClick={() => copyToClipboard(generatedContent.content, 'content')}
                      className="text-purple-600 hover:text-purple-700 text-sm flex items-center gap-1"
                    >
                      {copiedField === 'content' ? (
                        <>
                          <Check className="w-4 h-4" /> Copié
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" /> Copier
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-gray-900 whitespace-pre-wrap">{generatedContent.content}</p>
                </div>

                {/* Hashtags */}
                {generatedContent.hashtags && generatedContent.hashtags.length > 0 && (
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                        <Hash className="w-4 h-4" /> Hashtags
                      </label>
                      <button
                        onClick={() => copyToClipboard(generatedContent.hashtags.join(' '), 'hashtags')}
                        className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                      >
                        {copiedField === 'hashtags' ? (
                          <>
                            <Check className="w-4 h-4" /> Copié
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" /> Copier
                          </>
                        )}
                      </button>
                    </div>
                    <p className="text-blue-700 text-sm">
                      {generatedContent.hashtags.join(' ')}
                    </p>
                  </div>
                )}

                {/* Call to Action */}
                {generatedContent.cta && (
                  <div className="bg-green-50 rounded-lg p-4">
                    <label className="text-sm font-medium text-gray-700 block mb-2">
                      Call-to-Action
                    </label>
                    <p className="text-green-700 font-medium">{generatedContent.cta}</p>
                  </div>
                )}

                {/* Meilleur timing */}
                <div className="grid grid-cols-2 gap-3">
                  {generatedContent.best_time && (
                    <div className="bg-purple-50 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-4 h-4 text-purple-600" />
                        <span className="text-xs font-medium text-gray-700">Meilleure heure</span>
                      </div>
                      <p className="text-purple-700 font-bold">{generatedContent.best_time}</p>
                    </div>
                  )}
                  {generatedContent.best_day && (
                    <div className="bg-purple-50 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Calendar className="w-4 h-4 text-purple-600" />
                        <span className="text-xs font-medium text-gray-700">Meilleur jour</span>
                      </div>
                      <p className="text-purple-700 font-bold">{generatedContent.best_day}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-12"
              >
                <Wand2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">
                  Sélectionne un produit et clique sur "Générer"
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Mes Templates */}
      {myTemplates.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Mes Templates Récents</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {myTemplates.slice(0, 6).map((template) => (
              <div
                key={template.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition"
              >
                <div className="flex items-center gap-2 mb-2">
                  {getPlatformIcon(template.platform)}
                  <span className="text-sm font-medium text-gray-600 capitalize">
                    {template.platform} • {template.content_type}
                  </span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-3 mb-3">
                  {template.content}
                </p>
                <button
                  onClick={() => {
                    setGeneratedContent({
                      title: template.title,
                      content: template.content,
                      hashtags: template.hashtags,
                      cta: template.call_to_action,
                      best_time: template.best_post_time,
                      best_day: template.best_post_day
                    });
                  }}
                  className="text-purple-600 hover:text-purple-700 text-sm font-medium"
                >
                  Réutiliser →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentStudio;
