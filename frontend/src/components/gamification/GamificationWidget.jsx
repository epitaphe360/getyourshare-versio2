/**
 * Gamification Widget
 * Composant réutilisable pour Marchands, Influenceurs et Commerciaux
 * - Points & Niveau
 * - Badges
 * - Missions quotidiennes
 * - Leaderboard
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

// Icons
const StarIcon = () => <span>⭐</span>;
const TrophyIcon = () => <span>🏆</span>;
const FireIcon = () => <span>🔥</span>;
const TargetIcon = () => <span>🎯</span>;
const GiftIcon = () => <span>🎁</span>;
const CrownIcon = () => <span>👑</span>;

const GamificationWidget = ({ userType = 'merchant', userId }) => {
  const [gamificationData, setGamificationData] = useState(null);
  const [dailyMissions, setDailyMissions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, missions, leaderboard

  useEffect(() => {
    fetchGamificationData();
  }, [userId, userType]);

  const fetchGamificationData = async () => {
    setIsLoading(true);
    try {
      const [gamifRes, missionsRes, leaderboardRes] = await Promise.all([
        axios.get(`/api/gamification/user/${userId}`),
        axios.get(`/api/gamification/missions/daily?user_type=${userType}`),
        axios.get(`/api/gamification/leaderboard?user_type=${userType}&period=month`)
      ]);

      setGamificationData(gamifRes.data);
      setDailyMissions(missionsRes.data);
      setLeaderboard(leaderboardRes.data);
    } catch (error) {
      console.error('Erreur chargement gamification:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClaimMission = async (missionId) => {
    try {
      await axios.post(`/api/gamification/missions/${missionId}/claim`);
      fetchGamificationData();
      toast.success('Mission complétée ! Points gagnés 🏆');
    } catch (error) {
      console.error('Erreur réclamation mission:', error);
      toast.error(error.response?.data?.error || 'Erreur lors de la réclamation');
    }
  };

  if (isLoading && !gamificationData) {
    return <div className="animate-pulse bg-gray-200 h-64 rounded-lg"></div>;
  }

  const { points, level_tier, badges, achievements, rank } = gamificationData || {};

  // Configuration des niveaux
  const levelConfig = {
    bronze: { color: '#CD7F32', next: 'silver', threshold: 5000 },
    silver: { color: '#C0C0C0', next: 'gold', threshold: 15000 },
    gold: { color: '#FFD700', next: 'platinum', threshold: 30000 },
    platinum: { color: '#E5E4E2', next: 'diamond', threshold: 50000 },
    diamond: { color: '#B9F2FF', next: 'legend', threshold: 100000 },
    legend: { color: '#FF6B6B', next: null, threshold: Infinity }
  };

  const currentLevel = levelConfig[level_tier] || levelConfig.bronze;
  const pointsToNextLevel = currentLevel.threshold - (points || 0);
  const progressPercent = currentLevel.next
    ? ((points || 0) / currentLevel.threshold) * 100
    : 100;

  return (
    <div className="gamification-widget bg-white rounded-lg shadow-sm">
      {/* Tabs */}
      <div className="border-b">
        <div className="flex">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 font-semibold ${
              activeTab === 'overview'
                ? 'border-b-2 border-indigo-500 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Vue d'ensemble
          </button>
          <button
            onClick={() => setActiveTab('missions')}
            className={`px-6 py-3 font-semibold ${
              activeTab === 'missions'
                ? 'border-b-2 border-indigo-500 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Missions <span className="text-xs">({dailyMissions.filter(m => !m.completed).length})</span>
          </button>
          <button
            onClick={() => setActiveTab('leaderboard')}
            className={`px-6 py-3 font-semibold ${
              activeTab === 'leaderboard'
                ? 'border-b-2 border-indigo-500 text-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Classement
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <OverviewTab
            points={points}
            level_tier={level_tier}
            badges={badges}
            achievements={achievements}
            rank={rank}
            currentLevel={currentLevel}
            pointsToNextLevel={pointsToNextLevel}
            progressPercent={progressPercent}
          />
        )}

        {activeTab === 'missions' && (
          <MissionsTab
            missions={dailyMissions}
            onClaimMission={handleClaimMission}
          />
        )}

        {activeTab === 'leaderboard' && (
          <LeaderboardTab
            leaderboard={leaderboard}
            currentUserId={userId}
          />
        )}
      </div>
    </div>
  );
};

