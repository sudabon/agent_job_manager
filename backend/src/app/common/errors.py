"""Application error types."""


class ApplicationError(Exception):
    """Base exception for application failures."""


class ValidationError(ApplicationError):
    """Raised when an input payload is invalid."""


class JobNotFound(ApplicationError):
    """Raised when the requested job does not exist."""


class AuthenticationFailed(ApplicationError):
    """Raised when API key authentication fails."""
