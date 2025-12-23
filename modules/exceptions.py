"""Custom exceptions for ngx-renamer."""


class NGXRenamerError(Exception):
    """Base exception for all ngx-renamer errors."""
    pass


class SettingsError(NGXRenamerError):
    """Exception raised for settings-related errors."""
    pass


class LLMProviderError(NGXRenamerError):
    """Exception raised for LLM provider errors."""
    pass


class TitleGenerationError(LLMProviderError):
    """Exception raised when title generation fails."""
    pass


class PaperlessAPIError(NGXRenamerError):
    """Exception raised for Paperless NGX API errors."""
    pass
