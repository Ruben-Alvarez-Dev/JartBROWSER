"""
OAuth Authentication Service
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

import httpx
import jwt
from jwt import PyJWKClient


class OAuthProvider(Enum):
    """Supported OAuth providers"""

    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"


class AuthProvider:
    """OAuth provider configuration"""

    def __init__(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # Provider-specific URLs
        self._urls = {
            OAuthProvider.GOOGLE: {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
            },
            OAuthProvider.GITHUB: {
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
            },
            OAuthProvider.MICROSOFT: {
                "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
            },
        }

    def get_auth_url(self, state: str, scopes: List[str] = None) -> str:
        """Generate OAuth authorization URL"""
        scopes = scopes or self._get_default_scopes()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
        }

        url = self._urls[self.provider]["auth_url"]
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{url}?{query}"

    def _get_default_scopes(self) -> List[str]:
        """Get default scopes for provider"""
        scopes = {
            OAuthProvider.GOOGLE: [
                "openid",
                "email",
                "profile",
            ],
            OAuthProvider.GITHUB: [
                "read:user",
                "user:email",
            ],
            OAuthProvider.MICROSOFT: [
                "openid",
                "email",
                "profile",
                "User.Read",
            ],
        }
        return scopes.get(self.provider, [])


@dataclass
class User:
    """Authenticated user"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    name: str = ""
    avatar_url: Optional[str] = None
    provider: OAuthProvider = OAuthProvider.GOOGLE
    provider_id: str = ""  # ID from the OAuth provider
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthSession:
    """Authentication session"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    access_token: str = ""
    refresh_token: Optional[str] = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))
    created_at: datetime = field(default_factory=datetime.utcnow)


class OAuthService:
    """
    OAuth authentication service.

    Supports:
    - Google
    - GitHub
    - Microsoft
    """

    def __init__(self, secret_key: str = "change-me-in-production"):
        self._providers: Dict[OAuthProvider, AuthProvider] = {}
        self._sessions: Dict[str, AuthSession] = {}
        self._users: Dict[str, User] = {}
        self._secret_key = secret_key

    def register_provider(
        self,
        provider: OAuthProvider,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> None:
        """Register an OAuth provider"""
        self._providers[provider] = AuthProvider(
            provider=provider,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )

    def get_provider(self, provider: OAuthProvider) -> Optional[AuthProvider]:
        """Get a registered provider"""
        return self._providers.get(provider)

    def get_authorization_url(self, provider: OAuthProvider) -> Optional[str]:
        """Get authorization URL for a provider"""
        auth_provider = self._providers.get(provider)
        if not auth_provider:
            return None

        state = str(uuid.uuid4())
        return auth_provider.get_auth_url(state)

    async def exchange_code(
        self,
        provider: OAuthProvider,
        code: str,
    ) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for tokens"""
        auth_provider = self._providers.get(provider)
        if not auth_provider:
            return None

        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                auth_provider._urls[provider]["token_url"],
                data={
                    "client_id": auth_provider.client_id,
                    "client_secret": auth_provider.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": auth_provider.redirect_uri,
                },
            )

            if token_response.status_code != 200:
                return None

            tokens = token_response.json()

            # Get user info
            user_response = await client.get(
                auth_provider._urls[provider]["userinfo_url"],
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )

            if user_response.status_code != 200:
                return None

            user_data = user_response.json()

            return {
                "tokens": tokens,
                "user": user_data,
            }

    def create_session(self, user: User, tokens: Dict[str, Any]) -> AuthSession:
        """Create an authentication session"""
        expires_in = tokens.get("expires_in", 3600)

        session = AuthSession(
            user_id=user.id,
            access_token=tokens["access_token"],
            refresh_token=tokens.get("refresh_token"),
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
        )

        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[AuthSession]:
        """Get a session"""
        return self._sessions.get(session_id)

    def validate_session(self, session_id: str) -> bool:
        """Check if session is valid"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        if datetime.utcnow() > session.expires_at:
            return False

        return True

    def create_user(self, provider: OAuthProvider, user_data: Dict[str, Any]) -> User:
        """Create or update user from OAuth data"""
        provider_id = str(user_data.get("id", ""))

        # Find existing user
        existing = next(
            (
                u
                for u in self._users.values()
                if u.provider == provider and u.provider_id == provider_id
            ),
            None,
        )

        if existing:
            existing.last_login = datetime.utcnow()
            return existing

        # Create new user
        user = User(
            email=user_data.get("email", ""),
            name=user_data.get("name", user_data.get("login", "")),
            avatar_url=user_data.get("picture", user_data.get("avatar_url")),
            provider=provider,
            provider_id=provider_id,
        )

        self._users[user.id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    def generate_jwt(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            "sub": user.id,
            "email": user.email,
            "name": user.name,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=7),
        }
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            return jwt.decode(token, self._secret_key, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None


# Singleton
_oauth_service: Optional[OAuthService] = None


def get_oauth_service() -> OAuthService:
    """Get OAuth service instance"""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service
