import React, { useState } from 'react';
import Button from '../common/Button';
import Card from '../common/Card';
import { Copy, ExternalLink, Link as LinkIcon } from 'lucide-react';
import { toast } from 'react-toastify';
import axios from 'axios';

const AffiliateLinksGenerator = () => {
  const [campaign, setCampaign] = useState('');
  const [generatedLink, setGeneratedLink] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateLink = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/commercial/tracking/generate-link', {
        campaign
      });

      if (response.data.success) {
        setGeneratedLink(response.data.data);
        toast.success("✅ Lien généré ! Votre lien affilié est prêt à être utilisé");
      }
    } catch (error) {
      console.error(error);
      toast.error("❌ Erreur: Impossible de générer le lien");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.info("📋 Copié ! Le lien a été copié dans le presse-papiers");
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <LinkIcon className="w-5 h-5" />
        Générer un lien affilié
      </h3>

      <div className="space-y-4">
        <div>
          <label htmlFor="campaign" className="block text-sm font-medium text-gray-700 mb-1">
            Nom de la campagne (optionnel)
          </label>
          <input
            id="campaign"
            type="text"
            placeholder="black_friday_2024"
            value={campaign}
            onChange={(e) => setCampaign(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <Button 
          onClick={generateLink} 
          disabled={loading}
          className="w-full"
          variant="primary"
        >
          {loading ? 'Génération...' : '🔗 Générer le lien'}
        </Button>

        {generatedLink && (
          <div className="space-y-3 mt-6 pt-6 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Code unique</label>
              <div className="flex gap-2 mt-1">
                <input 
                  value={generatedLink.unique_code} 
                  readOnly 
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md font-mono text-sm"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(generatedLink.unique_code)}
                  ariaLabel="Copier le code unique"
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lien complet</label>
              <div className="flex gap-2 mt-1">
                <input 
                  value={generatedLink.full_url} 
                  readOnly 
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md font-mono text-xs"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(generatedLink.full_url)}
                  ariaLabel="Copier le lien complet"
                >
                  <Copy className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(generatedLink.full_url, '_blank')}
                  ariaLabel="Ouvrir le lien"
                >
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lien court</label>
              <div className="flex gap-2 mt-1">
                <input 
                  value={generatedLink.short_url} 
                  readOnly 
                  className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md font-mono text-sm"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(generatedLink.short_url)}
                  ariaLabel="Copier le lien court"
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default AffiliateLinksGenerator;
