"""
Rate Limiting Avancé par Plan d'Abonnement
Différenciation Free/Starter/Pro/Enterprise
Protection DDoS, IP Whitelisting, Blacklisting
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import time
import hashlib
from supabase import Client

import logging
logger = logging.getLogger(__name__)


class AdvancedRateLimiter:
    """Rate limiting granulaire par plan d'abonnement"""

    def __init__(self, supabase: Client):
        self.supabase = supabase

        # Cache en mémoire pour performance
        self._request_counts = defaultdict(list)  # {key: [(timestamp, count)]}
        self._blacklist_cache = set()
        self._whitelist_cache = set()

        # Limites par plan (requests per minute)
        self.PLAN_LIMITS = {
            'free': {
                'api_calls_per_minute': 10,
                'api_calls_per_hour': 100,
                'api_calls_per_day': 500,
                'burst_limit': 20
            },
            'starter': {
                'api_calls_per_minute': 50,
                'api_calls_per_hour': 1000,
                'api_calls_per_day': 10000,
                'burst_limit': 100
            },
            'pro': {
                'api_calls_per_minute': 200,
                'api_calls_per_hour': 10000,
                'api_calls_per_day': 100000,
                'burst_limit': 500
            },
            'enterprise': {
                'api_calls_per_minute': 1000,
                'api_calls_per_hour': 50000,
                'api_calls_per_day': 500000,
                'burst_limit': 2000
            }
        }

        # Endpoints avec limites spécifiques
        self.ENDPOINT_LIMITS = {
            '/api/auth/login': {'max_per_minute': 5, 'max_per_hour': 20},  # Protection brute force
            '/api/auth/register': {'max_per_minute': 3, 'max_per_hour': 10},
            '/api/payments/create': {'max_per_minute': 10, 'max_per_hour': 50},
            '/api/webhooks/stripe': {'max_per_minute': 100, 'max_per_hour': 1000},  # Webhooks externes
        }


    async def check_rate_limit(
        self,
        user_id: Optional[str],
        ip_address: str,
        endpoint: str,
        subscription_plan: str = 'free'
    ) -> Tuple[bool, Dict]:
        """
        Vérifier si la requête est autorisée selon les limites

        Returns:
            (allowed: bool, info: Dict)
            info contient: remaining, reset_at, limit, etc.
        """
        try:
            # 1. Vérifier blacklist IP
            if await self._is_blacklisted(ip_address):
                return False, {
                    'error': 'IP blacklisted',
                    'reason': 'Suspicious activity detected',
                    'retry_after': None
                }

            # 2. Vérifier whitelist (bypass rate limit)
            if await self._is_whitelisted(ip_address):
                return True, {'whitelisted': True}

            # 3. Déterminer les limites applicables
            limits = self.PLAN_LIMITS.get(subscription_plan, self.PLAN_LIMITS['free'])

            # Endpoint spécifique ?
            if endpoint in self.ENDPOINT_LIMITS:
                endpoint_limits = self.ENDPOINT_LIMITS[endpoint]
            else:
                endpoint_limits = None

            # 4. Vérifier les limites
            now = time.time()
            rate_key = f"{user_id or ip_address}:{endpoint}"

            # Nettoyer les vieilles entrées
            self._cleanup_old_requests(rate_key, now)

            # Compter les requêtes
            minute_count = self._count_requests(rate_key, now, 60)
            hour_count = self._count_requests(rate_key, now, 3600)
            day_count = self._count_requests(rate_key, now, 86400)

            # Limites endpoint spécifiques
            if endpoint_limits:
                if minute_count >= endpoint_limits['max_per_minute']:
                    return False, {
                        'error': 'Rate limit exceeded',
                        'limit': endpoint_limits['max_per_minute'],
                        'remaining': 0,
                        'reset_at': self._get_reset_time(60),
                        'window': 'minute'
                    }

                if hour_count >= endpoint_limits['max_per_hour']:
                    return False, {
                        'error': 'Rate limit exceeded',
                        'limit': endpoint_limits['max_per_hour'],
                        'remaining': 0,
                        'reset_at': self._get_reset_time(3600),
                        'window': 'hour'
                    }

            # Limites plan
            if minute_count >= limits['api_calls_per_minute']:
                return False, {
                    'error': 'Rate limit exceeded',
                    'limit': limits['api_calls_per_minute'],
                    'remaining': 0,
                    'reset_at': self._get_reset_time(60),
                    'window': 'minute',
                    'plan': subscription_plan,
                    'upgrade_message': 'Upgrade your plan for higher limits'
                }

            if hour_count >= limits['api_calls_per_hour']:
                return False, {
                    'error': 'Rate limit exceeded',
                    'limit': limits['api_calls_per_hour'],
                    'remaining': 0,
                    'reset_at': self._get_reset_time(3600),
                    'window': 'hour',
                    'plan': subscription_plan
                }

            if day_count >= limits['api_calls_per_day']:
                return False, {
                    'error': 'Daily limit exceeded',
                    'limit': limits['api_calls_per_day'],
                    'remaining': 0,
                    'reset_at': self._get_reset_time(86400),
                    'window': 'day',
                    'plan': subscription_plan
                }

            # 5. Enregistrer la requête
            self._record_request(rate_key, now)

            # 6. Retourner info
            return True, {
                'allowed': True,
                'limit_minute': limits['api_calls_per_minute'],
                'remaining_minute': limits['api_calls_per_minute'] - minute_count - 1,
                'limit_hour': limits['api_calls_per_hour'],
                'remaining_hour': limits['api_calls_per_hour'] - hour_count - 1,
                'limit_day': limits['api_calls_per_day'],
                'remaining_day': limits['api_calls_per_day'] - day_count - 1,
                'reset_minute': self._get_reset_time(60),
                'reset_hour': self._get_reset_time(3600),
                'reset_day': self._get_reset_time(86400),
                'plan': subscription_plan
            }

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # En cas d'erreur, autoriser par défaut (fail-open)
            return True, {'error': 'Rate limiter error', 'allowed': True}


    def _count_requests(self, key: str, now: float, window: int) -> int:
        """Compter les requêtes dans une fenêtre de temps"""
        if key not in self._request_counts:
            return 0

        cutoff = now - window
        count = sum(1 for timestamp, _ in self._request_counts[key] if timestamp > cutoff)
        return count


    def _record_request(self, key: str, timestamp: float):
        """Enregistrer une requête"""
        self._request_counts[key].append((timestamp, 1))

        # Limiter la taille du cache (garder max 1000 entrées par clé)
        if len(self._request_counts[key]) > 1000:
            self._request_counts[key] = self._request_counts[key][-500:]


    def _cleanup_old_requests(self, key: str, now: float):
        """Nettoyer les requêtes anciennes (> 24h)"""
        if key not in self._request_counts:
            return

        cutoff = now - 86400  # 24 heures
        self._request_counts[key] = [
            (ts, count) for ts, count in self._request_counts[key]
            if ts > cutoff
        ]


    def _get_reset_time(self, window: int) -> str:
        """Calculer le temps de reset"""
        reset_at = datetime.now() + timedelta(seconds=window)
        return reset_at.isoformat()


    async def _is_blacklisted(self, ip_address: str) -> bool:
        """Vérifier si une IP est blacklistée"""
        # Check cache
        if ip_address in self._blacklist_cache:
            return True

        # Check DB
        try:
            result = self.supabase.table('ip_blacklist').select('*').eq('ip_address', ip_address).eq('active', True).single().execute()

            if result.data:
                self._blacklist_cache.add(ip_address)
                return True

            return False

        except Exception:
            return False


    async def _is_whitelisted(self, ip_address: str) -> bool:
        """Vérifier si une IP est whitelistée"""
        # Check cache
        if ip_address in self._whitelist_cache:
            return True

        # Check DB
        try:
            result = self.supabase.table('ip_whitelist').select('*').eq('ip_address', ip_address).eq('active', True).single().execute()

            if result.data:
                self._whitelist_cache.add(ip_address)
                return True

            return False

        except Exception:
            return False


    async def add_to_blacklist(
        self,
        ip_address: str,
        reason: str,
        duration_hours: Optional[int] = None,
        added_by: Optional[str] = None
    ) -> Dict:
        """Ajouter une IP à la blacklist"""
        try:
            expires_at = None
            if duration_hours:
                expires_at = (datetime.now() + timedelta(hours=duration_hours)).isoformat()

            blacklist_entry = {
                'ip_address': ip_address,
                'reason': reason,
                'active': True,
                'expires_at': expires_at,
                'added_by': added_by
            }

            result = self.supabase.table('ip_blacklist').insert(blacklist_entry).execute()

            # Ajouter au cache
            self._blacklist_cache.add(ip_address)

            return {
                "success": True,
                "ip_address": ip_address,
                "expires_at": expires_at
            }

        except Exception as e:
            logger.error(f"Error adding to blacklist: {e}")
            raise


    async def add_to_whitelist(
        self,
        ip_address: str,
        reason: str,
        added_by: Optional[str] = None
    ) -> Dict:
        """Ajouter une IP à la whitelist"""
        try:
            whitelist_entry = {
                'ip_address': ip_address,
                'reason': reason,
                'active': True,
                'added_by': added_by
            }

            result = self.supabase.table('ip_whitelist').insert(whitelist_entry).execute()

            # Ajouter au cache
            self._whitelist_cache.add(ip_address)

            return {
                "success": True,
                "ip_address": ip_address
            }

        except Exception as e:
            logger.error(f"Error adding to whitelist: {e}")
            raise


    async def detect_suspicious_activity(
        self,
        ip_address: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Détecter une activité suspecte (potentiel DDoS ou abuse)

        Returns:
            Dict si suspect, None sinon
        """
        try:
            now = time.time()
            key = f"{user_id or ip_address}:*"

            # Compter TOUTES les requêtes de cette IP (tous endpoints)
            total_minute = sum(
                self._count_requests(k, now, 60)
                for k in self._request_counts.keys()
                if k.startswith(f"{user_id or ip_address}:")
            )

            total_hour = sum(
                self._count_requests(k, now, 3600)
                for k in self._request_counts.keys()
                if k.startswith(f"{user_id or ip_address}:")
            )

            # Seuils DDoS
            if total_minute > 500:  # Plus de 500 req/min
                return {
                    'type': 'ddos',
                    'severity': 'critical',
                    'requests_per_minute': total_minute,
                    'action': 'auto_blacklist_recommended'
                }

            if total_hour > 10000:  # Plus de 10k req/h
                return {
                    'type': 'abuse',
                    'severity': 'high',
                    'requests_per_hour': total_hour,
                    'action': 'monitor'
                }

            return None

        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return None


    async def get_rate_limit_stats(
        self,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        period: str = 'hour'
    ) -> Dict:
        """
        Statistiques d'utilisation des rate limits
        """
        try:
            now = time.time()

            if period == 'minute':
                window = 60
            elif period == 'hour':
                window = 3600
            else:
                window = 86400

            key_pattern = f"{user_id or ip_address}:"

            total_requests = sum(
                self._count_requests(k, now, window)
                for k in self._request_counts.keys()
                if k.startswith(key_pattern)
            )

            return {
                'period': period,
                'total_requests': total_requests,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {}
