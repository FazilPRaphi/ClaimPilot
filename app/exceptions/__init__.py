"""
Custom exceptions for ClaimPilot application.
Provides a hierarchy for specific error types that can be caught and handled appropriately.
"""


class ClaimPilotException(Exception):
    """
    Base exception for all ClaimPilot-specific errors.
    All custom exceptions inherit from this.
    """
    pass


class AuthenticationError(ClaimPilotException):
    """Raised when authentication fails (invalid credentials, expired token, etc.)."""
    pass


class AuthorizationError(ClaimPilotException):
    """Raised when user lacks permissions for an operation."""
    pass


class ValidationError(ClaimPilotException):
    """Raised when business logic validation fails."""
    pass


class DatabaseError(ClaimPilotException):
    """Raised when database operations fail."""
    pass


class NotFoundError(ClaimPilotException):
    """Raised when a requested resource is not found."""
    pass


class ConflictError(ClaimPilotException):
    """Raised when operation conflicts with existing data (e.g., duplicate email)."""
    pass
