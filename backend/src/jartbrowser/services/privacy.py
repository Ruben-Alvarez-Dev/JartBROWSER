"""
Privacy & Security Service

Provides local-first mode, privacy controls,
and security settings management.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class PrivacyMode(Enum):
    """Privacy mode options"""

    LOCAL_ONLY = "local_only"
    HYBRID = "hybrid"
    CLOUD = "cloud"


class DataLocation(Enum):
    """Data storage location"""

    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


@dataclass
class PrivacySettings:
    """Privacy settings"""

    mode: PrivacyMode = PrivacyMode.LOCAL_ONLY
    local_data_retention_days: int = 30
    cloud_sync_enabled: bool = False
    telemetry_enabled: bool = False
    crash_reports_enabled: bool = True
    auto_delete_history_days: int = 0  # 0 = never
    allow_ai_training: bool = False
    encrypt_local_data: bool = True


@dataclass
class SecuritySettings:
    """Security settings"""

    api_key_encryption_enabled: bool = True
    session_timeout_minutes: int = 60
    require_auth_for_api: bool = False
    allowed_origins: List[str] = field(default_factory=lambda: ["http://localhost:*"])
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100


class PrivacyService:
    """
    Service for managing privacy and security settings.

    Provides:
    - Local-first mode configuration
    - Privacy controls
    - Data retention policies
    - Security settings
    """

    def __init__(self):
        self._privacy = PrivacySettings()
        self._security = SecuritySettings()
        self._encryption_key: Optional[str] = None

    # ============== Privacy Settings ==============

    def get_privacy_settings(self) -> PrivacySettings:
        """Get current privacy settings"""
        return self._privacy

    def update_privacy_settings(
        self,
        mode: Optional[PrivacyMode] = None,
        local_data_retention_days: Optional[int] = None,
        cloud_sync_enabled: Optional[bool] = None,
        telemetry_enabled: Optional[bool] = None,
        auto_delete_history_days: Optional[int] = None,
        allow_ai_training: Optional[bool] = None,
        encrypt_local_data: Optional[bool] = None,
    ) -> PrivacySettings:
        """Update privacy settings"""
        if mode is not None:
            self._privacy.mode = mode
        if local_data_retention_days is not None:
            self._privacy.local_data_retention_days = local_data_retention_days
        if cloud_sync_enabled is not None:
            self._privacy.cloud_sync_enabled = cloud_sync_enabled
        if telemetry_enabled is not None:
            self._privacy.telemetry_enabled = telemetry_enabled
        if auto_delete_history_days is not None:
            self._privacy.auto_delete_history_days = auto_delete_history_days
        if allow_ai_training is not None:
            self._privacy.allow_ai_training = allow_ai_training
        if encrypt_local_data is not None:
            self._privacy.encrypt_local_data = encrypt_local_data

        return self._privacy

    def is_local_only(self) -> bool:
        """Check if running in local-only mode"""
        return self._privacy.mode == PrivacyMode.LOCAL_ONLY

    def is_cloud_enabled(self) -> bool:
        """Check if cloud features are enabled"""
        return self._privacy.cloud_sync_enabled or self._privacy.mode == PrivacyMode.CLOUD

    def should_collect_telemetry(self) -> bool:
        """Check if telemetry should be collected"""
        return self._privacy.telemetry_enabled and self._is_user_consented()

    def _is_user_consented(self) -> bool:
        """Check if user has consented to data collection"""
        # In production, would check user consent status
        return True

    # ============== Security Settings ==============

    def get_security_settings(self) -> SecuritySettings:
        """Get current security settings"""
        return self._security

    def update_security_settings(
        self,
        api_key_encryption_enabled: Optional[bool] = None,
        session_timeout_minutes: Optional[int] = None,
        require_auth_for_api: Optional[bool] = None,
        allowed_origins: Optional[List[str]] = None,
        rate_limit_enabled: Optional[bool] = None,
        rate_limit_requests: Optional[int] = None,
    ) -> SecuritySettings:
        """Update security settings"""
        if api_key_encryption_enabled is not None:
            self._security.api_key_encryption_enabled = api_key_encryption_enabled
        if session_timeout_minutes is not None:
            self._security.session_timeout_minutes = session_timeout_minutes
        if require_auth_for_api is not None:
            self._security.require_auth_for_api = require_auth_for_api
        if allowed_origins is not None:
            self._security.allowed_origins = allowed_origins
        if rate_limit_enabled is not None:
            self._security.rate_limit_enabled = rate_limit_enabled
        if rate_limit_requests is not None:
            self._security.rate_limit_requests = rate_limit_requests

        return self._security

    def is_api_key_encryption_enabled(self) -> bool:
        """Check if API key encryption is enabled"""
        return self._security.api_key_encryption_enabled

    def is_origin_allowed(self, origin: str) -> bool:
        """Check if an origin is allowed"""
        # Check exact matches and wildcards
        for allowed in self._security.allowed_origins:
            if allowed.endswith("*"):
                prefix = allowed[:-1]
                if origin.startswith(prefix):
                    return True
            elif allowed == origin:
                return True

        return False

    # ============== Data Management ==============

    def get_data_location(self) -> DataLocation:
        """Determine where data should be stored"""
        if self._privacy.mode == PrivacyMode.LOCAL_ONLY:
            return DataLocation.LOCAL
        elif self._privacy.mode == PrivacyMode.CLOUD:
            return DataLocation.CLOUD
        else:
            return DataLocation.HYBRID

    def should_delete_data_older_than(self) -> Optional[datetime]:
        """Get cutoff date for data deletion"""
        if self._privacy.auto_delete_history_days > 0:
            from datetime import timedelta

            return datetime.utcnow() - timedelta(days=self._privacy.auto_delete_history_days)
        return None

    # ============== Encryption ==============

    def set_encryption_key(self, key: str) -> None:
        """Set the encryption key"""
        self._encryption_key = key

    def get_encryption_key(self) -> Optional[str]:
        """Get the encryption key"""
        return self._encryption_key

    def has_encryption_key(self) -> bool:
        """Check if encryption key is set"""
        return self._encryption_key is not None

    # ============== Export/Import ==============

    def export_settings(self) -> Dict[str, Any]:
        """Export privacy and security settings"""
        return {
            "privacy": {
                "mode": self._privacy.mode.value,
                "local_data_retention_days": self._privacy.local_data_retention_days,
                "cloud_sync_enabled": self._privacy.cloud_sync_enabled,
                "telemetry_enabled": self._privacy.telemetry_enabled,
                "auto_delete_history_days": self._privacy.auto_delete_history_days,
                "allow_ai_training": self._privacy.allow_ai_training,
                "encrypt_local_data": self._privacy.encrypt_local_data,
            },
            "security": {
                "api_key_encryption_enabled": self._security.api_key_encryption_enabled,
                "session_timeout_minutes": self._security.session_timeout_minutes,
                "require_auth_for_api": self._security.require_auth_for_api,
                "allowed_origins": self._security.allowed_origins,
                "rate_limit_enabled": self._security.rate_limit_enabled,
                "rate_limit_requests": self._security.rate_limit_requests,
            },
        }

    def import_settings(self, settings: Dict[str, Any]) -> None:
        """Import privacy and security settings"""
        if "privacy" in settings:
            p = settings["privacy"]
            self.update_privacy_settings(
                mode=PrivacyMode(p.get("mode", "local_only")),
                local_data_retention_days=p.get("local_data_retention_days"),
                cloud_sync_enabled=p.get("cloud_sync_enabled"),
                telemetry_enabled=p.get("telemetry_enabled"),
                auto_delete_history_days=p.get("auto_delete_history_days"),
                allow_ai_training=p.get("allow_ai_training"),
                encrypt_local_data=p.get("encrypt_local_data"),
            )

        if "security" in settings:
            s = settings["security"]
            self.update_security_settings(
                api_key_encryption_enabled=s.get("api_key_encryption_enabled"),
                session_timeout_minutes=s.get("session_timeout_minutes"),
                require_auth_for_api=s.get("require_auth_for_api"),
                allowed_origins=s.get("allowed_origins"),
                rate_limit_enabled=s.get("rate_limit_enabled"),
                rate_limit_requests=s.get("rate_limit_requests"),
            )


# Singleton
_privacy_service: Optional[PrivacyService] = None


def get_privacy_service() -> PrivacyService:
    """Get the privacy service instance"""
    global _privacy_service
    if _privacy_service is None:
        _privacy_service = PrivacyService()
    return _privacy_service
