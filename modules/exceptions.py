"""Custom exceptions for ngx-renamer."""


class NGXRenamerError(Exception):
    """Base exception for all ngx-renamer errors."""
    pass


class PaperlessAPIError(NGXRenamerError):
    """Exception raised for Paperless NGX API errors."""
    pass