// ============================================
// TAB COMPONENTS
// ============================================

const OverviewTab = ({
  points,
  level_tier,
  badges,
  achievements,
  rank,
  currentLevel,
  pointsToNextLevel,
  progressPercent
}) => {
  return (
    <div className="space-y-6">
      {/* Niveau actuel */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-4"
          style={{ backgroundColor: currentLevel.color + '40', border: `3px solid ${currentLevel.color}` }}>
          <CrownIcon className="text-5xl" />
        </div>

        <h3 className="text-2xl font-bold text-gray-900 uppercase mb-1">
          {level_tier}
        </h3>
        <p className="text-gray-600">{(points || 0).toLocaleString()} points</p>

        {currentLevel.next && (
          <>
            {/* Progress Bar */}
            <div className="mt-4 bg-gray-200 rounded-full h-3 max-w-md mx-auto">
              <div
                className="h-3 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(progressPercent, 100)}%`,
                  backgroundColor: currentLevel.color
                }}
              ></div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {pointsToNextLevel.toLocaleString()} points pour {currentLevel.next.toUpperCase()}
            </p>
          </>
        )}

        {!currentLevel.next && (
          <p className="text-sm text-purple-600 mt-2 font-semibold">
            🎉 Niveau maximum atteint!
          </p>
        )}
      </div>

      {/* Rang */}
      {rank && (
        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 text-center">
          <div className="text-sm text-gray-600 mb-1">Votre classement</div>
          <div className="text-3xl font-bold text-indigo-600">
            #{rank.rank}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            Top {rank.percentile}% des utilisateurs
          </div>
        </div>
      )}

      {/* Avantages du niveau */}
      <div className="bg-blue-50 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <GiftIcon /> Avantages {level_tier.toUpperCase()}
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>✓ Réduction commission: {getLevelDiscount(level_tier)}%</li>
          <li>✓ Support: {getLevelSupport(level_tier)}</li>
          <li>✓ Features: {getLevelFeatures(level_tier)}</li>
        </ul>
      </div>

      {/* Badges */}
      {badges && badges.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Badges obtenus</h4>
          <div className="grid grid-cols-3 gap-3">
            {badges.map((badge, idx) => (
              <div key={idx} className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl mb-1">{badge.icon || '🏅'}</div>
                <div className="text-xs font-semibold text-gray-700">{badge.name}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Achievements récents */}
      {achievements && achievements.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-3">Achievements récents</h4>
          <div className="space-y-2">
            {achievements.slice(0, 3).map((achievement, idx) => (
              <div key={idx} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                <div className="text-2xl">{achievement.icon}</div>
                <div className="flex-1">
                  <div className="text-sm font-semibold">{achievement.name}</div>
                  <div className="text-xs text-gray-600">{achievement.description}</div>
                </div>
                <div className="text-xs text-gray-500">
                  {new Date(achievement.earned_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const MissionsTab = ({ missions, onClaimMission }) => {
  const activeMissions = missions.filter(m => !m.completed);
  const completedMissions = missions.filter(m => m.completed);

  return (
    <div className="space-y-6">
      {/* Missions actives */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <TargetIcon /> Missions du jour
        </h4>

        {activeMissions.length > 0 ? (
          <div className="space-y-3">
            {activeMissions.map((mission) => (
              <div key={mission.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-semibold text-gray-900">{mission.title}</h5>
                    <p className="text-sm text-gray-600">{mission.description}</p>
                  </div>
                  <div className="text-sm font-bold text-indigo-600">
                    +{mission.reward_points} pts
                  </div>
                </div>

                {/* Progress */}
                <div className="mt-3">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Progression</span>
                    <span className="font-semibold">
                      {mission.current} / {mission.target}
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-500 rounded-full h-2 transition-all"
                      style={{ width: `${mission.completion_pct}%` }}
                    ></div>
                  </div>
                </div>

                {mission.completed && (
                  <button
                    onClick={() => onClaimMission(mission.id)}
                    className="mt-3 w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                  >
                    ✓ Réclamer la récompense
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-8">
            Aucune mission active
          </div>
        )}
      </div>

      {/* Missions complétées */}
      {completedMissions.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            ✅ Complétées aujourd'hui
          </h4>
          <div className="space-y-2">
            {completedMissions.map((mission) => (
              <div key={mission.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <div className="text-sm font-semibold text-green-900">{mission.title}</div>
                  <div className="text-xs text-green-700">+{mission.reward_points} points gagnés</div>
                </div>
                <div className="text-green-500 text-2xl">✓</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const LeaderboardTab = ({ leaderboard, currentUserId }) => {
  return (
    <div>
      <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <TrophyIcon /> Top 10 du mois
      </h4>

      {leaderboard.length > 0 ? (
        <div className="space-y-3">
          {leaderboard.map((user, index) => (
            <div
              key={user.id}
              className={`flex items-center justify-between p-4 rounded-lg ${
                index === 0
                  ? 'bg-gradient-to-r from-yellow-100 to-yellow-50 border-2 border-yellow-400'
                  : index === 1
                  ? 'bg-gradient-to-r from-gray-100 to-gray-50 border-2 border-gray-400'
                  : index === 2
                  ? 'bg-gradient-to-r from-orange-100 to-orange-50 border-2 border-orange-400'
                  : user.id === currentUserId
                  ? 'bg-indigo-50 border-2 border-indigo-300'
                  : 'bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-4">
                <div className={`text-2xl font-bold ${
                  index === 0 ? 'text-yellow-600' :
                  index === 1 ? 'text-gray-600' :
                  index === 2 ? 'text-orange-600' :
                  'text-gray-400'
                }`}>
                  #{index + 1}
                </div>

                <div>
                  <div className="font-semibold text-gray-900">
                    {user.name}
                    {user.id === currentUserId && (
                      <span className="ml-2 text-xs px-2 py-1 bg-indigo-100 text-indigo-700 rounded">
                        Vous
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-600">
                    {user.level_tier.toUpperCase()}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-bold text-indigo-600">
                  {user.points.toLocaleString()} pts
                </div>
                <div className="text-sm text-gray-600">
                  {user.metric_value} {user.metric_label}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center text-gray-500 py-8">
          Aucune donnée disponible
        </div>
      )}
    </div>
  );
};

// ============================================
// HELPER FUNCTIONS
// ============================================

const getLevelDiscount = (tier) => {
  const discounts = {
    bronze: 0,
    silver: 5,
    gold: 10,
    platinum: 15,
    diamond: 20,
    legend: 25
  };
  return discounts[tier] || 0;
};

const getLevelSupport = (tier) => {
  const support = {
    bronze: 'Email',
    silver: 'Email prioritaire',
    gold: 'Chat',
    platinum: 'Téléphone',
    diamond: 'Dédié',
    legend: 'VIP'
  };
  return support[tier] || 'Email';
};

const getLevelFeatures = (tier) => {
  const features = {
    bronze: 'Basiques',
    silver: 'Analytics + Badge',
    gold: 'AI Basic + Featured',
    platinum: 'Pro + Manager',
    diamond: 'Illimité + White Label',
    legend: 'Partenariat exclusif'
  };
  return features[tier] || 'Basiques';
};

export default GamificationWidget;
