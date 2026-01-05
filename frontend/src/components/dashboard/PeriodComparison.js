import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart, Line, BarChart, Bar, ComposedChart,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell
} from 'recharts';
import { TrendingUp, TrendingDown, Calendar } from 'lucide-react';

/**
 * Composant pour comparer les performances entre deux périodes
 * Affiche: graphiques side-by-side, % d'évolution, prévisions
 */

const PeriodComparison = ({ data = [], currentPeriod = 'month' }) => {
  const [selectedPeriod, setSelectedPeriod] = useState(currentPeriod);
  const [compareType, setCompareType] = useState('month'); // month, quarter, year

  // =====================================================
  // CALCULS
  // =====================================================

  const comparison = useMemo(() => {
    if (!data || data.length === 0) return null;

    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth();

    // Données actuelles (période N)
    const currentPeriodData = data.filter(d => {
      const date = new Date(d.date);
      if (compareType === 'month') {
        return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
      } else if (compareType === 'quarter') {
        const quarter = Math.floor(date.getMonth() / 3);
        const currentQuarter = Math.floor(currentMonth / 3);
        return quarter === currentQuarter && date.getFullYear() === currentYear;
      } else {
        return date.getFullYear() === currentYear;
      }
    });

    // Données précédentes (période N-1)
    let previousPeriodData = [];
    if (compareType === 'month') {
      const prevMonth = currentMonth === 0 ? 11 : currentMonth - 1;
      const prevYear = currentMonth === 0 ? currentYear - 1 : currentYear;
      previousPeriodData = data.filter(d => {
        const date = new Date(d.date);
        return date.getMonth() === prevMonth && date.getFullYear() === prevYear;
      });
    } else if (compareType === 'quarter') {
      const currentQuarter = Math.floor(currentMonth / 3);
      const prevQuarter = currentQuarter === 0 ? 3 : currentQuarter - 1;
      const prevYear = currentQuarter === 0 ? currentYear - 1 : currentYear;
      previousPeriodData = data.filter(d => {
        const date = new Date(d.date);
        const quarter = Math.floor(date.getMonth() / 3);
        return quarter === prevQuarter && date.getFullYear() === prevYear;
      });
    } else {
      previousPeriodData = data.filter(d => {
        const date = new Date(d.date);
        return date.getFullYear() === currentYear - 1;
      });
    }

    // Calculs KPIs
    const currentRevenue = currentPeriodData.reduce((sum, d) => sum + (d.revenue || 0), 0);
    const previousRevenue = previousPeriodData.reduce((sum, d) => sum + (d.revenue || 0), 0);
    const revenueEvolution = previousRevenue === 0 ? 0 : ((currentRevenue - previousRevenue) / previousRevenue) * 100;

    const currentLeads = currentPeriodData.reduce((sum, d) => sum + (d.leads || 0), 0);
    const previousLeads = previousPeriodData.reduce((sum, d) => sum + (d.leads || 0), 0);
    const leadsEvolution = previousLeads === 0 ? 0 : ((currentLeads - previousLeads) / previousLeads) * 100;

    const currentConversions = currentPeriodData.filter(d => d.converted).length;
    const previousConversions = previousPeriodData.filter(d => d.converted).length;
    const conversionEvolution = previousConversions === 0 ? 0 : ((currentConversions - previousConversions) / previousConversions) * 100;

    // Prévisions
    const daysInCurrentPeriod = compareType === 'month' ? 30 : compareType === 'quarter' ? 90 : 365;
    const daysElapsed = compareType === 'month' ? today.getDate() : 
                        compareType === 'quarter' ? today.getDate() + (Math.floor(today.getMonth() / 3) * 30) : 
                        today.getDate();
    
    const dailyRevenue = currentRevenue / Math.max(daysElapsed, 1);
    const projectedRevenue = dailyRevenue * daysInCurrentPeriod;
    const remainingDays = daysInCurrentPeriod - daysElapsed;
    const remainingRevenue = dailyRevenue * remainingDays;

    return {
      current: {
        revenue: currentRevenue,
        leads: currentLeads,
        conversions: currentConversions,
        data: currentPeriodData
      },
      previous: {
        revenue: previousRevenue,
        leads: previousLeads,
        conversions: previousConversions,
        data: previousPeriodData
      },
      evolution: {
        revenue: revenueEvolution,
        leads: leadsEvolution,
        conversions: conversionEvolution
      },
      forecast: {
        projected: projectedRevenue,
        remaining: remainingRevenue,
        daysRemaining: remainingDays,
        onTrack: projectedRevenue >= previousRevenue
      }
    };
  }, [data, compareType]);

  if (!comparison) {
    return (
      <div className="text-center py-12 text-gray-500">
        Pas de données pour comparer
      </div>
    );
  }

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <div className="space-y-6">
      {/* Contrôles */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-sm p-4 flex flex-wrap gap-4 items-center"
      >
        <div className="flex items-center gap-2">
          <Calendar size={18} className="text-purple-600" />
          <select
            value={compareType}
            onChange={(e) => setCompareType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="month">Comparer Mois</option>
            <option value="quarter">Comparer Trimestre</option>
            <option value="year">Comparer Année</option>
          </select>
        </div>
      </motion.div>

      {/* KPIs de Comparaison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Revenue */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 font-medium">Revenu Total</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {comparison.current.revenue.toLocaleString('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                  maximumFractionDigits: 0
                })}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${comparison.evolution.revenue >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              {comparison.evolution.revenue >= 0 ? (
                <TrendingUp className="text-green-600" size={24} />
              ) : (
                <TrendingDown className="text-red-600" size={24} />
              )}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-600">
              Précédent: {comparison.previous.revenue.toLocaleString('fr-FR', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </p>
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${
              comparison.evolution.revenue >= 0 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {comparison.evolution.revenue >= 0 ? '+' : ''}{comparison.evolution.revenue.toFixed(1)}%
            </div>
          </div>
        </motion.div>

        {/* Leads */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 font-medium">Leads Générés</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {comparison.current.leads}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${comparison.evolution.leads >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              {comparison.evolution.leads >= 0 ? (
                <TrendingUp className="text-green-600" size={24} />
              ) : (
                <TrendingDown className="text-red-600" size={24} />
              )}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-600">
              Précédent: {comparison.previous.leads} leads
            </p>
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${
              comparison.evolution.leads >= 0 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {comparison.evolution.leads >= 0 ? '+' : ''}{comparison.evolution.leads.toFixed(1)}%
            </div>
          </div>
        </motion.div>

        {/* Conversions */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm text-gray-600 font-medium">Conversions</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {comparison.current.conversions}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${comparison.evolution.conversions >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              {comparison.evolution.conversions >= 0 ? (
                <TrendingUp className="text-green-600" size={24} />
              ) : (
                <TrendingDown className="text-red-600" size={24} />
              )}
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-gray-600">
              Précédent: {comparison.previous.conversions} conversions
            </p>
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${
              comparison.evolution.conversions >= 0 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {comparison.evolution.conversions >= 0 ? '+' : ''}{comparison.evolution.conversions.toFixed(1)}%
            </div>
          </div>
        </motion.div>
      </div>

      {/* Graphiques Comparatifs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-lg shadow-sm p-6"
      >
        <h3 className="text-lg font-bold text-gray-900 mb-4">📊 Tendances Comparées</h3>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={[
            {
              name: 'Période actuelle',
              revenue: comparison.current.revenue,
              leads: comparison.current.leads
            },
            {
              name: 'Période précédente',
              revenue: comparison.previous.revenue,
              leads: comparison.previous.leads
            }
          ]}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis yAxisId="left" label={{ value: 'Revenue (€)', angle: -90, position: 'insideLeft' }} />
            <YAxis yAxisId="right" orientation="right" label={{ value: 'Leads', angle: 90, position: 'insideRight' }} />
            <Tooltip />
            <Legend />
            <Bar yAxisId="left" dataKey="revenue" fill="#8b5cf6" name="Revenue (€)" />
            <Bar yAxisId="right" dataKey="leads" fill="#3b82f6" name="Leads" />
          </ComposedChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Prévisions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className={`rounded-lg p-6 border-2 ${
          comparison.forecast.onTrack
            ? 'bg-green-50 border-green-300'
            : 'bg-orange-50 border-orange-300'
        }`}
      >
        <h3 className="text-lg font-bold text-gray-900 mb-4">🎯 Prévisions Fin de Période</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Revenue Projeté</p>
            <p className="text-2xl font-bold text-gray-900">
              {comparison.forecast.projected.toLocaleString('fr-FR', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {comparison.forecast.onTrack ? '✅ En avance' : '⚠️ En retard'} par rapport à la période précédente
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Revenue Restante</p>
            <p className="text-2xl font-bold text-gray-900">
              {comparison.forecast.remaining.toLocaleString('fr-FR', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              à générer en {comparison.forecast.daysRemaining} jours
            </p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Rythme Quotidien Requis</p>
            <p className="text-2xl font-bold text-gray-900">
              {(comparison.forecast.remaining / Math.max(comparison.forecast.daysRemaining, 1)).toLocaleString('fr-FR', {
                style: 'currency',
                currency: 'EUR',
                maximumFractionDigits: 0
              })}
            </p>
            <p className="text-xs text-gray-500 mt-1">par jour</p>
          </div>
        </div>

        {/* Barre de progression */}
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-700 mb-2">Progression</p>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min((comparison.current.revenue / comparison.previous.revenue) * 100, 100)}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-full ${comparison.forecast.onTrack ? 'bg-green-500' : 'bg-orange-500'}`}
            />
          </div>
          <p className="text-xs text-gray-600 mt-1">
            {((comparison.current.revenue / comparison.previous.revenue) * 100).toFixed(0)}% vs période précédente
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default PeriodComparison;
