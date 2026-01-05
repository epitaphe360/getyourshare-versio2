import React, { useEffect, useState } from 'react';
import Card from '../common/Card';
import Button from '../common/Button';
import { Copy, TrendingUp, MousePointer, DollarSign } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-toastify';

const AffiliateLinksTable = () => {
  const [links, setLinks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLinks();
  }, []);

  const fetchLinks = async () => {
    try {
      const response = await axios.get('/api/commercial/tracking/links');
      
      if (response.data.success) {
        setLinks(response.data.data.links);
        setStats(response.data.data.stats);
      }
    } catch (error) {
      console.error('Error fetching links:', error);
      toast.error("Erreur lors du chargement des liens");
    } finally {
      setLoading(false);
    }
  };

  const copyLink = (url) => {
    navigator.clipboard.writeText(url);
    toast.info("Lien copié !");
  };

  if (loading) {
    return <div className="p-4 text-center">Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats globales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MousePointer className="w-4 h-4" />
            Clics totaux
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.total_clicks || 0}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <TrendingUp className="w-4 h-4" />
            Conversions
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.total_conversions || 0}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <TrendingUp className="w-4 h-4" />
            Taux de conversion
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.conversion_rate || 0}%
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <DollarSign className="w-4 h-4" />
            Commissions
          </div>
          <div className="text-2xl font-bold mt-1">
            {(stats.total_commission || 0).toFixed(2)} €
          </div>
        </Card>
      </div>

      {/* Table des liens */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4">Mes liens affiliés</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50">
              <tr>
                <th className="px-6 py-3">Code</th>
                <th className="px-6 py-3">Campagne</th>
                <th className="px-6 py-3 text-right">Clics</th>
                <th className="px-6 py-3 text-right">Conversions</th>
                <th className="px-6 py-3 text-right">Revenu</th>
                <th className="px-6 py-3 text-right">Commission</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {links.map((link) => (
                <tr key={link.id} className="bg-white border-b hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {link.unique_code}
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded border border-blue-400">
                      {link.campaign || 'Sans nom'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">{link.clicks}</td>
                  <td className="px-6 py-4 text-right">
                    <span className="font-semibold text-green-600">
                      {link.conversions}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {link.total_revenue.toFixed(2)} €
                  </td>
                  <td className="px-6 py-4 text-right font-semibold">
                    {link.commission_earned.toFixed(2)} €
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyLink(link.tracking_url)}
                      ariaLabel="Copier le lien"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {links.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Aucun lien affilié créé pour le moment
          </div>
        )}
      </Card>
    </div>
  );
};

export default AffiliateLinksTable;
