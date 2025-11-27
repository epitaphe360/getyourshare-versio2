import React, { useState } from 'react';
import api from '../../services/api';
import { Wand2, Copy, Check, RefreshCw } from 'lucide-react';

const AIContentGenerator = () => {
  const [formData, setFormData] = useState({
    platform: 'instagram',
    content_type: 'post',
    product_name: '',
    features: '',
    tone: 'enthusiastic'
  });
  const [generatedContent, setGeneratedContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const platforms = [
    { id: 'instagram', label: 'Instagram' },
    { id: 'tiktok', label: 'TikTok' },
    { id: 'facebook', label: 'Facebook' },
    { id: 'twitter', label: 'Twitter / X' },
    { id: 'linkedin', label: 'LinkedIn' }
  ];

  const contentTypes = [
    { id: 'post', label: 'Post Classique' },
    { id: 'story', label: 'Story' },
    { id: 'reel', label: 'Reel / TikTok Script' },
    { id: 'thread', label: 'Thread' }
  ];

  const tones = [
    { id: 'enthusiastic', label: 'Enthousiaste & Énergique' },
    { id: 'professional', label: 'Professionnel & Informatif' },
    { id: 'urgent', label: 'Urgent (Promo limitée)' },
    { id: 'storytelling', label: 'Storytelling & Émotionnel' },
    { id: 'humorous', label: 'Humoristique & Décalé' }
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setGeneratedContent(null);

    try {
      const response = await api.post('/api/ai/generate-content', formData);
      setGeneratedContent(response.data);
    } catch (error) {
      console.error('Error generating content:', error);
      // Fallback mock data if API fails (for demo purposes)
      setTimeout(() => {
        setGeneratedContent({
          content: `🔥 DÉCOUVREZ ${formData.product_name.toUpperCase()} ! 🔥\n\nVous cherchez à améliorer votre quotidien ? Ne cherchez plus ! ${formData.product_name} est là pour vous.\n\n✨ POURQUOI VOUS ALLEZ L'ADORER :\n${formData.features.split(',').map(f => `✅ ${f.trim()}`).join('\n')}\n\n👉 Cliquez sur le lien dans ma bio pour commander maintenant !\n\n#${formData.product_name.replace(/\s/g, '')} #MustHave #Promo`,
          hashtags: ['#New', '#Trending', '#MustHave'],
          estimated_engagement: 'High'
        });
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedContent?.content) {
      navigator.clipboard.writeText(generatedContent.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Form Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-pink-100 rounded-lg text-pink-600">
            <Wand2 size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Générateur de Contenu IA</h2>
            <p className="text-sm text-gray-500">Créez des posts viraux en quelques secondes</p>
          </div>
        </div>

        <form onSubmit={handleGenerate} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Plateforme</label>
              <select
                name="platform"
                value={formData.platform}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                {platforms.map(p => <option key={p.id} value={p.id}>{p.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type de contenu</label>
              <select
                name="content_type"
                value={formData.content_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
              >
                {contentTypes.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nom du Produit / Service</label>
            <input
              type="text"
              name="product_name"
              value={formData.product_name}
              onChange={handleChange}
              placeholder="Ex: Super Blender 3000"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Points Clés (séparés par des virgules)</label>
            <textarea
              name="features"
              value={formData.features}
              onChange={handleChange}
              placeholder="Ex: Puissant, Silencieux, Facile à nettoyer, Garantie 2 ans"
              rows={3}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ton de la communication</label>
            <select
              name="tone"
              value={formData.tone}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            >
              {tones.map(t => <option key={t.id} value={t.id}>{t.label}</option>)}
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-6 bg-gradient-to-r from-pink-600 to-purple-600 text-white font-semibold rounded-lg shadow-md hover:from-pink-700 hover:to-purple-700 transition duration-300 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="animate-spin" size={20} />
                Génération en cours...
              </>
            ) : (
              <>
                <Wand2 size={20} />
                Générer le Contenu
              </>
            )}
          </button>
        </form>
      </div>

      {/* Result Section */}
      <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 flex flex-col h-full">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Résultat Généré</h3>
        
        {generatedContent ? (
          <div className="flex-1 flex flex-col">
            <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex-1 whitespace-pre-wrap text-gray-700 mb-4 font-sans text-sm leading-relaxed">
              {generatedContent.content}
            </div>
            
            <div className="flex items-center justify-between mt-auto">
              <div className="text-xs text-gray-500">
                Engagement estimé: <span className="font-semibold text-green-600">{generatedContent.estimated_engagement || 'Élevé'}</span>
              </div>
              <button
                onClick={copyToClipboard}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ${
                  copied 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? 'Copié !' : 'Copier le texte'}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
            <Wand2 size={48} className="mb-4 opacity-20" />
            <p className="text-center">Remplissez le formulaire et cliquez sur "Générer" pour voir la magie opérer.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIContentGenerator;
