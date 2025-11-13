import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Share2, Users, DollarSign, TrendingUp, Copy, CheckCircle,
  Award, Crown, Gift, Link as LinkIcon
} from 'lucide-react';
import api from '../../utils/api';
import { useToast } from '../../context/ToastContext';

const ReferralDashboard = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [copied, setCopied] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const toast = useToast();

  useEffect(() => {
    fetchDashboard();
    fetchLeaderboard();
  }, [userId]);

  const fetchDashboard = async () => {
    try {
      const response = await api.get(`/api/referrals/dashboard/${userId}`);
      setDashboard(response.data);
    } catch (error) {
      toast?.error('Erreur chargement dashboard parrainage');
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await api.get('/api/referrals/leaderboard?limit=10');
      setLeaderboard(response.data.leaderboard || []);
    } catch (error) {
      // Silent fail
    }
  };

  const copyReferralLink = () => {
    const link = dashboard?.referral_code?.share_link;
    if (link) {
      navigator.clipboard.writeText(link);
      setCopied(true);
      toast?.success('Lien copié!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getBadgeEmoji = (badge) => {
    const badges = {
      'bronze': '🥉',
      'silver': '🥈',
      'gold': '🥇',
      'platinum': '💎',
      'diamond': '👑'
    };
    return badges[badge] || '🏅';
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  const code = dashboard?.referral_code?.code;
  const earnings = dashboard?.earnings;
  const network = dashboard?.network;

  return (
    <div className="space-y-6">
      {/* Header avec code de parrainage */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">Programme Parrainage</h2>
            <p className="text-purple-100">Gagne jusqu'à 10% sur les ventes de tes filleuls!</p>
          </div>
          <Gift className="w-12 h-12 opacity-80" />
        </div>

        <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-100 mb-1">Ton code de parrainage</p>
              <p className="text-3xl font-bold tracking-wider">{code || 'CHARGEMENT...'}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={copyReferralLink}
                className="bg-white/30 hover:bg-white/40 px-4 py-2 rounded-lg transition flex items-center gap-2"
              >
                {copied ? <CheckCircle className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
                {copied ? 'Copié!' : 'Copier'}
              </button>
              <button
                onClick={() => {
                  const message = dashboard?.referral_code?.share_message;
                  if (navigator.share) {
                    navigator.share({
                      title: 'Rejoins GetYourShare',
                      text: message,
                      url: dashboard?.referral_code?.share_link
                    });
                  }
                }}
                className="bg-white/30 hover:bg-white/40 px-4 py-2 rounded-lg transition flex items-center gap-2"
              >
                <Share2 className="w-5 h-5" />
                Partager
              </button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg p-4 shadow-md"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Réseau</p>
              <p className="text-2xl font-bold">{network?.total_network || 0}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg p-4 shadow-md"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Gains Ce Mois</p>
              <p className="text-2xl font-bold text-green-600">
                {earnings?.this_month_earnings?.toFixed(2) || '0.00'}€
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-500" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg p-4 shadow-md"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Gains Totaux</p>
              <p className="text-2xl font-bold text-purple-600">
                {earnings?.total_earnings?.toFixed(2) || '0.00'}€
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-purple-500" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg p-4 shadow-md"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Badge</p>
              <p className="text-2xl font-bold">
                {getBadgeEmoji(earnings?.badge_level)} {earnings?.badge_level || 'bronze'}
              </p>
            </div>
            <Award className="w-8 h-8 text-yellow-500" />
          </div>
        </motion.div>
      </div>

      {/* Réseau de parrainage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mon réseau */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-lg p-6 shadow-md"
        >
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-500" />
            Mon Réseau
          </h3>

          {network?.network && network.network.length > 0 ? (
            <div className="space-y-3">
              {network.network.slice(0, 10).map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      member.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                    }`} />
                    <div>
                      <p className="font-medium">{member.referred_username}</p>
                      <p className="text-xs text-gray-500">
                        Niveau {member.level} • {member.status}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-green-600">
                      +{member.referrer_earnings?.toFixed(2)}€
                    </p>
                    <p className="text-xs text-gray-500">
                      {member.total_sales?.toFixed(0)}€ ventes
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Aucun filleul pour le moment</p>
              <p className="text-sm text-gray-400 mt-2">
                Partage ton code pour commencer à gagner!
              </p>
            </div>
          )}

          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Niveau 1:</span>
              <span className="font-bold">{network?.level1_count || 0} filleuls</span>
            </div>
            <div className="flex justify-between text-sm mt-2">
              <span className="text-gray-600">Niveau 2:</span>
              <span className="font-bold">{network?.level2_count || 0} filleuls</span>
            </div>
          </div>
        </motion.div>

        {/* Leaderboard */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-lg p-6 shadow-md"
        >
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Crown className="w-6 h-6 text-yellow-500" />
            Top Parrains
          </h3>

          <div className="space-y-2">
            {leaderboard.map((leader) => (
              <div
                key={leader.user_id}
                className={`flex items-center justify-between p-3 rounded-lg ${
                  leader.user_id === userId ? 'bg-purple-50 border-2 border-purple-300' : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold w-8 text-center">
                    {leader.rank === 1 ? '🥇' : leader.rank === 2 ? '🥈' : leader.rank === 3 ? '🥉' : leader.rank}
                  </span>
                  <div>
                    <p className="font-medium">
                      {leader.username}
                      {leader.user_id === userId && (
                        <span className="ml-2 text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded">
                          Toi
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-gray-500">
                      {leader.total_referrals} filleuls • {leader.badge_emoji}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-green-600">
                    {leader.total_earnings?.toFixed(0)}€
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Gains en attente */}
      {earnings?.pending_earnings > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90 mb-1">Gains en attente</p>
              <p className="text-3xl font-bold">{earnings.pending_earnings.toFixed(2)}€</p>
              <p className="text-sm mt-2 opacity-90">
                Seront payés après validation des ventes
              </p>
            </div>
            <DollarSign className="w-16 h-16 opacity-50" />
          </div>
        </motion.div>
      )}

      {/* Comment ça marche */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-bold mb-4 text-blue-900">💡 Comment ça marche?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">1️⃣</div>
            <h4 className="font-bold mb-1">Partage ton code</h4>
            <p className="text-sm text-gray-600">
              Envoie ton code à tes amis influenceurs/marchands
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">2️⃣</div>
            <h4 className="font-bold mb-1">Ils s'inscrivent</h4>
            <p className="text-sm text-gray-600">
              Ils utilisent ton code lors de l'inscription
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="text-2xl mb-2">3️⃣</div>
            <h4 className="font-bold mb-1">Tu gagnes!</h4>
            <p className="text-sm text-gray-600">
              10% niveau 1 + 5% niveau 2 sur leurs ventes
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferralDashboard;
