"""Preparation schema for REST API v1"""

from datetime import datetime

from pydantic import BaseModel, Field

from preparation_api.domain.value_objects import PreparationStatus


class PreparationV1(BaseModel):
    """Preparation schema representing a preparation record"""

    id: str = Field(description="Unique identifier for the preparation")
    preparation_position: int | None = Field(
        None, description="Position of the preparation in the queue"
    )

    preparation_time: int = Field(
        description="Time required for the preparation in minutes"
    )

    estimated_ready_time: datetime | None = Field(
        None, description="Estimated time when the preparation will be ready"
    )

    preparation_status: PreparationStatus = Field(
        PreparationStatus.RECEIVED, description="Status of the preparation"
    )

    created_at: datetime = Field(
        description="Creation date and time of the preparation"
    )

    timestamp: datetime = Field(
        description="Last update date and time of the preparation"
    )


class PreparationListV1(BaseModel):
    """Schema representing a list of preparations"""

    items: list[PreparationV1] = Field(..., description="List of preparation records")
