# 🎨 Composants UI - Système de Tracking Commercial

## 📋 Vue d'ensemble

Composants React à ajouter dans le dashboard commercial pour gérer les liens affiliés et le tracking des ventes.

---

## 🆕 Nouveaux Composants

### 1. Composant: Générateur de Liens Affiliés

**Fichier:** `app/dashboard/commercial/components/AffiliateLinksGenerator.tsx`

```tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Copy, ExternalLink, Link as LinkIcon } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface GeneratedLink {
  tracking_link_id: string;
  unique_code: string;
  full_url: string;
  short_url: string;
}

export default function AffiliateLinksGenerator() {
  const [campaign, setCampaign] = useState('');
  const [generatedLink, setGeneratedLink] = useState<GeneratedLink | null>(null);
  const [loading, setLoading] = useState(false);

  const generateLink = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/commercial/tracking/generate-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ campaign })
      });

      const data = await response.json();
      
      if (data.success) {
        setGeneratedLink(data.data);
        toast({
          title: "✅ Lien généré !",
          description: "Votre lien affilié est prêt à être utilisé"
        });
      }
    } catch (error) {
      toast({
        title: "❌ Erreur",
        description: "Impossible de générer le lien",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "📋 Copié !",
      description: "Le lien a été copié dans le presse-papiers"
    });
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <LinkIcon className="w-5 h-5" />
        Générer un lien affilié
      </h3>

      <div className="space-y-4">
        <div>
          <Label htmlFor="campaign">Nom de la campagne (optionnel)</Label>
          <Input
            id="campaign"
            placeholder="black_friday_2024"
            value={campaign}
            onChange={(e) => setCampaign(e.target.value)}
          />
        </div>

        <Button 
          onClick={generateLink} 
          disabled={loading}
          className="w-full"
        >
          {loading ? 'Génération...' : '🔗 Générer le lien'}
        </Button>

        {generatedLink && (
          <div className="space-y-3 mt-6 pt-6 border-t">
            <div>
              <Label>Code unique</Label>
              <div className="flex gap-2 mt-1">
                <Input 
                  value={generatedLink.unique_code} 
                  readOnly 
                  className="font-mono"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => copyToClipboard(generatedLink.unique_code)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div>
              <Label>Lien complet</Label>
              <div className="flex gap-2 mt-1">
                <Input 
                  value={generatedLink.full_url} 
                  readOnly 
                  className="font-mono text-xs"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => copyToClipboard(generatedLink.full_url)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => window.open(generatedLink.full_url, '_blank')}
                >
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div>
              <Label>Lien court</Label>
              <div className="flex gap-2 mt-1">
                <Input 
                  value={generatedLink.short_url} 
                  readOnly 
                  className="font-mono"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => copyToClipboard(generatedLink.short_url)}
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
}
```

---

### 2. Composant: Liste des Liens Affiliés

**Fichier:** `app/dashboard/commercial/components/AffiliateLinksTable.tsx`

```tsx
'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Copy, TrendingUp, MousePointer, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface AffiliateLink {
  id: string;
  unique_code: string;
  campaign: string;
  clicks: number;
  conversions: number;
  total_revenue: number;
  commission_earned: number;
  created_at: string;
  tracking_url: string;
}

export default function AffiliateLinksTable() {
  const [links, setLinks] = useState<AffiliateLink[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLinks();
  }, []);

  const fetchLinks = async () => {
    try {
      const response = await fetch('/api/commercial/tracking/links');
      const data = await response.json();
      
      if (data.success) {
        setLinks(data.data.links);
        setStats(data.data.stats);
      }
    } catch (error) {
      console.error('Error fetching links:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyLink = (url: string) => {
    navigator.clipboard.writeText(url);
  };

  if (loading) {
    return <div>Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats globales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MousePointer className="w-4 h-4" />
            Clics totaux
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.total_clicks || 0}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <TrendingUp className="w-4 h-4" />
            Conversions
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.total_conversions || 0}
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <TrendingUp className="w-4 h-4" />
            Taux de conversion
          </div>
          <div className="text-2xl font-bold mt-1">
            {stats.conversion_rate || 0}%
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
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
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3">Code</th>
                <th className="text-left p-3">Campagne</th>
                <th className="text-right p-3">Clics</th>
                <th className="text-right p-3">Conversions</th>
                <th className="text-right p-3">Revenu</th>
                <th className="text-right p-3">Commission</th>
                <th className="text-right p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {links.map((link) => (
                <tr key={link.id} className="border-b hover:bg-muted/50">
                  <td className="p-3">
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {link.unique_code}
                    </code>
                  </td>
                  <td className="p-3">
                    <Badge variant="outline">{link.campaign || 'Sans nom'}</Badge>
                  </td>
                  <td className="p-3 text-right">{link.clicks}</td>
                  <td className="p-3 text-right">
                    <span className="font-semibold text-green-600">
                      {link.conversions}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    {link.total_revenue.toFixed(2)} €
                  </td>
                  <td className="p-3 text-right font-semibold">
                    {link.commission_earned.toFixed(2)} €
                  </td>
                  <td className="p-3 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyLink(link.tracking_url)}
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
          <div className="text-center py-8 text-muted-foreground">
            Aucun lien affilié créé pour le moment
          </div>
        )}
      </Card>
    </div>
  );
}
```

---

### 3. Composant: Tableau des Commissions

**Fichier:** `app/dashboard/commercial/components/CommissionsTable.tsx`

