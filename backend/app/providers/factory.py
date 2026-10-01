"""
AI Provider Factory Module.
Provides centralized factory instantiation and lightweight configuration checks for AI providers.
Ensures lazy client creation and controlled configuration validation.
"""

import logging
from typing import Any, Dict, Optional

from backend.app.config import Settings, get_settings
from backend.app.providers.base import BaseAIProvider
from backend.app.providers.demo import DemoProvider
from backend.app.providers.exceptions import (
    ProviderConfigurationError,
    UnsupportedProviderError,
)
from backend.app.providers.gemini_provider import GeminiProvider

logger = logging.getLogger("sahayakai.providers.factory")


def get_provider(
    provider_name: Optional[str] = None,
    settings: Optional[Settings] = None,
) -> BaseAIProvider:
    """
    Factory function returning the configured or requested AI provider instance.

    Args:
        provider_name: Explicit provider override ('demo' or 'gemini').
        settings: Optional Settings instance. If None, loaded from environment cache.

    Returns:
        Instance implementing BaseAIProvider.

    Raises:
        UnsupportedProviderError: When an unrecognized provider is requested.
        ProviderConfigurationError: When required credentials for the provider are missing.
    """
    if settings is None:
        settings = get_settings()

    target = (provider_name or settings.AI_PROVIDER).lower().strip()

    if target == "demo":
        return DemoProvider()
    if target == "gemini":
        if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
            raise ProviderConfigurationError(
                "GEMINI_API_KEY is required when AI_PROVIDER is configured as 'gemini'."
            )
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            default_model=settings.GEMINI_MODEL,
            timeout=float(settings.AI_TIMEOUT_SECONDS),
        )

    else:
        raise UnsupportedProviderError(
            f"Unsupported AI provider '{target}'. Supported options are: 'demo', 'gemini'."
        )


def check_provider_status(settings: Optional[Settings] = None) -> Dict[str, Any]:
    """
    Lightweight diagnostic inspection of provider readiness.
    Performs purely internal validation without external network calls.
    """
    if settings is None:
        settings = get_settings()

    provider = settings.AI_PROVIDER.lower().strip()

    if provider == "demo":
        return {
            "status": "ok",
            "provider": "demo",
            "model": "demo-deterministic",
            "details": "Local deterministic engine ready (zero credentials required)",
        }
    if provider == "gemini":
        has_key = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
        return {
            "status": "ok" if has_key else "unconfigured",
            "provider": "gemini",
            "model": settings.GEMINI_MODEL,
            "details": "API key present" if has_key else "Missing GEMINI_API_KEY",
        }
    else:
        return {
            "status": "error",
            "provider": provider,
            "details": f"Unknown provider '{provider}' configured",
        }
