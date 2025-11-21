import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { Trophy, Star, Target, Award, TrendingUp, Zap, Gift, Crown } from 'lucide-react';

const GamificationWidget = ({ userId, userType = 'merchant' }) => {
  const [gamifData, setGamifData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGamification();
  }, [userId]);

  const fetchGamification = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/gamification/${userId}`);
      setGamifData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching gamification:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-6 bg-purple-200 rounded w-1/2 mb-4"></div>
          <div className="h-4 bg-purple-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (!gamifData) {
    return null;
  }

  const { level, points, badges, missions, leaderboard_position, rewards } = gamifData;

  // Niveaux et couleurs
  const levelConfig = {
    bronze: { color: 'from-orange-400 to-orange-600', icon: Trophy, label: 'Bronze' },
    silver: { color: 'from-gray-300 to-gray-500', icon: Award, label: 'Argent' },
    gold: { color: 'from-yellow-400 to-yellow-600', icon: Crown, label: 'Or' },
    platinum: { color: 'from-blue-300 to-blue-500', icon: Star, label: 'Platine' },
    diamond: { color: 'from-cyan-400 to-blue-600', icon: Zap, label: 'Diamant' },
    legend: { color: 'from-purple-500 to-pink-600', icon: Gift, label: 'Légende' }
  };

  const currentLevel = levelConfig[level?.tier || 'bronze'];
  const LevelIcon = currentLevel.icon;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-lg bg-gradient-to-br ${currentLevel.color} text-white shadow-md`}>
            <LevelIcon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">Niveau {currentLevel.label}</h3>
            <p className="text-sm text-gray-600">{points?.total || 0} points</p>
          </div>
        </div>
        {leaderboard_position && (
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600">#{leaderboard_position}</div>
            <div className="text-xs text-gray-500">Classement</div>
          </div>
        )}
      </div>

      {/* Barre de progression */}
      {level && (
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{level.current_points} / {level.next_level_points} pts</span>
            <span>{Math.round((level.current_points / level.next_level_points) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${currentLevel.color} transition-all duration-500 rounded-full`}
              style={{ width: `${Math.min((level.current_points / level.next_level_points) * 100, 100)}%` }}
            ></div>
          </div>
          {level.next_tier && (
            <p className="text-xs text-gray-500 mt-1">
              Prochain niveau: {levelConfig[level.next_tier]?.label} ({level.next_level_points - level.current_points} pts restants)
            </p>
          )}
        </div>
      )}

      {/* Badges récents */}
      {badges && badges.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Award className="w-4 h-4 text-purple-600" />
            Badges Récents
          </h4>
          <div className="flex gap-2 flex-wrap">
            {badges.slice(0, 6).map((badge, idx) => (
              <div
                key={idx}
                className="group relative"
                title={badge.description}
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-md hover:scale-110 transition-transform cursor-pointer">
                  <span className="text-xl">{badge.icon || '🏆'}</span>
                </div>
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  {badge.name}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Missions actives */}
      {missions && missions.active && missions.active.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-indigo-600" />
            Missions Actives
          </h4>
          <div className="space-y-2">
            {missions.active.slice(0, 3).map((mission, idx) => (
              <div key={idx} className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800">{mission.title}</p>
                    <p className="text-xs text-gray-500">{mission.description}</p>
                  </div>
                  <span className="text-xs font-bold text-purple-600 bg-purple-100 px-2 py-1 rounded">
                    +{mission.reward_points} pts
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full rounded-full transition-all"
                      style={{ width: `${Math.min((mission.progress / mission.target) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-gray-600 font-medium">
                    {mission.progress}/{mission.target}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Récompenses disponibles */}
      {rewards && rewards.available && rewards.available.length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3 border-2 border-green-200">
          <div className="flex items-center gap-2 text-green-700">
            <Gift className="w-5 h-5" />
            <span className="text-sm font-semibold">
              {rewards.available.length} récompense{rewards.available.length > 1 ? 's' : ''} disponible{rewards.available.length > 1 ? 's' : ''} !
            </span>
          </div>
        </div>
      )}

      {/* Avantages du niveau actuel */}
      {level && level.benefits && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            Avantages Actuels
          </h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {level.benefits.commission_discount > 0 && (
              <div className="bg-white rounded p-2 border border-gray-200">
                <span className="text-gray-600">Réduction: </span>
                <span className="font-bold text-green-600">-{level.benefits.commission_discount}%</span>
              </div>
            )}
            {level.benefits.priority_support && (
              <div className="bg-white rounded p-2 border border-gray-200">
                <span className="text-purple-600 font-medium">Support Prioritaire</span>
              </div>
            )}
            {level.benefits.free_products > 0 && (
              <div className="bg-white rounded p-2 border border-gray-200">
                <span className="text-gray-600">Produits gratuits: </span>
                <span className="font-bold text-blue-600">{level.benefits.free_products}</span>
              </div>
            )}
            {level.benefits.featured_listing && (
              <div className="bg-white rounded p-2 border border-gray-200">
                <span className="text-indigo-600 font-medium">Mise en avant</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GamificationWidget;
