import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import {
  Search, Users, ShoppingBag, Package, Sparkles, Target,
  UserCheck, DollarSign, TrendingUp, FileText, Settings,
  Home, BarChart3
} from 'lucide-react';
import api from '../utils/api';
import './GlobalSearch.css';

/**
 * GlobalSearch - Barre de recherche globale (Cmd+K / Ctrl+K)
 *
 * Features SaaS Premium:
 * - Raccourci clavier universel (Cmd/Ctrl + K)
 * - Recherche cross-sections (users, products, services, etc.)
 * - Suggestions intelligentes
 * - Navigation rapide
 * - Historique de recherche
 */
const GlobalSearch = () => {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [results, setResults] = useState({
    users: [],
    products: [],
    services: [],
    merchants: [],
    subscriptions: [],
    registrations: []
  });
  const [loading, setLoading] = useState(false);

  // Navigation rapide
  const quickActions = [
    { id: 'dashboard', label: 'Tableau de Bord', icon: Home, path: '/admin/dashboard', category: 'Navigation' },
    { id: 'overview', label: 'Vue d\'ensemble', icon: BarChart3, path: '/admin/dashboard?tab=overview', category: 'Navigation' },
    { id: 'users', label: 'Utilisateurs', icon: Users, path: '/admin/dashboard?tab=users', category: 'Navigation' },
    { id: 'merchants', label: 'Annonceurs', icon: ShoppingBag, path: '/admin/dashboard?tab=merchants', category: 'Navigation' },
    { id: 'products', label: 'Produits', icon: Package, path: '/admin/dashboard?tab=products', category: 'Navigation' },
    { id: 'services', label: 'Services', icon: Sparkles, path: '/admin/dashboard?tab=services', category: 'Navigation' },
    { id: 'subscriptions', label: 'Abonnements', icon: Target, path: '/admin/dashboard?tab=subscriptions', category: 'Navigation' },
    { id: 'registrations', label: 'Inscriptions', icon: UserCheck, path: '/admin/dashboard?tab=registrations', category: 'Navigation' },
    { id: 'finance', label: 'Finances', icon: DollarSign, path: '/admin/dashboard?tab=finance', category: 'Navigation' },
    { id: 'analytics', label: 'Analytiques', icon: TrendingUp, path: '/admin/dashboard?tab=analytics', category: 'Navigation' },
    { id: 'settings', label: 'Paramètres', icon: Settings, path: '/settings', category: 'Système' }
  ];

  // Raccourci clavier Cmd+K / Ctrl+K
  useEffect(() => {
    const down = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  // Recherche avec debounce
  useEffect(() => {
    if (!search || search.length < 2) {
      setResults({
        users: [],
        products: [],
        services: [],
        merchants: [],
        subscriptions: [],
        registrations: []
      });
      return;
    }

    const debounce = setTimeout(() => {
      performSearch(search);
    }, 300);

    return () => clearTimeout(debounce);
  }, [search]);

  const performSearch = useCallback(async (query) => {
    setLoading(true);
    try {
      // Recherche parallèle dans toutes les sections
      const [usersRes, productsRes, servicesRes, merchantsRes] = await Promise.allSettled([
        api.get(`/api/admin/users?search=${query}&limit=5`),
        api.get(`/api/products?search=${query}&limit=5`),
        api.get(`/api/services?search=${query}&limit=5`),
        api.get(`/api/admin/users?role=merchant&search=${query}&limit=5`)
      ]);

      setResults({
        users: usersRes.status === 'fulfilled' ? (usersRes.value.data.users || usersRes.value.data || []).slice(0, 5) : [],
        products: productsRes.status === 'fulfilled' ? (productsRes.value.data.products || productsRes.value.data || []).slice(0, 5) : [],
        services: servicesRes.status === 'fulfilled' ? (servicesRes.value.data.services || servicesRes.value.data || []).slice(0, 5) : [],
        merchants: merchantsRes.status === 'fulfilled' ? (merchantsRes.value.data.users || merchantsRes.value.data || []).slice(0, 5) : [],
        subscriptions: [],
        registrations: []
      });
    } catch (error) {
      console.error('Erreur recherche:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSelect = useCallback((path) => {
    setOpen(false);
    setSearch('');
    navigate(path);
  }, [navigate]);

  if (!open) return null;

  return (
    <div className="global-search-overlay" onClick={() => setOpen(false)}>
      <div className="global-search-container" onClick={(e) => e.stopPropagation()}>
        <Command className="global-search-command">
          <div className="global-search-header">
            <Search className="global-search-icon" size={20} />
            <Command.Input
              placeholder="Rechercher... (Utilisateurs, Produits, Services, etc.)"
              value={search}
              onValueChange={setSearch}
              className="global-search-input"
            />
            <kbd className="global-search-kbd">Esc</kbd>
          </div>

          <Command.List className="global-search-list">
            <Command.Empty className="global-search-empty">
              {loading ? (
                <div className="global-search-loading">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div>
                  <p className="mt-2 text-sm">Recherche en cours...</p>
                </div>
              ) : (
                <p>Aucun résultat trouvé</p>
              )}
            </Command.Empty>

            {/* Navigation Rapide */}
            {!search && (
              <Command.Group heading="Navigation Rapide" className="global-search-group">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <Command.Item
                      key={action.id}
                      onSelect={() => handleSelect(action.path)}
                      className="global-search-item"
                    >
                      <Icon size={18} className="global-search-item-icon" />
                      <span>{action.label}</span>
                      <span className="global-search-item-badge">{action.category}</span>
                    </Command.Item>
                  );
                })}
              </Command.Group>
            )}

            {/* Résultats Utilisateurs */}
            {results.users.length > 0 && (
              <Command.Group heading="Utilisateurs" className="global-search-group">
                {results.users.map((user) => (
                  <Command.Item
                    key={`user-${user.id}`}
                    onSelect={() => handleSelect(`/admin/users/${user.id}`)}
                    className="global-search-item"
                  >
                    <Users size={18} className="global-search-item-icon" />
                    <div className="flex-1">
                      <p className="font-medium">{user.email}</p>
                      <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* Résultats Produits */}
            {results.products.length > 0 && (
              <Command.Group heading="Produits" className="global-search-group">
                {results.products.map((product) => (
                  <Command.Item
                    key={`product-${product.id}`}
                    onSelect={() => handleSelect(`/admin/products/${product.id}`)}
                    className="global-search-item"
                  >
                    <Package size={18} className="global-search-item-icon" />
                    <div className="flex-1">
                      <p className="font-medium">{product.name}</p>
                      <p className="text-xs text-gray-500">{product.price} €</p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* Résultats Services */}
            {results.services.length > 0 && (
              <Command.Group heading="Services" className="global-search-group">
                {results.services.map((service) => (
                  <Command.Item
                    key={`service-${service.id}`}
                    onSelect={() => handleSelect(`/admin/services/${service.id}`)}
                    className="global-search-item"
                  >
                    <Sparkles size={18} className="global-search-item-icon" />
                    <div className="flex-1">
                      <p className="font-medium">{service.title || service.name}</p>
                      <p className="text-xs text-gray-500">{service.budget_total} € budget</p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* Résultats Merchants */}
            {results.merchants.length > 0 && (
              <Command.Group heading="Annonceurs" className="global-search-group">
                {results.merchants.map((merchant) => (
                  <Command.Item
                    key={`merchant-${merchant.id}`}
                    onSelect={() => handleSelect(`/admin/merchants/${merchant.id}`)}
                    className="global-search-item"
                  >
                    <ShoppingBag size={18} className="global-search-item-icon" />
                    <div className="flex-1">
                      <p className="font-medium">{merchant.company_name || merchant.email}</p>
                      <p className="text-xs text-gray-500">{merchant.email}</p>
                    </div>
                  </Command.Item>
                ))}
              </Command.Group>
            )}
          </Command.List>

          <div className="global-search-footer">
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <kbd className="global-search-kbd-small">↑↓</kbd>
                <span>Naviguer</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="global-search-kbd-small">↵</kbd>
                <span>Sélectionner</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="global-search-kbd-small">Esc</kbd>
                <span>Fermer</span>
              </div>
            </div>
          </div>
        </Command>
      </div>
    </div>
  );
};

export default GlobalSearch;
