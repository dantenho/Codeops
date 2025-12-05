"""
Domain Exceptions

Custom exceptions for the domain layer.
"""


class DomainException(Exception):
    """Base exception for domain layer."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    pass


class EntityAlreadyExistsError(DomainException):
    """Raised when attempting to create an entity that already exists."""
    pass


class InvalidEntityStateError(DomainException):
    """Raised when an entity is in an invalid state for an operation."""
    pass


class ValidationError(DomainException):
    """Raised when entity validation fails."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass
