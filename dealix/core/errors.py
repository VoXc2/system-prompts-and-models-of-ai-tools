"""Custom exception hierarchy | شجرة الاستثناءات."""

from __future__ import annotations


class AICompanyError(Exception):
    """Base exception for all AI Company errors."""


class ConfigurationError(AICompanyError):
    """Missing or invalid configuration."""


class LLMError(AICompanyError):
    """LLM provider error."""


class IntegrationError(AICompanyError):
    """External integration error."""


class AgentError(AICompanyError):
    """Agent execution error."""


class ValidationError(AICompanyError):
    """Input validation error."""


class RateLimitError(AICompanyError):
    """Rate limit hit."""


class AuthenticationError(AICompanyError):
    """Authentication failed."""
