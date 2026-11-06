"""Domain-specific errors for Subsystem 3: Analytics Dashboard & AI Advisory."""


class Subsystem3Error(ValueError):
    """Base exception for Subsystem 3 analytics and AI advisory errors."""


class InvalidMetricError(Subsystem3Error):
    """Raised when emission metric values, percentages, or activity counts are invalid."""


class InvalidDatePeriodError(Subsystem3Error):
    """Raised when period or year parameters have an invalid format or range."""


class AnalyticsAggregationError(Subsystem3Error):
    """Raised when analytics aggregation fails or an analytics state is invalid."""


class InsufficientDataError(Subsystem3Error):
    """Raised when required activity records are missing for analytics generation."""


class AIAdvisorError(Subsystem3Error):
    """Raised when AI advisory recommendation generation fails or advisor configuration is invalid."""

