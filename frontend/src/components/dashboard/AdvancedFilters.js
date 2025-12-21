import React, { useState, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Search, Filter, X, Heart, Clock, DollarSign,
  Thermometer, Calendar, Save, Trash2, Download
} from 'lucide-react';
import { toast } from 'react-toastify';

/**
 * Composant pour filtres avancés des leads
 * Includes: recherche, filtres par date/statut/température/valeur
 * Sauvegarde des filtres favoris dans localStorage
 */

const AdvancedFilters = ({ 
  data = [], 
  onFilter, 
  onExport,
  filterableFields = {
    search: ['name', 'email', 'company'],
    status: ['nouveau', 'qualifie', 'en_negociation', 'conclu'],
    temperature: ['froid', 'tiede', 'chaud'],
    minValue: 0,
    maxValue: 100000
  }
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: [],
    temperature: [],
    minValue: 0,
    maxValue: filterableFields.maxValue || 100000,
    dateFrom: '',
    dateTo: '',
    sortBy: 'recent'
  });

  const [savedFilters, setSavedFilters] = useState(() => {
    const saved = localStorage.getItem('commercialFilters');
    return saved ? JSON.parse(saved) : [];
  });

  const [showSaveModal, setShowSaveModal] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  // =====================================================
  // FILTRAGE & RECHERCHE
  // =====================================================

  const filteredData = useMemo(() => {
    let result = [...data];

    // Recherche textuelle
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(item => {
        const searchableText = `${item.first_name || ''} ${item.last_name || ''} ${item.email || ''} ${item.company || ''}`.toLowerCase();
        return searchableText.includes(term);
      });
    }

    // Filtre statut
    if (filters.status.length > 0) {
      result = result.filter(item => filters.status.includes(item.status));
    }

    // Filtre température
    if (filters.temperature.length > 0) {
      result = result.filter(item => filters.temperature.includes(item.temperature));
    }

    // Filtre valeur estimée
    result = result.filter(item => {
      const value = item.estimated_value || 0;
      return value >= filters.minValue && value <= filters.maxValue;
    });

    // Filtre dates
    if (filters.dateFrom) {
      const fromDate = new Date(filters.dateFrom);
      result = result.filter(item => new Date(item.created_at || '') >= fromDate);
    }
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo);
      toDate.setHours(23, 59, 59, 999);
      result = result.filter(item => new Date(item.created_at || '') <= toDate);
    }

    // Tri
    result.sort((a, b) => {
      switch (filters.sortBy) {
        case 'recent':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'value_high':
          return (b.estimated_value || 0) - (a.estimated_value || 0);
        case 'value_low':
          return (a.estimated_value || 0) - (b.estimated_value || 0);
        case 'name':
          return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
        default:
          return 0;
      }
    });

    return result;
  }, [data, searchTerm, filters]);

  // =====================================================
  // HANDLERS
  // =====================================================

  const handleStatusChange = (status) => {
    setFilters(prev => ({
      ...prev,
      status: prev.status.includes(status)
        ? prev.status.filter(s => s !== status)
        : [...prev.status, status]
    }));
  };

  const handleTemperatureChange = (temp) => {
    setFilters(prev => ({
      ...prev,
      temperature: prev.temperature.includes(temp)
        ? prev.temperature.filter(t => t !== temp)
        : [...prev.temperature, temp]
    }));
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setFilters({
      status: [],
      temperature: [],
      minValue: 0,
      maxValue: filterableFields.maxValue || 100000,
      dateFrom: '',
      dateTo: '',
      sortBy: 'recent'
    });
    toast.info('Filtres réinitialisés');
  };

  const handleSaveFilter = () => {
    if (!filterName.trim()) {
      toast.error('Nom du filtre obligatoire');
      return;
    }

    const newFilter = {
      id: Date.now(),
      name: filterName,
      filters: { ...filters, searchTerm },
      count: filteredData.length,
      createdAt: new Date().toLocaleDateString()
    };

    const updated = [...savedFilters, newFilter];
    setSavedFilters(updated);
    localStorage.setItem('commercialFilters', JSON.stringify(updated));
    setFilterName('');
    setShowSaveModal(false);
    toast.success('Filtre sauvegardé !');
  };

  const handleLoadFilter = (filter) => {
    setSearchTerm(filter.searchTerm || '');
    setFilters(filter.filters);
    toast.info(`Filtre "${filter.name}" chargé`);
  };

  const handleDeleteSavedFilter = (id) => {
    const updated = savedFilters.filter(f => f.id !== id);
    setSavedFilters(updated);
    localStorage.setItem('commercialFilters', JSON.stringify(updated));
    toast.success('Filtre supprimé');
  };

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm p-4 mb-6"
    >
      {/* Barre de recherche principale */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="🔍 Chercher par nom, email, entreprise..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition flex items-center gap-2 font-medium"
        >
          <Filter size={18} />
          Filtres Avancés {isExpanded ? '▼' : '▶'}
          {(filters.status.length > 0 || filters.temperature.length > 0 || filters.dateFrom) && (
            <span className="ml-2 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs">
              {filters.status.length + filters.temperature.length}
            </span>
          )}
        </button>

        <button
          onClick={() => onExport?.(filteredData)}
          className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition flex items-center gap-2 font-medium"
        >
          <Download size={18} />
          Export
        </button>
      </div>

      {/* Filtres avancés (expandable) */}
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="border-t pt-4 space-y-4"
        >
          {/* Statut */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Statut</label>
            <div className="flex flex-wrap gap-2">
              {filterableFields.status.map(status => (
                <button
                  key={status}
                  onClick={() => handleStatusChange(status)}
                  className={`px-3 py-1 rounded-full text-sm transition ${
                    filters.status.includes(status)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {status === 'nouveau' && '🆕'}
                  {status === 'qualifie' && '✅'}
                  {status === 'en_negociation' && '🤝'}
                  {status === 'conclu' && '🎉'}
                  {' '}{status}
                </button>
              ))}
            </div>
          </div>

          {/* Température */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Température</label>
            <div className="flex flex-wrap gap-2">
              {filterableFields.temperature.map(temp => (
                <button
                  key={temp}
                  onClick={() => handleTemperatureChange(temp)}
                  className={`px-3 py-1 rounded-full text-sm transition ${
                    filters.temperature.includes(temp)
                      ? temp === 'chaud' ? 'bg-red-500 text-white' : temp === 'tiede' ? 'bg-yellow-500 text-white' : 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <Thermometer size={14} className="inline mr-1" />
                  {temp === 'chaud' ? '🔥' : temp === 'tiede' ? '☀️' : '❄️'} {temp}
                </button>
              ))}
            </div>
          </div>

          {/* Valeur estimée */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              <DollarSign className="inline mr-1" size={16} />
              Valeur estimée: {filters.minValue}€ - {filters.maxValue}€
            </label>
            <div className="flex gap-3">
              <input
                type="number"
                min="0"
                placeholder="Min"
                value={filters.minValue}
                onChange={(e) => setFilters(prev => ({ ...prev, minValue: parseInt(e.target.value) || 0 }))}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
              <input
                type="number"
                max="1000000"
                placeholder="Max"
                value={filters.maxValue}
                onChange={(e) => setFilters(prev => ({ ...prev, maxValue: parseInt(e.target.value) || 100000 }))}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Du</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Au</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          {/* Tri */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Tri</label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="recent">📅 Plus récent d'abord</option>
              <option value="oldest">📅 Plus ancien d'abord</option>
              <option value="value_high">💰 Valeur la plus élevée</option>
              <option value="value_low">💰 Valeur la plus basse</option>
              <option value="name">🔤 Nom (A-Z)</option>
            </select>
          </div>

          {/* Actions filtres */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={() => setShowSaveModal(true)}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition flex items-center justify-center gap-2 font-medium"
            >
              <Save size={16} />
              Sauvegarder ce filtre
            </button>
            <button
              onClick={handleClearFilters}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition flex items-center gap-2 font-medium"
            >
              <X size={16} />
              Réinitialiser
            </button>
          </div>
        </motion.div>
      )}

      {/* Résultats & Filtres sauvegardés */}
      <div className="flex items-center justify-between text-sm text-gray-600 pt-2">
        <span>
          <strong>{filteredData.length}</strong> résultat{filteredData.length !== 1 ? 's' : ''} 
          {data.length > 0 && ` sur ${data.length}`}
        </span>
        {savedFilters.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            {savedFilters.slice(0, 3).map(filter => (
              <button
                key={filter.id}
                onClick={() => handleLoadFilter(filter)}
                title={`${filter.count} résultats (${filter.createdAt})`}
                className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs hover:bg-indigo-200 transition flex items-center gap-1"
              >
                <Heart size={12} />
                {filter.name}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSavedFilter(filter.id);
                  }}
                  className="ml-1 hover:text-red-600"
                >
                  ✕
                </button>
              </button>
            ))}
            {savedFilters.length > 3 && (
              <span className="text-xs text-gray-500">+{savedFilters.length - 3}</span>
            )}
          </div>
        )}
      </div>

      {/* Modal Sauvegarde Filtre */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-bold text-gray-900 mb-4">Sauvegarder le filtre</h3>
            <input
              type="text"
              placeholder="Nom du filtre (ex: Leads chauds décembre)"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              autoFocus
              className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-purple-500"
              onKeyPress={(e) => e.key === 'Enter' && handleSaveFilter()}
            />
            <div className="flex gap-2">
              <button
                onClick={() => setShowSaveModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium"
              >
                Annuler
              </button>
              <button
                onClick={handleSaveFilter}
                className="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium"
              >
                Sauvegarder
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
};

export default AdvancedFilters;
