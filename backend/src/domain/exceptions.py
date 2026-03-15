"""Domain exceptions."""


class DomainError(Exception):
    """Base exception for domain failures."""


class InvalidEntity(DomainError):
    """Raised when a domain entity is constructed with invalid values."""


class InvalidJobStateTransition(DomainError):
    """Raised when a job state transition is not allowed."""


class InvalidTimeout(DomainError):
    """Raised when a timeout is outside the allowed bounds."""