```tsx
'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Clock, CheckCircle, XCircle } from 'lucide-react';

interface Commission {
  id: string;
  user_email: string;
  subscription_amount: number;
  commission_percentage: number;
  commission_amount: number;
  status: 'pending' | 'approved' | 'paid' | 'cancelled';
  attribution_type: string;
  created_at: string;
  paid_at: string | null;
}

export default function CommissionsTable() {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [summary, setSummary] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCommissions();
  }, []);

  const fetchCommissions = async () => {
    try {
      const response = await fetch('/api/commercial/commissions');
      const data = await response.json();
      
      if (data.success) {
        setCommissions(data.data.commissions);
        setSummary(data.data.summary);
      }
    } catch (error) {
      console.error('Error fetching commissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: Commission['status']) => {
    const variants = {
      pending: { variant: 'secondary' as const, icon: Clock, label: 'En attente' },
      approved: { variant: 'default' as const, icon: CheckCircle, label: 'Approuvée' },
      paid: { variant: 'default' as const, icon: DollarSign, label: 'Payée' },
      cancelled: { variant: 'destructive' as const, icon: XCircle, label: 'Annulée' }
    };

    const config = variants[status];
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  if (loading) {
    return <div>Chargement...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Résumé commissions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">En attente</div>
          <div className="text-2xl font-bold text-yellow-600">
            {summary.total_pending?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {summary.count_pending || 0} ventes
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Approuvées</div>
          <div className="text-2xl font-bold text-green-600">
            {summary.total_approved?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {summary.count_approved || 0} ventes
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Payées</div>
          <div className="text-2xl font-bold text-blue-600">
            {summary.total_paid?.toFixed(2) || '0.00'} €
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {summary.count_paid || 0} ventes
          </div>
        </Card>
      </div>

      {/* Table commissions */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4">Historique des commissions</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-3">Date</th>
                <th className="text-left p-3">Client</th>
                <th className="text-right p-3">Montant vente</th>
                <th className="text-right p-3">Taux</th>
                <th className="text-right p-3">Commission</th>
                <th className="text-left p-3">Statut</th>
                <th className="text-left p-3">Attribution</th>
              </tr>
            </thead>
            <tbody>
              {commissions.map((commission) => (
                <tr key={commission.id} className="border-b hover:bg-muted/50">
                  <td className="p-3 text-sm">
                    {new Date(commission.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="p-3 text-sm">{commission.user_email}</td>
                  <td className="p-3 text-right">
                    {commission.subscription_amount.toFixed(2)} €
                  </td>
                  <td className="p-3 text-right">
                    {commission.commission_percentage}%
                  </td>
                  <td className="p-3 text-right font-semibold">
                    {commission.commission_amount.toFixed(2)} €
                  </td>
                  <td className="p-3">
                    {getStatusBadge(commission.status)}
                  </td>
                  <td className="p-3 text-xs text-muted-foreground">
                    {commission.attribution_type}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {commissions.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            Aucune commission enregistrée
          </div>
        )}
      </Card>
    </div>
  );
}
```

---

### 4. Page Dashboard - Onglet Tracking

**Fichier:** `app/dashboard/commercial/tracking/page.tsx`

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AffiliateLinksGenerator from '../components/AffiliateLinksGenerator';
import AffiliateLinksTable from '../components/AffiliateLinksTable';
import CommissionsTable from '../components/CommissionsTable';

export default function CommercialTrackingPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">🔗 Tracking & Commissions</h1>
        <p className="text-muted-foreground mt-2">
          Générez des liens affiliés et suivez vos commissions en temps réel
        </p>
      </div>

      <Tabs defaultValue="links" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generator">Générer</TabsTrigger>
          <TabsTrigger value="links">Mes liens</TabsTrigger>
          <TabsTrigger value="commissions">Commissions</TabsTrigger>
        </TabsList>

        <TabsContent value="generator" className="mt-6">
          <AffiliateLinksGenerator />
        </TabsContent>

        <TabsContent value="links" className="mt-6">
          <AffiliateLinksTable />
        </TabsContent>

        <TabsContent value="commissions" className="mt-6">
          <CommissionsTable />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## 🔧 Intégration dans le Dashboard

### Ajouter le lien dans la navigation

**Fichier:** `app/dashboard/commercial/layout.tsx`

```tsx
<nav>
  {/* ... autres liens ... */}
  <Link href="/dashboard/commercial/tracking">
    <Button variant="ghost">
      🔗 Tracking & Commissions
    </Button>
  </Link>
</nav>
```

---

## 📝 Notes d'implémentation

1. **Composants UI:**
   - Utilise shadcn/ui pour cohérence visuelle
   - Responsive design (mobile-first)
   - Dark mode compatible

2. **State Management:**
   - useState pour état local
   - useEffect pour fetch initial
   - Toast notifications pour feedback

3. **Performance:**
   - Lazy loading des tables
   - Pagination côté serveur
   - Cache avec SWR (optionnel)

4. **UX:**
   - Copy to clipboard avec feedback
   - Loading states clairs
   - Messages d'erreur explicites
   - Filtres et tri dans tables

---

## ✅ Checklist d'intégration

- [ ] Créer dossier `app/dashboard/commercial/components/`
- [ ] Ajouter `AffiliateLinksGenerator.tsx`
- [ ] Ajouter `AffiliateLinksTable.tsx`
- [ ] Ajouter `CommissionsTable.tsx`
- [ ] Créer page `tracking/page.tsx`
- [ ] Ajouter lien dans navigation
- [ ] Tester responsive design
- [ ] Vérifier dark mode
- [ ] Valider toasts/notifications
- [ ] Tester copie liens
- [ ] Déployer

---

**Prochaine étape:** Voir `TEST_PLAN_TRACKING.md` pour le plan de tests complet.
