"""
Service OAuth pour Connexions Multi-Plateformes
Gestion sécurisée des authentifications Instagram, Twitter, LinkedIn, Facebook, TikTok
"""

import os
import secrets
import hashlib
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import httpx

from models.media_models import (
    PlatformType,
    OAuthInitRequest,
    OAuthInitResponse,
    OAuthCallbackRequest,
    PlatformConnectionCreate,
    PlatformConnection
)


class MediaOAuthService:
    """
    Service de gestion OAuth2 pour toutes les plateformes sociales
    Support: PKCE, refresh tokens, stockage sécurisé
    """

    def __init__(self):
        # Configuration des plateformes
        self.platform_configs = {
            PlatformType.INSTAGRAM: {
                "client_id": os.getenv("INSTAGRAM_CLIENT_ID"),
                "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET"),
                "authorization_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "scope": "user_profile,user_media,instagram_business_basic",
                "response_type": "code",
                "grant_type": "authorization_code"
            },
            PlatformType.TWITTER: {
                "client_id": os.getenv("TWITTER_CLIENT_ID"),
                "client_secret": os.getenv("TWITTER_CLIENT_SECRET"),
                "authorization_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "scope": "tweet.read tweet.write users.read offline.access",
                "response_type": "code",
                "grant_type": "authorization_code",
                "use_pkce": True
            },
            PlatformType.LINKEDIN: {
                "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
                "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
                "authorization_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "scope": "r_liteprofile r_emailaddress w_member_social",
                "response_type": "code",
                "grant_type": "authorization_code"
            },
            PlatformType.FACEBOOK: {
                "client_id": os.getenv("FACEBOOK_APP_ID"),
                "client_secret": os.getenv("FACEBOOK_APP_SECRET"),
                "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "scope": "pages_manage_posts,pages_read_engagement,pages_show_list",
                "response_type": "code",
                "grant_type": "authorization_code"
            },
            PlatformType.TIKTOK: {
                "client_key": os.getenv("TIKTOK_CLIENT_KEY"),
                "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
                "authorization_url": "https://www.tiktok.com/v2/auth/authorize",
                "token_url": "https://open.tiktokapis.com/v2/oauth/token/",
                "scope": "user.info.basic,video.list,video.upload",
                "response_type": "code",
                "grant_type": "authorization_code",
                "use_pkce": True
            }
        }

    # ============================================
    # OAUTH FLOW - INITIALISATION
    # ============================================

    async def initiate_oauth_flow(
        self,
        user_id: int,
        platform: PlatformType,
        redirect_uri: str
    ) -> OAuthInitResponse:
        """
        Initie le flux OAuth pour une plateforme

        Args:
            user_id: ID de l'utilisateur
            platform: Plateforme à connecter
            redirect_uri: URL de callback

        Returns:
            URL d'autorisation et state token
        """
        config = self.platform_configs.get(platform)
        if not config:
            raise ValueError(f"Platform {platform} not supported")

        # Générer un state token sécurisé
        state_token = secrets.token_urlsafe(32)

        # Générer code_verifier et code_challenge pour PKCE (si supporté)
        code_verifier = None
        code_challenge = None
        if config.get("use_pkce"):
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)

        # Construire les paramètres OAuth
        oauth_params = {
            "client_id": config.get("client_id") or config.get("client_key"),
            "redirect_uri": redirect_uri,
            "response_type": config["response_type"],
            "scope": config["scope"],
            "state": state_token
        }

        # Ajouter code_challenge si PKCE
        if code_challenge:
            oauth_params["code_challenge"] = code_challenge
            oauth_params["code_challenge_method"] = "S256"

        # Construire l'URL d'autorisation
        authorization_url = f"{config['authorization_url']}?{urlencode(oauth_params)}"

        # Sauvegarder le state en DB (dans la vraie app)
        # await self._save_oauth_state(user_id, platform, state_token, code_verifier, redirect_uri)

        return OAuthInitResponse(
            authorization_url=authorization_url,
            state=state_token,
            platform=platform
        )

    # ============================================
    # OAUTH FLOW - CALLBACK
    # ============================================

    async def complete_oauth_flow(
        self,
        user_id: int,
        platform: PlatformType,
        code: str,
        state: str,
        redirect_uri: str
    ) -> PlatformConnection:
        """
        Complete le flux OAuth après le callback

        Args:
            user_id: ID de l'utilisateur
            platform: Plateforme
            code: Code d'autorisation
            state: State token
            redirect_uri: URL de callback

        Returns:
            Connexion de plateforme créée
        """
        # Vérifier le state (dans la vraie app)
        # await self._verify_oauth_state(user_id, platform, state)

        config = self.platform_configs.get(platform)
        if not config:
            raise ValueError(f"Platform {platform} not supported")

        # Récupérer code_verifier si PKCE (dans la vraie app)
        code_verifier = None  # await self._get_code_verifier(user_id, platform, state)

        # Échanger le code contre un access token
        token_data = await self._exchange_code_for_token(
            platform=platform,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier
        )

        # Récupérer les informations du compte
        account_info = await self._fetch_account_info(platform, token_data["access_token"])

        # Créer la connexion
        connection_data = PlatformConnectionCreate(
            platform=platform,
            account_name=account_info.get("username") or account_info.get("name"),
            account_id=account_info.get("id"),
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
            metadata=account_info
        )

        # Sauvegarder en DB (dans la vraie app)
        # connection = await self._save_platform_connection(user_id, connection_data)

        # Pour cet exemple, retourner un objet mock
        return connection_data

    # ============================================
    # TOKEN REFRESH
    # ============================================

    async def refresh_access_token(
        self,
        user_id: int,
        platform_id: int
    ) -> PlatformConnection:
        """
        Rafraîchit un access token expiré

        Args:
            user_id: ID de l'utilisateur
            platform_id: ID de la connexion

        Returns:
            Connexion mise à jour
        """
        # Récupérer la connexion (dans la vraie app)
        # connection = await self._get_platform_connection(platform_id, user_id)

        # Mock pour l'exemple
        connection = None  # À remplacer
        if not connection:
            raise ValueError("Platform connection not found")

        config = self.platform_configs.get(connection.platform)
        if not config:
            raise ValueError(f"Platform {connection.platform} not supported")

        # Rafraîchir le token
        async with httpx.AsyncClient() as client:
            token_data = {
                "grant_type": "refresh_token",
                "refresh_token": connection.refresh_token,
                "client_id": config.get("client_id") or config.get("client_key"),
                "client_secret": config["client_secret"]
            }

            response = await client.post(config["token_url"], data=token_data)
            if response.status_code != 200:
                error = response.text
                raise Exception(f"Failed to refresh token: {error}")

            new_token_data = response.json()

        # Mettre à jour la connexion (dans la vraie app)
        # await self._update_platform_connection(
        #     platform_id,
        #     access_token=new_token_data["access_token"],
        #     token_expires_at=datetime.utcnow() + timedelta(seconds=new_token_data.get("expires_in", 3600))
        # )

        return connection

    # ============================================
    # DISCONNECT
    # ============================================

    async def disconnect_platform(
        self,
        user_id: int,
        platform_id: int
    ) -> bool:
        """
        Déconnecte une plateforme

        Args:
            user_id: ID de l'utilisateur
            platform_id: ID de la connexion

        Returns:
            True si succès
        """
        # Dans la vraie app:
        # 1. Révoquer le token auprès de la plateforme
        # 2. Supprimer ou désactiver la connexion en DB

        return True

    # ============================================
    # MÉTHODES PRIVÉES
    # ============================================

    def _generate_code_verifier(self) -> str:
        """Génère un code_verifier pour PKCE"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

    def _generate_code_challenge(self, verifier: str) -> str:
        """Génère un code_challenge à partir du verifier"""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

    async def _exchange_code_for_token(
        self,
        platform: PlatformType,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Échange le code d'autorisation contre un access token"""
        config = self.platform_configs[platform]

        async with httpx.AsyncClient() as client:
            token_data = {
                "grant_type": config["grant_type"],
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": config.get("client_id") or config.get("client_key"),
                "client_secret": config["client_secret"]
            }

            # Ajouter code_verifier si PKCE
            if code_verifier:
                token_data["code_verifier"] = code_verifier

            response = await client.post(config["token_url"], data=token_data)
            if response.status_code != 200:
                error = response.text
                raise Exception(f"Failed to exchange code for token: {error}")

            return response.json()

    async def _fetch_account_info(
        self,
        platform: PlatformType,
        access_token: str
    ) -> Dict[str, Any]:
        """Récupère les informations du compte depuis la plateforme"""
        # URLs pour récupérer les infos de profil
        profile_urls = {
            PlatformType.INSTAGRAM: "https://graph.instagram.com/me?fields=id,username,account_type",
            PlatformType.TWITTER: "https://api.twitter.com/2/users/me",
            PlatformType.LINKEDIN: "https://api.linkedin.com/v2/me",
            PlatformType.FACEBOOK: "https://graph.facebook.com/me?fields=id,name",
            PlatformType.TIKTOK: "https://open.tiktokapis.com/v2/user/info/"
        }

        url = profile_urls.get(platform)
        if not url:
            return {"id": "unknown", "username": "unknown"}

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                # Si erreur, retourner des infos par défaut
                return {"id": "unknown", "username": "unknown"}

            return response.json()

    async def _save_oauth_state(
        self,
        user_id: int,
        platform: PlatformType,
        state_token: str,
        code_verifier: Optional[str],
        redirect_uri: str
    ):
        """Sauvegarde l'état OAuth en base de données"""
        # Dans la vraie app:
        # INSERT INTO media_oauth_states (user_id, platform, state_token, code_verifier, redirect_uri, expires_at)
        # VALUES (user_id, platform, state_token, code_verifier, redirect_uri, NOW() + INTERVAL '10 minutes')
        pass

    async def _verify_oauth_state(
        self,
        user_id: int,
        platform: PlatformType,
        state: str
    ):
        """Vérifie que le state token est valide"""
        # Dans la vraie app:
        # SELECT * FROM media_oauth_states
        # WHERE user_id = user_id AND platform = platform AND state_token = state
        # AND expires_at > NOW() AND used = FALSE
        #
        # Si trouvé:
        # UPDATE media_oauth_states SET used = TRUE WHERE id = ...
        # Sinon:
        # raise Exception("Invalid or expired state token")
        pass

    async def _get_code_verifier(
        self,
        user_id: int,
        platform: PlatformType,
        state: str
    ) -> Optional[str]:
        """Récupère le code_verifier depuis la DB"""
        # Dans la vraie app:
        # SELECT code_verifier FROM media_oauth_states
        # WHERE user_id = user_id AND platform = platform AND state_token = state
        return None

    async def _save_platform_connection(
        self,
        user_id: int,
        connection_data: PlatformConnectionCreate
    ) -> PlatformConnection:
        """Sauvegarde une connexion de plateforme"""
        # Dans la vraie app:
        # 1. Chiffrer les tokens avec encryption_key
        # 2. INSERT ou UPDATE media_platforms
        # 3. Retourner l'objet PlatformConnection
        pass

    async def _get_platform_connection(
        self,
        platform_id: int,
        user_id: int
    ) -> Optional[PlatformConnection]:
        """Récupère une connexion depuis la DB"""
        # Dans la vraie app:
        # SELECT * FROM media_platforms
        # WHERE id = platform_id AND user_id = user_id
        # Déchiffrer les tokens
        return None

    async def _update_platform_connection(
        self,
        platform_id: int,
        **updates
    ):
        """Met à jour une connexion"""
        # Dans la vraie app:
        # UPDATE media_platforms
        # SET ... WHERE id = platform_id
        pass


# ============================================
# UTILITY: ENCRYPTION/DECRYPTION
# ============================================

class TokenEncryption:
    """
    Classe utilitaire pour chiffrer/déchiffrer les tokens
    """

    def __init__(self):
        from cryptography.fernet import Fernet
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            # Générer une clé pour le développement (NE PAS FAIRE EN PRODUCTION!)
            key = Fernet.generate_key()
            print(f"⚠️  ENCRYPTION_KEY not set! Generated temporary key: {key.decode()}")

        self.cipher = Fernet(key if isinstance(key, bytes) else key.encode())

    def encrypt(self, token: str) -> str:
        """Chiffre un token"""
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        """Déchiffre un token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()


# Instance globale
token_encryption = TokenEncryption()
