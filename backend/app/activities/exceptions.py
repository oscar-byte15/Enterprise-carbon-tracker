"""Domain-specific errors for Subsystem 2: Carbon Activity Management."""


class Subsystem2Error(ValueError):
    """Base exception for invalid carbon activity operations."""


class InvalidActivityError(Subsystem2Error):
    """Raised when carbon activity data or measurement units are invalid."""


class EmissionFactorNotFoundError(Subsystem2Error):
    """Raised when a category or activity type has no configured factor."""


class ActivityNotFoundError(Subsystem2Error):
    """Raised when an activity cannot be found within the enterprise."""
