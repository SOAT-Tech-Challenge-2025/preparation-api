"""Preparation status value object module"""

from enum import Enum, unique


@unique
class PreparationStatus(str, Enum):
    """Enumeration of possible preparation statuses."""

    RECEIVED = "RECEIVED"
    IN_PREPARATION = "IN_PREPARATION"
    READY = "READY"
    COMPLETED = "COMPLETED"
