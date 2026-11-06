class Subsystem1Error(ValueError):
    """Base exception for Subsystem 1 authentication and enterprise errors."""


class EmailAlreadyRegisteredError(Subsystem1Error):
    """Raised when a user attempts to register with an email already in use."""


class EnterpriseNotFoundError(Subsystem1Error):
    """Raised when an enterprise record cannot be found for a requested update."""
