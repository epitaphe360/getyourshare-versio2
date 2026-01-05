import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import StatCard from '../../components/common/StatCard';
import { useToast } from '../../context/ToastContext';
import { 
  DollarSign, 
  Users, 
  TrendingUp, 
  TrendingDown, 
  Award, 
  Target, 
  ArrowUpRight, 
  ArrowDownRight,
  Filter,
  Download,
  Calendar
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

const MLMCommissions = () => {
  const toast = useToast();
  const [animatedValues, setAnimatedValues] = useState({
    total: 0,
    affiliates: 0,
    rate: 0
  });
  
  const [period, setPeriod] = useState('month');
  const [hoveredLevel, setHoveredLevel] = useState(null);

  // Fonction d'export
  const handleExport = () => {
    try {
      toast.info('Préparation de l\'export...');
      const csvContent = `Niveau,Pourcentage,Affiliés,Gains,Croissance\n${levels.map(l => 
        `${l.level},${l.percentage}%,${l.affiliates},${l.earned}€,${l.growth}%`
      ).join('\n')}`;
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `mlm_commissions_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      toast.success('Export réussi !');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  // Animation des chiffres au chargement
  useEffect(() => {
    const animateValue = (start, end, duration, key) => {
      const startTime = Date.now();
      const animate = () => {
        const now = Date.now();
        const progress = Math.min((now - startTime) / duration, 1);
        const value = start + (end - start) * progress;
        
        setAnimatedValues(prev => ({
          ...prev,
          [key]: key === 'rate' ? value.toFixed(1) : Math.floor(value)
        }));

        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    };

    animateValue(0, 9180, 1500, 'total');
    animateValue(0, 257, 1200, 'affiliates');
    animateValue(0, 5.8, 1300, 'rate');
  }, []);

  const levels = [
    { 
      level: 1, 
      percentage: 10, 
      affiliates: 45, 
      earned: 4500,
      growth: 12.5,
      color: '#3B82F6',
      gradient: 'from-blue-500 to-blue-600'
    },
    { 
      level: 2, 
      percentage: 5, 
      affiliates: 123, 
      earned: 3450,
      growth: 8.3,
      color: '#10B981',
      gradient: 'from-green-500 to-green-600'
    },
    { 
      level: 3, 
      percentage: 2.5, 
      affiliates: 89, 
      earned: 1230,
      growth: -2.1,
      color: '#8B5CF6',
      gradient: 'from-purple-500 to-purple-600'
    },
  ];

  // Données pour graphiques
  const evolutionData = [
    { month: 'Jan', total: 7500, level1: 3800, level2: 2800, level3: 900 },
    { month: 'Fév', total: 8200, level1: 4100, level2: 3000, level3: 1100 },
    { month: 'Mar', total: 8800, level1: 4300, level2: 3200, level3: 1300 },
    { month: 'Avr', total: 9180, level1: 4500, level2: 3450, level3: 1230 },
  ];

  const distributionData = levels.map(level => ({
    name: `Niveau ${level.level}`,
    value: level.earned,
    percentage: level.percentage
  }));

  const topPerformers = [
    { rank: 1, name: 'Sophie Martin', level: 1, commission: 850, affiliates: 12 },
    { rank: 2, name: 'Thomas Dubois', level: 1, commission: 720, affiliates: 9 },
    { rank: 3, name: 'Marie Lambert', level: 2, commission: 680, affiliates: 15 },
    { rank: 4, name: 'Lucas Bernard', level: 2, commission: 590, affiliates: 11 },
    { rank: 5, name: 'Emma Petit', level: 3, commission: 420, affiliates: 8 },
  ];

  const COLORS = ['#3B82F6', '#10B981', '#8B5CF6'];

  return (
    <div className="space-y-6 animate-fadeIn" data-testid="mlm-commissions">
      {/* Header avec actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Award className="text-blue-600" size={32} />
            Commissions MLM
          </h1>
          <p className="text-gray-600 mt-2">Rapports Multi-Level Marketing en temps réel</p>
        </div>
        
        <div className="flex gap-3 mt-4 md:mt-0">
          <select 
            id="period-select"
            name="period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="week">7 derniers jours</option>
            <option value="month">30 derniers jours</option>
            <option value="quarter">3 derniers mois</option>
            <option value="year">12 derniers mois</option>
          </select>
          
          <button 
            onClick={handleExport}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Download size={18} />
            Exporter
          </button>
        </div>
      </div>

      {/* KPI Cards avec animation */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <DollarSign size={32} className="opacity-80" />
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">+15.3%</span>
          </div>
          <h3 className="text-sm font-medium opacity-90 mb-1">Total Commissions MLM</h3>
          <p className="text-3xl font-bold">{animatedValues.total.toLocaleString()} €</p>
          <div className="flex items-center gap-1 mt-2 text-sm">
            <ArrowUpRight size={16} />
            <span>1,250€ ce mois</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <Users size={32} className="opacity-80" />
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">+8.2%</span>
          </div>
          <h3 className="text-sm font-medium opacity-90 mb-1">Affiliés Actifs</h3>
          <p className="text-3xl font-bold">{animatedValues.affiliates}</p>
          <div className="flex items-center gap-1 mt-2 text-sm">
            <ArrowUpRight size={16} />
            <span>+18 nouveaux</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <TrendingUp size={32} className="opacity-80" />
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">Stable</span>
          </div>
          <h3 className="text-sm font-medium opacity-90 mb-1">Taux Moyen</h3>
          <p className="text-3xl font-bold">{animatedValues.rate}%</p>
          <div className="flex items-center gap-1 mt-2 text-sm">
            <ArrowUpRight size={16} />
            <span>+0.3% ce mois</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg transform hover:scale-105 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <Target size={32} className="opacity-80" />
            <span className="text-sm bg-white/20 px-2 py-1 rounded-full">82%</span>
          </div>
          <h3 className="text-sm font-medium opacity-90 mb-1">Objectif Mensuel</h3>
          <p className="text-3xl font-bold">11,200 €</p>
          <div className="flex items-center gap-1 mt-2 text-sm">
            <span>Reste 2,020€</span>
          </div>
        </div>
      </div>

      {/* Graphiques */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Évolution des Commissions">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={evolutionData}>
              <defs>
                <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="total" 
                stroke="#3B82F6" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorTotal)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Distribution par Niveau">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={distributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                animationBegin={0}
                animationDuration={800}
              >
                {distributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => `${value.toLocaleString()} €`}
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Commissions par niveau - Design amélioré */}
      <Card title="Commissions par Niveau" subtitle="Performance détaillée de chaque niveau MLM">
        <div className="space-y-4">
          {levels.map((level) => (
            <div 
              key={level.level} 
              className={`relative overflow-hidden rounded-xl transition-all duration-300 ${
                hoveredLevel === level.level ? 'shadow-xl scale-[1.02]' : 'shadow-md'
              }`}
              onMouseEnter={() => setHoveredLevel(level.level)}
              onMouseLeave={() => setHoveredLevel(null)}
            >
              <div className={`bg-gradient-to-r ${level.gradient} p-6 text-white`}>
                <div className="flex justify-between items-center">
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold">
                        {level.level}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold">Niveau {level.level}</h3>
                        <p className="text-sm opacity-90">{level.percentage}% de commission</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 mt-4">
                      <div className="bg-white/20 px-4 py-2 rounded-lg">
                        <p className="text-xs opacity-80">Affiliés</p>
                        <p className="text-2xl font-bold">{level.affiliates}</p>
                      </div>
                      <div className="bg-white/20 px-4 py-2 rounded-lg">
                        <p className="text-xs opacity-80">Croissance</p>
                        <div className="flex items-center gap-1">
                          {level.growth > 0 ? (
                            <ArrowUpRight size={18} />
                          ) : (
                            <ArrowDownRight size={18} />
                          )}
                          <p className="text-xl font-bold">{Math.abs(level.growth)}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-sm opacity-80 mb-1">Total gagné</p>
                    <p className="text-5xl font-bold">{level.earned.toLocaleString()}€</p>
                    <p className="text-sm opacity-90 mt-2">
                      Moy: {(level.earned / level.affiliates).toFixed(0)}€/affilié
                    </p>
                  </div>
                </div>

                {/* Barre de progression */}
                <div className="mt-4 bg-white/20 rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-white h-full rounded-full transition-all duration-1000"
                    style={{ width: `${(level.earned / 5000) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Top Performers */}
      <Card title="Top 5 Affiliés" subtitle="Meilleurs performers du mois">
        <div className="space-y-3">
          {topPerformers.map((performer) => (
            <div 
              key={performer.rank}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${
                  performer.rank === 1 ? 'bg-gradient-to-br from-yellow-400 to-yellow-500' :
                  performer.rank === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-400' :
                  performer.rank === 3 ? 'bg-gradient-to-br from-orange-400 to-orange-500' :
                  'bg-gradient-to-br from-gray-400 to-gray-500'
                }`}>
                  #{performer.rank}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{performer.name}</p>
                  <p className="text-sm text-gray-600">Niveau {performer.level} · {performer.affiliates} affiliés</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-blue-600">{performer.commission}€</p>
                <p className="text-sm text-gray-600">ce mois</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Comparaison par niveau */}
      <Card title="Comparaison des Niveaux">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={evolutionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="month" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#fff', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Bar dataKey="level1" name="Niveau 1" fill="#3B82F6" radius={[8, 8, 0, 0]} />
            <Bar dataKey="level2" name="Niveau 2" fill="#10B981" radius={[8, 8, 0, 0]} />
            <Bar dataKey="level3" name="Niveau 3" fill="#8B5CF6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
};

export default MLMCommissions;
